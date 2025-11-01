/**
 * ObjectLifecycle — Pulse-Driven Lifecycle Event System
 * 
 * Manages lifecycle events for ontological objects rendered in Mirror.
 * All lifecycle events are emitted as Pulses and can be:
 * - Validated by SAGE
 * - Indexed by Kronos
 * - Logged by Shadow
 * - Monitored by Mirror
 * 
 * Lifecycle Events:
 * - object.loading: Object definition is being fetched
 * - object.loaded: Object definition fetched successfully
 * - object.rendering: Component is being instantiated
 * - object.rendered: Component rendered in viewport
 * - object.interacted: User interacted with object
 * - object.updated: Object state changed
 * - object.unmounting: Component is being removed
 * - object.unmounted: Component removed from viewport
 * - object.error: Error occurred during lifecycle
 * 
 * Author: Brady Simmons
 * Copyright: © 2025 Sovereignty Foundation. All rights reserved.
 */

import { PulseBridge } from './PulseBridge';

export interface LifecycleEvent {
  phase: LifecyclePhase;
  object_id: string;
  component?: string;
  timestamp: string;
  metadata?: Record<string, any>;
  error?: string;
}

export type LifecyclePhase =
  | 'loading'
  | 'loaded'
  | 'rendering'
  | 'rendered'
  | 'interacted'
  | 'updated'
  | 'unmounting'
  | 'unmounted'
  | 'error';

class ObjectLifecycleClass {
  private activeObjects: Map<string, LifecycleEvent[]> = new Map();
  private listeners: Map<LifecyclePhase, Set<(event: LifecycleEvent) => void>> = new Map();

  constructor() {
    // Initialize listener sets for each phase
    const phases: LifecyclePhase[] = [
      'loading', 'loaded', 'rendering', 'rendered',
      'interacted', 'updated', 'unmounting', 'unmounted', 'error'
    ];
    
    phases.forEach(phase => {
      this.listeners.set(phase, new Set());
    });
  }

  /**
   * Emit a lifecycle event
   */
  emit(event: LifecycleEvent): void {
    const { phase, object_id, component, metadata, error } = event;

    // Store in active objects history
    if (!this.activeObjects.has(object_id)) {
      this.activeObjects.set(object_id, []);
    }
    this.activeObjects.get(object_id)!.push(event);

    // Emit as Pulse
    PulseBridge.emit(`mirror.object.${phase}`, {
      source: 'mirror',
      target: 'core',
      intent: `object.${phase}`,
      payload: {
        object_id,
        component,
        timestamp: event.timestamp,
        metadata,
        error
      }
    });

    // Notify local listeners
    const phaseListeners = this.listeners.get(phase);
    if (phaseListeners) {
      phaseListeners.forEach(listener => {
        try {
          listener(event);
        } catch (err) {
          console.error(`[ObjectLifecycle] Listener error:`, err);
        }
      });
    }

    // Log to console
    this.logEvent(event);
  }

  /**
   * Subscribe to lifecycle events for a specific phase
   */
  on(phase: LifecyclePhase, listener: (event: LifecycleEvent) => void): () => void {
    const phaseListeners = this.listeners.get(phase);
    if (phaseListeners) {
      phaseListeners.add(listener);
    }

    // Return unsubscribe function
    return () => {
      if (phaseListeners) {
        phaseListeners.delete(listener);
      }
    };
  }

  /**
   * Get lifecycle history for an object
   */
  getHistory(objectId: string): LifecycleEvent[] {
    return this.activeObjects.get(objectId) || [];
  }

  /**
   * Get all active objects
   */
  getActiveObjects(): string[] {
    return Array.from(this.activeObjects.keys());
  }

  /**
   * Get current phase for an object
   */
  getCurrentPhase(objectId: string): LifecyclePhase | null {
    const history = this.getHistory(objectId);
    if (history.length === 0) return null;
    return history[history.length - 1].phase;
  }

  /**
   * Check if object is in a specific phase
   */
  isInPhase(objectId: string, phase: LifecyclePhase): boolean {
    return this.getCurrentPhase(objectId) === phase;
  }

