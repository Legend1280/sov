import React, { useEffect, useRef, useState } from 'react';
import { usePulse } from '../../core/pulse/usePulse';

interface Node {
  id: string;
  label: string;
  x: number;
  y: number;
  status: 'healthy' | 'warning' | 'error' | 'offline';
  role: string;
  lastPulse?: number;
}

interface Connection {
  from: string;
  to: string;
  active: boolean;
  pulseCount: number;
}

export const SystemHealthVisualizer: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const { pulses } = usePulse('system.*');
  const [nodes, setNodes] = useState<Node[]>([
    { id: 'mirror', label: 'Mirror', x: 150, y: 100, status: 'healthy', role: 'Interface' },
    { id: 'pulsemesh', label: 'PulseMesh', x: 400, y: 100, status: 'healthy', role: 'Relay' },
    { id: 'core', label: 'Core', x: 650, y: 100, status: 'healthy', role: 'Mind' },
    { id: 'sage', label: 'SAGE', x: 250, y: 300, status: 'healthy', role: 'Governor' },
    { id: 'kronos', label: 'Kronos', x: 400, y: 300, status: 'healthy', role: 'Memory' },
    { id: 'shadow', label: 'Shadow', x: 550, y: 300, status: 'healthy', role: 'Witness' },
  ]);
  const [connections, setConnections] = useState<Connection[]>([
    { from: 'mirror', to: 'pulsemesh', active: false, pulseCount: 0 },
    { from: 'pulsemesh', to: 'core', active: false, pulseCount: 0 },
    { from: 'core', to: 'sage', active: false, pulseCount: 0 },
    { from: 'core', to: 'kronos', active: false, pulseCount: 0 },
    { from: 'core', to: 'shadow', active: false, pulseCount: 0 },
    { from: 'sage', to: 'shadow', active: false, pulseCount: 0 },
    { from: 'kronos', to: 'shadow', active: false, pulseCount: 0 },
  ]);
  const [activePulses, setActivePulses] = useState<Array<{ from: string; to: string; progress: number }>>([]);

  // Update node status based on Pulses
  useEffect(() => {
    if (pulses.length === 0) return;

    const latestPulse = pulses[pulses.length - 1];
    const topic = latestPulse.topic;
    const source = latestPulse.source;
    const target = latestPulse.target;

    // Update node status
    setNodes(prev => prev.map(node => {
      if (node.id === source || node.id === target) {
        return { ...node, status: 'healthy', lastPulse: Date.now() };
      }
      return node;
    }));

    // Animate Pulse flow
    if (source && target) {
      setActivePulses(prev => [...prev, { from: source, to: target, progress: 0 }]);
      
      // Update connection
      setConnections(prev => prev.map(conn => {
        if (conn.from === source && conn.to === target) {
          return { ...conn, active: true, pulseCount: conn.pulseCount + 1 };
        }
        return conn;
      }));
    }
  }, [pulses]);

  // Animate Pulses
  useEffect(() => {
    const interval = setInterval(() => {
      setActivePulses(prev => {
        return prev
          .map(pulse => ({ ...pulse, progress: pulse.progress + 0.05 }))
          .filter(pulse => pulse.progress < 1);
      });

      // Deactivate connections after animation
      setConnections(prev => prev.map(conn => ({ ...conn, active: false })));
    }, 50);

    return () => clearInterval(interval);
  }, []);

  // Check for offline nodes (no Pulse in 10 seconds)
  useEffect(() => {
    const interval = setInterval(() => {
      const now = Date.now();
      setNodes(prev => prev.map(node => {
        if (node.lastPulse && now - node.lastPulse > 10000) {
          return { ...node, status: 'offline' };
        }
        return node;
      }));
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  // Draw visualization
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw connections
    connections.forEach(conn => {
      const fromNode = nodes.find(n => n.id === conn.from);
      const toNode = nodes.find(n => n.id === conn.to);
      if (!fromNode || !toNode) return;

      ctx.beginPath();
      ctx.moveTo(fromNode.x, fromNode.y);
      ctx.lineTo(toNode.x, toNode.y);
      ctx.strokeStyle = conn.active ? '#00ffff' : '#334155';
      ctx.lineWidth = conn.active ? 3 : 1;
      ctx.stroke();

      // Draw pulse count
      const midX = (fromNode.x + toNode.x) / 2;
      const midY = (fromNode.y + toNode.y) / 2;
      if (conn.pulseCount > 0) {
        ctx.fillStyle = '#64748b';
        ctx.font = '10px monospace';
        ctx.fillText(`${conn.pulseCount}`, midX, midY);
      }
    });

    // Draw active Pulses
    activePulses.forEach(pulse => {
      const fromNode = nodes.find(n => n.id === pulse.from);
      const toNode = nodes.find(n => n.id === pulse.to);
      if (!fromNode || !toNode) return;

      const x = fromNode.x + (toNode.x - fromNode.x) * pulse.progress;
      const y = fromNode.y + (toNode.y - fromNode.y) * pulse.progress;

      // Draw pulse particle
      ctx.beginPath();
      ctx.arc(x, y, 6, 0, Math.PI * 2);
      ctx.fillStyle = '#00ffff';
      ctx.fill();
      ctx.strokeStyle = '#ffffff';
      ctx.lineWidth = 2;
      ctx.stroke();

      // Glow effect
      ctx.beginPath();
      ctx.arc(x, y, 12, 0, Math.PI * 2);
      ctx.strokeStyle = 'rgba(0, 255, 255, 0.3)';
      ctx.lineWidth = 4;
      ctx.stroke();
    });

    // Draw nodes
    nodes.forEach(node => {
      const statusColors = {
        healthy: '#22c55e',
        warning: '#eab308',
        error: '#ef4444',
        offline: '#64748b',
      };

      // Node circle
      ctx.beginPath();
      ctx.arc(node.x, node.y, 30, 0, Math.PI * 2);
      ctx.fillStyle = '#1e293b';
      ctx.fill();
      ctx.strokeStyle = statusColors[node.status];
      ctx.lineWidth = 3;
      ctx.stroke();

      // Glow effect for healthy nodes
      if (node.status === 'healthy') {
        ctx.beginPath();
        ctx.arc(node.x, node.y, 35, 0, Math.PI * 2);
        ctx.strokeStyle = `rgba(34, 197, 94, 0.3)`;
        ctx.lineWidth = 6;
        ctx.stroke();
      }

      // Node label
      ctx.fillStyle = '#ffffff';
      ctx.font = 'bold 12px monospace';
      ctx.textAlign = 'center';
      ctx.fillText(node.label, node.x, node.y + 5);

      // Role label
      ctx.fillStyle = '#94a3b8';
      ctx.font = '10px monospace';
      ctx.fillText(node.role, node.x, node.y + 50);

      // Status indicator
      ctx.fillStyle = statusColors[node.status];
      ctx.font = '9px monospace';
      ctx.fillText(node.status.toUpperCase(), node.x, node.y + 65);
    });
  }, [nodes, connections, activePulses]);

  const totalPulses = connections.reduce((sum, conn) => sum + conn.pulseCount, 0);
  const healthyNodes = nodes.filter(n => n.status === 'healthy').length;
  const avgHealth = (healthyNodes / nodes.length) * 100;

  // Send test Pulse
  const sendTestPulse = () => {
    const testPulse = {
      id: `pulse_${Date.now()}`,
      topic: 'mirror.intent',
      source: 'mirror',
      target: 'core',
      intent: 'update',
      payload: { message: 'Test Pulse from UI' },
      metadata: { coherence: 0.95, timestamp: new Date().toISOString() },
      status: 'active'
    };
    
    // Simulate Pulse reception
    const syntheticPulse = {
      ...testPulse,
      timestamp: new Date().toISOString()
    };
    
    // Trigger animation
    setActivePulses(prev => [...prev, { from: 'mirror', to: 'core', progress: 0 }]);
    setConnections(prev => prev.map(conn => {
      if (conn.from === 'mirror' && conn.to === 'pulsemesh') {
        return { ...conn, active: true, pulseCount: conn.pulseCount + 1 };
      }
      if (conn.from === 'pulsemesh' && conn.to === 'core') {
        setTimeout(() => {
          setConnections(p => p.map(c => {
            if (c.from === 'pulsemesh' && c.to === 'core') {
              return { ...c, active: true, pulseCount: c.pulseCount + 1 };
            }
            return c;
          }));
        }, 500);
      }
      return conn;
    }));
    
    // Update node status
    setNodes(prev => prev.map(node => {
      if (['mirror', 'pulsemesh', 'core'].includes(node.id)) {
        return { ...node, status: 'healthy', lastPulse: Date.now() };
      }
      return node;
    }));
  };

  return (
    <div className="w-full h-full bg-slate-900 p-6 overflow-hidden">
      <div className="mb-4">
        <div className="flex items-center justify-between mb-2">
          <h2 className="text-2xl font-bold text-cyan-400">System Health Monitor</h2>
          <button
            onClick={sendTestPulse}
            className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded font-mono text-sm transition-colors"
          >
            Send Test Pulse
          </button>
        </div>
        <div className="flex gap-6 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-green-500"></div>
            <span className="text-slate-300">Nodes Online: {healthyNodes}/{nodes.length}</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-cyan-500"></div>
            <span className="text-slate-300">Total Pulses: {totalPulses}</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-blue-500"></div>
            <span className="text-slate-300">System Health: {avgHealth.toFixed(0)}%</span>
          </div>
        </div>
      </div>

      <canvas
        ref={canvasRef}
        width={800}
        height={400}
        className="border border-slate-700 rounded-lg bg-slate-950"
      />

      <div className="mt-4 grid grid-cols-3 gap-4">
        {nodes.map(node => (
          <div
            key={node.id}
            className="bg-slate-800 p-3 rounded border border-slate-700"
          >
            <div className="flex items-center justify-between mb-2">
              <span className="font-bold text-white">{node.label}</span>
              <div
                className={`w-2 h-2 rounded-full ${
                  node.status === 'healthy'
                    ? 'bg-green-500'
                    : node.status === 'warning'
                    ? 'bg-yellow-500'
                    : node.status === 'error'
                    ? 'bg-red-500'
                    : 'bg-slate-500'
                }`}
              ></div>
            </div>
            <div className="text-xs text-slate-400">{node.role}</div>
            <div className="text-xs text-slate-500 mt-1">
              {node.lastPulse
                ? `Last pulse: ${Math.floor((Date.now() - node.lastPulse) / 1000)}s ago`
                : 'No pulses yet'}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
