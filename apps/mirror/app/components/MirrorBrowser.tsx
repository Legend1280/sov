import React, { useState, useEffect } from 'react';
import { ObjectRendererWeb as ObjectRenderer } from './ObjectRendererWeb';
import { usePulse } from '../hooks/usePulse';
import { emitPulse } from '../lib/PulseClient';

interface MirrorBrowserProps {
  theme?: 'mirror' | 'light' | 'dark';
  layout?: {
    navigatorWidth?: number;
    surfaceWidth?: number;
    viewportSplit?: number;
  };
}

/**
 * MirrorBrowser - Sovereignty-native semantic browser
 * 
 * This is the root component that instantiates the entire browser
 * as a semantic object. Every child component is also a semantic object
 * rendered via ObjectRenderer.
 * 
 * Architecture:
 * - Ontology-first: All components defined in Core ontology
 * - Pulse-native: All communication via PulseBus
 * - Governed: All actions validated by SAGE
 * - Observable: Participates in recursive stability loop
 */
export const MirrorBrowser: React.FC<MirrorBrowserProps> = ({
  theme = 'mirror',
  layout = {}
}) => {
  const {
    navigatorWidth = 192,
    surfaceWidth = 384,
    viewportSplit = 0.5
  } = layout;

  // State
  const [initialized, setInitialized] = useState(false);
  const [currentTheme, setCurrentTheme] = useState(theme);
  const [navigatorCollapsed, setNavigatorCollapsed] = useState(false);
  const [surfaceCollapsed, setSurfaceCollapsed] = useState(false);
  const [activeViewport, setActiveViewport] = useState<'viewport1' | 'viewport2'>('viewport1');
  const [viewport1Content, setViewport1Content] = useState<any>(null);
  const [viewport2Content, setViewport2Content] = useState<any>(null);
  const [surfaceContent, setSurfaceContent] = useState<any>(null);

  // Listen for theme changes from Navigator
  usePulse('navigator.theme.changed', (payload) => {
    setCurrentTheme(payload.new_theme);
    emitPulse('mirror.theme.changed', {
      previous_theme: payload.previous_theme,
      new_theme: payload.new_theme,
      timestamp: new Date().toISOString()
    }, ['core', 'kronos']);
  });

  // Listen for navigation events
  usePulse('navigator.item.selected', (payload) => {
    // Load content based on navigation target
    if (payload.target.startsWith('ontology.')) {
      // Load ontology content in viewport
      setViewport1Content({
        type: 'ontology',
        target: payload.target
      });
    } else if (payload.target.startsWith('system.')) {
      // Load system content
      setViewport1Content({
        type: 'system',
        target: payload.target
      });
    }
  });

  // Listen for viewport interactions
  usePulse('viewport.interaction', (payload) => {
    // Update surface with selected object details
    if (payload.interaction_type === 'object_selected') {
      setSurfaceContent({
        type: 'object_details',
        object_id: payload.interaction_data.object_id
      });
    }
  });

  // Listen for Core responses
  usePulse('core.reasoning.complete', (payload) => {
    // Update viewport with Core response
    if (activeViewport === 'viewport1') {
      setViewport1Content({
        type: 'reasoning_result',
        content: payload
      });
    } else {
      setViewport2Content({
        type: 'reasoning_result',
        content: payload
      });
    }
  });

  // Listen for SAGE validation results
  usePulse('sage.validation.failed', (payload) => {
    console.error('SAGE validation failed:', payload);
    // Show error in UI
  });

  // Initialization
  useEffect(() => {
    const initialize = async () => {
      // Emit initialization event
      await emitPulse('mirror.initialized', {
        theme: currentTheme,
        layout: { navigatorWidth, surfaceWidth, viewportSplit },
        timestamp: new Date().toISOString()
      }, ['core', 'sage', 'kronos', 'shadow']);

      setInitialized(true);
    };

    initialize();

    // Cleanup on unmount
    return () => {
      emitPulse('mirror.shutdown', {
        timestamp: new Date().toISOString()
      }, ['core', 'kronos', 'shadow']);
    };
  }, []);

  // Calculate layout dimensions
  const contentWidth = typeof window !== 'undefined' ? window.innerWidth : 1920;
  const contentHeight = typeof window !== 'undefined' ? window.innerHeight : 1080;
  
  const actualNavigatorWidth = navigatorCollapsed ? 0 : navigatorWidth;
  const actualSurfaceWidth = surfaceCollapsed ? 0 : surfaceWidth;
  const viewportsWidth = contentWidth - actualNavigatorWidth - actualSurfaceWidth;
  const viewport1Width = viewportsWidth * viewportSplit;
  const viewport2Width = viewportsWidth * (1 - viewportSplit);

  if (!initialized) {
    return (
      <div className="mirror-loading" style={styles.loading}>
        <div style={styles.loadingText}>Initializing Mirror...</div>
      </div>
    );
  }

  return (
    <div 
      className={`mirror-browser theme-${currentTheme}`}
      style={{
        ...styles.browser,
        ...(currentTheme === 'mirror' ? styles.themeMirror : {}),
        ...(currentTheme === 'light' ? styles.themeLight : {}),
        ...(currentTheme === 'dark' ? styles.themeDark : {})
      }}
    >
      {/* Header */}
      <div style={styles.header}>
        <div style={styles.headerTitle}>Mirror</div>
        <div style={styles.headerSubtitle}>Sovereignty Stack Browser</div>
      </div>

      {/* Main content area */}
      <div style={styles.content}>
        {/* Navigator */}
        {!navigatorCollapsed && (
          <div style={{ ...styles.navigator, width: navigatorWidth }}>
            <ObjectRenderer 
              object="navigator"
              props={{
                width: navigatorWidth,
                collapsed: false,
                theme: currentTheme
              }}
            />
          </div>
        )}

        {/* Viewports */}
        <div style={styles.viewports}>
          {/* Viewport 1 */}
          <div 
            style={{ 
              ...styles.viewport,
              width: viewport1Width,
              borderRight: '1px solid rgba(0,0,0,0.1)'
            }}
            onClick={() => setActiveViewport('viewport1')}
          >
            <div style={styles.viewportLabel}>Viewport 1</div>
            <ObjectRenderer 
              object="viewport"
              props={{
                viewport_id: 'viewport1',
                viewport_type: viewport1Content?.type || 'empty',
                content: viewport1Content,
                theme: currentTheme,
                focused: activeViewport === 'viewport1'
              }}
            />
          </div>

          {/* Viewport 2 */}
          <div 
            style={{ 
              ...styles.viewport,
              width: viewport2Width
            }}
            onClick={() => setActiveViewport('viewport2')}
          >
            <div style={styles.viewportLabel}>Viewport 2</div>
            <ObjectRenderer 
              object="viewport"
              props={{
                viewport_id: 'viewport2',
                viewport_type: viewport2Content?.type || 'empty',
                content: viewport2Content,
                theme: currentTheme,
                focused: activeViewport === 'viewport2'
              }}
            />
          </div>
        </div>

        {/* Surface Viewer */}
        {!surfaceCollapsed && (
          <div style={{ ...styles.surface, width: surfaceWidth }}>
            <ObjectRenderer 
              object="surface"
              props={{
                width: surfaceWidth,
                active_tab: 'ontology',
                content: surfaceContent,
                theme: currentTheme
              }}
            />
          </div>
        )}
      </div>
    </div>
  );
};

