import React, { useEffect, useState } from 'react';
import { componentRegistry } from './ComponentRegistry';
import { apiService } from './APIService';
import type { ViewportConfig } from './ModuleRegistry';

/**
 * ViewportManager - Dynamically renders viewports based on manifest configuration
 * 
 * Takes a viewport config from a module manifest and:
 * 1. Fetches data from the specified dataSource
 * 2. Looks up the component type in ComponentRegistry
 * 3. Renders the component with the fetched data
 */

interface ViewportManagerProps {
  config: ViewportConfig;
}

export const ViewportManager: React.FC<ViewportManagerProps> = ({ config }) => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        const result = await apiService.fetchData(config.dataSource);
        setData(result);
      } catch (err) {
        console.error(`[ViewportManager] Failed to fetch data for ${config.id}:`, err);
        setError(err instanceof Error ? err.message : 'Failed to load data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [config.dataSource, config.id]);

  // Get component from registry
  const Component = componentRegistry.get(config.type);

  if (!Component) {
    return (
      <div className="flex items-center justify-center h-full bg-card text-destructive">
        <div className="text-center">
          <p className="text-lg font-semibold">Component Not Found</p>
          <p className="text-sm">Type: {config.type}</p>
          <p className="text-xs mt-2">Register this component in ComponentRegistry</p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full bg-card text-muted-foreground">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p>Loading {config.title}...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-full bg-card text-destructive">
        <div className="text-center">
          <p className="text-lg font-semibold">Error Loading Data</p>
          <p className="text-sm">{error}</p>
          <p className="text-xs mt-2">Source: {config.dataSource}</p>
        </div>
      </div>
    );
  }

  // Render component with data and any additional props from config
  return <Component data={data} title={config.title} {...(config.props || {})} />;
};

export default ViewportManager;
