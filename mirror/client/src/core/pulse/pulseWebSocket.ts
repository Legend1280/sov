/**
 * Pulse WebSocket Connection (Secure)
 * 
 * Establishes and maintains WebSocket connection to PulseMesh
 * with signature-based authentication
 * 
 * Author: Brady Simmons
 * Copyright: © 2025 Sovereignty Foundation. All rights reserved.
 */

const PULSE_MESH_URL = 'ws://localhost:8088/ws/mesh';
const RECONNECT_DELAY = 3000;
const SECRET_KEY = 'mirror:logos:2025';

// Generate SHA256 signature for handshake
async function generateSignature(message: any): Promise<string> {
  const messageStr = JSON.stringify(message, Object.keys(message).sort());
  const data = messageStr + SECRET_KEY;
  const encoder = new TextEncoder();
  const dataBuffer = encoder.encode(data);
  const hashBuffer = await crypto.subtle.digest('SHA-256', dataBuffer);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
  return hashHex;
}

export function initializePulseWebSocket(topic: string = 'mirror.intent') {
  let ws: WebSocket | null = null;
  let reconnectTimeout: NodeJS.Timeout | null = null;
  let isAuthenticated = false;

  async function connect() {
    try {
      const wsUrl = `${PULSE_MESH_URL}/${topic}`;
      ws = new WebSocket(wsUrl);

      ws.onopen = async () => {
        console.log(`[PulseWS] Connected to PulseMesh topic: ${topic}`);
        
        // Send secure handshake
        const handshakeMessage = {
          source: 'mirror',
          target: 'pulsemesh',
          timestamp: new Date().toISOString()
        };
        
        const signature = await generateSignature(handshakeMessage);
        
        const handshake = {
          message: handshakeMessage,
          signature: signature
        };
        
        console.log('[PulseWS] Sending handshake...');
        ws?.send(JSON.stringify(handshake));
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log('[PulseWS] Received:', data);

          // Handle handshake confirmation
          if (data.type === 'handshake_ok') {
            console.log('[PulseWS] ✅ Handshake successful!', data.client_id);
            isAuthenticated = true;
            (window as any).__PULSE_WS__ = ws;
            return;
          }

          // Handle Pulse events
          if (data.type === 'pulse_event') {
            console.log(`[PulseWS] Received Pulse: ${data.topic}`, data.payload);
            // Dispatch to local PulseBridge listeners
            if ((window as any).__PULSE_BRIDGE__) {
              (window as any).__PULSE_BRIDGE__.handleRemotePulse(data);
            }
            return;
          }

          // Handle errors
          if (data.type === 'error') {
            console.error('[PulseWS] Error:', data.message);
            return;
          }

        } catch (error) {
          console.error('[PulseWS] Failed to parse message:', error);
        }
      };

      ws.onerror = (error) => {
        console.error('[PulseWS] WebSocket error:', error);
      };

      ws.onclose = (event) => {
        console.log(`[PulseWS] Disconnected (code: ${event.code})`);
        (window as any).__PULSE_WS__ = null;
        isAuthenticated = false;
        
        // Handle specific close codes
        if (event.code === 4003) {
          console.error('[PulseWS] ❌ Invalid signature - authentication failed');
          return; // Don't reconnect on auth failure
        }
        
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
