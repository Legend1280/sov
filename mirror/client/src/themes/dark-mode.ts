import { Theme } from './types';

/**
 * Dark Mode Theme
 * 
 * Professional dark theme with blue accents
 * Easy on the eyes for extended use
 */

export const darkModeTheme: Theme = {
  id: 'dark',
  name: 'Dark',
  description: 'Professional dark theme',
  
  colors: {
    primary: 'hsl(202 100% 64%)',
    primaryForeground: 'hsl(0 0% 100%)',
    
    background: 'hsl(0 0% 10%)',
    foreground: 'hsl(0 0% 95%)',
    
    card: 'hsl(0 0% 15%)',
    cardForeground: 'hsl(0 0% 95%)',
    
    muted: 'hsl(0 0% 20%)',
    mutedForeground: 'hsl(0 0% 60%)',
    accent: 'hsl(202 100% 64%)',
    accentForeground: 'hsl(0 0% 100%)',
    border: 'hsl(0 0% 25%)',
    
    chart: [
      'hsl(202 100% 75%)',
      'hsl(202 100% 64%)',
      'hsl(202 100% 54%)',
      'hsl(202 80% 44%)',
      'hsl(202 60% 34%)',
      'hsl(202 40% 24%)',
    ],
    
    line: 'hsl(202 100% 64%)',
    positive: 'hsl(142 76% 46%)',
    negative: 'hsl(0 84% 70%)',
  },
  
  effects: {
    shimmer: false,
    glass: false,
    shadows: 'medium',
  },
};
