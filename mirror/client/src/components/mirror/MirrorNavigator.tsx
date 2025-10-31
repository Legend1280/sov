/**
 * MirrorNavigator - Schema-driven navigator sidebar component
 * 
 * Displays a collapsible sidebar with sections and navigation items.
 * Supports themes, navigation groups, badges, and custom content.
 * 
 * Author: Brady Simmons
 * Copyright: © 2025 Sovereignty Foundation. All rights reserved.
 */

import { useState } from 'react';
import { useMirror } from '@/core/MirrorContext';

export interface NavigatorSection {
  id: string;
  title: string;
  items?: NavigatorItem[];
  component?: React.ReactNode;
}

export interface NavigatorItem {
  id: string;
  label: string;
  icon?: string;
  badge?: string | number;
  onClick?: () => void;
}

export interface MirrorNavigatorProps {
  sections?: NavigatorSection[];
  width?: number;
  collapsible?: boolean;
  defaultCollapsed?: boolean;
  children?: React.ReactNode;
}

export function MirrorNavigator({
  sections = [],
  width = 280,
  collapsible = true,
  defaultCollapsed = false,
  children,
}: MirrorNavigatorProps) {
  const [collapsed, setCollapsed] = useState(defaultCollapsed);
  const { eventBus } = useMirror();

  const handleToggle = () => {
    setCollapsed(!collapsed);
    eventBus.emit('navigator:toggle', { collapsed: !collapsed });
  };

  const handleItemClick = (item: NavigatorItem) => {
    if (item.onClick) {
      item.onClick();
    } else {
      eventBus.emit('navigator:itemClick', { itemId: item.id });
    }
  };

  if (collapsed) {
    return (
      <button
        onClick={handleToggle}
        className="w-10 bg-card border-r border-border flex items-center justify-center hover:bg-secondary transition-all duration-200 shadow-refined"
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
        </svg>
      </button>
    );
  }

  return (
    <aside
      className="bg-card border-r border-border flex flex-col transition-all duration-300 shadow-refined"
      style={{ width: `${width}px` }}
    >
      {/* Header */}
      <div className="px-6 py-4 border-b border-border flex items-center justify-between">
        <h2 className="text-xs font-semibold text-muted-foreground tracking-wider">NAVIGATOR</h2>
        {collapsible && (
          <button
            onClick={handleToggle}
            className="h-6 w-6 p-0 hover:bg-secondary rounded transition-colors flex items-center justify-center"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
        )}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6">
        {sections.map((section) => (
          <div key={section.id} className="space-y-3 mb-8">
            <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-3">
              {section.title}
            </h3>
            
            {/* Custom component */}
            {section.component && section.component}
            
            {/* Navigation items */}
            {section.items?.map((item) => (
              <button
                key={item.id}
                onClick={() => handleItemClick(item)}
                className="w-full text-left px-4 py-2.5 rounded-lg text-sm text-foreground hover:bg-secondary transition-all duration-200 flex items-center justify-between"
              >
                <span className="flex items-center gap-2">
                  {item.icon && <span>{item.icon}</span>}
                  <span>{item.label}</span>
                </span>
                {item.badge && (
                  <span className="text-xs bg-destructive text-destructive-foreground px-2 py-0.5 rounded-full font-medium">
                    {item.badge}
                  </span>
                )}
              </button>
            ))}
          </div>
        ))}
        
        {/* Custom children */}
        {children}
      </div>
    </aside>
  );
}

export default MirrorNavigator;
