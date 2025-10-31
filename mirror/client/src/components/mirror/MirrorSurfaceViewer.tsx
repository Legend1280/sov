/**
 * MirrorSurfaceViewer - Schema-driven surface viewer sidebar
 * 
 * Displays a collapsible right sidebar with tabbed interface for viewing object details,
 * documents, and provenance information.
 * 
 * Author: Brady Simmons
 * Copyright: © 2025 Sovereignty Foundation. All rights reserved.
 */

import { useState } from 'react';
import { useMirror } from '@/core/MirrorContext';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

export interface SurfaceTab {
  id: string;
  label: string;
  content?: React.ReactNode;
}

export interface MirrorSurfaceViewerProps {
  tabs?: SurfaceTab[];
  selectedObject?: any;
  width?: number;
  collapsible?: boolean;
  defaultCollapsed?: boolean;
  children?: React.ReactNode;
}

export function MirrorSurfaceViewer({
  tabs = [
    { id: 'details', label: 'Details' },
    { id: 'document', label: 'Document' },
    { id: 'provenance', label: 'Provenance' },
  ],
  selectedObject,
  width = 400,
  collapsible = true,
  defaultCollapsed = false,
  children,
}: MirrorSurfaceViewerProps) {
  const [collapsed, setCollapsed] = useState(defaultCollapsed);
  const [activeTab, setActiveTab] = useState(tabs[0]?.id || 'details');
  const { eventBus } = useMirror();

  const handleToggle = () => {
    setCollapsed(!collapsed);
    eventBus.emit('surfaceViewer:toggle', { collapsed: !collapsed });
  };

  if (collapsed) {
    return (
      <button
        onClick={handleToggle}
        className="w-10 bg-card border-l border-border flex items-center justify-center hover:bg-secondary transition-all duration-200 shadow-refined"
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
        </svg>
      </button>
    );
  }

  return (
    <aside
      className="bg-card border-l border-border flex flex-col transition-all duration-300 shadow-refined-md"
      style={{ width: `${width}px` }}
    >
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-border">
        <h2 className="text-xs font-semibold text-muted-foreground tracking-wider">SURFACE VIEWER</h2>
        {collapsible && (
          <button
            onClick={handleToggle}
            className="h-8 px-2 hover:bg-secondary rounded transition-colors flex items-center gap-2"
          >
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 4L4 12M4 4l8 8"/>
            </svg>
            <span className="text-sm">Hide Details</span>
          </button>
        )}
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col">
        <TabsList className="grid w-full rounded-none border-b bg-transparent" style={{ gridTemplateColumns: `repeat(${tabs.length}, 1fr)` }}>
          {tabs.map((tab) => (
            <TabsTrigger
              key={tab.id}
              value={tab.id}
              className="data-[state=active]:border-b-2 data-[state=active]:border-primary data-[state=active]:text-primary"
            >
              {tab.label}
            </TabsTrigger>
          ))}
        </TabsList>

        {tabs.map((tab) => (
          <TabsContent key={tab.id} value={tab.id} className="flex-1 p-6">
            {tab.content || (
              <div className="h-full flex items-center justify-center text-muted-foreground">
                {selectedObject ? (
                  <div className="text-sm">
                    <p>Object details will appear here</p>
                    {selectedObject.id && <p className="mt-2 text-xs">ID: {selectedObject.id}</p>}
                  </div>
                ) : (
                  <p>Select an object to view {tab.label.toLowerCase()}</p>
                )}
              </div>
            )}
          </TabsContent>
        ))}
      </Tabs>

      {/* Custom children */}
      {children}
    </aside>
  );
}

export default MirrorSurfaceViewer;
