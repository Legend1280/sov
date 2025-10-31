/**
 * MirrorContainer - Complete Mirror interface container
 * 
 * Renders the full Mirror interface with header, navigator, viewports, and surface viewer.
 * Uses schema-driven components for all UI elements.
 * 
 * Author: Brady Simmons
 * Copyright: © 2025 Sovereignty Foundation. All rights reserved.
 */

import { useState, useEffect } from 'react';
import { useMirror } from '@/core/MirrorContext';
import Renderer from '@/components/core/Renderer';
import { MirrorLayoutSchema } from '@/types/schema';
import MirrorHeader from './MirrorHeader';
import MirrorNavigator, { NavigatorSection } from './MirrorNavigator';
import MirrorViewport from './MirrorViewport';
import MirrorSurfaceViewer from './MirrorSurfaceViewer';
import ResizablePanel from './ResizablePanel';

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
        const viewportLayoutMap = new Map<string, MirrorLayoutSchema>();
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
      {headerLayout && (
        <Renderer layout={headerLayout.viewports.header[0]} />
      )}

      {/* Main Layout */}
      <div className="flex-1 flex overflow-hidden">
        {/* Navigator */}
        {navLayout && (
          <>
            <Renderer layout={navLayout.viewports.navigator[0]} />
            <ResizablePanel direction="vertical" />
          </>
        )}

        {/* Center Viewports */}
        <main className="flex-1 flex flex-col overflow-hidden">
          {viewports.map((viewport, index) => {
            const layout = viewportLayouts.get(viewport.id);
            if (!layout) return null;

            return (
              <div key={viewport.id} className="flex-1 overflow-hidden">
                <MirrorViewport
                  id={viewport.id}
                  label={viewport.label}
                  height={viewport.defaultHeight}
                >
                  {layout.viewports && layout.viewports.viewport1 && layout.viewports.viewport1[0] && (
                    <Renderer layout={layout.viewports.viewport1[0]} />
                  )}
                </MirrorViewport>
                {index < viewports.length - 1 && <ResizablePanel direction="horizontal" />}
              </div>
            );
          })}
        </main>

        {/* Surface Viewer */}
        {surfaceLayout && (
          <>
            <ResizablePanel direction="vertical" />
            <Renderer layout={surfaceLayout.viewports.surfaceViewer[0]} />
          </>
        )}
      </div>
    </div>
  );
}

export default MirrorContainer;
