"""
Loom Core API
The central "Semantic OS" backend that provides ontology, provenance, and vector services
to all viewer applications (LoomLite, DexaBooks, etc.)

Version: 1.0.0
Date: October 29, 2025
"""
import os
import sqlite3
import json
import uuid
import hashlib
from datetime import datetime
from typing import Optional, List
from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import core modules
from .models import MicroOntology, DocumentMetadata, OntologyVersion, Span, Concept, Relation, MentionLink
from .reader import read_document
from .extractor import extract_ontology_from_text, store_ontology
from .provenance import log_provenance_event, get_provenance_events
from .embedding_service import add_document_embedding, add_concept_embedding

app = FastAPI(
    title="Loom Core API",
    version="1.0.0",
    description="Central Semantic OS providing ontology, provenance, and vector services"
)

# CORS - Allow all viewer applications
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://loomlite.vercel.app",
        "https://dexabooks.vercel.app",
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://localhost:5000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
        "http://127.0.0.1:5000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database path - use /data volume for persistence on Render, or local path for development
DB_DIR = os.getenv("DB_DIR", "/data" if os.path.exists("/data") else ".")
try:
    os.makedirs(DB_DIR, exist_ok=True)
except OSError:
    DB_DIR = "."
DB_PATH = os.path.join(DB_DIR, "loom_core.db")

# Job storage (in-memory for now)
jobs = {}

# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

def init_database():
    """Initialize database with schema if it doesn't exist"""
    schema_path = os.path.join(os.path.dirname(__file__), "schema_v2.sql")
    
    if os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='documents'")
        if cur.fetchone():
            conn.close()
            print(f"✅ Loom Core database already initialized at {DB_PATH}")
            return
        conn.close()
    
    print(f"🔧 Initializing Loom Core database at {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    with open(schema_path, 'r') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
    print("✅ Loom Core database initialized successfully")

# Initialize on startup
init_database()

# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class IngestRequest(BaseModel):
    content: str
    title: Optional[str] = None
    source_uri: Optional[str] = None
    object_type: str = "document"  # document, transaction, etc.

class IngestResponse(BaseModel):
    job_id: str
    status: str
    message: str

class DocumentResponse(BaseModel):
    id: str
    title: str
    source_uri: Optional[str]
    created_at: str
    summary: Optional[str]

# ============================================================================
# CORE API ENDPOINTS
# ============================================================================

@app.get("/")
def root():
    """Health check endpoint"""
    return {
        "service": "Loom Core",
        "version": "1.0.0",
        "status": "operational",
        "description": "Central Semantic OS for ontology, provenance, and vector services"
    }

@app.post("/api/core/ingest", response_model=IngestResponse)
async def ingest_content(request: IngestRequest, background_tasks: BackgroundTasks):
    """
    Universal ingestion endpoint for any type of content
    Accepts structured data and stores it in the ontology
    """
    job_id = str(uuid.uuid4())
    
    # Create job
    jobs[job_id] = {
        "status": "processing",
        "created_at": datetime.now().isoformat(),
        "object_type": request.object_type
    }
    
    # Process in background
    background_tasks.add_task(process_ingestion, job_id, request)
    
    return IngestResponse(
        job_id=job_id,
        status="processing",
        message=f"Ingestion started for {request.object_type}"
    )

def process_ingestion(job_id: str, request: IngestRequest):
    """Background task to process ingestion"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        # Generate document ID
        doc_id = str(uuid.uuid4())
        
        # Store document metadata
        cur.execute("""
            INSERT INTO documents (id, title, source_uri, created_at, summary)
            VALUES (?, ?, ?, ?, ?)
        """, (
            doc_id,
            request.title or f"{request.object_type}_{doc_id[:8]}",
            request.source_uri,
            datetime.now().isoformat(),
            request.content[:200] if len(request.content) > 200 else request.content
        ))
        
        # Log provenance
        log_provenance_event(
            doc_id=doc_id,
            event_type="ingested",
            actor="loom_core",
            checksum=hashlib.sha256(request.content.encode()).hexdigest()
        )
        
        conn.commit()
        conn.close()
        
        # Update job status
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["doc_id"] = doc_id
        
    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)
        print(f"❌ Ingestion failed: {e}")

@app.get("/api/core/documents")
def get_documents():
    """Retrieve all documents"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    cur.execute("""
        SELECT id, title, source_uri, created_at, summary
        FROM documents
        ORDER BY created_at DESC
    """)
    
    documents = [dict(row) for row in cur.fetchall()]
    conn.close()
    
    return {"documents": documents, "count": len(documents)}

@app.get("/api/core/documents/{doc_id}")
def get_document(doc_id: str):
    """Retrieve a specific document with its ontology"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    # Get document
    cur.execute("SELECT * FROM documents WHERE id = ?", (doc_id,))
    doc = cur.fetchone()
    
    if not doc:
        conn.close()
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Get concepts
    cur.execute("SELECT * FROM concepts WHERE doc_id = ?", (doc_id,))
    concepts = [dict(row) for row in cur.fetchall()]
    
    # Get relations
    cur.execute("SELECT * FROM relations WHERE doc_id = ?", (doc_id,))
    relations = [dict(row) for row in cur.fetchall()]
    
    conn.close()
    
    return {
        "document": dict(doc),
        "concepts": concepts,
        "relations": relations
    }

@app.get("/api/core/provenance/{doc_id}")
def get_provenance(doc_id: str):
    """Get provenance trail for a document"""
    events = get_provenance_events(doc_id)
    return {"doc_id": doc_id, "events": events}

@app.get("/api/core/jobs/{job_id}")
def get_job_status(job_id: str):
    """Check the status of an ingestion job"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return jobs[job_id]

# ============================================================================
# STARTUP MESSAGE
# ============================================================================

@app.on_event("startup")
def startup_event():
    print("=" * 60)
    print("🧠 LOOM CORE - Semantic OS")
    print("=" * 60)
    print(f"📊 Database: {DB_PATH}")
    print(f"🌐 API: http://localhost:8001")
    print("=" * 60)
