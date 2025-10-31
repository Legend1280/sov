# Mirror Modular Design Specification (v1)

**Version:** 1.0  
**Date:** October 31, 2025  
**Status:** Design Specification  
**Author:** Brady Simmons  
**Copyright:** © 2025 Sovereignty Foundation. All rights reserved.

---

## Executive Summary

This document defines the architectural design for refactoring the Mirror UI framework from a hard-coded component system to a modular, schema-driven architecture. The refactor enables dynamic component composition, plug-and-play module integration with Core, and a clear separation between layout structure and component implementation.

The design maintains Mirror's existing static shell (Header, Navigator, Viewports, Surface Viewer) while enabling dynamic content loading through JSON schemas stored in Core as **MirrorLayout** ontology objects. Components become self-contained, discoverable modules that can be composed declaratively without modifying application code.

---

## Design Principles

### 1. Static Shell, Dynamic Content

Mirror retains its proven layout structure as a **static shell** while viewport contents become **dynamically loaded** based on schemas. This approach provides consistency and predictability while enabling flexibility and extensibility.

**Static Elements:**
- Overall layout structure (header, navigator, viewports, surface viewer)
- Panel visibility controls and resize handles
- View mode switching (full, split, left-only)
- Theme system and temporal mode controls

**Dynamic Elements:**
- Viewport component composition
- Module-specific navigator sources
- Surface viewer tab configuration
- Component data sources and event handlers

### 2. Schema-Driven Composition

Components are composed using **nested JSON schemas** that describe the component tree structure, similar to React's virtual DOM. Schemas are stored in Core as **MirrorLayout** ontology objects and cached locally for performance.

**Schema Structure:**
```json
{
  "type": "Container",
  "props": { "layout": "vertical", "gap": 4 },
  "children": [
    { 
      "type": "Timeline", 
      "props": { "dataSource": "/api/kronos/events" } 
    },
    { 
      "type": "Inspector", 
      "props": { "dataSource": "/api/sage/validate" } 
    }
  ]
}
```

### 3. Self-Contained Components

Components are **self-contained units** responsible for their own data fetching, state management, and error handling. This ensures reusability, testability, and clear boundaries.

**Component Responsibilities:**
- Fetch data from provided `dataSource` prop
- Manage internal loading and error states
- Emit events to the central event bus
- Subscribe to relevant event bus topics
- Render UI based on internal state

### 4. Module-Based Organization

Components are organized into **modules** representing distinct semantic contexts (e.g., SAGE, Kronos, Logos, Rita). Each module is a self-contained directory with its own components, schemas, and configuration.

**Module Structure:**
```
modules/
├── sage/
│   ├── components/
│   │   ├── GovernanceInspector.tsx
│   │   ├── CoherenceChart.tsx
│   │   └── TrustTimeline.tsx
│   ├── layouts/
│   │   └── sage_default.json
│   └── module.json
```

---

## Architecture Overview

### System Layers

The refactored Mirror architecture consists of four primary layers:

**Layer 1: Core Runtime**
- Component Registry (maps type strings to React components)
- Module Registry (manages module manifests and activation)
- Layout Manager (centralized layout state with Zustand)
- Event Bus (inter-component communication)
- Data Context (unified API access)

**Layer 2: Renderer**
- Dynamic component loader
- Schema parser and validator
- Props injection and template variable resolution
- Error boundary and fallback handling

**Layer 3: Components**
- UI primitives (buttons, cards, modals)
- Core components (shared across modules)
- Module-specific components (domain logic)
- Layout containers (grid, stack, tabs)

**Layer 4: Schemas**
- MirrorLayout ontology objects (stored in Core)
- Module manifests (component metadata)
- Default layouts (bundled with frontend)

### Data Flow

The complete rendering pipeline follows this sequence:

1. **Module Activation** → User selects module or system loads default
2. **Schema Loading** → `ModuleRegistry` fetches layout schema from Core or local cache
3. **Schema Parsing** → `Renderer` parses JSON and resolves component types
4. **Component Resolution** → `ComponentRegistry` maps type strings to React components
5. **Props Injection** → Template variables resolved, dataContext and eventBus injected
6. **Component Rendering** → React mounts component tree
7. **Data Fetching** → Components fetch data from their `dataSource` endpoints
8. **Event Handling** → Components emit/subscribe to event bus for communication

---

## Folder Structure

### Complete Directory Layout

