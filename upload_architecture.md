# Upload System Architecture Diagram

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                           │
│                    (Mirror Framework - React)                    │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 │ 1. User clicks Upload
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                      MirrorLayout.tsx                            │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  Header: [Mirror Logo] [View Modes] [Upload Button]   │    │
│  └────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 │ 2. Renders component
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                     UploadHandler.tsx                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  • File picker dialog                                     │  │
│  │  • FileReader API (read file)                            │  │
│  │  • Base64 encoding                                       │  │
│  │  • MIME type detection                                   │  │
│  │  • Metadata extraction                                   │  │
│  │  • HTTP POST request                                     │  │
│  │  • Success/Error notifications                           │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 │ 3. POST /api/ingest
                                 │    (JSON payload)
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CORE API (FastAPI)                            │
│                   localhost:8001                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  core_api.py                                             │  │
│  │  ┌────────────────────────────────────────────────────┐ │  │
│  │  │  @app.post("/api/ingest")                          │ │  │
│  │  │  def ingest_file(request: FileIngestRequest)       │ │  │
│  │  └────────────────────────────────────────────────────┘ │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 │ 4. Process file
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PROCESSING PIPELINE                           │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Step 1: Decode base64 → binary content                 │  │
│  │  Step 2: Compute SHA-256 hash                           │  │
│  │  Step 3: Classify ontology type (MIME → Type)          │  │
│  │  Step 4: Create document data structure                 │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 │ 5. Ingest into semantic layer
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                      REASONER ENGINE                             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  reasoner.ingest(ontology_type, data, actor)            │  │
│  │  ┌────────────────────────────────────────────────────┐ │  │
│  │  │  • Validate against ontology schema                │ │  │
│  │  │  • Generate vector embedding (MiniLM)              │ │  │
│  │  │  • Run SAGE evaluation                             │ │  │
│  │  │  • Store in symbolic layer                         │ │  │
│  │  │  • Create provenance record                        │ │  │
│  │  └────────────────────────────────────────────────────┘ │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 │ 6. Store in database
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    STORAGE LAYER                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  SQLite Database (core.db)                               │  │
│  │  ┌────────────────────────────────────────────────────┐ │  │
│  │  │  • objects table (symbolic data)                   │ │  │
│  │  │  • embeddings table (vector data)                  │ │  │
│  │  │  • provenance table (audit trail)                  │ │  │
│  │  │  • sage_scores table (validation metrics)          │ │  │
│  │  └────────────────────────────────────────────────────┘ │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 │ 7. Return response
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    RESPONSE PAYLOAD                              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  {                                                        │  │
│  │    "status": "success",                                  │  │
│  │    "object_id": "uuid",                                  │  │
│  │    "ontology_type": "Document",                          │  │
│  │    "provenance_id": "uuid",                              │  │
│  │    "metadata": {                                         │  │
│  │      "filename": "...",                                  │  │
│  │      "content_hash": "sha256...",                        │  │
│  │      "sage_validated": true,                            │  │
│  │      "coherence_score": 0.95                            │  │
│  │    }                                                     │  │
│  │  }                                                       │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 │ 8. Update UI state
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                      MIRROR UI UPDATE                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  • Show success notification                             │  │
│  │  • Store object in state                                 │  │
│  │  • Open SurfaceViewer panel                              │  │
│  │  • Log to console                                        │  │
│  │  • Ready for Viewport 2 rendering                        │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow Sequence

```
┌──────┐     ┌──────────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│ User │────▶│ UploadHandler│────▶│ Core API │────▶│ Reasoner │────▶│ Database │
└──────┘     └──────────────┘     └──────────┘     └──────────┘     └──────────┘
   │               │                    │                │                │
   │ Select file   │                    │                │                │
   │──────────────▶│                    │                │                │
   │               │ Read & encode      │                │                │
   │               │───────────────────▶│                │                │
   │               │                    │ Validate       │                │
   │               │                    │───────────────▶│                │
   │               │                    │                │ Store          │
   │               │                    │                │───────────────▶│
   │               │                    │                │◀───────────────│
   │               │                    │◀───────────────│   Confirm      │
   │               │◀───────────────────│   Response     │                │
   │◀──────────────│   Show success     │                │                │
   │  Notification │                    │                │                │
```

## Component Relationships

```
MirrorLayout
    │
    ├─── Header
    │     ├─── Logo
    │     ├─── View Mode Buttons
    │     ├─── Temporal Controls
    │     └─── UploadHandler ◀── NEW COMPONENT
    │            │
    │            ├─── File Input (hidden)
    │            ├─── Upload Button (visible)
    │            └─── Alert Notification
    │
    ├─── Navigator (left panel)
    ├─── Viewport 1 (top center)
    ├─── Viewport 2 (bottom center) ◀── Future: display uploaded objects
    └─── SurfaceViewer (right panel) ◀── Opens on upload success
```

## File Type Classification

```
File Extension
    │
    ├─── .pdf, .doc, .docx, .pages, .txt, .json, .xml
    │         └─── MIME Type: application/*, text/*
    │                   └─── Ontology Type: Document
    │
    ├─── .xls, .xlsx, .csv
    │         └─── MIME Type: application/vnd.*, text/csv
    │                   └─── Ontology Type: Spreadsheet
    │
    └─── .png, .jpg, .jpeg, .gif, .svg
              └─── MIME Type: image/*
                        └─── Ontology Type: Image
```

## Provenance Tracking

```
Upload Event
    │
    ├─── event_type: "ingest"
    ├─── actor: "MirrorUser"
    ├─── timestamp: ISO 8601 string
    ├─── content_hash: SHA-256 hex
    ├─── source: "MirrorUpload"
    └─── metadata
          ├─── filename
          ├─── size
          └─── mimetype
```

## Error Handling Flow

```
Upload Attempt
    │
    ├─── File Selection Failed
    │         └─── Silent (user cancelled)
    │
    ├─── File Read Failed
    │         └─── Show error: "Failed to read file"
    │
    ├─── Core API Unreachable
    │         └─── Show error: "Core API unreachable. Please ensure Core is running on port 8001."
    │
    ├─── Invalid File Type
    │         └─── Show error: "Unsupported file format"
    │
    ├─── Server Error
    │         └─── Show error: "Ingestion failed: [details]"
    │
    └─── Success
              └─── Show success: "File successfully uploaded and ingested into Core."
```

## State Management

```
UploadHandler Component State
    │
    ├─── isUploading: boolean
    │         └─── Controls button disabled state
    │         └─── Shows "Uploading..." text
    │
    ├─── uploadStatus: { type, message }
    │         └─── type: 'success' | 'error' | null
    │         └─── message: string
    │         └─── Controls Alert visibility
    │
    └─── fileInputRef: React.RefObject
              └─── Programmatic file picker trigger
              └─── Reset after upload

MirrorLayout Component State
    │
    └─── uploadedObject: object | null
              └─── Stores latest upload result
              └─── Used for Viewport 2 rendering
              └─── Triggers SurfaceViewer open
```

---

This architecture ensures:
- **Separation of concerns**: UI, API, processing, storage
- **Type safety**: TypeScript + Pydantic validation
- **Error resilience**: Comprehensive error handling
- **Semantic integrity**: Ontology-first design
- **Audit trail**: Complete provenance tracking
- **User feedback**: Real-time status updates
