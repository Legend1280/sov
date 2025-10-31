/**
 * MirrorHeader - Schema-driven header component for Mirror
 * 
 * Displays the main header with logo, view mode controls, temporal controls, and actions.
 * All elements are configurable via props for schema-driven composition.
 * 
 * Author: Brady Simmons
 * Copyright: © 2025 Sovereignty Foundation. All rights reserved.
 */

import { useMirror } from '@/core/MirrorContext';

export interface MirrorHeaderProps {
  logo?: string;
  title?: string;
  showViewModes?: boolean;
  showTemporalControls?: boolean;
  showUpload?: boolean;
  children?: React.ReactNode;
}

export function MirrorHeader({
  logo,
  title = 'Mirror',
  showViewModes = true,
  showTemporalControls = true,
  showUpload = true,
  children,
}: MirrorHeaderProps) {
  const { eventBus } = useMirror();

  const handleViewModeChange = (mode: string) => {
    eventBus.emit('viewMode:change', { mode });
  };

  const handleTemporalChange = (mode: string) => {
    eventBus.emit('temporal:change', { mode });
  };

  return (
    <header className="bg-card border-b border-border px-6 py-4 flex items-center justify-between shadow-refined relative">
      {/* Left Section - View Mode Controls */}
      <div className="flex-1">
        {showViewModes && (
          <div className="flex gap-2">
            <button
              onClick={() => handleViewModeChange('full')}
              className="p-2 hover:bg-secondary rounded-md transition-colors"
              title="Full View"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <rect x="3" y="3" width="18" height="18" rx="2" />
              </svg>
            </button>
            <button
              onClick={() => handleViewModeChange('split')}
              className="p-2 hover:bg-secondary rounded-md transition-colors"
              title="Split View"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <rect x="3" y="3" width="18" height="8" rx="2" />
                <rect x="3" y="13" width="18" height="8" rx="2" />
              </svg>
            </button>
            <button
              onClick={() => handleViewModeChange('left-only')}
              className="p-2 hover:bg-secondary rounded-md transition-colors"
              title="Left Only"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <rect x="3" y="3" width="8" height="18" rx="2" />
              </svg>
            </button>
          </div>
        )}
      </div>

      {/* Center Section - Logo/Title */}
      <div className="flex items-center gap-2">
        {logo && <img src={logo} alt={title} className="h-6" />}
        <span className="text-xl font-semibold tracking-tight">{title}</span>
      </div>

      {/* Right Section - Temporal Controls + Actions */}
      <div className="flex-1 flex justify-end gap-2">
        {showTemporalControls && (
          <>
            <button
              onClick={() => handleTemporalChange('past')}
              className="px-3 py-1.5 text-sm hover:bg-secondary rounded-md transition-colors"
            >
              Past
            </button>
            <button
              onClick={() => handleTemporalChange('present')}
              className="px-3 py-1.5 text-sm hover:bg-secondary rounded-md transition-colors"
            >
              Present
            </button>
            <button
              onClick={() => handleTemporalChange('future')}
              className="px-3 py-1.5 text-sm hover:bg-secondary rounded-md transition-colors"
            >
              Future
            </button>
          </>
        )}
        {showUpload && (
          <button
            onClick={() => eventBus.emit('upload:trigger')}
            className="px-4 py-1.5 text-sm bg-primary text-primary-foreground hover:bg-primary/90 rounded-md transition-colors font-medium"
          >
            Upload
          </button>
        )}
        {children}
      </div>
    </header>
  );
}

export default MirrorHeader;
