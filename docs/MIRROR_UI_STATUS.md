# Mirror UI Extraction Status

**Author:** Brady Simmons  
**Copyright:** © 2025 Sovereignty Foundation. All rights reserved.  
**Date:** October 31, 2025

---

## Current State

The Mirror Base UI is **functionally working** with all core components rendering, but needs **visual refinement** to match the original design.

### What's Working ✅

1. **MirrorHeader** - Renders with view mode controls, temporal controls, and upload button
2. **MirrorNavigator** - Displays sections (THEMES, FINANCIAL, GOVERNANCE) with navigation items
3. **MirrorViewport** - Shows viewport content with labels
4. **MirrorSurfaceViewer** - Renders with tabbed interface (Details, Document, Provenance)
5. **Schema Loading** - All JSON schemas load correctly
6. **Component Registry** - All 18 components registered and rendering

### What Needs Work 🔧

#### 1. **ThemeSwitcher Component**
- **Issue:** Shows text "ThemeSwitcher" instead of rendering the actual theme list
- **Root Cause:** Navigator schema references ThemeSwitcher as a string, not rendering it as a component
- **Fix:** Update MirrorNavigator to handle component references in sections

#### 2. **Layout and Spacing**
- Navigator is too narrow
- Viewports need better height distribution
- Surface Viewer needs proper width
- Missing resize handle functionality

#### 3. **Styling Consistency**
- Colors and borders need refinement
- Shadows and depth need adjustment
- Typography needs to match original
- Button styles need polish

#### 4. **Missing Components**
From the original MirrorLayout, we still need to extract:
- **CashFlowTimeline** - Financial visualization component
- **ExpenseBreakdown** - Expense analysis component
- **ManusDialog** - Custom dialog wrapper

#### 5. **Viewport Content**
- Viewport 2 is not rendering (only shows label)
- Need to create proper placeholder content
- Grid layout in Viewport 1 needs styling

---

## Comparison: Old vs New

### Old MirrorLayout Features

```tsx
// From MirrorLayout.tsx
- Header with view mode icons (Full, Split, Left-only)
- Temporal controls (Past, Present, Future)
- Upload button
- Navigator with:
  - Theme switcher (actual rendered list)
  - Collapsible sections
  - Navigation items with badges
  - Proper spacing and styling
- Dual viewports with:
  - Resize handles
  - Focus mode (double-click)
  - Proper height distribution
- Surface Viewer with:
  - Tabbed interface
  - Close button
  - Proper width (400px)
```

### Current Mirror Base Status

```tsx
// What we have now
✅ Header structure
✅ Navigator structure
✅ Viewport structure
✅ Surface Viewer structure
❌ ThemeSwitcher not rendering
❌ Resize handles not functional
❌ Layout proportions off
❌ Styling incomplete
```

---

## Action Plan

### Phase 1: Fix ThemeSwitcher Rendering
1. Update MirrorNavigator to detect component references in sections
2. Render components dynamically using the Renderer
3. Test theme switching functionality

### Phase 2: Fix Layout Proportions
1. Set proper widths:
   - Navigator: 280px
   - Surface Viewer: 400px
   - Viewports: flex-1 (fill remaining space)
2. Set proper heights:
   - Header: auto
   - Main content: flex-1
   - Viewports: 50/50 split with resize capability

### Phase 3: Implement Resize Functionality
1. Connect ResizablePanel to actual resize logic
2. Store resize state in MirrorContext
3. Apply resize values to component widths/heights

### Phase 4: Refine Styling
1. Match colors from original design
2. Add proper shadows and borders
3. Refine typography
4. Polish button states (hover, active, focus)

### Phase 5: Extract Domain Components
1. Wrap CashFlowTimeline as schema component
2. Wrap ExpenseBreakdown as schema component
3. Create example viewport using these components

### Phase 6: Test and Verify
1. Compare side-by-side with old Mirror
2. Test all interactions (collapse, resize, focus, theme switch)
3. Verify schema loading and component rendering
4. Document any remaining differences

---

## Next Immediate Steps

1. **Fix ThemeSwitcher** - This is the most visible issue
2. **Fix Viewport 2** - Should show content, not just label
3. **Adjust layout proportions** - Make it look like the original
4. **Test resize handles** - Ensure they actually work

---

## Files to Modify

1. `/mirror/client/src/components/mirror/MirrorNavigator.tsx` - Fix component rendering
2. `/mirror/client/src/components/mirror/MirrorContainer.tsx` - Fix layout proportions
3. `/mirror/client/src/components/mirror/ResizablePanel.tsx` - Implement resize logic
4. `/mirror/client/src/apps/mirror-base/navigator.json` - Fix ThemeSwitcher reference
5. `/mirror/client/src/apps/mirror-base/viewport2.json` - Add proper content

---

## Success Criteria

The Mirror Base UI will be considered complete when:

✅ ThemeSwitcher renders and works  
✅ All layout proportions match original  
✅ Resize handles function correctly  
✅ Styling matches original design  
✅ All components render without errors  
✅ Visual parity with old Mirror achieved  

---

**Status:** In Progress - 70% Complete
