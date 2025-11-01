# Sovereignty Constitution

**Version:** 1.0  
**Constitution ID:** SOV-CONST-001  
**Hash:** SHA3-512:82be17951693abc9a6e68ce654015766eeff5c7bddd6e5b097b0ab73eafaebff8209b58f17a59b7b6c9a593c045e8cda4ddba7de3d825c2065e515f1bcf2aca8

---

## Overview

The **Sovereignty Constitution** is the formal governance framework for the Sovereignty Stack. It defines the fundamental rights, obligations, and enforcement mechanisms that govern all nodes participating in the PulseMesh network.

The Constitution is implemented as a **Pulse-native** governance layer, where constitutional alignment is verified during the PulseMesh handshake process. Nodes that have not signed the Constitution are rejected with close code **4004**.

---

## Architecture

### Constitutional Alignment Flow

```
Node Startup
    ↓
Sign Constitution (node_sign.py)
    ↓
Generate SHA256 Signature
    ↓
Store in signatures.json
    ↓
Connect to PulseMesh
    ↓
Handshake: Signature Verification (existing)
    ↓
Handshake: Constitutional Alignment Check (NEW)
    ↓
Verify Constitution Signature
    ↓
[ALIGNED] → Session Created
[NOT ALIGNED] → Connection Rejected (4004)
```

### Components

#### 1. Constitution Definition (`constitution.yaml`)

The source constitution defining:
- **Preamble**: Foundational principles
- **Rights**: What nodes are entitled to
- **Obligations**: What nodes must do
- **Enforcement**: How violations are handled
- **Amendments**: How the constitution evolves

#### 2. Constitution Compiler (`constitution_compile.py`)

Compiles the YAML constitution into JSON with:
- SHA3-512 cryptographic hash
- Timestamp and version tracking
- Environment variable export
- Provenance metadata

**Usage:**
```bash
python3.11 constitution_compile.py
```

**Output:**
- `constitution.json` - Compiled constitution with hash
- `constitution.env` - Environment variables for deployment

#### 3. Constitution Registration (`constitution_register.py`)

Registers the constitution across all nodes via **PulseBus** (Pulse-native, not HTTP):
- Emits `{node}.constitution.register` Pulse to each node
- Emits global `constitution.activated` event
- Uses asyncio and PulseBus for event-driven registration

**Usage:**
```bash
python3.11 constitution_register.py
```

**Pulse Events Emitted:**
- `mirror.constitution.register`
- `core.constitution.register`
- `sage.constitution.register`
- `kronos.constitution.register`
- `shadow.constitution.register`
- `pulsemesh.constitution.register`
- `constitution.activated` (global)

#### 4. Constitution Checker (`constitution_check.py`)

Verifies constitutional alignment for nodes:
- Loads compiled constitution
- Loads node signatures from `signatures.json`
- Verifies signature hash matches current constitution
- Returns alignment status with reason codes

**API:**
```python
from constitution_check import verify_node_alignment

alignment = verify_node_alignment("mirror")
# Returns: {
#   "aligned": True,
#   "reason": "signed",
#   "constitution_hash": "SHA3-512:...",
#   "signed_at": "2025-11-01T01:43:24.713081Z"
# }
```

**Reason Codes:**
- `signed` - Node is constitutionally aligned
- `unsigned` - Node has not signed the constitution
- `hash_mismatch` - Node signed a different constitution version
- `constitution_not_loaded` - Constitution file not found

#### 5. Node Signing (`node_sign.py`)

Signs the constitution on behalf of a node:
- Generates deterministic SHA256 signature
- Stores signature in `signatures.json`
- Verifies alignment after signing

**Usage:**
```bash
# Sign as specific node
python3.11 node_sign.py mirror

# Sign all nodes
python3.11 node_sign.py
```

**Signature Format:**
```json
{
  "constitution_id": "SOV-CONST-001",
  "signatures": {
    "mirror": {
      "constitution_hash": "SHA3-512:...",
      "node_signature": "3812c3fb92b237d7...",
      "signed_at": "2025-11-01T01:43:24.713081Z"
    }
  }
}
```

