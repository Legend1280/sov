# Mirror Commands

**Purpose:** This directory contains the canonical definitions of all Mirror commands, forming the command-language interface for the Sovereignty Stack.

---

## Directory Structure

```
COMMANDS/
├── README.md                        # This file
├── COMMAND_SCHEMA.json              # JSON schema for command validation
├── MIRROR_COMMAND_SPEC_v0.1.md      # Human-readable command specification
└── HISTORY/
    └── 2025-10-31_initial_commands.json  # Machine-readable command definitions
```

---

## What Are Mirror Commands?

Mirror commands are **semantic operations** that:

- Mutate or query layout schemas
- Control visualization and data display
- Integrate with Core's governance (SAGE) and temporal tracking (Kronos)
- Are version-controlled as first-class system primitives
- Can be executed via `/command` syntax or natural language through Manus

---

## Command Categories

| Category          | Purpose                               | Examples                    |
|:------------------|:--------------------------------------|:----------------------------|
| **layout**        | Modify viewport or layout composition | `/clear`, `/add tab`        |
| **visualization** | Spawn or modify live displays         | `/visualize pulse`          |
| **data**          | Show, filter, or stream logs          | `/show log`                 |
| **governance**    | Undo, validate, or secure changes     | `/reset`                    |

---

## Current Commands (v0.1)

### Implemented ✅
1. **`/clear [viewport]`** - Reset viewport to blank state
2. **`/visualize pulse [source→target]`** - Display live Pulse telemetry

### Planned 🚧
3. **`/add tab [viewport] [label]`** - Add tabbed panel to viewport (v0.2)
4. **`/show log [type]`** - Display event/ledger log feed (v0.2)
5. **`/reset [scope]`** - Restore previous state from provenance (v0.3)

---

## Storage Layers

| Layer                    | Location                                    | Function                      |
|:-------------------------|:--------------------------------------------|:------------------------------|
| **Core Ontology**        | `objects → MirrorCommand`                   | Canonical command definitions |
| **Mirror Runtime Cache** | `/src/core/commands/registry.json`          | Executable lookup table       |
| **Git Docs**             | `docs/COMMANDS/`                            | Human-readable reference      |
| **Shadow Ledger**        | `storage/shadow_ledger.log`                 | Records each invocation       |

---

## Versioning Policy

Commands follow semantic versioning as part of the Mirror Protocol:

| Version | Description                                          |
|:--------|:-----------------------------------------------------|
| v0.1    | Basic layout commands (`/clear`, `/visualize`)       |
| v0.2    | Theming + context switching commands (`/add tab`)    |
| v0.3    | Governance commands (`/reset`, `/validate`)          |
| v1.0    | Formalized protocol + registry integration with Core |

---

## Adding New Commands

To add a new command:

1. **Define in Markdown** - Add to `MIRROR_COMMAND_SPEC_v{version}.md`
2. **Add JSON definition** - Update `HISTORY/{date}_commands.json`
3. **Validate schema** - Run `pnpm exec ajv validate -s COMMAND_SCHEMA.json -d HISTORY/*.json`
4. **Register in Core** - Add as `MirrorCommand` object in Core ontology
5. **Implement handler** - Add execution logic in Mirror runtime
6. **Commit to Git** - `git commit -m "feat: add /new-command to Mirror CLI"`

---

## Validation

All command definitions are validated against `COMMAND_SCHEMA.json`:

```bash
# Validate all command definitions
pnpm exec ajv validate -s docs/COMMANDS/COMMAND_SCHEMA.json -d docs/COMMANDS/HISTORY/*.json
```

---

## Integration with Manus

Manus can load command definitions from this directory to:

- Display available operations (like `/help`)
- Enforce syntax automatically
- Execute commands through natural language
- Provide autocomplete and suggestions

---

## References

- [PULSE Specification](../PULSE_SPEC_COMPLIANCE.md)
- [SAGE Governance Model](../../mirror/client/src/core/sage/SageMiddleware.ts)
- [Kronos Temporal Tracker](../../mirror/client/src/core/kronos/KronosTracker.ts)
- [PulseBridge](../../mirror/client/src/core/pulse/PulseBridge.ts)

---

**Last Updated:** October 31, 2025  
**Maintained By:** Brady Simmons
