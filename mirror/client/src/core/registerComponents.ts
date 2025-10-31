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

// Mirror components
import MirrorContainer from '@/components/mirror/MirrorContainer';
import MirrorHeader from '@/components/mirror/MirrorHeader';
import MirrorNavigator from '@/components/mirror/MirrorNavigator';
import MirrorViewport from '@/components/mirror/MirrorViewport';
import MirrorSurfaceViewer from '@/components/mirror/MirrorSurfaceViewer';
import ResizablePanel from '@/components/mirror/ResizablePanel';
import ThemeSwitcher from '@/components/mirror/ThemeSwitcher';
import UploadButton from '@/components/mirror/UploadButton';

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

  // Mirror components
  componentRegistry.register('MirrorContainer', MirrorContainer);
  componentRegistry.register('MirrorHeader', MirrorHeader);
  componentRegistry.register('MirrorNavigator', MirrorNavigator);
  componentRegistry.register('MirrorViewport', MirrorViewport);
  componentRegistry.register('MirrorSurfaceViewer', MirrorSurfaceViewer);
  componentRegistry.register('ResizablePanel', ResizablePanel);
  componentRegistry.register('ThemeSwitcher', ThemeSwitcher);
  componentRegistry.register('UploadButton', UploadButton);

  console.log(`[Mirror] Registered ${componentRegistry.getTypes().length} components`);
}

export default registerComponents;
