# DexaBooks v1.0: MVP Project Outline

**Date:** October 29, 2025  
**Author:** Manus AI  
**Strategy:** Separate Dashboard (Lean & Intentional)

---

## 1. Vision & Guiding Principles

This document outlines a lean, 10-day sprint plan to build DexaBooks v1.0, a functional Minimum Viable Product (MVP) for financial forecasting. Our core principle is **speed through simplicity**. We will achieve this by building DexaBooks as a **separate, standalone frontend application** that communicates with the robust, existing LoomLite backend. This approach minimizes complexity, eliminates the risk of breaking the core LoomLite application, and allows for rapid, parallel development.

**The Goal:** A working dashboard that can ingest a CSV of transactions, forecast recurring expenses, and visualize cash flow on a timeline.

## 2. System Architecture (Option 1: Separate Dashboards)

We will create a new, independent frontend for DexaBooks while extending the LoomLite backend with a dedicated financial module. This is the cleanest, fastest path to a functional MVP.

```mermaid
graph TD
    subgraph User
        U[User's Browser]
    end

    subgraph Vercel Deployments
        LL_FE[LoomLite UI]
        DX_FE[DexaBooks UI (New)]
    end

    subgraph Render Deployment
        subgraph FastAPI Backend (LoomLite)
            LL_API[LoomLite Endpoints (/api/*)]
            DX_API[DexaBooks Endpoints (New) (/api/dexabooks/*)]
            
            subgraph Shared Services
                DB[SQLite Database]
                VDB[ChromaDB]
                MiniLM[Embedding Service]
                Prov[Provenance Service]
            end
        end
    end

    U -- Visits --> LL_FE
    U -- Visits --> DX_FE

    LL_FE -- Calls --> LL_API
    DX_FE -- Calls --> DX_API

    LL_API --> DB
    LL_API --> VDB
    LL_API --> MiniLM
    LL_API --> Prov

    DX_API --> DB
    DX_API --> VDB
    DX_API --> MiniLM
    DX_API --> Prov
```

| Component | Architecture Decision |
|---|---|
| **Project Structure** | A new `/dexabooks` project will be created, sibling to `/loomlite`. |
| **Frontend** | A new, separate Single-Page Application (SPA) in `/dexabooks/frontend`. It will reuse LoomLite's basic HTML structure and `eventBus.js` but will have its own new D3.js visualizations. |
| **Backend** | The existing LoomLite FastAPI server. A new, dedicated module will be created at `loomlite/backend/dexabooks/` to contain all financial-specific logic. |
| **API** | A new API router will be added to the FastAPI app, exposing endpoints under the `/api/dexabooks/` prefix to keep financial and knowledge-graph endpoints separate. |
| **Database** | The existing `loom_lite_v2.db` will be extended. New tables (`transactions`, `forecasts`, `accounts`) will be added via a migration script, ensuring no disruption to existing LoomLite data. |


## 3. 10-Day MVP Sprint Roadmap

This is an aggressive but achievable timeline focused on delivering a functional proof-of-concept.

### **Phase 1: Foundation & Scaffolding (Days 1-2)**

*Goal: Create the skeleton of the project and the database schema.*

- **Task 1.1:** Create the new project directory: `mkdir /home/ubuntu/dexabooks`.
- **Task 1.2:** Create the backend module structure: `mkdir -p /home/ubuntu/loomlite/backend/dexabooks`.
- **Task 1.3:** Define the database schema for `transactions`, `forecasts`, and `accounts` in `/loomlite/backend/dexabooks/schema.py`.
- **Task 1.4:** Create a new migration script (`migrate_dexabooks.py`) to add the new tables to the existing database.
- **Task 1.5:** Create the DexaBooks frontend by cloning the basic structure of the LoomLite frontend (`index.html`, `config.js`, `eventBus.js`) into `/dexabooks/frontend/` and removing all LoomLite-specific components (`galaxyView.js`, `planetView.js`, etc.).

### **Phase 2: Backend - Ingestion & Forecasting (Days 3-5)**

*Goal: Build the core data processing pipeline.*

- **Task 2.1:** In `loomlite/backend/dexabooks/api.py`, create the CSV ingestion endpoint: `/api/dexabooks/ingest`.
- **Task 2.2:** Implement the file parsing logic to read CSV rows and create `Transaction` objects according to the new schema.
- **Task 2.3:** Implement the rule-based forecasting logic. After transactions are stored, this logic will scan them to identify recurring expenses and create future `Forecast` objects.
- **Task 2.4:** Integrate the MiniLM embedding service to generate vectors for the `vendor` and `category` fields of each transaction, enabling future semantic search capabilities.
- **Task 2.5:** Add provenance logging for all key events: `transaction_ingested`, `forecast_generated`, `vector_embedded`.

### **Phase 3: Frontend - Visualization & UI (Days 6-9)**

*Goal: Build the user-facing dashboard components.*

- **Task 3.1:** Design the main dashboard layout in `/dexabooks/frontend/index.html` with placeholders for the key visualizations.
- **Task 3.2 (Core Deliverable):** Build the **Cash Flow Timeline View**. This new D3.js component will fetch all transaction and forecast data and render them on a chronological axis, showing past debits and future projections.
- **Task 3.3:** Build the **Expense Breakdown View**. A simple D3.js bar chart that displays the top 10 expenses by category or vendor, providing an at-a-glance summary.
- **Task 3.4:** Adapt the LoomLite `Navigator` component to list financial accounts and allow filtering by time period (e.g., "Next 7 Days", "This Month").
- **Task 3.5:** Connect the `eventBus` so that clicking a transaction on the timeline displays its full details in a `Surface Viewer`-style panel.

### **Phase 4: Integration, Testing & Handoff (Day 10)**

*Goal: Ensure the system works end-to-end and is ready for user testing.*

- **Task 4.1:** Perform end-to-end testing: Upload a sample CSV and verify that the data flows correctly through ingestion, forecasting, and is accurately rendered in both the timeline and breakdown views.
- **Task 4.2:** Write a `README.md` for the `/dexabooks` project with simple instructions on how to run the frontend and use the application.
- **Task 4.3:** Clean up code, add comments, and prepare the repository for handoff and user review.

## 4. DexaBooks v1.0 Deliverables

Upon completion of this 10-day sprint, we will have:

1.  **A Functional Web Dashboard:** A live, working prototype accessible via a Vercel URL.
2.  **CSV Ingestion:** The ability to upload a standard CSV file of financial transactions.
3.  **Core Visualizations:**
    - A dynamic **Cash Flow Timeline** showing past and future (forecasted) expenses.
    - An **Expense Breakdown** chart for quick analysis of top spending categories.
4.  **Complete Source Code:** The full, organized codebase for the new DexaBooks frontend and the extended backend module.
5.  **Clear Path Forward:** A stable foundation upon which to build v1.1 features like semantic search, budget tracking, and more advanced analytics.
