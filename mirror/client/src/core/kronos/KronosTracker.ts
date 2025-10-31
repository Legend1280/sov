/**
 * Kronos Tracker - Temporal decay tracking for Pulse events
 * 
 * Tracks temporal decay and coherence history for all Pulses.
 * Each Pulse carries a half-life measured by Kronos.
 * When coherence or relevance decays below a threshold, the Pulse is archived.
 * 
 * Temporal decay formula: C_t = C_0 * e^(-λt)
 * 
 * Author: Brady Simmons
 * Copyright: © 2025 Sovereignty Foundation. All rights reserved.
 */

import { PulseObject } from '../pulse/PulseBridge';

export interface TemporalMetrics {
  pulse_id: string;
  creation_time: string;
  last_update: string;
  age_seconds: number;
  decay_factor: number;      // λ (lambda) in the decay formula
  current_coherence: number;
  initial_coherence: number;
  decayed_coherence: number; // C_t = C_0 * e^(-λt)
  half_life_hours: number;
  status: 'active' | 'decayed' | 'terminated';
}

export interface DecayConfig {
  decay_threshold: number;    // Coherence threshold for archiving (e.g., 0.3)
  default_half_life: number;  // Default half-life in hours
  update_interval: number;    // How often to check for decay (in seconds)
}

const DEFAULT_CONFIG: DecayConfig = {
  decay_threshold: 0.3,
  default_half_life: 24, // 24 hours
  update_interval: 60,   // Check every 60 seconds
};

class KronosTrackerCore {
  private metrics: Map<string, TemporalMetrics> = new Map();
  private config: DecayConfig = DEFAULT_CONFIG;
  private updateTimer: NodeJS.Timeout | null = null;

  /**
   * Initialize Kronos Tracker
   */
  initialize(): void {
    console.log('[KronosTracker] Initialized');
    
    // Start periodic decay updates
    this.startDecayUpdates();
  }

  /**
   * Track a new Pulse
   */
  track(pulse: PulseObject): void {
    const now = new Date().toISOString();
    
    const metrics: TemporalMetrics = {
      pulse_id: pulse.id,
      creation_time: pulse.timestamp,
      last_update: now,
      age_seconds: 0,
      decay_factor: this.calculateDecayFactor(pulse),
      current_coherence: pulse.coherence,
      initial_coherence: pulse.coherence,
      decayed_coherence: pulse.coherence,
      half_life_hours: this.config.default_half_life,
      status: pulse.status,
    };

    this.metrics.set(pulse.id, metrics);
  }

  /**
   * Update temporal metrics for a Pulse
   */
  update(pulseId: string): TemporalMetrics | null {
    const metrics = this.metrics.get(pulseId);
    if (!metrics) return null;

    const now = new Date();
    const creationTime = new Date(metrics.creation_time);
    const ageSeconds = (now.getTime() - creationTime.getTime()) / 1000;
    const ageHours = ageSeconds / 3600;

    // Calculate decayed coherence: C_t = C_0 * e^(-λt)
    const decayedCoherence = metrics.initial_coherence * Math.exp(-metrics.decay_factor * ageHours);

    // Update metrics
    metrics.age_seconds = ageSeconds;
    metrics.last_update = now.toISOString();
    metrics.decayed_coherence = decayedCoherence;

    // Check if Pulse should be archived
    if (decayedCoherence < this.config.decay_threshold && metrics.status === 'active') {
      metrics.status = 'decayed';
      console.log(`[KronosTracker] Pulse ${pulseId} has decayed (coherence: ${decayedCoherence.toFixed(2)})`);
    }

    this.metrics.set(pulseId, metrics);
    return metrics;
  }

  /**
   * Get temporal metrics for a Pulse
   */
  getMetrics(pulseId: string): TemporalMetrics | null {
    return this.metrics.get(pulseId) || null;
  }

  /**
   * Get all tracked Pulses
   */
  getAllMetrics(): TemporalMetrics[] {
    return Array.from(this.metrics.values());
  }

  /**
   * Get active Pulses (not decayed or terminated)
   */
  getActivePulses(): TemporalMetrics[] {
    return Array.from(this.metrics.values()).filter(m => m.status === 'active');
  }

  /**
   * Get decayed Pulses
   */
  getDecayedPulses(): TemporalMetrics[] {
    return Array.from(this.metrics.values()).filter(m => m.status === 'decayed');
  }

  /**
   * Terminate a Pulse (mark as terminated)
   */
  terminate(pulseId: string): void {
    const metrics = this.metrics.get(pulseId);
    if (metrics) {
      metrics.status = 'terminated';
      metrics.last_update = new Date().toISOString();
      this.metrics.set(pulseId, metrics);
    }
  }

  /**
   * Archive old Pulses (remove from tracking)
   */
  archiveOldPulses(maxAgeHours: number = 168): number {
    const now = new Date();
    let archivedCount = 0;

    for (const [pulseId, metrics] of this.metrics.entries()) {
      const creationTime = new Date(metrics.creation_time);
      const ageHours = (now.getTime() - creationTime.getTime()) / (1000 * 3600);

      if (ageHours > maxAgeHours) {
        this.metrics.delete(pulseId);
        archivedCount++;
      }
    }

    if (archivedCount > 0) {
      console.log(`[KronosTracker] Archived ${archivedCount} old Pulses`);
    }

    return archivedCount;
  }

  /**
   * Calculate decay factor (λ) based on Pulse properties
   * Higher decay factor = faster decay
   */
  private calculateDecayFactor(pulse: PulseObject): number {
    // λ = ln(2) / half_life
    // This ensures that at t = half_life, C_t = C_0 / 2
    const ln2 = 0.693147;
    
    // Different intents have different decay rates
    let halfLife = this.config.default_half_life;
    
    switch (pulse.intent) {
      case 'query':
        halfLife = 12; // Queries decay faster (12 hours)
        break;
      case 'update':
        halfLife = 24; // Updates decay normally (24 hours)
        break;
      case 'create':
        halfLife = 48; // Creates last longer (48 hours)
        break;
      case 'govern':
        halfLife = 72; // Governance lasts even longer (72 hours)
        break;
      case 'reflect':
        halfLife = 168; // Reflections last a week
        break;
    }

    return ln2 / halfLife;
  }

  /**
   * Start periodic decay updates
   */
  private startDecayUpdates(): void {
    if (this.updateTimer) {
      clearInterval(this.updateTimer);
    }

    this.updateTimer = setInterval(() => {
      // Update all tracked Pulses
      for (const pulseId of this.metrics.keys()) {
        this.update(pulseId);
      }

      // Archive old Pulses (older than 7 days)
      this.archiveOldPulses(168);
    }, this.config.update_interval * 1000);
  }

  /**
   * Stop decay updates
   */
  stopDecayUpdates(): void {
    if (this.updateTimer) {
      clearInterval(this.updateTimer);
      this.updateTimer = null;
    }
  }

  /**
   * Update configuration
   */
  setConfig(config: Partial<DecayConfig>): void {
    this.config = { ...this.config, ...config };
    
    // Restart updates with new interval if changed
    if (config.update_interval !== undefined) {
      this.startDecayUpdates();
    }
  }

  /**
   * Get current configuration
   */
  getConfig(): DecayConfig {
    return { ...this.config };
  }

  /**
   * Clear all metrics
   */
  clear(): void {
    this.metrics.clear();
  }
}

// Singleton instance
export const KronosTracker = new KronosTrackerCore();