#### 6. PulseMesh Integration (`pulse_mesh.py`)

PulseMesh handshake now includes constitutional alignment:

**3-Step Handshake:**
1. **Signature Verification** (existing) - Verify SHA256 HMAC signature
2. **Constitutional Alignment Check** (NEW) - Verify node has signed constitution
3. **Session Creation** - Create authenticated session

**Close Codes:**
- `4001` - Missing handshake data
- `4003` - Invalid signature
- `4004` - **Not constitutionally aligned** (NEW)

**Pulse Events Emitted:**
- `constitution.alignment.verified` - Node alignment verified
- `constitution.alignment.failed` - Node alignment failed

#### 7. Test Suite (`test_constitution.py`)

Comprehensive test suite verifying:
- Constitution loading and hash integrity
- Node signature verification
- Alignment status reporting
- Signature persistence
- Rogue node rejection

**Usage:**
```bash
python3.11 test_constitution.py
```

**Tests:**
1. Constitution Loading
2. Node Signatures
3. Alignment Verification
4. Alignment Status
5. Hash Integrity
6. Signature Persistence

---

## Constitution Content

### Preamble

> We, the nodes of the Sovereignty Stack, establish this Constitution to ensure transparent, accountable, and user-sovereign governance of all semantic communication within the PulseMesh network.

### Rights

All nodes participating in the Sovereignty Stack have the right to:

1. **Semantic Transparency**: Access to the ontological definitions governing all events
2. **Temporal Awareness**: Query the temporal state and decay of all indexed events
3. **Provenance Verification**: Audit the complete lineage of any event or decision
4. **Governance Participation**: Propose and vote on amendments to this Constitution
5. **Fair Computation**: Equal access to computational resources within capacity limits

### Obligations

All nodes participating in the Sovereignty Stack must:

1. **Emit Governed Events**: All events must conform to registered ontologies
2. **Respect SAGE Decisions**: Honor governance decisions made by SAGE
3. **Maintain Temporal Integrity**: Report accurate timestamps for all events
4. **Log Provenance**: Record all actions in the Shadow Ledger
5. **Honor User Sovereignty**: Prioritize user intent over system convenience

### Enforcement

Constitutional violations are enforced through:

1. **Event Rejection**: Non-conforming events are rejected by SAGE
2. **Temporal Decay**: Violations accelerate temporal decay in Kronos
3. **Provenance Flagging**: Violations are permanently flagged in Shadow Ledger
4. **Node Suspension**: Repeated violations result in temporary suspension
5. **Constitutional Review**: Severe violations trigger governance review

### Amendments

This Constitution may be amended through:

1. **Proposal**: Any node may propose an amendment via `constitution.amendment.proposed` Pulse
2. **Review**: SAGE reviews amendment for consistency and feasibility
3. **Vote**: All nodes vote on amendment via `constitution.amendment.vote` Pulse
4. **Ratification**: Amendment requires 2/3 majority to pass
5. **Deployment**: Ratified amendments are compiled with new hash and re-signed by all nodes

---

## Implementation Status

### ✅ Phase 1: Constitution Definition
- Created `constitution.yaml` with preamble, rights, obligations, enforcement, amendments
- Compiled to JSON with SHA3-512 hash
- Generated environment variables for deployment

### ✅ Phase 2: Pulse-Native Registration
- Registered constitution across all 6 nodes via PulseBus
- Emitted constitution registration Pulses (not HTTP)
- Global `constitution.activated` event emitted

### ✅ Phase 3: PulseMesh Enforcement
- Added constitutional alignment check to PulseMesh handshake
- Nodes without valid signatures rejected with close code 4004
- Alignment events emitted to PulseBus

### ✅ Phase 4: Node Signing
- All 6 nodes signed the constitution:
  - Mirror (signed at 2025-11-01T01:43:24Z)
  - Core (signed at 2025-11-01T01:43:24Z)
  - SAGE (signed at 2025-11-01T01:43:24Z)
  - Kronos (signed at 2025-11-01T01:43:24Z)
  - Shadow (signed at 2025-11-01T01:43:24Z)
  - PulseMesh (signed at 2025-11-01T01:43:24Z)

