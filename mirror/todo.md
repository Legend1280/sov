# Mirror Framework - Development TODO

## Phase 1: Setup Mirror Framework ✅
- [x] Initialize web-static project
- [x] Copy Mirror framework core files
- [x] Copy Mirror UI components
- [x] Copy theme system
- [x] Install dependencies (Zustand, D3.js)
- [x] Set up routing
- [x] Wire up MirrorLayout to Home page
- [x] Fix TypeScript errors
- [x] Verify theme switching works

## Phase 2: Build Core API
- [ ] Create standalone Core API (FastAPI)
- [ ] Add financial ontology endpoints
- [ ] Add vector embedding service
- [ ] Add provenance tracking
- [ ] Test Core API endpoints

## Phase 3: Build DexaBooks Integration
- [ ] Copy DexaBooks components (CashFlowTimeline, ExpenseBreakdown)
- [ ] Create DexaBooks API proxy
- [ ] Connect Mirror to Core API
- [ ] Load sample financial data
- [ ] Wire up visualizations

## Phase 4: Testing & Polish
- [ ] Test full stack integration
- [ ] Verify theme switching
- [ ] Test viewport loading
- [ ] Create sample transactions
- [ ] Present working demo

## Milestone 6: Upload System ✅
- [x] Upload button functional — Ingests files into Core and reflects in Mirror
- [x] Created UploadHandler component with file processing logic
- [x] Integrated with MirrorLayout header
- [x] Added Core API ingestion endpoint (/api/ingest)
- [x] Implemented provenance tracking with content hashing
- [x] Added UI feedback with success/error notifications
- [x] Support for multiple file types (PDF, DOCX, CSV, images, etc.)
- [x] Automatic ontology type classification
- [x] Comprehensive documentation created
- **Tag**: `M6_UPLOAD_SYSTEM_COMPLETE`
