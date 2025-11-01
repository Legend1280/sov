#!/usr/bin/env python3.11
"""
Test client for PulseMesh WebSocket connection
Tests HMAC-SHA256 handshake and message flow
"""

import asyncio
import websockets
import json
import hmac
from hashlib import sha256
from datetime import datetime

# Configuration
PULSEMESH_URL = "ws://localhost:8088/ws/mesh/mirror.control"
SECRET_KEY = "mirror:logos:2025"
CLIENT_ID = "mirror"


def generate_signature(message: dict) -> str:
    """Generate HMAC-SHA256 signature matching PulseMesh algorithm"""
    message_str = json.dumps(message, sort_keys=True)
    signature = hmac.new(
        SECRET_KEY.encode(),
        message_str.encode(),
        sha256
    ).hexdigest()
    return signature


async def test_handshake():
    """Test PulseMesh handshake with HMAC-SHA256"""
    print(f"[Test Client] Connecting to {PULSEMESH_URL}...")
    
    try:
        async with websockets.connect(PULSEMESH_URL) as websocket:
            print("[Test Client] WebSocket connection established")
            
            # Prepare handshake message
            message = {
                "source": CLIENT_ID,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Generate signature
            signature = generate_signature(message)
            
            # Send handshake
            handshake = {
                "message": message,
                "signature": signature
            }
            
            print(f"[Test Client] Sending handshake...")
            print(f"  Message: {json.dumps(message, indent=2)}")
            print(f"  Signature: {signature[:32]}...")
            
            await websocket.send(json.dumps(handshake))
            print("[Test Client] Handshake sent")
            
            # Wait for response
            print("[Test Client] Waiting for handshake response...")
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            response_data = json.loads(response)
            
            print(f"[Test Client] Handshake response received:")
            print(json.dumps(response_data, indent=2))
            
            if response_data.get("type") == "handshake_ok":
                print("[Test Client] ✓ Handshake successful!")
                print(f"  Client ID: {response_data.get('client_id')}")
                print(f"  Session ID: {response_data.get('session_id')}")
                
                # Test sending a Pulse
                print("\n[Test Client] Sending test Pulse...")
                test_pulse = {
                    "source": CLIENT_ID,
                    "target": "core",
                    "type": "test",
                    "payload": {"message": "Hello from test client"},
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                await websocket.send(json.dumps(test_pulse))
                print("[Test Client] Test Pulse sent")
                
                # Keep connection alive for a bit
                print("[Test Client] Connection active, waiting for messages...")
                try:
                    while True:
                        message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                        print(f"[Test Client] Received: {message}")
                except asyncio.TimeoutError:
                    print("[Test Client] No messages received (timeout)")
                
            else:
                print(f"[Test Client] ✗ Handshake failed: {response_data}")
                
    except websockets.exceptions.ConnectionClosed as e:
        print(f"[Test Client] ✗ Connection closed: code={e.code}, reason={e.reason}")
    except asyncio.TimeoutError:
        print("[Test Client] ✗ Timeout waiting for handshake response")
    except Exception as e:
        print(f"[Test Client] ✗ Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


async def test_signature_generation():
    """Test that signature generation matches PulseMesh"""
    print("\n[Test Client] Testing signature generation...")
    
    test_message = {
        "source": "mirror",
        "timestamp": "2025-11-01T00:00:00.000000"
    }
    
    # Generate signature
    signature = generate_signature(test_message)
    
    print(f"  Message: {json.dumps(test_message, sort_keys=True)}")
    print(f"  Signature: {signature}")
    print(f"  Length: {len(signature)} characters")
    
    # Verify it's 64 hex characters (SHA256 output)
    if len(signature) == 64 and all(c in '0123456789abcdef' for c in signature):
        print("  ✓ Signature format valid (64 hex characters)")
    else:
        print("  ✗ Signature format invalid")


if __name__ == "__main__":
    print("=" * 60)
    print("PulseMesh Test Client")
    print("=" * 60)
    
    # Test signature generation first
    asyncio.run(test_signature_generation())
    
    print("\n" + "=" * 60)
    print("Testing Handshake")
    print("=" * 60 + "\n")
    
    # Test handshake
    asyncio.run(test_handshake())
    
    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)
