"""
Kronos Models - Database schema and helpers for temporal events
"""

KRONOS_SCHEMA = """
CREATE TABLE IF NOT EXISTS kronos_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    object_id TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    event_type TEXT NOT NULL,
    vector BLOB,
    coherence_score REAL NOT NULL,
    trust_score REAL NOT NULL,
    metadata TEXT DEFAULT '{}',
    FOREIGN KEY (object_id) REFERENCES objects(id)
);

CREATE INDEX IF NOT EXISTS idx_kronos_object_time 
ON kronos_events(object_id, timestamp);

CREATE INDEX IF NOT EXISTS idx_kronos_time 
ON kronos_events(timestamp);

CREATE INDEX IF NOT EXISTS idx_kronos_event_type 
ON kronos_events(event_type);
"""


def initialize_kronos_tables(storage):
    """
    Initialize Kronos tables in the database.
    
    Args:
        storage: Storage instance
    """
    with storage.get_connection() as conn:
        cursor = conn.cursor()
        
        # Execute schema
        cursor.executescript(KRONOS_SCHEMA)
    
    print("✓ Kronos tables initialized")
