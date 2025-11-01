"""
Scribe Listener - Pulse-Native Service
Listens to PulseMesh for Wisp composition requests

Architecture:
- Subscribes to "scribe.compose" topic
- Loads Scribe Fusion Transformer model
- Fuses 4 modal embeddings into unified Wisp
- Publishes result to "scribe.composed" topic

Author: Sovereignty Foundation
"""

import asyncio
import websockets
import json
import torch
import torch.nn.functional as F
import numpy as np
from datetime import datetime
import logging
import os
import sys

# Add core to path
sys.path.insert(0, '/home/ubuntu/sov/core')

from scribe_fusion_model import ScribeFusionTransformer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [Scribe] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# Configuration
PULSEMESH_URL = os.environ.get("PULSEMESH_URL", "ws://localhost:8088/ws/mesh/scribe")
MODEL_DIR = os.environ.get("SCRIBE_MODEL_DIR", "/home/ubuntu/sov/core/models")
MODEL_NAME = "scribe_fusion_v1.0_production.pt"
EMBEDDING_DIM = 384

# Global model
_model = None
_device = None
_model_loaded = False


def load_model():
    """Load Scribe Fusion model"""
    global _model, _device, _model_loaded
    
    try:
        # Determine device
        _device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f"Using device: {_device}")
        
        # Model path
        model_path = os.path.join(MODEL_DIR, MODEL_NAME)
        
        if not os.path.exists(model_path):
            logger.warning(f"Model file not found: {model_path}")
            logger.warning("Creating untrained model for testing...")
            
            # Create untrained model
            _model = ScribeFusionTransformer(
                embedding_dim=EMBEDDING_DIM,
                num_heads=8,
                num_layers=4,
                feedforward_dim=1536,
                dropout=0.1
            ).to(_device)
            
            _model.eval()
            _model_loaded = True
            logger.info("⚠️  Using UNTRAINED model (for testing only)")
            return
        
        logger.info(f"Loading model from: {model_path}")
        
        # Create model architecture
        _model = ScribeFusionTransformer(
            embedding_dim=EMBEDDING_DIM,
            num_heads=8,
            num_layers=4,
            feedforward_dim=1536,
            dropout=0.1
        ).to(_device)
        
        # Load weights
        checkpoint = torch.load(model_path, map_location=_device, weights_only=False)
        
        if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
            _model.load_state_dict(checkpoint['model_state_dict'])
            logger.info(f"Loaded trained model (epoch: {checkpoint.get('epoch', 'unknown')})")
        else:
            _model.load_state_dict(checkpoint)
            logger.info("Loaded model weights")
        
        _model.eval()
        _model_loaded = True
        
        # Count parameters
        total_params = sum(p.numel() for p in _model.parameters())
        logger.info(f"✅ Model loaded ({total_params:,} parameters)")
        
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        _model_loaded = False
        raise


def compute_coherence(wisp_emb: torch.Tensor, narrative_emb: torch.Tensor) -> float:
    """Compute coherence between fused Wisp and narrative"""
    wisp_norm = F.normalize(wisp_emb, p=2, dim=1)
    narrative_norm = F.normalize(narrative_emb, p=2, dim=1)
    similarity = (wisp_norm * narrative_norm).sum(dim=1)
    return similarity.mean().item()


