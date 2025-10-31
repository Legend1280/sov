# Mirror Modular Design Specification (v2)

**Version:** 2.0  
**Date:** October 31, 2025  
**Status:** Design Specification  
**Author:** Brady Simmons  
**Copyright:** © 2025 Sovereignty Foundation. All rights reserved.

---

## Executive Summary

This document defines the architectural design for refactoring the Mirror UI framework into a modular, schema-driven architecture. This version (v2) introduces a **three-tier hierarchy** to provide a clear separation of concerns between the core framework, application containers, and modular components.

The new architecture consists of:
1.  **Mirror Framework:** The base runtime and shell.
2.  **App Layer:** First-tier containers that define a specific context (e.g., DexaBooks, SAGE), including navigation and header configuration.
3.  **Component Layer:** Modular, composable building blocks that populate the apps.

This design enables greater flexibility, allowing entire application contexts to be swapped dynamically while maintaining a stable core framework.

---

## Design Principles

### 1. Three-Tier Hierarchy

The architecture is structured into three distinct layers:

*   **Mirror Framework (Base Runtime):** The foundational layer that is always loaded. It provides the core shell (viewport grid, event bus, data context), rendering engine, and shared utilities.
*   **App Layer (First-Tier Container):** Each "App" defines a complete user context, including the Navigator, Header, and the default arrangement of viewports. Apps serve as entry points into functional domains.
*   **Component Layer (Modular Building Blocks):** These are the individual, governed components (e.g., buttons, charts, forms) that are composed within an App's viewports.

### 2. Schema-Driven Composition

Apps and components are composed using **nested JSON schemas**. The root of a layout is an `AppContainer`, which in turn loads schemas for its constituent parts (Header, Navigator, Viewports).

### 3. Self-Contained Components and Apps

Components and Apps are self-contained units, responsible for their own data, state, and logic. This ensures reusability, testability, and clear boundaries.

---

## Architecture Overview

### System Layers

The refactored Mirror architecture consists of four primary layers:

**Layer 1: Core Runtime**
- App Registry (manages App manifests)
- Component Registry (maps type strings to React components)
- Module Registry (manages module manifests and activation)
- Layout Manager (centralized layout state with Zustand)
- Event Bus (inter-component communication)
- Data Context (unified API access)

**Layer 2: Renderer**
- Dynamic component loader that recognizes `AppContainer` as a root node.
- Schema parser and validator.
- Props injection and template variable resolution.

**Layer 3: Components**
- `AppContainer`: The root component for an App.
- UI primitives (buttons, cards, modals).
- Core components (shared across modules).
- Module-specific components (domain logic).
- Layout containers (grid, stack, tabs).

**Layer 4: Schemas**
- `MirrorLayout` ontology objects in Core, with a new `AppContainer` type.
- Module manifests that define apps, components, and their relationships.

### Data Flow

1.  **App Activation** → User selects an App from the App Registry.
2.  **App Schema Loading** → The `AppContainer` schema is loaded from Core.
3.  **AppContainer Rendering** → The Renderer mounts the `AppContainer` component.
4.  **Sub-Schema Loading** → `AppContainer` loads the schemas for the Header, Navigator, and Viewports.
5.  **Component Rendering** → The Renderer recursively mounts the components for each sub-schema.

---

## Folder Structure

```
mirror/
├── client/
│   ├── src/
│   │   ├── components/
│   │   │   ├── core/
│   │   │   │   ├── AppContainer.tsx      # New App Container
│   │   │   │   ├── MirrorLayout.tsx
│   │   │   │   ├── Renderer.tsx
│   │   │   │   └── ...
│   │   ├── core/
│   │   │   ├── AppRegistry.ts          # New App Registry
│   │   │   ├── ComponentRegistry.ts
│   │   │   ├── ModuleRegistry.ts
│   │   │   └── ...
│   │   ├── apps/                      # New directory for App definitions
│   │   │   ├── dexabooks/
│   │   │   │   ├── app.json
│   │   │   │   ├── header.json
│   │   │   │   └── navigator.json
│   │   │   └── sage/
│   │   │       ├── app.json
│   │   │       ├── header.json
│   │   │       └── navigator.json
│   │   └── modules/                   # Existing modules with components
│   │       └── ...
└── ...
```

---

## Schema Definition

### AppContainer Schema

The `AppContainer` is the root of an application layout.

```json
{
  "id": "dexabooks_app_container",
  "type": "AppContainer",
  "props": {
    "appId": "dexabooks",
    "navigatorSchema": "dexabooks_nav",
    "headerSchema": "dexabooks_header",
    "viewports": [
      { "id": "viewport1", "schema": "dexabooks_main_view" }
    ]
  }
}
```

### Module Manifest Update

Module manifests will now declare the apps they provide.

```json
{
  "id": "dexabooks",
  "type": "app-provider",
  "name": "DexaBooks",
  "apps": [
    {
      "id": "dexabooks_app",
      "name": "DexaBooks",
      "icon": "BookOpen",
      "defaultLayout": "dexabooks_app_container"
    }
  ]
}
```

