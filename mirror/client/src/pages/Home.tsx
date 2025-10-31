/**
 * Home - Main application page
 * 
 * Loads and renders the default application using the AppContainer.
 * 
 * Author: Brady Simmons
 * Copyright: © 2025 Sovereignty Foundation. All rights reserved.
 */

import { useEffect, useState } from 'react';
import { useMirror } from '@/core/MirrorContext';
import Renderer from '@/components/core/Renderer';
import { LayoutNode } from '@/types/schema';

export default function Home() {
  const { appRegistry } = useMirror();
  const [appLayout, setAppLayout] = useState<LayoutNode | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadApp = async () => {
      try {
        setLoading(true);
        setError(null);

        // Wait for app discovery to complete
        await new Promise(resolve => setTimeout(resolve, 100));

        // Try to load Mirror base app
        let app = appRegistry.get('mirror-base');
        
        if (!app) {
          // If not found, try to load it
          try {
            app = await appRegistry.load('mirror-base');
          } catch (loadError) {
            console.warn('[Home] Could not load DexaBooks app:', loadError);
          }
        }

        if (!app) {
          throw new Error('No apps available. Please create an app in /src/apps/');
        }

        // Set as active app
        await appRegistry.setActive(app.id);

        // Create MirrorContainer layout
        const layout: LayoutNode = {
          type: 'MirrorContainer',
          props: {
            appId: app.id,
            headerSchema: app.header,
            navigatorSchema: app.navigator,
            surfaceViewerSchema: app.surfaceViewer,
            viewports: app.viewports || [
              { id: 'viewport1', label: 'Viewport 1', schema: `${app.id}/main`, defaultHeight: 100 }
            ]
          }
        };

        setAppLayout(layout);
        setLoading(false);
      } catch (err) {
        console.error('[Home] Failed to load app:', err);
        setError(err instanceof Error ? err.message : 'Failed to load application');
        setLoading(false);
      }
    };

    loadApp();
  }, [appRegistry]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="text-lg font-semibold">Loading Mirror...</div>
          <div className="text-sm text-muted-foreground mt-2">Initializing application framework</div>
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
          <div className="text-xs text-muted-foreground mt-4">
            Check the console for more details.
          </div>
        </div>
      </div>
    );
  }

  if (!appLayout) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="text-lg font-semibold">No app loaded</div>
        </div>
      </div>
    );
  }

  return <Renderer layout={appLayout} />;
}
