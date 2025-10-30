# Upload Button - Quick Start Guide

## Getting Started

This guide will help you get the Upload Button working in your Mirror + Core environment.

## Prerequisites

- Node.js 22+ installed
- Python 3.11+ installed
- Core API dependencies installed
- Mirror client dependencies installed

## Step 1: Start Core API

The Core API must be running on port 8001 for uploads to work.

```bash
cd /home/ubuntu/sov/core

# Install dependencies (first time only)
pip3 install -r requirements.txt

# Start the Core API
uvicorn core_api:app --host 0.0.0.0 --port 8001 --reload
```

You should see output like:
```
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

Verify Core is running:
```bash
curl http://localhost:8001/
```

Expected response:
```json
{
  "service": "Core Semantic Kernel",
  "version": "2.0.0",
  "status": "operational",
  ...
}
```

## Step 2: Start Mirror Client

In a new terminal:

```bash
cd /home/ubuntu/sov/mirror

# Install dependencies (first time only)
pnpm install

# Start the development server
pnpm dev
```

You should see:
```
VITE v5.x.x  ready in xxx ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

## Step 3: Test Upload

1. **Open Mirror in your browser**: Navigate to `http://localhost:5173`

2. **Locate the Upload button**: Top-right corner of the header, next to the temporal controls (Past/Present/Future)

3. **Click "Upload"**: A file picker dialog will open

4. **Select a test file**: Choose any supported file type:
   - PDF document
   - Word document (.doc, .docx)
   - Spreadsheet (.xls, .xlsx, .csv)
   - Image (.png, .jpg, .gif)
   - Text file (.txt)
   - JSON or XML file

5. **Wait for upload**: The button will show "Uploading..." during processing

6. **Success notification**: A green notification will appear below the button:
   > "File successfully uploaded and ingested into Core."

7. **Check the console**: Open browser DevTools (F12) and check the Console tab for the upload response:
   ```javascript
   Upload complete: {
     status: "success",
     object_id: "uuid-here",
     ontology_type: "Document",
     provenance_id: "uuid-here",
     metadata: { ... }
   }
   ```

## Step 4: Verify in Core

Check that the object was stored in Core:

```bash
# Get the object_id from the console output, then:
curl http://localhost:8001/api/core/object/{object_id}
```

This should return the full semantic object with SAGE validation scores.

## Troubleshooting

### "Core API unreachable" Error

**Cause**: Core API is not running or not accessible on port 8001

**Solution**:
1. Check if Core is running: `curl http://localhost:8001/`
2. If not, start Core: `cd /home/ubuntu/sov/core && uvicorn core_api:app --port 8001`
3. Check for port conflicts: `lsof -i :8001`

### Upload Button Doesn't Respond

**Cause**: JavaScript error in browser

**Solution**:
1. Open browser DevTools (F12) → Console tab
2. Look for red error messages
3. Common issues:
   - UploadHandler component not imported correctly
   - Alert component missing
   - TypeScript compilation errors

**Fix**:
```bash
cd /home/ubuntu/sov/mirror
pnpm install  # Reinstall dependencies
pnpm dev      # Restart dev server
```

### File Upload Fails Silently

**Cause**: Server-side error in Core API

**Solution**:
1. Check Core API terminal for error logs
2. Look for Python traceback messages
3. Common issues:
   - Database connection failed
   - Reasoner initialization error
   - Invalid ontology configuration

### Success Notification Doesn't Appear

**Cause**: Alert component styling issue

**Solution**:
1. Check that Tailwind CSS is working
2. Verify Alert component exists: `ls mirror/client/src/components/ui/alert.tsx`
3. Check browser DevTools → Elements tab for the Alert div

## Testing Different File Types

Create test files to verify all supported formats:

```bash
# Create test directory
mkdir -p ~/test-uploads

# Create test files
echo "Test document" > ~/test-uploads/test.txt
echo "name,value\ntest,123" > ~/test-uploads/test.csv
echo '{"test": "data"}' > ~/test-uploads/test.json

# Download a sample PDF
curl -o ~/test-uploads/sample.pdf https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf
```

Upload each file and verify:
- Correct MIME type detection
- Appropriate ontology type assignment
- Successful provenance recording

## Next Steps

After verifying the Upload Button works:

1. **Implement Viewport 2 Rendering**: Display uploaded objects in the viewport
2. **Add Vector Embeddings**: Generate MiniLM embeddings for text content
3. **Create Upload History**: Show recent uploads in Navigator panel
4. **Add Drag-and-Drop**: Support drag-and-drop file upload
5. **Implement Batch Upload**: Allow multiple file selection

## Support

For issues or questions:
- Check the full documentation: `UPLOAD_SYSTEM_DOCUMENTATION.md`
- Review Core API logs for server-side errors
- Check browser console for client-side errors
- Verify all dependencies are installed correctly

---

**Happy Uploading! 🚀**
