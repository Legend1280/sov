/**
 * PulseBridge - Semantic coherence communication layer
 * 
 * Carries meaning-bearing Pulse objects between Mirror and Core.
 * Unlike traditional event buses, PulseBridge maintains semantic identity
 * and measures coherence drift over time.
 * 
 * Author: Brady Simmons
 * Copyright: © 2025 Sovereignty Foundation. All rights reserved.
 */

export interface PulseObject {
  id: string;
  source: string;        // 'mirror', 'core', 'sage', etc.
  target: string;        // destination component
  mode: 'bi' | 'send' | 'receive';
  topic: string;         // semantic topic (e.g., 'intent:update', 'core:response')
  payload?: any;         // the actual content
  coherence?: number;    // measured alignment (0-1)
  timestamp: number;     // temporal marker
  vector?: number[];     // optional embedding for coherence measurement
}

export interface PulseListener {
  topic: string;
  handler: (pulse: PulseObject) => void;
}

class PulseBridgeCore {
  private listeners: Map<string, PulseListener[]> = new Map();
  private pulseLog: PulseObject[] = [];
  private maxLogSize = 1000;

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
   */
  emit(pulse: Partial<PulseObject>): void {
    const fullPulse: PulseObject = {
      id: this.generateId(),
      timestamp: Date.now(),
      mode: 'send',
      ...pulse,
    } as PulseObject;

    // Log the pulse
    this.logPulse(fullPulse);

    // Notify exact topic listeners
    const exactListeners = this.listeners.get(fullPulse.topic) || [];
    exactListeners.forEach(listener => listener.handler(fullPulse));

    // Notify wildcard listeners
    const wildcardListeners = this.listeners.get('*') || [];
    wildcardListeners.forEach(listener => listener.handler(fullPulse));

    // Notify source:* listeners
    const sourceWildcard = `${fullPulse.source}:*`;
    const sourceListeners = this.listeners.get(sourceWildcard) || [];
    sourceListeners.forEach(listener => listener.handler(fullPulse));

    // Notify target:* listeners
    const targetWildcard = `${fullPulse.target}:*`;
    const targetListeners = this.listeners.get(targetWildcard) || [];
    targetListeners.forEach(listener => listener.handler(fullPulse));
  }

  /**
   * Send a Pulse with simplified parameters
   */
  send(topic: string, payload: any, options?: Partial<PulseObject>): void {
    this.emit({
      topic,
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
  }

  /**
   * Calculate coherence between two pulses (simplified version)
   * In production, this would use vector embeddings
   */
  calculateCoherence(pulse1: PulseObject, pulse2: PulseObject): number {
    // Simplified coherence: check if topics are related
    if (pulse1.topic === pulse2.topic) return 1.0;
    
    // Check if one is a response to the other
    if (pulse1.topic.includes('intent') && pulse2.topic.includes('response')) {
      return 0.85;
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
