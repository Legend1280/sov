# Upload Button Implementation Documentation

## Overview

The **Upload Button** is a fully functional, ontology-aware file ingestion bridge between Mirror (UI) and Core (semantic kernel). It transforms local files into semantic objects with complete provenance tracking.

## Architecture

### Components

#### 1. **UploadHandler Component** (`mirror/client/src/components/UploadHandler.tsx`)

The primary React component that handles the entire upload workflow:

- **File Selection**: Opens native file picker dialog
- **Content Processing**: Converts files to base64 for transmission
- **Metadata Extraction**: Detects MIME types and computes file properties
- **API Communication**: Sends structured payload to Core ingestion endpoint
- **UI Feedback**: Displays success/error notifications with auto-dismiss
- **State Management**: Tracks upload progress and status

**Key Features:**
- Supports multiple file types (PDF, DOCX, Pages, XLSX, CSV, images, etc.)
- Automatic MIME type detection based on file extension
- Base64 encoding for binary file transmission
- Error handling with user-friendly messages
- Loading states during upload
- Auto-dismissing notifications (5s for success, 8s for errors)

#### 2. **Core Ingestion Endpoint** (`core/core_api.py`)

FastAPI endpoint at `POST /api/ingest` that processes uploaded files:

**Pipeline:**
1. Decode base64 content
2. Compute SHA-256 content hash for provenance
3. Determine ontology type based on MIME type
4. Create semantic object using Core reasoner
5. Generate provenance record
6. Return structured response with object metadata

**Request Schema:**
```json
{
  "filename": "string",
  "mimetype": "string",
  "size": "integer",
  "content_base64": "string",
  "source": "MirrorUpload",
  "timestamp": "ISO 8601 string"
}
```

**Response Schema:**
```json
{
  "status": "success",
  "object_id": "uuid",
  "ontology_type": "Document|Image|Spreadsheet",
  "provenance_id": "uuid",
  "metadata": {
    "filename": "string",
    "mimetype": "string",
    "size": "integer",
    "content_hash": "sha256 hex",
    "ingested_at": "ISO 8601 string",
    "sage_validated": "boolean",
    "coherence_score": "float"
  }
}
```

#### 3. **MirrorLayout Integration** (`mirror/client/src/components/MirrorLayout.tsx`)

The Upload Button is integrated into the main Mirror layout header:

- Replaces the previous non-functional Upload button
- Stores uploaded object metadata in component state
- Automatically opens SurfaceViewer panel on successful upload
- Logs upload events to console for debugging

## File Type Support

### Supported Formats

| Category | Extensions | MIME Types | Ontology Type |
|----------|-----------|------------|---------------|
| **Documents** | .pdf, .doc, .docx, .pages, .txt | application/pdf, application/msword, etc. | Document |
| **Spreadsheets** | .xls, .xlsx, .csv | application/vnd.ms-excel, text/csv | Spreadsheet |
| **Images** | .png, .jpg, .jpeg, .gif, .svg | image/png, image/jpeg, etc. | Image |
| **Data** | .json, .xml | application/json, application/xml | Document |

## Semantic Principles

### Ontology Awareness

Every uploaded file becomes a **semantic object** with:
- **Type Classification**: Automatic ontology type assignment
- **Provenance Tracking**: Complete audit trail of ingestion event
- **Content Hashing**: SHA-256 hash for integrity verification
- **SAGE Validation**: Coherence and trust scoring (when available)

### Provenance Event Structure

Each upload generates a provenance record:
```json
{
  "event_type": "ingest",
  "actor": "MirrorUser",
  "timestamp": "2025-10-30T20:15:00Z",
  "content_hash": "sha256...",
  "source": "MirrorUpload",
  "metadata": {
    "filename": "document.pdf",
    "size": 23847,
    "mimetype": "application/pdf"
  }
}
```

## User Experience

### Upload Flow

1. **User clicks "Upload" button** in Mirror header (top-right)
2. **File picker dialog opens** with supported file type filters
3. **User selects file** from local filesystem
4. **Button shows "Uploading..." state** with disabled interaction
5. **File is processed** (read, encoded, metadata extracted)
6. **Request sent to Core** at `localhost:8001/api/ingest`
7. **Success notification appears** below button for 5 seconds
8. **SurfaceViewer opens** automatically to display object details
9. **Object metadata stored** in Mirror state for Viewport 2 rendering

### Error Handling

The system provides clear error messages for common issues:

