# Core Kernel Architecture v1.0

**Date:** October 30, 2025  
**Objective:** Build Core as a semantic reasoning kernel for the Sovereignty Stack

---

## 1. Kernel Design Principles

Core is **not just an API** - it is a **semantic operating system kernel** that provides:

1. **Symbolic Reasoning** - Ontology schemas, validation, logical rules
2. **Subsymbolic Reasoning** - Vector embeddings, semantic similarity, context clustering
3. **Governance** - SAGE validation, provenance tracking, coherence scoring
4. **Local Inference** - No external API dependencies, self-contained reasoning

---

## 2. Kernel Modules

### 2.1 Reasoner (`reasoner.py`)
**Purpose:** Main reasoning engine that fuses symbolic and vector representations

**Functions:**
- `reason(object_type, object_id)` → Returns `ReasonedObject`
- `infer_relations(object_id)` → Returns semantic neighbors
- `validate_coherence(object)` → Returns coherence score

**Data Flow:**
```
Input Object → [Ontology Validation + Vector Embedding + SAGE Check] → ReasonedObject
```

### 2.2 Ontology (`ontology.py`)
**Purpose:** Schema validation and object management

**Reuses:** `ontology_validator.py` (existing logic)

**Functions:**
- `validate(obj, object_type)` → (is_valid, errors)
- `get_schema(object_type)` → Schema definition
- `list_object_types()` → Available types

### 2.3 Embeddings (`embeddings.py`)
**Purpose:** Vector operations and semantic similarity

**Reuses:** `embedding_service.py`, `vector_utils.py` (existing logic)

**Functions:**
- `generate_embedding(text)` → Vector
- `find_similar(vector, top_k)` → Similar objects
- `coherence_score(vec1, vec2)` → Similarity score

### 2.4 Provenance (`provenance.py`)
**Purpose:** Audit trail and lineage tracking

**Status:** Already exists, keep as-is

**Functions:**
- `log_event(action, object_id, metadata)`
- `get_lineage(object_id)` → Provenance chain

### 2.5 SAGE (`sage.py`)
**Purpose:** Governance logic and validation

**Functions:**
- `validate_action(user, action, object)` → Allowed/Denied
- `coherence_check(object)` → Coherence score
- `trust_score(object_id)` → Trust rating

### 2.6 Storage (`storage.py`)
**Purpose:** SQLite persistence layer

**Functions:**
- `save_object(obj)` → object_id
- `get_object(object_id)` → Object
- `query(filters)` → List of objects

### 2.7 API (`api.py`)
**Purpose:** FastAPI interface (thin layer over reasoner)

**Endpoints:**
- `POST /api/core/reason` - Main reasoning endpoint
- `GET /api/core/object/{id}` - Get reasoned object
- `POST /api/core/ingest` - Ingest new object
- `GET /api/core/similar/{id}` - Find similar objects

---

## 3. Data Structures

### ReasonedObject
```python
{
    "object": "Transaction",
    "symbolic": {
        "id": "txn_001",
        "amount": 2500,
        "category": "Equipment Lease",
        "timestamp": "2025-10-29T21:55:00Z"
    },
    "vector": {
        "embedding": [0.129, 0.884, ...],  # 384-dim
        "coherence": 0.93,
        "relations": ["txn_131", "txn_118"]
    },
    "provenance": {
        "created_by": "Mirror.UI",
        "validated_by": "SAGE",
        "module": "DexaBooks",
        "timestamp": "2025-10-29T21:55:00Z"
    },
    "sage": {
        "coherence_score": 0.93,
        "trust_score": 0.87,
        "validated": true
    }
}
```

---

## 4. Reasoning Pipeline

```
1. Input: Object + Context
   ↓
2. Ontology: Validate against schema
   ↓
3. Embeddings: Generate vector representation
   ↓
4. SAGE: Check coherence and trust
   ↓
5. Reasoner: Fuse symbolic + vector + governance
   ↓
6. Output: ReasonedObject
   ↓
7. Mirror: Render visualization
```

---

## 5. Implementation Plan

### Phase 1: Core Kernel Modules
- [x] Audit existing logic (ontology_validator, embedding_service, provenance)
- [ ] Create `storage.py` - SQLite persistence
- [ ] Create `sage.py` - Governance logic
- [ ] Create `embeddings.py` - Wrapper around existing embedding_service
- [ ] Create `ontology.py` - Wrapper around existing ontology_validator
- [ ] Create `reasoner.py` - Main reasoning engine

### Phase 2: API Layer
- [ ] Create `api.py` - FastAPI endpoints
- [ ] Add CORS for Mirror
- [ ] Add health checks
- [ ] Test reasoning pipeline

### Phase 3: Integration
- [ ] Connect Mirror to Core API
- [ ] Test DexaBooks with real data
- [ ] Verify provenance tracking
- [ ] Test semantic similarity

---

## 6. Design Philosophy

Core operates on the same cognitive loop as human reasoning:

| Cognitive Function | System Equivalent |
|--------------------|-------------------|
| Perception | Embeddings (vector space) |
| Interpretation | Ontology (symbolic schema) |
| Judgment | SAGE (governance) |
| Memory | Provenance (audit trail) |
| Reasoning | Reasoner (fusion engine) |

---

## 7. Key Differences from Traditional APIs

**Traditional API:**
- Stateless request/response
- No semantic understanding
- No reasoning capability
- External dependencies

**Core Kernel:**
- Stateful reasoning engine
- Semantic understanding (symbolic + vector)
- Local inference capability
- Self-contained (no external APIs)

---

## 8. Next Steps

1. Build storage layer
2. Build SAGE governance
3. Build reasoner
4. Create API endpoints
5. Test with DexaBooks
6. Connect to Mirror

---

**Status:** Architecture defined, ready for implementation
