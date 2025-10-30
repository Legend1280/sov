# Mirror Framework v1.0 - Developer Documentation

## Overview

Mirror is a **universal viewport system** that dynamically loads and renders applications from JSON manifests. It provides a modular UI/UX skeleton where new applications can be added without rebuilding the framework.

**Architecture:**
```
Core API (Backend) → Mirror Framework (Frontend) → Module (JSON) → UI Rendered
```

## Core Concepts

### 1. **Modules**
Modules are applications defined by JSON configuration files. Each module specifies:
- **Viewports**: What visualizations to display
- **Data Sources**: Where to fetch data from
- **Navigator Sources**: Sidebar navigation items
- **Surface Tabs**: Right panel tabs (Ontology, Document, Provenance)

**Example Module** (`/modules/dexabooks/config.json`):
```json
{
  "id": "dexabooks",
  "name": "DexaBooks Financial Suite",
  "viewports": [
    {
      "id": "cash-flow-timeline",
      "type": "timeline",
      "title": "Cash Flow Timeline",
      "dataSource": "http://localhost:8002/api/transactions"
    }
  ],
  "surfaceTabs": ["Ontology", "Document", "Provenance"],
  "navigatorSources": [
    { "id": "dashboard", "label": "Dashboard", "badge": 10 }
  ]
}
```

### 2. **Component Registry**
Maps component type strings (from manifests) to React components.

**Location:** `/client/src/core/ComponentRegistry.ts`

**Usage:**
```typescript
import { componentRegistry } from '../core/ComponentRegistry';
import CashFlowTimeline from './components/CashFlowTimeline';

// Register component
componentRegistry.register('timeline', CashFlowTimeline);

// Get component
const Component = componentRegistry.get('timeline');
```

### 3. **Module Registry**
Loads and manages module manifests.

**Location:** `/client/src/core/ModuleRegistry.ts`

**Usage:**
```typescript
import { moduleRegistry } from '../core/ModuleRegistry';

// Load module from JSON
await moduleRegistry.load('dexabooks');

// Set active module
moduleRegistry.setActive('dexabooks');

// Get active module
const activeModule = moduleRegistry.getActive();
```

### 4. **Viewport Manager**
Dynamically renders viewports based on module configuration.

**Location:** `/client/src/core/ViewportManager.tsx`

**How it works:**
1. Receives viewport config from module manifest
2. Fetches data from `dataSource` URL
3. Looks up component type in ComponentRegistry
4. Renders component with fetched data

### 5. **Layout Manager**
Centralized state management for layout (panel sizes, focus mode, visibility).

**Location:** `/client/src/core/LayoutManager.ts`

**Features:**
- Navigator collapse/expand
- Surface Viewer hide/show
- Viewport focus mode (double-click)
- Panel resizing with drag handles
- View mode switching (Full, Split, Left Only)

### 6. **API Service**
Unified API handler for Core backend calls.

**Location:** `/client/src/core/APIService.ts`

**Features:**
- Centralized error handling
- Automatic response unwrapping
- Type-safe methods for common endpoints
- Generic `fetchData()` for module-defined endpoints

## Creating a New Module

### Step 1: Create Module Directory
```bash
mkdir -p /client/src/modules/mymodule/components
```

### Step 2: Create config.json
```json
{
  "id": "mymodule",
  "name": "My Module",
  "description": "Description of my module",
  "viewports": [
    {
      "id": "my-viewport",
      "type": "chart",
      "title": "My Chart",
      "dataSource": "http://localhost:8003/api/data"
    }
  ],
  "surfaceTabs": ["Ontology", "Document", "Provenance"],
  "navigatorSources": [
    { "id": "dashboard", "label": "Dashboard" }
  ]
}
```

### Step 3: Create Components
Create React components in `/modules/mymodule/components/`:

```typescript
// MyChart.tsx
interface MyChartProps {
  data?: any;
  title?: string;
}

export default function MyChart({ data, title }: MyChartProps) {
  // Component implementation
  return <div>{title}: {JSON.stringify(data)}</div>;
}
```

### Step 4: Register Components
Create `/modules/mymodule/register.ts`:

```typescript
import { componentRegistry } from '../../core/ComponentRegistry';
import MyChart from './components/MyChart';

export function registerMyModuleComponents() {
  componentRegistry.register('chart', MyChart);
  console.log('[MyModule] Components registered');
}

// Auto-register on import
registerMyModuleComponents();
```

