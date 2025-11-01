/**
 * Semantic Instantiation Demo
 * 
 * Demonstrates the holy grail of the Sovereignty Stack:
 * Declarative semantic instantiation of ontological objects.
 * 
 * This page shows how to "speak" Logos into existence and see it
 * render as a governed, first-class object with complete lifecycle tracking.
 * 
 * Author: Brady Simmons
 * Copyright: © 2025 Sovereignty Foundation. All rights reserved.
 */

import React, { useEffect, useState } from 'react';
import { View, Text, ScrollView, StyleSheet } from 'react-native';
import ObjectRenderer from '@/components/ObjectRenderer';
import { ObjectLifecycle, LifecycleEvent } from '@/lib/ObjectLifecycle';
import { SchemaLoader } from '@/lib/SchemaLoader';

export default function SemanticInstantiationDemo() {
  const [lifecycleEvents, setLifecycleEvents] = useState<LifecycleEvent[]>([]);
  const [stats, setStats] = useState(ObjectLifecycle.getStats());

  // Subscribe to all lifecycle events
  useEffect(() => {
    const phases = [
      'loading', 'loaded', 'rendering', 'rendered',
      'interacted', 'updated', 'unmounting', 'unmounted', 'error'
    ] as const;

    const unsubscribers = phases.map(phase =>
      ObjectLifecycle.on(phase, (event) => {
        setLifecycleEvents(prev => [...prev, event]);
        setStats(ObjectLifecycle.getStats());
      })
    );

    return () => {
      unsubscribers.forEach(unsub => unsub());
    };
  }, []);

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Semantic Instantiation Demo</Text>
        <Text style={styles.subtitle}>
          Declarative rendering of ontological objects
        </Text>
      </View>

      {/* Demonstration Section */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>🎯 Live Demonstration</Text>
        <Text style={styles.description}>
          The component below is not hardcoded — it's instantiated from the
          Logos ontology object definition in Core. Watch the lifecycle events
          as it materializes.
        </Text>

        <View style={styles.demoBox}>
          <ObjectRenderer 
            object="logos" 
            props={{ mode: 'login' }}
            onLoad={(obj) => console.log('Logos loaded:', obj)}
            onError={(err) => console.error('Logos error:', err)}
          />
        </View>
      </View>

      {/* Statistics Section */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>📊 Lifecycle Statistics</Text>
        <View style={styles.statsBox}>
          <StatRow label="Active Objects" value={stats.activeObjects} />
          <StatRow label="Total Events" value={stats.totalEvents} />
          
          {Object.entries(stats.phaseDistribution || {}).map(([phase, count]) => (
            <StatRow 
              key={phase} 
              label={`  ${phase}`} 
              value={count}
              indent 
            />
          ))}
        </View>
      </View>

      {/* Event Log Section */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>📝 Lifecycle Event Log</Text>
        <Text style={styles.description}>
          All events are emitted as Pulses and can be validated by SAGE,
          indexed by Kronos, and logged by Shadow.
        </Text>
        
        <View style={styles.logBox}>
          {lifecycleEvents.length === 0 ? (
            <Text style={styles.logEmpty}>No events yet...</Text>
          ) : (
            lifecycleEvents.slice(-10).reverse().map((event, index) => (
              <LogEntry key={index} event={event} />
            ))
          )}
        </View>
      </View>

      {/* Explanation Section */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>💡 What's Happening</Text>
        <Text style={styles.explanation}>
          1. <Text style={styles.bold}>ObjectRenderer</Text> receives "logos" as the object ID
          {'\n\n'}
          2. Fetches the Logos ontology definition from Core
          {'\n\n'}
          3. Resolves the <Text style={styles.bold}>ui_binding</Text> to LogosLoginButton component
          {'\n\n'}
          4. Emits lifecycle Pulses (loading → loaded → rendering → rendered)
          {'\n\n'}
          5. Dynamically imports and renders the component
          {'\n\n'}
          6. Passes ontology context and PulseBridge to component
          {'\n\n'}
          7. Component communicates via Pulses (logos.authenticate, etc.)
          {'\n\n'}
          This is <Text style={styles.bold}>declarative semantic instantiation</Text> — 
          you're not coding a button, you're manifesting identity as a 
          governed ontological object.
        </Text>
      </View>

      {/* Schema Example */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>📋 Schema Definition</Text>
        <View style={styles.codeBox}>
          <Text style={styles.code}>
{`{
  "type": "Viewport",
  "id": "home",
  "children": [
    {
      "type": "Logos",
      "props": { "mode": "login" }
    }
  ]
}`}
          </Text>
        </View>
        <Text style={styles.description}>
          This schema tells Mirror to render the Logos object. The ObjectRenderer
          handles the rest — fetching, resolving, and instantiating.
        </Text>
      </View>
    </ScrollView>
  );
}

// Helper Components

function StatRow({ 
  label, 
  value, 
  indent = false 
}: { 
  label: string; 
  value: number; 
  indent?: boolean;
}) {
  return (
    <View style={[styles.statRow, indent && styles.statRowIndent]}>
      <Text style={styles.statLabel}>{label}</Text>
      <Text style={styles.statValue}>{value}</Text>
    </View>
  );
}

function LogEntry({ event }: { event: LifecycleEvent }) {
  const phaseEmoji: Record<string, string> = {
    loading: '⏳',
    loaded: '✅',
    rendering: '🎨',
    rendered: '🖼️',
    interacted: '👆',
    updated: '🔄',
    unmounting: '⏸️',
    unmounted: '💤',
    error: '❌'
  };

  const emoji = phaseEmoji[event.phase] || '📍';
  const time = new Date(event.timestamp).toLocaleTimeString();

  return (
    <View style={styles.logEntry}>
      <Text style={styles.logEmoji}>{emoji}</Text>
      <View style={styles.logContent}>
        <Text style={styles.logPhase}>{event.phase}</Text>
        <Text style={styles.logObject}>{event.object_id}</Text>
        {event.component && (
          <Text style={styles.logComponent}>[{event.component}]</Text>
        )}
      </View>
      <Text style={styles.logTime}>{time}</Text>
    </View>
  );
}

// Styles

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFFFFF'
  },
  header: {
    padding: 24,
    backgroundColor: '#00A3FF',
    borderBottomWidth: 4,
    borderBottomColor: '#0088CC'
  },
  title: {
    fontSize: 28,
    fontWeight: '700',
    color: '#FFFFFF',
    marginBottom: 8
  },
  subtitle: {
    fontSize: 16,
    color: '#E0F2FF',
    fontWeight: '500'
  },
  section: {
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#E0E0E0'
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: '#333',
    marginBottom: 12
  },
  description: {
    fontSize: 15,
    color: '#666',
    lineHeight: 22,
    marginBottom: 16
  },
  explanation: {
    fontSize: 15,
    color: '#666',
    lineHeight: 24
  },
  bold: {
    fontWeight: '700',
    color: '#333'
  },
  demoBox: {
    padding: 20,
    backgroundColor: '#F8F9FA',
    borderRadius: 12,
    borderWidth: 2,
    borderColor: '#00A3FF',
    borderStyle: 'dashed'
  },
  statsBox: {
    backgroundColor: '#F8F9FA',
    borderRadius: 8,
    padding: 16
  },
  statRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#E0E0E0'
  },
  statRowIndent: {
    paddingLeft: 16
  },
  statLabel: {
    fontSize: 15,
    color: '#666',
    fontWeight: '500'
  },
  statValue: {
    fontSize: 15,
    color: '#00A3FF',
    fontWeight: '700'
  },
  logBox: {
    backgroundColor: '#1E1E1E',
    borderRadius: 8,
    padding: 16,
    maxHeight: 400
  },
  logEmpty: {
    fontSize: 14,
    color: '#888',
    fontStyle: 'italic',
    textAlign: 'center'
  },
  logEntry: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#333'
  },
  logEmoji: {
    fontSize: 18,
    marginRight: 12
  },
  logContent: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8
  },
  logPhase: {
    fontSize: 13,
    color: '#00D9FF',
    fontWeight: '600',
    fontFamily: 'monospace'
  },
  logObject: {
    fontSize: 13,
    color: '#FFFFFF',
    fontFamily: 'monospace'
  },
  logComponent: {
    fontSize: 12,
    color: '#888',
    fontFamily: 'monospace'
  },
  logTime: {
    fontSize: 11,
    color: '#666',
    fontFamily: 'monospace'
  },
  codeBox: {
    backgroundColor: '#1E1E1E',
    borderRadius: 8,
    padding: 16,
    marginBottom: 12
  },
  code: {
    fontSize: 13,
    color: '#00D9FF',
    fontFamily: 'monospace',
    lineHeight: 20
  }
});
