/**
 * ViewportPulseVisualizer - Live Pulse Stream Monitor
 * 
 * Displays real-time Pulse traffic flowing through PulseMesh
 * Shows source, target, topic, coherence, and payload
 * 
 * Author: Brady Simmons
 * Copyright: © 2025 Sovereignty Foundation. All rights reserved.
 */

import { useState, useEffect, useRef } from 'react';
import { PulseTransport, PulseMessage } from '../../core/pulse/PulseTransport';

interface PulseLogEntry extends PulseMessage {
  id: string;
  _mesh_timestamp?: string;
}

export function ViewportPulseVisualizer() {
  const [log, setLog] = useState<PulseLogEntry[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [stats, setStats] = useState({
    total: 0,
    avgCoherence: 0,
    topicsActive: new Set<string>()
  });
  const transportRef = useRef<PulseTransport | null>(null);

  useEffect(() => {
    // Initialize PulseTransport in mesh mode
    const transport = new PulseTransport({
      mode: 'mesh',
      meshUrl: 'ws://localhost:8088',
      topic: 'mirror.intent'
    });

    transport.connect((msg: PulseMessage) => {
      const entry: PulseLogEntry = {
        ...msg,
        id: `pulse_${Date.now()}_${Math.random()}`
      };

      setLog(prev => {
        const updated = [...prev, entry];
        // Keep only last 100 messages
        if (updated.length > 100) {
          updated.shift();
        }
        return updated;
      });

      // Update stats
      setStats(prev => {
        const newTopics = new Set(prev.topicsActive);
        newTopics.add(msg.topic);
        
        const totalCoherence = prev.avgCoherence * prev.total + (msg.coherence || 0);
        const newTotal = prev.total + 1;
        
        return {
          total: newTotal,
          avgCoherence: totalCoherence / newTotal,
          topicsActive: newTopics
        };
      });
    });

    transportRef.current = transport;

    // Check connection status periodically
    const interval = setInterval(() => {
      setIsConnected(transport.isConnected());
    }, 1000);

    return () => {
      clearInterval(interval);
      transport.disconnect();
    };
  }, []);

  const getIntentColor = (intent?: string) => {
    const colors: Record<string, string> = {
      update: 'text-pink-400',
      query: 'text-blue-400',
      create: 'text-orange-400',
      govern: 'text-green-400',
      reflect: 'text-yellow-400'
    };
    return colors[intent || ''] || 'text-gray-400';
  };

  const getCoherenceColor = (coherence?: number) => {
    if (!coherence) return 'text-gray-500';
    if (coherence >= 0.9) return 'text-green-400';
    if (coherence >= 0.7) return 'text-yellow-400';
    return 'text-red-400';
  };

  return (
    <div className="h-full bg-gray-900 text-gray-100 font-mono text-sm flex flex-col">
      {/* Header */}
      <div className="bg-gray-800 border-b border-gray-700 p-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <h3 className="text-lg font-semibold text-cyan-400">Pulse Stream Monitor</h3>
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`} />
              <span className="text-xs text-gray-400">
                {isConnected ? 'Connected to PulseMesh' : 'Disconnected'}
              </span>
            </div>
          </div>
          
          {/* Stats */}
          <div className="flex gap-4 text-xs">
            <div>
              <span className="text-gray-500">Total: </span>
              <span className="text-cyan-400 font-semibold">{stats.total}</span>
            </div>
            <div>
              <span className="text-gray-500">Avg Coherence: </span>
              <span className={getCoherenceColor(stats.avgCoherence)}>
                {(stats.avgCoherence * 100).toFixed(1)}%
              </span>
            </div>
            <div>
              <span className="text-gray-500">Topics: </span>
              <span className="text-purple-400">{stats.topicsActive.size}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Pulse Log */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        {log.length === 0 ? (
          <div className="text-center text-gray-500 mt-8">
            <p>No pulses yet. Waiting for semantic traffic...</p>
            <p className="text-xs mt-2">Connected to topic: mirror.intent</p>
          </div>
        ) : (
          log.slice().reverse().map((pulse) => (
            <div
              key={pulse.id}
              className="bg-gray-800 border border-gray-700 rounded p-2 hover:border-cyan-600 transition-colors"
            >
              <div className="flex items-center justify-between mb-1">
                <div className="flex items-center gap-2">
                  <span className="text-blue-400 font-semibold">{pulse.source}</span>
                  <span className="text-gray-600">→</span>
                  <span className="text-purple-400 font-semibold">{pulse.target}</span>
                </div>
                
                <div className="flex items-center gap-3 text-xs">
                  {pulse.intent && (
                    <span className={`px-2 py-0.5 rounded ${getIntentColor(pulse.intent)} bg-opacity-20`}>
                      {pulse.intent}
                    </span>
                  )}
                  {pulse.coherence !== undefined && (
                    <span className={getCoherenceColor(pulse.coherence)}>
                      {(pulse.coherence * 100).toFixed(1)}%
                    </span>
                  )}
                  <span className="text-gray-500">
                    {new Date(pulse._mesh_timestamp || pulse.timestamp || Date.now()).toLocaleTimeString()}
                  </span>
                </div>
              </div>
              
              <div className="text-xs">
                <span className="text-gray-500">Topic: </span>
                <span className="text-cyan-300">{pulse.topic}</span>
              </div>
              
              {pulse.payload && (
                <div className="mt-1 text-xs text-gray-400 truncate">
                  <span className="text-gray-600">Payload: </span>
                  {typeof pulse.payload === 'string' 
                    ? pulse.payload 
                    : JSON.stringify(pulse.payload).substring(0, 100)}
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
