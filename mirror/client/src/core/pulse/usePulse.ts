/**
 * usePulse - React hook for Pulse communication
 * 
 * Provides a clean interface for components to send and receive Pulses
 * 
 * Author: Brady Simmons
 * Copyright: © 2025 Sovereignty Foundation. All rights reserved.
 */

import { useEffect, useCallback, useRef } from 'react';
import { PulseBridge, PulseObject } from './PulseBridge';

export interface UsePulseReturn {
  emitPulse: (pulse: Partial<PulseObject>) => void;
  sendPulse: (topic: string, payload: any, options?: Partial<PulseObject>) => void;
  onPulse: (topic: string, handler: (pulse: PulseObject) => void) => void;
  pulses: PulseObject[];
  getAllPulses: () => PulseObject[];
}

/**
 * Hook for Pulse communication
 * @param channel - The communication channel (e.g., 'mirror↔core')
 */
export function usePulse(channel?: string): UsePulseReturn {
  const unsubscribersRef = useRef<(() => void)[]>([]);

  // Clean up listeners on unmount
  useEffect(() => {
    return () => {
      unsubscribersRef.current.forEach(unsub => unsub());
      unsubscribersRef.current = [];
    };
  }, []);

  const emitPulse = useCallback((pulse: Partial<PulseObject>) => {
    PulseBridge.emit({
      ...pulse,
      source: pulse.source || (channel ? channel.split('↔')[0] : 'unknown'),
      target: pulse.target || (channel ? channel.split('↔')[1] : 'unknown'),
    });
  }, [channel]);

  const sendPulse = useCallback((topic: string, payload: any, options?: Partial<PulseObject>) => {
    PulseBridge.send(topic, payload, {
      ...options,
      source: options?.source || (channel ? channel.split('↔')[0] : 'unknown'),
      target: options?.target || (channel ? channel.split('↔')[1] : 'unknown'),
    });
  }, [channel]);

  const onPulse = useCallback((topic: string, handler: (pulse: PulseObject) => void) => {
    const unsubscribe = PulseBridge.on(topic, handler);
    unsubscribersRef.current.push(unsubscribe);
  }, []);

  const getAllPulses = useCallback(() => {
    return PulseBridge.getLog();
  }, []);

  return {
    emitPulse,
    sendPulse,
    onPulse,
    pulses: PulseBridge.getLog(), // Direct access
    getAllPulses,
  };
}
