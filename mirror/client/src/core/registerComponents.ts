/**
 * registerComponents - Register all Mirror components
 * 
 * This file registers all components with the ComponentRegistry.
 * It should be imported and called during application initialization.
 * 
 * Author: Brady Simmons
 * Copyright: © 2025 Sovereignty Foundation. All rights reserved.
 */

import { componentRegistry } from './ComponentRegistry';

// Core components
import AppContainer from '@/components/core/AppContainer';
import Text from '@/components/core/Text';
import NavigatorSection from '@/components/core/NavigatorSection';
import NavigatorItem from '@/components/core/NavigatorItem';
import ButtonWrapper from '@/components/core/ButtonWrapper';
import BadgeWrapper from '@/components/core/BadgeWrapper';

// Layout containers
import Grid from '@/components/layout/Grid';
import Stack from '@/components/layout/Stack';
import Tabs, { TabPanel } from '@/components/layout/Tabs';
import Split from '@/components/layout/Split';

/**
 * Register all core and layout components
 */
export function registerComponents(): void {
  console.log('[Mirror] Registering components...');

  // Core components
  componentRegistry.register('AppContainer', AppContainer);
  componentRegistry.register('Text', Text);
  componentRegistry.register('NavigatorSection', NavigatorSection);
  componentRegistry.register('NavigatorItem', NavigatorItem);
  componentRegistry.register('Button', ButtonWrapper);
  componentRegistry.register('Badge', BadgeWrapper);

  // Layout containers
  componentRegistry.register('Grid', Grid);
  componentRegistry.register('Stack', Stack);
  componentRegistry.register('Tabs', Tabs);
  componentRegistry.register('TabPanel', TabPanel);
  componentRegistry.register('Split', Split);

  console.log(`[Mirror] Registered ${componentRegistry.getTypes().length} components`);
}

export default registerComponents;