  /**
   * Clear history for an object
   */
  clearHistory(objectId: string): void {
    this.activeObjects.delete(objectId);
  }

  /**
   * Get lifecycle statistics
   */
  getStats(): {
    activeObjects: number;
    totalEvents: number;
    phaseDistribution: Record<LifecyclePhase, number>;
  } {
    let totalEvents = 0;
    const phaseDistribution: Record<string, number> = {};

    this.activeObjects.forEach(history => {
      totalEvents += history.length;
      history.forEach(event => {
        phaseDistribution[event.phase] = (phaseDistribution[event.phase] || 0) + 1;
      });
    });

    return {
      activeObjects: this.activeObjects.size,
      totalEvents,
      phaseDistribution: phaseDistribution as Record<LifecyclePhase, number>
    };
  }

  /**
   * Log lifecycle event to console
   */
  private logEvent(event: LifecycleEvent): void {
    const { phase, object_id, component, error } = event;
    
    const phaseEmoji: Record<LifecyclePhase, string> = {
      loading: '⏳',
      loaded: '✅',
      rendering: '🎨',
      rendered: '🖼️',
      interacted: '👆',
      updated: '🔄',
      unmounting: '⏸️',
      unmounted: '💤',
      error: '❌'
    };

    const emoji = phaseEmoji[phase] || '📍';
    const componentInfo = component ? ` [${component}]` : '';
    const errorInfo = error ? ` - ${error}` : '';

    console.log(
      `${emoji} [ObjectLifecycle] ${object_id}${componentInfo} → ${phase}${errorInfo}`
    );
  }
}

// Export singleton instance
export const ObjectLifecycle = new ObjectLifecycleClass();

/**
 * Convenience functions for emitting lifecycle events
 */

export function emitLoading(objectId: string, component?: string, metadata?: Record<string, any>) {
  ObjectLifecycle.emit({
    phase: 'loading',
    object_id: objectId,
    component,
    timestamp: new Date().toISOString(),
    metadata
  });
}

export function emitLoaded(objectId: string, component?: string, metadata?: Record<string, any>) {
  ObjectLifecycle.emit({
    phase: 'loaded',
    object_id: objectId,
    component,
    timestamp: new Date().toISOString(),
    metadata
  });
}

export function emitRendering(objectId: string, component?: string, metadata?: Record<string, any>) {
  ObjectLifecycle.emit({
    phase: 'rendering',
    object_id: objectId,
    component,
    timestamp: new Date().toISOString(),
    metadata
  });
}

export function emitRendered(objectId: string, component?: string, metadata?: Record<string, any>) {
  ObjectLifecycle.emit({
    phase: 'rendered',
    object_id: objectId,
    component,
    timestamp: new Date().toISOString(),
    metadata
  });
}

export function emitInteracted(objectId: string, component?: string, metadata?: Record<string, any>) {
  ObjectLifecycle.emit({
    phase: 'interacted',
    object_id: objectId,
    component,
    timestamp: new Date().toISOString(),
    metadata
  });
}

export function emitUpdated(objectId: string, component?: string, metadata?: Record<string, any>) {
  ObjectLifecycle.emit({
    phase: 'updated',
    object_id: objectId,
    component,
    timestamp: new Date().toISOString(),
    metadata
  });
}

export function emitUnmounting(objectId: string, component?: string, metadata?: Record<string, any>) {
  ObjectLifecycle.emit({
    phase: 'unmounting',
    object_id: objectId,
    component,
    timestamp: new Date().toISOString(),
    metadata
  });
}

export function emitUnmounted(objectId: string, component?: string, metadata?: Record<string, any>) {
  ObjectLifecycle.emit({
    phase: 'unmounted',
    object_id: objectId,
    component,
    timestamp: new Date().toISOString(),
    metadata
  });
}

export function emitError(objectId: string, error: string, component?: string, metadata?: Record<string, any>) {
  ObjectLifecycle.emit({
    phase: 'error',
    object_id: objectId,
    component,
    timestamp: new Date().toISOString(),
    metadata,
    error
  });
}
