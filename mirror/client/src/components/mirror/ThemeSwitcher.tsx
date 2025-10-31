/**
 * ThemeSwitcher - Schema-driven theme selection component
 * 
 * Displays a list of available themes and allows switching between them.
 * Integrates with the ThemeManager for theme state management.
 * 
 * Author: Brady Simmons
 * Copyright: © 2025 Sovereignty Foundation. All rights reserved.
 */

import { useThemeStore } from '@/themes/ThemeManager';
import { useMirror } from '@/core/MirrorContext';

export interface ThemeSwitcherProps {
  showDescription?: boolean;
}

export function ThemeSwitcher({ showDescription = true }: ThemeSwitcherProps) {
  const { activeThemeId, setTheme, getAllThemes } = useThemeStore();
  const { eventBus } = useMirror();

  const handleThemeChange = (themeId: string) => {
    setTheme(themeId as any);
    eventBus.emit('theme:change', { themeId });
  };

  const themes = getAllThemes();

  return (
    <div className="space-y-2">
      {themes.map((theme: any) => (
        <button
          key={theme.id}
          onClick={() => handleThemeChange(theme.id)}
          className={`w-full text-left px-4 py-2.5 rounded-lg text-sm transition-all duration-200 flex items-center justify-between ${
            activeThemeId === theme.id
              ? 'bg-primary text-primary-foreground'
              : 'text-foreground hover:bg-secondary'
          }`}
        >
          <div>
            <div className="font-medium">{theme.name}</div>
            {showDescription && (
              <div className="text-xs opacity-70 mt-0.5">{theme.description}</div>
            )}
          </div>
          {activeThemeId === theme.id && (
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
            </svg>
          )}
        </button>
      ))}
    </div>
  );
}

export default ThemeSwitcher;
