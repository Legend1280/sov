"""
Security Event Listener

Listens for security events on PulseBus and triggers SAGE validation,
Kronos indexing, and Shadow logging as defined in security.yaml ontology.

Author: Brady Simmons
Copyright: © 2025 Sovereignty Foundation. All rights reserved.
"""

import asyncio
from datetime import datetime
from typing import Dict, Any
import yaml
from pathlib import Path

# Import Core components
from pulse_bus import PulseBus
import sage
import kronos
import provenance as shadow

# Load security ontology
def load_security_ontology():
    """Load security.yaml ontology"""
    ontology_path = Path("/home/ubuntu/sov/core/ontology/security.yaml")
    if ontology_path.exists():
        with open(ontology_path, 'r') as f:
            return yaml.safe_load(f)
    return {}

security_ontology = load_security_ontology()
print(f"[SecurityListener] Loaded security ontology v{security_ontology.get('ontology', {}).get('version', 'unknown')}")

# Initialize PulseBus
pulse_bus = PulseBus()

# Security event handlers
async def handle_handshake_initiated(event: Dict[str, Any]):
    """Handle auth.handshake.initiated event"""
    print(f"[SecurityListener] Handshake initiated from {event['payload'].get('client_id')}")
    
    # Kronos indexing
    await kronos.index_event({
        "event_type": "auth.handshake.initiated",
        "timestamp": event['payload'].get('timestamp'),
        "client_id": event['payload'].get('client_id'),
        "source": event['payload'].get('source')
    })
    
    # Shadow logging
    await shadow.log_event({
        "category": "authentication",
        "event": "handshake_initiated",
        "data": event['payload']
    })

async def handle_handshake_success(event: Dict[str, Any]):
    """Handle auth.handshake.success event"""
    client_id = event['payload'].get('client_id')
    print(f"[SecurityListener] ✅ Handshake successful for {client_id}")
    
    # Kronos indexing
    await kronos.index_event({
        "event_type": "auth.handshake.success",
        "timestamp": datetime.utcnow().isoformat(),
        "client_id": client_id,
        "session_id": event['payload'].get('session_id'),
        "authentication_method": event['payload'].get('authentication_method')
    })
    
    # Shadow logging
    await shadow.log_event({
        "category": "authentication",
        "event": "handshake_success",
        "data": event['payload']
    })

async def handle_handshake_failed(event: Dict[str, Any]):
    """Handle auth.handshake.failed event"""
    reason = event['payload'].get('reason')
    client_id = event['payload'].get('client_id', 'unknown')
    print(f"[SecurityListener] ❌ Handshake failed for {client_id}: {reason}")
    
    # SAGE validation (check if this is a security threat)
    sage_decision = await sage.validate_event({
        "event_type": "auth.handshake.failed",
        "client_id": client_id,
        "reason": reason,
        "close_code": event['payload'].get('close_code')
    })
    
    if sage_decision.get('threat_level') == 'high':
        print(f"[SecurityListener] ⚠️ SAGE detected high threat from {client_id}")
        # Emit security violation event
        await pulse_bus.emit("security.violation.detected", {
            "violation_type": "repeated_auth_failure",
            "source": client_id,
            "details": event['payload']
        })
    
    # Kronos indexing
    await kronos.index_event({
        "event_type": "auth.handshake.failed",
        "timestamp": datetime.utcnow().isoformat(),
        "client_id": client_id,
        "reason": reason,
        "sage_decision": sage_decision
    })
    
    # Shadow logging
    await shadow.log_event({
        "category": "authentication",
        "event": "handshake_failed",
        "severity": "warning",
        "data": event['payload']
    })

async def handle_session_created(event: Dict[str, Any]):
    """Handle auth.session.created event"""
    session_id = event['payload'].get('session_id')
    print(f"[SecurityListener] Session created: {session_id}")
    
    # Kronos indexing
    await kronos.index_event({
        "event_type": "auth.session.created",
        "timestamp": datetime.utcnow().isoformat(),
        "session_id": session_id,
        "client_id": event['payload'].get('client_id'),
        "expires_at": event['payload'].get('expires_at')
    })
    
    # Shadow logging
    await shadow.log_event({
        "category": "session_management",
        "event": "session_created",
        "data": event['payload']
    })

async def handle_security_violation(event: Dict[str, Any]):
    """Handle security.violation.detected event"""
    violation_type = event['payload'].get('violation_type')
    source = event['payload'].get('source')
    print(f"[SecurityListener] 🚨 SECURITY VIOLATION: {violation_type} from {source}")
    
    # SAGE validation (immediate action required)
    sage_decision = await sage.validate_event({
        "event_type": "security.violation.detected",
        "violation_type": violation_type,
        "source": source,
        "details": event['payload'].get('details')
    })
    
    # Take action based on SAGE decision
    if sage_decision.get('action') == 'block':
        print(f"[SecurityListener] 🛑 SAGE decision: BLOCK {source}")
        # Emit block event (PulseMesh will handle)
        await pulse_bus.emit("security.action.block", {
            "target": source,
            "reason": violation_type,
            "duration": sage_decision.get('duration', 3600)  # 1 hour default
        })
    
    # Kronos indexing (critical event)
    await kronos.index_event({
        "event_type": "security.violation.detected",
        "timestamp": datetime.utcnow().isoformat(),
        "violation_type": violation_type,
        "source": source,
        "sage_decision": sage_decision,
        "priority": "critical"
    })
    
    # Shadow logging (critical)
    await shadow.log_event({
        "category": "security_violation",
        "event": "violation_detected",
        "severity": "critical",
        "data": event['payload'],
        "sage_decision": sage_decision
    })

# Register event listeners
async def initialize_security_listeners():
    """Register all security event listeners with PulseBus"""
    print("[SecurityListener] Initializing security event listeners...")
    
    # Authentication events
    pulse_bus.on("auth.handshake.initiated", handle_handshake_initiated)
    pulse_bus.on("auth.handshake.success", handle_handshake_success)
    pulse_bus.on("auth.handshake.failed", handle_handshake_failed)
    
    # Session events
    pulse_bus.on("auth.session.created", handle_session_created)
    
    # Security violation events
    pulse_bus.on("security.violation.detected", handle_security_violation)
    
    print("[SecurityListener] ✅ Security listeners registered")
    print("[SecurityListener] Monitoring topics:")
    print("  - auth.handshake.*")
    print("  - auth.session.*")
    print("  - security.violation.*")

# Main entry point
if __name__ == "__main__":
    print("[SecurityListener] Starting security event listener...")
    asyncio.run(initialize_security_listeners())
    
    # Keep running
    try:
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        print("\n[SecurityListener] Shutting down...")