- **"Core API unreachable"**: Core service not running on port 8001
- **"Unsupported file format"**: File type not in supported list
- **"Invalid base64 content"**: File encoding failed
- **"Ingestion failed: [details]"**: Server-side processing error

## Testing

### Manual Testing Steps

1. **Start Core API:**
   ```bash
   cd /home/ubuntu/sov/core
   uvicorn core_api:app --host 0.0.0.0 --port 8001 --reload
   ```

2. **Start Mirror Client:**
   ```bash
   cd /home/ubuntu/sov/mirror
   pnpm install
   pnpm dev
   ```

3. **Test Upload:**
   - Open Mirror in browser (typically `http://localhost:5173`)
   - Click "Upload" button in header
   - Select a test file (PDF, CSV, image, etc.)
   - Verify success notification appears
   - Check browser console for upload response
   - Verify SurfaceViewer opens with object details

### Verification Checklist

- [ ] File picker opens on button click
- [ ] Button shows "Uploading..." during processing
- [ ] Success notification displays with correct message
- [ ] Error notification shows if Core API is down
- [ ] SurfaceViewer opens automatically on success
- [ ] Console logs show complete response object
- [ ] Multiple uploads work sequentially
- [ ] Different file types are handled correctly

## API Endpoints

### Core API

- **Base URL**: `http://localhost:8001`
- **Endpoint**: `POST /api/ingest`
- **Content-Type**: `application/json`
- **CORS**: Enabled for all origins

### Request Example

```bash
curl -X POST http://localhost:8001/api/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "test.pdf",
    "mimetype": "application/pdf",
    "size": 12345,
    "content_base64": "JVBERi0xLjQK...",
    "source": "MirrorUpload",
    "timestamp": "2025-10-30T20:15:00Z"
  }'
```

## Future Enhancements

### Planned Features

1. **Vector Embedding Generation**: Automatic MiniLM embedding for text-based files
2. **Viewport 2 Rendering**: Display uploaded objects in dedicated viewport
3. **Batch Upload**: Support multiple file selection
4. **Progress Indicators**: Show upload progress percentage
5. **File Preview**: Display file content before upload
6. **Drag-and-Drop**: Support drag-and-drop file upload
7. **Upload History**: Show recent uploads in Navigator panel
8. **Content Extraction**: Parse and index file contents (PDF text, CSV data, etc.)

### Ontology Extensions

Future ontology types to support:
- **Email**: .eml, .msg files
- **Code**: .py, .js, .tsx files
- **Archive**: .zip, .tar.gz files
- **Audio**: .mp3, .wav files
- **Video**: .mp4, .mov files

## Troubleshooting

### Common Issues

**Issue**: "Core API unreachable" error
- **Solution**: Ensure Core API is running on port 8001
- **Check**: `curl http://localhost:8001/` should return health check

**Issue**: Upload button doesn't respond
- **Solution**: Check browser console for JavaScript errors
- **Check**: Verify UploadHandler component is imported correctly

**Issue**: File upload fails silently
- **Solution**: Check Core API logs for server-side errors
- **Check**: Verify file size is reasonable (< 50MB recommended)

**Issue**: Success notification doesn't appear
- **Solution**: Check Alert component is properly imported
- **Check**: Verify Tailwind CSS classes are compiled

## Milestone Completion

### ✅ M6_UPLOAD_SYSTEM_COMPLETE

The Upload Button implementation satisfies all requirements:

- [x] File picker dialog opens on click
- [x] Supports multiple file formats (CSV, PDF, DOCX, Pages, XLSX, images)
- [x] Parses file metadata and content
- [x] Sends processed data to Core ingestion endpoint
- [x] Registers provenance event with timestamp and actor
- [x] Returns structured response with object ID and type
- [x] Displays confirmation notification
- [x] Maintains minimal design aesthetic
- [x] Includes comprehensive error handling
- [x] Integrates seamlessly with existing Mirror layout

## References

- **Mirror Framework Documentation**: `docs/architecture/Mirror Framework v1.0 - Developer Documentation.md`
- **Core Constitution**: `docs/architecture/The Core Constitution v1.0.md`
- **LoomLite Ontology Standard**: `docs/architecture/LoomLite_Ontology_Standard_v2.2.md`
- **Project Structure**: `STRUCTURE.txt`

---

**Last Updated**: October 30, 2025  
**Version**: 1.0  
**Status**: Implementation Complete
