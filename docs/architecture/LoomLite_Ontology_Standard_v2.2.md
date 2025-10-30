# LoomLite Ontology Standard v2.2

**Version:** 2.2  
**Date:** October 29, 2025  
**Author:** Manus AI  
**Changes:** **MINOR VERSION** - Added formal documentation for the `provenance_events` table schema, updated deployment architecture to reflect Render migration, and documented local development database configuration.

---

## 1. Introduction

This document defines the complete data structures, schema, and user interface standards for the LoomLite ontology system, version 2.2. This is a minor version update that formally documents the provenance events table that was implemented but not included in v2.1, and updates deployment information to reflect the migration from Railway to Render.

**Key Updates in v2.2:**
- ✅ **Provenance Events Table Documented** - Formal schema definition for audit trail system
- ✅ **Render Deployment** - Updated from Railway to Render hosting
- ✅ **Local Development Support** - Documented local database configuration
- ✅ **Database Path Flexibility** - Support for both production and local environments

**Implementation Status (Unchanged from v2.1):**
- **Documents Table:** ✅ 4 vector columns present (vector, vector_model, vector_fingerprint, vector_dimension)
- **Concepts Table:** ✅ 4 vector columns present (vector, vector_model, vector_fingerprint, vector_dimension)
- **Provenance Events Table:** ✅ Now formally documented
- **ChromaDB Integration:** ✅ Schema present
- **Embedding Pipeline:** ⏳ Implementation in progress

---

## 2. Core Data Structures

- **Document:** Metadata about the source document + semantic vector
- **Concept:** An abstract idea or entity extracted from the document + semantic vector
- **Relation:** A connection between two concepts
- **Span:** A specific text snippet from the original document
- **Mention:** A link between a concept and a span
- **ProvenanceEvent:** ✅ **NEWLY DOCUMENTED** - A record of a single transformation or action taken on a document
- **VectorFingerprint:** Semantic provenance tracking for embeddings

---

## 3. Schema Definitions

### 3.1. `provenance_events` Table ✅ **NEW IN v2.2**

This table provides a complete, immutable audit trail for all document processing operations. It was implemented in the v5.2 development cycle but was not formally documented in the v2.1 standard.

| Field | Type | Description |
|---|---|---|
| `id` | INTEGER | Primary key, auto-incrementing. |
| `doc_id` | TEXT | Foreign key to the `documents` table. |
| `event_type` | TEXT | The type of event. Standard values: `ingested`, `ontology_extracted`, `summaries_generated`, `vector_generated`. |
| `timestamp` | TEXT | ISO 8601 timestamp of when the event occurred. |
| `actor` | TEXT | The component or service that performed the action (e.g., `document_reader`, `gpt-4.1-mini`, `all-MiniLM-L6-v2`). |
| `checksum` | TEXT | SHA-256 checksum of the document content at the time of the event, for integrity verification. |
| `semantic_integrity` | REAL | Optional confidence score (0.0 to 1.0) for the quality of the transformation. |
| `derived_from` | TEXT | Optional JSON array of source document IDs if this document was derived from others. |
| `metadata` | TEXT | Optional JSON string containing additional event-specific data. |

**Indexes:**
- `idx_provenance_doc_id` - For fast lookup of all events for a given document

**Usage:**
This table enables the system to answer questions like:
- When was this document ingested?
- What transformations have been applied?
- Which AI model extracted the ontology?
- Has the document been modified since ingestion?

### 3.2. `documents` Table

| Field | Type | Description | Status |
|---|---|---|---|
| `id` | TEXT | Unique identifier for the document. | ✅ |
| `title` | TEXT | The title of the document. | ✅ |
| `source_uri` | TEXT | The original source URI of the document. | ✅ |
| `created_at` | TEXT | The timestamp when the document was added. | ✅ |
| `summary` | TEXT | A 2-3 sentence summary of the entire document. | ✅ |
| `vector` | BLOB | Compressed 384-dimensional semantic vector (zlib compressed, ~500 bytes). | ✅ |
| `vector_fingerprint` | TEXT | Semantic provenance fingerprint (format: `{model}:{dim}:{hash}:{timestamp}`). | ✅ |
| `vector_model` | TEXT | Embedding model used (default: `all-MiniLM-L6-v2`). | ✅ |
| `vector_dimension` | INTEGER | Vector dimensionality (default: 384 for MiniLM). | ✅ |

### 3.3. `concepts` Table

| Field | Type | Description | Status |
|---|---|---|---|
| `id` | TEXT | Unique identifier for the concept. | ✅ |
| `doc_id` | TEXT | The ID of the document this concept belongs to. | ✅ |
| `label` | TEXT | The human-readable label for the concept. | ✅ |
| `type` | TEXT | The semantic type of the concept. | ✅ |
| `hierarchy_level` | INTEGER | The level in the semantic hierarchy. | ✅ |
| `parent_cluster_id` | TEXT | The ID of the parent cluster concept. | ✅ |
| `summary` | TEXT | A 1-sentence summary of the concept. | ✅ |
| `confidence` | REAL | The model's confidence score (0.0 to 1.0). | ✅ |
| `context_scope` | TEXT | JSON string of character offsets for highlighting. | ✅ |
| `vector` | BLOB | Compressed 384-dimensional semantic vector. | ✅ |
| `vector_fingerprint` | TEXT | Semantic provenance fingerprint. | ✅ |
| `vector_model` | TEXT | Embedding model used. | ✅ |
| `vector_dimension` | INTEGER | Vector dimensionality. | ✅ |

---

## 4. Deployment Architecture (Updated for v2.2)

### 4.1. Production Deployment (Render)

**Platform:** Render  
**Backend URL:** `https://loomlite.onrender.com`  
**Frontend URL:** `https://loomlite.vercel.app`

**Database Location:**
- Production: Managed by Render, path determined by environment
- Database Type: SQLite with persistent volume

### 4.2. Local Development Environment

**Backend:** `localhost:8000`  
**Frontend:** `localhost:3000`

**Database Configuration:**
```python
DB_DIR = os.getenv("DB_DIR", "/data" if os.path.exists("/data") else ".")
DB_PATH = os.path.join(DB_DIR, "loom_lite_v2.db")
```

**Local Database Path:** `./loom_lite_v2.db` (project root)

**Environment Variables Required:**
- `OPENAI_API_KEY` - For ontology extraction via GPT-4.1-mini

---

## 5. Migration Notes

### 5.1. Provenance Events Table Creation

For existing databases that do not have the `provenance_events` table, run:

```sql
CREATE TABLE IF NOT EXISTS provenance_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    doc_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    actor TEXT,
    checksum TEXT,
    semantic_integrity REAL,
    derived_from TEXT,
    metadata TEXT
);

CREATE INDEX IF NOT EXISTS idx_provenance_doc_id ON provenance_events(doc_id);
```

### 5.2. Migration Script

A migration utility (`migrate_local.py`) is available in the `backend/` directory to apply all necessary schema updates to local databases.

---

## 6. Version History

| Version | Date | Changes |
|---|---|---|
| 2.0 | Oct 2025 | Added vector columns to documents and concepts tables |
| 2.1 | Oct 28, 2025 | Documented Railway deployment and migration tooling |
| 2.2 | Oct 29, 2025 | Documented provenance_events table, updated for Render deployment |

---

**Author:** Manus AI  
**Last Updated:** October 29, 2025
