/**
 * MirrorContext - Top-level provider that bundles all Mirror contexts
 * 
 * Provides a unified context for the entire Mirror application:
 * - EventBus for inter-component communication
 * - DataContext for API access and application state
 * - AppRegistry for application management
 * 
 * This ensures all components in the tree inherit the same global state references.
 * 
 * Author: Brady Simmons
 * Copyright: © 2025 Sovereignty Foundation. All rights reserved.
 */

import { ReactNode, createContext, useContext } from 'react';
import { DataContextProvider, DataContextValue, useDataContext } from './DataContext';
import { eventBus, EventBus } from './EventBus';
import { appRegistry, AppManifest } from './AppRegistry';
import { componentRegistry } from './ComponentRegistry';

export interface MirrorContextValue extends DataContextValue {
  eventBus: EventBus;
  appRegistry: typeof appRegistry;
  componentRegistry: typeof componentRegistry;
}

const MirrorContext = createContext<MirrorContextValue | null>(null);

interface MirrorProviderProps {
  children: ReactNode;
  apiBaseUrl?: string;
}

/**
 * MirrorProvider - Root provider for the Mirror application
 * 
 * Wraps the application with all necessary contexts and registries.
 */
export function MirrorProvider({ children, apiBaseUrl }: MirrorProviderProps) {
  return (
    <DataContextProvider apiBaseUrl={apiBaseUrl}>
      <MirrorContextInternal>
        {children}
      </MirrorContextInternal>
    </DataContextProvider>
  );
}

/**
 * Internal component that provides the combined context
 */
function MirrorContextInternal({ children }: { children: ReactNode }) {
  const dataContext = useDataContext();

  const value: MirrorContextValue = {
    ...dataContext,
    eventBus,
    appRegistry,
    componentRegistry,
  };

  return (
    <MirrorContext.Provider value={value}>
      {children}
    </MirrorContext.Provider>
  );
}

/**
 * useMirror - Hook to access the Mirror context
 * 
 * Provides access to all Mirror systems:
 * - api: APIService instance
 * - eventBus: EventBus instance
 * - appRegistry: AppRegistry instance
 * - componentRegistry: ComponentRegistry instance
 * - selectedObject: Currently selected object
 * - currentUser: Current user information
 * - activeApp: Active app ID
 * - activeModule: Active module ID
 * - globalState: Global application state
 */
export function useMirror(): MirrorContextValue {
  const context = useContext(MirrorContext);
  if (!context) {
    throw new Error('useMirror must be used within MirrorProvider');
  }
  return context;
}

export default MirrorContext;
