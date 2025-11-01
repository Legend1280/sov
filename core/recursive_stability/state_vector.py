"""
Self-State Vector Generator

Captures the current state of the Mirror-Core-SAGE loop as a compact
embedding vector that can be fed back through the system to test
recursive stability.

Author: Brady Simmons
Copyright: © 2025 Sovereignty Foundation. All rights reserved.
"""

import json
import hashlib
from datetime import datetime
from typing import Dict, List, Any
import numpy as np

class StateVectorGenerator:
    """Generates self-state vectors for recursive stability testing"""
    
    def __init__(self):
        self.state_history: List[Dict[str, Any]] = []
        self.vector_history: List[np.ndarray] = []
    
    def capture_state(self, 
                     mirror_state: Dict[str, Any],
                     core_state: Dict[str, Any],
                     sage_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Capture the current state of the Mirror-Core-SAGE loop
        
        Args:
            mirror_state: Mirror's active components and render state
            core_state: Core's reasoning state and intent
            sage_state: SAGE's governance and constraint state
        
        Returns:
            Complete state snapshot with hash
        """
        state = {
            "mirror": {
                "active_components": mirror_state.get("active_components", []),
                "rendered_objects": mirror_state.get("rendered_objects", []),
                "viewport_state": mirror_state.get("viewport_state", "idle"),
                "pulse_count": mirror_state.get("pulse_count", 0)
            },
            "core": {
                "state_hash": self._hash_state(core_state),
                "intent": core_state.get("intent", "observe_self"),
                "reasoning_depth": core_state.get("reasoning_depth", 0),
                "ontology_objects": core_state.get("ontology_objects", [])
            },
            "sage": {
                "constraint_state": sage_state.get("constraint_state", "enforcing"),
                "validation_count": sage_state.get("validation_count", 0),
                "violations": sage_state.get("violations", 0),
                "governance_active": sage_state.get("governance_active", True)
            },
            "timestamp": datetime.utcnow().isoformat() + 'Z',
            "iteration": len(self.state_history)
        }
        
        # Add state hash
        state["state_hash"] = self._hash_state(state)
        
        # Store in history
        self.state_history.append(state)
        
        return state
    
    def state_to_vector(self, state: Dict[str, Any]) -> np.ndarray:
        """
        Convert state snapshot to embedding vector
        
        This is a simple feature vector. In production, you'd use:
        - MiniLM embeddings
        - OpenAI embeddings
        - Custom trained embeddings
        
        Args:
            state: State snapshot
        
        Returns:
            Numpy array embedding (128-dim)
        """
        features = []
        
        # Mirror features (32 dims)
        mirror = state["mirror"]
        features.extend([
            len(mirror["active_components"]),
            len(mirror["rendered_objects"]),
            1.0 if mirror["viewport_state"] == "active" else 0.0,
            mirror["pulse_count"] / 100.0  # Normalize
        ])
        # Pad to 32
        features.extend([0.0] * 28)
        
        # Core features (32 dims)
        core = state["core"]
        features.extend([
            core["reasoning_depth"] / 10.0,  # Normalize
            len(core["ontology_objects"]),
            1.0 if core["intent"] == "observe_self" else 0.5,
            hash(core["state_hash"]) % 100 / 100.0  # Hash as feature
        ])
        # Pad to 32
        features.extend([0.0] * 28)
        
        # SAGE features (32 dims)
        sage = state["sage"]
        features.extend([
            sage["validation_count"] / 100.0,  # Normalize
            sage["violations"] / 10.0,  # Normalize
            1.0 if sage["governance_active"] else 0.0,
            1.0 if sage["constraint_state"] == "enforcing" else 0.5
        ])
        # Pad to 32
        features.extend([0.0] * 28)
        
        # Meta features (32 dims)
        features.extend([
            state["iteration"] / 100.0,  # Normalize
            hash(state["state_hash"]) % 100 / 100.0
        ])
        # Pad to 32
        features.extend([0.0] * 30)
        
        vector = np.array(features[:128], dtype=np.float32)
        
        # Store in history
        self.vector_history.append(vector)
        
        return vector
    
    def get_baseline_vector(self) -> np.ndarray:
        """Get the baseline (first) state vector"""
        if len(self.vector_history) == 0:
            raise ValueError("No vectors in history")
        return self.vector_history[0]
    
    def get_latest_vector(self) -> np.ndarray:
        """Get the most recent state vector"""
        if len(self.vector_history) == 0:
            raise ValueError("No vectors in history")
        return self.vector_history[-1]
    
    def get_vector_at(self, iteration: int) -> np.ndarray:
        """Get state vector at specific iteration"""
        if iteration >= len(self.vector_history):
            raise ValueError(f"Iteration {iteration} not in history")
        return self.vector_history[iteration]
    
    def _hash_state(self, state: Any) -> str:
        """Generate SHA256 hash of state"""
        state_str = json.dumps(state, sort_keys=True)
        return hashlib.sha256(state_str.encode()).hexdigest()
    
    def export_state(self, iteration: int = -1) -> Dict[str, Any]:
        """Export state snapshot for visualization"""
        if iteration == -1:
            iteration = len(self.state_history) - 1
        
        if iteration >= len(self.state_history):
            raise ValueError(f"Iteration {iteration} not in history")
        
        state = self.state_history[iteration]
        vector = self.vector_history[iteration]
        
        return {
            "iteration": iteration,
            "state": state,
            "vector": vector.tolist(),
            "vector_norm": float(np.linalg.norm(vector)),
            "timestamp": state["timestamp"]
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about captured states"""
        if len(self.state_history) == 0:
            return {
                "total_iterations": 0,
                "vector_dimensions": 128,
                "state_count": 0
            }
        
        return {
            "total_iterations": len(self.state_history),
            "vector_dimensions": 128,
            "state_count": len(self.state_history),
            "latest_iteration": self.state_history[-1]["iteration"],
            "latest_timestamp": self.state_history[-1]["timestamp"],
            "vector_norm_mean": float(np.mean([np.linalg.norm(v) for v in self.vector_history])),
            "vector_norm_std": float(np.std([np.linalg.norm(v) for v in self.vector_history]))
        }


# Example usage
if __name__ == "__main__":
    generator = StateVectorGenerator()
    
    # Simulate state capture
    for i in range(5):
        mirror_state = {
            "active_components": ["ObjectRenderer", "LogosButton"],
            "rendered_objects": ["logos"],
            "viewport_state": "active",
            "pulse_count": i * 10
        }
        
        core_state = {
            "intent": "observe_self",
            "reasoning_depth": i,
            "ontology_objects": ["logos", "sage", "kronos"]
        }
        
        sage_state = {
            "constraint_state": "enforcing",
            "validation_count": i * 5,
            "violations": 0,
            "governance_active": True
        }
        
        state = generator.capture_state(mirror_state, core_state, sage_state)
        vector = generator.state_to_vector(state)
        
        print(f"\nIteration {i}:")
        print(f"  State Hash: {state['state_hash'][:16]}...")
        print(f"  Vector Norm: {np.linalg.norm(vector):.4f}")
    
    print("\n" + "="*60)
    print("Statistics:")
    stats = generator.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
