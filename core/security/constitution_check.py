"""
Constitutional Alignment Checker

Verifies that nodes have signed the Sovereignty Constitution before
allowing them to participate in PulseMesh.

This module is imported by PulseMesh to enforce constitutional alignment
during the handshake process.

Author: Brady Simmons
Copyright: © 2025 Sovereignty Foundation. All rights reserved.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

class ConstitutionChecker:
    """Verifies constitutional alignment for nodes"""
    
    def __init__(self):
        """Initialize the constitution checker"""
        self.constitution_path = Path(__file__).parent / 'constitution.json'
        self.signatures_path = Path(__file__).parent / 'signatures.json'
        self.constitution = None
        self.signatures = {}
        
        # Load constitution
        self._load_constitution()
        
        # Load signatures
        self._load_signatures()
    
    def _load_constitution(self):
        """Load the compiled constitution"""
        if self.constitution_path.exists():
            with open(self.constitution_path, 'r', encoding='utf-8') as f:
                self.constitution = json.load(f)
    
    def _load_signatures(self):
        """Load node signatures"""
        if self.signatures_path.exists():
            with open(self.signatures_path, 'r', encoding='utf-8') as f:
                self.signatures = json.load(f)
        else:
            # Initialize empty signatures file
            self.signatures = {
                "constitution_id": "SOV-CONST-001",
                "signatures": {}
            }
            self._save_signatures()
    
    def _save_signatures(self):
        """Save signatures to disk"""
        with open(self.signatures_path, 'w', encoding='utf-8') as f:
            json.dump(self.signatures, f, indent=2)
    
    def verify_alignment(self, node_id: str) -> Dict[str, any]:
        """
        Verify that a node has signed the constitution
        
        Args:
            node_id: The node identifier (e.g., "mirror", "core", "sage")
        
        Returns:
            Dict with 'aligned' (bool), 'reason' (str), and 'constitution_hash' (str)
        """
        if not self.constitution:
            return {
                "aligned": False,
                "reason": "constitution_not_loaded",
                "constitution_hash": None
            }
        
        constitution_hash = self.constitution['provenance']['hash']
        
        # Check if node has signed
        if node_id not in self.signatures['signatures']:
            return {
                "aligned": False,
                "reason": "unsigned",
                "constitution_hash": constitution_hash,
                "message": f"Node '{node_id}' has not signed the Sovereignty Constitution"
            }
        
        signature = self.signatures['signatures'][node_id]
        
        # Verify signature matches current constitution
        if signature['constitution_hash'] != constitution_hash:
            return {
                "aligned": False,
                "reason": "hash_mismatch",
                "constitution_hash": constitution_hash,
                "signed_hash": signature['constitution_hash'],
                "message": f"Node '{node_id}' signed a different constitution version"
            }
        
        # Node is aligned
        return {
            "aligned": True,
            "reason": "signed",
            "constitution_hash": constitution_hash,
            "signed_at": signature['signed_at'],
            "message": f"Node '{node_id}' is constitutionally aligned"
        }
    
    def sign_constitution(self, node_id: str, node_signature: str) -> bool:
        """
        Record a node's signature of the constitution
        
        Args:
            node_id: The node identifier
            node_signature: The node's cryptographic signature
        
        Returns:
            True if signature was recorded, False otherwise
        """
        if not self.constitution:
            return False
        
        constitution_hash = self.constitution['provenance']['hash']
        
        # Record signature
        self.signatures['signatures'][node_id] = {
            "constitution_hash": constitution_hash,
            "node_signature": node_signature,
            "signed_at": datetime.utcnow().isoformat() + 'Z'
        }
        
        self._save_signatures()
        return True
    
    def get_alignment_status(self) -> Dict[str, any]:
        """
        Get alignment status for all nodes
        
        Returns:
            Dict with overall alignment statistics
        """
        if not self.constitution:
            return {
                "constitution_loaded": False,
                "nodes": {}
            }
        
        expected_nodes = ["mirror", "core", "sage", "kronos", "shadow", "pulsemesh"]
        
        status = {
            "constitution_loaded": True,
            "constitution_id": self.constitution['constitution_id'],
            "constitution_hash": self.constitution['provenance']['hash'],
            "total_nodes": len(expected_nodes),
            "signed_nodes": 0,
            "unsigned_nodes": 0,
            "nodes": {}
        }
        
        for node_id in expected_nodes:
            alignment = self.verify_alignment(node_id)
            status['nodes'][node_id] = alignment
            
            if alignment['aligned']:
                status['signed_nodes'] += 1
            else:
                status['unsigned_nodes'] += 1
        
        return status


# Global instance
_checker = None

def get_checker() -> ConstitutionChecker:
    """Get or create the global constitution checker"""
    global _checker
    if _checker is None:
        _checker = ConstitutionChecker()
    return _checker


def verify_node_alignment(node_id: str) -> Dict[str, any]:
    """
    Convenience function to verify a node's constitutional alignment
    
    Args:
        node_id: The node identifier
    
    Returns:
        Alignment verification result
    """
    checker = get_checker()
    return checker.verify_alignment(node_id)


def sign_constitution(node_id: str, node_signature: str) -> bool:
    """
    Convenience function to sign the constitution
    
    Args:
        node_id: The node identifier
        node_signature: The node's cryptographic signature
    
    Returns:
        True if signature was recorded
    """
    checker = get_checker()
    return checker.sign_constitution(node_id, node_signature)
