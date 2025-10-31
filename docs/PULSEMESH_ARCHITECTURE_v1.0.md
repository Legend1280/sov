# PulseMesh Architecture v1.0

**Distributed Semantic Event Bus for the Sovereignty Stack**

Author: Brady Simmons  
Date: October 31, 2025  
Copyright: © 2025 Sovereignty Foundation. All rights reserved.

---

## Executive Summary

**PulseMesh** is the foundational communication layer of the Sovereignty Stack, replacing traditional REST APIs with a governed, event-driven semantic bus. It enables real-time, coherence-measured communication between Mirror (UI), Core (Reasoner), SAGE (Governor), and future nodes.

### Key Achievements

✅ **Zero-dependency local event bus** (Python asyncio)  
✅ **WebSocket-based distributed relay** (FastAPI)  
✅ **Transport abstraction layer** (Local/WebSocket/Mesh modes)  
✅ **Live Pulse visualization** (Mirror UI component)  
✅ **Ontology-driven topology** (YAML schema)  
✅ **SAGE governance hooks** (Phase 2 ready)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        PulseMesh                             │
│                  (Distributed Event Bus)                     │
└─────────────────────────────────────────────────────────────┘
           ↑                ↑                ↑
           │                │                │
    ┌──────┴──────┐  ┌──────┴──────┐  ┌──────┴──────┐
    │   Mirror    │  │    Core     │  │    SAGE     │
    │  (UI Layer) │  │ (Reasoner)  │  │ (Governor)  │
    └─────────────┘  └─────────────┘  └─────────────┘
```

### Communication Flow

1. **Mirror** emits Pulse → PulseMesh topic
2. **PulseMesh** validates & broadcasts to subscribers
3. **Core** receives Pulse → processes via ontology
4. **SAGE** validates governance rules
5. **Kronos** indexes temporal event
6. **Shadow Ledger** logs provenance
7. **Core** emits reply Pulse → Mirror

---

## Components

### 1. PulseBus (Core Event Loop)

**File:** `/sov/core/pulse_bus.py`

**Purpose:** In-process asyncio event bus for local communication

**Features:**
- Topic-based pub/sub
- Async/await handlers
- Zero external dependencies
- Decorator-based registration

**Usage:**
```python
from pulse_bus import on, emit

@on("core.reasoner.ingest")
async def handle_ingest(event):
    await reasoner.ingest(event)

await emit("core.reasoner.ingest", payload)
```

---

### 2. PulseMesh Relay

**File:** `/sov/core/pulse_mesh.py`

**Purpose:** FastAPI WebSocket relay for distributed nodes

**Endpoints:**
- `GET /` - Health check
- `GET /api/mesh/schema` - Topology configuration
- `GET /api/mesh/topics` - Active topics list
- `GET /api/mesh/history` - Message history
- `WS /ws/mesh/{topic}` - Topic subscription
- `WS /ws/node/{node_id}` - Node-to-node routing

**Features:**
- Topic-based broadcasting
- Message history (last 1000)
- Auto-reconnect support
- CORS enabled for development

**Launch:**
```bash
cd /home/ubuntu/sov/core
python3.11 pulse_mesh.py
# Runs on http://0.0.0.0:8088
```

---

### 3. PulseTransport (Mirror Abstraction)

**File:** `/sov/mirror/client/src/core/pulse/PulseTransport.ts`

**Purpose:** Transport abstraction layer for Mirror

**Modes:**
- **Local**: In-process PulseBridge (UI reactivity)
- **WebSocket**: Direct Core connection
- **Mesh**: PulseMesh relay (distributed)

**Usage:**
```typescript
const transport = new PulseTransport({
  mode: 'mesh',
  meshUrl: 'ws://localhost:8088',
  topic: 'mirror.intent'
});

transport.connect((msg: PulseMessage) => {
  console.log('Received:', msg);
});

transport.emit({
  source: 'mirror',
  target: 'core',
  topic: 'mirror.intent',
  payload: { text: 'Hello Core' }
});
```

---

### 4. ViewportPulseVisualizer

**File:** `/sov/mirror/client/src/components/visualizations/ViewportPulseVisualizer.tsx`

**Purpose:** Live Pulse stream monitor in Mirror UI

**Features:**
- Real-time Pulse log (last 100 messages)
- Color-coded coherence scores
- Intent badges (update/query/create/govern/reflect)
- Connection status indicator
- Stats: total pulses, avg coherence, active topics

**Display:**
- Source → Target routing
- Topic name
- Coherence percentage
- Timestamp
- Payload preview

---

### 5. PulseMesh Ontology

**File:** `/sov/core/ontology/pulsemesh.yaml`

**Purpose:** Define mesh topology and topic schema

**Nodes:**
- **mirror** - UI layer (topics: mirror.intent, mirror.update, mirror.query)
- **core** - Reasoner (topics: core.reply, core.status, core.ingest)
- **sage** - Governor (topics: audit.log, governance.decision)

**Topics:**
- `mirror.intent` - User intentions from UI
- `core.reply` - Reasoning responses
- `audit.log` - SAGE audit trail
- `governance.decision` - SAGE rulings

---

## PulseObject Schema

```typescript
interface PulseMessage {
  source: string;          // Emitting node ID
  target: string;          // Receiving node ID
  topic: string;           // Topic name
  intent?: string;         // update|query|create|govern|reflect
  payload: any;            // Message payload
  coherence?: number;      // 0.0-1.0 coherence score
  timestamp?: string;      // ISO 8601 timestamp
  metadata?: Record<string, any>;  // Additional metadata
}
```

---

## Integration with Sovereignty Stack

### SAGE Governance (Phase 2)

Every Pulse will trigger:
1. **Topic-level permissions** - SAGE validates sender can emit to topic
2. **Payload validation** - SAGE checks ontology compliance
3. **Audit logging** - All Pulses logged to Shadow Ledger
4. **Decision enforcement** - SAGE can allow/flag/deny Pulses

### Kronos Temporal Indexing

- Every Pulse gets temporal index
- Decay tracking for coherence drift
- Replay capability for offline nodes

### Shadow Ledger Provenance

- Full Pulse history logged
- Cryptographic signatures (Phase 2)
- Audit trail for governance

---

## Deployment Modes

### Development (Current)

```
Mirror (Browser) → PulseMesh (localhost:8088) → Core (localhost:8000)
```

**Mode:** Stub (no authentication)  
**Transport:** WebSocket  
**Topology:** Static YAML

### Production (Phase 2)

```
Mirror → PulseMesh (distributed) → Core Cluster
                ↕
              SAGE + Kronos + Shadow
