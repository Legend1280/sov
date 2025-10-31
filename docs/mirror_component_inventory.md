# Mirror Component Inventory & Extraction Plan

**Author:** Brady Simmons  
**Copyright:** © 2025 Sovereignty Foundation. All rights reserved.

---

## Overview

This document inventories all components from the old Mirror interface and maps them to the new modular schema-driven architecture.

---

## Component Categories

### 1. **Layout Components** (Already Built in v2)
- ✅ Grid
- ✅ Stack
- ✅ Tabs
- ✅ Split

### 2. **Core Mirror Components** (Need to Extract & Rebuild)

#### MirrorLayout (Main Container)
**Current State:** Hardcoded monolithic component  
**New Approach:** Break into modular schema-driven components

**Sub-components to extract:**
1. **Header**
   - Logo/Title
   - View Mode Controls (Full, Split, Left-Only)
   - Temporal Controls (Past, Present, Future)
   - Upload Handler
   
2. **Navigator** (Left Sidebar)
   - Section Headers (THEMES, FINANCIAL)
   - Theme Switcher List
   - Navigation Items with Badges
   - Collapse/Expand Toggle
   
3. **Viewports** (Center Content)
   - Viewport Container
   - Viewport Labels
   - Focus Mode Toggle
   - Resize Handles
   
4. **Surface Viewer** (Right Sidebar)
   - Tabbed Interface
   - Object Details Display
   - Close Button

#### Specialized Components
1. **SurfaceViewer**
   - Tab navigation
   - Object detail views
   - Document view
   - Provenance trail

2. **ResizeHandle**
   - Vertical resize
   - Horizontal resize
   - Drag interaction

3. **UploadHandler**
   - File upload button
   - Upload progress
   - Success/error handling

4. **Viewport**
   - Content container
   - Placeholder states

5. **ViewportPlaceholder**
   - Empty state messaging
   - Instructions

### 3. **Domain Components** (Custom Built)

#### Financial/Analytics
1. **CashFlowTimeline**
   - Timeline visualization
   - Data display

2. **ExpenseBreakdown**
   - Expense categorization
   - Chart/graph display

### 4. **UI Primitives** (shadcn/ui - Keep As Is)
Already available in `/components/ui/`:
- accordion, alert-dialog, alert, avatar, badge
- breadcrumb, button, button-group, calendar, card
- carousel, chart, checkbox, collapsible, command
- context-menu, dialog, drawer, dropdown-menu
- empty, field, form, hover-card, input, input-group
- input-otp, item, kbd, label, menubar, navigation-menu
- pagination, popover, progress, radio-group, resizable
- scroll-area, select, separator, sheet, sidebar
- skeleton, slider, sonner, spinner, switch, table
- tabs, textarea, toggle, toggle-group, tooltip

### 5. **Utility Components**
1. **ErrorBoundary** - Already exists
2. **ManusDialog** - Custom dialog wrapper

---

## Extraction Strategy

### Phase 1: Core Layout Components
Extract from MirrorLayout:
1. **MirrorHeader** → Schema-driven header component
2. **MirrorNavigator** → Schema-driven navigator component
3. **MirrorViewport** → Schema-driven viewport container
4. **MirrorSurfaceViewer** → Schema-driven surface viewer

### Phase 2: Control Components
1. **ViewModeToggle** → View mode switcher
2. **TemporalControls** → Past/Present/Future selector
3. **ThemeSwitcher** → Theme selection list
4. **NavigatorToggle** → Show/hide navigator button

### Phase 3: Interactive Components
1. **ResizablePanel** → Wrap ResizeHandle as schema component
2. **UploadButton** → Wrap UploadHandler as schema component
3. **FocusModeContainer** → Focus mode wrapper

### Phase 4: Domain Components
1. **FinancialDashboard** → Wrap CashFlowTimeline + ExpenseBreakdown
2. **ObjectInspector** → Enhanced SurfaceViewer

---

## Schema Mapping

### Mirror Base App Schema Structure