async def compose_wisp(narrative, modal, temporal, role):
    """
    Compose Wisp from 4 modal embeddings
    
    Args:
        narrative: 384-dim list
        modal: 384-dim list
        temporal: 384-dim list
        role: 384-dim list
        
    Returns:
        dict with wisp, coherence, timestamp
    """
    if not _model_loaded:
        raise Exception("Model not loaded")
    
    # Validate dimensions
    if len(narrative) != EMBEDDING_DIM:
        raise ValueError(f"Narrative must be {EMBEDDING_DIM}-dimensional")
    if len(modal) != EMBEDDING_DIM:
        raise ValueError(f"Modal must be {EMBEDDING_DIM}-dimensional")
    if len(temporal) != EMBEDDING_DIM:
        raise ValueError(f"Temporal must be {EMBEDDING_DIM}-dimensional")
    if len(role) != EMBEDDING_DIM:
        raise ValueError(f"Role must be {EMBEDDING_DIM}-dimensional")
    
    # Convert to tensors
    narrative_emb = torch.tensor([narrative], dtype=torch.float32).to(_device)
    modal_emb = torch.tensor([modal], dtype=torch.float32).to(_device)
    temporal_emb = torch.tensor([temporal], dtype=torch.float32).to(_device)
    role_emb = torch.tensor([role], dtype=torch.float32).to(_device)
    
    # Run inference
    with torch.no_grad():
        fused_emb = _model(narrative_emb, modal_emb, temporal_emb, role_emb)
    
    # Compute coherence
    coherence = compute_coherence(fused_emb, narrative_emb)
    
    # Convert to list
    wisp_vector = fused_emb.cpu().numpy()[0].tolist()
    
    return {
        "wisp": wisp_vector,
        "coherence": round(coherence, 4),
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "model_version": "scribe_fusion_v1.0"
    }


async def handle_pulse(pulse):
    """Handle incoming Pulse event"""
    try:
        pulse_type = pulse.get("type")
        payload = pulse.get("payload", {})
        
        if pulse_type == "scribe.compose":
            logger.info(f"Received composition request")
            
            # Extract embeddings
            narrative = payload.get("narrative")
            modal = payload.get("modal")
            temporal = payload.get("temporal")
            role = payload.get("role")
            
            if not all([narrative, modal, temporal, role]):
                raise ValueError("Missing required embeddings")
            
            # Compose Wisp
            result = await compose_wisp(narrative, modal, temporal, role)
            
            logger.info(f"Wisp composed (coherence: {result['coherence']})")
            
            # Build response Pulse
            response = {
                "type": "scribe.composed",
                "source": "scribe",
                "target": pulse.get("source", "mirror"),
                "payload": result,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
            
            return response
            
        else:
            logger.warning(f"Unknown pulse type: {pulse_type}")
            return None
            
    except Exception as e:
        logger.error(f"Error handling pulse: {e}")
        
        # Build error response
        error_response = {
            "type": "scribe.error",
            "source": "scribe",
            "target": pulse.get("source", "mirror"),
            "payload": {
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        }
        
        return error_response


async def listen_to_pulsemesh():
    """Main listener loop"""
    logger.info("Starting Scribe Listener...")
    
    # Load model first
    try:
        load_model()
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        return
    
    logger.info(f"Connecting to PulseMesh: {PULSEMESH_URL}")
    
    while True:
        try:
            async with websockets.connect(PULSEMESH_URL) as websocket:
                logger.info("✅ Connected to PulseMesh")
                logger.info("Listening for Wisp composition requests...")
                
                async for message in websocket:
                    try:
                        pulse = json.loads(message)
                        
                        # Handle pulse
                        response = await handle_pulse(pulse)
                        
                        # Send response if any
                        if response:
                            await websocket.send(json.dumps(response))
                            logger.info(f"Sent response: {response['type']}")
                            
                    except json.JSONDecodeError:
                        logger.error(f"Invalid JSON: {message}")
                    except Exception as e:
                        logger.error(f"Error processing message: {e}")
                        
        except websockets.exceptions.ConnectionClosed:
            logger.warning("Connection closed, reconnecting in 5s...")
            await asyncio.sleep(5)
        except Exception as e:
            logger.error(f"Connection error: {e}")
            logger.info("Retrying in 5s...")
            await asyncio.sleep(5)


if __name__ == "__main__":
    try:
        asyncio.run(listen_to_pulsemesh())
    except KeyboardInterrupt:
        logger.info("Scribe Listener stopped")
