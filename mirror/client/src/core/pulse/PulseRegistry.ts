/**
 * Pulse Registry - Central index of all PulseObjects
 * 
 * Provides a centralized, indexed store for all PulseObjects.
 * Tracks coherence drift and provides query capabilities.
 * 
 * Author: Brady Simmons
 * Copyright: © 2025 Sovereignty Foundation. All rights reserved.
 */

import { PulseObject, PulseIntent, PulseStatus } from './PulseBridge';
import { KronosTracker } from '../kronos/KronosTracker';

export interface CoherenceDrift {
  pulse_id: string;
  initial_coherence: number;
  current_coherence: number;
  drift: number;              // Absolute change
  drift_percent: number;      // Percentage change
  trend: 'increasing' | 'decreasing' | 'stable';
  measurements: Array<{
    timestamp: string;
    coherence: number;
  }>;
}

export interface PulseQuery {
  origin?: string;
  target?: string;
  intent?: PulseIntent;
  status?: PulseStatus;
  min_coherence?: number;
  max_coherence?: number;
  since?: string;            // ISO timestamp
  until?: string;            // ISO timestamp
}

class PulseRegistryCore {
  private pulses: Map<string, PulseObject> = new Map();
  private coherenceMeasurements: Map<string, Array<{ timestamp: string; coherence: number }>> = new Map();
  private maxPulses = 10000;  // Maximum number of pulses to keep in memory

  /**
   * Register a new Pulse
   */
  register(pulse: PulseObject): void {
    this.pulses.set(pulse.id, pulse);

    // Initialize coherence measurements
    if (!this.coherenceMeasurements.has(pulse.id)) {
      this.coherenceMeasurements.set(pulse.id, []);
    }

    // Record initial coherence
    this.recordCoherence(pulse.id, pulse.coherence);

    // Cleanup old pulses if we exceed max
    if (this.pulses.size > this.maxPulses) {
      this.cleanupOldPulses();
    }
  }

  /**
   * Update an existing Pulse
   */
  update(pulseId: string, updates: Partial<PulseObject>): PulseObject | null {
    const pulse = this.pulses.get(pulseId);
    if (!pulse) return null;

    const updatedPulse = { ...pulse, ...updates };
    this.pulses.set(pulseId, updatedPulse);

    // Record coherence if it changed
    if (updates.coherence !== undefined && updates.coherence !== pulse.coherence) {
      this.recordCoherence(pulseId, updates.coherence);
    }

    return updatedPulse;
  }

  /**
   * Get a Pulse by ID
   */
  get(pulseId: string): PulseObject | null {
    return this.pulses.get(pulseId) || null;
  }

  /**
   * Query Pulses
   */
  query(query: PulseQuery): PulseObject[] {
    let results = Array.from(this.pulses.values());

    if (query.origin) {
      results = results.filter(p => p.origin === query.origin);
    }

    if (query.target) {
      results = results.filter(p => p.target === query.target);
    }

    if (query.intent) {
      results = results.filter(p => p.intent === query.intent);
    }

    if (query.status) {
      results = results.filter(p => p.status === query.status);
    }

    if (query.min_coherence !== undefined) {
      results = results.filter(p => p.coherence >= query.min_coherence!);
    }

    if (query.max_coherence !== undefined) {
      results = results.filter(p => p.coherence <= query.max_coherence!);
    }

    if (query.since) {
      results = results.filter(p => p.timestamp >= query.since!);
    }

    if (query.until) {
      results = results.filter(p => p.timestamp <= query.until!);
    }

    return results;
  }

  /**
   * Get all Pulses
   */
  getAll(): PulseObject[] {
    return Array.from(this.pulses.values());
  }

  /**
   * Get Pulse count
   */
  count(): number {
    return this.pulses.size;
  }

  /**
   * Record a coherence measurement
   */
  private recordCoherence(pulseId: string, coherence: number): void {
    const measurements = this.coherenceMeasurements.get(pulseId) || [];
    measurements.push({
      timestamp: new Date().toISOString(),
      coherence
    });
    this.coherenceMeasurements.set(pulseId, measurements);
  }

