/**
 * DataContext - Unified API access and application state provider
 * 
 * Provides all components with access to:
 * - Core API client
 * - Current user information
 * - Selected object state
 * - Module/App state
 * - Global application state
 */

import { createContext, useContext, useState, ReactNode } from 'react';
import { APIService } from './APIService';

export interface DataContextValue {
  api: APIService;
  selectedObject: any | null;
  setSelectedObject: (obj: any | null) => void;
  currentUser: any | null;
  setCurrentUser: (user: any | null) => void;
  activeApp: string | null;
  setActiveApp: (appId: string | null) => void;
  activeModule: string | null;
  setActiveModule: (moduleId: string | null) => void;
  globalState: Record<string, any>;
  setGlobalState: (key: string, value: any) => void;
}

const DataContext = createContext<DataContextValue | null>(null);

interface DataContextProviderProps {
  children: ReactNode;
  apiBaseUrl?: string;
}

export function DataContextProvider({ 
  children, 
  apiBaseUrl = 'http://localhost:8001' 
}: DataContextProviderProps) {
  const [api] = useState(() => new APIService(apiBaseUrl));
  const [selectedObject, setSelectedObject] = useState<any | null>(null);
  const [currentUser, setCurrentUser] = useState<any | null>(null);
  const [activeApp, setActiveApp] = useState<string | null>(null);
  const [activeModule, setActiveModule] = useState<string | null>(null);
  const [globalState, setGlobalStateInternal] = useState<Record<string, any>>({});

  const setGlobalState = (key: string, value: any) => {
    setGlobalStateInternal(prev => ({ ...prev, [key]: value }));
  };

  const value: DataContextValue = {
    api,
    selectedObject,
    setSelectedObject,
    currentUser,
    setCurrentUser,
    activeApp,
    setActiveApp,
    activeModule,
    setActiveModule,
    globalState,
    setGlobalState,
  };

  return (
    <DataContext.Provider value={value}>
      {children}
    </DataContext.Provider>
  );
}

export function useDataContext(): DataContextValue {
  const context = useContext(DataContext);
  if (!context) {
    throw new Error('useDataContext must be used within DataContextProvider');
  }
  return context;
}

export default DataContext;
