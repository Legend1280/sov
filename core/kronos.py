"""
Kronos - Temporal Indexer (Pulse-Native)

Tracks all Pulses over time, measures coherence decay, and enables temporal queries.

Kronos provides:
- Temporal indexing of all Pulses
- Coherence decay tracking
- Event replay capability
- Time-based queries
- Wake-aware initialization
- Pulse-native communication

Author: Brady Simmons
Copyright: © 2025 Sovereignty Foundation. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
from pulse_bus import PulseBus

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Kronos")

# Global PulseBus instance
bus = PulseBus()

class Kronos:
    """Temporal Indexer - Pulse-Native"""
    
    def __init__(self):
        self.temporal_index: Dict[str, List[Dict]] = defaultdict(list)
        self.decay_rates: Dict[str, float] = {}
        self.is_awake = False
        self.start_time = datetime.utcnow()
        
        # Register Pulse listeners
        self._register_pulse_listeners()
    
    def _register_pulse_listeners(self):
        """Register Kronos's Pulse event listeners"""
        
        @bus.on("system.genesis")
        async def on_genesis(pulse):
            """Respond to Wake genesis pulse"""
            logger.info("[Kronos] Awakening - initializing temporal index")
            await self.initialize()
            
            await bus.emit("wake.node_ready", {
                "node_id": "kronos",
                "role": "temporal",
                "services": ["indexing", "decay_tracking", "replay"],
                "timestamp": datetime.utcnow().isoformat()
            })
            
            self.is_awake = True
            logger.info("[Kronos] Temporal indexer operational")
        
        @bus.on("*")  # Listen to ALL Pulses
        async def on_any_pulse(pulse):
            """Auto-index all Pulses"""
            if not self.is_awake:
                return
            
            # Index the Pulse
            topic = pulse.get("topic", "unknown")
            timestamp = pulse.get("timestamp", datetime.utcnow().isoformat())
            
            self.temporal_index[topic].append({
                "pulse": pulse,
                "indexed_at": datetime.utcnow().isoformat()
            })
            
            # Track decay
            await self.track_decay(topic, pulse)
        
        @bus.on("kronos.query")
        async def on_query(pulse):
            """Handle temporal queries"""
            payload = pulse.get("payload", {})
            query_type = payload.get("type")
            topic = payload.get("topic")
            start_time = payload.get("start_time")
            end_time = payload.get("end_time")
            
            results = self.query_temporal_index(
                topic=topic,
                start_time=start_time,
                end_time=end_time
            )
            
            await bus.emit("kronos.query_result", {
                "request_id": pulse.get("id"),
                "results": results,
                "count": len(results),
                "timestamp": datetime.utcnow().isoformat()
            })
        
        @bus.on("shadow.evidence.stored")
        async def on_evidence_stored(pulse):
            """Index test evidence for temporal drift analysis"""
            if not self.is_awake:
                return
            
            payload = pulse.get("payload", {})
            test_id = payload.get("test_id")
            
            # Store in temporal index for drift tracking
            self.temporal_index["test_evidence"].append({
                "test_id": test_id,
                "mode": payload.get("mode"),
                "sample_count": payload.get("sample_count"),
                "timestamp": payload.get("timestamp"),
                "indexed_at": datetime.utcnow().isoformat()
            })
            
            logger.info(f"[Kronos] Indexed test evidence: {test_id}")
        
        @bus.on("kronos.drift.query")
        async def on_drift_query(pulse):
            """Handle temporal drift queries for test evidence"""
            if not self.is_awake:
                return
            
            # Get test evidence timeline
            evidence_timeline = self.temporal_index.get("test_evidence", [])
            
            # Calculate drift metrics
            drift_analysis = {
                "total_tests": len(evidence_timeline),
                "timeline": evidence_timeline[-10:],  # Last 10 tests
                "drift_detected": len(evidence_timeline) > 1
            }
            
            await bus.emit("kronos.drift.result", {
                "request_id": pulse.get("id"),
                "analysis": drift_analysis,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            logger.info(f"[Kronos] Drift query returned {len(evidence_timeline)} indexed tests")
        
        @bus.on("system.health_check")
        async def on_health_check(pulse):
            """Respond to health check requests"""
            await bus.emit("system.health_response", {
                "node_id": "kronos",
                "status": "operational" if self.is_awake else "initializing",
                "coherence": 1.0,
                "indexed_events": sum(len(events) for events in self.temporal_index.values()),
                "uptime": self.get_uptime(),
                "timestamp": datetime.utcnow().isoformat()
            })
    
    async def initialize(self):
        """Initialize Kronos temporal indexer"""
        logger.info("[Kronos] Initializing temporal index...")
        # Clear index
        self.temporal_index.clear()
        self.decay_rates.clear()
        await asyncio.sleep(0.1)
        logger.info("[Kronos] Temporal index ready")
    
    def get_uptime(self) -> float:
        """Get Kronos uptime in seconds"""
        return (datetime.utcnow() - self.start_time).total_seconds()
    
    async def track_decay(self, topic: str, pulse: Dict[str, Any]):
        """Track coherence decay for a Pulse over time"""
        coherence = pulse.get("metadata", {}).get("coherence", 1.0)
        timestamp = pulse.get("timestamp", datetime.utcnow().isoformat())
        
        # Calculate decay rate (simplified)
        # In production, this would use more sophisticated models
        try:
            pulse_time = datetime.fromisoformat(timestamp)
            age_seconds = (datetime.utcnow() - pulse_time).total_seconds()
            
            # Exponential decay: coherence * e^(-λt)
            # λ = 0.0001 (decay constant)
            decay_rate = 0.0001
            current_coherence = coherence * (2.71828 ** (-decay_rate * age_seconds))
            
            # Store decay rate
            pulse_id = pulse.get("id", "unknown")
            self.decay_rates[pulse_id] = current_coherence
            
            # Emit decay event if coherence drops below threshold
            if current_coherence < 0.7 and coherence >= 0.7:
                await bus.emit("kronos.decay", {
                    "pulse_id": pulse_id,
                    "topic": topic,
                    "original_coherence": coherence,
                    "current_coherence": current_coherence,
                    "age_seconds": age_seconds,
                    "timestamp": datetime.utcnow().isoformat()
                })
        except Exception as e:
            logger.error(f"[Kronos] Error tracking decay: {e}")
    
    def query_temporal_index(
        self,
        topic: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None
    ) -> List[Dict]:
        """Query the temporal index"""
        results = []
        
        # Parse time filters
        start_dt = datetime.fromisoformat(start_time) if start_time else None
        end_dt = datetime.fromisoformat(end_time) if end_time else None
        
        # Filter by topic
        topics_to_search = [topic] if topic else self.temporal_index.keys()
        
        for t in topics_to_search:
            for entry in self.temporal_index.get(t, []):
                pulse = entry["pulse"]
                pulse_time = datetime.fromisoformat(pulse.get("timestamp", datetime.utcnow().isoformat()))
                
                # Apply time filters
                if start_dt and pulse_time < start_dt:
                    continue
                if end_dt and pulse_time > end_dt:
                    continue
                
                results.append(entry)
        
        # Sort by timestamp (newest first)
        results.sort(
            key=lambda x: x["pulse"].get("timestamp", ""),
            reverse=True
        )
        
        return results
    
    def get_decay_status(self, pulse_id: str) -> Optional[float]:
        """Get current coherence decay for a Pulse"""
        return self.decay_rates.get(pulse_id)
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about the temporal index"""
        total_events = sum(len(events) for events in self.temporal_index.values())
        topics = list(self.temporal_index.keys())
        
        return {
            "total_events": total_events,
            "total_topics": len(topics),
            "topics": topics,
            "uptime_seconds": self.get_uptime(),
            "decay_tracked": len(self.decay_rates)
        }


# Singleton instance
_kronos = None

def get_kronos() -> Kronos:
    """Get the global Kronos instance"""
    global _kronos
    if _kronos is None:
        _kronos = Kronos()
    return _kronos
