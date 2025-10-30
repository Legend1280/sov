# Sovereignty Stack - Quick Start Guide

**Repository:** https://github.com/Legend1280/sov

---

## Clone Repository

```bash
git clone https://github.com/Legend1280/sov.git
cd sov
```

---

## Run Core API (Semantic OS)

```bash
cd core

# Install dependencies
pip3 install -r requirements.txt

# Set environment variable
export OPENAI_API_KEY="your-key-here"

# Run server
uvicorn api:app --reload --port 8001
```

**API:** http://localhost:8001

---

## Run DexaBooks API

```bash
cd apps/dexabooks/backend

# Install dependencies
pip3 install -r requirements.txt

# Run server
uvicorn api_finance:app --reload --port 8002
```

**API:** http://localhost:8002

---

## Run Mirror Frontend (When Implemented)

```bash
cd mirror

# Install dependencies
pnpm install

# Run dev server
pnpm dev
```

**UI:** http://localhost:3000

---

## Using Startup Scripts

```bash
# Start Core API
./scripts/start-core.sh

# Start DexaBooks API
./scripts/start-dexabooks.sh
```

---

## Repository Structure

```
sov/
├── core/                    # Semantic OS backend
│   ├── api.py              # Core API
│   ├── extractor.py        # Data extraction
│   ├── embedding_service.py # Vector embeddings
│   └── requirements.txt
│
├── mirror/                  # UI Framework
│   ├── src/
│   │   ├── core/           # Framework core
│   │   ├── components/     # UI components
│   │   └── themes/         # Theme system
│   └── README.md
│
├── apps/
│   └── dexabooks/          # Financial app
│       ├── backend/
│       │   ├── api_finance.py
│       │   └── requirements.txt
│       └── README.md
│
├── docs/                    # Documentation
│   ├── architecture/
│   ├── implementation/
│   └── guides/
│
└── scripts/                 # Utility scripts
    ├── start-core.sh
    └── start-dexabooks.sh
```

---

## Test Core API

```bash
# Health check
curl http://localhost:8001/

# Create transaction
curl -X POST http://localhost:8001/api/core/financial/transaction \
  -H "Content-Type: application/json" \
  -d '{
    "amount": -50.00,
    "date": "2025-10-29",
    "description": "Test transaction",
    "transaction_type": "expense",
    "category": "Food"
  }'
```

---

## Test DexaBooks API

```bash
# Health check
curl http://localhost:8002/

# Get financial summary
curl http://localhost:8002/api/analytics/summary

# List transactions
curl http://localhost:8002/api/transactions
```

---

## Documentation

- **Root README:** `/README.md` - Project overview
- **Core README:** `/core/README.md` - API documentation
- **Mirror README:** `/mirror/README.md` - Framework guide
- **DexaBooks README:** `/apps/dexabooks/README.md` - App features
- **Architecture Docs:** `/docs/architecture/`
- **Implementation Reports:** `/docs/implementation/`

---

## Development Workflow

### 1. Make Changes
```bash
# Edit files in your preferred editor
code .
```

### 2. Test Locally
```bash
# Run Core API
./scripts/start-core.sh

# Run DexaBooks API (in another terminal)
./scripts/start-dexabooks.sh
```

### 3. Commit Changes
```bash
git add .
git commit -m "Description of changes"
git push origin main
```

---

## Next Steps

1. **Implement Mirror Framework** (TypeScript + React)
2. **Build DexaBooks Frontend** (D3.js visualizations)
3. **Deploy to Production** (Render + Vercel)
4. **Add LoomLite** (Document viewer)

---

## Support

- **Issues:** https://github.com/Legend1280/sov/issues
- **Discussions:** https://github.com/Legend1280/sov/discussions

---

## License

Proprietary