---

## Implementation Roadmap

### Phase 1: Core Infrastructure Update (Current)

*   **Implement `AppRegistry.ts`** to manage app manifests.
*   **Update `ModuleRegistry.ts`** to discover and register apps from modules.
*   **Implement `AppContainer.tsx`** to act as the root layout component.
*   **Update `Renderer.tsx`** to recognize and correctly render `AppContainer`.

### Phase 2: Schema and Module Migration

*   Create the new `/apps` directory structure.
*   Create example app schemas for `dexabooks` and `sage`.
*   Update module manifests to declare their provided apps.

### Phase 3: Integration and Testing

*   Update `App.tsx` to use the new `AppRegistry` to load a default app.
*   Test app switching and dynamic loading of headers, navigators, and viewports.

This updated design will be implemented in the current development cycle, building upon the existing modular foundation of the modular refactor.


---

## Appendix A: Developer Lifecycle Walkthrough

This appendix provides a technical narrative of the end-to-end lifecycle of loading and rendering an application in the Mirror v2 architecture. It is intended to give engineers a clear mental model of the system's execution flow.

### 1. Application Startup

1.  **`main.tsx`** - The application entry point renders the `App` component.
2.  **`App.tsx`** - The root `App` component mounts.
    *   A `useEffect` hook is triggered on the first render.
    *   `registerComponents()` is called, populating the `ComponentRegistry` with all core and layout components.
    *   `appRegistry.discoverApps()` is called. This function scans the `/src/apps` directory for `app.json` files and registers each one as an `AppManifest` in the `AppRegistry`.
3.  **`MirrorProvider`** - The `App` component is wrapped in the `MirrorProvider`, which sets up the `DataContext` and makes the `eventBus`, `appRegistry`, and `componentRegistry` available to all child components via the `useMirror` hook.

### 2. Home Page Render

1.  **`Home.tsx`** - The `Home` page component mounts.
2.  **`useMirror()`** - The component calls the `useMirror` hook to get access to the `appRegistry`.
3.  **App Loading** - A `useEffect` hook triggers the app loading sequence:
    *   It waits briefly to ensure app discovery is complete.
    *   It retrieves the `dexabooks` app manifest from the `appRegistry`.
    *   If the app is not yet registered, it attempts to load it dynamically via `appRegistry.load("dexabooks")`.
    *   It calls `appRegistry.setActive("dexabooks")`, which triggers the `onActivate` lifecycle hook for the DexaBooks app (if defined).
4.  **Layout Construction** - A new `LayoutNode` is created for the `AppContainer`:

    ```json
    {
      "type": "AppContainer",
      "props": {
        "appId": "dexabooks",
        "navigatorSchema": "dexabooks/navigator",
        "headerSchema": "dexabooks/header",
        "viewports": [
          { "id": "viewport1", "schema": "dexabooks/main" }
        ]
      }
    }
    ```

5.  **State Update** - The `appLayout` state is updated with this `LayoutNode`, triggering a re-render.

### 3. Dynamic Rendering

1.  **`Renderer.tsx`** - The `Home` page renders the `Renderer` component, passing the `appLayout` as a prop.
2.  **Component Resolution** - The `Renderer` looks up the component with the type `"AppContainer"` in the `ComponentRegistry`.
3.  **`AppContainer.tsx`** - The `AppContainer` component is mounted with the props from the layout schema.

### 4. App Container Execution

1.  **Schema Loading** - Inside the `AppContainer`, a `useEffect` hook begins loading the sub-schemas:
    *   It sets the active app ID in the `DataContext`.
    *   It dynamically imports `dexabooks/header.json` and `dexabooks/navigator.json`.
    *   It dynamically imports the viewport schema `dexabooks/main.json`.
2.  **Recursive Rendering** - Once the schemas are loaded, the `AppContainer` renders its own content, which includes:
    *   A `<header>` element containing a `Renderer` for the header layout.
    *   An `<aside>` element containing a `Renderer` for the navigator layout.
    *   A `<main>` element containing a `Renderer` for each viewport layout.
3.  **Component Tree Mount** - The `Renderer` recursively walks through each of these sub-schemas, resolving component types from the `ComponentRegistry` and mounting the corresponding React components. This process continues until the entire component tree is rendered.

### 5. User Interaction

1.  **Event Emission** - A user clicks a button in the UI (e.g., a `NavigatorItem`).
2.  **Event Handler** - The `onClick` handler in the component is triggered.
3.  **Event Bus** - The handler calls `eventBus.emit("navigatorItemClicked", { ... })`.
4.  **Event Subscription** - Other components that are subscribed to this event (e.g., a viewport manager or a data-fetching component) will receive the event and its payload, allowing them to update their state and re-render accordingly.

This entire lifecycle, from startup to interaction, is designed to be declarative, decoupled, and highly extensible. Developers can add new apps, components, and schemas without modifying the core framework, ensuring a scalable and maintainable codebase.
