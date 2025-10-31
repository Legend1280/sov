/**
 * MirrorContainer - Complete Mirror interface container with layout management
 * 
 * Renders the full Mirror interface with header, navigator, viewports, and surface viewer.
 * Implements resize, focus mode, and collapsible panels.
 * 
 * Author: Brady Simmons
 * Copyright: © 2025 Sovereignty Foundation. All rights reserved.
 */

import { useState, useEffect } from 'react';
import { useMirror } from '@/core/MirrorContext';
import { useLayoutStore } from '@/core/LayoutStore';
import Renderer from '@/components/core/Renderer';
import { MirrorLayoutSchema } from '@/types/schema';
import ResizablePanel from './ResizablePanel';
import { Button } from '@/components/ui/button';

export interface MirrorContainerProps {
  appId: string;
  headerSchema?: string;
  navigatorSchema?: string;
  surfaceViewerSchema?: string;
  viewports?: Array<{
    id: string;
    label?: string;
    schema: string;
    defaultHeight?: number;
  }>;
}

export function MirrorContainer({
  appId,
  headerSchema,
  navigatorSchema,
  surfaceViewerSchema,
  viewports = [],
}: MirrorContainerProps) {
  const { appRegistry } = useMirror();
  const [headerLayout, setHeaderLayout] = useState<MirrorLayoutSchema | null>(null);
  const [navLayout, setNavLayout] = useState<MirrorLayoutSchema | null>(null);
  const [surfaceLayout, setSurfaceLayout] = useState<MirrorLayoutSchema | null>(null);
  const [viewportLayouts, setViewportLayouts] = useState<Map<string, MirrorLayoutSchema>>(new Map());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Layout state from Zustand
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

  // Load all schemas
  useEffect(() => {
    const loadSchemas = async () => {
      try {
        setLoading(true);

        const schemas = import.meta.glob('/src/apps/**/*.json');

        const loadSchema = async (schemaPath: string): Promise<MirrorLayoutSchema> => {
          const fullPath = `/src/apps/${schemaPath}.json`;
          const loader = schemas[fullPath];
          
          if (!loader) {
            throw new Error(`Schema '${schemaPath}' not found`);
          }

          const module = await loader() as { default: MirrorLayoutSchema };
          return module.default;
        };

        // Load header
        if (headerSchema) {
          const header = await loadSchema(headerSchema);
          setHeaderLayout(header);
        }

        // Load navigator
        if (navigatorSchema) {
          const nav = await loadSchema(navigatorSchema);
          setNavLayout(nav);
        }

        // Load surface viewer
        if (surfaceViewerSchema) {
          const surface = await loadSchema(surfaceViewerSchema);
          setSurfaceLayout(surface);
        }

        // Load viewport schemas
        const viewportLayoutMap = new Map<MirrorLayoutSchema>();
        for (const viewport of viewports) {
          const layout = await loadSchema(viewport.schema);
          viewportLayoutMap.set(viewport.id, layout);
        }
        setViewportLayouts(viewportLayoutMap);

        setLoading(false);
      } catch (err) {
        console.error('[MirrorContainer] Failed to load schemas:', err);
        setError(err instanceof Error ? err.message : 'Failed to load Mirror schemas');
        setLoading(false);
      }
    };

    loadSchemas();
  }, [appId, headerSchema, navigatorSchema, surfaceViewerSchema, viewports]);

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

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="text-lg font-semibold">Loading Mirror...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center max-w-md">
          <div className="text-lg font-semibold text-destructive">Failed to load Mirror</div>
          <div className="text-sm text-muted-foreground mt-2">{error}</div>
        </div>
      </div>
    );
  }

  // Render the full Mirror layout
  return (
    <div className="h-screen flex flex-col bg-background">
      {/* Header */}
      <header className="bg-card border-b border-border px-6 py-4 flex items-center justify-between shadow-sm">
        <div className="flex-1" />
        
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

        {/* Logo */}
        <div className="flex items-center gap-2">
          <span className="text-xl font-semibold tracking-tight">Mirror</span>
        </div>

        {/* Temporal Controls */}
        <div className="flex gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setTemporalMode('past')}
            className={temporalMode === 'past' ? 'bg-secondary' : ''}
          >
            Past
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setTemporalMode('present')}
            className={temporalMode === 'present' ? 'bg-secondary' : ''}
          >
            Present
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setTemporalMode('future')}
            className={temporalMode === 'future' ? 'bg-secondary' : ''}
          >
            Future
          </Button>
          <Button variant="default" size="sm">
            Upload
          </Button>
        </div>
      </header>

      {/* Main Layout */}
      <div className="flex-1 flex overflow-hidden">
        {/* Navigator */}
        {navigatorVisible ? (
          <>
            <aside
              className="bg-card border-r border-border flex flex-col transition-all duration-300"
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
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                  </svg>
                </Button>
              </div>
              <div className="flex-1 overflow-y-auto p-6">
                {navLayout && navLayout.viewports && navLayout.viewports.navigator && navLayout.viewports.navigator[0] && (
                  <Renderer layout={navLayout.viewports.navigator[0]} />
                )}
              </div>
            </aside>
            <ResizablePanel direction="vertical" onResize={resizeNavigator} />
          </>
        ) : (
          <button
            onClick={toggleNavigator}
            className="w-10 bg-card border-r border-border flex items-center justify-center hover:bg-secondary transition-all duration-200"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </button>
        )}

        {/* Center Viewports */}
        <main className="flex-1 flex flex-col overflow-hidden">
          {focusMode ? (
            <div
              className="flex-1 overflow-hidden"
              onDoubleClick={() => toggleFocus(focusMode)}
            >
              {focusMode === 'viewport1' && viewportLayouts.get(viewports[0]?.id) && (
                <Renderer layout={viewportLayouts.get(viewports[0].id)!.viewports.viewport1[0]} />
              )}
              {focusMode === 'viewport2' && viewportLayouts.get(viewports[1]?.id) && (
                <Renderer layout={viewportLayouts.get(viewports[1].id)!.viewports.viewport1[0]} />
              )}
            </div>
          ) : (
            <>
              <div
                className="overflow-hidden relative"
                style={{ height: `${viewport1Height}%` }}
                onDoubleClick={() => toggleFocus('viewport1')}
              >
                <div className="absolute top-2 left-4 text-[10px] text-muted-foreground uppercase tracking-widest font-medium opacity-50 z-10">
                  Viewport 1
                </div>
                {viewportLayouts.get(viewports[0]?.id) && viewportLayouts.get(viewports[0].id)!.viewports.viewport1 && (
                  <Renderer layout={viewportLayouts.get(viewports[0].id)!.viewports.viewport1[0]} />
                )}
              </div>
              {viewMode === 'split' && (
                <>
                  <ResizablePanel direction="horizontal" onResize={handleViewportResize} />
                  <div
                    className="overflow-hidden relative"
                    style={{ height: `${100 - viewport1Height}%` }}
                    onDoubleClick={() => toggleFocus('viewport2')}
                  >
                    <div className="absolute top-2 left-4 text-[10px] text-muted-foreground uppercase tracking-widest font-medium opacity-50 z-10">
                      Viewport 2
                    </div>
                    {viewportLayouts.get(viewports[1]?.id) && viewportLayouts.get(viewports[1].id)!.viewports.viewport1 && (
                      <Renderer layout={viewportLayouts.get(viewports[1].id)!.viewports.viewport1[0]} />
                    )}
                  </div>
                </>
              )}
            </>
          )}
        </main>

        {/* Surface Viewer */}
        {surfaceViewerVisible ? (
          <>
            <ResizablePanel direction="vertical" onResize={resizeSurfaceViewer} />
            <aside
              className="bg-card border-l border-border flex flex-col transition-all duration-300"
              style={{ width: `${surfaceViewerWidth}px` }}
            >
              <div className="px-6 py-4 border-b border-border flex items-center justify-between">
                <h2 className="text-xs font-semibold text-muted-foreground tracking-wider">SURFACE VIEWER</h2>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={toggleSurfaceViewer}
                  className="h-6 w-6 p-0"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </Button>
              </div>
              <div className="flex-1 overflow-y-auto">
                {surfaceLayout && surfaceLayout.viewports && surfaceLayout.viewports.surfaceViewer && surfaceLayout.viewports.surfaceViewer[0] && (
                  <Renderer layout={surfaceLayout.viewports.surfaceViewer[0]} />
                )}
              </div>
            </aside>
          </>
        ) : (
          <button
            onClick={toggleSurfaceViewer}
            className="w-10 bg-card border-l border-border flex items-center justify-center hover:bg-secondary transition-all duration-200"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
        )}
      </div>
    </div>
  );
}

export default MirrorContainer;
