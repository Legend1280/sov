import React, { useState, useEffect } from 'react';
import { emitPulse } from '../lib/PulseClient';
import { usePulse } from '../hooks/usePulse';

interface SurfaceViewerProps {
  width: number;
  active_tab?: 'ontology' | 'document' | 'provenance';
  content?: any;
  theme: 'mirror' | 'light' | 'dark';
}

interface Tab {
  id: string;
  label: string;
  icon: string;
  description: string;
}

/**
 * SurfaceViewer - Multi-tab detail panel
 * 
 * Displays detailed information about selected objects:
 * - Ontology: Object properties, relationships, metadata
 * - Document: Rich text content with formatting
 * - Provenance: Event timeline and governance log
 */
export const SurfaceViewer: React.FC<SurfaceViewerProps> = ({
  width,
  active_tab: initialActiveTab = 'ontology',
  content,
  theme
}) => {
  const [activeTab, setActiveTab] = useState(initialActiveTab);
  const [loading, setLoading] = useState(false);

  const tabs: Tab[] = [
    {
      id: 'ontology',
      label: 'Ontology',
      icon: '◇',
      description: 'View object details and relationships'
    },
    {
      id: 'document',
      label: 'Document',
      icon: '📄',
      description: 'View document content'
    },
    {
      id: 'provenance',
      label: 'Provenance',
      icon: '🔗',
      description: 'View provenance chain'
    }
  ];

  // Listen for object selection from viewport
  usePulse('viewport.interaction', (payload) => {
    if (payload.interaction_type === 'object_selected') {
      loadObjectDetails(payload.interaction_data.object_id);
    }
  });

  // Initialization
  useEffect(() => {
    emitPulse('surface.initialized', {
      tabs: tabs.map(t => t.id),
      timestamp: new Date().toISOString()
    }, ['mirror', 'core', 'kronos']);
  }, []);

  // Handle tab change
  const handleTabChange = async (tabId: string) => {
    const previousTab = activeTab;
    setActiveTab(tabId);

    await emitPulse('surface.tab.changed', {
      previous_tab: previousTab,
      new_tab: tabId,
      timestamp: new Date().toISOString()
    }, ['mirror', 'core', 'kronos']);

    // Load tab content
    if (content) {
      loadTabContent(tabId);
    }
  };

  // Load object details
  const loadObjectDetails = async (objectId: string) => {
    setLoading(true);

    await emitPulse('surface.object.selected', {
      object_id: objectId,
      object_type: 'unknown',
      source_component: 'viewport',
      timestamp: new Date().toISOString()
    }, ['mirror', 'core', 'sage', 'kronos']);

    // Simulate loading (in real implementation, would fetch from Core)
    await new Promise(resolve => setTimeout(resolve, 300));

    setLoading(false);
  };

  // Load tab-specific content
  const loadTabContent = async (tabId: string) => {
    setLoading(true);

    await emitPulse('surface.content.loading', {
      tab_id: tabId,
      content_type: tabId,
      content_source: content?.object_id || 'none',
      timestamp: new Date().toISOString()
    }, ['mirror', 'core']);

    // Simulate loading
    await new Promise(resolve => setTimeout(resolve, 200));

    await emitPulse('surface.content.loaded', {
      tab_id: tabId,
      content_type: tabId,
      load_time_ms: 200,
      timestamp: new Date().toISOString()
    }, ['mirror', 'core', 'kronos', 'shadow']);

    setLoading(false);
  };

  const getThemeStyles = () => {
    switch (theme) {
      case 'mirror':
        return {
          background: 'rgba(255,255,255,0.5)',
          color: '#2C2C2C',
          borderColor: 'rgba(0,0,0,0.1)',
          tabActiveBg: 'rgba(255,255,255,0.8)'
        };
      case 'light':
        return {
          background: '#F9FAFB',
          color: '#111827',
          borderColor: '#E5E7EB',
          tabActiveBg: '#FFFFFF'
        };
      case 'dark':
        return {
          background: '#1F2937',
          color: '#F9FAFB',
          borderColor: '#374151',
          tabActiveBg: '#111827'
        };
    }
  };

  const themeStyles = getThemeStyles();

  const renderTabContent = () => {
    if (loading) {
      return (
        <div style={styles.centerContent}>
          <div style={{ ...styles.loadingText, color: themeStyles.color, opacity: 0.5 }}>
            Loading...
          </div>
        </div>
      );
    }

    if (!content) {
      return (
        <div style={styles.centerContent}>
          <div style={{ ...styles.emptyState, color: themeStyles.color, opacity: 0.3 }}>
            <div style={styles.emptyIcon}>□</div>
            <div style={styles.emptyText}>No Content</div>
            <div style={styles.emptySubtext}>Select an object to view details</div>
          </div>
        </div>
      );
    }

    switch (activeTab) {
      case 'ontology':
        return (
          <div style={styles.tabContent}>
            <div style={{ ...styles.sectionTitle, color: themeStyles.color }}>
              Object Properties
            </div>
            <div style={{ ...styles.propertyList, color: themeStyles.color }}>
              <div style={styles.property}>
                <div style={styles.propertyKey}>Type:</div>
                <div style={styles.propertyValue}>{content.type || 'object_details'}</div>
              </div>
              <div style={styles.property}>
                <div style={styles.propertyKey}>ID:</div>
                <div style={styles.propertyValue}>{content.object_id || 'N/A'}</div>
              </div>
              <div style={styles.property}>
                <div style={styles.propertyKey}>Status:</div>
                <div style={styles.propertyValue}>Active</div>
              </div>
            </div>

            <div style={{ ...styles.sectionTitle, color: themeStyles.color, marginTop: 24 }}>
              Relationships
            </div>
            <div style={{ ...styles.relationshipList, color: themeStyles.color, opacity: 0.6 }}>
              No relationships defined
            </div>
          </div>
        );

      case 'document':
        return (
          <div style={styles.tabContent}>
            <div style={{ ...styles.sectionTitle, color: themeStyles.color }}>
              Document Content
            </div>
            <div style={{ ...styles.documentContent, color: themeStyles.color }}>
              {content.document || 'No document content available'}
            </div>
          </div>
        );

      case 'provenance':
        return (
          <div style={styles.tabContent}>
            <div style={{ ...styles.sectionTitle, color: themeStyles.color }}>
              Provenance Chain
            </div>
            <div style={{ ...styles.provenanceTimeline, color: themeStyles.color }}>
              <div style={styles.provenanceEvent}>
                <div style={styles.provenanceTime}>2025-10-31 22:00:00</div>
                <div style={styles.provenanceAction}>Object created</div>
                <div style={styles.provenanceActor}>Core</div>
              </div>
              <div style={styles.provenanceEvent}>
                <div style={styles.provenanceTime}>2025-10-31 22:00:05</div>
                <div style={styles.provenanceAction}>Validated by SAGE</div>
                <div style={styles.provenanceActor}>SAGE</div>
              </div>
              <div style={styles.provenanceEvent}>
                <div style={styles.provenanceTime}>2025-10-31 22:00:10</div>
                <div style={styles.provenanceAction}>Indexed by Kronos</div>
                <div style={styles.provenanceActor}>Kronos</div>
              </div>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div style={{ ...styles.surface, width, ...themeStyles }}>
      {/* Tabs */}
      <div style={{ ...styles.tabs, borderBottom: `1px solid ${themeStyles.borderColor}` }}>
        {tabs.map(tab => (
          <div
            key={tab.id}
            style={{
              ...styles.tab,
              ...(activeTab === tab.id ? {
                ...styles.tabActive,
                background: themeStyles.tabActiveBg,
                color: themeStyles.color
              } : {
                color: themeStyles.color,
                opacity: 0.6
              })
            }}
            onClick={() => handleTabChange(tab.id)}
            title={tab.description}
          >
            <span style={styles.tabIcon}>{tab.icon}</span>
            <span style={styles.tabLabel}>{tab.label}</span>
          </div>
        ))}
      </div>

      {/* Content */}
      <div style={styles.content}>
        {renderTabContent()}
      </div>
    </div>
  );
};

const styles: Record<string, React.CSSProperties> = {
  surface: {
    display: 'flex',
    flexDirection: 'column',
    height: '100%',
    overflowY: 'auto'
  },
  tabs: {
    display: 'flex',
    height: 48,
    flexShrink: 0
  },
  tab: {
    flex: 1,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    cursor: 'pointer',
    transition: 'all 0.15s ease',
    userSelect: 'none',
    fontSize: 14
  },
  tabActive: {
    fontWeight: 500
  },
  tabIcon: {
    fontSize: 16
  },
  tabLabel: {},
  content: {
    flex: 1,
    overflowY: 'auto'
  },
  centerContent: {
    height: '100%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center'
  },
  loadingText: {
    fontSize: 14
  },
  emptyState: {
    textAlign: 'center',
    userSelect: 'none'
  },
  emptyIcon: {
    fontSize: 48,
    marginBottom: 16,
    opacity: 0.3
  },
  emptyText: {
    fontSize: 16,
    fontWeight: 500,
    marginBottom: 8
  },
  emptySubtext: {
    fontSize: 14,
    opacity: 0.6
  },
  tabContent: {
    padding: 24
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: 600,
    marginBottom: 16
  },
  propertyList: {
    display: 'flex',
    flexDirection: 'column',
    gap: 12
  },
  property: {
    display: 'flex',
    gap: 12,
    fontSize: 14
  },
  propertyKey: {
    fontWeight: 500,
    minWidth: 80
  },
  propertyValue: {
    opacity: 0.8
  },
  relationshipList: {
    fontSize: 14
  },
  documentContent: {
    fontSize: 14,
    lineHeight: 1.6,
    whiteSpace: 'pre-wrap'
  },
  provenanceTimeline: {
    display: 'flex',
    flexDirection: 'column',
    gap: 16
  },
  provenanceEvent: {
    fontSize: 14,
    paddingLeft: 16,
    borderLeft: '2px solid rgba(0,0,0,0.1)'
  },
  provenanceTime: {
    fontSize: 12,
    opacity: 0.5,
    marginBottom: 4
  },
  provenanceAction: {
    fontWeight: 500,
    marginBottom: 2
  },
  provenanceActor: {
    fontSize: 12,
    opacity: 0.6
  }
};

export default SurfaceViewer;
