import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { Theme, ThemeId } from './types';
import { mirrorSilverTheme } from './mirror-silver';
import { whiteCanvasTheme } from './white-canvas';
import { darkModeTheme } from './dark-mode';

/**
 * ThemeManager - Centralized theme state management
 * 
 * Manages:
 * - Active theme selection
 * - Theme switching
 * - Custom theme creation
 * - Theme persistence (localStorage)
 */

interface ThemeState {
  // Available themes
  themes: Record<ThemeId, Theme>;
  
  // Active theme
  activeThemeId: ThemeId;
  activeTheme: Theme;
  
  // Actions
  setTheme: (themeId: ThemeId) => void;
  setCustomTheme: (theme: Theme) => void;
  
  // Helpers
  getTheme: (themeId: ThemeId) => Theme | undefined;
  getAllThemes: () => Theme[];
}

export const useThemeStore = create<ThemeState>()(
  persist(
    (set, get) => ({
      // Initial themes
      themes: {
        'mirror': mirrorSilverTheme,
        'light': whiteCanvasTheme,
        'dark': darkModeTheme,
        'custom': mirrorSilverTheme, // Default custom theme
      },
      
      // Default to Mirror
      activeThemeId: 'mirror',
      activeTheme: mirrorSilverTheme,
      
      // Set theme by ID
      setTheme: (themeId: ThemeId) => {
        const theme = get().themes[themeId];
        if (theme) {
          set({ activeThemeId: themeId, activeTheme: theme });
          applyThemeToDOM(theme);
        }
      },
      
      // Set custom theme
      setCustomTheme: (theme: Theme) => {
        set((state) => ({
          themes: { ...state.themes, custom: theme },
          activeThemeId: 'custom',
          activeTheme: theme,
        }));
        applyThemeToDOM(theme);
      },
      
      // Get theme by ID
      getTheme: (themeId: ThemeId) => get().themes[themeId],
      
      // Get all themes as array (unique only)
      getAllThemes: () => {
        const themes = get().themes;
        const uniqueThemes = new Map();
        Object.values(themes).forEach(theme => {
          if (theme.id !== 'custom' && !uniqueThemes.has(theme.id)) {
            uniqueThemes.set(theme.id, theme);
          }
        });
        return Array.from(uniqueThemes.values());
      },
    }),
    {
      name: 'mirror-theme-storage',
      partialize: (state) => ({ activeThemeId: state.activeThemeId }),
    }
  )
);

/**
 * Apply theme colors to DOM CSS variables
 */
function applyThemeToDOM(theme: Theme) {
  const root = document.documentElement;
  
  // Apply color variables
  root.style.setProperty('--primary', theme.colors.primary);
  root.style.setProperty('--primary-foreground', theme.colors.primaryForeground);
  root.style.setProperty('--background', theme.colors.background);
  root.style.setProperty('--foreground', theme.colors.foreground);
  root.style.setProperty('--card', theme.colors.card);
  root.style.setProperty('--card-foreground', theme.colors.cardForeground);
  root.style.setProperty('--muted', theme.colors.muted);
  root.style.setProperty('--muted-foreground', theme.colors.mutedForeground);
  root.style.setProperty('--accent', theme.colors.accent);
  root.style.setProperty('--accent-foreground', theme.colors.accentForeground);
  root.style.setProperty('--border', theme.colors.border);
  
  // Apply chart colors
  theme.colors.chart.forEach((color, i) => {
    root.style.setProperty(`--chart-${i + 1}`, color);
  });
  
  // Apply visualization colors
  root.style.setProperty('--color-line', theme.colors.line);
  root.style.setProperty('--color-positive', theme.colors.positive);
  root.style.setProperty('--color-negative', theme.colors.negative);
  
  // Apply effect classes
  root.classList.toggle('shimmer-enabled', theme.effects.shimmer);
  root.classList.toggle('glass-enabled', theme.effects.glass);
  root.setAttribute('data-shadows', theme.effects.shadows);
}

// Initialize theme on load
if (typeof window !== 'undefined') {
  const store = useThemeStore.getState();
  applyThemeToDOM(store.activeTheme);
}
