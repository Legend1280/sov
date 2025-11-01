"""
Scribe Service API v1.0
FastAPI service for Scribe Fusion Transformer inference

Provides endpoints for:
- Wisp composition (fusing 4 modal embeddings)
- Model health checks
- Batch inference

Author: Sovereignty Foundation
"""

import torch
import torch.nn.functional as F
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import numpy as np
from datetime import datetime
import logging
import os

from scribe_fusion_model import ScribeFusionTransformer, create_scribe_fusion_model

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Scribe Fusion Service",
    description="Multimodal embedding fusion for Wisp composition",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model instance
_model = None
_device = None
_model_path = None
_model_loaded = False

# Configuration
MODEL_DIR = os.environ.get("SCRIBE_MODEL_DIR", "/home/ubuntu/sov/core/models")
DEFAULT_MODEL = "scribe_fusion_v1.0_production.pt"
EMBEDDING_DIM = 384


# ============================================================================
# Pydantic Models
# ============================================================================

class WispInput(BaseModel):
    """Input for Wisp composition"""
    narrative: List[float] = Field(..., description="Narrative embedding (384-dim)")
    modal: List[float] = Field(..., description="Modal embedding (384-dim)")
    temporal: List[float] = Field(..., description="Temporal embedding (384-dim)")
    role: List[float] = Field(..., description="Role embedding (384-dim)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "narrative": [0.1] * 384,
                "modal": [0.2] * 384,
                "temporal": [0.3] * 384,
                "role": [0.4] * 384
            }
        }


class WispOutput(BaseModel):
    """Output from Wisp composition"""
    wisp: List[float] = Field(..., description="Fused Wisp embedding (384-dim)")
    coherence: float = Field(..., description="Self-coherence score (0.0-1.0)")
    timestamp: str = Field(..., description="Composition timestamp (ISO 8601)")
    model_version: str = Field(..., description="Scribe model version")


class BatchWispInput(BaseModel):
    """Batch input for multiple Wisp compositions"""
    wisps: List[WispInput] = Field(..., description="List of Wisp inputs")
    
    class Config:
        json_schema_extra = {
            "example": {
                "wisps": [
                    {
                        "narrative": [0.1] * 384,
                        "modal": [0.2] * 384,
                        "temporal": [0.3] * 384,
                        "role": [0.4] * 384
                    }
                ]
            }
        }


class BatchWispOutput(BaseModel):
    """Batch output from multiple Wisp compositions"""
    wisps: List[WispOutput] = Field(..., description="List of fused Wisps")
    batch_size: int = Field(..., description="Number of Wisps processed")
    processing_time_ms: float = Field(..., description="Total processing time in milliseconds")


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    model_loaded: bool = Field(..., description="Whether model is loaded")
    model_path: Optional[str] = Field(None, description="Path to loaded model")
    device: str = Field(..., description="Device (cuda/cpu)")
    embedding_dim: int = Field(..., description="Embedding dimension")
    timestamp: str = Field(..., description="Current timestamp")


# ============================================================================
# Model Management
# ============================================================================

def load_model(model_name: str = DEFAULT_MODEL) -> None:
    """Load Scribe Fusion model into memory"""
    global _model, _device, _model_path, _model_loaded
    
    try:
        # Determine device
        _device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f"Using device: {_device}")
        
        # Construct model path
        _model_path = os.path.join(MODEL_DIR, model_name)
        
        if not os.path.exists(_model_path):
            raise FileNotFoundError(f"Model file not found: {_model_path}")
        
        logger.info(f"Loading Scribe model from: {_model_path}")
        
        # Create model architecture
        _model = ScribeFusionTransformer(
            embedding_dim=EMBEDDING_DIM,
            num_heads=8,
            num_layers=4,
            feedforward_dim=1536,
            dropout=0.1
        ).to(_device)
        
        # Load trained weights
        checkpoint = torch.load(_model_path, map_location=_device)
        
        # Handle different checkpoint formats
        if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
            _model.load_state_dict(checkpoint['model_state_dict'])
            logger.info(f"Loaded model from checkpoint (epoch: {checkpoint.get('epoch', 'unknown')})")
        else:
            _model.load_state_dict(checkpoint)
            logger.info("Loaded model state dict")
        
        # Set to evaluation mode
        _model.eval()
        _model_loaded = True
        
        # Count parameters
        total_params = sum(p.numel() for p in _model.parameters())
        logger.info(f"Model loaded successfully ({total_params:,} parameters)")
        
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        _model_loaded = False
        raise


def get_model():
    """Get loaded model instance"""
    if not _model_loaded or _model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return _model


def compute_coherence(wisp_emb: torch.Tensor, narrative_emb: torch.Tensor) -> float:
    """
    Compute self-coherence score between fused Wisp and original narrative
    
    Args:
        wisp_emb: Fused Wisp embedding (batch_size, 384)
        narrative_emb: Original narrative embedding (batch_size, 384)
        
    Returns:
        coherence: Cosine similarity score (0.0-1.0)
    """
    # Normalize embeddings
    wisp_norm = F.normalize(wisp_emb, p=2, dim=1)
    narrative_norm = F.normalize(narrative_emb, p=2, dim=1)
    
    # Compute cosine similarity
    similarity = (wisp_norm * narrative_norm).sum(dim=1)
    
    # Return mean coherence across batch
    return similarity.mean().item()


