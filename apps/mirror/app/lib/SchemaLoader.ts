/**
 * SchemaLoader — Layout Schema Fetcher and Cache
 * 
 * Fetches and caches layout schemas from Core that define how ontological
 * objects should be arranged in viewports. Schemas are JSON definitions
 * that map to ObjectRenderer instances.
 * 
 * Schema Format:
 * {
 *   "type": "Viewport",
 *   "id": "home",
 *   "children": [
 *     {
 *       "type": "Logos",
 *       "props": { "mode": "login" }
 *     }
 *   ]
 * }
 * 
 * Author: Brady Simmons
 * Copyright: © 2025 Sovereignty Foundation. All rights reserved.
 */

import { PulseBridge } from './PulseBridge';

export interface SchemaObject {
  type: string;
  id?: string;
  props?: Record<string, any>;
  children?: SchemaObject[];
  style?: Record<string, any>;
}

export interface LayoutSchema {
  type: 'Viewport';
  id: string;
  metadata?: {
    title?: string;
    description?: string;
    version?: string;
  };
  children: SchemaObject[];
}

class SchemaLoaderClass {
  private cache: Map<string, LayoutSchema> = new Map();
  private loading: Map<string, Promise<LayoutSchema>> = new Map();
  private cacheTTL: number = 3600000; // 1 hour
  private cacheTimestamps: Map<string, number> = new Map();

  /**
   * Load a layout schema by ID
   * 
   * @param schemaId - The schema identifier (e.g., "home", "dashboard")
   * @param forceRefresh - Force fetch from Core, bypass cache
   * @returns Promise<LayoutSchema>
   */
  async load(schemaId: string, forceRefresh: boolean = false): Promise<LayoutSchema> {
    // Check cache first
    if (!forceRefresh && this.isCached(schemaId)) {
      const cached = this.cache.get(schemaId);
      if (cached) {
        console.log(`[SchemaLoader] Cache hit: ${schemaId}`);
        return cached;
      }
    }

    // Check if already loading
    if (this.loading.has(schemaId)) {
      console.log(`[SchemaLoader] Already loading: ${schemaId}`);
      return this.loading.get(schemaId)!;
    }

    // Fetch from Core
    const loadPromise = this.fetchSchema(schemaId);
    this.loading.set(schemaId, loadPromise);

    try {
      const schema = await loadPromise;
      
      // Cache the result
      this.cache.set(schemaId, schema);
      this.cacheTimestamps.set(schemaId, Date.now());
      
      console.log(`[SchemaLoader] Loaded and cached: ${schemaId}`);
      
      return schema;
    } finally {
      this.loading.delete(schemaId);
    }
  }

  /**
   * Fetch schema from Core
   */
  private async fetchSchema(schemaId: string): Promise<LayoutSchema> {
    // Emit schema request Pulse
    PulseBridge.emit('mirror.schema.request', {
      source: 'mirror',
      target: 'core',
      intent: 'schema.request',
      payload: {
        schema_id: schemaId,
        timestamp: new Date().toISOString()
      }
    });

    // In production, this would fetch from Core API
    // For now, use mock schemas
    return this.getMockSchema(schemaId);
  }

  /**
   * Check if schema is cached and not expired
   */
  private isCached(schemaId: string): boolean {
    if (!this.cache.has(schemaId)) {
      return false;
    }

    const timestamp = this.cacheTimestamps.get(schemaId);
    if (!timestamp) {
      return false;
    }

    const age = Date.now() - timestamp;
    return age < this.cacheTTL;
  }

  /**
   * Clear cache for a specific schema or all schemas
   */
  clearCache(schemaId?: string): void {
    if (schemaId) {
      this.cache.delete(schemaId);
      this.cacheTimestamps.delete(schemaId);
      console.log(`[SchemaLoader] Cache cleared: ${schemaId}`);
    } else {
      this.cache.clear();
      this.cacheTimestamps.clear();
      console.log(`[SchemaLoader] All cache cleared`);
    }
  }

  /**
   * Preload multiple schemas
   */
  async preload(schemaIds: string[]): Promise<void> {
    console.log(`[SchemaLoader] Preloading ${schemaIds.length} schemas...`);
    
    await Promise.all(
      schemaIds.map(id => this.load(id).catch(err => {
        console.error(`[SchemaLoader] Failed to preload ${id}:`, err);
      }))
    );
    
    console.log(`[SchemaLoader] Preload complete`);
  }

  /**
   * Get cache statistics
   */
  getCacheStats(): {
    size: number;
    schemas: string[];
    oldestAge: number;
  } {
    const schemas = Array.from(this.cache.keys());
    const ages = Array.from(this.cacheTimestamps.values()).map(ts => Date.now() - ts);
    
    return {
      size: this.cache.size,
      schemas,
      oldestAge: ages.length > 0 ? Math.max(...ages) : 0
    };
  }

  /**
   * Mock schema provider (replace with actual Core API)
   */
  private async getMockSchema(schemaId: string): Promise<LayoutSchema> {
    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 300));

    // Mock schemas
    const schemas: Record<string, LayoutSchema> = {
      home: {
        type: 'Viewport',
        id: 'home',
        metadata: {
          title: 'Home',
          description: 'Main landing viewport',
          version: '1.0'
        },
        children: [
          {
            type: 'Header',
            props: {
              title: 'Sovereignty Stack',
              subtitle: 'Semantic Communication Architecture'
            }
          },
          {
            type: 'Logos',
            props: {
              mode: 'login'
            }
          },
          {
            type: 'SystemStatus',
            props: {
              showNodes: true
            }
          }
        ]
      },
      
      dashboard: {
        type: 'Viewport',
        id: 'dashboard',
        metadata: {
          title: 'Dashboard',
          description: 'User dashboard with system overview',
          version: '1.0'
        },
        children: [
          {
            type: 'Header',
            props: {
              title: 'Dashboard'
            }
          },
          {
            type: 'Grid',
            children: [
              {
                type: 'PulseMonitor',
                props: {
                  realtime: true
                }
              },
              {
                type: 'SystemHealth',
                props: {
                  showMetrics: true
                }
              }
            ]
          }
        ]
      },

      login: {
        type: 'Viewport',
        id: 'login',
        metadata: {
          title: 'Login',
          description: 'Authentication viewport',
          version: '1.0'
        },
        children: [
          {
            type: 'Logos',
            props: {
              mode: 'login'
            }
          }
        ]
      }
    };

    const schema = schemas[schemaId];
    
    if (!schema) {
      throw new Error(`Schema not found: ${schemaId}`);
    }

    // Emit schema loaded Pulse
    PulseBridge.emit('mirror.schema.loaded', {
      source: 'mirror',
      target: 'core',
      intent: 'schema.loaded',
      payload: {
        schema_id: schemaId,
        timestamp: new Date().toISOString()
      }
    });

    return schema;
  }
}

// Export singleton instance
export const SchemaLoader = new SchemaLoaderClass();
