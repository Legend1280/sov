/**
 * PulseBridge - Semantic coherence communication layer
 * 
 * Carries meaning-bearing Pulse objects between Mirror and Core.
 * Unlike traditional event buses, PulseBridge maintains semantic identity
 * and measures coherence drift over time.
 * 
 * All Pulses are validated by SAGE before transmission.
 * 
 * Author: Brady Simmons
 * Copyright: © 2025 Sovereignty Foundation. All rights reserved.
 */

import { SageMiddleware } from '../sage/SageMiddleware';
import { KronosTracker } from '../kronos/KronosTracker';
import { PulseRegistry } from './PulseRegistry';

export type PulseIntent = 'update' | 'query' | 'create' | 'govern' | 'reflect';
export type PulseStatus = 'active' | 'decayed' | 'terminated';

export interface PulseProvenance {
  initiator: string;      // e.g., 'logos:user_001'
  authorized_by: string;  // e.g., 'sage:rule_001'
}

export interface PulseObject {
  id: string;
  origin: string;         // source module: 'mirror', 'core', 'sage', etc.
  target: string;         // destination module
  intent: PulseIntent;    // classification: update, query, create, govern, reflect
  payload: any;           // semantic content of the communication
  coherence: number;      // measure of alignment between intent and response (0-1)
  sage_ruleset: string;   // governance rule that validates this interaction
  vector_ids: string[];   // references to stored embeddings in Core
  timestamp: string;      // ISO 8601 UTC timestamp
  status: PulseStatus;    // active, decayed, or terminated
  provenance: PulseProvenance; // traceability record of actor responsibility
}

export interface PulseListener {
  topic: string;
  handler: (pulse: PulseObject) => void;
}

class PulseBridgeCore {
  private listeners: Map<string, PulseListener[]> = new Map();
  private pulseLog: PulseObject[] = [];
  private maxLogSize = 1000;

  constructor() {
    // Initialize Kronos Tracker
    KronosTracker.initialize();
  }

  /**
   * Register a listener for a specific topic or wildcard
   */
  on(topic: string, handler: (pulse: PulseObject) => void): () => void {
    const listener: PulseListener = { topic, handler };
    
    if (!this.listeners.has(topic)) {
      this.listeners.set(topic, []);
    }
    
    this.listeners.get(topic)!.push(listener);

    // Return unsubscribe function
    return () => {
      const listeners = this.listeners.get(topic);
      if (listeners) {
        const index = listeners.indexOf(listener);
        if (index > -1) {
          listeners.splice(index, 1);
        }
      }
    };
  }

  /**
   * Emit a Pulse object to all matching listeners
   * Validates with SAGE before transmission
   */
  emit(pulse: Partial<PulseObject>): void {
    // Validate with SAGE
    const validation = SageMiddleware.validate(pulse);
    
    if (!validation.approved) {
      console.error('[PulseBridge] SAGE validation failed:', validation.message);
      // Emit a validation failure event
      const failureEvent: PulseObject = {
        id: this.generateId(),
        origin: 'sage',
        target: pulse.origin || 'unknown',
        intent: 'govern',
        payload: {
          error: validation.message,
          original_pulse: pulse
        },
        coherence: 0.0,
        sage_ruleset: validation.rule_id,
        vector_ids: [],
        timestamp: new Date().toISOString(),
        status: 'terminated',
        provenance: {
          initiator: 'sage:middleware',
          authorized_by: validation.rule_id
        }
      };
      this.logPulse(failureEvent);
      return;
    }

    // Log warnings if any
    if (validation.warnings && validation.warnings.length > 0) {
      console.warn('[PulseBridge] SAGE warnings:', validation.warnings);
    }

    const fullPulse: PulseObject = {
      id: this.generateId(),
      timestamp: new Date().toISOString(),
      status: 'active',
      coherence: 0.0,
      sage_ruleset: validation.rule_id,
      vector_ids: [],
      provenance: {
        initiator: pulse.origin || 'system',
        authorized_by: validation.rule_id
      },
      ...pulse,
    } as PulseObject;

    // Log the pulse
    this.logPulse(fullPulse);

    // Track with Kronos for temporal decay
    KronosTracker.track(fullPulse);

    // Register with PulseRegistry
    PulseRegistry.register(fullPulse);

    // Create topic for routing
    const topic = `${fullPulse.origin}:${fullPulse.intent}`;

    // Notify exact topic listeners
    const exactListeners = this.listeners.get(topic) || [];
    exactListeners.forEach(listener => listener.handler(fullPulse));

    // Notify wildcard listeners
    const wildcardListeners = this.listeners.get('*') || [];
    wildcardListeners.forEach(listener => listener.handler(fullPulse));

    // Notify origin:* listeners
    const originWildcard = `${fullPulse.origin}:*`;
    const originListeners = this.listeners.get(originWildcard) || [];
    originListeners.forEach(listener => listener.handler(fullPulse));

    // Notify target:* listeners
    const targetWildcard = `${fullPulse.target}:*`;
    const targetListeners = this.listeners.get(targetWildcard) || [];
    targetListeners.forEach(listener => listener.handler(fullPulse));
  }

  /**
   * Send a Pulse with simplified parameters
   */
  send(intent: PulseIntent, payload: any, options?: Partial<PulseObject>): void {
    this.emit({
      intent,
      payload,
      ...options,
    });
  }

  /**
   * Get the pulse log for debugging/visualization
   */
  getLog(): PulseObject[] {
    return [...this.pulseLog];
  }

  /**
   * Clear the pulse log
   */
  clearLog(): void {
    this.pulseLog = [];
    
    // Notify all wildcard listeners that the log was cleared
    const wildcardListeners = this.listeners.get('*') || [];
    const clearEvent: PulseObject = {
      id: 'log_cleared',
      origin: 'system',
      target: '*',
      intent: 'update',
      payload: { action: 'log_cleared' },
      coherence: 1.0,
      sage_ruleset: 'default-governance',
      vector_ids: [],
      timestamp: new Date().toISOString(),
      status: 'active',
      provenance: {
        initiator: 'system',
        authorized_by: 'sage:default'
      }
    };
    wildcardListeners.forEach(listener => listener.handler(clearEvent));
  }

  /**
   * Calculate coherence between two pulses (simplified version)
   * In production, this would use vector embeddings
   */
  calculateCoherence(pulse1: PulseObject, pulse2: PulseObject): number {
    // Simplified coherence: check if intents are related
    if (pulse1.intent === pulse2.intent) return 1.0;
    
    // Check if one is a query and the other is an update (request-response pattern)
    if ((pulse1.intent === 'query' && pulse2.intent === 'update') ||
        (pulse1.intent === 'update' && pulse2.intent === 'query')) {
      return 0.85;
    }
    
    // Reflect intent always has high coherence with its origin
    if (pulse1.intent === 'reflect' || pulse2.intent === 'reflect') {
      return 0.9;
    }
    
    // Default: low coherence
    return 0.3;
  }

  private logPulse(pulse: PulseObject): void {
    this.pulseLog.push(pulse);
    
    // Keep log size manageable
    if (this.pulseLog.length > this.maxLogSize) {
      this.pulseLog.shift();
    }
  }

  private generateId(): string {
    return `pulse_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
}

// Singleton instance
export const PulseBridge = new PulseBridgeCore();
