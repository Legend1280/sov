import React, { useState, useEffect } from 'react';
import { emitPulse, requestFromCore } from '../lib/PulseClient';
import Navigator from './Navigator';
import Viewport from './Viewport';
import SurfaceViewer from './SurfaceViewer';

interface ObjectRendererProps {
  object: string;
  props?: Record<string, any>;
}

/**
 * ObjectRendererWeb - Production version with real Pulse integration
 * 
 * Fetches ontology definitions from Core via PulseMesh, resolves UI bindings,
 * and instantiates components with full governance context.
 * 
 * Flow:
 * 1. Emit ontology.request Pulse to Core
 * 2. Core validates request via SAGE
 * 3. Core returns ontology YAML
 * 4. Resolve ui_binding to component
 * 5. Dynamically instantiate component
 * 6. Emit lifecycle Pulses (loading, rendered, unmounted)
 * 7. All Pulses flow through SAGE → Kronos → Shadow
 */
export const ObjectRendererWeb: React.FC<ObjectRendererProps> = ({
  object,
  props = {}
}) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [Component, setComponent] = useState<React.ComponentType<any> | null>(null);
  const [ontology, setOntology] = useState<any | null>(null);

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

        console.log(`[ObjectRenderer] Requesting ontology for: ${object}`);

        // Request ontology from Core via Pulse
        const response = await requestFromCore('ontology.request', {
          object_id: object,
          requester: 'mirror',
          timestamp: new Date().toISOString()
        }, 10000); // 10 second timeout

        if (response.status === 'error') {
          throw new Error(`Ontology request failed: ${response.error}`);
        }

        const ontologyData = response.ontology;
        setOntology(ontologyData);

        console.log(`[ObjectRenderer] Received ontology:`, ontologyData);

        // Extract UI binding
        const uiBinding = ontologyData.ui_binding;
        if (!uiBinding || !uiBinding.component) {
          throw new Error(`No UI binding found in ontology for: ${object}`);
        }

        // Map component names to actual components
        // In production, this could use dynamic imports based on ui_binding.path
        const componentMap: Record<string, React.ComponentType<any>> = {
          'Navigator': Navigator,
          'Viewport': Viewport,
          'SurfaceViewer': SurfaceViewer
        };

        const resolvedComponent = componentMap[uiBinding.component];

        if (!resolvedComponent) {
          throw new Error(`Component not found: ${uiBinding.component}`);
        }

        console.log(`[ObjectRenderer] Resolved component: ${uiBinding.component}`);

        setComponent(() => resolvedComponent);

        // Emit rendered event
        await emitPulse('mirror.object.rendered', {
          object_id: object,
          object_type: 'component',
          component_name: uiBinding.component,
          component_path: uiBinding.path,
          render_time_ms: 0,
          timestamp: new Date().toISOString()
        }, ['core', 'sage', 'kronos', 'shadow']);

        setLoading(false);
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Unknown error';
        console.error(`[ObjectRenderer] Error loading ${object}:`, errorMessage);
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
    return (
      <div style={styles.error}>
        <div>Error loading {object}</div>
        <div style={styles.errorDetail}>{error}</div>
      </div>
    );
  }

  if (!Component) {
    return <div style={styles.error}>Component not found: {object}</div>;
  }

  // Pass ontology context to component
  return <Component ontology={ontology} {...props} />;
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
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 24,
    fontSize: 14,
    color: '#EF4444',
    gap: 8
  },
  errorDetail: {
    fontSize: 12,
    opacity: 0.7
  }
};

export default ObjectRendererWeb;
