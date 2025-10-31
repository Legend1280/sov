/**
 * AppContainer - Root component for an application
 * 
 * Loads and orchestrates the schemas for:
 * - Header (top bar)
 * - Navigator (left sidebar)
 * - Viewports (main content areas)
 * 
 * This is the first-tier container in the three-tier architecture.
 */

import { useEffect, useState } from 'react';
import { MirrorLayoutSchema, ViewportConfig } from '@/types/schema';
import { useDataContext } from '@/core/DataContext';
import Renderer from './Renderer';

interface AppContainerProps {
  appId: string;
  navigatorSchema?: string;
  headerSchema?: string;
  viewports?: ViewportConfig[];
  dataContext?: any;
  eventBus?: any;
}

export function AppContainer({
  appId,
  navigatorSchema,
  headerSchema,
  viewports = [],
}: AppContainerProps) {
  const dataContext = useDataContext();
  const [headerLayout, setHeaderLayout] = useState<MirrorLayoutSchema | null>(null);
  const [navLayout, setNavLayout] = useState<MirrorLayoutSchema | null>(null);
  const [viewportLayouts, setViewportLayouts] = useState<Map<string, MirrorLayoutSchema>>(new Map());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadSchemas = async () => {
      try {
        setLoading(true);
        setError(null);

        // Set active app in context
        dataContext.setActiveApp(appId);

        // Load header schema
        if (headerSchema) {
          const header = await loadSchema(headerSchema);
          setHeaderLayout(header);
        }

        // Load navigator schema
        if (navigatorSchema) {
          const nav = await loadSchema(navigatorSchema);
          setNavLayout(nav);
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
        console.error('[AppContainer] Failed to load schemas:', err);
        setError(err instanceof Error ? err.message : 'Failed to load app schemas');
        setLoading(false);
      }
    };

    loadSchemas();
  }, [appId, headerSchema, navigatorSchema, viewports, dataContext]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="text-lg font-semibold">Loading {appId}...</div>
          <div className="text-sm text-muted-foreground mt-2">Initializing application</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center max-w-md">
          <div className="text-lg font-semibold text-destructive">Failed to load app</div>
          <div className="text-sm text-muted-foreground mt-2">{error}</div>
        </div>
      </div>
    );
  }

  return (
    <div className="app-container h-screen flex flex-col">
      {/* Header */}
      {headerLayout && (
        <header className="app-header">
          <Renderer layout={headerLayout.viewports?.viewport1 || []} />
        </header>
      )}

      <div className="flex-1 flex overflow-hidden">
        {/* Navigator */}
        {navLayout && (
          <aside className="app-navigator">
            <Renderer layout={navLayout.viewports?.viewport1 || []} />
          </aside>
        )}

        {/* Viewports */}
        <main className="flex-1 flex flex-col">
          {Array.from(viewportLayouts.entries()).map(([viewportId, layout]) => (
            <div key={viewportId} className="viewport-container flex-1">
              <Renderer layout={layout.viewports?.viewport1 || []} />
            </div>
          ))}
        </main>
      </div>
    </div>
  );
}

/**
 * Load a schema from Core API or local cache
 * 
 * TODO: Implement proper caching and Core API integration
 * For now, this loads from local JSON files
 */
async function loadSchema(schemaId: string): Promise<MirrorLayoutSchema> {
  try {
    // Try to load from local apps directory first
    const module = await import(`../../apps/${schemaId}.json`);
    return module.default || module;
  } catch (error) {
    // Fallback to Core API
    console.warn(`[AppContainer] Schema "${schemaId}" not found locally, trying Core API...`);
    
    // TODO: Implement Core API fetch
    // const response = await fetch(`/api/layouts/${schemaId}`);
    // return await response.json();
    
    throw new Error(`Schema "${schemaId}" not found`);
  }
}

export default AppContainer;
