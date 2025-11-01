"""
Shadow Ledger - Provenance Logger (Pulse-Native)

Tracks all Pulses and events for audit, lineage, and forensics.

Shadow Ledger provides:
- Immutable event logging
- Provenance tracking
- Audit trail
- Forensic analysis
- Wake-aware initialization
- Pulse-native communication

Author: Brady Simmons
Copyright: © 2025 Sovereignty Foundation. All rights reserved.
"""

import sqlite3
import json
import asyncio
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path
from pulse_bus import PulseBus

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Shadow")

# Global PulseBus instance
bus = PulseBus()

class ShadowLedger:
    """Shadow Ledger - Pulse-Native Provenance Logger"""
    
    def __init__(self, db_path: str = "/home/ubuntu/sov/data/shadow_ledger.db"):
        self.db_path = db_path
        self.is_awake = False
        self.start_time = datetime.utcnow()
        
        # Register Pulse listeners
        self._register_pulse_listeners()
    
    def _register_pulse_listeners(self):
        """Register Shadow Ledger's Pulse event listeners"""
        
        @bus.on("system.genesis")
        async def on_genesis(pulse):
            """Respond to Wake genesis pulse"""
            logger.info("[Shadow] Awakening - opening provenance log")
            await self.initialize()
            
            await bus.emit("wake.node_ready", {
                "node_id": "shadow",
                "role": "witness",
                "services": ["provenance", "audit_trail", "forensics"],
                "timestamp": datetime.utcnow().isoformat()
            })
            
            self.is_awake = True
            logger.info("[Shadow] Provenance logger operational")
        
        @bus.on("*")  # Listen to ALL Pulses
        async def on_any_pulse(pulse):
            """Auto-log all Pulses to Shadow Ledger"""
            if not self.is_awake:
                return
            
            # Log the Pulse
            await self.log_pulse(pulse)
        
        @bus.on("shadow.query")
        async def on_query(pulse):
            """Handle provenance queries"""
            payload = pulse.get("payload", {})
            object_id = payload.get("object_id")
            event_type = payload.get("event_type")
            start_time = payload.get("start_time")
            end_time = payload.get("end_time")
            
            results = self.query_provenance(
                object_id=object_id,
                event_type=event_type,
                start_time=start_time,
                end_time=end_time
            )
            
            await bus.emit("shadow.query_result", {
                "request_id": pulse.get("id"),
                "results": results,
                "count": len(results),
                "timestamp": datetime.utcnow().isoformat()
            })
        
        @bus.on("scribe.result.batch")
        async def on_scribe_result(pulse):
            """Store Scribe test evidence and emit to Kronos"""
            if not self.is_awake:
                return
            
            payload = pulse.get("payload", {})
            
            # Store test evidence
            await self.store_test_evidence(payload)
            
            logger.info(f"[Shadow] Stored test evidence: {payload.get('test_id', 'unknown')}")
        
        @bus.on("shadow.evidence.query")
        async def on_evidence_query(pulse):
            """Handle test evidence queries"""
            if not self.is_awake:
                return
            
            payload = pulse.get("payload", {})
            limit = payload.get("limit", 10)
            mode = payload.get("mode")
            category = payload.get("category")
            
            results = self.query_test_evidence(limit=limit, mode=mode, category=category)
            
            await bus.emit("shadow.evidence.result", {
                "request_id": pulse.get("id"),
                "results": results,
                "count": len(results),
                "timestamp": datetime.utcnow().isoformat()
            })
            
            logger.info(f"[Shadow] Evidence query returned {len(results)} results")
        
        @bus.on("system.health_check")
        async def on_health_check(pulse):
            """Respond to health check requests"""
            stats = self.get_ledger_stats()
            
            await bus.emit("system.health_response", {
                "node_id": "shadow",
                "status": "operational" if self.is_awake else "initializing",
                "coherence": 1.0,
                "logged_events": stats.get("total_events", 0),
                "uptime": self.get_uptime(),
                "timestamp": datetime.utcnow().isoformat()
            })
    
    async def initialize(self):
        """Initialize Shadow Ledger database"""
        logger.info("[Shadow] Initializing provenance database...")
        
        # Create data directory if needed
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Create database schema
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS provenance_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pulse_id TEXT,
                topic TEXT,
                source TEXT,
                target TEXT,
                intent TEXT,
                event_type TEXT,
                timestamp TEXT,
                payload TEXT,
                metadata TEXT,
                coherence REAL,
                logged_at TEXT
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_pulse_id ON provenance_log(pulse_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_topic ON provenance_log(topic)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp ON provenance_log(timestamp)
        """)
        
        # Create test_evidence table for Scribe/MiniLM empirical measurements
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_evidence (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                test_id TEXT UNIQUE NOT NULL,
                timestamp TEXT NOT NULL,
                mode TEXT NOT NULL,
                batch_size INTEGER NOT NULL,
                category TEXT,
                sample_count INTEGER NOT NULL,
                scribe_coherence_mean REAL,
                scribe_coherence_std REAL,
                minilm_coherence_mean REAL,
                minilm_coherence_std REAL,
                p_value REAL,
                effect_size REAL,
                sample_results TEXT,
                vectors_blob BLOB,
                metadata TEXT,
                logged_at TEXT NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_test_timestamp ON test_evidence(timestamp DESC)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_test_mode ON test_evidence(mode)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_test_category ON test_evidence(category)
        """)
        
        conn.commit()
        conn.close()
        
        await asyncio.sleep(0.1)
        logger.info("[Shadow] Provenance database ready")
    
    def get_uptime(self) -> float:
        """Get Shadow Ledger uptime in seconds"""
        return (datetime.utcnow() - self.start_time).total_seconds()
    
    async def log_pulse(self, pulse: Dict[str, Any]):
        """Log a Pulse to the Shadow Ledger"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO provenance_log (
                    pulse_id, topic, source, target, intent, event_type,
                    timestamp, payload, metadata, coherence, logged_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                pulse.get("id", "unknown"),
                pulse.get("topic", "unknown"),
                pulse.get("source", "unknown"),
                pulse.get("target", "unknown"),
                pulse.get("intent", "unknown"),
                pulse.get("event_type", "pulse"),
                pulse.get("timestamp", datetime.utcnow().isoformat()),
                json.dumps(pulse.get("payload", {})),
                json.dumps(pulse.get("metadata", {})),
                pulse.get("metadata", {}).get("coherence", 0.0),
                datetime.utcnow().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"[Shadow] Error logging Pulse: {e}")
    
    def log_provenance_event(
        self,
        doc_id: str,
        event_type: str,
        actor: Optional[str] = None,
        checksum: Optional[str] = None,
        semantic_integrity: Optional[float] = None,
        derived_from: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Log a provenance event (legacy interface for backward compatibility)
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO provenance_log (
                    pulse_id, topic, source, target, intent, event_type,
                    timestamp, payload, metadata, coherence, logged_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                doc_id,
                "legacy.provenance",
                actor or "unknown",
                doc_id,
                "provenance",
                event_type,
                datetime.utcnow().isoformat(),
                json.dumps({"checksum": checksum, "derived_from": derived_from}),
                json.dumps(metadata or {}),
                semantic_integrity or 0.0,
                datetime.utcnow().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"[Shadow] Error logging provenance event: {e}")
    
    def query_provenance(
        self,
        object_id: Optional[str] = None,
        event_type: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Query the provenance log"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = "SELECT * FROM provenance_log WHERE 1=1"
            params = []
            
            if object_id:
                query += " AND pulse_id = ?"
                params.append(object_id)
            
            if event_type:
                query += " AND event_type = ?"
                params.append(event_type)
            
            if start_time:
                query += " AND timestamp >= ?"
                params.append(start_time)
            
            if end_time:
                query += " AND timestamp <= ?"
                params.append(end_time)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            conn.close()
            
            # Convert to dict
            results = []
            for row in rows:
                results.append({
                    "id": row[0],
                    "pulse_id": row[1],
                    "topic": row[2],
                    "source": row[3],
                    "target": row[4],
                    "intent": row[5],
                    "event_type": row[6],
                    "timestamp": row[7],
                    "payload": json.loads(row[8]) if row[8] else {},
                    "metadata": json.loads(row[9]) if row[9] else {},
                    "coherence": row[10],
                    "logged_at": row[11]
                })
            
            return results
            
        except Exception as e:
            logger.error(f"[Shadow] Error querying provenance: {e}")
            return []
    
    def get_ledger_stats(self) -> Dict[str, Any]:
        """Get statistics about the Shadow Ledger"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM provenance_log")
            total_events = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(DISTINCT topic) FROM provenance_log")
            total_topics = cursor.fetchone()[0]
            
            cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM provenance_log")
            time_range = cursor.fetchone()
            
            conn.close()
            
            return {
                "total_events": total_events,
                "total_topics": total_topics,
                "first_event": time_range[0],
                "last_event": time_range[1],
                "uptime_seconds": self.get_uptime()
            }
            
        except Exception as e:
            logger.error(f"[Shadow] Error getting stats: {e}")
            return {"total_events": 0}


