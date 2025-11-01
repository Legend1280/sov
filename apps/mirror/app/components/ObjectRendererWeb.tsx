import React, { useState, useEffect } from 'react';
import { emitPulse } from '../lib/PulseClient';
import Navigator from './Navigator';
import Viewport from './Viewport';
import SurfaceViewer from './SurfaceViewer';

interface ObjectRendererProps {
  object: string;
  props?: Record<string, any>;
}

/**
 * ObjectRendererWeb - Web-compatible version of ObjectRenderer
 * 
 * Resolves ontological objects and renders them as React components.
 * This is the bridge between semantic definitions and visual instantiation.
 */
export const ObjectRendererWeb: React.FC<ObjectRendererProps> = ({
  object,
  props = {}
}) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [Component, setComponent] = useState<React.ComponentType<any> | null>(null);

  useEffect(() => {
    const loadObject = async () => {
      try {
        setLoading(true);

        // Emit loading event
        await emitPulse('mirror.object.loading', {
          object_id: object,
          object_type: 'component',
          timestamp: new Date().toISOString()
        }, ['core', 'kronos']);

        // Map object IDs to components
        const componentMap: Record<string, React.ComponentType<any>> = {
          'navigator': Navigator,
          'viewport': Viewport,
          'surface': SurfaceViewer
        };

        const resolvedComponent = componentMap[object];

        if (!resolvedComponent) {
          throw new Error(`Component not found for object: ${object}`);
        }

        setComponent(() => resolvedComponent);

        // Emit rendered event
        await emitPulse('mirror.object.rendered', {
          object_id: object,
          object_type: 'component',
          component_path: object,
          render_time_ms: 0,
          timestamp: new Date().toISOString()
        }, ['core', 'sage', 'kronos', 'shadow']);

        setLoading(false);
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Unknown error';
        setError(errorMessage);
        setLoading(false);

        await emitPulse('mirror.object.failed', {
          object_id: object,
          error_message: errorMessage,
          timestamp: new Date().toISOString()
        }, ['core', 'sage', 'shadow']);
      }
    };

    loadObject();

    // Cleanup
    return () => {
      emitPulse('mirror.object.unmounted', {
        object_id: object,
        object_type: 'component',
        lifetime_ms: 0,
        timestamp: new Date().toISOString()
      }, ['core', 'kronos', 'shadow']);
    };
  }, [object]);

  if (loading) {
    return <div style={styles.loading}>Loading {object}...</div>;
  }

  if (error) {
    return <div style={styles.error}>Error: {error}</div>;
  }

  if (!Component) {
    return <div style={styles.error}>Component not found: {object}</div>;
  }

  return <Component {...props} />;
};

const styles: Record<string, React.CSSProperties> = {
  loading: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 24,
    fontSize: 14,
    opacity: 0.6
  },
  error: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 24,
    fontSize: 14,
    color: '#EF4444'
  }
};

export default ObjectRendererWeb;
