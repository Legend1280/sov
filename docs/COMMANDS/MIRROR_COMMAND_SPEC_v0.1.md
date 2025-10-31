# Mirror Command Specification v0.1

**Author:** Brady Simmons  
**Copyright:** © 2025 Sovereignty Foundation. All rights reserved.  
**Version:** 0.1  
**Date:** October 31, 2025

---

## Purpose

This document defines the first five actionable semantic commands executable by Mirror, Core, or Manus through `/command` syntax or natural-language equivalents. These commands form the foundation of Mirror's command-language interface, enabling governed, provenance-tracked operations across the Sovereignty Stack.

---

## Ontology Definition

All commands are stored as `MirrorCommand` objects in Core's ontology system:

```yaml
MirrorCommand:
  fields:
    syntax: str
    description: str
    args: list
    effect: str
    version: str
    category: str
    verified: bool
  relations:
    author: User
    created_at: datetime
    updated_at: datetime
```

---

## Command Categories

| Category          | Purpose                               |
|:------------------|:--------------------------------------|
| **layout**        | Modify viewport or layout composition |
| **visualization** | Spawn or modify live displays         |
| **data**          | Show, filter, or stream logs          |
| **governance**    | Undo, validate, or secure changes     |

---

## 1. /clear [viewport]

### Intent
Reset a specific viewport to a blank state.

### Syntax
```
/clear viewport1
/clear viewport2
```

### Effect
- Removes all rendered components from the specified viewport
- Replaces it with a placeholder node (`<div class="viewport-blank" />`)
- Logs an event to Shadow Ledger: `cleared:viewport{N}`
- Maintains viewport structure but clears content

### Arguments
| Name     | Type   | Required | Description                    |
|:---------|:-------|:---------|:-------------------------------|
| viewport | string | Yes      | ID of viewport to clear (e.g., `viewport1`) |

### Examples
```
/clear viewport1  → Clears top viewport
/clear viewport2  → Clears bottom viewport
```

### Status
✅ Implemented in v0.1  
📍 File: `/src/pages/Home.tsx`

---

## 2. /visualize pulse [source→target]

### Intent
Spawn a real-time visualization of semantic Pulse activity between two systems.

### Syntax
```
/visualize pulse mirror→core
/visualize pulse core→sage
```

### Effect
- Loads `MirrorPulseViewer` or `PulseConnectionVisualizer` into specified viewport
- Subscribes to active `PulseBridge` stream for the specified connection
- Renders live coherence and transmission metrics:
  - Coherence percentage (0-100%)
  - Pulse latency
  - Trust score
  - Intent distribution
- Updates in real-time as Pulses flow

### Arguments
| Name   | Type   | Required | Description                           |
|:-------|:-------|:---------|:--------------------------------------|
| source | string | Yes      | Source system (e.g., `mirror`, `core`) |
| target | string | Yes      | Target system (e.g., `core`, `sage`)   |

### Examples
```
/visualize pulse mirror→core  → Shows Mirror-Core communication
/visualize pulse core→sage    → Shows Core-SAGE governance flow
```

### Status
✅ Implemented in v0.1  
📍 Files: 
- `/src/components/mirror/MirrorPulseViewer.tsx`
- `/src/components/mirror/PulseConnectionVisualizer.tsx`

---

## 3. /add tab [viewport] [label]

### Intent
Add a new tabbed panel to an existing viewport for multi-context visualization.

### Syntax
```
/add tab viewport2 "Provenance Log"
/add tab viewport1 "SAGE Rules"
```

### Effect
- Creates a new tab container within specified viewport
- Loads appropriate component based on label context
- Updates layout schema under `apps/mirror-base/app.json`
- Logs addition to provenance: `added:tab:{label}`
- Enables multi-view context switching within single viewport

### Arguments
| Name     | Type   | Required | Description                        |
|:---------|:-------|:---------|:-----------------------------------|
| viewport | string | Yes      | Target viewport ID                 |
| label    | string | Yes      | Human-readable tab label (quoted)  |

### Examples
```
/add tab viewport2 "Provenance Log"  → Adds provenance viewer tab
/add tab viewport1 "SAGE Rules"      → Adds governance rules tab
/add tab viewport2 "Kronos Timeline" → Adds temporal decay viewer
```

### Status
🚧 Planned for v0.2  
📍 Target File: `/src/core/layout/TabController.ts`

---

