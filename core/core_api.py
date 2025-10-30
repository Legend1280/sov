"""
Core API - Semantic Kernel Interface
FastAPI layer over the Core reasoning engine

Endpoints:
- POST /api/core/ingest - Ingest new object
- GET /api/core/object/{id} - Get reasoned object
- GET /api/core/reason/{id} - Reason about object
- GET /api/core/similar/{id} - Find similar objects
- GET /api/core/query - Query objects
- GET /api/core/types - List object types
- GET / - Health check
"""

import os
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from reasoner import get_reasoner

# Initialize FastAPI
app = FastAPI(
    title="Core - Semantic Kernel",
    version="1.0.0",
    description="Semantic reasoning engine for the Sovereignty Stack"
)

# CORS - Allow Mirror and other frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:5000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:5000",
        "*"  # Allow all for development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize reasoner
DB_PATH = os.getenv("CORE_DB_PATH", "./core.db")
ONTOLOGY_DIR = os.getenv("ONTOLOGY_DIR", "./ontology")

reasoner = get_reasoner(DB_PATH, ONTOLOGY_DIR)

# ==================== REQUEST/RESPONSE MODELS ====================

class IngestRequest(BaseModel):
    object_type: str
    data: Dict[str, Any]
    actor: Optional[str] = "system"

class IngestResponse(BaseModel):
    success: bool
    object_id: str
    reasoned_object: Dict[str, Any]

class ReasonResponse(BaseModel):
    reasoned_object: Dict[str, Any]

class SimilarResponse(BaseModel):
    object_id: str
    relations: List[Dict[str, Any]]

class QueryResponse(BaseModel):
    objects: List[Dict[str, Any]]
    count: int

class TypesResponse(BaseModel):
    types: List[str]

# ==================== ENDPOINTS ====================

@app.get("/")
def health_check():
    """Health check endpoint"""
    return {
        "service": "Core Semantic Kernel",
        "version": "1.0.0",
        "status": "operational",
        "components": {
            "reasoner": "active",
            "ontology": "loaded",
            "embeddings": "ready",
            "sage": "active",
            "storage": "connected"
        }
    }

@app.post("/api/core/ingest")
def ingest_object(request: IngestRequest):
    """
    Ingest a new object into Core
    
    Pipeline:
    1. Validate against ontology
    2. Generate embedding
    3. Run SAGE validation
    4. Store object + vector + metadata
    5. Log provenance
    6. Return ReasonedObject
    """
    try:
        reasoned = reasoner.ingest(
            request.object_type,
            request.data,
            request.actor
        )
        
        return {
            "success": True,
            "object_id": reasoned["symbolic"]["id"],
            "reasoned_object": reasoned
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@app.get("/api/core/object/{object_id}", response_model=ReasonResponse)
def get_object(object_id: str):
    """
    Get a reasoned object by ID
    
    Returns ReasonedObject with:
    - symbolic (ontology data)
    - vector (embedding + relations)
    - provenance (audit trail)
    - sage (governance metadata)
    """
    try:
        reasoned = reasoner.reason(object_id)
        return {"reasoned_object": reasoned}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@app.get("/api/core/reason/{object_id}", response_model=ReasonResponse)
def reason_about(object_id: str):
    """
    Perform reasoning on an object
    
    Same as /object/{id} but more explicit about reasoning
    """
    return get_object(object_id)

@app.get("/api/core/similar/{object_id}", response_model=SimilarResponse)
def find_similar(object_id: str, top_k: int = 5):
    """
    Find semantically similar objects
    
    Uses vector embeddings to find related objects
    """
    try:
        relations = reasoner.infer_relations(object_id, top_k)
        return {
            "object_id": object_id,
            "relations": relations
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@app.get("/api/core/query", response_model=QueryResponse)
def query_objects(object_type: Optional[str] = None, limit: int = 100):
    """
    Query objects from Core
    
    Args:
        object_type: Filter by type (optional)
        limit: Maximum results
    """
    try:
        objects = reasoner.query(object_type, limit)
        return {
            "objects": objects,
            "count": len(objects)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@app.get("/api/core/types", response_model=TypesResponse)
def list_types():
    """
    List all available object types from ontology
    """
    try:
        types = reasoner.ontology.list_types()
        return {"types": types}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

# ==================== FINANCIAL DOMAIN ENDPOINTS ====================
# These are specific to DexaBooks but use the Core reasoning engine

class TransactionCreate(BaseModel):
    amount: float
    date: str
    description: str
    transaction_type: str  # "income" or "expense"
    category: Optional[str] = None
    vendor: Optional[str] = None

@app.post("/api/financial/transaction")
def create_transaction(transaction: TransactionCreate):
    """Create a financial transaction (DexaBooks)"""
    try:
        # Convert to Core object
        reasoned = reasoner.ingest(
            "Transaction",
            transaction.dict(),
            "DexaBooks"
        )
        
        # Ensure it's JSON serializable
        import json
        json_str = json.dumps(reasoned)
        return json.loads(json_str)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@app.get("/api/financial/transactions")
def list_transactions(limit: int = 100):
    """List all transactions"""
    try:
        transactions = reasoner.query("Transaction", limit)
        return {
            "transactions": transactions,
            "count": len(transactions)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@app.get("/api/financial/analytics/summary")
def financial_summary():
    """Get financial summary"""
    try:
        transactions = reasoner.query("Transaction", limit=1000)
        
        # Calculate summary
        total_income = sum(
            t["symbolic"]["amount"] 
            for t in transactions 
            if t["symbolic"].get("transaction_type") == "income"
        )
        
        total_expenses = sum(
            abs(t["symbolic"]["amount"])
            for t in transactions 
            if t["symbolic"].get("transaction_type") == "expense"
        )
        
        return {
            "total_income": total_income,
            "total_expenses": total_expenses,
            "net": total_income - total_expenses,
            "transaction_count": len(transactions)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
