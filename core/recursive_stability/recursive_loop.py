"""
Recursive Feedback System

Implements the Mirror → Core → SAGE → Mirror loop with embedding
similarity measurement to test for recursive stability.

Tests whether the system converges toward equilibrium (ΔState → 0)
or diverges/oscillates.

Author: Brady Simmons
Copyright: © 2025 Sovereignty Foundation. All rights reserved.
"""

import numpy as np
from typing import Dict, List, Any, Tuple
from datetime import datetime
from state_vector import StateVectorGenerator

class RecursiveFeedbackLoop:
    """Manages recursive feedback through Mirror-Core-SAGE loop"""
    
    def __init__(self):
        self.vector_gen = StateVectorGenerator()
        self.similarity_history: List[float] = []
        self.delta_history: List[float] = []
        self.iteration = 0
        self.converged = False
        self.convergence_threshold = 0.999  # 99.9% similarity
        self.convergence_window = 3  # Must be stable for 3 iterations
    
    def cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two vectors
        
        Args:
            vec1: First vector
            vec2: Second vector
        
        Returns:
            Similarity score [0, 1]
        """
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = dot_product / (norm1 * norm2)
        
        # Clamp to [0, 1]
        return max(0.0, min(1.0, similarity))
    
    def euclidean_distance(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Calculate Euclidean distance between two vectors
        
        Args:
            vec1: First vector
            vec2: Second vector
        
        Returns:
            Distance (lower is more similar)
        """
        return float(np.linalg.norm(vec1 - vec2))
    
    def iterate(self, 
                mirror_state: Dict[str, Any],
                core_state: Dict[str, Any],
                sage_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run one iteration of the recursive loop
        
        Args:
            mirror_state: Current Mirror state
            core_state: Current Core state
            sage_state: Current SAGE state
        
        Returns:
            Iteration results with similarity metrics
        """
        # Capture current state
        state = self.vector_gen.capture_state(mirror_state, core_state, sage_state)
        vector = self.vector_gen.state_to_vector(state)
        
        # Calculate similarity with previous iteration
        similarity = None
        delta = None
        
        if self.iteration > 0:
            prev_vector = self.vector_gen.get_vector_at(self.iteration - 1)
            similarity = self.cosine_similarity(vector, prev_vector)
            delta = self.euclidean_distance(vector, prev_vector)
            
            self.similarity_history.append(similarity)
            self.delta_history.append(delta)
        
        # Check for convergence
        if self._check_convergence():
            self.converged = True
        
        self.iteration += 1
        
        return {
            "iteration": self.iteration - 1,
            "state_hash": state["state_hash"],
            "vector_norm": float(np.linalg.norm(vector)),
            "similarity": similarity,
            "delta": delta,
            "converged": self.converged,
            "timestamp": state["timestamp"]
        }
    
    def _check_convergence(self) -> bool:
        """
        Check if the loop has converged
        
        Returns:
            True if converged, False otherwise
        """
        if len(self.similarity_history) < self.convergence_window:
            return False
        
        # Check last N iterations
        recent_similarities = self.similarity_history[-self.convergence_window:]
        
        # All must be above threshold
        return all(s >= self.convergence_threshold for s in recent_similarities)
    
    def get_convergence_metrics(self) -> Dict[str, Any]:
        """
        Get convergence metrics
        
        Returns:
            Metrics dictionary
        """
        if len(self.similarity_history) == 0:
            return {
                "converged": False,
                "iterations": self.iteration,
                "mean_similarity": None,
                "latest_similarity": None,
                "mean_delta": None,
                "latest_delta": None
            }
        
        return {
            "converged": self.converged,
            "iterations": self.iteration,
            "mean_similarity": float(np.mean(self.similarity_history)),
            "latest_similarity": float(self.similarity_history[-1]),
            "min_similarity": float(np.min(self.similarity_history)),
            "max_similarity": float(np.max(self.similarity_history)),
            "mean_delta": float(np.mean(self.delta_history)),
            "latest_delta": float(self.delta_history[-1]),
            "min_delta": float(np.min(self.delta_history)),
            "max_delta": float(np.max(self.delta_history)),
            "convergence_threshold": self.convergence_threshold,
            "convergence_window": self.convergence_window
        }
    
    def get_similarity_trend(self) -> List[float]:
        """Get similarity history for plotting"""
        return self.similarity_history.copy()
    
    def get_delta_trend(self) -> List[float]:
        """Get delta history for plotting"""
        return self.delta_history.copy()
    
    def reset(self):
        """Reset the loop"""
        self.vector_gen = StateVectorGenerator()
        self.similarity_history = []
        self.delta_history = []
        self.iteration = 0
        self.converged = False


# Example usage
if __name__ == "__main__":
    loop = RecursiveFeedbackLoop()
    
    print("=" * 60)
    print("RECURSIVE STABILITY TEST")
    print("=" * 60)
    
    # Simulate 20 iterations with gradual convergence
    for i in range(20):
        # Simulate state that gradually stabilizes
        noise_factor = max(0, 1.0 - i / 15.0)  # Decreasing noise
        
        mirror_state = {
            "active_components": ["ObjectRenderer", "LogosButton"],
            "rendered_objects": ["logos"],
            "viewport_state": "active",
            "pulse_count": 100 + int(np.random.normal(0, noise_factor * 5))
        }
        
        core_state = {
            "intent": "observe_self",
            "reasoning_depth": 5 + int(np.random.normal(0, noise_factor * 2)),
            "ontology_objects": ["logos", "sage", "kronos"]
        }
        
        sage_state = {
            "constraint_state": "enforcing",
            "validation_count": 50 + int(np.random.normal(0, noise_factor * 3)),
            "violations": 0,
            "governance_active": True
        }
        
        result = loop.iterate(mirror_state, core_state, sage_state)
        
        if result["similarity"] is not None:
            print(f"\nIteration {result['iteration']}:")
            print(f"  Similarity: {result['similarity']:.6f}")
            print(f"  Delta: {result['delta']:.6f}")
            print(f"  Converged: {result['converged']}")
    
    print("\n" + "=" * 60)
    print("CONVERGENCE METRICS")
    print("=" * 60)
    
    metrics = loop.get_convergence_metrics()
    for key, value in metrics.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.6f}")
        else:
            print(f"  {key}: {value}")
    
    print("\n" + "=" * 60)
    print("STABILITY ASSESSMENT")
    print("=" * 60)
    
    if metrics["converged"]:
        print("  ✅ RECURSIVE STABILITY ACHIEVED")
        print(f"  System converged after {metrics['iterations']} iterations")
        print(f"  Final similarity: {metrics['latest_similarity']:.6f}")
        print(f"  Final delta: {metrics['latest_delta']:.6f}")
    else:
        print("  ⚠️  RECURSIVE STABILITY NOT YET ACHIEVED")
        print(f"  Current similarity: {metrics['latest_similarity']:.6f}")
        print(f"  Threshold: {metrics['convergence_threshold']:.6f}")
