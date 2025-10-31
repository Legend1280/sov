/**
 * MirrorPulseViewer - Live visualization of Pulse communication
 * 
 * Displays a real-time stream of Pulse objects flowing between Mirror and Core,
 * showing semantic coherence scores and temporal decay.
 * 
 * Author: Brady Simmons
 * Copyright: © 2025 Sovereignty Foundation. All rights reserved.
 */

import { useState, useEffect } from 'react';
import { usePulse } from '@/core/pulse/usePulse';
import { PulseObject, PulseBridge } from '@/core/pulse/PulseBridge';
import { Button } from '@/components/ui/button';

export function MirrorPulseViewer() {
  const [log, setLog] = useState<PulseObject[]>([]);
  const [inputText, setInputText] = useState('');
  const { sendPulse, onPulse } = usePulse('mirror↔core');

  // Listen to all Pulses
  useEffect(() => {
    onPulse('*', (pulse: PulseObject) => {
      setLog(prev => [pulse, ...prev].slice(0, 50)); // Keep last 50 pulses
    });
  }, [onPulse]);

  const handleSendIntent = () => {
    if (!inputText.trim()) return;

    sendPulse('intent:update', { text: inputText });
    setInputText('');
  };

  const handleSendQuery = () => {
    if (!inputText.trim()) return;

    sendPulse('intent:query', { text: inputText });
    setInputText('');
  };

  const handleSendCreate = () => {
    if (!inputText.trim()) return;

    sendPulse('intent:create', { text: inputText });
    setInputText('');
  };

  const getCoherenceColor = (coherence?: number): string => {
    if (!coherence) return 'text-muted-foreground';
    if (coherence >= 0.9) return 'text-green-500';
    if (coherence >= 0.7) return 'text-yellow-500';
    return 'text-red-500';
  };

  const getSourceColor = (source: string): string => {
    switch (source) {
      case 'mirror':
        return 'text-blue-400';
      case 'core':
        return 'text-purple-400';
      case 'sage':
        return 'text-green-400';
      default:
        return 'text-gray-400';
    }
  };

  return (
    <div className="h-full flex flex-col bg-background">
      {/* Header */}
      <div className="px-6 py-4 border-b border-border">
        <h2 className="text-2xl font-bold mb-2">Pulse Stream</h2>
        <p className="text-sm text-muted-foreground">
          Live semantic communication between Mirror and Core
        </p>
      </div>

      {/* Input Area */}
      <div className="px-6 py-4 border-b border-border bg-card">
        <div className="flex gap-2 mb-2">
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSendIntent()}
            placeholder="Enter message to send to Core..."
            className="flex-1 px-3 py-2 bg-background border border-input rounded-md text-sm"
          />
        </div>
        <div className="flex gap-2">
          <Button onClick={handleSendIntent} size="sm" variant="default">
            Send Update
          </Button>
          <Button onClick={handleSendQuery} size="sm" variant="secondary">
            Send Query
          </Button>
          <Button onClick={handleSendCreate} size="sm" variant="outline">
            Send Create
          </Button>
          <Button 
            onClick={() => {
              PulseBridge.clearLog();
              setLog([]);
            }} 
            size="sm" 
            variant="ghost"
            className="ml-auto"
          >
            Clear Log
          </Button>
        </div>
      </div>

      {/* Pulse Log */}
      <div className="flex-1 overflow-y-auto px-6 py-4 font-mono text-sm">
        {log.length === 0 ? (
          <div className="text-center text-muted-foreground py-8">
            No pulses yet. Send a message to start the semantic loop.
          </div>
        ) : (
          <div className="space-y-2">
            {log.map((pulse) => (
              <div
                key={pulse.id}
                className="p-3 bg-card border border-border rounded-md hover:bg-accent/50 transition-colors"
              >
                <div className="flex items-start justify-between mb-1">
                  <div className="flex items-center gap-2">
                    <span className={`font-semibold ${getSourceColor(pulse.source)}`}>
                      {pulse.source}
                    </span>
                    <span className="text-muted-foreground">→</span>
                    <span className={`font-semibold ${getSourceColor(pulse.target)}`}>
                      {pulse.target}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    {pulse.coherence !== undefined && (
                      <span className={`text-xs font-semibold ${getCoherenceColor(pulse.coherence)}`}>
                        {(pulse.coherence * 100).toFixed(0)}%
                      </span>
                    )}
                    <span className="text-xs text-muted-foreground">
                      {new Date(pulse.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                </div>
                <div className="text-xs text-muted-foreground mb-1">
                  [{pulse.topic}]
                </div>
                {pulse.payload && (
                  <div className="text-xs bg-background/50 p-2 rounded border border-border/50 mt-2">
                    <pre className="whitespace-pre-wrap break-words">
                      {typeof pulse.payload === 'string'
                        ? pulse.payload
                        : JSON.stringify(pulse.payload, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Stats Footer */}
      <div className="px-6 py-3 border-t border-border bg-card">
        <div className="flex items-center justify-between text-xs text-muted-foreground">
          <span>Total Pulses: {log.length}</span>
          <span>
            Avg Coherence:{' '}
            {log.length > 0
              ? (
                  (log.reduce((sum, p) => sum + (p.coherence || 0), 0) / log.length) *
                  100
                ).toFixed(1)
              : '0'}
            %
          </span>
        </div>
      </div>
    </div>
  );
}
