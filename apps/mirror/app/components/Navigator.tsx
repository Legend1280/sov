import React, { useState, useEffect } from 'react';
import { emitPulse } from '../lib/PulseClient';
import { usePulse } from '../hooks/usePulse';

interface NavigatorProps {
  width: number;
  collapsed: boolean;
  active_section?: string;
  active_item?: string;
  theme: 'mirror' | 'light' | 'dark';
}

interface NavigationItem {
  id: string;
  label: string;
  action: string;
  target?: string;
  icon?: string;
}

interface NavigationSection {
  id: string;
  label: string;
  type: string;
  items: NavigationItem[];
}

/**
 * Navigator - Semantic navigation sidebar
 * 
 * Provides structured navigation through ontological objects,
 * system features, and themes. All navigation actions emit Pulses
 * and are validated by SAGE.
 */
export const Navigator: React.FC<NavigatorProps> = ({
  width,
  collapsed,
  active_section: initialActiveSection,
  active_item: initialActiveItem,
  theme
}) => {
  const [activeSection, setActiveSection] = useState(initialActiveSection || 'themes');
  const [activeItem, setActiveItem] = useState(initialActiveItem);
  const [favorites, setFavorites] = useState<string[]>([]);

  // Navigation structure from ontology
  const sections: NavigationSection[] = [
    {
      id: 'themes',
      label: 'THEMES',
      type: 'theme_selector',
      items: [
        { id: 'mirror', label: 'Mirror', action: 'switch_theme', icon: '✨' },
        { id: 'light', label: 'Light', action: 'switch_theme', icon: '☀️' },
        { id: 'dark', label: 'Dark', action: 'switch_theme', icon: '🌙' }
      ]
    },
    {
      id: 'ontology',
      label: 'ONTOLOGY',
      type: 'object_browser',
      items: [
        { id: 'browse_all', label: 'Browse All Objects', action: 'navigate', target: 'ontology.browser' },
        { id: 'recent', label: 'Recently Viewed', action: 'navigate', target: 'ontology.recent' },
        { id: 'favorites', label: 'Favorites', action: 'navigate', target: 'ontology.favorites' }
      ]
    },
    {
      id: 'system',
      label: 'SYSTEM',
      type: 'system_navigation',
      items: [
        { id: 'dashboard', label: 'Dashboard', action: 'navigate', target: 'system.dashboard' },
        { id: 'provenance', label: 'Provenance', action: 'navigate', target: 'system.provenance' },
        { id: 'governance', label: 'Governance', action: 'navigate', target: 'system.governance' },
        { id: 'constitution', label: 'Constitution', action: 'navigate', target: 'system.constitution' }
      ]
    },
    {
      id: 'tools',
      label: 'TOOLS',
      type: 'tool_navigation',
      items: [
        { id: 'query_builder', label: 'Query Builder', action: 'navigate', target: 'tools.query' },
        { id: 'visualizer', label: 'Visualizer', action: 'navigate', target: 'tools.visualizer' },
        { id: 'inspector', label: 'Inspector', action: 'navigate', target: 'tools.inspector' }
      ]
    }
  ];

  // Listen for navigation sync from other components
  usePulse('mirror.navigation', (payload) => {
    if (payload.source !== 'navigator') {
      setActiveItem(payload.to_section);
    }
  });

  // Initialization
  useEffect(() => {
    emitPulse('navigator.initialized', {
      sections: sections.map(s => s.id),
      timestamp: new Date().toISOString()
    }, ['mirror', 'core', 'kronos']);
  }, []);

  // Handle section selection
  const handleSectionClick = (sectionId: string) => {
    const previousSection = activeSection;
    setActiveSection(sectionId);
    
    emitPulse('navigator.section.selected', {
      section_id: sectionId,
      previous_section: previousSection,
      timestamp: new Date().toISOString()
    }, ['mirror', 'core', 'kronos']);
  };

  // Handle item selection
  const handleItemClick = async (item: NavigationItem, sectionId: string) => {
    setActiveItem(item.id);

    // Emit selection event
    await emitPulse('navigator.item.selected', {
      item_id: item.id,
      section_id: sectionId,
      action: item.action,
      target: item.target || item.id,
      timestamp: new Date().toISOString()
    }, ['mirror', 'core', 'sage']);

    // Handle specific actions
    if (item.action === 'switch_theme') {
      const currentTheme = theme;
      const newTheme = item.id as 'mirror' | 'light' | 'dark';
      
      await emitPulse('navigator.theme.changed', {
        previous_theme: currentTheme,
        new_theme: newTheme,
        timestamp: new Date().toISOString()
      }, ['mirror', 'core', 'kronos']);
    }
  };

  const getThemeStyles = () => {
    switch (theme) {
      case 'mirror':
        return {
          background: 'rgba(255,255,255,0.5)',
          color: '#2C2C2C',
          borderColor: 'rgba(0,0,0,0.1)'
        };
      case 'light':
        return {
          background: '#F9FAFB',
          color: '#111827',
          borderColor: '#E5E7EB'
        };
      case 'dark':
        return {
          background: '#1F2937',
          color: '#F9FAFB',
          borderColor: '#374151'
        };
    }
  };

  const themeStyles = getThemeStyles();

  return (
    <div style={{ ...styles.navigator, width, ...themeStyles }}>
      {sections.map(section => (
        <div key={section.id} style={styles.section}>
          <div 
            style={{
              ...styles.sectionLabel,
              color: themeStyles.color,
              opacity: 0.5
            }}
            onClick={() => handleSectionClick(section.id)}
          >
            {section.label}
          </div>
          
          <div style={styles.items}>
            {section.items.map(item => (
              <div
                key={item.id}
                style={{
                  ...styles.item,
                  ...(activeItem === item.id ? {
                    ...styles.itemActive,
                    background: theme === 'dark' ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.05)'
                  } : {}),
                  color: themeStyles.color
                }}
                onClick={() => handleItemClick(item, section.id)}
              >
                {item.icon && <span style={styles.itemIcon}>{item.icon}</span>}
                <span style={styles.itemLabel}>{item.label}</span>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
};

const styles: Record<string, React.CSSProperties> = {
  navigator: {
    display: 'flex',
    flexDirection: 'column',
    padding: '24px 0',
    overflowY: 'auto'
  },
  section: {
    marginBottom: 24
  },
  sectionLabel: {
    fontSize: 11,
    fontWeight: 600,
    letterSpacing: '0.5px',
    padding: '0 16px',
    marginBottom: 8,
    cursor: 'pointer',
    userSelect: 'none'
  },
  items: {
    display: 'flex',
    flexDirection: 'column',
    gap: 2
  },
  item: {
    display: 'flex',
    alignItems: 'center',
    gap: 8,
    padding: '8px 16px',
    fontSize: 14,
    cursor: 'pointer',
    transition: 'all 0.15s ease',
    userSelect: 'none'
  },
  itemActive: {
    fontWeight: 500
  },
  itemIcon: {
    fontSize: 16,
    width: 16,
    textAlign: 'center'
  },
  itemLabel: {
    flex: 1
  }
};

export default Navigator;
