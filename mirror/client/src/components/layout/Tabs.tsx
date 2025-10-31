/**
 * Tabs - Tab container layout
 * 
 * Arranges child components in tabs.
 * Children should be TabPanel components.
 * 
 * Props:
 * - defaultTab: ID of the default active tab
 */

import { ReactNode, useState, Children, isValidElement } from 'react';
import { cn } from '@/lib/utils';

interface TabsProps {
  defaultTab?: string;
  className?: string;
  children?: ReactNode;
  dataContext?: any;
  eventBus?: any;
}

interface TabPanelProps {
  id: string;
  label: string;
  children?: ReactNode;
  dataContext?: any;
  eventBus?: any;
}

export function Tabs({
  defaultTab,
  className,
  children,
}: TabsProps) {
  // Extract tab panels from children
  const tabPanels = Children.toArray(children).filter(
    child => isValidElement(child) && child.type === TabPanel
  );

  const firstTabId = isValidElement(tabPanels[0]) ? (tabPanels[0].props as TabPanelProps).id : '';
  const [activeTab, setActiveTab] = useState(defaultTab || firstTabId);

  return (
    <div className={cn('tabs-container', className)}>
      {/* Tab Headers */}
      <div className="flex border-b border-border">
        {tabPanels.map((panel) => {
          if (!isValidElement(panel)) return null;
          const { id, label } = panel.props as TabPanelProps;
          return (
            <button
              key={id}
              onClick={() => setActiveTab(id)}
              className={cn(
                'px-4 py-2 text-sm font-medium transition-colors',
                'border-b-2 -mb-px',
                activeTab === id
                  ? 'border-primary text-primary'
                  : 'border-transparent text-muted-foreground hover:text-foreground'
              )}
            >
              {label}
            </button>
          );
        })}
      </div>

      {/* Tab Content */}
      <div className="tab-content p-4">
        {tabPanels.map((panel) => {
          if (!isValidElement(panel)) return null;
          const { id, children: panelChildren } = panel.props as TabPanelProps;
          return (
            <div
              key={id}
              className={cn(
                'tab-panel',
                activeTab === id ? 'block' : 'hidden'
              )}
            >
              {panelChildren}
            </div>
          );
        })}
      </div>
    </div>
  );
}

export function TabPanel({
  children,
}: TabPanelProps) {
  return <>{children}</>;
}

export default Tabs;