```

**Mode:** Token (JWT authentication)  
**Transport:** WebSocket + Redis pub/sub  
**Topology:** Dynamic from Core ontology API

---

## Testing

### 1. Start PulseMesh Relay

```bash
cd /home/ubuntu/sov/core
python3.11 pulse_mesh.py
```

### 2. Start Mirror

```bash
cd /home/ubuntu/sov/mirror/client
pnpm run dev
```

### 3. Send Test Pulse

Open Mirror → Viewport 1 shows live Pulse stream

Send message via input → Pulse appears in visualizer

### 4. Verify Flow

```bash
# Check PulseMesh health
curl http://localhost:8088/

# Check active topics
curl http://localhost:8088/api/mesh/topics

# Check message history
curl http://localhost:8088/api/mesh/history
```

---

## Phase 2 Roadmap

### Token Mode Authentication

**File:** `pulse_auth.py`

**Features:**
- JWT-based node identity
- SAGE public key verification
- Topic-level permissions
- Unauthorized access rejection

**Flow:**
1. Node requests JWT from SAGE
2. JWT includes: node_id, role, allowed_topics
3. PulseMesh verifies JWT on connect
4. Unauthorized topics trigger SAGE audit

### Message Persistence

**File:** `pulse_replay.py`

**Features:**
- Persistent message queue (Redis/PostgreSQL)
- Replay for offline nodes
- Guaranteed delivery
- Message deduplication

### Governance Integration

**File:** `pulse_governor.py`

**Features:**
- Real-time SAGE validation
- Topic-based access control
- Payload schema enforcement
- Coherence threshold enforcement

### Metrics Dashboard

**File:** `ViewportPulseMetrics.tsx`

**Features:**
- Coherence decay visualization
- Latency monitoring
- Throughput graphs
- Topic activity heatmap

---

## File Structure

```
sov/
├── core/
│   ├── pulse_bus.py              # Local event bus
│   ├── pulse_mesh.py             # WebSocket relay
│   ├── pulse_listeners.py        # Core event handlers
│   ├── pulse_bridge_ws.py        # WebSocket bridge
│   └── ontology/
│       └── pulsemesh.yaml        # Topology schema
│
├── mirror/client/src/
│   ├── core/pulse/
│   │   ├── PulseTransport.ts     # Transport abstraction
│   │   ├── PulseBridge.ts        # Local event bridge
│   │   └── usePulse.ts           # React hook
│   └── components/visualizations/
│       └── ViewportPulseVisualizer.tsx  # Live monitor
│
└── docs/
    ├── PULSE_SPEC_COMPLIANCE.md  # v1.0 spec compliance
    └── PULSEMESH_ARCHITECTURE_v1.0.md  # This document
```

---

## Benefits Over REST APIs

### 1. **Semantic Coherence**
- Every message has coherence score
- Drift detection and monitoring
- Temporal indexing via Kronos

### 2. **Governance Native**
- SAGE validates every Pulse
- Topic-based permissions
- Audit trail in Shadow Ledger

### 3. **Real-time Reactivity**
- WebSocket bidirectional communication
- No polling required
- Instant UI updates

### 4. **Distributed by Design**
- Mesh topology from ontology
- Multi-node coordination
- Load balancing ready

### 5. **Provenance Tracking**
- Full message history
- Cryptographic signatures
- Replay capability

---

## Conclusion

PulseMesh transforms the Sovereignty Stack from a collection of microservices into a **unified semantic organism**. Every interaction is:

- **Governed** by SAGE
- **Indexed** by Kronos
- **Logged** by Shadow Ledger
- **Measured** for coherence

This architecture eliminates REST coupling, enables distributed reasoning, and provides the foundation for autonomous multi-agent coordination.

**Status:** Phase 1 Complete (Functional Prototype)  
**Next:** Phase 2 - Governance, Authentication, Persistence

---

## References

- [PULSE Specification v1.0](/docs/PULSE_SPEC_COMPLIANCE.md)
- [Mirror Command Spec](/docs/COMMANDS/MIRROR_COMMAND_SPEC_v0.1.md)
- [Core Ontology System](/core/ontology/)
- [SAGE Governance](/core/sage.py)
- [Kronos Temporal Tracking](/core/kronos/)

---

**© 2025 Sovereignty Foundation. All rights reserved.**
