/**
 * ResizablePanel - Schema-driven resizable panel wrapper
 * 
 * Wraps the existing ResizeHandle component to make it schema-compatible.
 * Provides horizontal and vertical resize capabilities.
 * 
 * Author: Brady Simmons
 * Copyright: © 2025 Sovereignty Foundation. All rights reserved.
 */

import ResizeHandle from '@/components/ResizeHandle';
import { useMirror } from '@/core/MirrorContext';

export interface ResizablePanelProps {
  direction?: 'horizontal' | 'vertical';
  onResize?: (delta: number) => void;
}

export function ResizablePanel({
  direction = 'horizontal',
  onResize,
}: ResizablePanelProps) {
  const { eventBus } = useMirror();

  const handleResize = (delta: number) => {
    if (onResize) {
      onResize(delta);
    } else {
      eventBus.emit('panel:resize', { direction, delta });
    }
  };

  return <ResizeHandle direction={direction} onResize={handleResize} />;
}

export default ResizablePanel;
