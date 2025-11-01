/**
 * LogosLoginButton — Identity Anchor Component
 * 
 * The visual manifestation of Logos, the identity and authentication layer.
 * This is not just a button — it's a governed ontological object that
 * authenticates narrative coherence between user and system.
 * 
 * This component is bound to the Logos ontology object and communicates
 * entirely through Pulse events. It has no direct API calls.
 * 
 * Author: Brady Simmons
 * Copyright: © 2025 Sovereignty Foundation. All rights reserved.
 */

import React, { useState, useEffect } from 'react';
import { 
  TouchableOpacity, 
  Text, 
  View, 
  ActivityIndicator, 
  StyleSheet,
  Animated
} from 'react-native';
import { PulseBridge } from '@/lib/PulseBridge';

interface LogosLoginButtonProps {
  mode?: 'login' | 'logout';
  ontology?: any;  // Ontology object passed by ObjectRenderer
  pulseBridge?: typeof PulseBridge;  // PulseBridge instance
  onAuthenticated?: (session: any) => void;
  onError?: (error: string) => void;
}

type AuthState = 'idle' | 'authenticating' | 'authenticated' | 'error';

export default function LogosLoginButton({
  mode = 'login',
  ontology,
  pulseBridge = PulseBridge,
  onAuthenticated,
  onError
}: LogosLoginButtonProps) {
  const [authState, setAuthState] = useState<AuthState>('idle');
  const [errorMessage, setErrorMessage] = useState<string>('');
  const [fadeAnim] = useState(new Animated.Value(1));

  // Listen for authentication responses
  useEffect(() => {
    // Listen for successful authentication
    const unsubscribeAuth = pulseBridge.on('logos.authenticated', (pulse: any) => {
      setAuthState('authenticated');
      
      if (onAuthenticated) {
        onAuthenticated(pulse.payload);
      }

      // Fade out after success
      Animated.timing(fadeAnim, {
        toValue: 0,
        duration: 1000,
        delay: 1500,
        useNativeDriver: true
      }).start();
    });

    // Listen for authentication failures
    const unsubscribeFail = pulseBridge.on('logos.authentication.failed', (pulse: any) => {
      setAuthState('error');
      setErrorMessage(pulse.payload.reason || 'Authentication failed');
      
      if (onError) {
        onError(pulse.payload.reason);
      }

      // Reset to idle after showing error
      setTimeout(() => {
        setAuthState('idle');
        setErrorMessage('');
      }, 3000);
    });

    return () => {
      unsubscribeAuth();
      unsubscribeFail();
    };
  }, [pulseBridge, onAuthenticated, onError]);

  // Handle authentication
  const handleAuthenticate = () => {
    setAuthState('authenticating');

    // Emit authentication Pulse
    pulseBridge.emit('logos.authenticate', {
      source: 'mirror',
      target: 'core',
      intent: 'authenticate',
      payload: {
        method: 'narrative',
        timestamp: new Date().toISOString()
      }
    });
  };

  // Handle logout
  const handleLogout = () => {
    // Emit logout Pulse
    pulseBridge.emit('logos.logout', {
      source: 'mirror',
      target: 'core',
      intent: 'logout',
      payload: {
        timestamp: new Date().toISOString()
      }
    });

    setAuthState('idle');
  };

  // Get visual properties from ontology or use defaults
  const visual = ontology?.schema?.visual || {
    label: 'Log In with Logos',
    color: '#00A3FF'
  };

  // Get state-specific styling
  const getStateStyle = () => {
    switch (authState) {
      case 'idle':
        return {
          backgroundColor: visual.color || '#00A3FF',
          textColor: '#FFFFFF'
        };
      case 'authenticating':
        return {
          backgroundColor: '#0088CC',
          textColor: '#FFFFFF'
        };
      case 'authenticated':
        return {
          backgroundColor: '#00CC66',
          textColor: '#FFFFFF'
        };
      case 'error':
        return {
          backgroundColor: '#CC0000',
          textColor: '#FFFFFF'
        };
    }
  };

  const stateStyle = getStateStyle();

  // Get label based on state
  const getLabel = () => {
    switch (authState) {
      case 'idle':
        return mode === 'login' ? visual.label : 'Log Out';
      case 'authenticating':
        return 'Authenticating...';
      case 'authenticated':
        return '✓ Authenticated';
      case 'error':
        return errorMessage || 'Authentication Failed';
    }
  };

  return (
    <Animated.View style={{ opacity: fadeAnim }}>
      <TouchableOpacity
        style={[
          styles.button,
          { backgroundColor: stateStyle.backgroundColor }
        ]}
        onPress={mode === 'login' ? handleAuthenticate : handleLogout}
        disabled={authState === 'authenticating' || authState === 'authenticated'}
        activeOpacity={0.8}
      >
        <View style={styles.content}>
          {authState === 'authenticating' && (
            <ActivityIndicator 
              size="small" 
              color={stateStyle.textColor} 
              style={styles.spinner}
            />
          )}
          
          <Text style={[styles.label, { color: stateStyle.textColor }]}>
            {getLabel()}
          </Text>
        </View>
      </TouchableOpacity>

      {/* Ontology metadata (debug info) */}
      {ontology && __DEV__ && (
        <View style={styles.debug}>
          <Text style={styles.debugText}>
            Ontology: {ontology.id} | Layer: {ontology.layer}
          </Text>
          <Text style={styles.debugText}>
            Channel: {ontology.pulse_channel}
          </Text>
        </View>
      )}
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  button: {
    borderRadius: 12,
    paddingVertical: 14,
    paddingHorizontal: 24,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 52,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.15,
    shadowRadius: 4,
    elevation: 3
  },
  content: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center'
  },
  spinner: {
    marginRight: 10
  },
  label: {
    fontSize: 18,
    fontWeight: '600',
    letterSpacing: 0.3
  },
  debug: {
    marginTop: 8,
    padding: 8,
    backgroundColor: '#F0F0F0',
    borderRadius: 6
  },
  debugText: {
    fontSize: 11,
    color: '#666',
    fontFamily: 'monospace'
  }
});
