# Semantic Instantiation — Declarative Object Rendering

**Version:** 1.0  
**Date:** 2025-11-01  
**Status:** Operational

---

## Overview

**Semantic Instantiation** is the holy grail of the Sovereignty Stack — the ability to "speak" ontological objects into visual existence through declarative schemas. Instead of coding UI components, you **instantiate identity, governance, and functionality** as first-class semantic objects.

This document describes the complete architecture for transforming ontology definitions into rendered UI components with full lifecycle tracking and governance.

---

## The Philosophical Shift

### Traditional Approach
```tsx
// Hardcoded component
<LoginButton onClick={handleLogin} />
```

You're coding a button.

### Semantic Instantiation
```tsx
// Ontological object
<ObjectRenderer object="logos" />
```

You're **manifesting identity** as a governed semantic object.

---

## Architecture

### Flow Diagram

```
User Intent
    ↓
Schema Definition (JSON)
    ↓
SchemaLoader (fetch from Core)
    ↓
ObjectRenderer (resolve object ID)
    ↓
Fetch Ontology Object (logos.yaml)
    ↓
Resolve ui_binding (LogosLoginButton)
    ↓
Dynamic Import (component)
    ↓
Lifecycle Events (loading → rendered)
    ↓
Render Component (with ontology context)
    ↓
Pulse Communication (logos.authenticate)
    ↓
SAGE Validation + Kronos Indexing + Shadow Logging
```

### Components

#### 1. Ontology Object Definition (`logos.yaml`)

Defines Logos as a first-class object:

```yaml
object:
  id: "logos"
  type: "SystemComponent"
  layer: "Identity"
  
  metadata:
    title: "Logos — Authentication Layer"
    description: "Authenticates narrative coherence between user and system"
    role: "Identity anchor and coherence verifier"
  
  ui_binding:
    component: "LogosLoginButton"
    path: "components/LogosLoginButton"
    framework: "react-native"
  
  pulse_channel: "mirror↔core.identity"
  
  schema:
    intent: "authenticate"
    method: "narrative"
    visual:
      type: "button"
      label: "Log In with Logos"
      color: "#00A3FF"
  
  events:
    - name: "logos.authenticate"
      description: "User initiated authentication"
    - name: "logos.authenticated"
      description: "Authentication successful"
  
  governance:
    sage_validation: true
    kronos_indexing: true
    shadow_logging: true
    constitutional_alignment: true
```

**Key Sections:**
- `ui_binding` — Maps ontology to React component
- `pulse_channel` — Communication channel for events
- `schema.visual` — Visual properties for rendering
- `events` — Pulse events emitted/received
- `governance` — Integration with SAGE/Kronos/Shadow

#### 2. ObjectRenderer Component

The semantic bridge that resolves ontology → component:

```tsx
<ObjectRenderer 
  object="logos" 
  props={{ mode: "login" }}
  onLoad={(obj) => console.log('Loaded:', obj)}
  onError={(err) => console.error('Error:', err)}
/>
```

**Responsibilities:**
1. Fetch ontology object definition from Core
2. Resolve `ui_binding` to component path
3. Dynamically import component
4. Emit lifecycle Pulses
5. Pass ontology context to component
6. Handle errors and loading states

**Lifecycle Events Emitted:**
- `mirror.object.loading` — Fetching ontology
- `mirror.object.loaded` — Ontology fetched
- `mirror.object.rendering` — Component instantiating
- `mirror.object.rendered` — Component rendered
- `mirror.object.unmounted` — Component removed
- `mirror.object.error` — Error occurred

#### 3. LogosLoginButton Component

The visual manifestation of the Logos ontology:

```tsx
export default function LogosLoginButton({
  mode = 'login',
  ontology,
  pulseBridge = PulseBridge,
  onAuthenticated,
  onError
}: LogosLoginButtonProps) {
  const [authState, setAuthState] = useState<AuthState>('idle');

  const handleAuthenticate = () => {
    setAuthState('authenticating');
    
    pulseBridge.emit('logos.authenticate', {
      source: 'mirror',
      target: 'core',
      intent: 'authenticate',
      payload: { method: 'narrative' }
    });
  };

  // Listen for authentication response
  useEffect(() => {
    const unsub = pulseBridge.on('logos.authenticated', (pulse) => {
      setAuthState('authenticated');
      onAuthenticated?.(pulse.payload);
    });
    
    return unsub;
  }, []);

  return (
    <TouchableOpacity onPress={handleAuthenticate}>
      <Text>{getLabel()}</Text>
    </TouchableOpacity>
  );
}
```

