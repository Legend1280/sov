"""
PulseMesh Listener - Connects Core components to PulseMesh

This service subscribes Core components (SAGE, Kronos, Shadow) to PulseMesh
topics and triggers their handlers when Pulses arrive.

Author: Brady Simmons
Copyright: © 2025 Sovereignty Foundation. All rights reserved.
"""

import asyncio
import websockets
import json
import logging
from pulse_bus import PulseBus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PulseMeshListener")

# PulseBus instance for local event distribution
bus = PulseBus()

# PulseMesh WebSocket URL
PULSEMESH_URL = "ws://localhost:8088/ws/mesh"

# Topics to subscribe to
CORE_TOPICS = [
    "mirror.intent",
    "mirror.update",
    "core.ingest",
    "governance.validate",
    "kronos.index",
    "shadow.provenance"
]


async def listen_to_topic(topic: str):
    """
    Subscribe to a PulseMesh topic and forward Pulses to local PulseBus
    
    Args:
        topic: Topic name to subscribe to
    """
    url = f"{PULSEMESH_URL}/{topic}"
    
    while True:
        try:
            async with websockets.connect(url) as websocket:
                logger.info(f"[Listener] Connected to PulseMesh topic: {topic}")
                
                async for message in websocket:
                    try:
                        pulse = json.loads(message)
                        logger.info(f"[Listener] Received Pulse on {topic}: {pulse.get('source')} → {pulse.get('target')}")
                        
                        # Forward to local PulseBus
                        await bus.emit(topic, pulse)
                        
                        # Trigger governance pipeline based on topic
                        if topic == "mirror.intent":
                            # Trigger SAGE validation
                            await bus.emit("governance.validate", pulse)
                            # Trigger Kronos indexing
                            await bus.emit("kronos.index", pulse)
                            # Trigger Shadow logging
                            await bus.emit("shadow.provenance", pulse)
                            
                            logger.info(f"[Listener] Triggered governance pipeline for {pulse.get('id', 'unknown')}")
                        
                    except json.JSONDecodeError as e:
                        logger.error(f"[Listener] Invalid JSON on {topic}: {e}")
                    except Exception as e:
                        logger.error(f"[Listener] Error processing Pulse on {topic}: {e}")
                        
        except websockets.exceptions.ConnectionClosed:
            logger.warning(f"[Listener] Connection to {topic} closed, reconnecting in 5s...")
            await asyncio.sleep(5)
        except Exception as e:
            logger.error(f"[Listener] Error connecting to {topic}: {e}")
            await asyncio.sleep(5)


async def main():
    """Start all topic listeners"""
    logger.info("[Listener] Starting PulseMesh listeners for Core components...")
    
    # Create tasks for all topics
    tasks = [listen_to_topic(topic) for topic in CORE_TOPICS]
    
    # Run all listeners concurrently
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("[Listener] Shutting down...")