## 4. /show log [type]

### Intent
Render a scrollable event viewer for system logs, provenance, or ledger data.

### Syntax
```
/show log shadow-ledger
/show log provenance
/show log system-events
```

### Effect
- Loads corresponding log viewer component in designated viewport
- Queries Core via Pulse for event stream
- Displays real-time append-only updates with:
  - Timestamp (ISO 8601 UTC)
  - Actor/initiator
  - Action performed
  - Coherence score (if applicable)
- Supports filtering and search

### Arguments
| Name | Type   | Required | Description                                    |
|:-----|:-------|:---------|:-----------------------------------------------|
| type | string | Yes      | Log type: `shadow-ledger`, `provenance`, `system-events` |

### Examples
```
/show log shadow-ledger  → Shows immutable provenance ledger
/show log provenance     → Shows object creation/modification history
/show log system-events  → Shows system-level events and errors
```

### Status
🚧 Planned for v0.2  
📍 Target Files:
- `/src/components/logs/ShadowLedgerViewer.tsx`
- `/src/components/logs/ProvenanceViewer.tsx`

---

## 5. /reset [scope]

### Intent
Undo recent modifications within a defined scope (viewport, app, or session).

### Syntax
```
/reset viewport1
/reset layout
/reset session
```

### Effect
- Restores last committed state from Core's version history
- Writes reversal to provenance: `undo:{scope}`
- Optionally triggers `git revert` if linked to dev environment
- SAGE validates rollback permission before execution
- Kronos timestamps the restoration event

### Arguments
| Name  | Type   | Required | Description                                           |
|:------|:-------|:---------|:------------------------------------------------------|
| scope | string | Yes      | Reset scope: `viewport1`, `viewport2`, `layout`, `session` |

### Examples
```
/reset viewport1  → Restores viewport1 to last saved state
/reset layout     → Restores entire layout configuration
/reset session    → Clears all session state and reloads
```

### Status
🚧 Planned for v0.3  
📍 Target File: `/src/core/governance/ResetController.ts`

---

## Storage & Tracking

| Layer                    | Location                                    | Function                      |
|:-------------------------|:--------------------------------------------|:------------------------------|
| **Core Ontology**        | `objects → MirrorCommand`                   | Canonical command definitions |
| **Mirror Runtime Cache** | `/src/core/commands/registry.json`          | Executable lookup table       |
| **Git Docs**             | `docs/COMMANDS/MIRROR_COMMAND_SPEC_v0.1.md` | Human-readable reference      |
| **Shadow Ledger**        | `storage/shadow_ledger.log`                 | Records each invocation       |

---

## Lifecycle of a Command

| Phase              | Operation                           | Example                                      |
|:-------------------|:------------------------------------|:---------------------------------------------|
| **Definition**     | Stored as `MirrorCommand` in Core   | `id=uuid, syntax="/clear [viewport]"`        |
| **Execution**      | Mirror sends Pulse → Core validates | Pulse topic = `mirror:command:execute`       |
| **Governance**     | SAGE checks permission              | Ensures command not destructive beyond scope |
| **Temporal Trace** | Kronos logs timestamp & phase       | `phase=Δt since prior command`               |
| **Reflection**     | Mirror updates UI + logs provenance | Viewer shows `Executed /clear viewport1`     |

---

## Versioning Policy

Commands are versioned semantically as part of the Mirror Protocol:

| Version | Description                                          |
|:--------|:-----------------------------------------------------|
| v0.1    | Basic layout commands (`/clear`, `/visualize`)       |
| v0.2    | Theming + context switching commands (`/add tab`)    |
| v0.3    | Governance commands (`/reset`, `/validate`)          |
| v1.0    | Formalized protocol + registry integration with Core |

---

## Next Steps

To make these commands fully operational:

1. ✅ Define commands in this specification
2. 🚧 Register commands as `MirrorCommand` objects in Core
3. 🚧 Implement `CommandInterpreter` in Mirror runtime
4. 🚧 Add SAGE governance rules for command execution
5. 🚧 Integrate with Shadow Ledger for provenance tracking

---

## References

- [PULSE Specification](../PULSE_SPEC_COMPLIANCE.md)
- [SAGE Governance Model](../../mirror/client/src/core/sage/SageMiddleware.ts)
- [Kronos Temporal Tracker](../../mirror/client/src/core/kronos/KronosTracker.ts)
