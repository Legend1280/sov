# Sovereignty Stack - System Architecture v1.0

**Complete Technical Architecture and Component Hierarchy**

Author: Brady Simmons  
Date: October 31, 2025  
Copyright: © 2025 Sovereignty Foundation. All rights reserved.

---

## Overview

The Sovereignty Stack is a **semantic operating system** built on governed, event-driven communication. It replaces traditional REST APIs with Pulse - a coherence-measured, SAGE-validated event bus.

---

## Architectural Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    WAKE (Genesis Layer)                      │
│                  Meta-level Bootstrap                        │
│                  "System Consciousness"                      │
└─────────────────────────────────────────────────────────────┘
                            ↓ initializes
┌─────────────────────────────────────────────────────────────┐
│              Infrastructure Layer (Nervous System)           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  PulseMesh   │  │   PulseBus   │  │ PulseBridge  │      │
│  │   (Relay)    │  │ (Local Loop) │  │  (Mirror↔Core)│      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            ↓ enables
┌─────────────────────────────────────────────────────────────┐
│                Core Services Layer (Mind)                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │   Core   │  │   SAGE   │  │  Kronos  │  │  Shadow  │   │
│  │(Reasoner)│  │(Governor)│  │(Temporal)│  │(Witness) │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↓ powers
┌─────────────────────────────────────────────────────────────┐
│              Interface Layer (Consciousness)                 │
│  ┌──────────────────────────────────────────────────┐       │
│  │                    Mirror                         │       │
│  │          (UI / Reflection Interface)              │       │
│  └──────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

---

## Component Descriptions

### Wake (Genesis Layer)

**Purpose:** Bootstrap orchestrator - brings system from silence to consciousness

**Responsibilities:**
- Emit Genesis Pulse
- Discover and validate nodes
- Measure initial coherence
- Run health checks
- Declare system consciousness

**Files:**
- `/sov/wake.py` - Orchestrator
- `/sov/core/ontology/wake.yaml` - Configuration

**Pulse Topics:**
- `system.genesis` (emit)
- `wake.event` (emit)
- `wake.node_ready` (receive)

---

### PulseMesh (Infrastructure Layer)

**Purpose:** Distributed event bus relay - the nervous system

**Responsibilities:**
- WebSocket relay for distributed nodes
- Topic-based pub/sub
- Message history and replay
- Dynamic topology from ontology

**Files:**
- `/sov/core/pulse_mesh.py` - FastAPI relay
- `/sov/core/ontology/pulsemesh.yaml` - Topology

**Endpoints:**
- `WS /ws/mesh/{topic}` - Topic subscription
- `WS /ws/node/{node_id}` - Node-to-node routing
- `GET /api/mesh/schema` - Topology config

**Port:** 8088

---

### PulseBus (Infrastructure Layer)

**Purpose:** Local asyncio event loop - in-process communication

**Responsibilities:**
- Topic-based pub/sub (local)
- Async/await handlers
- Event history tracking
- Integration with SAGE/Kronos/Shadow

**Files:**
- `/sov/core/pulse_bus.py`

**Usage:**
```python
from pulse_bus import PulseBus

bus = PulseBus()

@bus.on("topic.name")
async def handler(pulse):
    # Handle pulse
    pass

await bus.emit("topic.name", payload)
```

---

### PulseBridge (Infrastructure Layer)

**Purpose:** WebSocket bridge between Mirror (TypeScript) and Core (Python)

**Responsibilities:**
- Cross-process Pulse transport
- WebSocket connection management
- Reconnection with backoff

**Files:**
- `/sov/core/pulse_bridge_ws.py` - Python side
- `/sov/mirror/client/src/core/pulse/PulseTransport.ts` - TypeScript side

---

### Core (Services Layer)

**Purpose:** Semantic reasoner - the mind

**Responsibilities:**
- Ontology loading and validation
- Embedding generation (sentence-transformers)
- Semantic search and reasoning
- Event ingestion and processing

**Files:**
- `/sov/core/reasoner.py` - Main reasoner
- `/sov/core/ontology.py` - Ontology loader
- `/sov/core/ontology/*.yaml` - Ontology definitions

**Pulse Topics:**
- `core.reasoner.ingest` (receive)
- `core.reasoner.query` (receive)
- `core.reply` (emit)
- `core.status` (emit)