### Step 5: Load Module in Home.tsx
```typescript
import '../modules/mymodule/register';

useEffect(() => {
  const loadModule = async () => {
    await moduleRegistry.load('mymodule');
    moduleRegistry.setActive('mymodule');
  };
  loadModule();
}, []);
```

## Component Requirements

All viewport components must accept these props:

```typescript
interface ViewportComponentProps {
  data?: any;        // Data from API
  title?: string;    // Viewport title
  // ... any custom props
}
```

**Data Flow:**
1. ViewportManager fetches data from `dataSource`
2. Data is passed as `data` prop to component
3. Component transforms and renders data

## Layout Structure

```
┌─────────────────────────────────────────────────────────┐
│ Header (View Modes | Logo | Temporal | Upload)         │
├──────┬─────────────────────────────┬────────────────────┤
│      │                             │                    │
│ Nav  │  Viewport 1 (Top)           │  Surface Viewer    │
│      │  (Resizable)                │  (Ontology/Doc/    │
│      ├─────────────────────────────┤   Provenance)      │
│      │  Viewport 2 (Bottom)        │                    │
│      │  (Resizable)                │                    │
└──────┴─────────────────────────────┴────────────────────┘
```

**Interactions:**
- **Navigator**: Click collapse button or double-click to hide
- **Surface Viewer**: Click Hide Details or double-click to hide
- **Viewports**: Double-click to enter focus mode (expand to full center area)
- **Resize**: Drag handles between panels to adjust sizes

## File Structure

```
/client/src/
├── core/                    # Framework core
│   ├── LayoutManager.ts     # Layout state management
│   ├── ModuleRegistry.ts    # Module loading
│   ├── ComponentRegistry.ts # Component mapping
│   ├── ViewportManager.tsx  # Dynamic viewport rendering
│   └── APIService.ts        # API calls
├── modules/                 # Application modules
│   ├── dexabooks/
│   │   ├── config.json      # Module manifest
│   │   ├── register.ts      # Component registration
│   │   └── components/      # Module components
│   └── mymodule/
│       ├── config.json
│       ├── register.ts
│       └── components/
├── components/              # Framework components
│   ├── MirrorLayout.tsx     # Main layout
│   ├── SurfaceViewer.tsx    # Right panel
│   └── ResizeHandle.tsx     # Drag handles
└── pages/
    └── Home.tsx             # Entry point
```

## API Response Patterns

Mirror's APIService automatically unwraps common response patterns:

**Wrapped Response:**
```json
{
  "transactions": [...],
  "count": 17
}
```
**Unwrapped to:** `[...]`

**Summary Response:**
```json
{
  "summary": {
    "total_income": 3500,
    "top_categories": [...]
  }
}
```
**Unwrapped to:** `{ total_income: 3500, top_categories: [...] }`

## Best Practices

1. **Module Isolation**: Each module should be self-contained with its own components
2. **Component Reusability**: Register generic components (charts, tables) for reuse across modules
3. **Data Transformation**: Transform API data in components, not in APIService
4. **Error Handling**: Components should handle loading and error states
5. **Responsive Design**: Components should adapt to viewport size changes
6. **Type Safety**: Use TypeScript interfaces for props and data structures

## Future Enhancements

- **Module Marketplace**: Load modules from external URLs
- **Component Library**: Shared visualization components
- **Theme System**: Customizable color schemes per module
- **Plugin System**: Extend framework with custom tools
- **State Persistence**: Save layout preferences
- **Multi-Module Views**: Display multiple modules simultaneously

## Troubleshooting

**Module not loading:**
- Check console for errors
- Verify config.json is valid JSON
- Ensure components are registered in register.ts

**Component not rendering:**
- Check if component type is registered in ComponentRegistry
- Verify dataSource URL is correct
- Check browser console for API errors

**Data not displaying:**
- Add console.log in component to inspect data structure
- Verify API response format matches component expectations
- Check APIService unwrapping logic

## Support

For questions or issues:
- Review this documentation
- Check browser console for errors
- Examine working DexaBooks module as reference
- Test API endpoints directly with curl

---

**Mirror Framework v1.0** - Built with React, TypeScript, D3.js, and Zustand