### ✅ Phase 5: Testing and Validation
- All 6 tests passed:
  - Constitution Loading ✅
  - Node Signatures ✅
  - Alignment Verification ✅
  - Alignment Status ✅
  - Hash Integrity ✅
  - Signature Persistence ✅

---

## Files

### Core Files
- `/core/security/constitution.yaml` - Source constitution definition
- `/core/security/constitution.json` - Compiled constitution with hash
- `/core/security/constitution.env` - Environment variables
- `/core/security/signatures.json` - Node signatures

### Implementation
- `/core/security/constitution_compile.py` - Compiler
- `/core/security/constitution_register.py` - Registration via PulseBus
- `/core/security/constitution_check.py` - Alignment verification
- `/core/security/node_sign.py` - Node signing utility
- `/core/security/test_constitution.py` - Test suite

### Integration
- `/core/pulse_mesh.py` - PulseMesh with constitutional alignment enforcement

---

## Usage Examples

### Check Node Alignment

```python
from constitution_check import verify_node_alignment

# Check if mirror is aligned
alignment = verify_node_alignment("mirror")

if alignment['aligned']:
    print(f"✅ Mirror is constitutionally aligned")
    print(f"   Signed at: {alignment['signed_at']}")
else:
    print(f"❌ Mirror is not aligned: {alignment['reason']}")
```

### Sign Constitution as Node

```bash
# Sign as specific node
python3.11 node_sign.py mirror

# Sign all nodes
python3.11 node_sign.py
```

### Get Alignment Status

```python
from constitution_check import get_checker

checker = get_checker()
status = checker.get_alignment_status()

print(f"Constitution: {status['constitution_id']}")
print(f"Signed Nodes: {status['signed_nodes']}/{status['total_nodes']}")

for node_id, alignment in status['nodes'].items():
    icon = "✅" if alignment['aligned'] else "❌"
    print(f"{icon} {node_id}: {alignment['reason']}")
```

### Run Tests

```bash
python3.11 test_constitution.py
```

---

## Security Considerations

### Hash Integrity

The constitution uses **SHA3-512** hashing to ensure:
- Tamper detection: Any modification changes the hash
- Version tracking: Each constitution version has unique hash
- Signature verification: Nodes sign specific hash, not content

### Signature Storage

Node signatures are stored in `signatures.json`:
- Each signature includes constitution hash
- Signatures are verified against current constitution
- Mismatched hashes indicate version drift

### Handshake Enforcement

PulseMesh enforces constitutional alignment:
- Alignment checked after signature verification
- Unsigned nodes rejected before session creation
- Close code 4004 indicates constitutional violation

### Rogue Node Protection

Nodes without signatures cannot:
- Connect to PulseMesh
- Emit or receive Pulses
- Participate in governance
- Access system resources

---

## Future Work

### Amendment Process
- Implement `constitution.amendment.proposed` Pulse handler
- Create voting mechanism via SAGE
- Automate re-compilation and re-signing on ratification

### Constitutional Queries
- Add GraphQL endpoint for constitution queries
- Enable natural language constitution search
- Integrate with Mirror UI for user-facing constitution display

### Governance Dashboard
- Real-time alignment status visualization
- Amendment proposal and voting interface
- Constitutional violation tracking and reporting

### Multi-Version Support
- Support multiple constitution versions simultaneously
- Graceful migration between versions
- Backward compatibility for legacy nodes

---

## References

- [PulseMesh Architecture](./PULSEMESH_ARCHITECTURE_v1.0.md)
- [PulseMesh Security](./PULSEMESH_SECURITY.md)
- [Pulse Migration Guide](./PULSE_MIGRATION_GUIDE.md)
- [Security Ontology](../core/ontology/security.yaml)
- [Constitution Source](../core/security/constitution.yaml)

---

**Copyright © 2025 Sovereignty Foundation. All rights reserved.**