// Inline styles for initial implementation
const styles: Record<string, React.CSSProperties> = {
  browser: {
    width: '100vw',
    height: '100vh',
    display: 'flex',
    flexDirection: 'column',
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    overflow: 'hidden'
  },
  themeMirror: {
    background: 'linear-gradient(135deg, #E8E8E8 0%, #C0C0C0 100%)',
    color: '#2C2C2C'
  },
  themeLight: {
    background: '#FFFFFF',
    color: '#111827'
  },
  themeDark: {
    background: '#111827',
    color: '#F9FAFB'
  },
  header: {
    height: 64,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '0 24px',
    borderBottom: '1px solid rgba(0,0,0,0.1)',
    background: 'rgba(255,255,255,0.8)',
    backdropFilter: 'blur(10px)'
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 600,
    letterSpacing: '-0.5px'
  },
  headerSubtitle: {
    fontSize: 14,
    opacity: 0.6
  },
  content: {
    flex: 1,
    display: 'flex',
    overflow: 'hidden'
  },
  navigator: {
    borderRight: '1px solid rgba(0,0,0,0.1)',
    background: 'rgba(255,255,255,0.5)',
    backdropFilter: 'blur(10px)',
    overflowY: 'auto'
  },
  viewports: {
    flex: 1,
    display: 'flex',
    overflow: 'hidden'
  },
  viewport: {
    position: 'relative',
    display: 'flex',
    flexDirection: 'column',
    background: 'rgba(255,255,255,0.3)',
    overflow: 'hidden'
  },
  viewportLabel: {
    position: 'absolute',
    top: 8,
    left: 8,
    fontSize: 11,
    fontWeight: 600,
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
    opacity: 0.4,
    pointerEvents: 'none',
    zIndex: 10
  },
  surface: {
    borderLeft: '1px solid rgba(0,0,0,0.1)',
    background: 'rgba(255,255,255,0.5)',
    backdropFilter: 'blur(10px)',
    overflowY: 'auto'
  },
  loading: {
    width: '100vw',
    height: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    background: 'linear-gradient(135deg, #E8E8E8 0%, #C0C0C0 100%)'
  },
  loadingText: {
    fontSize: 18,
    fontWeight: 500,
    color: '#2C2C2C',
    opacity: 0.6
  }
};

export default MirrorBrowser;
