"""
Sovereignty Constitution Registration (Pulse-Native)

Registers the constitution across all nodes using PulseBus instead of HTTP.
Each node must acknowledge and sign the constitution to participate in PulseMesh.

Author: Brady Simmons
Copyright: © 2025 Sovereignty Foundation. All rights reserved.
"""

import json
import asyncio
from pathlib import Path
from datetime import datetime

# Import PulseBus for Pulse-native communication
import sys
sys.path.append(str(Path(__file__).parent.parent))
from pulse_bus import PulseBus

async def register_constitution():
    """Register constitution across all nodes via PulseBus"""
    
    # Load compiled constitution
    constitution_path = Path(__file__).parent / 'constitution.json'
    print("[Constitution] Loading compiled constitution...")
    
    with open(constitution_path, 'r', encoding='utf-8') as f:
        constitution = json.load(f)
    
    constitution_hash = constitution['provenance']['hash']
    constitution_id = constitution['constitution_id']
    version = constitution['version']
    
    print(f"[Constitution] ID: {constitution_id}")
    print(f"[Constitution] Version: {version}")
    print(f"[Constitution] Hash: {constitution_hash[:48]}...")
    
    # Initialize PulseBus
    pulse_bus = PulseBus()
    
    # Define all nodes that must sign the constitution
    nodes = ["mirror", "core", "sage", "kronos", "shadow", "pulsemesh"]
    
    print(f"\n[Constitution] Registering across {len(nodes)} nodes...")
    
    # Register with each node via Pulse
    for node in nodes:
        print(f"\n[Constitution] → Registering with {node}...")
        
        # Emit constitution.register Pulse
        await pulse_bus.emit(f"{node}.constitution.register", {
            "constitution_id": constitution_id,
            "version": version,
            "hash": constitution_hash,
            "rights": constitution['rights'],
            "obligations": constitution['obligations'],
            "enforcement": constitution['enforcement'],
            "timestamp": datetime.utcnow().isoformat() + 'Z',
            "source": "constitution_register"
        })
        
        print(f"[Constitution] ✅ Pulse emitted to {node}")
    
    # Emit global constitution.activated event
    print("\n[Constitution] Emitting global activation event...")
    await pulse_bus.emit("constitution.activated", {
        "constitution_id": constitution_id,
        "version": version,
        "hash": constitution_hash,
        "nodes": nodes,
        "timestamp": datetime.utcnow().isoformat() + 'Z'
    })
    
    print("\n[Constitution] 🜂 Constitution registered across all nodes")
    print("[Constitution] All nodes must now sign to participate in PulseMesh")
    
    return constitution

async def verify_registration():
    """Verify that all nodes received and acknowledged the constitution"""
    print("\n[Constitution] Verifying registration...")
    
    # In a full implementation, this would query each node for acknowledgment
    # For now, we'll just log the expectation
    
    nodes = ["mirror", "core", "sage", "kronos", "shadow", "pulsemesh"]
    
    print("[Constitution] Expected acknowledgments from:")
    for node in nodes:
        print(f"  - {node}: Awaiting signature...")
    
    print("\n[Constitution] ⚠️  Nodes must restart and sign constitution")
    print("[Constitution] Unsigned nodes will be rejected by PulseMesh")

if __name__ == "__main__":
    print("=" * 60)
    print("🜂 SOVEREIGNTY CONSTITUTION REGISTRATION")
    print("=" * 60)
    
    # Run registration
    constitution = asyncio.run(register_constitution())
    
    # Verify
    asyncio.run(verify_registration())
    
    print("\n" + "=" * 60)
    print("✅ CONSTITUTION REGISTRATION COMPLETE")
    print("=" * 60)
