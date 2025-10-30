"""
Core API - Semantic Kernel Interface (Milestone 2)

Clean JSON responses, no Pydantic response models.
Enforces SAGE governance decisions.
Exposes provenance for audit.
"""

from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import tempfile
import os

from reasoner import get_reasoner
from ingest import create_importer

# Initialize FastAPI
app = FastAPI(
    title="Core - Semantic Kernel",
    version="2.0.0",
    description="Governed semantic reasoning engine for the Sovereignty Stack"
)

# CORS - Allow Mirror and other frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize reasoner
reasoner = get_reasoner("./core.db", "./ontology")

# Initialize importer
importer = create_importer(reasoner, reasoner.storage)

# ==================== SANITIZATION ====================

def sanitize_for_json(obj: Any) -> Any:
    """
    Convert any object to JSON-serializable form
    
    - bytes → None (drop)
    - numpy/decimal → float
    - datetime → ISO string
    - UUID → string
    - dict/list → recursive
    """
    if obj is None:
        return None
    
    if isinstance(obj, (str, int, float, bool)):
        return obj
    
    if isinstance(obj, bytes):
        return None  # Drop bytes
    
    # Handle numpy types
    if hasattr(obj, 'item'):  # numpy scalar
        return float(obj.item())
    
    if isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}
    
    if isinstance(obj, (list, tuple)):
        return [sanitize_for_json(item) for item in obj]
    
    # Convert to string as fallback
    return str(obj)

# ==================== REQUEST MODELS ====================

class IngestRequest(BaseModel):
    object_type: str
    data: Dict[str, Any]
    actor: Optional[str] = "system"

# ==================== ENDPOINTS ====================

@app.get("/")
def health_check():
    """Health check endpoint"""
    return JSONResponse({
        "service": "Core Semantic Kernel",
        "version": "2.0.0",
        "status": "operational",
        "milestone": "M2: Sovereignty Loop",
        "components": {
            "reasoner": "active",
            "ontology": "loaded",
            "embeddings": "ready",
            "sage": "enforcing",
            "storage": "connected",
            "provenance": "tracking"
        }
    })

@app.post("/api/core/ingest")
def ingest_object(request: IngestRequest):
    """
    Ingest a new object into Core
    
    Pipeline:
    1. Validate against ontology
    2. Generate embedding
    3. Run SAGE evaluation (returns decision: allow/flag/deny)
    4. Enforce SAGE decision:
       - allow: store normally
       - flag: store with is_validated=false
       - deny: reject, log denial in provenance
    5. Return governed response
    """
    try:
        reasoned = reasoner.ingest(
            request.object_type,
            request.data,
            request.actor
        )
        
        # Extract clean response
        response = {
            "object_id": reasoned["symbolic"]["id"],
            "type": reasoned["object"],
            "fields": {
                k: v for k, v in reasoned["symbolic"].items()
                if k not in ["id", "created_at", "updated_at"]
            },
            "sage": {
                "coherence_score": reasoned["sage"]["coherence_score"],
                "trust_score": reasoned["sage"]["trust_score"],
                "is_validated": reasoned["sage"]["validated"],
                "decision": reasoned["sage"].get("decision", "allow")
            },
            "provenance": {
                "ingested_at": reasoned["symbolic"]["created_at"],
                "embedded": reasoned["vector"]["has_embedding"],
                "checked_by_sage": True
            }
        }
        
        # Sanitize and return
        return JSONResponse(sanitize_for_json(response))
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@app.get("/api/core/object/{object_id}")
def get_object(object_id: str):
    """Get a governed object by ID"""
    try:
        reasoned = reasoner.reason(object_id)
        
        # Clean response
        response = {
            "object_id": reasoned["symbolic"]["id"],
            "type": reasoned["object"],
            "fields": {
                k: v for k, v in reasoned["symbolic"].items()
                if k not in ["id", "created_at", "updated_at"]
            },
            "sage": {
                "coherence_score": reasoned["sage"]["coherence_score"],
                "trust_score": reasoned["sage"]["trust_score"],
                "is_validated": reasoned["sage"]["validated"],
                "decision": reasoned["sage"].get("decision", "allow")
            },
            "vector": {
                "has_embedding": reasoned["vector"]["has_embedding"],
                "dimension": reasoned["vector"]["dimension"],
                "relations_count": len(reasoned["vector"]["relations"])
            },
            "provenance": {
                "created_at": reasoned["symbolic"]["created_at"],
                "updated_at": reasoned["symbolic"]["updated_at"],
                "events_count": len(reasoned["provenance"])
            }
        }
        
        return JSONResponse(sanitize_for_json(response))
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@app.get("/api/core/provenance/{object_id}")
def get_provenance(object_id: str):
    """
    Get provenance timeline for an object
    
    Returns ordered list of events showing:
    - What was done
    - When it was done
    - Who/what did it
    - SAGE decisions
    """
    try:
        reasoned = reasoner.reason(object_id)
        
        # Build timeline from provenance
        timeline = []
        for event in reasoned["provenance"]:
            timeline.append({
                "event": event["action"],
                "ts": event["timestamp"],
                "actor": event["actor"],
                "details": event.get("metadata", {})
            })
        
        response = {
            "object_id": object_id,
            "timeline": timeline
        }
        
        return JSONResponse(sanitize_for_json(response))
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@app.get("/api/core/types")
def list_types():
    """List all available object types from ontology"""
    try:
        types = reasoner.ontology.list_types()
        return JSONResponse({"types": types})
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

