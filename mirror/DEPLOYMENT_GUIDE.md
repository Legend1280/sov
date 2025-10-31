# Mirror v2 Deployment Guide

**Version:** 2.0  
**Date:** October 31, 2025  
**Author:** Brady Simmons  
**Copyright:** © 2025 Sovereignty Foundation. All rights reserved.

---

## Overview

This guide provides step-by-step instructions for deploying the Mirror v2 modular architecture. All necessary files have been created and are ready for integration.

---

## Pre-Deployment Checklist

Before deploying, ensure you have:

- [x] Backup created: `mirror_backup_20251031_144952.tar.gz`
- [x] All new files created and in place
- [x] Component registration system implemented
- [x] MirrorContext provider configured
- [x] App schemas created (DexaBooks, SAGE)
- [x] Lifecycle hooks added to AppRegistry

---

## File Summary

### New Core Files (13 files)

| File | Purpose |
|------|---------|
| `/src/core/EventBus.ts` | Event communication system |
| `/src/core/DataContext.tsx` | API access and state provider |
| `/src/core/MirrorContext.tsx` | Unified context provider |
| `/src/core/AppRegistry.ts` | App manifest management with lifecycle hooks |
| `/src/core/registerComponents.ts` | Component registration system |
| `/src/types/schema.ts` | TypeScript type definitions |
| `/src/components/core/AppContainer.tsx` | Root app component |
| `/src/components/core/Renderer.tsx` | Dynamic component renderer |
| `/src/components/core/Text.tsx` | Text display component |
| `/src/components/core/NavigatorSection.tsx` | Navigator section header |
| `/src/components/core/NavigatorItem.tsx` | Navigator item button |
| `/src/components/core/ButtonWrapper.tsx` | Button schema wrapper |
| `/src/components/core/BadgeWrapper.tsx` | Badge schema wrapper |

### Layout Containers (4 files)

| File | Purpose |
|------|---------|
| `/src/components/layout/Grid.tsx` | Grid layout container |
| `/src/components/layout/Stack.tsx` | Stack layout container |
| `/src/components/layout/Tabs.tsx` | Tab container layout |
| `/src/components/layout/Split.tsx` | Split pane layout |

### App Schemas (8 files)

| File | Purpose |
|------|---------|
| `/src/apps/dexabooks/app.json` | DexaBooks app manifest |
| `/src/apps/dexabooks/header.json` | DexaBooks header schema |
| `/src/apps/dexabooks/navigator.json` | DexaBooks navigator schema |
| `/src/apps/dexabooks/main.json` | DexaBooks main viewport |
| `/src/apps/sage/app.json` | SAGE app manifest |
| `/src/apps/sage/header.json` | SAGE header schema |
| `/src/apps/sage/navigator.json` | SAGE navigator schema |
| `/src/apps/sage/main.json` | SAGE main viewport |

### Modified Files (2 files)

| File | Changes |
|------|---------|
| `/src/App.tsx` | Added MirrorProvider and component registration |
| `/src/pages/Home.tsx` | Updated to use AppContainer and Renderer |
| `/src/core/APIService.ts` | Enhanced with generic HTTP methods |

---

## Deployment Steps

### Step 1: Verify File Integrity

```bash
cd /home/ubuntu/sov/mirror/client/src

# Check that all new files exist
ls -la core/MirrorContext.tsx
ls -la core/registerComponents.tsx
ls -la components/core/AppContainer.tsx
ls -la components/core/Renderer.tsx
ls -la apps/dexabooks/app.json
ls -la apps/sage/app.json
```

### Step 2: Install Dependencies (if needed)

```bash
cd /home/ubuntu/sov/mirror
pnpm install
```

### Step 3: Build the Application

```bash
cd /home/ubuntu/sov/mirror
pnpm build
```

### Step 4: Test in Development Mode

```bash
cd /home/ubuntu/sov/mirror
pnpm dev
```

Open your browser to `http://localhost:5173` and verify:

- [ ] Application loads without errors
- [ ] DexaBooks app is loaded by default
- [ ] Header displays "DexaBooks" with an Upload button
- [ ] Navigator shows Financial section with Dashboard, Transactions, and Analytics items
- [ ] Main viewport displays "DexaBooks Dashboard" heading
- [ ] Console shows component registration and app discovery messages

### Step 5: Verify Component Registration

Open the browser console and check for these log messages:

```
[Mirror] Registering components...
[Mirror] Registered 11 components
[ComponentRegistry] Registered: AppContainer
[ComponentRegistry] Registered: Text
[ComponentRegistry] Registered: NavigatorSection
[ComponentRegistry] Registered: NavigatorItem
[ComponentRegistry] Registered: Button
[ComponentRegistry] Registered: Badge
[ComponentRegistry] Registered: Grid
[ComponentRegistry] Registered: Stack
[ComponentRegistry] Registered: Tabs
[ComponentRegistry] Registered: TabPanel
[ComponentRegistry] Registered: Split
[Mirror] App discovery complete
[AppRegistry] Registered app: DexaBooks (dexabooks)
[AppRegistry] Registered app: SAGE (sage)
[AppRegistry] Active app: dexabooks
```

### Step 6: Test App Switching (Optional)

To test app switching, you can temporarily add a button to switch between apps:

```typescript
// In Home.tsx, add this button
<button onClick={() => loadApp('sage')}>
  Switch to SAGE
</button>
```

This should trigger the `onDeactivate` hook for DexaBooks and the `onActivate` hook for SAGE.

---

## Troubleshooting

### Issue: "Component 'X' not found in registry"

**Solution:** Ensure the component is registered in `/src/core/registerComponents.ts` and that the file is imported correctly.

### Issue: "Schema 'X' not found"

**Solution:** Verify that the schema file exists in the `/src/apps` directory and that the file name matches the schema ID.

### Issue: "useMirror must be used within MirrorProvider"

**Solution:** Ensure that `MirrorProvider` is wrapping your app in `App.tsx` and that you're using the `useMirror` hook inside a component that is a child of the provider.

### Issue: Dynamic import errors

**Solution:** Vite requires explicit glob patterns for dynamic imports. The current implementation uses `import.meta.glob` which should work correctly. If you see errors, check the Vite configuration.

---

## Rollback Procedure

If you need to rollback to the previous version:

```bash
cd /home/ubuntu/sov
tar -xzf mirror_backup_20251031_144952.tar.gz
```

This will restore the original `mirror/client/src` directory.

---

## Next Steps

After successful deployment:

1. **Add Module Components** - Create domain-specific components for each module (SAGE, Kronos, Logos, etc.)
2. **Implement Data Fetching** - Connect components to the Core API using the `dataContext.api` service
3. **Add Event Handlers** - Use the `eventBus` to enable inter-component communication
4. **Create More Apps** - Add additional apps for other modules
5. **Integrate with Core** - Update the `loadSchema` function in `AppContainer.tsx` to fetch schemas from the Core API

---

## Support

For questions or issues:

- **Architecture Specification:** `/docs/architecture/mirror_modular_design_v2.md`
- **Implementation Guide:** `/docs/guides/implementation_guide.md`
- **File Manifest:** `/mirror/FILE_MANIFEST.md`

---

**End of Deployment Guide**