```
mirror/
├── client/
│   ├── public/
│   ├── src/
│   │   ├── App.tsx                    # Root application
│   │   ├── main.tsx                   # Entry point
│   │   ├── index.css                  # Global styles
│   │   ├── components/
│   │   │   ├── ui/                    # Generic UI primitives (53 components)
│   │   │   │   ├── button.tsx
│   │   │   │   ├── card.tsx
│   │   │   │   └── ...
│   │   │   ├── core/                  # Shared Mirror components
│   │   │   │   ├── MirrorLayout.tsx   # Main layout shell
│   │   │   │   ├── Viewport.tsx       # Viewport container
│   │   │   │   ├── Renderer.tsx       # Dynamic component renderer
│   │   │   │   ├── ErrorBoundary.tsx  # Error handling
│   │   │   │   ├── ResizeHandle.tsx   # Panel resizing
│   │   │   │   └── UploadHandler.tsx  # File upload
│   │   │   └── layout/                # Layout containers
│   │   │       ├── Grid.tsx           # Grid layout
│   │   │       ├── Stack.tsx          # Vertical/horizontal stack
│   │   │       ├── Tabs.tsx           # Tab container
│   │   │       └── Split.tsx          # Split pane
│   │   ├── modules/                   # Module-specific components
│   │   │   ├── sage/
│   │   │   │   ├── components/
│   │   │   │   │   ├── GovernanceInspector.tsx
│   │   │   │   │   ├── CoherenceChart.tsx
│   │   │   │   │   └── TrustTimeline.tsx
│   │   │   │   ├── layouts/
│   │   │   │   │   └── sage_default.json
│   │   │   │   └── module.json
│   │   │   ├── kronos/
│   │   │   │   ├── components/
│   │   │   │   │   ├── TemporalTimeline.tsx
│   │   │   │   │   ├── DriftDetector.tsx
│   │   │   │   │   └── CausalGraph.tsx
│   │   │   │   ├── layouts/
│   │   │   │   │   └── kronos_default.json
│   │   │   │   └── module.json
│   │   │   ├── logos/
│   │   │   │   ├── components/
│   │   │   │   │   ├── IdentityCard.tsx
│   │   │   │   │   ├── BiometricAuth.tsx
│   │   │   │   │   └── RoleManager.tsx
│   │   │   │   ├── layouts/
│   │   │   │   │   └── logos_default.json
│   │   │   │   └── module.json
│   │   │   ├── rita/
│   │   │   │   ├── components/
│   │   │   │   │   ├── OntologyExplorer.tsx
│   │   │   │   │   ├── RelationGraph.tsx
│   │   │   │   │   └── SchemaValidator.tsx
│   │   │   │   ├── layouts/
│   │   │   │   │   └── rita_default.json
│   │   │   │   └── module.json
│   │   │   └── orion/
│   │   │       ├── components/
│   │   │       │   ├── CompressionMonitor.tsx
│   │   │       │   ├── RehydrationView.tsx
│   │   │       │   └── PerformanceChart.tsx
│   │   │       ├── layouts/
│   │   │       │   └── orion_default.json
│   │   │       └── module.json
│   │   ├── core/                      # Core runtime systems
│   │   │   ├── ComponentRegistry.ts   # Component type → React component mapping
│   │   │   ├── ModuleRegistry.ts      # Module manifest management
│   │   │   ├── LayoutManager.ts       # Layout state (Zustand)
│   │   │   ├── ViewportManager.tsx    # Viewport orchestration
│   │   │   ├── EventBus.ts            # Inter-component communication
│   │   │   ├── DataContext.tsx        # Unified API access
│   │   │   └── APIService.ts          # HTTP client wrapper
│   │   ├── contexts/
│   │   │   └── ThemeContext.tsx       # Theme provider
│   │   ├── themes/
│   │   │   ├── ThemeManager.ts        # Theme state management
│   │   │   ├── dark-mode.ts
│   │   │   ├── mirror-silver.ts
│   │   │   └── white-canvas.ts
│   │   ├── hooks/
│   │   │   ├── useDataSource.ts       # Data fetching hook
│   │   │   ├── useEventBus.ts         # Event bus hook
│   │   │   ├── useModule.ts           # Module activation hook
│   │   │   └── useComposition.ts      # Component composition hook
│   │   ├── pages/
│   │   │   ├── Home.tsx               # Main page
│   │   │   └── NotFound.tsx           # 404 page
│   │   └── types/
│   │       ├── schema.ts              # Layout schema types
│   │       ├── module.ts              # Module manifest types
│   │       └── component.ts           # Component prop types
│   ├── index.html
│   └── package.json
├── server/
│   └── index.ts                       # Express server (if needed)
├── docs/
│   └── architecture/
│       └── mirror_modular_design_v1.md
└── package.json
```

### Key Directory Purposes

**`/components/ui/`** - Generic UI primitives from shadcn/ui. These are atomic, reusable components with no business logic.

**`/components/core/`** - Shared Mirror framework components used across all modules. These handle layout, rendering, and core functionality.

**`/components/layout/`** - Layout container components that can be used in schemas to compose complex layouts (Grid, Stack, Tabs, Split).

