/**
 * SAGE Middleware - Governance validation for Pulse events
 * 
 * Enforces ethical and logical coherence before Pulse transmission.
 * All Pulse creations and terminations are validated against SAGE rules.
 * 
 * In production, this would connect to the full SAGE governance engine.
 * 
 * Author: Brady Simmons
 * Copyright: © 2025 Sovereignty Foundation. All rights reserved.
 */

import { PulseObject, PulseIntent } from '../pulse/PulseBridge';

export interface SageRule {
  rule_id: string;
  name: string;
  condition: string;
  action: 'allow' | 'deny' | 'warn';
  constraints: string[];
  description: string;
}

export interface SageValidationResult {
  approved: boolean;
  rule_id: string;
  message: string;
  warnings?: string[];
}

/**
 * Default SAGE ruleset for Pulse validation
 */
const DEFAULT_RULES: SageRule[] = [
  {
    rule_id: 'sage:rule_001',
    name: 'Authenticated User Access',
    condition: "origin.role == 'authenticated_user'",
    action: 'allow',
    constraints: [
      'payload.length < 4096',
      "intent in ['query','update','create']"
    ],
    description: 'Allow authenticated users to query, update, and create'
  },
  {
    rule_id: 'sage:rule_002',
    name: 'System Governance',
    condition: "origin == 'system' || origin == 'sage'",
    action: 'allow',
    constraints: [
      "intent in ['govern','reflect']"
    ],
    description: 'Allow system and SAGE to govern and reflect'
  },
  {
    rule_id: 'sage:rule_003',
    name: 'Mirror to Core Communication',
    condition: "origin == 'mirror' && target == 'core'",
    action: 'allow',
    constraints: [
      'payload != null',
      "intent in ['update','query','create','govern','reflect']"
    ],
    description: 'Allow Mirror to communicate with Core'
  },
  {
    rule_id: 'sage:rule_004',
    name: 'Core to Mirror Response',
    condition: "origin == 'core' && target == 'mirror'",
    action: 'allow',
    constraints: [
      'coherence >= 0.0',
      'coherence <= 1.0'
    ],
    description: 'Allow Core to respond to Mirror with valid coherence'
  },
  {
    rule_id: 'sage:rule_default',
    name: 'Default Allow',
    condition: 'true',
    action: 'allow',
    constraints: [],
    description: 'Default rule - allow all'
  }
];

class SageMiddlewareCore {
  private rules: Map<string, SageRule> = new Map();
  private validationLog: Array<{
    timestamp: string;
    pulse_id: string;
    result: SageValidationResult;
  }> = [];

  constructor() {
    // Load default rules
    DEFAULT_RULES.forEach(rule => {
      this.rules.set(rule.rule_id, rule);
    });
  }

  /**
   * Validate a Pulse object against SAGE rules
   */
  validate(pulse: Partial<PulseObject>): SageValidationResult {
    const warnings: string[] = [];

    // Check if origin and target are provided
    if (!pulse.origin) {
      return {
        approved: false,
        rule_id: 'sage:validation_error',
        message: 'Pulse origin is required'
      };
    }

    if (!pulse.target) {
      return {
        approved: false,
        rule_id: 'sage:validation_error',
        message: 'Pulse target is required'
      };
    }

    // Check if intent is provided
    if (!pulse.intent) {
      return {
        approved: false,
        rule_id: 'sage:validation_error',
        message: 'Pulse intent is required'
      };
    }

    // Validate intent type
    const validIntents: PulseIntent[] = ['update', 'query', 'create', 'govern', 'reflect'];
    if (!validIntents.includes(pulse.intent)) {
      return {
        approved: false,
        rule_id: 'sage:validation_error',
        message: `Invalid intent: ${pulse.intent}`
      };
    }

    // Check payload constraints
    if (pulse.payload) {
      const payloadStr = JSON.stringify(pulse.payload);
      if (payloadStr.length > 4096) {
        warnings.push('Payload exceeds recommended size (4096 bytes)');
      }
    }

    // Check coherence bounds
    if (pulse.coherence !== undefined) {
      if (pulse.coherence < 0 || pulse.coherence > 1) {
        return {
          approved: false,
          rule_id: 'sage:validation_error',
          message: 'Coherence must be between 0 and 1'
        };
      }
    }

    // Find matching rule
    const matchingRule = this.findMatchingRule(pulse);

    // Log validation
    const result: SageValidationResult = {
      approved: matchingRule.action === 'allow',
      rule_id: matchingRule.rule_id,
      message: matchingRule.action === 'allow' 
        ? `Approved by ${matchingRule.name}`
        : `Denied by ${matchingRule.name}`,
      warnings: warnings.length > 0 ? warnings : undefined
    };

    this.logValidation(pulse.id || 'unknown', result);

    return result;
  }

  /**
   * Find the first matching rule for a Pulse
   */
  private findMatchingRule(pulse: Partial<PulseObject>): SageRule {
    // Check rule_003: Mirror to Core
    if (pulse.origin === 'mirror' && pulse.target === 'core') {
      return this.rules.get('sage:rule_003')!;
    }

    // Check rule_004: Core to Mirror
    if (pulse.origin === 'core' && pulse.target === 'mirror') {
      return this.rules.get('sage:rule_004')!;
    }

    // Check rule_002: System governance
    if (pulse.origin === 'system' || pulse.origin === 'sage') {
      if (pulse.intent === 'govern' || pulse.intent === 'reflect') {
        return this.rules.get('sage:rule_002')!;
      }
    }

    // Default rule
    return this.rules.get('sage:rule_default')!;
  }

  /**
   * Get a specific rule by ID
   */
  getRule(ruleId: string): SageRule | undefined {
    return this.rules.get(ruleId);
  }

  /**
   * Get all rules
   */
  getAllRules(): SageRule[] {
    return Array.from(this.rules.values());
  }

  /**
   * Add or update a rule
   */
  setRule(rule: SageRule): void {
    this.rules.set(rule.rule_id, rule);
  }

  /**
   * Get validation log
   */
  getValidationLog(): Array<{
    timestamp: string;
    pulse_id: string;
    result: SageValidationResult;
  }> {
    return [...this.validationLog];
  }

  /**
   * Log a validation result
   */
  private logValidation(pulseId: string, result: SageValidationResult): void {
    this.validationLog.push({
      timestamp: new Date().toISOString(),
      pulse_id: pulseId,
      result
    });

    // Keep log size manageable (last 1000 entries)
    if (this.validationLog.length > 1000) {
      this.validationLog.shift();
    }
  }

  /**
   * Clear validation log
   */
  clearLog(): void {
    this.validationLog = [];
  }
}

// Singleton instance
export const SageMiddleware = new SageMiddlewareCore();
