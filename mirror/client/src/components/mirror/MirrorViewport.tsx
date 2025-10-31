/**
 * MirrorViewport - Schema-driven viewport container
 * 
 * Displays a content viewport with optional label, focus mode, and resize capabilities.
 * Supports double-click to focus and escape to exit focus mode.
 * 
 * Author: Brady Simmons
 * Copyright: © 2025 Sovereignty Foundation. All rights reserved.
 */

import { useState, useEffect } from 'react';
import { useMirror } from '@/core/MirrorContext';

export interface MirrorViewportProps {
  id: string;
  label?: string;
  content?: React.ReactNode;
  focusable?: boolean;
  resizable?: boolean;
  height?: number | string;
  showLabel?: boolean;
  children?: React.ReactNode;
}

export function MirrorViewport({
  id,
  label,
  content,
  focusable = true,
  resizable = true,
  height = '50%',
  showLabel = true,
  children,
}: MirrorViewportProps) {
  const [focused, setFocused] = useState(false);
  const { eventBus } = useMirror();

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && focused) {
        setFocused(false);
        eventBus.emit('viewport:unfocus', { viewportId: id });
      }
    };

    if (focused) {
      window.addEventListener('keydown', handleKeyDown);
    }

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [focused, id, eventBus]);

  const handleDoubleClick = () => {
    if (focusable) {
      setFocused(!focused);
      eventBus.emit(focused ? 'viewport:unfocus' : 'viewport:focus', { viewportId: id });
    }
  };

  const heightStyle = typeof height === 'number' ? `${height}%` : height;

  return (
    <div
      className={`overflow-hidden relative ${focused ? 'fixed inset-0 z-50' : ''}`}
      style={focused ? {} : { height: heightStyle }}
      onDoubleClick={handleDoubleClick}
    >
      {showLabel && label && (
        <div className="absolute top-2 left-4 text-[10px] text-muted-foreground uppercase tracking-widest font-medium opacity-50 z-10">
          {label}
        </div>
      )}
      
      <div className="h-full w-full">
        {content || children}
      </div>

      {focused && (
        <div className="absolute top-4 right-4 text-xs text-muted-foreground bg-card/80 backdrop-blur-sm px-3 py-1.5 rounded-md border border-border">
          Press <kbd className="px-1.5 py-0.5 bg-secondary rounded text-[10px] font-mono">ESC</kbd> to exit focus mode
        </div>
      )}
    </div>
  );
}

export default MirrorViewport;
