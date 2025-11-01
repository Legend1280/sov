"""
Semantic Coherence Checker

Measures whether the self-model maintains semantic meaning across
recursive iterations. Stability without meaning isn't enough —
we must ensure ΔMeaning → 0 while maintaining ΔState → 0.

Uses trust coefficient from narrative coherence theory.

Author: Brady Simmons
Copyright: © 2025 Sovereignty Foundation. All rights reserved.
"""

import numpy as np
from typing import Dict, List, Any, Tuple
from state_vector import StateVectorGenerator

class SemanticCoherenceChecker:
    """Checks semantic coherence across recursive iterations"""
    
    def __init__(self):
        self.baseline_vector: np.ndarray = None
        self.trust_history: List[float] = []
        self.coherence_history: List[float] = []
        self.meaning_drift_history: List[float] = []
        self.trust_threshold = 0.9  # 90% trust required
    
    def set_baseline(self, vector: np.ndarray):
        """
        Set the baseline vector for coherence comparison
        
        Args:
            vector: Baseline state vector
        """
        self.baseline_vector = vector.copy()
    
    def calculate_trust_coefficient(self, 
                                    current_vector: np.ndarray,
                                    baseline_vector: np.ndarray = None) -> float:
        """
        Calculate trust coefficient between current and baseline vectors
        
        Trust coefficient measures how much the current state can be
        "trusted" to represent the same semantic meaning as the baseline.
        
        Formula:
            trust = (1 - normalized_distance) * coherence_factor
        
        Args:
            current_vector: Current state vector
            baseline_vector: Baseline vector (uses self.baseline_vector if None)
        
        Returns:
            Trust coefficient [0, 1]
        """
        if baseline_vector is None:
            if self.baseline_vector is None:
                raise ValueError("No baseline vector set")
            baseline_vector = self.baseline_vector
        
        # Calculate normalized Euclidean distance
        distance = np.linalg.norm(current_vector - baseline_vector)
        max_distance = np.linalg.norm(baseline_vector) * 2  # Max possible distance
        normalized_distance = min(1.0, distance / max_distance)
        
        # Calculate cosine similarity (coherence factor)
        dot_product = np.dot(current_vector, baseline_vector)
        norm1 = np.linalg.norm(current_vector)
        norm2 = np.linalg.norm(baseline_vector)
        
        if norm1 == 0 or norm2 == 0:
            coherence_factor = 0.0
        else:
            coherence_factor = max(0.0, dot_product / (norm1 * norm2))
        
        # Trust = (1 - distance) * coherence
        trust = (1.0 - normalized_distance) * coherence_factor
        
        return max(0.0, min(1.0, trust))
    
    def calculate_semantic_coherence(self,
                                     current_vector: np.ndarray,
                                     baseline_vector: np.ndarray = None) -> float:
        """
        Calculate semantic coherence score
        
        Coherence measures how well the current state maintains
        the semantic structure of the baseline.
        
        Args:
            current_vector: Current state vector
            baseline_vector: Baseline vector (uses self.baseline_vector if None)
        
        Returns:
            Coherence score [0, 1]
        """
        if baseline_vector is None:
            if self.baseline_vector is None:
                raise ValueError("No baseline vector set")
            baseline_vector = self.baseline_vector
        
        # Cosine similarity
        dot_product = np.dot(current_vector, baseline_vector)
        norm1 = np.linalg.norm(current_vector)
        norm2 = np.linalg.norm(baseline_vector)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = dot_product / (norm1 * norm2)
        
        # Normalize to [0, 1]
        coherence = (similarity + 1.0) / 2.0
        
        return max(0.0, min(1.0, coherence))
    
    def calculate_meaning_drift(self,
                                current_vector: np.ndarray,
                                baseline_vector: np.ndarray = None) -> float:
        """
        Calculate meaning drift (ΔMeaning)
        
        Drift measures how much the semantic meaning has changed
        from the baseline. Lower is better.
        
        Args:
            current_vector: Current state vector
            baseline_vector: Baseline vector (uses self.baseline_vector if None)
        
        Returns:
            Meaning drift [0, ∞) where 0 = no drift
        """
        if baseline_vector is None:
            if self.baseline_vector is None:
                raise ValueError("No baseline vector set")
            baseline_vector = self.baseline_vector
        
        # Normalized Euclidean distance
        distance = np.linalg.norm(current_vector - baseline_vector)
        baseline_norm = np.linalg.norm(baseline_vector)
        
        if baseline_norm == 0:
            return float('inf')
        
        drift = distance / baseline_norm
        
        return float(drift)
    
    def check_coherence(self, current_vector: np.ndarray) -> Dict[str, Any]:
        """
        Comprehensive coherence check
        
        Args:
            current_vector: Current state vector
        
        Returns:
            Coherence metrics dictionary
        """
        if self.baseline_vector is None:
            # First iteration - set baseline
            self.set_baseline(current_vector)
            return {
                "trust_coefficient": 1.0,
                "semantic_coherence": 1.0,
                "meaning_drift": 0.0,
                "coherent": True,
                "baseline": True
            }
        
        trust = self.calculate_trust_coefficient(current_vector)
        coherence = self.calculate_semantic_coherence(current_vector)
        drift = self.calculate_meaning_drift(current_vector)
        
        # Store in history
        self.trust_history.append(trust)
        self.coherence_history.append(coherence)
        self.meaning_drift_history.append(drift)
        
        # Check if coherent
        coherent = trust >= self.trust_threshold
        
        return {
            "trust_coefficient": float(trust),
            "semantic_coherence": float(coherence),
            "meaning_drift": float(drift),
            "coherent": coherent,
            "baseline": False
        }
    
    def get_coherence_metrics(self) -> Dict[str, Any]:
        """
        Get overall coherence metrics
        
        Returns:
            Metrics dictionary
        """
        if len(self.trust_history) == 0:
            return {
                "iterations": 0,
                "mean_trust": None,
                "min_trust": None,
                "latest_trust": None,
                "mean_coherence": None,
                "mean_drift": None,
                "coherent": False
            }
        
        return {
            "iterations": len(self.trust_history),
            "mean_trust": float(np.mean(self.trust_history)),
            "min_trust": float(np.min(self.trust_history)),
            "max_trust": float(np.max(self.trust_history)),
            "latest_trust": float(self.trust_history[-1]),
            "mean_coherence": float(np.mean(self.coherence_history)),
            "latest_coherence": float(self.coherence_history[-1]),
            "mean_drift": float(np.mean(self.meaning_drift_history)),
            "latest_drift": float(self.meaning_drift_history[-1]),
            "min_drift": float(np.min(self.meaning_drift_history)),
            "max_drift": float(np.max(self.meaning_drift_history)),
            "coherent": float(self.trust_history[-1]) >= self.trust_threshold,
            "trust_threshold": self.trust_threshold
        }
    
    def is_semantically_stable(self) -> bool:
        """
        Check if system is semantically stable
        
        Returns:
            True if stable (trust > threshold and drift → 0)
        """
        if len(self.trust_history) < 3:
            return False
        
        # Check recent trust scores
        recent_trust = self.trust_history[-3:]
        recent_drift = self.meaning_drift_history[-3:]
        
        # All trust scores must be above threshold
        trust_stable = all(t >= self.trust_threshold for t in recent_trust)
        
        # Drift must be decreasing or stable
        drift_stable = recent_drift[-1] <= recent_drift[0]
        
        return trust_stable and drift_stable