**`/modules/{module_name}/`** - Module-specific components and layouts. Each module is a self-contained directory with its own namespace.

**`/core/`** - Core runtime systems including registries, managers, and services. These are the "engine" of the modular system.

**`/hooks/`** - Custom React hooks for common patterns like data fetching, event bus access, and module activation.

**`/types/`** - TypeScript type definitions for schemas, modules, and components.

---

## Schema Definition

### MirrorLayout Schema

The **MirrorLayout** schema is a nested JSON structure describing the component tree for a viewport. It follows a recursive pattern where each node can contain children.

**Schema Type Definition:**

```typescript
interface LayoutNode {
  type: string;                    // Component type (e.g., "Timeline", "Grid")
  props?: Record<string, any>;     // Component props
  children?: LayoutNode[];         // Child components (for containers)
}

interface ViewportLayout {
  viewport1: LayoutNode[];         // Components for viewport 1
  viewport2: LayoutNode[];         // Components for viewport 2
}

interface MirrorLayoutSchema {
  id: string;                      // Unique layout identifier
  name: string;                    // Human-readable name
  description?: string;            // Layout description
  module?: string;                 // Associated module ID
  viewports: ViewportLayout;       // Viewport component trees
  surfaceTabs?: string[];          // Surface viewer tab names
  navigatorSources?: NavigatorSource[];  // Navigator sidebar items
  metadata?: Record<string, any>;  // Additional metadata
}

interface NavigatorSource {
  id: string;                      // Unique source identifier
  label: string;                   // Display label
  icon?: string;                   // Icon name (lucide-react)
  badge?: string;                  // Badge text (e.g., "3 new")
  action?: string;                 // Event to emit on click
}
```

### Example Schemas

**Example 1: SAGE Governance View**

```json
{
  "id": "sage_governance_view",
  "name": "SAGE Governance Dashboard",
  "description": "Real-time governance monitoring and validation interface",
  "module": "sage",
  "viewports": {
    "viewport1": [
      {
        "type": "Grid",
        "props": { "columns": 2, "gap": 4 },
        "children": [
          {
            "type": "GovernanceInspector",
            "props": {
              "dataSource": "/api/sage/recent",
              "refreshInterval": 5000
            }
          },
          {
            "type": "CoherenceChart",
            "props": {
              "dataSource": "/api/sage/coherence/trend",
              "timeRange": "24h"
            }
          }
        ]
      }
    ],
    "viewport2": [
      {
        "type": "TrustTimeline",
        "props": {
          "objectId": "{{selectedObject.id}}",
          "dataSource": "/api/sage/trust/history"
        }
      }
    ]
  },
  "surfaceTabs": ["Governance", "Validation", "Audit"],
  "navigatorSources": [
    {
      "id": "pending_validations",
      "label": "Pending Validations",
      "icon": "AlertCircle",
      "badge": "{{pendingCount}}",
      "action": "showPendingValidations"
    },
    {
      "id": "recent_decisions",
      "label": "Recent Decisions",
      "icon": "CheckCircle",
      "action": "showRecentDecisions"
    }
  ]
}
```

**Example 2: Kronos Temporal View**

```json
{
  "id": "kronos_temporal_view",
  "name": "Kronos Temporal Intelligence",
  "description": "Multi-dimensional temporal tracking and drift detection",
  "module": "kronos",
  "viewports": {
    "viewport1": [
      {
        "type": "Stack",
        "props": { "direction": "vertical", "gap": 4 },
        "children": [
          {
            "type": "TemporalTimeline",
            "props": {
              "dataSource": "/api/kronos/events",
              "limit": 100,
              "showDrift": true
            }
          },
          {
            "type": "DriftDetector",
            "props": {
              "dataSource": "/api/kronos/drift",
              "threshold": 0.1
            }
          }
        ]
      }
    ],
    "viewport2": [
      {
        "type": "CausalGraph",
        "props": {
          "objectId": "{{selectedObject.id}}",
          "dataSource": "/api/kronos/causal",
          "depth": 3
        }
      }
    ]
  },
  "surfaceTabs": ["Timeline", "Drift", "Causal"],
  "navigatorSources": [
    {
      "id": "recent_events",
      "label": "Recent Events",
      "icon": "Clock",
      "action": "showRecentEvents"
    },
    {
      "id": "drift_alerts",
      "label": "Drift Alerts",
      "icon": "TrendingUp",
      "badge": "{{driftCount}}",
      "action": "showDriftAlerts"
    }
  ]
}
```

**Example 3: Nested Layout with Tabs**

