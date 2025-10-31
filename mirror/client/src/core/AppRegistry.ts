/**
 * AppRegistry - Manages application manifests and activation
 * 
 * Apps are first-tier containers that define:
 * - Navigator schema (left sidebar)
 * - Header schema (top bar)
 * - Default viewport layouts
 * 
 * Example:
 *   appRegistry.register(dexabooksApp);
 *   appRegistry.activate("dexabooks");
 */

export interface AppManifest {
  id: string;                      // Unique app identifier
  name: string;                    // Human-readable name
  description?: string;            // App description
  icon?: string;                   // Icon name (lucide-react)
  defaultLayout: string;           // Default layout schema ID (AppContainer)
  navigatorSchema?: string;        // Navigator schema ID
  headerSchema?: string;           // Header schema ID
  permissions?: string[];          // Required permissions
  metadata?: Record<string, any>;  // Additional metadata
  onActivate?: () => void | Promise<void>;    // Lifecycle hook: called when app is activated
  onDeactivate?: () => void | Promise<void>;  // Lifecycle hook: called when app is deactivated
}

class AppRegistry {
  private apps: Map<string, AppManifest> = new Map();
  private activeAppId: string | null = null;

  /**
   * Register an app from a manifest object
   */
  register(manifest: AppManifest): void {
    if (this.apps.has(manifest.id)) {
      console.warn(`[AppRegistry] App "${manifest.id}" is already registered. Overwriting.`);
    }
    this.apps.set(manifest.id, manifest);
    console.log(`[AppRegistry] Registered app: ${manifest.name} (${manifest.id})`);
  }

  /**
   * Load an app manifest from a URL or import
   */
  async load(appId: string): Promise<AppManifest> {
    try {
      // Dynamic import of app config
      const module = await import(`../apps/${appId}/app.json`);
      const manifest: AppManifest = module.default || module;
      this.register(manifest);
      return manifest;
    } catch (error) {
      console.error(`[AppRegistry] Failed to load app "${appId}":`, error);
      throw error;
    }
  }

  /**
   * Get an app manifest by ID
   */
  get(appId: string): AppManifest | undefined {
    return this.apps.get(appId);
  }

  /**
   * Set the active app
   */
  async setActive(appId: string): Promise<void> {
    if (!this.apps.has(appId)) {
      throw new Error(`[AppRegistry] App "${appId}" is not registered`);
    }

    // Call onDeactivate for the currently active app
    if (this.activeAppId && this.activeAppId !== appId) {
      const currentApp = this.apps.get(this.activeAppId);
      if (currentApp?.onDeactivate) {
        try {
          await currentApp.onDeactivate();
          console.log(`[AppRegistry] Deactivated app: ${this.activeAppId}`);
        } catch (error) {
          console.error(`[AppRegistry] Error deactivating app "${this.activeAppId}":`, error);
        }
      }
    }

    this.activeAppId = appId;
    console.log(`[AppRegistry] Active app: ${appId}`);

    // Call onActivate for the new app
    const newApp = this.apps.get(appId);
    if (newApp?.onActivate) {
      try {
        await newApp.onActivate();
        console.log(`[AppRegistry] Activated app: ${appId}`);
      } catch (error) {
        console.error(`[AppRegistry] Error activating app "${appId}":`, error);
      }
    }
  }

  /**
   * Get the active app manifest
   */
  getActive(): AppManifest | null {
    if (!this.activeAppId) return null;
    return this.apps.get(this.activeAppId) || null;
  }

  /**
   * Get all registered app IDs
   */
  getAppIds(): string[] {
    return Array.from(this.apps.keys());
  }

  /**
   * Get all registered apps
   */
  getAllApps(): AppManifest[] {
    return Array.from(this.apps.values());
  }

  /**
   * Check if an app is registered
   */
  has(appId: string): boolean {
    return this.apps.has(appId);
  }

  /**
   * Unregister an app
   */
  unregister(appId: string): boolean {
    if (this.activeAppId === appId) {
      this.activeAppId = null;
    }
    return this.apps.delete(appId);
  }

  /**
   * Clear all apps
   */
  clear(): void {
    this.apps.clear();
    this.activeAppId = null;
  }

  /**
   * Discover apps from modules
   * Scans all modules for app manifests
   */
  async discoverApps(): Promise<void> {
    try {
      // Discover apps from the /apps directory
      const appModules = import.meta.glob('../apps/*/app.json');
      for (const [path, loader] of Object.entries(appModules)) {
        try {
          const manifest = await loader() as AppManifest;
          this.register(manifest);
        } catch (error) {
          console.warn(`[AppRegistry] Failed to load app from ${path}:`, error);
        }
      }
    } catch (error) {
      console.error('[AppRegistry] Failed to discover apps:', error);
    }
  }
}

// Export singleton instance
export const appRegistry = new AppRegistry();
export default appRegistry;
