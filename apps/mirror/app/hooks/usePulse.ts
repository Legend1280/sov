import { useEffect } from 'react';
import { subscribeToPulse } from '../lib/PulseClient';

/**
 * usePulse - React hook for subscribing to Pulse events
 * 
 * Usage:
 *   usePulse('mirror.theme.changed', (payload) => {
 *     console.log('Theme changed:', payload);
 *   });
 * 
 * The hook automatically unsubscribes when the component unmounts.
 */
export function usePulse(event: string, handler: (payload: any) => void) {
  useEffect(() => {
    const unsubscribe = subscribeToPulse(event, handler);

    return () => {
      unsubscribe();
    };
  }, [event, handler]);
}

export default usePulse;