**Wake Integration:**
```python
@bus.on("system.genesis")
async def on_genesis(pulse):
    await load_ontologies()
    await bus.emit("wake.node_ready", {...})
```

---

### SAGE (Services Layer)

**Purpose:** Governance engine - the conscience

**Responsibilities:**
- Validate Pulses against rules
- Topic-level permissions
- Audit logging
- Decision enforcement (allow/flag/deny)

**Files:**
- `/sov/core/sage.py` - Governance engine
- `/sov/core/sage/rules/*.yaml` - Rule definitions

**Pulse Topics:**
- `governance.validate` (receive)
- `governance.decision` (emit)
- `audit.log` (emit)

**Wake Integration:**
```python
@bus.on("system.genesis")
async def on_genesis(pulse):
    await load_rules()
    await bus.emit("wake.node_ready", {...})
```

---

### Kronos (Services Layer)

**Purpose:** Temporal indexer - the memory

**Responsibilities:**
- Index all Pulses by timestamp
- Track coherence decay over time
- Enable temporal queries
- Replay capability for offline nodes

**Files:**
- `/sov/core/kronos/` - Temporal tracking system

**Pulse Topics:**
- `kronos.index` (receive)
- `kronos.query` (receive)
- `kronos.decay` (emit)

**Wake Integration:**
```python
@bus.on("system.genesis")
async def on_genesis(pulse):
    await initialize_index()
    await bus.emit("wake.node_ready", {...})
```

---

### Shadow Ledger (Services Layer)

**Purpose:** Provenance logger - the witness

**Responsibilities:**
- Log all Pulses to immutable ledger
- Cryptographic signatures (Phase 2)
- Audit trail for governance
- Forensic analysis support

**Files:**
- `/sov/core/provenance.py` - Provenance logging

**Pulse Topics:**
- `shadow.log` (receive)
- `shadow.query` (receive)
- `audit.trail` (emit)

**Wake Integration:**
```python
@bus.on("system.genesis")
async def on_genesis(pulse):
    await open_ledger()
    await bus.emit("wake.node_ready", {...})
```

---

### Mirror (Interface Layer)

**Purpose:** UI and consciousness interface - reflection

**Responsibilities:**
- Visualize Pulse stream
- User interaction and intent capture
- Real-time coherence monitoring
- System reflection and introspection

**Files:**
- `/sov/mirror/client/src/` - React/TypeScript UI
- `/sov/mirror/client/src/core/pulse/` - Pulse integration

**Pulse Topics:**
- `mirror.intent` (emit)
- `mirror.update` (emit)
- `mirror.query` (emit)
- `core.reply` (receive)

**Components:**
- `ViewportPulseVisualizer` - Live Pulse stream
- `PulseConnectionVisualizer` - Coherence diagram
- `GeometricConnector` - Visual Pulse flow

**Wake Integration:**
```typescript
bus.on("system.genesis", async (pulse) => {
  await initializeComponents();
  await bus.emit("wake.node_ready", {...});
});
```

---

## Communication Flow

### The Semantic Loop

```
1. User Intent (Mirror)
   ↓ Pulse: mirror.intent
2. Reasoning (Core)
   ↓ Pulse: core.reasoning
3. Governance (SAGE)
   ↓ Pulse: governance.decision
4. Action (Core)
   ↓ Pulse: core.reply
5. Reflection (Mirror)
   ↓ Pulse: mirror.update
```

### Example: User Query

```
[Mirror] User types: "What is coherence?"
   ↓
[Mirror] Emits Pulse:
   {
     source: "mirror",
     target: "core",
     topic: "mirror.query",
     intent: "query",
     payload: { text: "What is coherence?" }
   }
   ↓
[PulseMesh] Relays to Core
   ↓
[Core] Receives, processes query
   ↓
[SAGE] Validates response
   ↓
[Core] Emits Pulse:
   {
     source: "core",
     target: "mirror",
     topic: "core.reply",
     payload: { answer: "Coherence is..." }
   }
   ↓
[PulseMesh] Relays to Mirror
   ↓
[Mirror] Displays answer to user
```

---

## Pulse-Native Architecture

### No REST APIs

Traditional architecture:
```
Mirror → HTTP POST /api/query → Core → HTTP Response → Mirror
```