```json
{
  "id": "financial_dashboard",
  "name": "Financial Dashboard",
  "module": "dexabooks",
  "viewports": {
    "viewport1": [
      {
        "type": "Tabs",
        "props": { "defaultTab": "overview" },
        "children": [
          {
            "type": "TabPanel",
            "props": { "id": "overview", "label": "Overview" },
            "children": [
              {
                "type": "FinancialSummary",
                "props": { "dataSource": "/api/financial/summary" }
              }
            ]
          },
          {
            "type": "TabPanel",
            "props": { "id": "transactions", "label": "Transactions" },
            "children": [
              {
                "type": "TransactionList",
                "props": { 
                  "dataSource": "/api/financial/transactions",
                  "limit": 50
                }
              }
            ]
          }
        ]
      }
    ],
    "viewport2": [
      {
        "type": "CashFlowTimeline",
        "props": { "dataSource": "/api/financial/cashflow" }
      }
    ]
  }
}
```

### Template Variables

Schemas support **template variables** for dynamic prop values that are resolved at render time:

**Supported Variables:**
- `{{selectedObject.id}}` - Currently selected object ID
- `{{selectedObject.type}}` - Currently selected object type
- `{{currentUser.id}}` - Current user ID
- `{{module.id}}` - Active module ID
- `{{pendingCount}}` - Dynamic count from state
- `{{driftCount}}` - Dynamic count from state

**Resolution Process:**
1. Renderer parses schema and identifies template variables
2. Variables are resolved from DataContext state
3. Resolved values are injected as component props
4. Components re-render when context values change

---

## Renderer Flow

### Component Resolution Pipeline

The **Renderer** component is responsible for parsing layout schemas and mounting the appropriate React components. It follows a multi-stage pipeline:

**Stage 1: Schema Loading**
- Fetch layout schema from ModuleRegistry
- Validate schema structure
- Cache schema for performance

**Stage 2: Component Resolution**
- Parse schema tree recursively
- Map component type strings to React components via ComponentRegistry
- Handle missing components with fallback UI

**Stage 3: Props Injection**
- Resolve template variables from DataContext
- Inject dataContext and eventBus into all components
- Merge schema props with injected props

**Stage 4: Rendering**
- Mount component tree with React
- Wrap each component in ErrorBoundary
- Apply Suspense for lazy-loaded components

**Stage 5: Lifecycle Management**
- Track mounted components
- Clean up subscriptions on unmount
- Handle hot module replacement

### Renderer Implementation

```typescript
// Renderer.tsx
import { ComponentRegistry } from '@/core/ComponentRegistry';
import { useDataContext } from '@/core/DataContext';
import { useEventBus } from '@/hooks/useEventBus';
import { LayoutNode } from '@/types/schema';
import { ErrorBoundary } from '@/components/core/ErrorBoundary';
import { Suspense } from 'react';

interface RendererProps {
  layout: LayoutNode[];
  fallback?: React.ReactNode;
}

export function Renderer({ layout, fallback }: RendererProps) {
  const dataContext = useDataContext();
  const eventBus = useEventBus();

  const renderNode = (node: LayoutNode, index: number): React.ReactNode => {
    // Resolve component from registry
    const Component = ComponentRegistry.get(node.type);
    
    if (!Component) {
      console.error(`Component type "${node.type}" not found in registry`);
      return (
        <div className="p-4 border border-destructive rounded-lg">
          <p className="text-destructive">Component "{node.type}" not found</p>
        </div>
      );
    }

    // Resolve template variables in props
    const resolvedProps = resolveTemplateVariables(node.props || {}, dataContext);

    // Inject dataContext and eventBus
    const injectedProps = {
      ...resolvedProps,
      dataContext,
      eventBus,
    };

    // Render children recursively
    const children = node.children?.map((child, i) => renderNode(child, i));

    return (
      <ErrorBoundary key={`${node.type}-${index}`}>
        <Suspense fallback={fallback || <div>Loading...</div>}>
          <Component {...injectedProps}>
            {children}
          </Component>
        </Suspense>
      </ErrorBoundary>
    );
  };

  return (
    <div className="renderer-container">
      {layout.map((node, index) => renderNode(node, index))}
    </div>
  );
}

function resolveTemplateVariables(
  props: Record<string, any>,
  context: any
): Record<string, any> {
  const resolved: Record<string, any> = {};

  for (const [key, value] of Object.entries(props)) {
    if (typeof value === 'string' && value.startsWith('{{') && value.endsWith('}}')) {
      const path = value.slice(2, -2).trim();
      resolved[key] = getNestedValue(context, path) || value;
    } else {
      resolved[key] = value;
    }
  }

  return resolved;
}

function getNestedValue(obj: any, path: string): any {
  return path.split('.').reduce((current, key) => current?.[key], obj);
}
```

### DataContext and EventBus Injection

All components receive two injected props:

**`dataContext`** - Provides access to:
- Core API client
- Current user information
- Selected object state
- Module state
- Global application state

