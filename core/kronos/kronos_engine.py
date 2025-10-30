"""
Kronos Engine - Temporal Intelligence for Sovereignty Stack

Tracks semantic drift, trust decay, and coherence evolution over time.
Every semantic object deserves temporal continuity and transparent change.

Memory is an ethical act.
"""

import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import math


class KronosEngine:
    """
    Temporal reasoning engine that tracks how semantic objects change over time.
    
    Key Concepts:
    - Coherence Drift (ΔC): How much an object's meaning has shifted
    - Trust Decay: How confidence degrades without validation
    - Temporal Baseline: Original semantic state for comparison
    """
    
    def __init__(self):
        # Trust decay parameters
        self.trust_half_life_days = 30.0  # Trust decays 50% after 30 days
        self.min_trust = 0.1  # Floor to prevent complete decay
        
        # Coherence drift thresholds
        self.drift_threshold_minor = 0.05  # 5% change = minor drift
        self.drift_threshold_major = 0.15  # 15% change = major drift
    
    def calculate_trust_decay(
        self, 
        initial_trust: float, 
        created_at: datetime, 
        current_time: Optional[datetime] = None
    ) -> float:
        """
        Calculate trust decay using exponential decay model.
        
        Trust(t) = max(min_trust, initial_trust * e^(-λt))
        where λ = ln(2) / half_life
        """
        if current_time is None:
            current_time = datetime.utcnow()
        
        # Calculate time delta in days
        delta = (current_time - created_at).total_seconds() / 86400.0
        
        # Exponential decay
        decay_constant = math.log(2) / self.trust_half_life_days
        decayed_trust = initial_trust * math.exp(-decay_constant * delta)
        
        # Apply floor
        return max(self.min_trust, decayed_trust)
    
    def calculate_coherence_drift(
        self, 
        baseline_vector: np.ndarray, 
        current_vector: np.ndarray
    ) -> Tuple[float, str]:
        """
        Calculate semantic drift between baseline and current embeddings.
        
        Returns:
            (drift_magnitude, drift_status)
            
        drift_status: "stable" | "minor_drift" | "major_drift"
        """
        # Cosine similarity (1.0 = identical, 0.0 = orthogonal)
        similarity = np.dot(baseline_vector, current_vector) / (
            np.linalg.norm(baseline_vector) * np.linalg.norm(current_vector)
        )
        
        # Convert to drift (0.0 = no drift, 1.0 = complete drift)
        drift = 1.0 - similarity
        
        # Classify drift
        if drift < self.drift_threshold_minor:
            status = "stable"
        elif drift < self.drift_threshold_major:
            status = "minor_drift"
        else:
            status = "major_drift"
        
        return drift, status
    
    def assess_temporal_health(
        self,
        object_id: str,
        initial_trust: float,
        created_at: datetime,
        baseline_vector: Optional[np.ndarray] = None,
        current_vector: Optional[np.ndarray] = None,
        current_time: Optional[datetime] = None
    ) -> Dict:
        """
        Comprehensive temporal health assessment for a semantic object.
        
        Returns governance recommendation based on trust decay and drift.
        """
        if current_time is None:
            current_time = datetime.utcnow()
        
        # Calculate trust decay
        current_trust = self.calculate_trust_decay(initial_trust, created_at, current_time)
        trust_delta = current_trust - initial_trust
        
        # Calculate coherence drift (if vectors provided)
        drift_magnitude = 0.0
        drift_status = "stable"
        
        if baseline_vector is not None and current_vector is not None:
            drift_magnitude, drift_status = self.calculate_coherence_drift(
                baseline_vector, current_vector
            )
        
        # Determine governance action
        action = self._determine_action(current_trust, drift_status)
        
        return {
            "object_id": object_id,
            "timestamp": current_time.isoformat(),
            "trust": {
                "initial": initial_trust,
                "current": current_trust,
                "delta": trust_delta,
                "age_days": (current_time - created_at).days
            },
            "drift": {
                "magnitude": drift_magnitude,
                "status": drift_status
            },
            "action": action,
            "requires_validation": action in ["flag", "deny"]
        }
    
    def _determine_action(self, trust: float, drift_status: str) -> str:
        """
        Determine governance action based on trust and drift.
        
        Rules:
        - High trust + stable = allow
        - Medium trust + minor drift = flag
        - Low trust or major drift = deny
        """
        if trust >= 0.7 and drift_status == "stable":
            return "allow"
        elif trust >= 0.5 and drift_status in ["stable", "minor_drift"]:
            return "flag"
        else:
            return "deny"
    
    def predict_decay_timeline(
        self, 
        initial_trust: float, 
        created_at: datetime,
        days_ahead: int = 90
    ) -> List[Dict]:
        """
        Predict trust decay over time for visualization.
        
        Returns list of {day, trust, action} predictions.
        """
        timeline = []
        
        for day in range(0, days_ahead + 1, 7):  # Weekly samples
            future_time = created_at + timedelta(days=day)
            trust = self.calculate_trust_decay(initial_trust, created_at, future_time)
            action = self._determine_action(trust, "stable")
            
            timeline.append({
                "day": day,
                "date": future_time.isoformat(),
                "trust": trust,
                "action": action
            })
        
        return timeline