**Key Features:**
- Receives ontology context from ObjectRenderer
- 100% Pulse-native communication
- 4 visual states (idle, authenticating, authenticated, error)
- No direct API calls
- Governed by SAGE, indexed by Kronos, logged by Shadow

#### 4. SchemaLoader

Fetches layout schemas that define object arrangements:

```typescript
const schema = await SchemaLoader.load('home');

// Returns:
{
  "type": "Viewport",
  "id": "home",
  "children": [
    {
      "type": "Logos",
      "props": { "mode": "login" }
    },
    {
      "type": "SystemStatus",
      "props": { "showNodes": true }
    }
  ]
}
```

**Features:**
- Fetches schemas from Core
- 1-hour cache TTL
- Prevents duplicate fetches
- Emits schema.request and schema.loaded Pulses
- Supports preloading

#### 5. ObjectLifecycle

Tracks and emits lifecycle events for all objects:

```typescript
import { ObjectLifecycle, emitRendered } from '@/lib/ObjectLifecycle';

// Emit lifecycle event
emitRendered('logos', 'LogosLoginButton', {
  viewport: 'home',
  user_id: 'user123'
});

// Subscribe to events
ObjectLifecycle.on('rendered', (event) => {
  console.log(`${event.object_id} rendered at ${event.timestamp}`);
});

// Get statistics
const stats = ObjectLifecycle.getStats();
// {
//   activeObjects: 3,
//   totalEvents: 12,
//   phaseDistribution: { loading: 3, loaded: 3, rendered: 3 }
// }
```

**Lifecycle Phases:**
1. `loading` — Object definition being fetched
2. `loaded` — Object definition fetched successfully
3. `rendering` — Component being instantiated
4. `rendered` — Component rendered in viewport
5. `interacted` — User interacted with object
6. `updated` — Object state changed
7. `unmounting` — Component being removed
8. `unmounted` — Component removed from viewport
9. `error` — Error occurred during lifecycle

---

## Usage Examples

### Example 1: Render Logos

```tsx
import ObjectRenderer from '@/components/ObjectRenderer';

export default function LoginScreen() {
  return (
    <View>
      <ObjectRenderer object="logos" props={{ mode: 'login' }} />
    </View>
  );
}
```

**What Happens:**
1. ObjectRenderer fetches logos.yaml from Core
2. Resolves ui_binding to LogosLoginButton
3. Emits lifecycle Pulses (loading → rendered)
4. Dynamically imports and renders LogosLoginButton
5. Component receives ontology context and PulseBridge
6. User clicks button → emits logos.authenticate Pulse
7. Core responds with logos.authenticated Pulse
8. Component updates to authenticated state

### Example 2: Schema-Driven Layout

```tsx
import { SchemaLoader } from '@/lib/SchemaLoader';
import ObjectRenderer from '@/components/ObjectRenderer';

export default function DynamicViewport({ schemaId }: { schemaId: string }) {
  const [schema, setSchema] = useState(null);

  useEffect(() => {
    SchemaLoader.load(schemaId).then(setSchema);
  }, [schemaId]);

  if (!schema) return <Loading />;

  return (
    <View>
      {schema.children.map((child, index) => (
        <ObjectRenderer 
          key={index}
          object={child.type.toLowerCase()}
          props={child.props}
        />
      ))}
    </View>
  );
}
```

**Usage:**
```tsx
<DynamicViewport schemaId="home" />
```

This renders all objects defined in the "home" schema.

### Example 3: Lifecycle Monitoring

```tsx
import { ObjectLifecycle } from '@/lib/ObjectLifecycle';

export default function LifecycleMonitor() {
  const [events, setEvents] = useState([]);

  useEffect(() => {
    const unsub = ObjectLifecycle.on('rendered', (event) => {
      setEvents(prev => [...prev, event]);
    });
    
    return unsub;
  }, []);

  return (
    <View>
      {events.map((event, i) => (
        <Text key={i}>
          {event.object_id} rendered at {event.timestamp}
        </Text>
      ))}
    </View>
  );
}
```

---

## Implementation Status

### ✅ Phase 1: Ontology Definition
- Created `logos.yaml` with complete object definition
- Defined ui_binding, events, governance, lifecycle
- 17 sections covering all aspects of Logos

### ✅ Phase 2: ObjectRenderer
- Built dynamic ontology-to-UI resolver
- Fetches objects from Core by ID
- Resolves ui_binding to component path
- Dynamically imports components
- Emits lifecycle Pulses

### ✅ Phase 3: LogosLoginButton
- Created Pulse-integrated UI component
- 4 visual states with animations
- 100% Pulse-native communication
- Receives ontology context from ObjectRenderer
- No direct API calls

