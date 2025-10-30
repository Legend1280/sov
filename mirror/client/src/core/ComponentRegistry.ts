import { ComponentType } from 'react';

/**
 * ComponentRegistry - Maps component type strings to React components
 * 
 * Allows modules to specify component types in JSON manifests,
 * which are then dynamically loaded and rendered by ViewportManager.
 * 
 * Example:
 *   ComponentRegistry.register('timeline', CashFlowTimeline);
 *   const Component = ComponentRegistry.get('timeline');
 */

type ComponentMap = Map<string, ComponentType<any>>;

class ComponentRegistry {
  private components: ComponentMap = new Map();

  /**
   * Register a component type
   */
  register(type: string, component: ComponentType<any>): void {
    if (this.components.has(type)) {
      console.warn(`Component type "${type}" is already registered. Overwriting.`);
    }
    this.components.set(type, component);
    console.log(`[ComponentRegistry] Registered: ${type}`);
  }

  /**
   * Get a component by type
   */
  get(type: string): ComponentType<any> | undefined {
    const component = this.components.get(type);
    if (!component) {
      console.error(`[ComponentRegistry] Component type "${type}" not found`);
    }
    return component;
  }

  /**
   * Check if a component type is registered
   */
  has(type: string): boolean {
    return this.components.has(type);
  }

  /**
   * Get all registered component types
   */
  getTypes(): string[] {
    return Array.from(this.components.keys());
  }

  /**
   * Unregister a component type
   */
  unregister(type: string): boolean {
    return this.components.delete(type);
  }

  /**
   * Clear all registered components
   */
  clear(): void {
    this.components.clear();
  }
}

// Export singleton instance
export const componentRegistry = new ComponentRegistry();
export default componentRegistry;
