/**
 * Renderer - Dynamic component renderer
 * 
 * Parses layout schemas and mounts the appropriate React components.
 * Handles:
 * - Component resolution from ComponentRegistry
 * - Template variable resolution
 * - DataContext and EventBus injection
 * - Error boundaries and fallbacks
 */

import { Suspense } from 'react';
import { componentRegistry } from '@/core/ComponentRegistry';
import { useDataContext } from '@/core/DataContext';
import { eventBus } from '@/core/EventBus';
import { LayoutNode } from '@/types/schema';
import ErrorBoundary from '@/components/ErrorBoundary';

interface RendererProps {
  layout: LayoutNode | LayoutNode[];
  fallback?: React.ReactNode;
}

export function Renderer({ layout, fallback }: RendererProps) {
  const dataContext = useDataContext();

  const renderNode = (node: LayoutNode, index: number): React.ReactNode => {
    // Resolve component from registry
    const Component = componentRegistry.get(node.type);
    
    if (!Component) {
      console.error(`[Renderer] Component type "${node.type}" not found in registry`);
      return (
        <div key={`error-${node.type}-${index}`} className="p-4 border border-destructive rounded-lg bg-destructive/10">
          <p className="text-destructive font-semibold">Component "{node.type}" not found</p>
          <p className="text-sm text-muted-foreground mt-1">
            Make sure the component is registered in ComponentRegistry
          </p>
        </div>
      );
    }

    // Resolve template variables in props
    const resolvedProps = resolveTemplateVariables(node.props || {}, dataContext);

    // Inject dataContext and eventBus
    const injectedProps = {
      ...resolvedProps,
      dataContext,
      eventBus,
    };

    // Render children recursively
    const children = node.children?.map((child, i) => renderNode(child, i));

    return (
      <ErrorBoundary key={`${node.type}-${index}`}>
        <Suspense fallback={fallback || <div className="p-4 text-muted-foreground">Loading...</div>}>
          <Component {...injectedProps}>
            {children}
          </Component>
        </Suspense>
      </ErrorBoundary>
    );
  };

  // Handle both single node and array of nodes
  const nodes = Array.isArray(layout) ? layout : [layout];

  return (
    <div className="renderer-container">
      {nodes.map((node, index) => renderNode(node, index))}
    </div>
  );
}

/**
 * Resolve template variables in props
 * 
 * Template variables are strings in the format {{path.to.value}}
 * They are resolved from the DataContext
 * 
 * Example:
 *   {{selectedObject.id}} → dataContext.selectedObject.id
 *   {{currentUser.name}} → dataContext.currentUser.name
 */
function resolveTemplateVariables(
  props: Record<string, any>,
  context: any
): Record<string, any> {
  const resolved: Record<string, any> = {};

  for (const [key, value] of Object.entries(props)) {
    if (typeof value === 'string' && value.startsWith('{{') && value.endsWith('}}')) {
      const path = value.slice(2, -2).trim();
      resolved[key] = getNestedValue(context, path) || value;
    } else if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
      // Recursively resolve nested objects
      resolved[key] = resolveTemplateVariables(value, context);
    } else {
      resolved[key] = value;
    }
  }

  return resolved;
}

/**
 * Get a nested value from an object using a dot-separated path
 * 
 * Example:
 *   getNestedValue({ user: { name: "John" } }, "user.name") → "John"
 */
function getNestedValue(obj: any, path: string): any {
  return path.split('.').reduce((current, key) => current?.[key], obj);
}

export default Renderer;
