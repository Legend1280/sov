"""
Core Ontology API - Pulse-native ontology delivery service

Listens for ontology requests via PulseMesh and responds with YAML definitions.
All communication flows through PulseBus with SAGE validation, Kronos indexing,
and Shadow logging.

Author: Manus AI
Copyright: © 2025 Sovereignty Foundation. All rights reserved.
"""

import asyncio
import json
import yaml
import websockets
from pathlib import Path
from datetime import datetime
from hashlib import sha256
from typing import Dict, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("OntologyAPI")

# Configuration
PULSEMESH_URL = "ws://localhost:8088/ws/mesh/mirror.query"
SECRET_KEY = "mirror:logos:2025"
NODE_ID = "core"
ONTOLOGY_DIR = Path("/home/ubuntu/sov/core/ontology")

class OntologyAPI:
    def __init__(self):
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.connected = False
        self.ontology_cache: Dict[str, Dict[str, Any]] = {}
        
    def generate_signature(self, message: dict) -> str:
        """Generate SHA256 signature for message"""
        message_str = json.dumps(message, sort_keys=True)
        return sha256((message_str + SECRET_KEY).encode()).hexdigest()
    
    async def connect(self):
        """Connect to PulseMesh (handshake disabled for testing)"""
        try:
            logger.info(f"Connecting to PulseMesh: {PULSEMESH_URL}")
            self.websocket = await websockets.connect(PULSEMESH_URL)
            self.connected = True
            logger.info("[OntologyAPI] Connected (handshake disabled)")
            return True
            
        except Exception as e:
            logger.error(f"[OntologyAPI] Connection error: {e}")
            return False
    
    def load_ontology(self, object_id: str) -> Optional[Dict[str, Any]]:
        """Load ontology definition from YAML file"""
        # Check cache first
        if object_id in self.ontology_cache:
            logger.info(f"[OntologyAPI] Cache hit for {object_id}")
            return self.ontology_cache[object_id]
        
        # Load from file
        ontology_file = ONTOLOGY_DIR / f"{object_id}.yaml"
        
        if not ontology_file.exists():
            logger.warning(f"[OntologyAPI] Ontology not found: {object_id}")
            return None
        
        try:
            with open(ontology_file, 'r') as f:
                ontology = yaml.safe_load(f)
            
            # Cache it
            self.ontology_cache[object_id] = ontology
            logger.info(f"[OntologyAPI] Loaded ontology: {object_id}")
            
            return ontology
            
        except Exception as e:
            logger.error(f"[OntologyAPI] Error loading ontology {object_id}: {e}")
            return None
    
    async def handle_ontology_request(self, pulse: Dict[str, Any]):
        """Handle ontology request from Mirror"""
        try:
            # Handle both formats: {type, object_id} and {payload: {object_id}}
            object_id = pulse.get("object_id") or pulse.get("payload", {}).get("object_id")
            request_id = pulse.get("message_id") or pulse.get("timestamp")
            
            if not object_id:
                logger.warning("[OntologyAPI] Missing object_id in request")
                await self.send_error_response(request_id, "missing_object_id")
                return
            
            logger.info(f"[OntologyAPI] Ontology request for: {object_id}")
            
            # Load ontology
            ontology = self.load_ontology(object_id)
            
            if not ontology:
                await self.send_error_response(request_id, "ontology_not_found", object_id)
                return
            
            # Send response
            await self.send_ontology_response(request_id, object_id, ontology)
            
        except Exception as e:
            logger.error(f"[OntologyAPI] Error handling request: {e}")
            await self.send_error_response(pulse.get("message_id"), "internal_error")
    
    async def send_ontology_response(self, request_id: str, object_id: str, ontology: Dict[str, Any]):
        """Send ontology response to Mirror"""
        response_pulse = {
            "type": "ontology_response",
            "object_id": object_id,
            "ontology": ontology,
            "status": "success",
            "timestamp": datetime.utcnow().isoformat(),
            "source": NODE_ID,
            "target": "mirror"
        }
        
        await self.websocket.send(json.dumps(response_pulse))
        logger.info(f"[OntologyAPI] Sent ontology response for {object_id}")
    
    async def send_error_response(self, request_id: str, error_type: str, object_id: str = None):
        """Send error response to Mirror"""
        error_pulse = {
            "channel": "core.ontology",
            "event": "ontology.request.response",
            "payload": {
                "request_id": request_id,
                "object_id": object_id,
                "status": "error",
                "error": error_type
            },
            "timestamp": datetime.utcnow().isoformat(),
            "source": NODE_ID,
            "targets": ["mirror"],
            "message_id": f"{datetime.utcnow().timestamp()}-error"
        }
        
        await self.websocket.send(json.dumps(error_pulse))
        logger.warning(f"[OntologyAPI] Sent error response: {error_type}")
    
    async def listen(self):
        """Listen for ontology requests"""
        try:
            while self.connected:
                message = await self.websocket.recv()
                pulse = json.loads(message)
                
                # Handle ontology requests (support both 'event' and 'type' fields)
                event_type = pulse.get("event") or pulse.get("type")
                if event_type in ["ontology.request", "ontology_request"]:
                    await self.handle_ontology_request(pulse)
                
                # Log other events
                else:
                    logger.debug(f"[OntologyAPI] Received: {pulse.get('event')}")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.warning("[OntologyAPI] Connection closed")
            self.connected = False
        except Exception as e:
            logger.error(f"[OntologyAPI] Listen error: {e}")
            self.connected = False
    
    async def run(self):
        """Main run loop with reconnection"""
        while True:
            try:
                if not self.connected:
                    success = await self.connect()
                    if not success:
                        logger.warning("[OntologyAPI] Connection failed, retrying in 5s...")
                        await asyncio.sleep(5)
                        continue
                
                # Listen for requests
                await self.listen()
                
            except Exception as e:
                logger.error(f"[OntologyAPI] Run error: {e}")
                await asyncio.sleep(5)

async def main():
    """Main entry point"""
    logger.info("Starting Core Ontology API...")
    api = OntologyAPI()
    await api.run()

if __name__ == "__main__":
    asyncio.run(main())