# Singleton instance
_shadow = None

def get_shadow() -> ShadowLedger:
    """Get the global Shadow Ledger instance"""
    global _shadow
    if _shadow is None:
        _shadow = ShadowLedger()
    return _shadow


# Legacy function for backward compatibility
def log_provenance_event(
    db_path: str,
    doc_id: str,
    event_type: str,
    actor: Optional[str] = None,
    checksum: Optional[str] = None,
    semantic_integrity: Optional[float] = None,
    derived_from: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
):
    """Legacy provenance logging function"""
    shadow = get_shadow()
    shadow.log_provenance_event(
        doc_id=doc_id,
        event_type=event_type,
        actor=actor,
        checksum=checksum,
        semantic_integrity=semantic_integrity,
        derived_from=derived_from,
        metadata=metadata
    )

    async def store_test_evidence(self, evidence: Dict[str, Any]):
        """
        Store test evidence from Scribe/MiniLM validation runs.
        
        Args:
            evidence: Ontological test result object from scribe.result.batch Pulse
        """
        try:
            import pickle
            
            test_id = evidence.get('test_id', f"test_{datetime.utcnow().timestamp()}")
            timestamp = evidence.get('timestamp', datetime.utcnow().isoformat())
            mode = evidence.get('mode', 'internal')  # 'internal' or 'pulse'
            
            batch_metadata = evidence.get('batch_metadata', {})
            batch_size = batch_metadata.get('batch_size', 0)
            category = batch_metadata.get('category_filter', 'all')
            
            sample_results = evidence.get('sample_results', [])
            sample_count = len(sample_results)
            
            statistics = evidence.get('statistical_summary', {})
            scribe_stats = statistics.get('scribe_coherence', {})
            minilm_stats = statistics.get('minilm_coherence', {})
            hypothesis = statistics.get('hypothesis_tests', {})
            
            # Serialize sample results and vectors
            sample_results_json = json.dumps(sample_results)
            
            # Extract and serialize vectors
            vectors = {
                'scribe_embeddings': [s.get('fusion_result', {}).get('wisp_embedding') for s in sample_results],
                'minilm_embeddings': [s.get('baseline_result', {}).get('embedding') for s in sample_results]
            }
            vectors_blob = pickle.dumps(vectors)
            
            metadata = {
                'ontology': evidence.get('ontology', 'scribe_results'),
                'category_breakdown': statistics.get('category_breakdown', {}),
                'latency_stats': statistics.get('latency', {})
            }
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO test_evidence (
                    test_id, timestamp, mode, batch_size, category, sample_count,
                    scribe_coherence_mean, scribe_coherence_std,
                    minilm_coherence_mean, minilm_coherence_std,
                    p_value, effect_size,
                    sample_results, vectors_blob, metadata, logged_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                test_id,
                timestamp,
                mode,
                batch_size,
                category,
                sample_count,
                scribe_stats.get('mean'),
                scribe_stats.get('std'),
                minilm_stats.get('mean'),
                minilm_stats.get('std'),
                hypothesis.get('p_value'),
                hypothesis.get('effect_size'),
                sample_results_json,
                vectors_blob,
                json.dumps(metadata),
                datetime.utcnow().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"[Shadow] Stored test evidence: {test_id} ({mode} mode, {sample_count} samples)")
            
            # Emit provenance event for Kronos indexing
            await bus.emit("shadow.evidence.stored", {
                "test_id": test_id,
                "mode": mode,
                "sample_count": sample_count,
                "timestamp": timestamp
            })
            
        except Exception as e:
            logger.error(f"[Shadow] Error storing test evidence: {e}")
    
    def query_test_evidence(self, limit: int = 10, mode: str = None, category: str = None) -> List[Dict]:
        """
        Query test evidence from Shadow Ledger.
        
        Args:
            limit: Maximum number of results (default: 10)
            mode: Filter by mode ('internal' or 'pulse')
            category: Filter by category
            
        Returns:
            List of test evidence records
        """
        try:
            import pickle
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = "SELECT * FROM test_evidence WHERE 1=1"
            params = []
            
            if mode:
                query += " AND mode = ?"
                params.append(mode)
            
            if category and category != 'all':
                query += " AND category = ?"
                params.append(category)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            results = []
            for row in rows:
                # Deserialize vectors
                vectors = pickle.loads(row[14]) if row[14] else {}
                
                results.append({
                    "test_id": row[1],
                    "timestamp": row[2],
                    "mode": row[3],
                    "batch_size": row[4],
                    "category": row[5],
                    "sample_count": row[6],
                    "scribe_coherence": {
                        "mean": row[7],
                        "std": row[8]
                    },
                    "minilm_coherence": {
                        "mean": row[9],
                        "std": row[10]
                    },
                    "hypothesis_tests": {
                        "p_value": row[11],
                        "effect_size": row[12]
                    },
                    "sample_results": json.loads(row[13]) if row[13] else [],
                    "vectors": vectors,
                    "metadata": json.loads(row[15]) if row[15] else {},
                    "logged_at": row[16]
                })
            
            conn.close()
            return results
            
        except Exception as e:
            logger.error(f"[Shadow] Error querying test evidence: {e}")
            return []

