import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

interface SurfaceViewerProps {
  selectedObject?: any;
  onClose: () => void;
}

export default function SurfaceViewer({ selectedObject, onClose }: SurfaceViewerProps) {
  const [activeTab, setActiveTab] = useState('tab1');

  return (
    <div className="h-full flex flex-col bg-card">
      {/* Header with Hide Details button */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-border">
        <h2 className="text-xs font-semibold text-muted-foreground tracking-wider">SURFACE VIEWER</h2>
        <Button
          variant="ghost"
          size="sm"
          onClick={onClose}
          className="h-8 px-2"
        >
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M12 4L4 12M4 4l8 8"/>
          </svg>
          <span className="ml-2">Hide Details</span>
        </Button>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col">
        <TabsList className="grid w-full grid-cols-3 rounded-none border-b bg-transparent">
          <TabsTrigger 
            value="tab1"
            className="data-[state=active]:border-b-2 data-[state=active]:border-primary data-[state=active]:text-primary"
          >
            Tab 1
          </TabsTrigger>
          <TabsTrigger 
            value="tab2"
            className="data-[state=active]:border-b-2 data-[state=active]:border-primary data-[state=active]:text-primary"
          >
            Tab 2
          </TabsTrigger>
          <TabsTrigger 
            value="tab3"
            className="data-[state=active]:border-b-2 data-[state=active]:border-primary data-[state=active]:text-primary"
          >
            Tab 3
          </TabsTrigger>
        </TabsList>

        <TabsContent value="tab1" className="flex-1 p-6">
          {selectedObject ? (
            <div className="text-sm text-muted-foreground">
              <p>Object details will appear here</p>
            </div>
          ) : (
            <div className="h-full flex items-center justify-center text-muted-foreground">
              Select an object to view ontology
            </div>
          )}
        </TabsContent>

        <TabsContent value="tab2" className="flex-1 p-6">
          <div className="h-full flex items-center justify-center text-muted-foreground">
            Document view
          </div>
        </TabsContent>

        <TabsContent value="tab3" className="flex-1 p-6">
          <div className="h-full flex items-center justify-center text-muted-foreground">
            Provenance trail
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
