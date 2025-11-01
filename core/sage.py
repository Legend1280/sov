"""
SAGE - Semantic Governance Engine (Pulse-Native)

Validates coherence, trust, and logical consistency through Pulse events.

SAGE provides:
- Coherence scoring (semantic consistency)
- Trust scoring (provenance-based reputation)
- Action validation (permissions and rules)
- Logical consistency checks
- Wake-aware initialization
- Pulse-native communication

Author: Brady Simmons
Copyright: © 2025 Sovereignty Foundation. All rights reserved.
"""

import numpy as np
import asyncio
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from pulse_bus import PulseBus

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SAGE")

# Global PulseBus instance
bus = PulseBus()

class SAGE:
    """Semantic Governance Engine - Pulse-Native"""
    
    def __init__(self):
        # Governance thresholds
        self.COHERENCE_THRESHOLD = 0.75
        self.TRUST_THRESHOLD = 0.70
        self.SIMILARITY_THRESHOLD = 0.80
        self.is_awake = False
        
        # Register Pulse listeners
        self._register_pulse_listeners()
    
    def _register_pulse_listeners(self):
        """Register SAGE's Pulse event listeners"""
        
        @bus.on("system.genesis")
        async def on_genesis(pulse):
            """Respond to Wake genesis pulse"""
            logger.info("[SAGE] Awakening - loading governance rules")
            await self.initialize()
            
            await bus.emit("wake.node_ready", {
                "node_id": "sage",
                "role": "governor",
                "services": ["validation", "governance", "audit"],
                "timestamp": datetime.utcnow().isoformat()
            })
            
            self.is_awake = True
            logger.info("[SAGE] Governance engine operational")
        
        @bus.on("governance.validate")
        async def on_validate_request(pulse):
            """Handle validation requests via Pulse"""
            payload = pulse.get("payload", {})
            obj = payload.get("object", {})
            vector = payload.get("vector")
            provenance = payload.get("provenance", [])
            
            # Perform validation
            result = self.validate_object(obj, vector, provenance)
            
            # Emit decision
            await bus.emit("governance.decision", {
                "request_id": pulse.get("id"),
                "source": pulse.get("source"),
                "decision": result["decision"],
                "validation": result,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Log to audit trail
            await bus.emit("audit.log", {
                "event": "governance.validation",
                "object_id": obj.get("id", "unknown"),
                "decision": result["decision"],
                "coherence": result["coherence_score"],
                "trust": result["trust_score"],
                "timestamp": datetime.utcnow().isoformat()
            })
        
        @bus.on("system.health_check")
        async def on_health_check(pulse):
            """Respond to health check requests"""
            await bus.emit("system.health_response", {
                "node_id": "sage",
                "status": "operational" if self.is_awake else "initializing",
                "coherence": 1.0,
                "uptime": self.get_uptime(),
                "timestamp": datetime.utcnow().isoformat()
            })
    
    async def initialize(self):
        """Initialize SAGE governance engine"""
        # Load governance rules (future: from YAML files)
        logger.info("[SAGE] Loading governance rules...")
        # Placeholder for rule loading
        await asyncio.sleep(0.1)
        logger.info("[SAGE] Governance rules loaded")
    
    def get_uptime(self) -> float:
        """Get SAGE uptime in seconds"""
        # Placeholder - would track actual start time
        return 0.0
    
    def coherence_check(self, obj: Dict[str, Any], vector: Optional[np.ndarray] = None) -> float:
        """
        Check semantic coherence of an object
        
        Coherence = how well the symbolic and vector representations align
        
        Returns: coherence score (0.0 - 1.0)
        """
        # Base coherence from object completeness
        required_fields = ["object_type", "data"]
        completeness = sum(1 for field in required_fields if field in obj) / len(required_fields)
        
        # If vector is provided, check its quality
        vector_quality = 1.0
        if vector is not None:
            # Check vector magnitude (should be normalized)
            magnitude = np.linalg.norm(vector)
            vector_quality = min(1.0, magnitude / 1.5)  # Penalize very small vectors
        
        # Combine scores
        coherence = (completeness * 0.6) + (vector_quality * 0.4)
        
        return round(coherence, 3)
    
    def trust_score(self, object_id: str, provenance_chain: list) -> float:
        """
        Calculate trust score based on provenance
        
        Trust = reputation based on:
        - Number of validations
        - Source credibility
        - Age of object
        - Consistency over time
        
        Returns: trust score (0.0 - 1.0)
        """
        if not provenance_chain:
            return 0.5  # Neutral trust for new objects
        
        # Count validations
        validations = sum(1 for event in provenance_chain if event.get("action") == "validated")
        validation_score = min(1.0, validations / 3.0)  # Max out at 3 validations
        
        # Check source credibility
        sources = [event.get("actor", "unknown") for event in provenance_chain]
        trusted_sources = ["SAGE", "Core", "Mirror.UI"]
        credibility = sum(1 for source in sources if source in trusted_sources) / max(len(sources), 1)
        
        # Age factor (older = more trusted, up to a point)
        if provenance_chain:
            first_event = provenance_chain[-1]  # Oldest event
            try:
                created_at = datetime.fromisoformat(first_event.get("timestamp", ""))
                age_days = (datetime.utcnow() - created_at).days
                age_score = min(1.0, age_days / 30.0)  # Max out at 30 days
            except:
                age_score = 0.0
        else:
            age_score = 0.0
        
        # Combine scores
        trust = (validation_score * 0.4) + (credibility * 0.4) + (age_score * 0.2)
        
        return round(trust, 3)
    
    def validate_action(self, user: str, action: str, obj: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate if an action is allowed
        
        Returns: (allowed, reason)
        """
        # For now, simple rules
        # In future, this could be expanded with role-based access control
        
        allowed_actions = ["read", "create", "update", "delete", "validate"]
        
        if action not in allowed_actions:
            return False, f"Unknown action: {action}"
        
        # Anyone can read
        if action == "read":
            return True, "Read access granted"
        
        # Only trusted actors can validate
        if action == "validate":
            trusted_actors = ["SAGE", "Core", "admin"]
            if user not in trusted_actors:
                return False, "Only trusted actors can validate"
        
        # Default: allow
        return True, f"Action '{action}' allowed for user '{user}'"
    
    def validate_relation(self, source_type: str, target_type: str, similarity: float) -> Tuple[bool, str]:
        """
        Validate if a semantic relation makes sense
        
        Returns: (valid, reason)
        """
        # Check similarity threshold
        if similarity < self.SIMILARITY_THRESHOLD:
            return False, f"Similarity too low: {similarity:.3f} < {self.SIMILARITY_THRESHOLD}"
        
        # Type compatibility rules
        compatible_pairs = [
            ("Transaction", "Transaction"),
            ("Transaction", "Account"),
            ("Account", "Account"),
            ("Forecast", "Transaction"),
            ("Document", "Document"),
            ("Concept", "Concept"),
        ]
        
        pair = (source_type, target_type)
        reverse_pair = (target_type, source_type)
        
        if pair not in compatible_pairs and reverse_pair not in compatible_pairs:
            return False, f"Incompatible types: {source_type} <-> {target_type}"
        
        return True, "Relation validated"
    
    def coherence_score_from_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Calculate coherence score from vector similarity
        
        Uses cosine similarity
        """
        # Normalize vectors
        vec1_norm = vec1 / (np.linalg.norm(vec1) + 1e-10)
        vec2_norm = vec2 / (np.linalg.norm(vec2) + 1e-10)
        
        # Cosine similarity
        similarity = np.dot(vec1_norm, vec2_norm)
        
        return round(float(similarity), 3)
    
    def validate_object(self, obj: Dict[str, Any], vector: Optional[np.ndarray] = None, provenance: Optional[list] = None) -> Dict[str, Any]:
        """
        Full SAGE validation of an object
        
        Returns: SAGE metadata with decision (allow/flag/deny)
        """
        # Calculate coherence
        coherence = self.coherence_check(obj, vector)
        
        # Calculate trust
        trust = self.trust_score(obj.get("id", "unknown"), provenance or [])
        
        # Decision logic (Milestone 2 contract)
        if coherence >= 0.8 and trust >= 0.7:
            decision = "allow"
            validated = True
            rationale = "Object meets coherence and trust thresholds"
        elif coherence >= 0.6 and trust >= 0.5:
            decision = "flag"
            validated = False
            rationale = "Object marginally coherent, flagged for review"
        else:
            decision = "deny"
            validated = False
            rationale = f"Coherence {coherence:.2f} or trust {trust:.2f} below threshold"
        
        return {
            "coherence_score": coherence,
            "trust_score": trust,
            "validated": validated,
            "decision": decision,
            "rationale": rationale,
            "thresholds": {
                "coherence": self.COHERENCE_THRESHOLD,
                "trust": self.TRUST_THRESHOLD
            }
        }


# Singleton instance
_sage = None

def get_sage() -> SAGE:
    """Get the global SAGE instance"""
    global _sage
    if _sage is None:
        _sage = SAGE()
    return _sage
