/**
 * Theme Type Definitions
 * 
 * Defines the structure for Mirror themes
 */

export interface Theme {
  id: string;
  name: string;
  description: string;
  
  // Core Colors
  colors: {
    // Primary brand color
    primary: string;
    primaryForeground: string;
    
    // Background colors
    background: string;
    foreground: string;
    
    // Card/Panel colors
    card: string;
    cardForeground: string;
    
    // UI Element colors
    muted: string;
    mutedForeground: string;
    accent: string;
    accentForeground: string;
    border: string;
    
    // Chart colors (for visualizations)
    chart: string[];
    
    // Visualization specific
    line: string; // Line chart color
    positive: string; // Positive values (green)
    negative: string; // Negative values (red)
  };
  
  // Effects
  effects: {
    shimmer: boolean; // Enable shimmer animation
    glass: boolean; // Enable glass effect
    shadows: 'none' | 'subtle' | 'medium' | 'strong';
  };
}

export type ThemeId = 'mirror' | 'light' | 'dark' | 'custom';
