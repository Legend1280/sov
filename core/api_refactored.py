"""
Loom Lite API v2.0 - Refactored
A thin viewer layer that consumes Core API services

This API handles:
- Document-specific UI features (folders, analytics, views)
- Proxying core operations to Core API (ingestion, search, provenance)

Core operations are delegated to the Core API at http://localhost:8001
"""
import os
import sqlite3
import json
import httpx
from datetime import datetime
from typing import Optional, List
from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

# Import LoomLite-specific modules (UI/UX features)
from semantic_folders import build_semantic_folders, get_saved_views, create_saved_view, delete_saved_view
from analytics import track_folder_view, track_pin_event, update_dwell_time, get_folder_stats, get_document_stats, get_trending_documents
from file_system import get_top_hits, get_pinned_folders, get_standard_folder, get_standard_folders_by_type, get_standard_folders_by_date, get_semantic_folder

# Core API configuration
CORE_API_URL = os.environ.get("CORE_API_URL", "http://localhost:8001")
CORE_API_TIMEOUT = 30.0

app = FastAPI(
    title="LoomLite Viewer API",
    version="2.0.0",
    description="Document knowledge navigator - powered by Core API"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://loomlite.vercel.app",
        "http://localhost:3000",
        "http://localhost:5000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database path
DB_PATH = os.environ.get("DB_PATH", "./loom_lite.db")

# HTTP client for Core API
http_client = httpx.AsyncClient(timeout=CORE_API_TIMEOUT)

# ==================== HEALTH CHECK ====================

@app.get("/")
def root():
    """Health check"""
    return {
        "service": "LoomLite Viewer",
        "version": "2.0.0",
        "status": "operational",
        "core_api": CORE_API_URL
    }

# ==================== CORE API PROXY ENDPOINTS ====================

class IngestionRequest(BaseModel):
    content: str
    title: Optional[str] = None
    source_uri: Optional[str] = None
    object_type: str = "document"

@app.post("/api/ingest")
async def ingest_document(request: IngestionRequest):
    """
    Proxy document ingestion to Core API
    """
    try:
        response = await http_client.post(
            f"{CORE_API_URL}/api/core/ingest",
            json=request.dict()
        )
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Core API error: {str(e)}")

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload file and proxy to Core API
    """
    try:
        content = await file.read()
        
        # Send to Core API
        response = await http_client.post(
            f"{CORE_API_URL}/api/core/ingest",
            json={
                "content": content.decode('utf-8', errors='ignore'),
                "title": file.filename,
                "source_uri": f"upload://{file.filename}",
                "object_type": "document"
            }
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

class SearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 10

@app.post("/api/search")
async def search_documents(request: SearchRequest):
    """
    Proxy semantic search to Core API
    """
    try:
        response = await http_client.post(
            f"{CORE_API_URL}/api/core/search",
            json=request.dict()
        )
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.get("/api/documents")
async def list_documents():
    """
    Proxy document list to Core API
    """
    try:
        response = await http_client.get(f"{CORE_API_URL}/api/core/documents")
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Core API error: {str(e)}")

@app.get("/api/documents/{doc_id}")
async def get_document(doc_id: str):
    """
    Proxy document retrieval to Core API
    """
    try:
        response = await http_client.get(f"{CORE_API_URL}/api/core/documents/{doc_id}")
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as e:
        raise HTTPException(status_code=404 if e.response.status_code == 404 else 500, 
                          detail=f"Document not found" if e.response.status_code == 404 else f"Core API error: {str(e)}")

@app.get("/api/provenance/{doc_id}")
async def get_provenance(doc_id: str):
    """
    Proxy provenance to Core API
    """
    try:
        response = await http_client.get(f"{CORE_API_URL}/api/core/provenance/{doc_id}")
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Core API error: {str(e)}")

@app.get("/api/jobs/{job_id}")
async def get_job_status(job_id: str):
    """
    Proxy job status to Core API
    """
    try:
        response = await http_client.get(f"{CORE_API_URL}/api/core/jobs/{job_id}")
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as e:
        raise HTTPException(status_code=404 if e.response.status_code == 404 else 500,
                          detail=f"Job not found" if e.response.status_code == 404 else f"Core API error: {str(e)}")

# ==================== LOOMLITE-SPECIFIC FEATURES ====================

@app.get("/api/folders/top-hits")
def get_top_hits_folder():
    """Get top hits folder (LoomLite-specific analytics)"""
    return get_top_hits(DB_PATH)

@app.get("/api/folders/pinned")
def get_pinned_folders_list():
    """Get pinned folders (LoomLite-specific)"""
    return get_pinned_folders(DB_PATH)

@app.get("/api/folders/standard/{folder_type}")
def get_standard_folder_view(folder_type: str):
    """Get standard folder view (LoomLite-specific)"""
    return get_standard_folder(DB_PATH, folder_type)

@app.get("/api/folders/by-type")
def get_folders_by_type():
    """Get folders organized by type (LoomLite-specific)"""
    return get_standard_folders_by_type(DB_PATH)

@app.get("/api/folders/by-date")
def get_folders_by_date():
    """Get folders organized by date (LoomLite-specific)"""
    return get_standard_folders_by_date(DB_PATH)

@app.get("/api/folders/semantic/{concept_id}")
def get_semantic_folder_view(concept_id: str):
    """Get semantic folder view (LoomLite-specific)"""
    return get_semantic_folder(DB_PATH, concept_id)

@app.get("/api/views")
def list_saved_views():
    """Get saved views (LoomLite-specific)"""
    return get_saved_views(DB_PATH)

class CreateViewRequest(BaseModel):
    name: str
    view_type: str
    config: dict

@app.post("/api/views")
def create_view(request: CreateViewRequest):
    """Create saved view (LoomLite-specific)"""
    return create_saved_view(DB_PATH, request.name, request.view_type, request.config)

@app.delete("/api/views/{view_id}")
def delete_view(view_id: str):
    """Delete saved view (LoomLite-specific)"""
    return delete_saved_view(DB_PATH, view_id)

# Analytics endpoints
@app.post("/api/analytics/folder-view")
def track_folder(folder_id: str):
    """Track folder view (LoomLite-specific analytics)"""
    track_folder_view(DB_PATH, folder_id)
    return {"status": "tracked"}

@app.post("/api/analytics/pin")
def track_pin(folder_id: str, pinned: bool):
    """Track pin event (LoomLite-specific analytics)"""
    track_pin_event(DB_PATH, folder_id, pinned)
    return {"status": "tracked"}

@app.post("/api/analytics/dwell")
def track_dwell(doc_id: str, dwell_time: int):
    """Track dwell time (LoomLite-specific analytics)"""
    update_dwell_time(DB_PATH, doc_id, dwell_time)
    return {"status": "tracked"}

@app.get("/api/analytics/folder-stats/{folder_id}")
def get_folder_statistics(folder_id: str):
    """Get folder statistics (LoomLite-specific)"""
    return get_folder_stats(DB_PATH, folder_id)

@app.get("/api/analytics/document-stats/{doc_id}")
def get_document_statistics(doc_id: str):
    """Get document statistics (LoomLite-specific)"""
    return get_document_stats(DB_PATH, doc_id)

@app.get("/api/analytics/trending")
def get_trending():
    """Get trending documents (LoomLite-specific)"""
    return get_trending_documents(DB_PATH)

# ==================== SHUTDOWN ====================

@app.on_event("shutdown")
async def shutdown_event():
    """Close HTTP client on shutdown"""
    await http_client.aclose()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
