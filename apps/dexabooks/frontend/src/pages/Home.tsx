import { useEffect, useState } from 'react';
import MirrorLayout from '../components/MirrorLayout';
import { moduleRegistry } from '../core/ModuleRegistry';
import { ViewportManager } from '../core/ViewportManager';
import ViewportPlaceholder from '../components/ViewportPlaceholder';
import '../modules/dexabooks/register'; // Auto-register DexaBooks components

export default function Home() {
  const [moduleLoaded, setModuleLoaded] = useState(false);
  const [selectedObject, setSelectedObject] = useState<any>(null);

  useEffect(() => {
    // Load DexaBooks module
    const loadModule = async () => {
      try {
        await moduleRegistry.load('dexabooks');
        moduleRegistry.setActive('dexabooks');
        setModuleLoaded(true);
        console.log('[Home] DexaBooks module loaded');
      } catch (error) {
        console.error('[Home] Failed to load module:', error);
      }
    };

    loadModule();
  }, []);

  if (!moduleLoaded) {
    return (
      <div className="flex items-center justify-center h-screen bg-background text-foreground">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-xl font-medium">Loading Mirror Framework...</p>
          <p className="text-sm text-muted-foreground mt-2">Initializing DexaBooks module</p>
        </div>
      </div>
    );
  }

  const activeModule = moduleRegistry.getActive();
  if (!activeModule) {
    return (
      <div className="flex items-center justify-center h-screen bg-background text-destructive">
        <div className="text-center">
          <p className="text-xl font-semibold">No Active Module</p>
          <p className="text-sm">Failed to load module configuration</p>
        </div>
      </div>
    );
  }

  // Use placeholders for now (will support dynamic content types later)
  const viewport1 = <ViewportPlaceholder label="Viewport 1" />;
  const viewport2 = <ViewportPlaceholder label="Viewport 2" />;

  return (
    <MirrorLayout
      viewport1={viewport1}
      viewport2={viewport2}
      selectedObject={selectedObject}
      onObjectSelect={setSelectedObject}
    />
  );
}
