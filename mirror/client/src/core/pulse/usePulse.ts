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
}

/**
 * Hook for Pulse communication
 * @param channel - The communication channel (e.g., 'mirror↔core')
 */
export function usePulse(channel: string): UsePulseReturn {
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
      source: pulse.source || channel.split('↔')[0],
      target: pulse.target || channel.split('↔')[1],
    });
  }, [channel]);

  const sendPulse = useCallback((topic: string, payload: any, options?: Partial<PulseObject>) => {
    PulseBridge.send(topic, payload, {
      ...options,
      source: options?.source || channel.split('↔')[0],
      target: options?.target || channel.split('↔')[1],
    });
  }, [channel]);

  const onPulse = useCallback((topic: string, handler: (pulse: PulseObject) => void) => {
    const unsubscribe = PulseBridge.on(topic, handler);
    unsubscribersRef.current.push(unsubscribe);
  }, []);

  return {
    emitPulse,
    sendPulse,
    onPulse,
  };
}
