/**
 * ModuleRegistry - Loads and manages module manifests
 * 
 * Modules are defined by JSON configuration files that specify:
 * - Viewports (what to display)
 * - Data sources (where to fetch data)
 * - Navigator sources (sidebar navigation)
 * - Surface tabs (right panel tabs)
 * 
 * Example manifest structure:
 * {
 *   "id": "dexabooks",
 *   "name": "DexaBooks Financial Suite",
 *   "viewports": [
 *     { "id": "timeline", "type": "timeline", "title": "Cash Flow", "dataSource": "/api/transactions" }
 *   ],
 *   "surfaceTabs": ["Ontology", "Document", "Provenance"],
 *   "navigatorSources": ["Dashboard", "Transactions", "Analytics"]
 * }
 */

export interface ViewportConfig {
  id: string;
  type: string;
  title: string;
  dataSource: string;
  props?: Record<string, any>;
}

export interface ModuleManifest {
  id: string;
  name: string;
  description?: string;
  viewports: ViewportConfig[];
  surfaceTabs?: string[];
  navigatorSources?: string[];
}

class ModuleRegistry {
  private modules: Map<string, ModuleManifest> = new Map();
  private activeModuleId: string | null = null;

  /**
   * Register a module from a manifest object
   */
  register(manifest: ModuleManifest): void {
    if (this.modules.has(manifest.id)) {
      console.warn(`Module "${manifest.id}" is already registered. Overwriting.`);
    }
    this.modules.set(manifest.id, manifest);
    console.log(`[ModuleRegistry] Registered module: ${manifest.name} (${manifest.id})`);
  }

  /**
   * Load a module manifest from a URL or import
   */
  async load(moduleId: string): Promise<ModuleManifest> {
    try {
      // Dynamic import of module config
      const module = await import(`../modules/${moduleId}/config.json`);
      const manifest: ModuleManifest = module.default || module;
      this.register(manifest);
      return manifest;
    } catch (error) {
      console.error(`[ModuleRegistry] Failed to load module "${moduleId}":`, error);
      throw error;
    }
  }

  /**
   * Get a module manifest by ID
   */
  get(moduleId: string): ModuleManifest | undefined {
    return this.modules.get(moduleId);
  }

  /**
   * Set the active module
   */
  setActive(moduleId: string): void {
    if (!this.modules.has(moduleId)) {
      throw new Error(`Module "${moduleId}" is not registered`);
    }
    this.activeModuleId = moduleId;
    console.log(`[ModuleRegistry] Active module: ${moduleId}`);
  }

  /**
   * Get the active module manifest
   */
  getActive(): ModuleManifest | null {
    if (!this.activeModuleId) return null;
    return this.modules.get(this.activeModuleId) || null;
  }

  /**
   * Get all registered module IDs
   */
  getModuleIds(): string[] {
    return Array.from(this.modules.keys());
  }

  /**
   * Get all registered modules
   */
  getAllModules(): ModuleManifest[] {
    return Array.from(this.modules.values());
  }

  /**
   * Check if a module is registered
   */
  has(moduleId: string): boolean {
    return this.modules.has(moduleId);
  }

  /**
   * Unregister a module
   */
  unregister(moduleId: string): boolean {
    if (this.activeModuleId === moduleId) {
      this.activeModuleId = null;
    }
    return this.modules.delete(moduleId);
  }

  /**
   * Clear all modules
   */
  clear(): void {
    this.modules.clear();
    this.activeModuleId = null;
  }
}

// Export singleton instance
export const moduleRegistry = new ModuleRegistry();
export default moduleRegistry;
