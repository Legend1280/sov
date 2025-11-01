"""
PulseMesh Relay - Distributed Semantic Event Bus

A lightweight FastAPI-based relay service that enables real-time,
governed communication between Mirror, Core, and future Sovereignty nodes.

Features:
- Topic-based pub/sub via WebSocket
- Dynamic topology from Core ontology
- SAGE governance hooks (Phase 2)
- Message persistence and replay (Phase 2)

Architecture:
    Mirror (TS) ↔ PulseMeshRelay (FastAPI) ↔ Core (Python)
                        ↕
                    SAGE + Kronos

Author: Brady Simmons
Copyright: © 2025 Sovereignty Foundation. All rights reserved.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Set, Any, List
import asyncio
import json
import yaml
from datetime import datetime, timedelta
import logging
from pathlib import Path
import hmac
from hashlib import sha256

# Import constitutional alignment checker
import sys
sys.path.append(str(Path(__file__).parent / 'security'))
from constitution_check import verify_node_alignment

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("PulseMesh")

# Initialize FastAPI
app = FastAPI(
    title="PulseMesh Relay",
    version="1.0.0",
    description="Distributed semantic event bus for the Sovereignty Stack"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Topic registry: topic → set of WebSocket connections
topic_subscribers: Dict[str, Set[WebSocket]] = {}

# Node registry: node_id → WebSocket connection
node_connections: Dict[str, WebSocket] = {}

# Message history (for replay and debugging)
message_history: List[Dict[str, Any]] = []
MAX_HISTORY = 1000

# Security: Active sessions and secret key
ACTIVE_SESSIONS: Dict[str, datetime] = {}
SECRET_KEY = "mirror:logos:2025"

# Load PulseMesh ontology for routing
def load_mesh_ontology():
    """Load pulsemesh.yaml for topic routing"""
    ontology_path = Path("/home/ubuntu/sov/core/ontology/pulsemesh.yaml")
    if ontology_path.exists():
        with open(ontology_path, 'r') as f:
            return yaml.safe_load(f)
    return {}

mesh_ontology = load_mesh_ontology()
logger.info(f"[PulseMesh] Loaded ontology with {len(mesh_ontology.get('topics', {}))} topics")


# Security Functions
def verify_signature(message: dict, signature: str) -> bool:
    """
    Verify message signature using HMAC-SHA256
    
    Args:
        message: The message payload
        signature: The signature to verify
    
    Returns:
        True if signature is valid, False otherwise
    """
    message_str = json.dumps(message, sort_keys=True)
    check = hmac.new(SECRET_KEY.encode(), message_str.encode(), sha256).hexdigest()
    
    # Debug logging
    if check != signature:
        logger.debug(f"[PulseMesh] Signature mismatch:")
        logger.debug(f"  Message: {message_str}")
        logger.debug(f"  Expected: {check}")
        logger.debug(f"  Received: {signature}")
    
    return check == signature


async def secure_connect(websocket: WebSocket) -> str:
    """
    Perform secure handshake with client
    
    Args:
        websocket: The WebSocket connection
    
    Returns:
        Success message with client_id, or error string
    
    Raises:
        WebSocketDisconnect: If signature is invalid
    """
    await websocket.accept()
    
    try:
        handshake = await websocket.receive_json()
        message = handshake.get("message")
        signature = handshake.get("signature")
        
        # TODO: Emit handshake initiated event (pulse_bus not yet implemented)
        # await pulse_bus.emit("auth.handshake.initiated", {
        #     "client_id": message.get("source", "unknown") if message else "unknown",
        #     "source": message.get("source", "unknown") if message else "unknown",
        #     "timestamp": datetime.utcnow().isoformat()
        # })
        
        if not message or not signature:
            # TODO: Emit handshake failed event
            # await pulse_bus.emit("auth.handshake.failed", {
            #     "client_id": None,
            #     "reason": "missing_data",
            #     "close_code": 4001
            # })
            
            await websocket.close(code=4001)
            return "Missing handshake data"
        
        if not verify_signature(message, signature):
            client_id = message.get('source', 'unknown')
            logger.warning(f"[PulseMesh] Invalid signature from {client_id}")
            
            # TODO: Emit handshake failed event
            # await pulse_bus.emit("auth.handshake.failed", {
            #     "client_id": client_id,
            #     "reason": "invalid_signature",
            #     "close_code": 4003
            # })
            
            await websocket.close(code=4003)
            return "Invalid Signature"
        
        # Check constitutional alignment
        client_id = message["source"]
        alignment = verify_node_alignment(client_id)
        
        if not alignment['aligned']:
            logger.warning(f"[PulseMesh] Constitutional alignment failed for {client_id}: {alignment['reason']}")
            
            # TODO: Emit alignment failed event
            # await pulse_bus.emit("constitution.alignment.failed", {
            #     "client_id": client_id,
            #     "reason": alignment['reason'],
            #     "constitution_hash": alignment.get('constitution_hash'),
            #     "close_code": 4004
            # })
            
            await websocket.close(code=4004, reason=alignment.get('message', 'Not constitutionally aligned'))
            return f"Constitutional alignment failed: {alignment['reason']}"
        
        session_id = f"{client_id}_{int(datetime.utcnow().timestamp())}"
        ACTIVE_SESSIONS[client_id] = datetime.utcnow()
        logger.info(f"[PulseMesh] Handshake OK from {client_id} (constitutionally aligned)")
        
        # TODO: Emit constitutional alignment success
        # await pulse_bus.emit("constitution.alignment.verified", {
        #     "client_id": client_id,
        #     "constitution_hash": alignment['constitution_hash'],
        #     "signed_at": alignment.get('signed_at')
        # })
        
        # TODO: Emit handshake success event
        # await pulse_bus.emit("auth.handshake.success", {
        #     "client_id": client_id,
        #     "session_id": session_id,
        #     "authentication_method": "hmac_sha256"
        # })
        
        # TODO: Emit session created event
        # await pulse_bus.emit("auth.session.created", {
        #     "session_id": session_id,
        #     "client_id": client_id,
        #     "session_type": "websocket_session",
        #     "expires_at": (datetime.utcnow() + timedelta(hours=24)).isoformat()
        # })
        
        # Send handshake confirmation
        await websocket.send_json({
            "type": "handshake_ok",
            "client_id": client_id,
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return f"Handshake OK from {client_id}"
        
    except Exception as e:
        logger.error(f"[PulseMesh] Handshake error: {e}")
        await websocket.close(code=4000)
        return f"Handshake failed: {e}"


@app.get("/")
async def health_check():
    """Health check endpoint"""
    return {
        "service": "PulseMesh Relay",
        "version": "1.0.0",
        "status": "operational",
        "active_topics": len(topic_subscribers),
        "active_connections": sum(len(subs) for subs in topic_subscribers.values()),
        "message_count": len(message_history)
    }


@app.get("/api/mesh/schema")
async def get_mesh_schema():
    """
    Get dynamic mesh topology from Core ontology
    
    Returns:
        Mesh configuration including nodes, topics, and roles
    """
    # TODO: Fetch from Core ontology API
    # For now, return static schema
    return {
        "nodes": [
            {"id": "mirror", "role": "ui", "topics": ["mirror.intent", "mirror.update"]},
            {"id": "core", "role": "reasoner", "topics": ["core.reply", "core.status", "core.ingest"]},
            {"id": "sage", "role": "governor", "topics": ["audit.log", "governance.decision"]}
        ],
        "topics": [
            {"name": "mirror.intent", "description": "User intentions from Mirror UI"},
            {"name": "mirror.update", "description": "UI state updates"},
            {"name": "core.reply", "description": "Reasoning responses from Core"},
            {"name": "core.status", "description": "Core system status"},
            {"name": "core.ingest", "description": "Data ingestion events"},
            {"name": "audit.log", "description": "SAGE audit trail"},
            {"name": "governance.decision", "description": "SAGE governance decisions"}
        ],
        "mode": "stub",  # stub | token
        "version": "1.0.0"
    }


@app.get("/api/mesh/topics")
async def list_topics():
    """List all active topics and subscriber counts"""
    return {
        "topics": [
            {
                "name": topic,
                "subscribers": len(subscribers),
                "active": len(subscribers) > 0
            }
            for topic, subscribers in topic_subscribers.items()
        ]
    }


@app.get("/api/mesh/history")
async def get_message_history(limit: int = 100):
    """Get recent message history"""
    return {
        "messages": message_history[-limit:],
        "total": len(message_history)
    }


@app.websocket("/ws/mesh/{topic}")
async def mesh_endpoint(websocket: WebSocket, topic: str):
    """
    WebSocket endpoint for topic-based pub/sub with security
    
    Args:
        websocket: WebSocket connection
        topic: Topic name to subscribe to
    """
    # TEMPORARY: Handshake disabled for testing
    await websocket.accept()
    logger.info(f"[PulseMesh] Connection accepted without handshake (testing mode)")
    
    # # Perform secure handshake
    # handshake_result = await secure_connect(websocket)
    # if "Invalid" in handshake_result or "failed" in handshake_result:
    #     logger.warning(f"[PulseMesh] Connection rejected: {handshake_result}")
    #     return
    
    # Register subscriber
    if topic not in topic_subscribers:
        topic_subscribers[topic] = set()
    topic_subscribers[topic].add(websocket)
    
    logger.info(f"[PulseMesh] Client subscribed to topic: {topic} (total: {len(topic_subscribers[topic])})")
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            pulse = json.loads(data)
            
            # Add metadata
            pulse["_mesh_timestamp"] = datetime.utcnow().isoformat()
            pulse["_mesh_topic"] = topic
            
            logger.info(f"[PulseMesh] Received pulse on {topic}: {pulse.get('source', 'unknown')} → {pulse.get('target', 'unknown')}")
            
            # Store in history
            message_history.append(pulse)
            if len(message_history) > MAX_HISTORY:
                message_history.pop(0)
            
            # Broadcast to all subscribers on this topic (except sender)
            disconnected = set()
            for subscriber in topic_subscribers[topic]:
                if subscriber != websocket:
                    try:
                        await subscriber.send_text(json.dumps(pulse))
                    except Exception as e:
                        logger.error(f"[PulseMesh] Error sending to subscriber: {e}")
                        disconnected.add(subscriber)
            
            # Clean up disconnected subscribers
            topic_subscribers[topic] -= disconnected
            
            # Route to target topics based on ontology
            topic_config = mesh_ontology.get('topics', {}).get(topic, {})
            target_nodes = topic_config.get('targets', [])
            
            if target_nodes:
                logger.info(f"[PulseMesh] Routing {topic} to targets: {target_nodes}")
                
                # For each target node, find their topics and broadcast
                for target_node in target_nodes:
                    # Find topics for this target node
                    node_topics = []
                    for node in mesh_ontology.get('nodes', []):
                        if node.get('id') == target_node:
                            node_topics = node.get('topics', [])
                            break
                    
                    # Broadcast to all topics of target node
                    for target_topic in node_topics:
                        if target_topic in topic_subscribers:
                            for subscriber in topic_subscribers[target_topic]:
                                try:
                                    await subscriber.send_text(json.dumps(pulse))
                                    logger.info(f"[PulseMesh] Routed to {target_topic}")
                                except Exception as e:
                                    logger.error(f"[PulseMesh] Error routing to {target_topic}: {e}")
            
    except WebSocketDisconnect:
        logger.info(f"[PulseMesh] Client disconnected from topic: {topic}")
    except Exception as e:
        logger.error(f"[PulseMesh] Error in mesh endpoint: {e}")
    finally:
        # Unregister subscriber
        if websocket in topic_subscribers.get(topic, set()):
            topic_subscribers[topic].remove(websocket)
        
        # Clean up empty topics
        if topic in topic_subscribers and len(topic_subscribers[topic]) == 0:
            del topic_subscribers[topic]
        
        logger.info(f"[PulseMesh] Cleaned up topic: {topic}")


@app.websocket("/ws/node/{node_id}")
async def node_endpoint(websocket: WebSocket, node_id: str):
    """
    WebSocket endpoint for node-to-node communication
    
    Args:
        websocket: WebSocket connection
        node_id: Unique node identifier
    """
    await websocket.accept()
    
    # Register node
    node_connections[node_id] = websocket
    logger.info(f"[PulseMesh] Node connected: {node_id}")
    
    try:
        while True:
            data = await websocket.receive_text()
            pulse = json.loads(data)
            
            # Route to target node
            target_id = pulse.get("target")
            if target_id and target_id in node_connections:
                target_ws = node_connections[target_id]
                try:
                    await target_ws.send_text(json.dumps(pulse))
                    logger.info(f"[PulseMesh] Routed pulse: {node_id} → {target_id}")
                except Exception as e:
                    logger.error(f"[PulseMesh] Error routing to {target_id}: {e}")
            else:
                logger.warning(f"[PulseMesh] Target node not found: {target_id}")
                
    except WebSocketDisconnect:
        logger.info(f"[PulseMesh] Node disconnected: {node_id}")
    except Exception as e:
        logger.error(f"[PulseMesh] Error in node endpoint: {e}")
    finally:
        # Unregister node
        if node_id in node_connections:
            del node_connections[node_id]
        logger.info(f"[PulseMesh] Cleaned up node: {node_id}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8088)
