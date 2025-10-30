import { ReactNode, useEffect, useState } from 'react';
import { Button } from '@/components/ui/button';
import SurfaceViewer from './SurfaceViewer';
import ResizeHandle from './ResizeHandle';
import UploadHandler from './UploadHandler';
import { useLayoutStore } from '../core/LayoutManager';
import { useThemeStore } from '../themes/ThemeManager';
import { moduleRegistry } from '../core/ModuleRegistry';

interface MirrorLayoutProps {
  viewport1?: ReactNode;
  viewport2?: ReactNode;
  selectedObject?: any;
  onObjectSelect?: (obj: any) => void;
}

export default function MirrorLayout({ viewport1, viewport2, selectedObject, onObjectSelect }: MirrorLayoutProps) {
  // State for uploaded objects
  const [uploadedObject, setUploadedObject] = useState<any>(null);

  // Use centralized layout state from LayoutManager
  const {
    navigatorVisible,
    surfaceViewerVisible,
    navigatorWidth,
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
  
  // Use theme state
  const { activeThemeId, setTheme, getAllThemes } = useThemeStore();

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

  // Get active module for Navigator sources
  const activeModule = moduleRegistry.getActive();
  const navigatorSources = activeModule?.navigatorSources || [];

  return (
    <div className="h-screen flex flex-col bg-background">
      {/* Header */}
      <header className="bg-card border-b border-border px-6 py-4 flex items-center justify-between shadow-refined relative">
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

        {/* Temporal Controls + Upload */}
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
          <UploadHandler 
            onComplete={(response) => {
              console.log('Upload complete:', response);
              // Store uploaded object for display in Viewport 2
              setUploadedObject({
                id: response.object_id,
                type: response.ontology_type,
                timestamp: new Date().toISOString(),
                provenance_id: response.provenance_id,
              });
              // Optionally trigger SurfaceViewer to open
              if (!surfaceViewerVisible) {
                toggleSurfaceViewer();
              }
            }}
            onError={(error) => {
              console.error('Upload error:', error);
            }}
          />
        </div>
      </header>

      {/* Main Layout */}
      <div className="flex-1 flex overflow-hidden">
        {/* Navigator */}
        {navigatorVisible ? (
          <>
            <aside
              className="bg-card border-r border-border flex flex-col transition-all duration-300 shadow-refined"
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
                {/* THEMES Section */}
                <div className="space-y-3 mb-8">
                  <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-3">THEMES</h3>
                  {getAllThemes().map((theme: any) => (
                    <button
                      key={theme.id}
                      onClick={() => setTheme(theme.id as any)}
                      className={`w-full text-left px-4 py-2.5 rounded-lg text-sm transition-all duration-200 flex items-center justify-between ${
                        activeThemeId === theme.id
                          ? 'bg-primary text-primary-foreground'
                          : 'text-foreground hover:bg-secondary'
                      }`}
                    >
                      <div>
                        <div className="font-medium">{theme.name}</div>
                        <div className="text-xs opacity-70 mt-0.5">{theme.description}</div>
                      </div>
                      {activeThemeId === theme.id && (
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                        </svg>
                      )}
                    </button>
                  ))}
                </div>
                
                {/* FINANCIAL Section */}
                <div className="space-y-3">
                  <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-3">FINANCIAL</h3>
                  {navigatorSources.map((source: any) => (
                    <button
                      key={source.id}
                      className="w-full text-left px-4 py-2.5 rounded-lg text-sm text-foreground hover:bg-secondary transition-all duration-200 flex items-center justify-between"
                    >
                      <span>{source.label}</span>
                      {source.badge && (
                        <span className="text-xs bg-destructive text-destructive-foreground px-2 py-0.5 rounded-full font-medium">
                          {source.badge}
                        </span>
                      )}
                    </button>
                  ))}
                </div>
              </div>
            </aside>
            <ResizeHandle direction="vertical" onResize={resizeNavigator} />
          </>
        ) : (
          <button
            onClick={toggleNavigator}
            className="w-10 bg-card border-r border-border flex items-center justify-center hover:bg-secondary transition-all duration-200 shadow-refined"
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
              {focusMode === 'viewport1' ? viewport1 : viewport2}
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
                {viewport1}
              </div>
              <ResizeHandle direction="horizontal" onResize={handleViewportResize} />
              <div
                className="overflow-hidden relative"
                style={{ height: `${100 - viewport1Height}%` }}
                onDoubleClick={() => toggleFocus('viewport2')}
              >
                <div className="absolute top-2 left-4 text-[10px] text-muted-foreground uppercase tracking-widest font-medium opacity-50 z-10">
                  Viewport 2
                </div>
                {viewport2}
              </div>
            </>
          )}
        </main>

        {/* Surface Viewer */}
        {surfaceViewerVisible ? (
          <>
            <ResizeHandle direction="vertical" onResize={resizeSurfaceViewer} />
            <aside
              className="bg-card border-l border-border flex flex-col transition-all duration-300 shadow-refined-md"
              style={{ width: `${surfaceViewerWidth}px` }}
              onDoubleClick={toggleSurfaceViewer}
            >
              <SurfaceViewer
                selectedObject={selectedObject}
                onClose={toggleSurfaceViewer}
              />
            </aside>
          </>
        ) : (
          <button
            onClick={toggleSurfaceViewer}
            className="w-10 bg-card border-l border-border flex items-center justify-center hover:bg-secondary transition-all duration-200 shadow-refined"
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
