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
from datetime import datetime
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
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
    WebSocket endpoint for topic-based pub/sub
    
    Args:
        websocket: WebSocket connection
        topic: Topic name to subscribe to
    """
    await websocket.accept()
    
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
