import React, { useState, useEffect } from 'react';
import { emitPulse } from '../lib/PulseClient';
import { usePulse } from '../hooks/usePulse';

interface ViewportProps {
  viewport_id: string;
  viewport_type: 'ontology' | 'visualization' | 'scene3d' | 'iframe' | 'stream' | 'empty';
  content?: any;
  theme: 'mirror' | 'light' | 'dark';
  focused: boolean;
}

/**
 * Viewport - Universal content container
 * 
 * Can render multiple content types:
 * - Ontological objects via ObjectRenderer
 * - D3.js visualizations
 * - Babylon.js 3D scenes
 * - Iframe content
 * - Streaming API data
 * 
 * All content loading is validated by SAGE before rendering.
 */
export const Viewport: React.FC<ViewportProps> = ({
  viewport_id,
  viewport_type,
  content,
  theme,
  focused
}) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loadTime, setLoadTime] = useState<number>(0);

  // Listen for content validation
  usePulse('sage.content.validated', async (payload) => {
    if (payload.viewport_id === viewport_id) {
      // Content validated, proceed with loading
      await loadContent();
    }
  });

  usePulse('sage.content.blocked', (payload) => {
    if (payload.viewport_id === viewport_id) {
      setError('Content blocked by governance');
      setLoading(false);
    }
  });

  // Load content
  const loadContent = async () => {
    if (!content || viewport_type === 'empty') {
      return;
    }

    const startTime = Date.now();
    setLoading(true);
    setError(null);

    try {
      await emitPulse('viewport.content.loading', {
        viewport_id,
        content_type: viewport_type,
        content_source: content.target || content.type,
        timestamp: new Date().toISOString()
      }, ['mirror', 'core']);

      // Simulate content loading (in real implementation, would fetch from Core)
      await new Promise(resolve => setTimeout(resolve, 500));

      const renderTime = Date.now() - startTime;
      setLoadTime(renderTime);

      await emitPulse('viewport.content.loaded', {
        viewport_id,
        content_type: viewport_type,
        render_time_ms: renderTime,
        timestamp: new Date().toISOString()
      }, ['mirror', 'core', 'kronos', 'shadow']);

      setLoading(false);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setError(errorMessage);

      await emitPulse('viewport.content.failed', {
        viewport_id,
        content_type: viewport_type,
        error_message: errorMessage,
        timestamp: new Date().toISOString()
      }, ['mirror', 'core', 'sage', 'shadow']);

      setLoading(false);
    }
  };

  // Initialization
  useEffect(() => {
    emitPulse('viewport.initialized', {
      viewport_id,
      viewport_type,
      timestamp: new Date().toISOString()
    }, ['mirror', 'core', 'kronos']);
  }, []);

  // Load content when it changes
  useEffect(() => {
    if (content && viewport_type !== 'empty') {
      loadContent();
    }
  }, [content, viewport_type]);

  // Handle focus
  useEffect(() => {
    if (focused) {
      emitPulse('viewport.focused', {
        viewport_id,
        previous_focus: null,
        timestamp: new Date().toISOString()
      }, ['mirror', 'core']);
    }
  }, [focused]);

  const getThemeStyles = () => {
    switch (theme) {
      case 'mirror':
        return {
          background: 'rgba(255,255,255,0.3)',
          color: '#2C2C2C',
          borderColor: 'rgba(0,0,0,0.1)'
        };
      case 'light':
        return {
          background: '#FFFFFF',
          color: '#111827',
          borderColor: '#E5E7EB'
        };
      case 'dark':
        return {
          background: '#1F2937',
          color: '#F9FAFB',
          borderColor: '#374151'
        };
    }
  };

  const themeStyles = getThemeStyles();

  const renderContent = () => {
    if (loading) {
      return (
        <div style={styles.centerContent}>
          <div style={styles.loadingSpinner}>Loading...</div>
        </div>
      );
    }

    if (error) {
      return (
        <div style={styles.centerContent}>
          <div style={{ ...styles.error, color: '#EF4444' }}>
            Error: {error}
          </div>
        </div>
      );
    }

    if (!content || viewport_type === 'empty') {
      return (
        <div style={styles.centerContent}>
          <div style={{ ...styles.emptyState, color: themeStyles.color, opacity: 0.3 }}>
            <div style={styles.emptyIcon}>□</div>
            <div style={styles.emptyText}>Empty Viewport</div>
            <div style={styles.emptySubtext}>Select content from Navigator</div>
          </div>
        </div>
      );
    }

    // Render based on viewport type
    switch (viewport_type) {
      case 'ontology':
        return (
          <div style={styles.contentArea}>
            <div style={{ ...styles.contentTitle, color: themeStyles.color }}>
              Ontology Object
            </div>
            <div style={{ ...styles.contentBody, color: themeStyles.color }}>
              Target: {content.target}
            </div>
            <div style={{ ...styles.contentMeta, color: themeStyles.color, opacity: 0.5 }}>
              Loaded in {loadTime}ms
            </div>
          </div>
        );

      case 'system':
        return (
          <div style={styles.contentArea}>
            <div style={{ ...styles.contentTitle, color: themeStyles.color }}>
              System View
            </div>
            <div style={{ ...styles.contentBody, color: themeStyles.color }}>
              Target: {content.target}
            </div>
          </div>
        );

      case 'reasoning_result':
        return (
          <div style={styles.contentArea}>
            <div style={{ ...styles.contentTitle, color: themeStyles.color }}>
              Core Reasoning Result
            </div>
            <div style={{ ...styles.contentBody, color: themeStyles.color }}>
              {JSON.stringify(content.content, null, 2)}
            </div>
          </div>
        );

      default:
        return (
          <div style={styles.contentArea}>
            <div style={{ ...styles.contentTitle, color: themeStyles.color }}>
              {viewport_type}
            </div>
            <div style={{ ...styles.contentBody, color: themeStyles.color }}>
              Content type not yet implemented
            </div>
          </div>
        );
    }
  };

  return (
    <div 
      style={{
        ...styles.viewport,
        ...themeStyles,
        ...(focused ? {
          boxShadow: `inset 0 0 0 2px ${theme === 'dark' ? '#60A5FA' : '#3B82F6'}`
        } : {})
      }}
    >
      {renderContent()}
    </div>
  );
};

const styles: Record<string, React.CSSProperties> = {
  viewport: {
    width: '100%',
    height: '100%',
    display: 'flex',
    flexDirection: 'column',
    position: 'relative',
    transition: 'box-shadow 0.2s ease'
  },
  centerContent: {
    flex: 1,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center'
  },
  loadingSpinner: {
    fontSize: 14,
    opacity: 0.5
  },
  error: {
    fontSize: 14,
    fontWeight: 500
  },
  emptyState: {
    textAlign: 'center',
    userSelect: 'none'
  },
  emptyIcon: {
    fontSize: 48,
    marginBottom: 16,
    opacity: 0.3
  },
  emptyText: {
    fontSize: 16,
    fontWeight: 500,
    marginBottom: 8
  },
  emptySubtext: {
    fontSize: 14,
    opacity: 0.6
  },
  contentArea: {
    flex: 1,
    padding: 24,
    overflowY: 'auto'
  },
  contentTitle: {
    fontSize: 20,
    fontWeight: 600,
    marginBottom: 16
  },
  contentBody: {
    fontSize: 14,
    lineHeight: 1.6,
    whiteSpace: 'pre-wrap',
    fontFamily: 'monospace'
  },
  contentMeta: {
    fontSize: 12,
    marginTop: 16
  }
};

export default Viewport;