# ==================== FINANCIAL DOMAIN ENDPOINTS ====================

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
    return ingest_object(IngestRequest(
        object_type="Transaction",
        data=transaction.dict(),
        actor="DexaBooks"
    ))

@app.get("/api/financial/recent")
def list_recent_transactions(limit: int = 20):
    """
    List recent transactions
    
    For Mirror integration - shows recent governed objects
    """
    try:
        transactions = reasoner.query("Transaction", limit)
        
        # Convert to clean response format
        results = []
        for t in transactions:
            results.append({
                "object_id": t["symbolic"]["id"],
                "type": t["object"],
                "fields": {k: v for k, v in t["symbolic"].items() if k not in ["id", "created_at", "updated_at"]},
                "sage": {
                    "coherence_score": t["sage"]["coherence_score"],
                    "trust_score": t["sage"]["trust_score"],
                    "is_validated": t["sage"]["validated"],
                    "decision": t["sage"].get("decision", "allow")
                },
                "created_at": t["symbolic"]["created_at"]
            })
        
        response = {
            "objects": results,
            "count": len(results)
        }
        
        return JSONResponse(sanitize_for_json(response))
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@app.get("/api/financial/analytics/summary")
def financial_summary():
    """Get financial summary"""
    try:
        transactions = reasoner.query("Transaction", limit=1000)
        
        # Calculate summary
        total_income = sum(
            t["data"]["amount"] 
            for t in transactions 
            if t["data"].get("transaction_type") == "income"
        )
        
        total_expenses = sum(
            abs(t["data"]["amount"])
            for t in transactions 
            if t["data"].get("transaction_type") == "expense"
        )
        
        response = {
            "total_income": total_income,
            "total_expenses": total_expenses,
            "net": total_income - total_expenses,
            "transaction_count": len(transactions)
        }
        
        return JSONResponse(sanitize_for_json(response))
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.post("/api/financial/import")
async def import_financial_file(file: UploadFile = File(...), actor: str = "User"):
    """
    Import structured financial data (Excel/CSV)
    
    Milestone 3: Structured Data Ingestion
    
    Args:
        file: Uploaded Excel or CSV file
        actor: Who initiated the import
        
    Returns:
        Ingestion summary with governance statistics
    """
    try:
        # Validate file type
        if not (file.filename.endswith('.xlsx') or 
                file.filename.endswith('.xls') or 
                file.filename.endswith('.csv')):
            raise HTTPException(
                status_code=400, 
                detail="Only Excel (.xlsx, .xls) and CSV files are supported"
            )
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        try:
            # Ingest file
            result = importer.ingest_file(
                file_path=tmp_path,
                source_name=file.filename,
                actor=actor
            )
            
            # Clean up temp file
            os.unlink(tmp_path)
            
            # Return sanitized result
            return JSONResponse(sanitize_for_json(result))
            
        except Exception as e:
            # Clean up temp file on error
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            raise e
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")


# ==================== KRONOS ENDPOINTS ====================

from kronos import TemporalIndexer

# Initialize Kronos indexer
kronos_indexer = TemporalIndexer(reasoner.storage)

@app.get("/api/kronos/events")
def get_kronos_events(object_id: Optional[str] = None, limit: int = 100):
    """
    Get temporal events for an object or all recent events.
    
    Query params:
        object_id: Filter by specific object (optional)
        limit: Max events to return (default 100)
    """
    try:
        if object_id:
            # Get timeline for specific object
            timeline = kronos_indexer.get_timeline(object_id, limit)
            return JSONResponse({
                "object_id": object_id,
                "events": timeline,
                "count": len(timeline)
            })
        else:
            # Get all recent events (implement if needed)
            return JSONResponse({
                "message": "Specify object_id to get temporal events",
                "example": "/api/kronos/events?object_id=obj_123"
            })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Kronos query failed: {str(e)}")


@app.get("/api/kronos/drift/{object_id}")
def get_drift_analysis(object_id: str):
    """
    Get coherence drift analysis for an object.
    
    Compares baseline to latest state.
    """
    try:
        baseline = kronos_indexer.get_baseline(object_id)
        latest = kronos_indexer.get_latest(object_id)
        
        if not baseline:
            raise HTTPException(status_code=404, detail="No baseline found for object")
        
        if not latest:
            raise HTTPException(status_code=404, detail="No events found for object")
        
        # Calculate drift if vectors available
        drift_data = {
            "object_id": object_id,
            "baseline": {
                "timestamp": baseline["timestamp"],
                "coherence": baseline["coherence_score"],
                "trust": baseline["trust_score"]
            },
            "latest": {
                "timestamp": latest["timestamp"],
                "coherence": latest["coherence_score"],
                "trust": latest["trust_score"]
            },
            "delta": {
                "coherence": latest["coherence_score"] - baseline["coherence_score"],
                "trust": latest["trust_score"] - baseline["trust_score"]
            }
        }
        
        return JSONResponse(drift_data)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Drift analysis failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
