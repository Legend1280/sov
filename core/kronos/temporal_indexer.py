"""
Temporal Indexer - Records semantic state changes over time

Maintains a timeline of vector embeddings and coherence scores,
enabling drift detection and temporal queries.
"""

import numpy as np
from datetime import datetime
from typing import Dict, List, Optional
import json


class TemporalIndexer:
    """
    Indexes semantic objects across time, recording snapshots of their state.
    
    Each event captures:
    - Timestamp
    - Embedding vector (baseline or current)
    - Coherence score
    - Trust score
    - Triggering action (create, update, validate)
    """
    
    def __init__(self, storage):
        """
        Args:
            storage: Storage instance for database access
        """
        self.storage = storage
    
    def record_event(
        self,
        object_id: str,
        event_type: str,
        vector: Optional[np.ndarray] = None,
        coherence_score: float = 0.0,
        trust_score: float = 0.0,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Record a temporal event for an object.
        
        Args:
            object_id: ID of the semantic object
            event_type: "baseline" | "update" | "validation" | "drift_detected"
            vector: Embedding vector at this point in time
            coherence_score: SAGE coherence at this moment
            trust_score: SAGE trust at this moment
            metadata: Additional context (e.g., drift magnitude, action)
        
        Returns:
            event_id
        """
        timestamp = datetime.utcnow().isoformat()
        
        # Serialize vector if provided
        vector_bytes = None
        if vector is not None:
            vector_bytes = vector.tobytes()
        
        # Serialize metadata
        metadata_json = json.dumps(metadata or {})
        
        # Store event
        with self.storage.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO kronos_events 
                (object_id, timestamp, event_type, vector, coherence_score, trust_score, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                object_id,
                timestamp,
                event_type,
                vector_bytes,
                float(coherence_score),
                float(trust_score),
                metadata_json
            ))
            
            event_id = cursor.lastrowid
        
        return f"kronos_event_{event_id}"
    
    def get_baseline(self, object_id: str) -> Optional[Dict]:
        """
        Get the baseline (first) event for an object.
        
        Returns:
            {timestamp, vector, coherence_score, trust_score, metadata}
        """
        with self.storage.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT timestamp, vector, coherence_score, trust_score, metadata
                FROM kronos_events
                WHERE object_id = ? AND event_type = 'baseline'
                ORDER BY timestamp ASC
                LIMIT 1
            """, (object_id,))
            
            row = cursor.fetchone()
        if not row:
            return None
        
        # Deserialize vector
        vector = None
        if row[1]:
            vector = np.frombuffer(row[1], dtype=np.float32)
        
        return {
            "timestamp": row[0],
            "vector": vector,
            "coherence_score": row[2],
            "trust_score": row[3],
            "metadata": json.loads(row[4])
        }
    
    def get_latest(self, object_id: str) -> Optional[Dict]:
        """
        Get the most recent event for an object.
        """
        with self.storage.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT timestamp, event_type, vector, coherence_score, trust_score, metadata
                FROM kronos_events
                WHERE object_id = ?
                ORDER BY timestamp DESC
                LIMIT 1
            """, (object_id,))
            
            row = cursor.fetchone()
        if not row:
            return None
        
        # Deserialize vector
        vector = None
        if row[2]:
            vector = np.frombuffer(row[2], dtype=np.float32)
        
        return {
            "timestamp": row[0],
            "event_type": row[1],
            "vector": vector,
            "coherence_score": row[3],
            "trust_score": row[4],
            "metadata": json.loads(row[5])
        }
    
    def get_timeline(
        self, 
        object_id: str,
        limit: int = 100
    ) -> List[Dict]:
        """
        Get full temporal timeline for an object.
        
        Returns list of events in chronological order.
        """
        with self.storage.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT timestamp, event_type, coherence_score, trust_score, metadata
                FROM kronos_events
                WHERE object_id = ?
                ORDER BY timestamp ASC
                LIMIT ?
            """, (object_id, limit))
            
            timeline = []
            for row in cursor.fetchall():
                timeline.append({
                    "timestamp": row[0],
                    "event_type": row[1],
                    "coherence_score": row[2],
                    "trust_score": row[3],
                    "metadata": json.loads(row[4])
                })
        
        return timeline
    
    def query_by_time_window(
        self,
        start_time: datetime,
        end_time: datetime,
        event_type: Optional[str] = None
    ) -> List[Dict]:
        """
        Query events within a time window.
        
        Useful for temporal filtering in Mirror UI.
        """
        with self.storage.get_connection() as conn:
            cursor = conn.cursor()
            
            query = """
                SELECT object_id, timestamp, event_type, coherence_score, trust_score, metadata
                FROM kronos_events
                WHERE timestamp >= ? AND timestamp <= ?
            """
            params = [start_time.isoformat(), end_time.isoformat()]
            
            if event_type:
                query += " AND event_type = ?"
                params.append(event_type)
            
            query += " ORDER BY timestamp DESC"
            
            cursor.execute(query, params)
            
            events = []
            for row in cursor.fetchall():
                events.append({
                    "object_id": row[0],
                    "timestamp": row[1],
                    "event_type": row[2],
                    "coherence_score": row[3],
                    "trust_score": row[4],
                    "metadata": json.loads(row[5])
                })
        
        return events
