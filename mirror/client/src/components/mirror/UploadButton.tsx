/**
 * UploadButton - Schema-driven upload button wrapper
 * 
 * Wraps the existing UploadHandler component to make it schema-compatible.
 * Provides file upload functionality with success/error handling.
 * 
 * Author: Brady Simmons
 * Copyright: © 2025 Sovereignty Foundation. All rights reserved.
 */

import UploadHandler from '@/components/UploadHandler';
import { useMirror } from '@/core/MirrorContext';

export interface UploadButtonProps {
  onComplete?: (response: any) => void;
  onError?: (error: any) => void;
  label?: string;
  variant?: 'default' | 'outline' | 'ghost';
}

export function UploadButton({
  onComplete,
  onError,
  label = 'Upload',
  variant = 'default',
}: UploadButtonProps) {
  const { eventBus } = useMirror();

  const handleComplete = (response: any) => {
    if (onComplete) {
      onComplete(response);
    } else {
      eventBus.emit('upload:complete', { response });
    }
  };

  const handleError = (error: any) => {
    if (onError) {
      onError(error);
    } else {
      eventBus.emit('upload:error', { error });
    }
  };

  return (
    <UploadHandler
      onComplete={handleComplete}
      onError={handleError}
    />
  );
}

export default UploadButton;
