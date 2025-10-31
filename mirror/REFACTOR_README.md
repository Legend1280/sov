# Mirror Modular Refactor: Complete Code Bundle

**Version:** 2.0  
**Date:** October 31, 2025  
**Status:** Ready for Integration  
**Author:** Brady Simmons  
**Copyright:** © 2025 Sovereignty Foundation. All rights reserved.

---

## Overview

This refactor introduces a **three-tier architecture** to the Mirror UI framework:

1.  **Mirror Framework** - The core runtime and shell
2.  **App Layer** - Self-contained application contexts
3.  **Component Layer** - Modular, reusable building blocks

This architecture enables dynamic component composition, plug-and-play module integration with Core, and a clear separation between layout structure and component implementation.

---

## What's Included

This code bundle contains the following new and updated files:

### Core Infrastructure

*   **`/src/core/EventBus.ts`** - Central event communication system
*   **`/src/core/DataContext.tsx`** - Unified API access and application state provider
*   **`/src/core/APIService.ts`** - Updated HTTP client wrapper (enhanced)
*   **`/src/core/AppRegistry.ts`** - Application manifest management
*   **`/src/core/ComponentRegistry.ts`** - Existing component registry (unchanged)
*   **`/src/core/ModuleRegistry.ts`** - Existing module registry (unchanged)

### Core Components

*   **`/src/components/core/AppContainer.tsx`** - Root component for an application
*   **`/src/components/core/Renderer.tsx`** - Dynamic component renderer

### Layout Containers

*   **`/src/components/layout/Grid.tsx`** - Grid layout container
*   **`/src/components/layout/Stack.tsx`** - Vertical/horizontal stack layout
*   **`/src/components/layout/Tabs.tsx`** - Tab container layout
*   **`/src/components/layout/Split.tsx`** - Split pane layout

### Type Definitions

*   **`/src/types/schema.ts`** - TypeScript types for layout schemas

### Example Apps

*   **`/src/apps/dexabooks/app.json`** - DexaBooks app manifest
*   **`/src/apps/dexabooks/header.json`** - DexaBooks header schema
*   **`/src/apps/dexabooks/navigator.json`** - DexaBooks navigator schema
*   **`/src/apps/sage/app.json`** - SAGE app manifest
*   **`/src/apps/sage/header.json`** - SAGE header schema
*   **`/src/apps/sage/navigator.json`** - SAGE navigator schema

### Documentation

*   **`/docs/architecture/mirror_modular_design_v2.md`** - Updated architectural design specification
*   **`/docs/guides/implementation_guide.md`** - Developer implementation guide

---

## Integration Steps

### Step 1: Copy Files

Copy all the new files from this bundle into your Mirror project, preserving the directory structure.

### Step 2: Update Component Registry

Update `/src/core/ComponentRegistry.ts` to register the new layout container components:

```typescript
import { componentRegistry } from '@/core/ComponentRegistry';
import Grid from '@/components/layout/Grid';
import Stack from '@/components/layout/Stack';
import Tabs, { TabPanel } from '@/components/layout/Tabs';
import Split from '@/components/layout/Split';
import AppContainer from '@/components/core/AppContainer';

// Register layout containers
componentRegistry.register('Grid', Grid);
componentRegistry.register('Stack', Stack);
componentRegistry.register('Tabs', Tabs);
componentRegistry.register('TabPanel', TabPanel);
componentRegistry.register('Split', Split);

// Register AppContainer
componentRegistry.register('AppContainer', AppContainer);
```

### Step 3: Update App.tsx

Update `/src/App.tsx` to use the new `DataContextProvider` and `AppRegistry`:

```typescript
import { DataContextProvider } from './core/DataContext';
import { appRegistry } from './core/AppRegistry';
import { useEffect } from 'react';

function App() {
  useEffect(() => {
    // Discover and register apps on startup
    appRegistry.discoverApps();
  }, []);

  return (
    <ErrorBoundary>
      <ThemeProvider defaultTheme="light">
        <DataContextProvider>
          <TooltipProvider>
            <Toaster />
            <Router />
          </TooltipProvider>
        </DataContextProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
}
```

### Step 4: Update Home.tsx

Update `/src/pages/Home.tsx` to load an app using the `AppContainer`:

```typescript
import { useEffect, useState } from 'react';
import { appRegistry } from '@/core/AppRegistry';
import Renderer from '@/components/core/Renderer';

export default function Home() {
  const [appLayout, setAppLayout] = useState(null);

  useEffect(() => {
    const loadApp = async () => {
      // Load the default app (DexaBooks)
      const app = await appRegistry.load('dexabooks');
      appRegistry.setActive('dexabooks');
      
      // Create AppContainer schema
      const layout = {
        type: 'AppContainer',
        props: {
          appId: app.id,
          navigatorSchema: app.navigatorSchema,
          headerSchema: app.headerSchema,
          viewports: [
            { id: 'viewport1', schema: 'dexabooks/main' }
          ]
        }
      };
      
      setAppLayout(layout);
    };

    loadApp();
  }, []);

  if (!appLayout) {
    return <div>Loading...</div>;
  }

  return <Renderer layout={appLayout} />;
}
```

### Step 5: Create Placeholder Components

You will need to create placeholder components for the components referenced in the app schemas (e.g., `Text`, `Button`, `Badge`, `NavigatorSection`, `NavigatorItem`). These can be simple wrappers around your existing UI components.

Example placeholder for `Text`:

```typescript
// /src/components/core/Text.tsx
interface TextProps {
  text: string;
  className?: string;
  dataContext?: any;
  eventBus?: any;
}

export function Text({ text, className }: TextProps) {
  return <span className={className}>{text}</span>;
}

export default Text;
```

Register these components in the `ComponentRegistry`.

### Step 6: Test the Integration

1.  Start the development server: `pnpm dev`
2.  Navigate to the home page
3.  Verify that the DexaBooks app loads with its header and navigator
4.  Test app switching (if you implement a UI for it)

---

## Next Steps

### Implement Missing Components

The example app schemas reference several components that need to be implemented:

*   `Text` - Simple text display
*   `Button` - Button component (may already exist in `/src/components/ui`)
*   `Badge` - Badge component (may already exist in `/src/components/ui`)
*   `NavigatorSection` - Navigator section header
*   `NavigatorItem` - Navigator item button

### Create Viewport Layouts

Create layout schemas for the main viewport content of each app (e.g., `dexabooks/main.json`, `sage/main.json`).

### Integrate with Core API

Update the `loadSchema` function in `AppContainer.tsx` to fetch schemas from the Core API when they are not found locally.

### Add App Switching UI

Implement a UI element (e.g., in the header or navigator) that allows users to switch between different apps.

---

## Troubleshooting

### Component Not Found Error

If you see an error like "Component 'X' not found in registry", make sure the component is:

1.  Implemented in the correct directory
2.  Registered in the `ComponentRegistry`
3.  Exported correctly from its file

### Schema Not Found Error

If you see an error like "Schema 'X' not found", make sure:

1.  The schema file exists in the `/src/apps` directory
2.  The file name matches the schema ID referenced in the app manifest
3.  The JSON is valid

### DataContext Error

If you see an error like "useDataContext must be used within DataContextProvider", make sure:

1.  The `DataContextProvider` is wrapping your app in `App.tsx`
2.  You are using the `useDataContext` hook inside a component that is a child of the provider

---

## Support

For questions or issues, please refer to:

*   **Architecture Specification:** `/docs/architecture/mirror_modular_design_v2.md`
*   **Implementation Guide:** `/docs/guides/implementation_guide.md`

---

**End of README**