  /**
   * Get coherence drift for a Pulse
   */
  getCoherenceDrift(pulseId: string): CoherenceDrift | null {
    const pulse = this.pulses.get(pulseId);
    const measurements = this.coherenceMeasurements.get(pulseId);

    if (!pulse || !measurements || measurements.length === 0) {
      return null;
    }

    const initial = measurements[0].coherence;
    const current = measurements[measurements.length - 1].coherence;
    const drift = current - initial;
    const driftPercent = initial !== 0 ? (drift / initial) * 100 : 0;

    let trend: 'increasing' | 'decreasing' | 'stable' = 'stable';
    if (Math.abs(driftPercent) > 5) {
      trend = drift > 0 ? 'increasing' : 'decreasing';
    }

    return {
      pulse_id: pulseId,
      initial_coherence: initial,
      current_coherence: current,
      drift,
      drift_percent: driftPercent,
      trend,
      measurements: [...measurements]
    };
  }

  /**
   * Get all Pulses with significant coherence drift
   */
  getPulsesWithDrift(minDriftPercent: number = 10): CoherenceDrift[] {
    const drifts: CoherenceDrift[] = [];

    for (const pulseId of this.pulses.keys()) {
      const drift = this.getCoherenceDrift(pulseId);
      if (drift && Math.abs(drift.drift_percent) >= minDriftPercent) {
        drifts.push(drift);
      }
    }

    return drifts.sort((a, b) => Math.abs(b.drift_percent) - Math.abs(a.drift_percent));
  }

  /**
   * Get average coherence across all Pulses
   */
  getAverageCoherence(): number {
    const pulses = Array.from(this.pulses.values());
    if (pulses.length === 0) return 0;

    const sum = pulses.reduce((acc, p) => acc + p.coherence, 0);
    return sum / pulses.length;
  }

  /**
   * Get statistics
   */
  getStatistics(): {
    total: number;
    by_status: Record<PulseStatus, number>;
    by_intent: Record<PulseIntent, number>;
    avg_coherence: number;
    coherence_range: { min: number; max: number };
  } {
    const pulses = Array.from(this.pulses.values());

    const byStatus: Record<PulseStatus, number> = {
      active: 0,
      decayed: 0,
      terminated: 0
    };

    const byIntent: Record<PulseIntent, number> = {
      update: 0,
      query: 0,
      create: 0,
      govern: 0,
      reflect: 0
    };

    let minCoherence = 1;
    let maxCoherence = 0;
    let sumCoherence = 0;

    for (const pulse of pulses) {
      byStatus[pulse.status]++;
      byIntent[pulse.intent]++;
      sumCoherence += pulse.coherence;
      minCoherence = Math.min(minCoherence, pulse.coherence);
      maxCoherence = Math.max(maxCoherence, pulse.coherence);
    }

    return {
      total: pulses.length,
      by_status: byStatus,
      by_intent: byIntent,
      avg_coherence: pulses.length > 0 ? sumCoherence / pulses.length : 0,
      coherence_range: { min: minCoherence, max: maxCoherence }
    };
  }

  /**
   * Cleanup old pulses (remove oldest ones)
   */
  private cleanupOldPulses(): void {
    const pulses = Array.from(this.pulses.values());
    
    // Sort by timestamp (oldest first)
    pulses.sort((a, b) => a.timestamp.localeCompare(b.timestamp));

    // Remove oldest 10%
    const toRemove = Math.floor(pulses.length * 0.1);
    for (let i = 0; i < toRemove; i++) {
      this.pulses.delete(pulses[i].id);
      this.coherenceMeasurements.delete(pulses[i].id);
    }

    console.log(`[PulseRegistry] Cleaned up ${toRemove} old pulses`);
  }

  /**
   * Clear all Pulses
   */
  clear(): void {
    this.pulses.clear();
    this.coherenceMeasurements.clear();
  }
}

// Singleton instance
export const PulseRegistry = new PulseRegistryCore();
