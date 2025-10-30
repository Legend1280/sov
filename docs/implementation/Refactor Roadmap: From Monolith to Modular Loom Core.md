# Refactor Roadmap: From Monolith to Modular Loom Core

**Date:** October 29, 2025  
**Author:** Manus AI  
**Vision:** Transform the monolithic LoomLite application into a modular "Semantic OS" with a shared backend (Loom Core) and multiple, independent frontend viewers (LoomLite, DexaBooks).

---

## 1. Strategic Imperative: Why Refactor?

The current LoomLite application successfully combines a backend data engine with a frontend visualization layer. However, this monolithic structure creates tight coupling, making it difficult to develop new, specialized applications like DexaBooks without risking the stability of the core system. 

By refactoring into a **Loom Core** architecture, we create a **layered, modular system** with clean separation of concerns. This is not just a technical improvement; it is a strategic evolution that enables a scalable ecosystem of semantic applications, all built upon a single, unified source of truth for ontology, provenance, and vector intelligence.

**Benefits of this Architecture:**
- **Clean Abstraction:** Core data logic evolves independently from visual UI logic.
- **Single Source of Truth:** All viewers (LoomLite, DexaBooks, etc.) consume data from the same trusted backend.
- **Scalable Ecosystem:** New applications (DexaMed, DexaOps) can be rapidly developed by building new viewers on top of the existing Core.

## 2. Target Architecture

Our goal is to achieve the following separation of concerns:

```mermaid
graph TD
    subgraph Core["Loom Core (Ontology Engine)"]
        A1[Ontology Manager]
        A2[Provenance Service]
        A3[Vector Engine]
        A4[Search API / Semantic Ops]
    end

    subgraph Viewers["Semantic Viewers"]
        L1[Loom Lite (Docs & Ontology Viewer)]
        D1[DexaBooks (Financial Viewer)]
    end

    User --> L1
    User --> D1

    L1 --> A1
    L1 --> A2
    L1 --> A3
    L1 --> A4

    D1 --> A1
    D1 --> A2
    D1 --> A3
    D1 --> A4
```

## 3. The Refactor Sprint Plan

This refactor will be executed in three phases, designed to systematically deconstruct the monolith and rebuild it as a modular system.

### **Phase 1: Carve out Loom Core**

*Goal: Isolate all shared, backend-agnostic logic into a new `loomcore` project.*

**Step 1.1: Create New Project Structure**
```bash
mkdir /home/ubuntu/loomcore
mkdir /home/ubuntu/loomcore/backend
```

**Step 1.2: Move Core Logic Modules**

The following modules from `loomlite/backend/` contain the fundamental logic of the semantic engine and will be **moved** to `loomcore/backend/`:

| File to Move | New Location | Responsibility |
|---|---|---|
| `models.py` | `/loomcore/backend/models.py` | Core Pydantic data models (Ontology, Document, etc.) |
| `extractor.py` | `/loomcore/backend/extractor.py` | Ontology extraction logic (calling OpenAI) |
| `embedding_service.py` | `/loomcore/backend/embedding_service.py`| Vector embedding generation (MiniLM) |
| `provenance.py` | `/loomcore/backend/provenance.py` | Provenance event logging service |
| `database.py` (logic) | `/loomcore/backend/database.py` | Database connection and initialization logic |
| `schema_v2.sql` | `/loomcore/backend/schema_v2.sql` | The master database schema |

**Step 1.3: Create the Loom Core API**

A new FastAPI application will be created at `/loomcore/backend/api.py`. This will become the single, unified entry point for all backend services. It will expose endpoints under the `/api/core/` prefix.

**Initial Endpoints for Loom Core API:**
- `POST /api/core/ingest`: Universal ingestion endpoint.
- `GET /api/core/documents/{doc_id}`: Retrieve a document and its ontology.
- `GET /api/core/search`: Perform semantic and keyword search.
- `GET /api/core/provenance/{doc_id}`: Get the provenance trail for an object.

### **Phase 2: Refactor LoomLite into a Pure Viewer**

