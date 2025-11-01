# Pulse Migration Scan Results

**Date:** 2025-10-31  
**Goal:** Identify all non-Pulse communication patterns in the codebase

---

## Mirror (TypeScript/React)

### API Calls Found

#### 1. UploadHandler.tsx
```typescript
// Line: components/UploadHandler.tsx
const response = await fetch('http://localhost:8001/api/ingest', {
  method: 'POST',
  body: formData
});
```
**Migration:**
```typescript
PulseBridge.emit('core.ingest', {
  source: 'mirror',
  target: 'core',
  intent: 'create',
  payload: { file: fileData }
});
```

#### 2. APIService.ts
```typescript
// core/APIService.ts (2 fetch calls)
const response = await fetch(url, { ... });
```
**Migration:** Replace entire APIService with PulseBridge wrapper

---

## Core (Python)

### Direct Imports/Calls Found

#### 1. core_api.py
```python
from reasoner import get_reasoner
from kronos import TemporalIndexer
```
**Current:** Direct function calls  
**Migration:** Listen to Pulse events

#### 2. reasoner.py
```python
from sage import get_sage
from storage import get_storage
from ontology import get_ontology
```
**Current:** Direct imports and calls  
**Migration:** Emit Pulses, listen for responses

#### 3. provenance.py
```python
# Already Pulse-native! ✅
from pulse_bus import PulseBus
```

---

## Migration Priority

### High Priority (User-Facing)
1. **UploadHandler.tsx** - File upload to Core
2. **APIService.ts** - Generic API wrapper
3. **SystemHealthVisualizer** - Connect to real Pulses

### Medium Priority (Internal)
4. **core_api.py** - API endpoints → Pulse listeners
5. **reasoner.py** - Direct calls → Pulse emit/listen

### Low Priority (Already Migrated)
- ✅ **provenance.py** - Already uses PulseBus
- ✅ **sage.py** - Already Pulse-aware
- ✅ **kronos.py** - Already Pulse-aware

---

## Summary

**Total Patterns to Migrate:** 5
- **Mirror fetch() calls:** 3
- **Core direct imports:** 2

**Already Pulse-Native:** 3
- provenance.py
- sage.py  
- kronos.py

**Estimated Effort:** 2-3 hours

---

## Next Steps

1. Create migration guide with before/after examples
2. Update Mirror components (UploadHandler, APIService)
3. Update Core components (core_api, reasoner)
4. Connect SystemHealthVisualizer to PulseBridge
5. Test end-to-end Pulse flow
6. Document and commit
