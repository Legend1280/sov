"""
Pulse Listeners - Core handlers for PulseEvent ingestion

Registers listeners on PulseBus that:
- Ingest PulseEvents into Core's ontology
- Apply SAGE governance validation
- Track temporal events with Kronos
- Log provenance to Shadow Ledger

Author: Brady Simmons
Copyright: © 2025 Sovereignty Foundation. All rights reserved.
"""

from typing import Dict, Any
from datetime import datetime

from pulse_bus import get_pulse_bus
from reasoner import get_reasoner

# Initialize
pulse_bus = get_pulse_bus()
reasoner = None

async def handle_ingest(event_data: Dict[str, Any]):
    """
    Handle PulseEvent ingestion
    
    Pipeline:
    1. Validate against PulseEvent ontology
    2. Generate embedding
    3. Run SAGE validation
    4. Store in Core database
    5. Index with Kronos
    6. Log to Shadow Ledger
    
    Args:
        event_data: Pulse event payload
    """
    try:
        print(f"[PulseListeners] Ingesting PulseEvent: {event_data.get('topic', 'unknown')}")
        
        # Extract object type and data
        object_type = event_data.get('object_type', 'PulseEvent')
        
        # Prepare data for ingestion
        ingest_data = {
            'source': event_data.get('source', 'unknown'),
            'target': event_data.get('target', 'unknown'),
            'topic': event_data.get('topic', 'unknown'),
            'intent': event_data.get('intent', 'update'),
            'payload': event_data.get('payload', ''),
            'coherence': float(event_data.get('coherence', 0.0)),
            'status': event_data.get('status', 'active'),
            'sage_ruleset': event_data.get('sage_ruleset', 'default-governance'),
            'vector_id': event_data.get('vector_id'),
            'metadata': event_data.get('metadata', {})
        }
        
        # Ingest through reasoner (triggers full pipeline)
        result = reasoner.ingest(
            object_type=object_type,
            data=ingest_data,
            actor='mirror'
        )
        
        print(f"[PulseListeners] PulseEvent ingested successfully:")
        print(f"  - ID: {result['symbolic']['id']}")
        print(f"  - Coherence: {result['sage']['coherence_score']:.2f}")
        print(f"  - Trust: {result['sage']['trust_score']:.2f}")
        print(f"  - Decision: {result['sage'].get('decision', 'allow')}")
        
        return result
        
    except Exception as e:
        print(f"[PulseListeners] Error ingesting PulseEvent: {e}")
        import traceback
        traceback.print_exc()
        raise


async def handle_query(event_data: Dict[str, Any]):
    """
    Handle query Pulse events
    
    Args:
        event_data: Query parameters
    """
    try:
        print(f"[PulseListeners] Handling query: {event_data.get('topic', 'unknown')}")
        
        # Future: Implement semantic query handling
        # For now, just log the query
        query_text = event_data.get('payload', '')
        print(f"[PulseListeners] Query text: {query_text}")
        
        return {"status": "query_received", "query": query_text}
        
    except Exception as e:
        print(f"[PulseListeners] Error handling query: {e}")
        raise


async def handle_update(event_data: Dict[str, Any]):
    """
    Handle update Pulse events
    
    Args:
        event_data: Update parameters
    """
    try:
        print(f"[PulseListeners] Handling update: {event_data.get('topic', 'unknown')}")
        
        # Future: Implement object update handling
        # For now, just log the update
        update_data = event_data.get('payload', '')
        print(f"[PulseListeners] Update data: {update_data}")
        
        return {"status": "update_received", "data": update_data}
        
    except Exception as e:
        print(f"[PulseListeners] Error handling update: {e}")
        raise


def initialize_listeners(reasoner_instance):
    """
    Initialize Pulse listeners with reasoner instance
    
    Args:
        reasoner_instance: The Core reasoner instance
    """
    global reasoner
    reasoner = reasoner_instance
    pulse_bus.set_reasoner(reasoner)
    
    print("[PulseListeners] Registering Core listeners...")
    
    # Register listeners
    pulse_bus.on("core.reasoner.ingest", handle_ingest)
    pulse_bus.on("core.reasoner.query", handle_query)
    pulse_bus.on("core.reasoner.update", handle_update)
    
    print("[PulseListeners] Listeners registered:")
    print(f"  - core.reasoner.ingest")
    print(f"  - core.reasoner.query")
    print(f"  - core.reasoner.update")
