# Pulse Migration Guide
**Transforming the Sovereignty Stack to Pulse-Native Architecture**

---

## Philosophy

**Old Way:** Components call each other directly (REST APIs, function calls)  
**New Way:** Components emit and listen to Pulses (event-driven, semantic)

**Benefits:**
- ✅ Real-time reactivity (no polling)
- ✅ SAGE governance on every message
- ✅ Kronos temporal tracking automatic
- ✅ Shadow provenance built-in
- ✅ Coherence measurement native
- ✅ Distributed by design

---

## Pattern 1: REST API Calls → Pulse Emit

### Before ❌
```typescript
// Mirror calling Core API
const response = await fetch('http://localhost:8001/api/ingest', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ data: payload })
});

const result = await response.json();
console.log(result);
```

### After ✅
```typescript
// Mirror emitting Pulse
import { PulseBridge } from '@/core/pulse/PulseBridge';

PulseBridge.emit('core.ingest', {
  source: 'mirror',
  target: 'core',
  intent: 'create',
  payload: { data: payload },
  metadata: {
    timestamp: new Date().toISOString(),
    user_id: currentUser.id
  }
});

// Listen for response
PulseBridge.on('core.reply', (pulse) => {
  if (pulse.metadata.request_id === requestId) {
    console.log('Core responded:', pulse.payload);
  }
});
```

---

## Pattern 2: Direct Function Calls → Pulse Events

### Before ❌
```python
# Core calling SAGE directly
from sage import get_sage

sage = get_sage()
decision = sage.validate(data)

if decision['approved']:
    process_data(data)
```

### After ✅
```python
# Core emitting Pulse to SAGE
from pulse_bus import PulseBus

bus = PulseBus()

# Emit validation request
await bus.emit('governance.validate', {
    'source': 'core',
    'target': 'sage',
    'payload': data
})

# Listen for SAGE decision
@bus.on('governance.decision')
async def handle_sage_decision(pulse):
    if pulse['payload']['approved']:
        await process_data(pulse['payload']['data'])
```

---

## Pattern 3: Polling → Event Listening

### Before ❌
```typescript
// Poll for status updates
setInterval(async () => {
  const response = await fetch('/api/status');
  const status = await response.json();
  updateUI(status);
}, 5000); // Poll every 5 seconds
```

### After ✅
```typescript
// Listen for status Pulses
PulseBridge.on('system.status', (pulse) => {
  updateUI(pulse.payload);
});

// Status emitted automatically by system
```

---

## Pattern 4: Event Emitters → PulseBridge

### Before ❌
```typescript
import { EventEmitter } from 'events';

const emitter = new EventEmitter();
emitter.on('data-updated', (data) => {
  console.log(data);
});

emitter.emit('data-updated', { foo: 'bar' });
```

### After ✅
```typescript
import { PulseBridge } from '@/core/pulse/PulseBridge';

PulseBridge.on('data.updated', (pulse) => {
  console.log(pulse.payload);
});

PulseBridge.emit('data.updated', {
  source: 'component-a',
  target: 'component-b',
  payload: { foo: 'bar' }
});
```

---

## Pattern 5: Callbacks → Pulse Responses

### Before ❌
```typescript
function processData(data, callback) {
  // Do work
  callback(null, result);
}

processData(myData, (err, result) => {
  if (err) handleError(err);
  else handleSuccess(result);
});
```

### After ✅
```typescript
// Emit request
PulseBridge.emit('data.process', {
  source: 'caller',
  target: 'processor',
  payload: myData,
  metadata: { request_id: generateId() }
});

// Listen for response
PulseBridge.on('data.processed', (pulse) => {
  if (pulse.status === 'completed') {
    handleSuccess(pulse.payload);
  } else {
    handleError(pulse.payload.error);
  }
});
```

---

## Migration Checklist

### For Each Component:

- [ ] Identify all outgoing calls (API, functions, events)
- [ ] Replace with `PulseBridge.emit(topic, pulse)`
- [ ] Identify all incoming calls (endpoints, handlers)
- [ ] Replace with `PulseBridge.on(topic, handler)`
- [ ] Add SAGE validation if needed
- [ ] Test Pulse flow end-to-end
- [ ] Remove old code (fetch, direct imports)

---

## Topic Naming Convention

```
<domain>.<action>
```

**Examples:**
- `mirror.intent` - User intentions from Mirror
- `core.ingest` - Data ingestion requests
- `core.reply` - Core responses
- `governance.validate` - SAGE validation requests
- `governance.decision` - SAGE decisions
- `kronos.index` - Temporal indexing
- `shadow.provenance` - Provenance logging
- `system.status` - System status updates
- `system.genesis` - Wake sequence

---

## PulseObject Schema

Every Pulse must conform to:

```typescript
interface PulseObject {
  source: string;        // Sending component
  target: string;        // Receiving component  
  topic: string;         // Routing topic
  intent: 'update' | 'query' | 'create' | 'govern' | 'reflect';
  payload: any;          // Actual data
  coherence: number;     // 0.0-1.0
  status: 'active' | 'completed' | 'failed';
  sage_ruleset: string;  // Governance ruleset
  vector_id?: string;    // Embedding ID
  metadata: {
    timestamp: string;
    reasoning?: string;
    request_id?: string;
  };
}
```

---

## Testing Pulse Flow

### 1. Send Test Pulse
```typescript
PulseBridge.emit('test.ping', {
  source: 'test',
  target: 'echo',
  intent: 'query',
  payload: { message: 'Hello' }
});
```

### 2. Listen for Response
```typescript
PulseBridge.on('test.pong', (pulse) => {
  console.log('Received:', pulse.payload);
});
```

### 3. Check Logs
- SAGE validation: Check governance logs
- Kronos indexing: Check temporal index
- Shadow logging: Check provenance ledger

---

## Common Pitfalls

### ❌ Don't: Wait for synchronous responses
```typescript
const result = PulseBridge.emit('topic', data); // Returns void!
```

### ✅ Do: Listen for async responses
```typescript
PulseBridge.emit('topic', data);
PulseBridge.on('topic.reply', (pulse) => {
  // Handle response
});
```

### ❌ Don't: Emit without schema
```typescript
PulseBridge.emit('topic', { foo: 'bar' }); // Missing required fields!
```

### ✅ Do: Use full PulseObject
```typescript
PulseBridge.emit('topic', {
  source: 'component',
  target: 'destination',
  intent: 'update',
  payload: { foo: 'bar' },
  // ... other required fields
});
```

---

## Next Steps

1. **Phase 1:** Migrate Mirror components
2. **Phase 2:** Migrate Core components  
3. **Phase 3:** Connect visualizations
4. **Phase 4:** Remove old code
5. **Phase 5:** Test end-to-end
6. **Phase 6:** Deploy and monitor

**The future is Pulse.** 🚀