**`eventBus`** - Provides methods for:
- `emit(event, payload)` - Emit event to all subscribers
- `on(event, handler)` - Subscribe to event
- `off(event, handler)` - Unsubscribe from event
- `once(event, handler)` - Subscribe to event once

**Example Component Using Injected Props:**

```typescript
interface TimelineProps {
  dataSource: string;
  dataContext: DataContext;
  eventBus: EventBus;
}

export function Timeline({ dataSource, dataContext, eventBus }: TimelineProps) {
  const [events, setEvents] = useState([]);

  useEffect(() => {
    // Fetch data using dataContext
    dataContext.api.get(dataSource).then(setEvents);

    // Subscribe to event bus
    const handleNewEvent = (event: any) => {
      setEvents(prev => [event, ...prev]);
    };
    eventBus.on('eventCreated', handleNewEvent);

    return () => {
      eventBus.off('eventCreated', handleNewEvent);
    };
  }, [dataSource, dataContext, eventBus]);

  const handleEventClick = (event: any) => {
    // Emit event to notify other components
    eventBus.emit('eventSelected', event);
  };

  return (
    <div>
      {events.map(event => (
        <div key={event.id} onClick={() => handleEventClick(event)}>
          {event.name}
        </div>
      ))}
    </div>
  );
}
```

---

## Module Activation Flow

### Module Registry Architecture

The **ModuleRegistry** manages module manifests and handles module activation. Each module is a semantic workspace with its own layout schema, components, and configuration.

**Module Manifest Structure:**

```typescript
interface ModuleManifest {
  id: string;                      // Unique module identifier
  name: string;                    // Human-readable name
  description?: string;            // Module description
  version: string;                 // Semantic version
  author?: string;                 // Module author
  icon?: string;                   // Icon name (lucide-react)
  defaultLayout: string;           // Default layout schema ID
  components: ComponentMetadata[]; // Component metadata
  dependencies?: string[];         // Required modules
  permissions?: string[];          // Required permissions
}

interface ComponentMetadata {
  type: string;                    // Component type identifier
  name: string;                    // Human-readable name
  description?: string;            // Component description
  category: string;                // Component category
  props: PropMetadata[];           // Prop definitions
  preview?: string;                // Preview image URL
}

interface PropMetadata {
  name: string;                    // Prop name
  type: string;                    // TypeScript type
  required: boolean;               // Is prop required
  default?: any;                   // Default value
  description?: string;            // Prop description
}
```

**Example Module Manifest:**

```json
{
  "id": "sage",
  "name": "SAGE Governance Engine",
  "description": "Semantic governance and validation system",
  "version": "1.0.0",
  "author": "Sovereignty Stack",
  "icon": "Shield",
  "defaultLayout": "sage_governance_view",
  "components": [
    {
      "type": "GovernanceInspector",
      "name": "Governance Inspector",
      "description": "Real-time governance validation display",
      "category": "governance",
      "props": [
        {
          "name": "dataSource",
          "type": "string",
          "required": true,
          "description": "API endpoint for governance data"
        },
        {
          "name": "refreshInterval",
          "type": "number",
          "required": false,
          "default": 5000,
          "description": "Auto-refresh interval in milliseconds"
        }
      ]
    }
  ],
  "dependencies": [],
  "permissions": ["read:governance", "read:sage"]
}
```

### Activation Sequence

The module activation sequence follows these steps:

1. **User Action** → User clicks module in navigator or system loads default module
2. **Module Lookup** → `ModuleRegistry.get(moduleId)` retrieves module manifest
3. **Permission Check** → Verify user has required permissions
4. **Dependency Resolution** → Load required dependency modules
5. **Component Registration** → Register module components in ComponentRegistry
6. **Layout Loading** → Fetch layout schema (Core API or local cache)
7. **State Update** → Update active module in ModuleRegistry
8. **Navigator Update** → Populate navigator with module-specific sources
9. **Viewport Rendering** → Renderer mounts components from layout schema
10. **Event Emission** → Emit `moduleActivated` event on event bus

**Activation Code Example:**