```json
{
  "id": "mirror-base",
  "name": "Mirror Base",
  "description": "Core Mirror interface framework",
  "version": "2.0.0",
  "header": "mirror-base/header",
  "navigator": "mirror-base/navigator",
  "surfaceViewer": "mirror-base/surface-viewer",
  "viewports": [
    {
      "id": "viewport1",
      "label": "Viewport 1",
      "schema": "mirror-base/viewport1",
      "defaultHeight": 50
    },
    {
      "id": "viewport2",
      "label": "Viewport 2",
      "schema": "mirror-base/viewport2",
      "defaultHeight": 50
    }
  ]
}
```

### Header Schema
```json
{
  "viewports": {
    "header": [
      {
        "type": "Stack",
        "props": { "direction": "horizontal", "justify": "between", "align": "center" },
        "children": [
          {
            "type": "ViewModeToggle",
            "props": { "modes": ["full", "split", "left-only"] }
          },
          {
            "type": "Text",
            "props": { "text": "Mirror", "variant": "logo" }
          },
          {
            "type": "Stack",
            "props": { "direction": "horizontal", "spacing": "sm" },
            "children": [
              {
                "type": "TemporalControls",
                "props": { "modes": ["past", "present", "future"] }
              },
              {
                "type": "UploadButton"
              }
            ]
          }
        ]
      }
    ]
  }
}
```

### Navigator Schema
```json
{
  "viewports": {
    "navigator": [
      {
        "type": "Stack",
        "props": { "spacing": "lg" },
        "children": [
          {
            "type": "NavigatorSection",
            "props": { "title": "THEMES" },
            "children": [
              {
                "type": "ThemeSwitcher"
              }
            ]
          },
          {
            "type": "NavigatorSection",
            "props": { "title": "FINANCIAL" },
            "children": [
              {
                "type": "NavigatorItem",
                "props": { "label": "Dashboard", "icon": "📊" }
              },
              {
                "type": "NavigatorItem",
                "props": { "label": "Transactions", "icon": "💳", "badge": "12" }
              }
            ]
          }
        ]
      }
    ]
  }
}
```

---

## Component Props Interface

### MirrorHeader
```typescript
interface MirrorHeaderProps {
  logo?: string;
  title?: string;
  viewModes?: string[];
  temporalModes?: string[];
  showUpload?: boolean;
  onViewModeChange?: (mode: string) => void;
  onTemporalChange?: (mode: string) => void;
}
```

### MirrorNavigator
```typescript
interface MirrorNavigatorProps {
  sections?: NavigatorSection[];
  width?: number;
  collapsible?: boolean;
  defaultCollapsed?: boolean;
}
```

### MirrorViewport
```typescript
interface MirrorViewportProps {
  label?: string;
  content?: React.ReactNode;
  focusable?: boolean;
  resizable?: boolean;
  height?: number | string;
}
```

### MirrorSurfaceViewer
```typescript
interface MirrorSurfaceViewerProps {
  tabs?: SurfaceTab[];
  selectedObject?: any;
  width?: number;
  collapsible?: boolean;
}
```

---

## Implementation Checklist

### Core Components
- [ ] MirrorHeader
- [ ] MirrorNavigator  
- [ ] MirrorViewport
- [ ] MirrorSurfaceViewer

### Control Components
- [ ] ViewModeToggle
- [ ] TemporalControls
- [ ] ThemeSwitcher
- [ ] NavigatorToggle
- [ ] SurfaceViewerToggle

### Interactive Components
- [ ] ResizablePanel
- [ ] UploadButton
- [ ] FocusModeContainer

### Domain Components
- [ ] CashFlowTimeline (wrap existing)
- [ ] ExpenseBreakdown (wrap existing)
- [ ] FinancialDashboard

### Schemas
- [ ] mirror-base/app.json
- [ ] mirror-base/header.json
- [ ] mirror-base/navigator.json
- [ ] mirror-base/surface-viewer.json
- [ ] mirror-base/viewport1.json
- [ ] mirror-base/viewport2.json

### Registration
- [ ] Register all new components in ComponentRegistry
- [ ] Update registerComponents.ts

---

## Next Steps

1. Build core Mirror components as modular schema-driven components
2. Create mirror-base app schemas
3. Test integration with existing v2 architecture
4. Migrate domain components (CashFlowTimeline, ExpenseBreakdown)
5. Document component APIs and usage

---

**Status:** Ready to begin extraction and rebuild
