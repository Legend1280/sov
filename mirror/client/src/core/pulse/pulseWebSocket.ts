/**
 * Pulse WebSocket Connection
 * 
 * Establishes and maintains WebSocket connection to Core's PulseBus
 * Enables schema-native, event-driven communication
 * 
 * Author: Brady Simmons
 * Copyright: © 2025 Sovereignty Foundation. All rights reserved.
 */

const PULSE_WS_URL = 'ws://localhost:8000/ws/pulse';
const RECONNECT_DELAY = 3000;

export function initializePulseWebSocket() {
  let ws: WebSocket | null = null;
  let reconnectTimeout: NodeJS.Timeout | null = null;

  function connect() {
    try {
      ws = new WebSocket(PULSE_WS_URL);

      ws.onopen = () => {
        console.log('[PulseWS] Connected to Core PulseBus');
        (window as any).__PULSE_WS__ = ws;
        
        // Send ping to verify connection
        ws?.send(JSON.stringify({ type: 'ping' }));
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log('[PulseWS] Received:', data);

          // Handle different message types
          switch (data.type) {
            case 'pong':
              console.log('[PulseWS] Connection alive');
              break;
            case 'pulse_ack':
              console.log(`[PulseWS] Pulse acknowledged: ${data.event_id}`);
              if (data.errors) {
                console.warn('[PulseWS] Validation errors:', data.errors);
              }
              break;
            case 'pulse_event':
              console.log(`[PulseWS] Received Pulse event: ${data.topic}`);
              // Future: Dispatch to local PulseBridge listeners
              break;
            case 'error':
              console.error('[PulseWS] Error:', data.message);
              break;
            default:
              console.log('[PulseWS] Unknown message type:', data.type);
          }
        } catch (error) {
          console.error('[PulseWS] Failed to parse message:', error);
        }
      };

      ws.onerror = (error) => {
        console.error('[PulseWS] WebSocket error:', error);
      };

      ws.onclose = () => {
        console.log('[PulseWS] Disconnected from Core PulseBus');
        (window as any).__PULSE_WS__ = null;
        
        // Attempt to reconnect
        if (reconnectTimeout) {
          clearTimeout(reconnectTimeout);
        }
        reconnectTimeout = setTimeout(() => {
          console.log('[PulseWS] Attempting to reconnect...');
          connect();
        }, RECONNECT_DELAY);
      };

    } catch (error) {
      console.error('[PulseWS] Failed to create WebSocket:', error);
      
      // Retry connection
      if (reconnectTimeout) {
        clearTimeout(reconnectTimeout);
      }
      reconnectTimeout = setTimeout(connect, RECONNECT_DELAY);
    }
  }

  // Initial connection
  connect();

  // Return cleanup function
  return () => {
    if (reconnectTimeout) {
      clearTimeout(reconnectTimeout);
    }
    if (ws) {
      ws.close();
      (window as any).__PULSE_WS__ = null;
    }
  };
}
