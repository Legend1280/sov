"""
Constitutional Alignment Test Suite

Tests the Sovereignty Constitution implementation:
1. Constitution compilation and hashing
2. Node signature verification
3. PulseMesh alignment enforcement
4. Alignment status reporting

Author: Brady Simmons
Copyright: © 2025 Sovereignty Foundation. All rights reserved.
"""

import json
from pathlib import Path
from constitution_check import get_checker, verify_node_alignment

def test_constitution_loaded():
    """Test that constitution is properly loaded"""
    print("\n" + "=" * 60)
    print("TEST 1: Constitution Loading")
    print("=" * 60)
    
    checker = get_checker()
    
    if not checker.constitution:
        print("❌ FAILED: Constitution not loaded")
        return False
    
    print(f"✅ Constitution loaded")
    print(f"   ID: {checker.constitution['constitution_id']}")
    print(f"   Version: {checker.constitution['version']}")
    print(f"   Hash: {checker.constitution['provenance']['hash'][:48]}...")
    
    return True


def test_node_signatures():
    """Test that all nodes have valid signatures"""
    print("\n" + "=" * 60)
    print("TEST 2: Node Signatures")
    print("=" * 60)
    
    nodes = ["mirror", "core", "sage", "kronos", "shadow", "pulsemesh"]
    all_signed = True
    
    for node_id in nodes:
        alignment = verify_node_alignment(node_id)
        
        if alignment['aligned']:
            print(f"✅ {node_id:12s} - Signed at {alignment['signed_at']}")
        else:
            print(f"❌ {node_id:12s} - {alignment['reason']}")
            all_signed = False
    
    if all_signed:
        print("\n✅ All nodes have valid signatures")
    else:
        print("\n❌ Some nodes missing signatures")
    
    return all_signed


def test_alignment_verification():
    """Test alignment verification for valid and invalid nodes"""
    print("\n" + "=" * 60)
    print("TEST 3: Alignment Verification")
    print("=" * 60)
    
    # Test valid node
    print("\nTesting valid node (mirror):")
    alignment = verify_node_alignment("mirror")
    
    if alignment['aligned']:
        print(f"✅ Mirror alignment verified")
        print(f"   Hash: {alignment['constitution_hash'][:48]}...")
    else:
        print(f"❌ Mirror alignment failed: {alignment['reason']}")
        return False
    
    # Test invalid node (not signed)
    print("\nTesting invalid node (rogue_node):")
    alignment = verify_node_alignment("rogue_node")
    
    if not alignment['aligned'] and alignment['reason'] == 'unsigned':
        print(f"✅ Rogue node correctly rejected")
        print(f"   Reason: {alignment['reason']}")
    else:
        print(f"❌ Rogue node should have been rejected")
        return False
    
    print("\n✅ Alignment verification working correctly")
    return True


def test_alignment_status():
    """Test overall alignment status reporting"""
    print("\n" + "=" * 60)
    print("TEST 4: Alignment Status Report")
    print("=" * 60)
    
    checker = get_checker()
    status = checker.get_alignment_status()
    
    print(f"\nConstitution: {status['constitution_id']}")
    print(f"Total Nodes: {status['total_nodes']}")
    print(f"Signed: {status['signed_nodes']}")
    print(f"Unsigned: {status['unsigned_nodes']}")
    
    print("\nNode Status:")
    for node_id, alignment in status['nodes'].items():
        status_icon = "✅" if alignment['aligned'] else "❌"
        print(f"  {status_icon} {node_id:12s} - {alignment['reason']}")
    
    if status['unsigned_nodes'] == 0:
        print("\n✅ All nodes constitutionally aligned")
        return True
    else:
        print(f"\n⚠️  {status['unsigned_nodes']} nodes not aligned")
        return False


def test_constitution_hash_integrity():
    """Test that constitution hash matches expected format"""
    print("\n" + "=" * 60)
    print("TEST 5: Constitution Hash Integrity")
    print("=" * 60)
    
    checker = get_checker()
    constitution_hash = checker.constitution['provenance']['hash']
    
    # Check hash format
    if not constitution_hash.startswith("SHA3-512:"):
        print(f"❌ Invalid hash format: {constitution_hash[:20]}...")
        return False
    
    print(f"✅ Hash format valid: SHA3-512")
    
    # Check hash length (SHA3-512 produces 128 hex characters)
    hash_value = constitution_hash.split(":", 1)[1]
    if len(hash_value) != 128:
        print(f"❌ Invalid hash length: {len(hash_value)} (expected 128)")
        return False
    
    print(f"✅ Hash length valid: 128 characters")
    print(f"   Full hash: {constitution_hash}")
    
    return True


def test_signature_persistence():
    """Test that signatures are persisted to disk"""
    print("\n" + "=" * 60)
    print("TEST 6: Signature Persistence")
    print("=" * 60)
    
    signatures_path = Path(__file__).parent / 'signatures.json'
    
    if not signatures_path.exists():
        print(f"❌ Signatures file not found: {signatures_path}")
        return False
    
    print(f"✅ Signatures file exists")
    
    with open(signatures_path, 'r') as f:
        signatures = json.load(f)
    
    if 'constitution_id' not in signatures:
        print(f"❌ Missing constitution_id in signatures")
        return False
    
    print(f"✅ Constitution ID: {signatures['constitution_id']}")
    
    if 'signatures' not in signatures:
        print(f"❌ Missing signatures section")
        return False
    
    node_count = len(signatures['signatures'])
    print(f"✅ {node_count} node signatures persisted")
    
    return True


def run_all_tests():
    """Run complete test suite"""
    print("\n" + "=" * 70)
    print("🜂 SOVEREIGNTY CONSTITUTION TEST SUITE")
    print("=" * 70)
    
    tests = [
        ("Constitution Loading", test_constitution_loaded),
        ("Node Signatures", test_node_signatures),
        ("Alignment Verification", test_alignment_verification),
        ("Alignment Status", test_alignment_status),
        ("Hash Integrity", test_constitution_hash_integrity),
        ("Signature Persistence", test_signature_persistence),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ TEST FAILED WITH EXCEPTION: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {test_name:30s} {status}")
    
    total = len(results)
    passed = sum(1 for r in results.values() if r)
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ ALL TESTS PASSED - CONSTITUTION OPERATIONAL")
        return True
    else:
        print(f"\n❌ {total - passed} TESTS FAILED")
        return False


if __name__ == "__main__":
    import sys
    success = run_all_tests()
    sys.exit(0 if success else 1)
