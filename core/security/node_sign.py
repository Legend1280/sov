"""
Node Constitution Signing

Each node must sign the Sovereignty Constitution at startup before
participating in PulseMesh. This script handles the signing process.

Usage:
    python3.11 node_sign.py <node_id>

Example:
    python3.11 node_sign.py mirror
    python3.11 node_sign.py core

Author: Brady Simmons
Copyright: © 2025 Sovereignty Foundation. All rights reserved.
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from hashlib import sha256

# Import constitution checker
from constitution_check import sign_constitution, verify_node_alignment, get_checker

def generate_node_signature(node_id: str, constitution_hash: str) -> str:
    """
    Generate a cryptographic signature for the node
    
    In a production system, this would use the node's private key.
    For now, we use a deterministic hash based on node_id and constitution.
    
    Args:
        node_id: The node identifier
        constitution_hash: The constitution hash to sign
    
    Returns:
        Node signature (hex string)
    """
    # Deterministic signature based on node_id and constitution
    signature_input = f"{node_id}:{constitution_hash}:sovereignty:2025"
    signature = sha256(signature_input.encode()).hexdigest()
    return signature


def sign_as_node(node_id: str) -> bool:
    """
    Sign the constitution as a specific node
    
    Args:
        node_id: The node identifier
    
    Returns:
        True if signing succeeded, False otherwise
    """
    print(f"\n{'=' * 60}")
    print(f"🜂 NODE CONSTITUTION SIGNING: {node_id.upper()}")
    print(f"{'=' * 60}\n")
    
    # Load constitution
    checker = get_checker()
    
    if not checker.constitution:
        print(f"[{node_id}] ❌ Constitution not found")
        return False
    
    constitution_id = checker.constitution['constitution_id']
    constitution_hash = checker.constitution['provenance']['hash']
    
    print(f"[{node_id}] Constitution ID: {constitution_id}")
    print(f"[{node_id}] Constitution Hash: {constitution_hash[:48]}...")
    
    # Check if already signed
    alignment = verify_node_alignment(node_id)
    
    if alignment['aligned']:
        print(f"\n[{node_id}] ✅ Already signed at {alignment['signed_at']}")
        print(f"[{node_id}] Constitutional alignment: VERIFIED")
        return True
    
    print(f"\n[{node_id}] Status: {alignment['reason']}")
    print(f"[{node_id}] Generating signature...")
    
    # Generate signature
    node_signature = generate_node_signature(node_id, constitution_hash)
    
    print(f"[{node_id}] Signature: {node_signature[:48]}...")
    
    # Sign constitution
    success = sign_constitution(node_id, node_signature)
    
    if success:
        print(f"\n[{node_id}] ✅ Constitution signed successfully")
        print(f"[{node_id}] Timestamp: {datetime.utcnow().isoformat()}Z")
        print(f"[{node_id}] Constitutional alignment: VERIFIED")
        
        # Verify alignment
        alignment = verify_node_alignment(node_id)
        if alignment['aligned']:
            print(f"[{node_id}] ✅ Alignment verification passed")
        else:
            print(f"[{node_id}] ⚠️  Alignment verification failed: {alignment['reason']}")
            return False
        
        return True
    else:
        print(f"\n[{node_id}] ❌ Failed to sign constitution")
        return False


def sign_all_nodes():
    """Sign constitution for all nodes"""
    nodes = ["mirror", "core", "sage", "kronos", "shadow", "pulsemesh"]
    
    print("\n" + "=" * 60)
    print("🜂 SIGNING CONSTITUTION FOR ALL NODES")
    print("=" * 60)
    
    results = {}
    
    for node_id in nodes:
        success = sign_as_node(node_id)
        results[node_id] = success
    
    print("\n" + "=" * 60)
    print("SIGNING SUMMARY")
    print("=" * 60)
    
    for node_id, success in results.items():
        status = "✅ SIGNED" if success else "❌ FAILED"
        print(f"  {node_id:12s} {status}")
    
    total = len(results)
    signed = sum(1 for s in results.values() if s)
    
    print(f"\nTotal: {signed}/{total} nodes signed")
    
    if signed == total:
        print("\n✅ ALL NODES CONSTITUTIONALLY ALIGNED")
    else:
        print(f"\n⚠️  {total - signed} nodes failed to sign")
    
    return signed == total


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Sign specific node
        node_id = sys.argv[1]
        success = sign_as_node(node_id)
        sys.exit(0 if success else 1)
    else:
        # Sign all nodes
        success = sign_all_nodes()
        sys.exit(0 if success else 1)