```typescript
// useModule.ts
export function useModule() {
  const moduleRegistry = useModuleRegistry();
  const componentRegistry = useComponentRegistry();
  const eventBus = useEventBus();

  const activateModule = async (moduleId: string) => {
    try {
      // 1. Get module manifest
      const manifest = moduleRegistry.get(moduleId);
      if (!manifest) {
        throw new Error(`Module "${moduleId}" not found`);
      }

      // 2. Check permissions
      const hasPermissions = await checkPermissions(manifest.permissions);
      if (!hasPermissions) {
        throw new Error(`Insufficient permissions for module "${moduleId}"`);
      }

      // 3. Load dependencies
      for (const depId of manifest.dependencies || []) {
        await activateModule(depId);
      }

      // 4. Register components
      for (const component of manifest.components) {
        const Component = await import(
          `@/modules/${moduleId}/components/${component.type}.tsx`
        );
        componentRegistry.register(component.type, Component.default);
      }

      // 5. Load layout schema
      const layout = await loadLayoutSchema(manifest.defaultLayout);

      // 6. Update active module
      moduleRegistry.setActive(moduleId);

      // 7. Emit event
      eventBus.emit('moduleActivated', { moduleId, manifest, layout });

      return { manifest, layout };
    } catch (error) {
      console.error(`Failed to activate module "${moduleId}":`, error);
      throw error;
    }
  };

  return { activateModule };
}
```

### Module Discovery

Modules are discovered through two mechanisms:

**1. Static Discovery** - Modules bundled with the frontend are discovered at build time by scanning the `/modules` directory.

**2. Dynamic Discovery** - Modules can be registered at runtime by fetching module manifests from the Core API at `/api/modules`.

**Discovery Implementation:**

```typescript
// ModuleRegistry.ts
class ModuleRegistry {
  private modules: Map<string, ModuleManifest> = new Map();
  private activeModuleId: string | null = null;

  async discoverModules() {
    // Discover static modules
    const staticModules = import.meta.glob('@/modules/*/module.json');
    for (const [path, loader] of Object.entries(staticModules)) {
      const manifest = await loader() as ModuleManifest;
      this.register(manifest);
    }

    // Discover dynamic modules from Core API
    try {
      const response = await fetch('/api/modules');
      const dynamicModules = await response.json();
      for (const manifest of dynamicModules) {
        this.register(manifest);
      }
    } catch (error) {
      console.warn('Failed to discover dynamic modules:', error);
    }
  }

  register(manifest: ModuleManifest) {
    this.modules.set(manifest.id, manifest);
    console.log(`[ModuleRegistry] Registered: ${manifest.name} (${manifest.id})`);
  }

  get(moduleId: string): ModuleManifest | undefined {
    return this.modules.get(moduleId);
  }

  setActive(moduleId: string) {
    if (!this.modules.has(moduleId)) {
      throw new Error(`Module "${moduleId}" not registered`);
    }
    this.activeModuleId = moduleId;
  }

  getActive(): ModuleManifest | null {
    return this.activeModuleId ? this.modules.get(this.activeModuleId) || null : null;
  }

  getAllModules(): ModuleManifest[] {
    return Array.from(this.modules.values());
  }
}
```

---

## Developer Workflow

### Adding a New Component (Manual Process)

The initial implementation uses a manual registration process. This ensures developers understand the system before automation is introduced.

**Step 1: Create Component File**

Create the component file in the appropriate module directory:

```bash
# Create component file
touch mirror/client/src/modules/sage/components/ValidationPanel.tsx
```

**Step 2: Implement Component**

Implement the component with proper TypeScript types:

```typescript
// ValidationPanel.tsx
import { useEffect, useState } from 'react';
import { Card } from '@/components/ui/card';
import { DataContext } from '@/core/DataContext';
import { EventBus } from '@/core/EventBus';

interface ValidationPanelProps {
  dataSource: string;
  dataContext: DataContext;
  eventBus: EventBus;
}

export default function ValidationPanel({
  dataSource,
  dataContext,
  eventBus
}: ValidationPanelProps) {
  const [validations, setValidations] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchValidations = async () => {
      try {
        const data = await dataContext.api.get(dataSource);
        setValidations(data);
      } catch (error) {
        console.error('Failed to fetch validations:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchValidations();

    // Subscribe to validation events
    const handleNewValidation = (validation: any) => {
      setValidations(prev => [validation, ...prev]);
    };
    eventBus.on('validationCreated', handleNewValidation);

    return () => {
      eventBus.off('validationCreated', handleNewValidation);
    };
  }, [dataSource, dataContext, eventBus]);

  if (loading) return <div>Loading validations...</div>;

  return (
    <Card className="p-4">
      <h2 className="text-lg font-semibold mb-4">Validations</h2>
      <div className="space-y-2">
        {validations.map((v: any) => (
          <div key={v.id} className="p-2 border rounded">
            {v.name}
          </div>
        ))}
      </div>
    </Card>
  );
}
```

**Step 3: Register Component**

Add the component to the ComponentRegistry:

```typescript
// ComponentRegistry.ts
import ValidationPanel from '@/modules/sage/components/ValidationPanel';

// In initialization code
componentRegistry.register('ValidationPanel', ValidationPanel);
```

**Step 4: Update Module Manifest**

Add component metadata to the module manifest:

