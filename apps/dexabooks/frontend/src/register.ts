/**
 * DexaBooks Component Registration
 * 
 * Registers all DexaBooks-specific components with the ComponentRegistry
 * so they can be dynamically loaded by ViewportManager.
 */

import { componentRegistry } from '../../core/ComponentRegistry';
import CashFlowTimeline from './components/CashFlowTimeline';
import ExpenseBreakdown from './components/ExpenseBreakdown';

export function registerDexaBooksComponents() {
  // Register timeline component
  componentRegistry.register('timeline', CashFlowTimeline);
  
  // Register bar chart component
  componentRegistry.register('bar', ExpenseBreakdown);
  
  console.log('[DexaBooks] Components registered');
}

// Auto-register on import
registerDexaBooksComponents();
