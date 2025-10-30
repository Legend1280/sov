"""
Core Storage Layer
SQLite persistence for the semantic kernel

Handles:
- Object storage (symbolic data)
- Vector storage (embeddings)
- Provenance ledger
- SAGE metadata
"""

import sqlite3
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from contextlib import contextmanager

class CoreStorage:
    """SQLite storage layer for Core kernel"""
    
    def __init__(self, db_path: str = "./core.db"):
        self.db_path = db_path
        self._init_database()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        # Don't use row_factory - causes issues with REAL types
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def _init_database(self):
        """Initialize database schema"""
        with self.get_connection() as conn:
            cur = conn.cursor()
            
            # Objects table (symbolic data)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS objects (
                    id TEXT PRIMARY KEY,
                    object_type TEXT NOT NULL,
                    data JSON NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            # Vectors table (embeddings)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS vectors (
                    object_id TEXT PRIMARY KEY,
                    embedding BLOB NOT NULL,
                    model TEXT NOT NULL,
                    dimension INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (object_id) REFERENCES objects(id)
                )
            """)
            
            # SAGE metadata table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS sage_metadata (
                    object_id TEXT PRIMARY KEY,
                    coherence_score REAL,
                    trust_score REAL,
                    validated BOOLEAN,
                    validated_at TEXT,
                    FOREIGN KEY (object_id) REFERENCES objects(id)
                )
            """)
            
            # Relations table (semantic connections)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS relations (
                    id TEXT PRIMARY KEY,
                    source_id TEXT NOT NULL,
                    target_id TEXT NOT NULL,
                    relation_type TEXT NOT NULL,
                    similarity_score REAL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (source_id) REFERENCES objects(id),
                    FOREIGN KEY (target_id) REFERENCES objects(id)
                )
            """)
            
            # Provenance table (audit trail)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS provenance (
                    id TEXT PRIMARY KEY,
                    object_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    actor TEXT,
                    metadata JSON,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY (object_id) REFERENCES objects(id)
                )
            """)
            
            # Create indexes
            cur.execute("CREATE INDEX IF NOT EXISTS idx_objects_type ON objects(object_type)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_relations_source ON relations(source_id)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_relations_target ON relations(target_id)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_provenance_object ON provenance(object_id)")
    
    # ==================== OBJECT OPERATIONS ====================
    
    def save_object(self, object_type: str, data: Dict[str, Any], object_id: Optional[str] = None) -> str:
        """Save an object to storage"""
        if object_id is None:
            object_id = str(uuid.uuid4())
        
        now = datetime.utcnow().isoformat()
        
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT OR REPLACE INTO objects (id, object_type, data, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
            """, (object_id, object_type, json.dumps(data), now, now))
        
        return object_id
    
    def get_object(self, object_id: str) -> Optional[Dict[str, Any]]:
        """Get an object by ID"""
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, object_type, data, created_at, updated_at FROM objects WHERE id = ?", (object_id,))
            row = cur.fetchone()
            
            if row is None:
                return None
            
            return {
                "id": row[0],
                "object_type": row[1],
                "data": json.loads(row[2]),
                "created_at": row[3],
                "updated_at": row[4]
            }
    
    def query_objects(self, object_type: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Query objects by type"""
        with self.get_connection() as conn:
            cur = conn.cursor()
            
            if object_type:
                cur.execute("""
                    SELECT id, object_type, data, created_at, updated_at FROM objects WHERE object_type = ? LIMIT ?
                """, (object_type, limit))
            else:
                cur.execute("SELECT id, object_type, data, created_at, updated_at FROM objects LIMIT ?", (limit,))
            
            rows = cur.fetchall()
            return [
                {
                    "id": row[0],
                    "object_type": row[1],
                    "data": json.loads(row[2]),
                    "created_at": row[3],
                    "updated_at": row[4]
                }
                for row in rows
            ]
    
    # ==================== VECTOR OPERATIONS ====================
    
    def save_vector(self, object_id: str, embedding: bytes, model: str, dimension: int):
        """Save vector embedding"""
        now = datetime.utcnow().isoformat()
        
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT OR REPLACE INTO vectors (object_id, embedding, model, dimension, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (object_id, embedding, model, dimension, now))
    
    def get_vector(self, object_id: str, include_embedding: bool = True) -> Optional[Dict[str, Any]]:
        """Get vector embedding"""
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT object_id, embedding, model, dimension, created_at FROM vectors WHERE object_id = ?", (object_id,))
            row = cur.fetchone()
            
            if row is None:
                return None
            
            result = {
                "object_id": row[0],
                "model": row[2],
                "dimension": row[3],
                "created_at": row[4]
            }
            
            if include_embedding:
                result["embedding"] = row[1]
            
            return result
    
    # ==================== SAGE OPERATIONS ====================
    
    def save_sage_metadata(self, object_id: str, coherence_score: float, trust_score: float, validated: bool):
        """Save SAGE governance metadata"""
        now = datetime.utcnow().isoformat()
        
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT OR REPLACE INTO sage_metadata 
                (object_id, coherence_score, trust_score, validated, validated_at)
                VALUES (?, ?, ?, ?, ?)
            """, (str(object_id), float(coherence_score), float(trust_score), int(validated), str(now)))
    
    def get_sage_metadata(self, object_id: str) -> Optional[Dict[str, Any]]:
        """Get SAGE metadata"""
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT object_id, coherence_score, trust_score, validated, validated_at FROM sage_metadata WHERE object_id = ?", (object_id,))
            row = cur.fetchone()
            
            if row is None:
                return None
            
            return {
                "object_id": row[0],
                "coherence_score": row[1],
                "trust_score": row[2],
                "validated": bool(row[3]),
                "validated_at": row[4]
            }
    
    # ==================== RELATION OPERATIONS ====================
    
    def save_relation(self, source_id: str, target_id: str, relation_type: str, similarity_score: float):
        """Save a semantic relation"""
        relation_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO relations (id, source_id, target_id, relation_type, similarity_score, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (str(relation_id), str(source_id), str(target_id), str(relation_type), float(similarity_score), str(now)))
        
        return relation_id
    
    def get_relations(self, object_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get relations for an object"""
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT id, source_id, target_id, relation_type, similarity_score, created_at FROM relations 
                WHERE source_id = ? OR target_id = ?
                ORDER BY similarity_score DESC
                LIMIT ?
            """, (object_id, object_id, limit))
            
            rows = cur.fetchall()
            return [
                {
                    "id": row[0],
                    "source_id": row[1],
                    "target_id": row[2],
                    "relation_type": row[3],
                    "similarity_score": row[4],
                    "created_at": row[5]
                }
                for row in rows
            ]
    
    # ==================== PROVENANCE OPERATIONS ====================
    
    def log_provenance(self, object_id: str, action: str, actor: Optional[str] = None, metadata: Optional[Dict] = None):
        """Log a provenance event"""
        event_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO provenance (id, object_id, action, actor, metadata, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (event_id, object_id, action, actor, json.dumps(metadata or {}), now))
        
        return event_id
    
    def get_provenance(self, object_id: str) -> List[Dict[str, Any]]:
        """Get provenance chain for an object"""
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT id, object_id, action, actor, metadata, timestamp FROM provenance 
                WHERE object_id = ?
                ORDER BY timestamp DESC
            """, (object_id,))
            
            rows = cur.fetchall()
            return [
                {
                    "id": row[0],
                    "object_id": row[1],
                    "action": row[2],
                    "actor": row[3],
                    "metadata": json.loads(row[4]),
                    "timestamp": row[5]
                }
                for row in rows
            ]


# Singleton instance
_storage = None

def get_storage(db_path: str = "./core.db") -> CoreStorage:
    """Get the global storage instance"""
    global _storage
    if _storage is None:
        _storage = CoreStorage(db_path)
    return _storage
