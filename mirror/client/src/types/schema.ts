/**
 * Schema Type Definitions
 * 
 * Defines the TypeScript types for layout schemas used by the Renderer.
 */

export interface LayoutNode {
  type: string;                    // Component type (e.g., "Timeline", "Grid", "AppContainer")
  props?: Record<string, any>;     // Component props
  children?: LayoutNode[];         // Child components (for containers)
}

export interface ViewportLayout {
  viewport1?: LayoutNode[];        // Components for viewport 1
  viewport2?: LayoutNode[];        // Components for viewport 2
}

export interface NavigatorSource {
  id: string;                      // Unique source identifier
  label: string;                   // Display label
  icon?: string;                   // Icon name (lucide-react)
  badge?: string;                  // Badge text (e.g., "3 new")
  action?: string;                 // Event to emit on click
}

export interface MirrorLayoutSchema {
  id: string;                      // Unique layout identifier
  name: string;                    // Human-readable name
  description?: string;            // Layout description
  module?: string;                 // Associated module ID
  app?: string;                    // Associated app ID
  viewports?: ViewportLayout;      // Viewport component trees
  surfaceTabs?: string[];          // Surface viewer tab names
  navigatorSources?: NavigatorSource[];  // Navigator sidebar items
  metadata?: Record<string, any>;  // Additional metadata
}

export interface AppContainerSchema extends LayoutNode {
  type: 'AppContainer';
  props: {
    appId: string;                 // App identifier
    navigatorSchema?: string;      // Navigator schema ID
    headerSchema?: string;         // Header schema ID
    viewports?: ViewportConfig[];  // Viewport configurations
  };
}

export interface ViewportConfig {
  id: string;                      // Viewport identifier (e.g., "viewport1")
  schema: string;                  // Layout schema ID for this viewport
}

export type LayoutSchema = MirrorLayoutSchema | AppContainerSchema;
