/**
 * PulseTransport - Transport abstraction layer for Pulse communication
 * 
 * Supports multiple transport modes:
 * - Local: In-process PulseBridge (for UI reactivity)
 * - WebSocket: Direct WebSocket to Core (for single-node deployment)
 * - Mesh: PulseMesh relay (for distributed deployment)
 * 
 * Author: Brady Simmons
 * Copyright: © 2025 Sovereignty Foundation. All rights reserved.
 */

export type TransportMode = 'local' | 'websocket' | 'mesh';

export interface PulseMessage {
  source: string;
  target: string;
  topic: string;
  intent?: string;
  payload: any;
  coherence?: number;
  timestamp?: string;
  metadata?: Record<string, any>;
}

export interface TransportConfig {
  mode: TransportMode;
  meshUrl?: string;
  wsUrl?: string;
  topic?: string;
  nodeId?: string;
}

export class PulseTransport {
  private ws?: WebSocket;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 10;
  private reconnectDelay = 3000;
  private messageHandlers: Set<(msg: PulseMessage) => void> = new Set();
  
  constructor(private config: TransportConfig) {}

  /**
   * Connect to the transport layer
   */
  connect(onMessage: (msg: PulseMessage) => void): void {
    this.messageHandlers.add(onMessage);

    if (this.config.mode === 'local') {
      // Local mode: Use in-process PulseBridge
      console.log('[PulseTransport] Using local PulseBridge');
      return;
    }

    if (this.config.mode === 'mesh') {
      this.connectToMesh();
    } else if (this.config.mode === 'websocket') {
      this.connectToWebSocket();
    }
  }

  /**
   * Connect to PulseMesh relay
   */
  private connectToMesh(): void {
    const meshUrl = this.config.meshUrl || 'ws://localhost:8088';
    const topic = this.config.topic || 'mirror.intent';
    const url = `${meshUrl}/ws/mesh/${topic}`;

    console.log(`[PulseTransport] Connecting to PulseMesh: ${url}`);

    try {
      this.ws = new WebSocket(url);

      this.ws.onopen = () => {
        console.log(`[PulseTransport] Connected to PulseMesh topic: ${topic}`);
        this.reconnectAttempts = 0;
      };

      this.ws.onmessage = (event) => {
        try {
          const message: PulseMessage = JSON.parse(event.data);
          console.log('[PulseTransport] Received:', message);
          
          // Notify all handlers
          this.messageHandlers.forEach(handler => handler(message));
        } catch (error) {
          console.error('[PulseTransport] Failed to parse message:', error);
        }
      };

      this.ws.onerror = (error) => {
        console.error('[PulseTransport] WebSocket error:', error);
      };

      this.ws.onclose = () => {
        console.log('[PulseTransport] Disconnected from PulseMesh');
        this.attemptReconnect();
      };

    } catch (error) {
      console.error('[PulseTransport] Failed to create WebSocket:', error);
      this.attemptReconnect();
    }
  }

  /**
   * Connect to Core WebSocket directly
   */
  private connectToWebSocket(): void {
    const wsUrl = this.config.wsUrl || 'ws://localhost:8000/ws/pulse';
    
    console.log(`[PulseTransport] Connecting to Core WebSocket: ${wsUrl}`);

    try {
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        console.log('[PulseTransport] Connected to Core WebSocket');
        this.reconnectAttempts = 0;
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log('[PulseTransport] Received:', data);
          
          // Handle different message types
          if (data.type === 'pulse_event') {
            const message: PulseMessage = data.payload;
            this.messageHandlers.forEach(handler => handler(message));
          }
        } catch (error) {
          console.error('[PulseTransport] Failed to parse message:', error);
        }
      };

      this.ws.onerror = (error) => {
        console.error('[PulseTransport] WebSocket error:', error);
      };

      this.ws.onclose = () => {
        console.log('[PulseTransport] Disconnected from Core WebSocket');
        this.attemptReconnect();
      };

    } catch (error) {
      console.error('[PulseTransport] Failed to create WebSocket:', error);
      this.attemptReconnect();
    }
  }

  /**
   * Attempt to reconnect after disconnect
   */
  private attemptReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('[PulseTransport] Max reconnect attempts reached');
      return;
    }

    this.reconnectAttempts++;
    console.log(`[PulseTransport] Reconnecting in ${this.reconnectDelay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);

    setTimeout(() => {
      if (this.config.mode === 'mesh') {
        this.connectToMesh();
      } else if (this.config.mode === 'websocket') {
        this.connectToWebSocket();
      }
    }, this.reconnectDelay);
  }

  /**
   * Emit a Pulse message
   */
  emit(pulse: PulseMessage): void {
    if (this.config.mode === 'local') {
      // Local mode: Use PulseBridge
      console.log('[PulseTransport] Emitting locally:', pulse);
      return;
    }

    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.warn('[PulseTransport] WebSocket not connected, cannot emit');
      return;
    }

    try {
      this.ws.send(JSON.stringify(pulse));
      console.log('[PulseTransport] Emitted:', pulse);
    } catch (error) {
      console.error('[PulseTransport] Failed to emit:', error);
    }
  }

  /**
   * Disconnect from transport
   */
  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = undefined;
    }
    this.messageHandlers.clear();
    console.log('[PulseTransport] Disconnected');
  }

  /**
   * Check if transport is connected
   */
  isConnected(): boolean {
    if (this.config.mode === 'local') {
      return true;
    }
    return this.ws?.readyState === WebSocket.OPEN;
  }
}
