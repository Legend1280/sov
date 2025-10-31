/**
 * ResizablePanel - Draggable resize handle for panels
 * 
 * Author: Brady Simmons
 * Copyright: © 2025 Sovereignty Foundation. All rights reserved.
 */

import { useEffect, useRef } from 'react';

interface ResizablePanelProps {
  direction: 'horizontal' | 'vertical';
  onResize: (delta: number) => void;
  className?: string;
}

export function ResizablePanel({ direction, onResize, className = '' }: ResizablePanelProps) {
  const handleRef = useRef<HTMLDivElement>(null);
  const isResizingRef = useRef(false);
  const startPosRef = useRef(0);

  useEffect(() => {
    const handle = handleRef.current;
    if (!handle) return;

    const handleMouseDown = (e: MouseEvent) => {
      isResizingRef.current = true;
      startPosRef.current = direction === 'vertical' ? e.clientX : e.clientY;
      document.body.style.cursor = direction === 'vertical' ? 'ew-resize' : 'ns-resize';
      document.body.style.userSelect = 'none';
      e.preventDefault();
    };

    const handleMouseMove = (e: MouseEvent) => {
      if (!isResizingRef.current) return;

      const currentPos = direction === 'vertical' ? e.clientX : e.clientY;
      const delta = currentPos - startPosRef.current;
      
      onResize(delta);
      startPosRef.current = currentPos;
    };

    const handleMouseUp = () => {
      if (isResizingRef.current) {
        isResizingRef.current = false;
        document.body.style.cursor = '';
        document.body.style.userSelect = '';
      }
    };

    handle.addEventListener('mousedown', handleMouseDown);
    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);

    return () => {
      handle.removeEventListener('mousedown', handleMouseDown);
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [direction, onResize]);

  return (
    <div
      ref={handleRef}
      className={`resize-handle ${direction} ${className}`}
      style={{
        background: 'rgba(42, 42, 42, 0.5)',
        position: 'relative',
        zIndex: 100,
        transition: 'all 0.15s cubic-bezier(0.25, 0.1, 0.25, 1)',
        cursor: direction === 'vertical' ? 'ew-resize' : 'ns-resize',
        ...(direction === 'vertical' ? {
          width: '8px',
          flexShrink: 0,
        } : {
          height: '8px',
          margin: 0,
        }),
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.background = 'rgba(250, 214, 67, 0.1)';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.background = 'rgba(42, 42, 42, 0.5)';
      }}
    />
  );
}

export default ResizablePanel;