```json
{
  "id": "sage",
  "components": [
    {
      "type": "ValidationPanel",
      "name": "Validation Panel",
      "description": "Displays recent SAGE validations",
      "category": "governance",
      "props": [
        {
          "name": "dataSource",
          "type": "string",
          "required": true,
          "description": "API endpoint for validation data"
        }
      ]
    }
  ]
}
```

**Step 5: Use in Layout Schema**

Add the component to a layout schema:

```json
{
  "viewports": {
    "viewport1": [
      {
        "type": "ValidationPanel",
        "props": {
          "dataSource": "/api/sage/validations"
        }
      }
    ]
  }
}
```

### Adding a New Module

**Step 1: Create Module Directory**

```bash
mkdir -p mirror/client/src/modules/new_module/components
mkdir -p mirror/client/src/modules/new_module/layouts
```

**Step 2: Create Module Manifest**

```json
{
  "id": "new_module",
  "name": "New Module",
  "description": "Description of the new module",
  "version": "1.0.0",
  "icon": "Box",
  "defaultLayout": "new_module_default",
  "components": [],
  "dependencies": [],
  "permissions": []
}
```

**Step 3: Create Default Layout**

```json
{
  "id": "new_module_default",
  "name": "New Module Default Layout",
  "module": "new_module",
  "viewports": {
    "viewport1": [],
    "viewport2": []
  }
}
```

**Step 4: Create Components**

Follow the component creation workflow above.

**Step 5: Register Module**

The module will be automatically discovered on application startup if the manifest is in the correct location.

### Future: CLI-Assisted Workflow

A future enhancement will introduce a CLI tool for automated scaffolding:

```bash
# Create new module
npx mirror create-module --name "New Module" --id new_module

# Create new component
npx mirror create-component ValidationPanel --module sage --category governance

# Register existing component
npx mirror register-component ValidationPanel --module sage
```

The CLI will:
- Generate boilerplate component files
- Update module manifests
- Register components in ComponentRegistry
- Create default layout schemas
- Generate TypeScript types

---

## Core API Integration

### Required Core Endpoints

The modular Mirror system requires the following Core API endpoints:

**Layout Management:**
- `GET /api/layouts` - List all available layouts
- `GET /api/layouts/:id` - Get specific layout schema
- `POST /api/layouts` - Create new layout (admin only)
- `PUT /api/layouts/:id` - Update layout (admin only)
- `DELETE /api/layouts/:id` - Delete layout (admin only)

**Module Management:**
- `GET /api/modules` - List all available modules
- `GET /api/modules/:id` - Get specific module manifest
- `POST /api/modules` - Register new module (admin only)

**Component Data:**
- Module-specific endpoints as defined in component `dataSource` props
- Example: `/api/sage/validations`, `/api/kronos/events`

### MirrorLayout Ontology Type

Layouts are stored in Core as a new ontology type: **MirrorLayout**

**Ontology Definition (YAML):**

```yaml
# mirror_layout.yaml
MirrorLayout:
  symbolic:
    - id: string (required)
    - name: string (required)
    - description: string (optional)
    - module: string (optional)
    - version: string (required)
  
  data:
    - viewports: object (required)
    - surfaceTabs: array (optional)
    - navigatorSources: array (optional)
    - metadata: object (optional)
  
  provenance:
    - created_by: string (required)
    - created_at: timestamp (required)
    - modified_by: string (optional)
    - modified_at: timestamp (optional)
```

**Storage in Core:**

Layouts are stored as objects in the `objects` table with `object_type = "MirrorLayout"`. The `data` field contains the complete layout schema as JSON.

**Example Storage:**

```python
# In Core API
layout_object = {
    "object_type": "MirrorLayout",
    "symbolic": {
        "id": "sage_governance_view",
        "name": "SAGE Governance Dashboard",
        "description": "Real-time governance monitoring",
        "module": "sage",
        "version": "1.0.0"
    },
    "data": {
        "viewports": {
            "viewport1": [...],
            "viewport2": [...]
        },
        "surfaceTabs": ["Governance", "Validation", "Audit"],
        "navigatorSources": [...]
    },
    "provenance": {
        "created_by": "system",
        "created_at": "2025-10-31T12:00:00Z"
    }
}

# Store via Reasoner
reasoner.ingest("MirrorLayout", layout_object, actor="system")
```

### Caching Strategy

To optimize performance, Mirror implements a multi-tier caching strategy:

**Tier 1: Build-Time Bundling**
- Default layouts bundled with frontend
- Fastest access, no network latency
- Used for core system layouts

**Tier 2: LocalStorage Cache**
- API-loaded layouts cached in browser
- Persists across sessions
- Invalidated on version change

**Tier 3: Memory Cache**
- Active layout kept in memory
- Instant access during session
- Cleared on module switch

**Cache Implementation:**

