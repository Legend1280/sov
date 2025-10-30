/**
 * UploadHandler Component
 * 
 * Ontology-aware file ingestion bridge between Mirror and Core.
 * Handles local file upload, metadata extraction, and semantic object creation.
 * 
 * Sovereignty Stack Principles:
 * - Every upload is a semantic act of memory
 * - Provenance is tracked at ingestion time
 * - Files become ontological objects, not mere data
 */

import { useState, useRef, ChangeEvent } from 'react';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';

interface UploadResponse {
  status: string;
  object_id: string;
  ontology_type: string;
  provenance_id?: string;
}

interface UploadHandlerProps {
  onComplete?: (response: UploadResponse) => void;
  onError?: (error: string) => void;
}

export default function UploadHandler({ onComplete, onError }: UploadHandlerProps) {
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<{
    type: 'success' | 'error' | null;
    message: string;
  }>({ type: null, message: '' });
  const fileInputRef = useRef<HTMLInputElement>(null);

  /**
   * Detect MIME type from file extension
   */
  const getMimeType = (filename: string): string => {
    const ext = filename.split('.').pop()?.toLowerCase();
    const mimeMap: Record<string, string> = {
      pdf: 'application/pdf',
      doc: 'application/msword',
      docx: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      pages: 'application/vnd.apple.pages',
      xls: 'application/vnd.ms-excel',
      xlsx: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      csv: 'text/csv',
      txt: 'text/plain',
      json: 'application/json',
      xml: 'application/xml',
      png: 'image/png',
      jpg: 'image/jpeg',
      jpeg: 'image/jpeg',
      gif: 'image/gif',
      svg: 'image/svg+xml',
    };
    return mimeMap[ext || ''] || 'application/octet-stream';
  };

  /**
   * Convert file to base64 for transmission
   */
  const fileToBase64 = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => {
        const result = reader.result as string;
        // Remove data URL prefix (e.g., "data:application/pdf;base64,")
        const base64 = result.split(',')[1];
        resolve(base64);
      };
      reader.onerror = (error) => reject(error);
    });
  };

  /**
   * Handle file selection and ingestion
   */
  const handleFileChange = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    setUploadStatus({ type: null, message: '' });

    try {
      // Read file content as base64
      const contentBase64 = await fileToBase64(file);

      // Prepare ingestion payload with semantic metadata
      const payload = {
        filename: file.name,
        mimetype: getMimeType(file.name),
        size: file.size,
        content_base64: contentBase64,
        source: 'MirrorUpload',
        timestamp: new Date().toISOString(),
      };

      // Send to Core ingestion endpoint
      const response = await fetch('http://localhost:8001/api/ingest', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          errorData.detail || 
          response.status === 404 
            ? 'Core API unreachable. Please ensure Core is running on port 8001.'
            : `Upload failed with status ${response.status}`
        );
      }

      const result: UploadResponse = await response.json();

      // Success: Update UI and notify parent
      setUploadStatus({
        type: 'success',
        message: `File successfully uploaded and ingested into Core.`,
      });

      // Invoke callback with response
      if (onComplete) {
        onComplete(result);
      }

      // Auto-hide success message after 5 seconds
      setTimeout(() => {
        setUploadStatus({ type: null, message: '' });
      }, 5000);

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      
      setUploadStatus({
        type: 'error',
        message: errorMessage,
      });

      if (onError) {
        onError(errorMessage);
      }

      // Auto-hide error message after 8 seconds
      setTimeout(() => {
        setUploadStatus({ type: null, message: '' });
      }, 8000);
    } finally {
      setIsUploading(false);
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  /**
   * Trigger file picker dialog
   */
  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="relative">
      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        className="hidden"
        onChange={handleFileChange}
        accept=".pdf,.doc,.docx,.pages,.xls,.xlsx,.csv,.txt,.json,.xml,.png,.jpg,.jpeg,.gif,.svg"
        disabled={isUploading}
      />

      {/* Upload button */}
      <Button
        variant="outline"
        size="sm"
        onClick={handleUploadClick}
        disabled={isUploading}
      >
        {isUploading ? 'Uploading...' : 'Upload'}
      </Button>

      {/* Status notification */}
      {uploadStatus.type && (
        <div className="absolute top-full right-0 mt-2 w-80 z-50">
          <Alert variant={uploadStatus.type === 'error' ? 'destructive' : 'default'}>
            <AlertDescription className="text-sm">
              {uploadStatus.message}
            </AlertDescription>
          </Alert>
        </div>
      )}
    </div>
  );
}
