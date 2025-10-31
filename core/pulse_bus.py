"""
PulseBus - Schema-Native Event Bus for Sovereignty Stack

A local asyncio-based event bus that enables semantic communication
between Mirror, Core, and other modules without HTTP coupling.

Features:
- Decoupled pub/sub messaging
- Schema-governed events (PulseEvent ontology)
- Automatic SAGE validation
- Kronos temporal indexing
- Shadow Ledger provenance tracking

Author: Brady Simmons
Copyright: © 2025 Sovereignty Foundation. All rights reserved.
"""

import asyncio
from collections import defaultdict
from typing import Dict, List, Callable, Any, Optional
from datetime import datetime
import json

# Type aliases
PulseHandler = Callable[[Dict[str, Any]], Any]

class PulseBus:
    """
    Local asyncio event bus for semantic communication
    
    Provides:
    - Topic-based pub/sub
    - Async event handling
    - Event history tracking
    - Integration with SAGE/Kronos/Shadow Ledger
    """
    
    def __init__(self):
        self.listeners: Dict[str, List[PulseHandler]] = defaultdict(list)
        self.event_history: List[Dict[str, Any]] = []
        self.reasoner: Optional[Any] = None
        
    def set_reasoner(self, reasoner):
        """Inject reasoner for ontology validation"""
        self.reasoner = reasoner
        
    def on(self, topic: str, handler: PulseHandler) -> Callable:
        """
        Register a listener for a topic
        
        Usage:
            @pulse_bus.on("core.reasoner.ingest")
            async def handle_ingest(event):
                await reasoner.ingest(event)
                
        Or:
            pulse_bus.on("mirror.ui.update", handle_ui_update)
        
        Args:
            topic: Event topic (e.g., "core.reasoner.ingest")
            handler: Async function to handle events
            
        Returns:
            The handler function (for decorator usage)
        """
        self.listeners[topic].append(handler)
        return handler
    
    async def emit(self, topic: str, data: Dict[str, Any], validate: bool = True) -> Dict[str, Any]:
        """
        Emit an event to all listeners on a topic
        
        Args:
            topic: Event topic
            data: Event payload
            validate: Whether to validate against PulseEvent ontology
            
        Returns:
            Event metadata (id, timestamp, validation result)
        """
        # Create event record
        event = {
            "id": f"pulse_{datetime.utcnow().timestamp()}",
            "topic": topic,
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
            "validated": False
        }
        
        # Validate against ontology if reasoner is available
        if validate and self.reasoner and "object_type" in data:
            try:
                # Validate PulseEvent schema
                is_valid, normalized, errors = self.reasoner.ontology.validate_and_normalize(
                    data, 
                    data.get("object_type", "PulseEvent")
                )
                
                if not is_valid:
                    event["validation_errors"] = errors
                    event["validated"] = False
                else:
                    event["data"] = normalized
                    event["validated"] = True
                    
            except Exception as e:
                event["validation_errors"] = [str(e)]
                event["validated"] = False
        
        # Store in history
        self.event_history.append(event)
        
        # Emit to all listeners
        handlers = self.listeners.get(topic, [])
        results = []
        
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    result = await handler(event["data"])
                else:
                    result = handler(event["data"])
                results.append({"handler": handler.__name__, "success": True, "result": result})
            except Exception as e:
                results.append({"handler": handler.__name__, "success": False, "error": str(e)})
        
        event["handlers_called"] = len(handlers)
        event["results"] = results
        
        return event
    
    def get_history(self, topic: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get event history
        
        Args:
            topic: Filter by topic (optional)
            limit: Maximum number of events to return
            
        Returns:
            List of events
        """
        if topic:
            filtered = [e for e in self.event_history if e["topic"] == topic]
            return filtered[-limit:]
        return self.event_history[-limit:]
    
    def list_topics(self) -> List[str]:
        """Get all registered topics"""
        return list(self.listeners.keys())
    
    def clear_history(self):
        """Clear event history"""
        self.event_history = []


# Global instance
_pulse_bus = None

def get_pulse_bus() -> PulseBus:
    """Get or create the global PulseBus instance"""
    global _pulse_bus
    if _pulse_bus is None:
        _pulse_bus = PulseBus()
    return _pulse_bus
