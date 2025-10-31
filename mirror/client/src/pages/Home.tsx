/**
 * Home - Main entry point for Mirror UI
 * 
 * Author: Brady Simmons
 * Copyright: © 2025 Sovereignty Foundation. All rights reserved.
 */

import { useState, useEffect, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { useLayoutStore } from '@/core/LayoutStore';
import { PulseConnectionVisualizer } from '@/components/mirror/PulseConnectionVisualizer';
import { GeometricConnector } from '@/components/visualizations/GeometricConnector';
import { ViewportPulseVisualizer } from '@/components/visualizations/ViewportPulseVisualizer';

export default function Home() {
  const {
    navigatorVisible,
    navigatorWidth,
    surfaceViewerVisible,
    surfaceViewerWidth,
    viewport1Height,
    viewMode,
    focusMode,
    temporalMode,
    toggleNavigator,
    toggleSurfaceViewer,
    toggleFocus,
    resizeNavigator,
    resizeSurfaceViewer,
    resizeViewport,
    setViewMode,
    setTemporalMode,
  } = useLayoutStore();

  // Handle ESC key to exit focus mode
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && focusMode) {
        toggleFocus(focusMode);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [focusMode, toggleFocus]);

  const handleViewportResize = (delta: number) => {
    const container = document.querySelector('main');
    if (!container) return;
    resizeViewport(delta, container.clientHeight);
  };

  return (
    <div className="h-screen flex flex-col bg-background">
      {/* Header */}
      <header className="bg-card border-b border-border px-6 py-3 flex items-center justify-between">
        {/* Logo */}
        <div className="flex items-center flex-1">
          <span className="text-xl font-semibold tracking-tight">Mirror</span>
        </div>

        {/* View Mode Controls */}
        <div className="flex gap-2">
          <Button
            variant="ghost"
            size="sm"
            title="Full View"
            onClick={() => setViewMode('full')}
            className={viewMode === 'full' ? 'bg-secondary' : ''}
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <rect x="3" y="3" width="18" height="18" rx="2" />
            </svg>
          </Button>
          <Button
            variant="ghost"
            size="sm"
            title="Split View"
            onClick={() => setViewMode('split')}
            className={viewMode === 'split' ? 'bg-secondary' : ''}
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <rect x="3" y="3" width="18" height="8" rx="2" />
              <rect x="3" y="13" width="18" height="8" rx="2" />
            </svg>
          </Button>
          <Button
            variant="ghost"
            size="sm"
            title="Left Only"
            onClick={() => setViewMode('left-only')}
            className={viewMode === 'left-only' ? 'bg-secondary' : ''}
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <rect x="3" y="3" width="8" height="18" rx="2" />
            </svg>
          </Button>
        </div>

        {/* Right side - empty for future components */}
        <div className="flex gap-2 flex-1 justify-end">
          {/* Future components can go here */}
        </div>
      </header>

      {/* Main Layout */}
      <div className="flex-1 flex overflow-hidden">
        {/* Navigator */}
        {navigatorVisible ? (
          <>
            <aside
              className="bg-card border-r border-border flex flex-col"
              style={{ width: `${navigatorWidth}px` }}
            >
              <div className="px-6 py-4 border-b border-border flex items-center justify-between">
                <h2 className="text-xs font-semibold text-muted-foreground tracking-wider">NAVIGATOR</h2>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={toggleNavigator}
                  className="h-6 w-6 p-0"
                >
                  ←
                </Button>
              </div>
              <div className="flex-1 overflow-y-auto p-6">
                <p className="text-sm text-muted-foreground">Navigator content</p>
              </div>
            </aside>
            <ResizeHandle direction="vertical" onResize={resizeNavigator} />
          </>
        ) : (
          <button
            onClick={toggleNavigator}
            className="w-10 bg-card border-r border-border flex items-center justify-center hover:bg-secondary"
          >
            →
          </button>
        )}

        {/* Center Viewports */}
        <main className="flex-1 flex flex-col overflow-hidden">
          {focusMode ? (
            <div
              className="flex-1 overflow-auto p-8 bg-background"
              onDoubleClick={() => toggleFocus(focusMode)}
            >
              <h2 className="text-2xl font-bold mb-4">
                {focusMode === 'viewport1' ? 'Viewport 1 (Focus Mode)' : 'Viewport 2 (Focus Mode)'}
              </h2>
              <p className="text-muted-foreground">Double-click to exit focus mode or press ESC</p>
            </div>
          ) : (
            <>
              <div
                className="overflow-auto bg-background"
                style={{ height: `${viewport1Height}%` }}
                onDoubleClick={() => toggleFocus('viewport1')}
              >
                <ViewportPulseVisualizer />
              </div>
              {viewMode === 'split' && (
                <>
                  <ResizeHandle direction="horizontal" onResize={handleViewportResize} />
                  <div
                    className="overflow-auto p-8 bg-background"
                    style={{ height: `${100 - viewport1Height}%` }}
                    onDoubleClick={() => toggleFocus('viewport2')}
                  >
                    <div className="absolute top-2 left-4 text-[10px] text-muted-foreground uppercase tracking-widest font-medium opacity-50 z-10">
                      Viewport 2
                    </div>
                    <PulseConnectionVisualizer />
                  </div>
                </>
              )}
            </>
          )}
        </main>

        {/* Surface Viewer */}
        {surfaceViewerVisible ? (
          <>
            <ResizeHandle direction="vertical" onResize={resizeSurfaceViewer} />
            <aside
              className="bg-card border-l border-border flex flex-col"
              style={{ width: `${surfaceViewerWidth}px` }}
            >
              <div className="px-6 py-4 border-b border-border flex items-center justify-between">
                <h2 className="text-xs font-semibold text-muted-foreground tracking-wider">SIDE VIEWPORT</h2>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={toggleSurfaceViewer}
                  className="h-6 w-6 p-0"
                >
                  ×
                </Button>
              </div>
              <div className="flex-1 overflow-y-auto p-6">
                <p className="text-sm text-muted-foreground">Side viewport content</p>
              </div>
            </aside>
          </>
        ) : (
          <button
            onClick={toggleSurfaceViewer}
            className="w-10 bg-card border-l border-border flex items-center justify-center hover:bg-secondary"
          >
            ←
          </button>
        )}
      </div>
    </div>
  );
}

// Simple ResizeHandle component
function ResizeHandle({ direction, onResize }: { direction: 'horizontal' | 'vertical'; onResize: (delta: number) => void }) {
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
      className="bg-border hover:bg-yellow-500/20 transition-colors"
      style={{
        cursor: direction === 'vertical' ? 'ew-resize' : 'ns-resize',
        ...(direction === 'vertical' ? { width: '4px' } : { height: '4px' }),
      }}
    />
  );
}
