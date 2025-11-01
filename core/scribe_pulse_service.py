#!/usr/bin/env python3
"""
Scribe Pulse Service - Pulse-Native Inference Service

Listens for scribe.encode.request Pulses, performs multimodal fusion,
emits scribe.encode.response Pulses with embeddings.

This enables empirical measurement of Pulse-based vs internal inference.

Author: Manus AI
"""

import asyncio
import json
import websockets
from datetime import datetime
from typing import Dict, Any
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scribe.scribe_model import ScribeModel

class ScribePulseService:
    def __init__(self):
        self.ws = None
        self.model = None
        self.request_count = 0
        
    async def connect_pulsemesh(self):
        """Connect to PulseMesh"""
        try:
            self.ws = await websockets.connect('ws://localhost:8088/ws/mesh/scribe_pulse_service')
            print("[Scribe Pulse Service] Connected to PulseMesh")
            return True
        except Exception as e:
            print(f"[Scribe Pulse Service] Failed to connect: {e}")
            return False
    
    def load_model(self):
        """Load Scribe model"""
        print("[Scribe Pulse Service] Loading Scribe model...")
        try:
            self.model = ScribeModel()
            print("[Scribe Pulse Service] Model loaded successfully")
            return True
        except Exception as e:
            print(f"[Scribe Pulse Service] Failed to load model: {e}")
            return False
    
    async def handle_encode_request(self, request: Dict[str, Any]):
        """
        Handle scribe.encode.request Pulse
        
        Request format:
        {
            "type": "scribe.encode.request",
            "request_id": "unique_id",
            "source": "batch_validation",
            "modalities": {
                "narrative": "text...",
                "modal": "text...",
                "temporal": "text...",
                "role": "text..."
            },
            "timestamp": "ISO8601"
        }
        """
        request_id = request.get('request_id')
        source = request.get('source', 'unknown')
        modalities = request.get('modalities', {})
        
        print(f"[Scribe Pulse Service] Encoding request {request_id} from {source}")
        
        start_time = datetime.utcnow()
        
        try:
            # Perform multimodal fusion
            result = self.model.encode_multimodal(modalities)
            
            end_time = datetime.utcnow()
            latency_ms = (end_time - start_time).total_seconds() * 1000
            
            # Emit response Pulse
            response = {
                'type': 'scribe.encode.response',
                'request_id': request_id,
                'source': 'scribe_pulse_service',
                'target': source,
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'result': {
                    'wisp_embedding': result['wisp'].tolist(),
                    'coherence': {
                        'mean': float(result['coherence']['mean']),
                        'narrative': float(result['coherence']['narrative']),
                        'modal': float(result['coherence']['modal']),
                        'temporal': float(result['coherence']['temporal']),
                        'role': float(result['coherence']['role'])
                    },
                    'attention_weights': result['attention_weights'].tolist(),
                    'semantic_drift': float(result['semantic_drift']),
                    'latency_ms': latency_ms
                },
                'success': True
            }
            
            await self.ws.send(json.dumps(response))
            
            self.request_count += 1
            print(f"[Scribe Pulse Service] Completed request {request_id} (latency: {latency_ms:.2f}ms, total: {self.request_count})")
            
        except Exception as e:
            print(f"[Scribe Pulse Service] Error processing request {request_id}: {e}")
            
            # Emit error response
            error_response = {
                'type': 'scribe.encode.response',
                'request_id': request_id,
                'source': 'scribe_pulse_service',
                'target': source,
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'success': False,
                'error': str(e)
            }
            
            await self.ws.send(json.dumps(error_response))
    
    async def listen(self):
        """Listen for encode requests"""
        print("[Scribe Pulse Service] Listening for scribe.encode.request Pulses...")
        
        while True:
            try:
                message_raw = await self.ws.recv()
                message = json.loads(message_raw)
                
                message_type = message.get('type')
                
                if message_type == 'scribe.encode.request':
                    await self.handle_encode_request(message)
                
            except websockets.exceptions.ConnectionClosed:
                print("[Scribe Pulse Service] Connection closed, reconnecting...")
                await asyncio.sleep(2)
                if await self.connect_pulsemesh():
                    print("[Scribe Pulse Service] Reconnected successfully")
                else:
                    print("[Scribe Pulse Service] Reconnection failed")
                    break
            except Exception as e:
                print(f"[Scribe Pulse Service] Error: {e}")
                await asyncio.sleep(1)

async def main():
    service = ScribePulseService()
    
    # Load model
    if not service.load_model():
        print("[Scribe Pulse Service] Failed to load model, exiting")
        return
    
    # Connect to PulseMesh
    if not await service.connect_pulsemesh():
        print("[Scribe Pulse Service] Failed to connect to PulseMesh, exiting")
        return
    
    print("[Scribe Pulse Service] Ready to serve Scribe inference via Pulses")
    
    # Listen for requests
    await service.listen()

if __name__ == "__main__":
    asyncio.run(main())
