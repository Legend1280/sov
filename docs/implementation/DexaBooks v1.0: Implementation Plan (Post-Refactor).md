> This plan has been updated to align with the new **Loom Core** modular architecture.

# DexaBooks v1.0: Implementation Plan (Post-Refactor)

**Date:** October 29, 2025  
**Author:** Manus AI  
**Architecture:** DexaBooks as a Viewer of Loom Core

---

## 1. Project Goal

To build a lean, functional financial forecasting dashboard (DexaBooks) as a standalone frontend application that consumes data from the central **Loom Core** backend. This ensures DexaBooks benefits from the shared semantic OS (ontology, provenance, vectors) while remaining an independent, easy-to-maintain application.

## 2. DexaBooks Implementation Sprint

This sprint runs **in parallel** with or **immediately after** the Loom Core refactor. It focuses exclusively on building the DexaBooks viewer.

### **Phase 1: Backend - Financial Module & API (2 Days)**

*Goal: Extend Loom Core to understand financial concepts and expose them via a dedicated API.* 

- **Task 1.1: Extend the Core Ontology:**
  - **Location:** `/loomcore/backend/schema_v2.sql`
  - **Action:** Add the `transactions`, `forecasts`, and `accounts` tables to the master database schema. Create a migration script (`migrate_dexabooks.py`) within the `/loomcore` project to apply these changes.

- **Task 1.2: Create the DexaBooks Backend Proxy:**
  - **Location:** `/dexabooks/backend/api_finance.py`
  - **Action:** Create a new, lightweight FastAPI server. This server will define the `/api/dexabooks/*` endpoints.

- **Task 1.3: Implement the Ingestion Endpoint:**
  - **Endpoint:** `POST /api/dexabooks/ingest`
  - **Logic:** This endpoint will:
    1. Receive a CSV file.
    2. Parse the CSV into structured `Transaction` objects.
    3. Call the **Loom Core API** (`POST /api/core/ingest`) to store these objects, mapping them to the newly defined ontology types.
    4. Trigger the recurrence detection and forecast generation logic (which also calls Loom Core to store `Forecast` objects).

- **Task 1.4: Implement Data Query Endpoints:**
  - **Endpoints:** 
    - `GET /api/dexabooks/transactions`
    - `GET /api/dexabooks/forecasts`
    - `GET /api/dexabooks/top_expenses`
  - **Logic:** These endpoints will simply act as proxies, calling the appropriate search and query endpoints on the Loom Core API to retrieve the financial data.

### **Phase 2: Frontend - Visualizations & UI (3 Days)**

*Goal: Build the user-facing dashboard components from scratch, reusing only the basic shell from LoomLite.*

- **Task 2.1: Initialize the Frontend Shell:**
  - **Location:** `/dexabooks/frontend/`
  - **Action:** Create the project by copying `index.html`, `eventBus.js`, and `config.js` from LoomLite. The `config.js` will point to the DexaBooks backend proxy (`http://localhost:8002`).

- **Task 2.2: Build the Cash Flow Timeline View:**
  - **File:** `cashFlowTimeline.js`
  - **Action:** Create the primary D3.js visualization. It will fetch data from `/api/dexabooks/transactions` and `/api/dexabooks/forecasts` to render past and future expenses on a chronological axis.

- **Task 2.3: Build the Expense Breakdown View:**
  - **File:** `expenseBreakdown.js`
  - **Action:** Create a D3.js bar chart that fetches data from `/api/dexabooks/top_expenses` to display a summary of spending.

- **Task 2.4: Build the Financial Navigator & Viewer:**
  - **Files:** `financialNavigator.js`, `transactionViewer.js`
  - **Action:** Create simplified versions of the LoomLite Navigator and Surface Viewer, adapted to display financial accounts, time filters, and transaction details.

### **Phase 3: Integration & Testing (1 Day)**

*Goal: Ensure the DexaBooks viewer works seamlessly with the Loom Core backend.*

- **Task 3.1:** End-to-end test: Upload a CSV through the DexaBooks UI and verify the data appears correctly in all visualizations.
- **Task 3.2:** Write a `README.md` for the `/dexabooks` project.
- **Task 3.3:** Prepare for handoff and user review.

---

## 3. Final Deliverables

1.  **A Refactored Loom Ecosystem:** Three separate, well-defined projects: `loomcore`, `loomlite`, and `dexabooks`.
2.  **A Functional DexaBooks Dashboard:** A working prototype that can ingest, forecast, and visualize financial data.
3.  **A Scalable Foundation:** A "Semantic OS" architecture ready for future applications.