# Example usage
if __name__ == "__main__":
    from state_vector import StateVectorGenerator
    
    print("=" * 60)
    print("SEMANTIC COHERENCE TEST")
    print("=" * 60)
    
    vector_gen = StateVectorGenerator()
    coherence_checker = SemanticCoherenceChecker()
    
    # Simulate 15 iterations with gradual convergence
    for i in range(15):
        # Simulate state that gradually stabilizes
        noise_factor = max(0, 1.0 - i / 10.0)
        
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
        
        state = vector_gen.capture_state(mirror_state, core_state, sage_state)
        vector = vector_gen.state_to_vector(state)
        
        result = coherence_checker.check_coherence(vector)
        
        if not result["baseline"]:
            print(f"\nIteration {i}:")
            print(f"  Trust Coefficient: {result['trust_coefficient']:.6f}")
            print(f"  Semantic Coherence: {result['semantic_coherence']:.6f}")
            print(f"  Meaning Drift: {result['meaning_drift']:.6f}")
            print(f"  Coherent: {result['coherent']}")
    
    print("\n" + "=" * 60)
    print("COHERENCE METRICS")
    print("=" * 60)
    
    metrics = coherence_checker.get_coherence_metrics()
    for key, value in metrics.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.6f}")
        else:
            print(f"  {key}: {value}")
    
    print("\n" + "=" * 60)
    print("SEMANTIC STABILITY ASSESSMENT")
    print("=" * 60)
    
    if coherence_checker.is_semantically_stable():
        print("  ✅ SEMANTIC STABILITY ACHIEVED")
        print(f"  Trust coefficient: {metrics['latest_trust']:.6f} (threshold: {metrics['trust_threshold']:.2f})")
        print(f"  Meaning drift: {metrics['latest_drift']:.6f} → 0")
    else:
        print("  ⚠️  SEMANTIC STABILITY NOT YET ACHIEVED")
        print(f"  Trust coefficient: {metrics['latest_trust']:.6f} (threshold: {metrics['trust_threshold']:.2f})")
