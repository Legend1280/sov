# Mirror Modular Architecture: Implementation Guide

**Version:** 1.0  
**Date:** October 31, 2025  
**Author:** Brady Simmons  
**Copyright:** © 2025 Sovereignty Foundation. All rights reserved.

---

## 1. Introduction

This guide provides a comprehensive overview of the new modular architecture for the Mirror UI framework. It is intended for developers who will be building and maintaining applications and components within this new structure.

The new architecture is based on a **three-tier hierarchy**:

1.  **Mirror Framework:** The core runtime and shell.
2.  **App Layer:** Self-contained application contexts (e.g., DexaBooks, SAGE).
3.  **Component Layer:** Reusable, modular building blocks.

This separation of concerns allows for greater flexibility, scalability, and maintainability.

## 2. Getting Started

### 2.1. Folder Structure

The key directories in the new architecture are:

*   `/src/apps`: Contains the definitions for each application (app.json, header.json, navigator.json).
*   `/src/components/core`: Core framework components like `AppContainer` and `Renderer`.
*   `/src/components/layout`: Layout container components (Grid, Stack, Tabs, Split).
*   `/src/core`: Core runtime systems like `AppRegistry`, `ComponentRegistry`, `EventBus`, and `DataContext`.
*   `/src/modules`: Contains the domain-specific components for each module.
*   `/src/types`: TypeScript type definitions for schemas, modules, and components.

### 2.2. Core Concepts

*   **Apps:** An "App" is a complete user context that defines the navigation, header, and the default arrangement of viewports. Each app has a manifest (`app.json`) that defines its properties.
*   **Components:** Components are the modular building blocks of the UI. They are registered in the `ComponentRegistry` and can be dynamically rendered from a layout schema.
*   **Schemas:** Layouts are defined using nested JSON schemas. The root of a layout is an `AppContainer`, which loads sub-schemas for its header, navigator, and viewports.
*   **Registries:** The `AppRegistry` and `ComponentRegistry` are responsible for discovering and managing apps and components.
*   **DataContext:** A React context that provides all components with access to the Core API, application state, and the event bus.
*   **EventBus:** A centralized event system for inter-component communication.

## 3. Developer Workflow

### 3.1. Creating a New App

1.  **Create the App Directory:**

    ```bash
    mkdir -p /home/ubuntu/sov/mirror/client/src/apps/my-app
    ```

2.  **Create the App Manifest (`app.json`):**

    ```json
    {
      "id": "my-app",
      "name": "My App",
      "description": "A new application.",
      "icon": "Package",
      "defaultLayout": "my_app_container",
      "navigatorSchema": "my-app/navigator",
      "headerSchema": "my-app/header"
    }
    ```

3.  **Create the Header and Navigator Schemas:**

    Create `header.json` and `navigator.json` in the app directory to define the app's header and navigation.

4.  **Create the App Container Schema:**

    Create a schema for the `AppContainer` that references the header, navigator, and viewport schemas.

5.  **Register the App:**

    The `AppRegistry` will automatically discover and register the new app on startup.

### 3.2. Creating a New Component

1.  **Create the Component File:**

    Place the new component in the appropriate module directory (e.g., `/src/modules/my-module/components/MyComponent.tsx`).

2.  **Implement the Component:**

    Your component will receive `dataContext` and `eventBus` as props, which you can use to interact with the Core API and other components.

3.  **Register the Component:**

    Add the component to the `ComponentRegistry` in `/src/core/ComponentRegistry.ts`.

    ```typescript
    import MyComponent from "@/modules/my-module/components/MyComponent";

    // In initialization code
    componentRegistry.register("MyComponent", MyComponent);
    ```

4.  **Use the Component in a Schema:**

    You can now use the component in any layout schema.

    ```json
    {
      "type": "MyComponent",
      "props": { ... }
    }
    ```

## 4. Advanced Topics

### 4.1. Layout Containers

The framework provides several layout container components to help you create complex layouts:

*   **Grid:** Arranges children in a responsive grid.
*   **Stack:** Arranges children in a vertical or horizontal stack.
*   **Tabs:** Arranges children in a tabbed interface.
*   **Split:** Divides the space into two resizable panes.

### 4.2. State Management

Global application state is managed through the `DataContext`. You can access the state using the `useDataContext` hook.

```typescript
const { globalState, setGlobalState } = useDataContext();

// Set a value
setGlobalState("myKey", "myValue");

// Get a value
const myValue = globalState.myKey;
```

### 4.3. Event Handling

The `EventBus` allows for decoupled communication between components.

```typescript
const { eventBus } = useDataContext();

// Emit an event
eventBus.emit("myEvent", { payload: "data" });

// Subscribe to an event
eventBus.on("myEvent", (data) => {
  console.log(data.payload);
});
```

---

This guide provides a starting point for developing with the new Mirror modular architecture. For more detailed information, please refer to the `mirror_modular_design_v2.md` specification document.
