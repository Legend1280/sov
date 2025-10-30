# Core - Semantic Operating System

**Version:** 1.0.0  
**Date:** October 29, 2025

---

## Overview

**Core** is the central semantic reasoning engine of the Sovereignty Stack. It provides ontology management, vector embeddings, provenance tracking, and a unified API for all applications.

Core acts as a **single source of truth** for semantic data, enabling multiple specialized frontends (DexaBooks, LoomLite, etc.) to share the same backend infrastructure.

---

## Architecture

Core provides four fundamental services:

### 1. Ontology Management
- Unified semantic schema and type hierarchy
- YAML-based ontology definitions
- Automatic validation of all objects
- Inheritance and property constraints

### 2. Vector Engine
- 384-dimensional embeddings using MiniLM
- Semantic similarity search
- Contextual relationship mapping
- Automatic embedding generation

### 3. Provenance Tracking
- Immutable audit trail for all operations
- Actor tracking (who created/modified)
- Event logging (created, updated, deleted)
- Metadata preservation

### 4. Search API
- Unified query interface for all data types
- SQL-like filtering (date, category, type)
- Vector-based semantic search
- Aggregations and analytics

---

## Files

```
core/
├── api.py                 # Core API implementation (FastAPI)
├── api_refactored.py      # Refactored version (modular)
├── extractor.py           # Data extraction and parsing
├── embedding_service.py   # Vector embedding service (MiniLM)
├── ontology_validator.py  # Ontology validation logic
├── provenance.py          # Provenance tracking
├── vector_utils.py        # Vector utilities
├── config.json            # Configuration
├── ontology/              # Ontology schemas (YAML)
│   ├── base_ontology.yaml
│   └── financial_ontology.yaml
└── database/              # Database schemas
    └── schema.sql
```

---

## Running Locally

### Prerequisites
- Python 3.11+
- OpenAI API key (for ontology extraction)

### Setup

```bash
cd core

# Install dependencies
pip3 install fastapi uvicorn sentence-transformers pyyaml requests

# Set environment variable
export OPENAI_API_KEY="your-key-here"

# Run the server
uvicorn api:app --reload --port 8001
```

The API will be available at `http://localhost:8001`

---

## API Endpoints

### Health Check
- `GET /` - Server health check

### Core Endpoints
- `POST /api/core/ingest` - Universal ingestion endpoint
- `GET /api/core/documents` - List all documents
- `GET /api/core/documents/{doc_id}` - Get document with ontology
- `GET /api/core/provenance/{doc_id}` - Get provenance trail
- `GET /api/core/jobs/{job_id}` - Check job status

### Financial Domain (DexaBooks)
- `POST /api/core/financial/transaction` - Create transaction
- `GET /api/core/financial/transactions` - List transactions
- `POST /api/core/financial/transactions/similar` - Semantic search
- `POST /api/core/financial/forecast` - Create forecast
- `GET /api/core/financial/forecasts` - List forecasts

### Ontology
- `GET /api/core/ontology/types` - List all object types
- `GET /api/core/ontology/schema/{type}` - Get schema for type

---

## Database

Core uses **SQLite** for data persistence.

**Database file location:**
- **Production:** `/data/core.db`
- **Local:** `./core.db`

**Tables:**
- `documents` - All ontological objects
- `document_embeddings` - Vector representations (384-dim)
- `provenance_events` - Audit trail

---

## Ontology System

### Base Ontology

All objects inherit from base types:

```yaml
Concept:
  properties:
    name: String
    description: String

Document:
  inherits: Concept
  properties:
    title: String
    content: String
    created_at: DateTime
    updated_at: DateTime
```

### Domain Ontologies

Domain-specific types extend the base:

**Financial Ontology** (`ontology/financial_ontology.yaml`):

```yaml
Transaction:
  inherits: Document
  properties:
    amount: Number
    date: Date (YYYY-MM-DD)
    description: String
    transaction_type: String (income|expense)
    category: String
    vendor: String
    is_recurring: Boolean
    recurrence_pattern: String

Forecast:
  inherits: Concept
  properties:
    predicted_amount: Number
    predicted_date: Date
    predicted_description: String
    confidence: Float (0.0-1.0)
    forecast_method: String
    status: String (pending|confirmed|missed)
```

---

## Vector Embeddings

Core automatically generates **384-dimensional embeddings** for all objects using the **MiniLM** model.

**Embedding Service:**
- Model: `sentence-transformers/all-MiniLM-L6-v2`
- Dimensions: 384
- Storage: `document_embeddings` table
- Use case: Semantic similarity search

**Example:**
```python
# Find similar transactions
POST /api/core/financial/transactions/similar
{
  "transaction_id": "abc-123",
  "limit": 5
}
```

---

## Provenance Tracking

Every operation is logged in the provenance ledger:

```json
{
  "event_id": "uuid",
  "doc_id": "abc-123",
  "event_type": "created",
  "actor": "dexabooks",
  "timestamp": "2025-10-29T21:55:00Z",
  "metadata": {
    "object_type": "Transaction",
    "amount": -1500.00
  }
}
```

**Query provenance:**
```bash
GET /api/core/provenance/{doc_id}
```

---

## Configuration

**config.json:**
```json
{
  "database": {
    "path": "./core.db"
  },
  "embeddings": {
    "model": "sentence-transformers/all-MiniLM-L6-v2",
    "dimensions": 384
  },
  "api": {
    "port": 8001,
    "cors_origins": ["http://localhost:3000"]
  }
}
```

---

## Development

### Adding a New Domain

1. Create ontology schema in `ontology/{domain}_ontology.yaml`
2. Add domain-specific endpoints to `api.py`
3. Update database schema if needed
4. Test validation and provenance

### Extending Ontology

1. Edit YAML schema in `ontology/`
2. Add new properties or types
3. Restart server to reload schema
4. Test with sample data

---

## Testing

### Test Transaction Creation
```bash
curl -X POST http://localhost:8001/api/core/financial/transaction \
  -H "Content-Type: application/json" \
  -d '{
    "amount": -50.00,
    "date": "2025-10-29",
    "description": "Grocery shopping",
    "transaction_type": "expense",
    "category": "Food"
  }'
```

### Test Semantic Search
```bash
curl -X POST http://localhost:8001/api/core/financial/transactions/similar \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "abc-123",
    "limit": 5
  }'
```

---

## Deployment

### Production Setup

```bash
# Install dependencies
pip3 install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY="your-key-here"
export DATABASE_PATH="/data/core.db"

# Run with production server
uvicorn api:app --host 0.0.0.0 --port 8001
```

### Docker (Optional)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8001"]
```

---

## Performance

| Metric | Value |
|--------|-------|
| Transaction Creation | ~200-300ms |
| Semantic Search | ~200-300ms |
| Embedding Generation | ~100-200ms |
| Provenance Query | ~50-100ms |

---

## License

Proprietary