*Goal: Transform the existing LoomLite project into a thin client that consumes data from Loom Core.*

**Step 2.1: Slim Down the LoomLite Backend**
The `loomlite/backend/api.py` will be drastically simplified. Its new role is to serve document-specific data to the LoomLite frontend, acting as a proxy to the Loom Core.

- **Remove:** All direct database access, ingestion logic, and model extraction code.
- **Refactor:** All endpoints (e.g., `/tree`, `/doc/{id}/ontology`) will be rewritten to make HTTP calls to the new Loom Core API (`/api/core/*`).

**Example Refactor:**
```python
# OLD: loomlite/backend/api.py
@app.get("/tree")
def get_document_tree():
    # Direct database query
    docs = query_database_for_documents()
    return docs

# NEW: loomlite/backend/api.py
import httpx

LOOM_CORE_URL = "http://localhost:8001"

@app.get("/tree")
def get_document_tree():
    # Call the Loom Core API
    response = httpx.get(f"{LOOM_CORE_URL}/api/core/documents")
    return response.json()
```

**Step 2.2: Update the LoomLite Frontend**
No major changes are needed for the LoomLite frontend initially. The `config.js` will continue to point to its own backend (`http://localhost:8000`), which now acts as a secure and specialized proxy to the master Loom Core.

### **Phase 3: Create the DexaBooks Viewer**

*Goal: Build the new DexaBooks application as the second viewer client of Loom Core.*

**Step 3.1: Create the DexaBooks Project**
```bash
mkdir /home/ubuntu/dexabooks
mkdir /home/ubuntu/dexabooks/frontend
mkdir /home/ubuntu/dexabooks/backend
```

**Step 3.2: Build the DexaBooks Frontend**
- **Clone:** Copy the basic shell from `loomlite/frontend/` (`index.html`, `eventBus.js`, `config.js`).
- **Remove:** Delete all LoomLite-specific visualization files (`galaxyView.js`, `planetView.js`, etc.).
- **Create:** Build the new D3.js components for financial visualization (`cashFlowTimeline.js`, `expenseBreakdown.js`).

**Step 3.3: Build the DexaBooks Backend**
A new, lightweight FastAPI server will be created at `dexabooks/backend/api_finance.py`. Similar to the refactored LoomLite backend, its job is to serve financial data by calling the Loom Core.

- **Extend Core Schema:** Add the `transactions`, `forecasts`, and `accounts` tables to the master `loomcore/backend/schema_v2.sql` and create a migration script.
- **Create Financial Endpoints:** The `api_finance.py` will define endpoints like `/api/dexabooks/ingest` and `/api/dexabooks/transactions`.
- **Call Core Services:** The ingestion endpoint will receive a CSV, parse it, and then call `POST /api/core/ingest` with the structured transaction data, mapping it to the extended ontology.

## 4. Post-Refactor Directory Structure

The final project layout will be:

```
/loomcore/
    └── backend/         # The "Semantic OS"
        ├── api.py
        ├── models.py
        ├── extractor.py
        ├── embedding_service.py
        ├── provenance.py
        └── schema_v2.sql

/loomlite/
    ├── frontend/        # Document Visualization UI
    │   ├── galaxyView.js
    │   └── ...
    └── backend/         # Thin proxy backend for docs
        └── api_docs.py

/dexabooks/
    ├── frontend/        # Financial Visualization UI
    │   ├── cashFlowTimeline.js
    │   └── ...
    └── backend/         # Thin proxy backend for finance
        └── api_finance.py
```

---

## 5. Next Steps

This refactor is a prerequisite for the DexaBooks sprint. Once this roadmap is approved, the next immediate actions are:

1.  **Execute Phase 1:** Create the `loomcore` directory and move the core modules.
2.  **Begin Phase 2:** Start refactoring the LoomLite backend to call the (soon-to-be-created) Loom Core API.
3.  **Update DexaBooks Plan:** Formally update the DexaBooks project plan to reflect this new architecture.