```typescript
// LayoutCache.ts
class LayoutCache {
  private memoryCache: Map<string, MirrorLayoutSchema> = new Map();
  
  async get(layoutId: string): Promise<MirrorLayoutSchema | null> {
    // Check memory cache
    if (this.memoryCache.has(layoutId)) {
      return this.memoryCache.get(layoutId)!;
    }
    
    // Check localStorage
    const cached = localStorage.getItem(`layout:${layoutId}`);
    if (cached) {
      const layout = JSON.parse(cached);
      this.memoryCache.set(layoutId, layout);
      return layout;
    }
    
    // Fetch from API
    try {
      const response = await fetch(`/api/layouts/${layoutId}`);
      const layout = await response.json();
      
      // Cache in both tiers
      this.memoryCache.set(layoutId, layout);
      localStorage.setItem(`layout:${layoutId}`, JSON.stringify(layout));
      
      return layout;
    } catch (error) {
      console.error(`Failed to load layout "${layoutId}":`, error);
      return null;
    }
  }
  
  invalidate(layoutId: string) {
    this.memoryCache.delete(layoutId);
    localStorage.removeItem(`layout:${layoutId}`);
  }
  
  clear() {
    this.memoryCache.clear();
    // Clear all layout keys from localStorage
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key?.startsWith('layout:')) {
        localStorage.removeItem(key);
      }
    }
  }
}
```

---

## Implementation Roadmap

### Phase 1: Core Infrastructure (Week 1)

**Deliverables:**
- ComponentRegistry implementation
- ModuleRegistry implementation
- Renderer component
- DataContext provider
- EventBus implementation
- Basic layout schema types

**Tasks:**
1. Implement ComponentRegistry with get/register/has methods
2. Implement ModuleRegistry with load/activate methods
3. Create Renderer component with recursive rendering
4. Implement DataContext with API client wrapper
5. Implement EventBus with emit/on/off methods
6. Define TypeScript types for schemas and modules

### Phase 2: Layout Containers (Week 1)

**Deliverables:**
- Grid layout component
- Stack layout component
- Tabs layout component
- Split layout component

**Tasks:**
1. Create Grid component with responsive columns
2. Create Stack component with vertical/horizontal modes
3. Create Tabs component with dynamic tab panels
4. Create Split component with resizable panes
5. Register all layout components in ComponentRegistry

### Phase 3: Module Migration (Week 2)

**Deliverables:**
- SAGE module with components and layouts
- Kronos module with components and layouts
- Module manifests for both modules

**Tasks:**
1. Create module directory structure
2. Migrate existing components to module structure
3. Create module manifests with component metadata
4. Create default layout schemas
5. Test module activation and rendering

### Phase 4: Core API Integration (Week 2)

**Deliverables:**
- MirrorLayout ontology type
- Layout management endpoints
- Module management endpoints

**Tasks:**
1. Define MirrorLayout ontology in YAML
2. Implement layout CRUD endpoints in Core API
3. Implement module listing endpoint
4. Test layout storage and retrieval
5. Implement caching in Mirror

### Phase 5: Testing and Polish (Week 3)

**Deliverables:**
- Unit tests for core systems
- Integration tests for rendering
- Documentation updates
- Performance optimization

**Tasks:**
1. Write tests for ComponentRegistry and ModuleRegistry
2. Write tests for Renderer with various schemas
3. Test module activation flow end-to-end
4. Optimize rendering performance
5. Update documentation with examples

### Phase 6: CLI Tooling (Week 4)

**Deliverables:**
- CLI tool for component scaffolding
- CLI tool for module creation
- Developer documentation

**Tasks:**
1. Implement `mirror create-module` command
2. Implement `mirror create-component` command
3. Implement `mirror register-component` command
4. Create templates for components and modules
5. Write developer guide for CLI usage

---

## Conclusion

This design specification provides a complete architectural blueprint for refactoring Mirror into a modular, schema-driven framework. The design maintains Mirror's proven layout structure while enabling dynamic component composition through JSON schemas stored in Core.

The modular architecture provides clear separation of concerns, self-contained components, and a plug-and-play system for extending Mirror with new modules. The schema-driven approach enables declarative UI composition without modifying application code, and the Core integration ensures all layouts are governed, versioned, and provenance-tracked.

The implementation roadmap provides a clear path forward with incremental deliverables and testable milestones. The system is designed to be implemented in phases, allowing for continuous testing and validation throughout the development process.

---

**Next Steps:**

1. Review and approve this design specification
2. Begin Phase 1 implementation (Core Infrastructure)
3. Create initial module structure for SAGE and Kronos
4. Implement Core API endpoints for layout management
5. Test end-to-end module activation and rendering

---

**Document Version:** 1.0  
**Last Updated:** October 31, 2025  
**Status:** Ready for Implementation
