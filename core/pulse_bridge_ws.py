"""
Pulse WebSocket Bridge - Connects Mirror (TS) to Core (Python) PulseBus

Provides a WebSocket endpoint that:
- Receives Pulse events from Mirror
- Emits them to Core's PulseBus
- Sends responses back to Mirror
- Maintains bidirectional communication

Author: Brady Simmons
Copyright: © 2025 Sovereignty Foundation. All rights reserved.
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Any, List
import json
import asyncio
from datetime import datetime

from pulse_bus import get_pulse_bus

class PulseBridgeWS:
    """WebSocket bridge for Pulse communication"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.pulse_bus = get_pulse_bus()
        
    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"[PulseBridge] Client connected. Active connections: {len(self.active_connections)}")
        
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        print(f"[PulseBridge] Client disconnected. Active connections: {len(self.active_connections)}")
        
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast a message to all connected clients"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"[PulseBridge] Error broadcasting to client: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected clients
        for conn in disconnected:
            self.disconnect(conn)
    
    async def handle_pulse_event(self, websocket: WebSocket, data: Dict[str, Any]):
        """
        Handle incoming Pulse event from Mirror
        
        Args:
            websocket: The WebSocket connection
            data: Pulse event data
        """
        try:
            # Extract topic and payload
            topic = data.get("topic", "unknown")
            payload = data.get("payload", {})
            
            print(f"[PulseBridge] Received Pulse: {topic}")
            
            # Emit to PulseBus
            event_result = await self.pulse_bus.emit(topic, payload, validate=True)
            
            # Send acknowledgment back to Mirror
            response = {
                "type": "pulse_ack",
                "event_id": event_result["id"],
                "topic": topic,
                "validated": event_result["validated"],
                "timestamp": event_result["timestamp"],
                "handlers_called": event_result["handlers_called"]
            }
            
            if "validation_errors" in event_result:
                response["errors"] = event_result["validation_errors"]
            
            await websocket.send_json(response)
            
            # Broadcast to other clients if needed
            if data.get("broadcast", False):
                await self.broadcast({
                    "type": "pulse_event",
                    "topic": topic,
                    "payload": payload,
                    "timestamp": event_result["timestamp"]
                })
                
        except Exception as e:
            print(f"[PulseBridge] Error handling Pulse event: {e}")
            await websocket.send_json({
                "type": "error",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            })
    
    async def handle_message(self, websocket: WebSocket, message: str):
        """
        Handle incoming WebSocket message
        
        Args:
            websocket: The WebSocket connection
            message: Raw message string
        """
        try:
            data = json.loads(message)
            message_type = data.get("type", "unknown")
            
            if message_type == "pulse":
                await self.handle_pulse_event(websocket, data)
            elif message_type == "ping":
                await websocket.send_json({"type": "pong", "timestamp": datetime.utcnow().isoformat()})
            elif message_type == "subscribe":
                # Future: Handle topic subscriptions
                await websocket.send_json({"type": "subscribed", "topic": data.get("topic")})
            else:
                await websocket.send_json({"type": "error", "message": f"Unknown message type: {message_type}"})
                
        except json.JSONDecodeError as e:
            await websocket.send_json({"type": "error", "message": f"Invalid JSON: {e}"})
        except Exception as e:
            await websocket.send_json({"type": "error", "message": str(e)})


# Global instance
_bridge = None

def get_pulse_bridge() -> PulseBridgeWS:
    """Get or create the global PulseBridgeWS instance"""
    global _bridge
    if _bridge is None:
        _bridge = PulseBridgeWS()
    return _bridge