### ✅ Phase 4: SchemaLoader
- Implemented layout schema fetcher
- 1-hour cache with TTL
- Prevents duplicate fetches
- Emits schema Pulses
- Mock schemas for home, dashboard, login

### ✅ Phase 5: ObjectLifecycle
- Built Pulse-driven lifecycle system
- 9 lifecycle phases tracked
- Local and remote event emission
- History tracking per object
- Statistics and monitoring

### ✅ Phase 6: Testing & Documentation
- Created SemanticInstantiationDemo page
- Live demonstration with lifecycle tracking
- Complete documentation
- Usage examples and API reference

---

## Files Created

### Core Ontology
- `/core/ontology/logos.yaml` — Logos object definition

### Mirror Components
- `/apps/mirror/app/components/ObjectRenderer.tsx` — Dynamic resolver
- `/apps/mirror/app/components/LogosLoginButton.tsx` — Logos UI component

### Mirror Libraries
- `/apps/mirror/app/lib/SchemaLoader.ts` — Layout schema fetcher
- `/apps/mirror/app/lib/ObjectLifecycle.ts` — Lifecycle event system

### Examples & Documentation
- `/apps/mirror/app/examples/SemanticInstantiationDemo.tsx` — Live demo
- `/docs/SEMANTIC_INSTANTIATION.md` — This document

**Total: 7 files**

---

## Key Achievements

### 1. Declarative Semantic Instantiation

You can now **speak objects into existence**:

```tsx
<ObjectRenderer object="logos" />
```

This is not a component — it's a **semantic invocation** of the Logos identity anchor.

### 2. Ontology-Driven UI

All UI elements are defined as **first-class ontological objects**:
- Queryable via Core
- Governed by SAGE
- Indexed by Kronos
- Logged by Shadow
- Versioned and immutable

### 3. Complete Lifecycle Tracking

Every object instantiation creates a **governed event trail**:
- Loading → Loaded → Rendering → Rendered → Unmounted
- All events emitted as Pulses
- Full provenance in Shadow Ledger
- Temporal decay in Kronos

### 4. Zero Direct API Calls

Components communicate **entirely through Pulses**:
- No REST endpoints
- No direct function calls
- Pure semantic event communication
- Constitutional alignment enforced

### 5. Dynamic Component Resolution

Components are **resolved at runtime**:
- Fetched from Core ontology
- Dynamically imported
- Passed ontology context
- Governed by constitution

---

## Future Work

### Amendment System
- Implement ontology amendment proposals
- Version migration for objects
- Backward compatibility for legacy schemas

### Component Registry
- Centralized component registration
- Dynamic imports from Core
- Hot reloading for development

### Visual Schema Editor
- Drag-and-drop schema builder
- Real-time preview
- Schema validation and linting

### Advanced Lifecycle
- Performance metrics per object
- Error recovery and retry logic
- Lifecycle hooks for custom behavior

### Multi-Framework Support
- Web (React)
- Desktop (Electron)
- Mobile (React Native)

---

## API Reference

### ObjectRenderer

```tsx
<ObjectRenderer
  object="logos"              // Object ID from Core
  props={{ mode: "login" }}   // Props to pass to component
  onLoad={(obj) => {}}        // Called when ontology loaded
  onError={(err) => {}}       // Called on error
/>
```

### SchemaLoader

```typescript
// Load schema
const schema = await SchemaLoader.load('home');

// Force refresh
const schema = await SchemaLoader.load('home', true);

// Clear cache
SchemaLoader.clearCache('home');  // Specific schema
SchemaLoader.clearCache();        // All schemas

// Preload schemas
await SchemaLoader.preload(['home', 'dashboard', 'login']);

// Get statistics
const stats = SchemaLoader.getCacheStats();
```

### ObjectLifecycle

```typescript
// Emit lifecycle event
emitRendered('logos', 'LogosLoginButton', { viewport: 'home' });

// Subscribe to events
const unsub = ObjectLifecycle.on('rendered', (event) => {
  console.log(event);
});

// Get history
const history = ObjectLifecycle.getHistory('logos');

// Get current phase
const phase = ObjectLifecycle.getCurrentPhase('logos');

// Get statistics
const stats = ObjectLifecycle.getStats();
```

---

## References

- [Logos Ontology](../core/ontology/logos.yaml)
- [PulseMesh Architecture](./PULSEMESH_ARCHITECTURE_v1.0.md)
- [Sovereignty Constitution](./SOVEREIGNTY_CONSTITUTION.md)
- [Pulse Migration Guide](./PULSE_MIGRATION_GUIDE.md)

---

**Copyright © 2025 Sovereignty Foundation. All rights reserved.**
