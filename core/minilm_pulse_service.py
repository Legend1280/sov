#!/usr/bin/env python3
"""
MiniLM Pulse Service - Pulse-Native Baseline Inference Service

Listens for minilm.encode.request Pulses, performs embedding,
emits minilm.encode.response Pulses.

This enables empirical measurement of Pulse-based vs internal inference.

Author: Manus AI
"""

import asyncio
import json
import websockets
from datetime import datetime
from typing import Dict, Any
from sentence_transformers import SentenceTransformer

class MiniLMPulseService:
    def __init__(self):
        self.ws = None
        self.model = None
        self.request_count = 0
        
    async def connect_pulsemesh(self):
        """Connect to PulseMesh"""
        try:
            self.ws = await websockets.connect('ws://localhost:8088/ws/mesh/minilm_pulse_service')
            print("[MiniLM Pulse Service] Connected to PulseMesh")
            return True
        except Exception as e:
            print(f"[MiniLM Pulse Service] Failed to connect: {e}")
            return False
    
    def load_model(self):
        """Load MiniLM model"""
        print("[MiniLM Pulse Service] Loading MiniLM model...")
        try:
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            print("[MiniLM Pulse Service] Model loaded successfully")
            return True
        except Exception as e:
            print(f"[MiniLM Pulse Service] Failed to load model: {e}")
            return False
    
    async def handle_encode_request(self, request: Dict[str, Any]):
        """
        Handle minilm.encode.request Pulse
        
        Request format:
        {
            "type": "minilm.encode.request",
            "request_id": "unique_id",
            "source": "batch_validation",
            "text": "text to encode...",
            "timestamp": "ISO8601"
        }
        """
        request_id = request.get('request_id')
        source = request.get('source', 'unknown')
        text = request.get('text', '')
        
        print(f"[MiniLM Pulse Service] Encoding request {request_id} from {source}")
        
        start_time = datetime.utcnow()
        
        try:
            # Perform encoding
            embedding = self.model.encode(text, convert_to_numpy=True)
            
            end_time = datetime.utcnow()
            latency_ms = (end_time - start_time).total_seconds() * 1000
            
            # Emit response Pulse
            response = {
                'type': 'minilm.encode.response',
                'request_id': request_id,
                'source': 'minilm_pulse_service',
                'target': source,
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'result': {
                    'embedding': embedding.tolist(),
                    'latency_ms': latency_ms
                },
                'success': True
            }
            
            await self.ws.send(json.dumps(response))
            
            self.request_count += 1
            print(f"[MiniLM Pulse Service] Completed request {request_id} (latency: {latency_ms:.2f}ms, total: {self.request_count})")
            
        except Exception as e:
            print(f"[MiniLM Pulse Service] Error processing request {request_id}: {e}")
            
            # Emit error response
            error_response = {
                'type': 'minilm.encode.response',
                'request_id': request_id,
                'source': 'minilm_pulse_service',
                'target': source,
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'success': False,
                'error': str(e)
            }
            
            await self.ws.send(json.dumps(error_response))
    
    async def listen(self):
        """Listen for encode requests"""
        print("[MiniLM Pulse Service] Listening for minilm.encode.request Pulses...")
        
        while True:
            try:
                message_raw = await self.ws.recv()
                message = json.loads(message_raw)
                
                message_type = message.get('type')
                
                if message_type == 'minilm.encode.request':
                    await self.handle_encode_request(message)
                
            except websockets.exceptions.ConnectionClosed:
                print("[MiniLM Pulse Service] Connection closed, reconnecting...")
                await asyncio.sleep(2)
                if await self.connect_pulsemesh():
                    print("[MiniLM Pulse Service] Reconnected successfully")
                else:
                    print("[MiniLM Pulse Service] Reconnection failed")
                    break
            except Exception as e:
                print(f"[MiniLM Pulse Service] Error: {e}")
                await asyncio.sleep(1)

async def main():
    service = MiniLMPulseService()
    
    # Load model
    if not service.load_model():
        print("[MiniLM Pulse Service] Failed to load model, exiting")
        return
    
    # Connect to PulseMesh
    if not await service.connect_pulsemesh():
        print("[MiniLM Pulse Service] Failed to connect to PulseMesh, exiting")
        return
    
    print("[MiniLM Pulse Service] Ready to serve MiniLM inference via Pulses")
    
    # Listen for requests
    await service.listen()

if __name__ == "__main__":
    asyncio.run(main())
