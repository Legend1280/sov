# Sovereignty Stack (SOV)

**Version:** 1.0.0  
**Date:** October 29, 2025

---

## Overview

The **Sovereignty Stack** is an ontology-first semantic operating system that provides a unified platform for building meaning-driven applications. It consists of three core layers:

1. **Core** - Central semantic reasoning engine (ontology, vectors, provenance)
2. **Mirror** - Reflective UI framework (dynamic visualization layer)
3. **Apps** - Domain-specific viewers (DexaBooks, LoomLite, etc.)

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Applications Layer                    │
│              (DexaBooks, LoomLite, etc.)                 │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  Mirror Framework                        │
│           (Reflective Visualization Layer)               │
│                                                           │
│  • LayoutManager - Viewport organization                 │
│  • ViewportManager - Dynamic rendering                   │
│  • ComponentRegistry - Visualization components          │
│  • ModuleRegistry - Manifest-based modules               │
│  • APIService - Core communication                       │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                    Core (Semantic OS)                    │
│                                                           │
│  • Ontology Management - Unified semantic schema         │
│  • Vector Engine - 384-dim embeddings (MiniLM)           │
│  • Provenance Tracking - Immutable audit trail           │
│  • Search API - Unified query interface                  │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              SQLite Database (core.db)                   │
│                                                           │
│  • documents - Ontological objects                        │
│  • document_embeddings - Vector representations           │
│  • provenance_events - Audit trail                       │
└─────────────────────────────────────────────────────────┘
```

---

## Repository Structure

```
sov/
├── core/                      # Semantic OS backend
│   ├── api.py                 # Core API implementation
│   ├── extractor.py           # Data extraction utilities
│   ├── embedding_service.py   # Vector embedding service
│   ├── ontology_validator.py  # Ontology validation
│   ├── provenance.py          # Provenance tracking
│   ├── vector_utils.py        # Vector utilities
│   ├── config.json            # Configuration
│   ├── ontology/              # Ontology schemas (YAML)
│   └── database/              # Database schemas
│
├── mirror/                    # UI Framework
│   ├── src/
│   │   ├── core/              # Framework core
│   │   │   ├── LayoutManager.ts
│   │   │   ├── ViewportManager.tsx
│   │   │   ├── ComponentRegistry.ts
│   │   │   ├── ModuleRegistry.ts
│   │   │   └── APIService.ts
│   │   ├── components/        # UI components
│   │   │   ├── MirrorLayout.tsx
│   │   │   ├── SurfaceViewer.tsx
│   │   │   └── ResizeHandle.tsx
│   │   └── themes/            # Theme system
│   │       └── ThemeManager.ts
│   └── public/
│
├── apps/                      # Applications
│   └── dexabooks/             # Financial forecasting app
│       ├── backend/
│       │   └── api_finance.py # DexaBooks API
│       ├── frontend/
│       │   └── components/    # D3.js visualizations
│       └── test_data/
│
├── docs/                      # Documentation
│   ├── architecture/          # System design docs
│   ├── implementation/        # Implementation reports
│   └── guides/                # Developer guides
│
└── scripts/                   # Utility scripts
    ├── start-core.sh
    ├── start-dexabooks.sh
    └── deploy.sh
```

---

## Quick Start

### Prerequisites

- **Python 3.11+** (for Core and app backends)
- **Node.js 22+** (for Mirror framework)
- **pnpm** (for package management)
- **OpenAI API Key** (for ontology extraction)

### Running Core (Semantic OS)

```bash
cd core
pip3 install fastapi uvicorn sentence-transformers pyyaml
export OPENAI_API_KEY="your-key-here"
uvicorn api:app --reload --port 8001
```

Core API will be available at `http://localhost:8001`

### Running DexaBooks

```bash
cd apps/dexabooks/backend
pip3 install fastapi uvicorn requests
uvicorn api_finance:app --reload --port 8002
```

DexaBooks API will be available at `http://localhost:8002`

### Running Mirror (Frontend)

```bash
cd mirror
pnpm install
pnpm dev
```

Mirror UI will be available at `http://localhost:3000`

---

## Core Principles

### 1. Ontology as Truth
All data structures are defined in YAML ontology schemas. The schema **is** the ontology—no ad-hoc data structures.

### 2. Provenance as Immutability
Every object has a creation story. All operations are logged in the provenance ledger for complete audit trails.

### 3. Vectors as Meaning
384-dimensional embeddings represent semantic meaning, enabling similarity search and contextual relationships.

### 4. Mirror as Reflection
The UI is not a traditional frontend—it's a reflective surface that visualizes and manipulates semantic structures from Core.

---

## Applications

### DexaBooks (Financial Forecasting)
**Status:** ✅ Backend v1.0 Complete

A financial analytics dashboard that treats transactions as ontological objects with semantic meaning.

**Features:**
- Transaction management (CRUD)
- CSV bulk ingestion
- Financial analytics and reporting
- Semantic search (find similar transactions)
- Forecast generation (rule-based)
- Ontology validation
- Provenance tracking

**API Endpoints:** See `apps/dexabooks/README.md`

### LoomLite (Document/Ontology Viewer)
**Status:** 🔜 Planned

A document management and ontology visualization tool.

---

## Technology Stack

### Backend
- **Language:** Python 3.11
- **Framework:** FastAPI
- **Database:** SQLite
- **Embeddings:** sentence-transformers (MiniLM)
- **Ontology:** YAML schemas

### Frontend
- **Framework:** React 18 + TypeScript
- **State Management:** Zustand
- **Visualization:** D3.js
- **Build Tool:** Vite
- **Package Manager:** pnpm

---

## Documentation

- **Architecture:** See `docs/architecture/`
  - Mirror Framework v1.0
  - Core Constitution v1.0
  - LoomLite Ontology Standard v2.2

- **Implementation:** See `docs/implementation/`
  - DexaBooks Backend v1.0 - Implementation Complete
  - DexaBooks v1.0 - Final Test Report
  - Technical Specification

- **Guides:** See `docs/guides/`
  - Developer Handoff
  - Creating New Modules

---

## Development Workflow

### Adding a New Application

1. Create `/apps/{app_name}/` directory
2. Add backend API in `/apps/{app_name}/backend/`
3. Create module manifest in `/apps/{app_name}/frontend/config.json`
4. Register visualizations in `/apps/{app_name}/frontend/components/`
5. Add ontology definitions to `/core/ontology/{domain}_ontology.yaml`
6. Test via Mirror UI

### Extending Core

1. Add new ontology types to `/core/ontology/`
2. Create migration script for database
3. Add new endpoints to `/core/api.py`
4. Update documentation

---

## Deployment

### Core API
- **Platform:** Render / Railway
- **Port:** 8001
- **Database:** SQLite (persistent volume)

### Application APIs
- **Platform:** Render / Railway
- **Ports:** 8002+ (one per app)

### Mirror Frontend
- **Platform:** Vercel
- **Build:** `pnpm build`
- **Output:** Static site

---

## License

Proprietary

---

## Contact

**Author:** Brady Simmons  
**Repository:** https://github.com/Legend1280/sov

---

## Next Steps

1. **Build DexaBooks Frontend** - D3.js visualizations in Mirror
2. **Deploy to Production** - Core + DexaBooks + Mirror
3. **Implement LoomLite** - Document/ontology viewer
4. **Add More Apps** - Health analytics, etc.

For detailed implementation status, see `docs/todo.md`
