import React, { useState, useEffect } from 'react';
import { usePulse } from '@/core/pulse/usePulse';
import { PulseBridge } from '@/core/pulse/PulseBridge';

interface PulseParticle {
  id: string;
  progress: number;
  direction: 'toCore' | 'toMirror';
  intent: string;
  coherence?: number;
}

export const PulseConnectionVisualizer: React.FC = () => {
  const { getAllPulses } = usePulse();
  const [allPulses, setAllPulses] = useState<any[]>([]);
  const [particles, setParticles] = useState<PulseParticle[]>([]);
  const [stats, setStats] = useState({ sent: 0, received: 0, avgCoherence: 0 });
  const [pingPongPosition, setPingPongPosition] = useState(0);
  const [pingPongDirection, setPingPongDirection] = useState<'forward' | 'backward'>('forward');

  // Animate the ping-pong particle
  useEffect(() => {
    const interval = setInterval(() => {
      setPingPongPosition(prev => {
        if (pingPongDirection === 'forward') {
          if (prev >= 100) {
            setPingPongDirection('backward');
            return 100;
          }
          return prev + 0.5;
        } else {
          if (prev <= 0) {
            setPingPongDirection('forward');
            return 0;
          }
          return prev - 0.5;
        }
      });
    }, 30);
    return () => clearInterval(interval);
  }, [pingPongDirection]);

  // Subscribe to pulse updates using event subscription instead of polling
  useEffect(() => {
    const updatePulses = () => {
      setAllPulses(getAllPulses());
    };
    
    // Initial load
    updatePulses();
    
    // Subscribe to all pulse events for real-time updates
    const unsubscribe = PulseBridge.on('*', updatePulses);
    
    return () => unsubscribe();
  }, [getAllPulses]);

  useEffect(() => {
    // Safety check - pulses might be undefined initially
    if (!allPulses || !Array.isArray(allPulses)) return;

    // Calculate stats from pulses
    const sent = allPulses.filter(p => p.origin === 'mirror').length;
    const received = allPulses.filter(p => p.origin === 'core').length;
    const coherences = allPulses
      .filter(p => p.origin === 'core' && p.coherence !== undefined)
      .map(p => p.coherence!);
    const avgCoherence = coherences.length > 0
      ? (coherences.reduce((a, b) => a + b, 0) / coherences.length) * 100
      : 0;

    setStats({ sent, received, avgCoherence });

    // Create particle for the latest pulse
    if (allPulses.length > 0) {
      const latest = allPulses[allPulses.length - 1];
      const isToCore = latest.origin === 'mirror';
      
      const newParticle: PulseParticle = {
        id: `${latest.timestamp}-${Math.random()}`,
        progress: 0,
        direction: isToCore ? 'toCore' : 'toMirror',
        intent: latest.intent || 'unknown',
        coherence: latest.coherence,
      };

      setParticles(prev => [...prev, newParticle]);

      // Animate particle progress
      let progress = 0;
      const animationInterval = setInterval(() => {
        progress += 2;
        setParticles(prev => 
          prev.map(p => p.id === newParticle.id ? { ...p, progress } : p)
        );
        if (progress >= 100) {
          clearInterval(animationInterval);
          setTimeout(() => {
            setParticles(prev => prev.filter(p => p.id !== newParticle.id));
          }, 500);        };
      }, 20);
    }
  }, [allPulses]);

  const getIntentColor = (intent: string) => {
    switch (intent) {
      case 'update': return { main: '#ec4899', glow: 'rgba(236, 72, 153, 0.6)' }; // pink
      case 'query': return { main: '#3b82f6', glow: 'rgba(59, 130, 246, 0.6)' }; // blue
      case 'create': return { main: '#f97316', glow: 'rgba(249, 115, 22, 0.6)' }; // orange
      case 'govern': return { main: '#10b981', glow: 'rgba(16, 185, 129, 0.6)' }; // green
      case 'reflect': return { main: '#f59e0b', glow: 'rgba(245, 158, 11, 0.6)' }; // amber
      default: return { main: '#8b5cf6', glow: 'rgba(139, 92, 246, 0.6)' }; // purple
    }
  };

  const getCoherenceColor = (coherence?: number) => {
    if (!coherence) return '#6b7280';
    if (coherence >= 90) return '#10b981'; // green
    if (coherence >= 70) return '#f59e0b'; // yellow
    return '#ef4444'; // red
  };

  // Calculate ping-pong particle position
  const pingPongX = 200 + (400 * pingPongPosition / 100);

  return (
    <div className="h-full flex flex-col bg-gradient-to-br from-gray-950 via-gray-900 to-gray-950 text-white p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold mb-2 bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
          Pulse Connection Diagram
        </h2>
        <p className="text-gray-400 text-sm">
          Real-time visualization of semantic communication between Mirror and Core
        </p>
      </div>

      {/* Connection Diagram */}
      <div className="flex-1 relative bg-gray-900/50 rounded-lg border border-gray-800 overflow-hidden backdrop-blur-sm">
        <svg className="w-full h-full" viewBox="0 0 800 400" preserveAspectRatio="xMidYMid meet">
          <defs>
            {/* Glowing gradient for wisps */}
            <radialGradient id="mirrorGlow" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="#3b82f6" stopOpacity="1" />
              <stop offset="50%" stopColor="#3b82f6" stopOpacity="0.6" />
              <stop offset="100%" stopColor="#3b82f6" stopOpacity="0" />
            </radialGradient>
            <radialGradient id="coreGlow" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="#8b5cf6" stopOpacity="1" />
              <stop offset="50%" stopColor="#8b5cf6" stopOpacity="0.6" />
              <stop offset="100%" stopColor="#8b5cf6" stopOpacity="0" />
            </radialGradient>

            {/* Ping-pong particle glow */}
            <radialGradient id="pingPongGlow" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="#60a5fa" stopOpacity="1" />
              <stop offset="50%" stopColor="#60a5fa" stopOpacity="0.6" />
              <stop offset="100%" stopColor="#60a5fa" stopOpacity="0" />
            </radialGradient>

            {/* Glow filter */}
            <filter id="glow">
              <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
              <feMerge>
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="SourceGraphic"/>
              </feMerge>
            </filter>

            {/* Strong glow filter for ping-pong */}
            <filter id="strongGlow">
              <feGaussianBlur stdDeviation="6" result="coloredBlur"/>
              <feMerge>
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="SourceGraphic"/>
              </feMerge>
            </filter>
          </defs>

          {/* Connecting Thread */}
          <line
            x1="200"
            y1="200"
            x2="600"
            y2="200"
            stroke="#374151"
            strokeWidth="2"
            opacity="0.5"
          />

          {/* Mirror Wisp */}
          <g>
            {/* Outer glow */}
            <circle cx="150" cy="200" r="80" fill="url(#mirrorGlow)" opacity="0.4">
              <animate attributeName="r" values="80;90;80" dur="3s" repeatCount="indefinite" />
              <animate attributeName="opacity" values="0.4;0.6;0.4" dur="3s" repeatCount="indefinite" />
            </circle>
            {/* Inner wisp */}
            <circle cx="150" cy="200" r="50" fill="#1f2937" stroke="#3b82f6" strokeWidth="2" filter="url(#glow)">
              <animate attributeName="r" values="50;52;50" dur="2s" repeatCount="indefinite" />
            </circle>
            {/* Core */}
            <circle cx="150" cy="200" r="30" fill="#3b82f6" opacity="0.3">
              <animate attributeName="opacity" values="0.3;0.5;0.3" dur="2s" repeatCount="indefinite" />
            </circle>
            <text x="150" y="200" textAnchor="middle" fill="#3b82f6" fontSize="18" fontWeight="bold" dy="6" filter="url(#glow)">
              Mirror
            </text>
            <text x="150" y="218" textAnchor="middle" fill="#6b7280" fontSize="11">
              UI Layer
            </text>
          </g>

          {/* Core Wisp */}
          <g>
            {/* Outer glow */}
            <circle cx="650" cy="200" r="80" fill="url(#coreGlow)" opacity="0.4">
              <animate attributeName="r" values="80;90;80" dur="3s" repeatCount="indefinite" begin="1.5s" />
              <animate attributeName="opacity" values="0.4;0.6;0.4" dur="3s" repeatCount="indefinite" begin="1.5s" />
            </circle>
            {/* Inner wisp */}
            <circle cx="650" cy="200" r="50" fill="#1f2937" stroke="#8b5cf6" strokeWidth="2" filter="url(#glow)">
              <animate attributeName="r" values="50;52;50" dur="2s" repeatCount="indefinite" begin="1s" />
            </circle>
            {/* Core */}
            <circle cx="650" cy="200" r="30" fill="#8b5cf6" opacity="0.3">
              <animate attributeName="opacity" values="0.3;0.5;0.3" dur="2s" repeatCount="indefinite" begin="1s" />
            </circle>
            <text x="650" y="200" textAnchor="middle" fill="#8b5cf6" fontSize="18" fontWeight="bold" dy="6" filter="url(#glow)">
              Core
            </text>
            <text x="650" y="218" textAnchor="middle" fill="#6b7280" fontSize="11">
              Reasoner
            </text>
          </g>

          {/* Ping-Pong Particle (always visible) */}
          <g>
            {/* Outer glow */}
            <circle
              cx={pingPongX}
              cy="200"
              r="20"
              fill="url(#pingPongGlow)"
              opacity="0.4"
              filter="url(#strongGlow)"
            />
            {/* Inner particle */}
            <circle
              cx={pingPongX}
              cy="200"
              r="6"
              fill="#60a5fa"
              filter="url(#strongGlow)"
            >
              <animate attributeName="r" values="6;8;6" dur="1s" repeatCount="indefinite" />
            </circle>
          </g>

          {/* Animated Pulse Particles */}
          {particles.map(particle => {
            const startX = particle.direction === 'toCore' ? 200 : 600;
            const endX = particle.direction === 'toCore' ? 600 : 200;
            const currentX = startX + (endX - startX) * (particle.progress / 100);
            const colors = getIntentColor(particle.intent);

            return (
              <g key={particle.id}>
                {/* Particle glow */}
                <circle
                  cx={currentX}
                  cy="200"
                  r="15"
                  fill={colors.glow}
                  opacity={0.6}
                  filter="url(#glow)"
                />
                {/* Particle core */}
                <circle
                  cx={currentX}
                  cy="200"
                  r="8"
                  fill={colors.main}
                  filter="url(#glow)"
                />
                {/* Intent label */}
                <text
                  x={currentX}
                  y="180"
                  textAnchor="middle"
                  fill={colors.main}
                  fontSize="10"
                  fontWeight="bold"
                  filter="url(#glow)"
                >
                  {particle.intent}
                </text>
              </g>
            );
          })}
        </svg>
      </div>

      {/* Stats Panel */}
      <div className="mt-6 grid grid-cols-3 gap-4">
        <div className="bg-gray-900/50 rounded-lg p-4 border border-gray-800 backdrop-blur-sm">
          <div className="text-xs text-gray-400 mb-2 uppercase tracking-wider">Pulses Sent</div>
          <div className="text-3xl font-bold text-blue-400">{stats.sent}</div>
        </div>
        <div className="bg-gray-900/50 rounded-lg p-4 border border-gray-800 backdrop-blur-sm">
          <div className="text-xs text-gray-400 mb-2 uppercase tracking-wider">Pulses Received</div>
          <div className="text-3xl font-bold text-purple-400">{stats.received}</div>
        </div>
        <div className="bg-gray-900/50 rounded-lg p-4 border border-gray-800 backdrop-blur-sm">
          <div className="text-xs text-gray-400 mb-2 uppercase tracking-wider">Avg Coherence</div>
          <div 
            className="text-3xl font-bold"
            style={{ color: getCoherenceColor(stats.avgCoherence) }}
          >
            {stats.avgCoherence.toFixed(1)}%
          </div>
        </div>
      </div>

      {/* Legend */}
      <div className="mt-4 flex gap-4 text-sm justify-center">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-pink-500 shadow-lg shadow-pink-500/50"></div>
          <span className="text-gray-400">Update</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-blue-500 shadow-lg shadow-blue-500/50"></div>
          <span className="text-gray-400">Query</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-orange-500 shadow-lg shadow-orange-500/50"></div>
          <span className="text-gray-400">Create</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-green-500 shadow-lg shadow-green-500/50"></div>
          <span className="text-gray-400">Govern</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-amber-500 shadow-lg shadow-amber-500/50"></div>
          <span className="text-gray-400">Reflect</span>
        </div>
      </div>
    </div>
  );
};