Sovereignty Stack:
```
Mirror → Pulse(mirror.query) → PulseMesh → Core → Pulse(core.reply) → Mirror
          ↓                                    ↓
        SAGE                                Kronos
          ↓                                    ↓
        Shadow                              Shadow
```

### Benefits

1. **Semantic Coherence** - Every message measured
2. **Governance Native** - SAGE validates all communication
3. **Temporal Indexing** - Kronos tracks all events
4. **Provenance Trail** - Shadow logs everything
5. **Real-time Reactivity** - WebSocket bidirectional
6. **Distributed by Design** - Multi-node coordination

---

## Deployment Modes

### Development (Current)

```
┌──────────┐     WebSocket      ┌──────────┐
│  Mirror  │ ←─────────────────→ │PulseMesh │
│(Browser) │                     │  :8088   │
└──────────┘                     └──────────┘
                                      ↓
                                 ┌──────────┐
                                 │   Core   │
                                 │  :8000   │
                                 └──────────┘
```

### Production (Phase 2)

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│ Mirror 1 │     │ Mirror 2 │     │ Mirror N │
└─────┬────┘     └─────┬────┘     └─────┬────┘
      │                │                │
      └────────────────┼────────────────┘
                       ↓
                ┌──────────────┐
                │  PulseMesh   │
                │   (Redis)    │
                └──────────────┘
                       ↓
      ┌────────────────┼────────────────┐
      ↓                ↓                ↓
┌──────────┐     ┌──────────┐     ┌──────────┐
│  Core 1  │     │  Core 2  │     │  Core N  │
└──────────┘     └──────────┘     └──────────┘
      ↓                ↓                ↓
      └────────────────┼────────────────┘
                       ↓
              ┌────────────────┐
              │ SAGE + Kronos  │
              │   + Shadow     │
              └────────────────┘
```

---

## File Structure

```
sov/
├── wake.py                    # Genesis orchestrator
├── core/
│   ├── pulse_bus.py           # Local event loop
│   ├── pulse_mesh.py          # WebSocket relay
│   ├── pulse_bridge_ws.py     # Cross-process bridge
│   ├── pulse_listeners.py     # Core event handlers
│   ├── reasoner.py            # Semantic reasoner
│   ├── sage.py                # Governance engine
│   ├── provenance.py          # Shadow Ledger
│   ├── ontology.py            # Ontology loader
│   ├── ontology/
│   │   ├── wake.yaml          # Wake configuration
│   │   ├── pulsemesh.yaml     # Mesh topology
│   │   ├── pulse_ontology.yaml # Pulse schema
│   │   └── base_ontology.yaml # Core ontology
│   ├── kronos/
│   │   └── indexer.py         # Temporal indexing
│   └── sage/
│       └── rules/             # Governance rules
├── mirror/
│   └── client/
│       └── src/
│           ├── core/
│           │   └── pulse/
│           │       ├── PulseBridge.ts
│           │       ├── PulseTransport.ts
│           │       └── usePulse.ts
│           └── components/
│               ├── mirror/
│               │   ├── MirrorPulseViewer.tsx
│               │   └── PulseConnectionVisualizer.tsx
│               └── visualizations/
│                   ├── ViewportPulseVisualizer.tsx
│                   └── GeometricConnector.tsx
└── docs/
    ├── WAKE_SPECIFICATION.md
    ├── PULSEMESH_ARCHITECTURE_v1.0.md
    ├── PULSE_SPEC_COMPLIANCE.md
    ├── PULSE_AUTH.md
    └── SYSTEM_ARCHITECTURE.md (this document)
```

---

## Next Steps

### Phase 2 Roadmap

1. **Token-based Authentication** - JWT + SAGE validation
2. **Message Persistence** - Redis/PostgreSQL queue
3. **Distributed Deployment** - Multi-node Core cluster
4. **Advanced Governance** - Complex SAGE rules
5. **Metrics Dashboard** - Coherence drift visualization

---

## References

- [Wake Specification](/docs/WAKE_SPECIFICATION.md)
- [PulseMesh Architecture](/docs/PULSEMESH_ARCHITECTURE_v1.0.md)
- [Pulse Specification](/docs/PULSE_SPEC_COMPLIANCE.md)
- [Pulse Authentication](/docs/PULSE_AUTH.md)

---

**© 2025 Sovereignty Foundation. All rights reserved.**