# ============================================================================
# API Endpoints
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Load model on service startup"""
    logger.info("Starting Scribe Fusion Service...")
    try:
        load_model()
        logger.info("✅ Scribe service ready")
    except Exception as e:
        logger.error(f"❌ Failed to start service: {e}")


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy" if _model_loaded else "unhealthy",
        model_loaded=_model_loaded,
        model_path=_model_path,
        device=str(_device) if _device else "unknown",
        embedding_dim=EMBEDDING_DIM,
        timestamp=datetime.utcnow().isoformat() + "Z"
    )


@app.post("/compose", response_model=WispOutput)
async def compose_wisp(wisp_input: WispInput):
    """
    Compose a Wisp from 4 modal embeddings
    
    Takes narrative, modal, temporal, and role embeddings and fuses them
    into a unified 384-dimensional Wisp embedding.
    """
    try:
        model = get_model()
        
        # Validate input dimensions
        if len(wisp_input.narrative) != EMBEDDING_DIM:
            raise HTTPException(status_code=400, detail=f"Narrative embedding must be {EMBEDDING_DIM}-dimensional")
        if len(wisp_input.modal) != EMBEDDING_DIM:
            raise HTTPException(status_code=400, detail=f"Modal embedding must be {EMBEDDING_DIM}-dimensional")
        if len(wisp_input.temporal) != EMBEDDING_DIM:
            raise HTTPException(status_code=400, detail=f"Temporal embedding must be {EMBEDDING_DIM}-dimensional")
        if len(wisp_input.role) != EMBEDDING_DIM:
            raise HTTPException(status_code=400, detail=f"Role embedding must be {EMBEDDING_DIM}-dimensional")
        
        # Convert to tensors
        narrative_emb = torch.tensor([wisp_input.narrative], dtype=torch.float32).to(_device)
        modal_emb = torch.tensor([wisp_input.modal], dtype=torch.float32).to(_device)
        temporal_emb = torch.tensor([wisp_input.temporal], dtype=torch.float32).to(_device)
        role_emb = torch.tensor([wisp_input.role], dtype=torch.float32).to(_device)
        
        # Run inference
        with torch.no_grad():
            fused_emb = model(narrative_emb, modal_emb, temporal_emb, role_emb)
        
        # Compute coherence
        coherence = compute_coherence(fused_emb, narrative_emb)
        
        # Convert to list
        wisp_vector = fused_emb.cpu().numpy()[0].tolist()
        
        return WispOutput(
            wisp=wisp_vector,
            coherence=round(coherence, 4),
            timestamp=datetime.utcnow().isoformat() + "Z",
            model_version="scribe_fusion_v1.0"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Composition error: {e}")
        raise HTTPException(status_code=500, detail=f"Composition failed: {str(e)}")


@app.post("/compose/batch", response_model=BatchWispOutput)
async def compose_wisp_batch(batch_input: BatchWispInput):
    """
    Compose multiple Wisps in batch
    
    More efficient than individual requests for large batches.
    """
    try:
        model = get_model()
        start_time = datetime.utcnow()
        
        batch_size = len(batch_input.wisps)
        
        if batch_size == 0:
            raise HTTPException(status_code=400, detail="Batch cannot be empty")
        
        # Collect all embeddings
        narrative_list = []
        modal_list = []
        temporal_list = []
        role_list = []
        
        for wisp in batch_input.wisps:
            # Validate dimensions
            if len(wisp.narrative) != EMBEDDING_DIM:
                raise HTTPException(status_code=400, detail=f"All embeddings must be {EMBEDDING_DIM}-dimensional")
            
            narrative_list.append(wisp.narrative)
            modal_list.append(wisp.modal)
            temporal_list.append(wisp.temporal)
            role_list.append(wisp.role)
        
        # Convert to tensors
        narrative_batch = torch.tensor(narrative_list, dtype=torch.float32).to(_device)
        modal_batch = torch.tensor(modal_list, dtype=torch.float32).to(_device)
        temporal_batch = torch.tensor(temporal_list, dtype=torch.float32).to(_device)
        role_batch = torch.tensor(role_list, dtype=torch.float32).to(_device)
        
        # Run batch inference
        with torch.no_grad():
            fused_batch = model(narrative_batch, modal_batch, temporal_batch, role_batch)
        
        # Compute coherence for each
        coherence_scores = []
        for i in range(batch_size):
            coh = compute_coherence(fused_batch[i:i+1], narrative_batch[i:i+1])
            coherence_scores.append(coh)
        
        # Convert to list
        fused_list = fused_batch.cpu().numpy().tolist()
        
        # Build output
        timestamp = datetime.utcnow().isoformat() + "Z"
        wisps_output = []
        
        for i in range(batch_size):
            wisps_output.append(WispOutput(
                wisp=fused_list[i],
                coherence=round(coherence_scores[i], 4),
                timestamp=timestamp,
                model_version="scribe_fusion_v1.0"
            ))
        
        # Calculate processing time
        end_time = datetime.utcnow()
        processing_time_ms = (end_time - start_time).total_seconds() * 1000
        
        return BatchWispOutput(
            wisps=wisps_output,
            batch_size=batch_size,
            processing_time_ms=round(processing_time_ms, 2)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch composition error: {e}")
        raise HTTPException(status_code=500, detail=f"Batch composition failed: {str(e)}")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Scribe Fusion Service",
        "version": "1.0.0",
        "status": "running" if _model_loaded else "model not loaded",
        "endpoints": {
            "health": "/health",
            "compose": "/compose",
            "batch_compose": "/compose/batch",
            "docs": "/docs"
        }
    }


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment or default to 8089
    port = int(os.environ.get("SCRIBE_PORT", 8089))
    
    logger.info(f"Starting Scribe Fusion Service on port {port}...")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
