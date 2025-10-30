import { Theme } from './types';

/**
 * White Canvas Theme
 * 
 * Clean minimal white with subtle accents
 * Perfect for content-focused interfaces
 */

export const whiteCanvasTheme: Theme = {
  id: 'light',
  name: 'Light',
  description: 'Clean minimal white theme',
  
  colors: {
    primary: 'hsl(202 100% 64%)',
    primaryForeground: 'hsl(0 0% 100%)',
    
    background: 'hsl(0 0% 100%)',
    foreground: 'hsl(0 0% 10%)',
    
    card: 'hsl(0 0% 100%)',
    cardForeground: 'hsl(0 0% 10%)',
    
    muted: 'hsl(0 0% 96%)',
    mutedForeground: 'hsl(0 0% 45%)',
    accent: 'hsl(202 100% 64%)',
    accentForeground: 'hsl(0 0% 100%)',
    border: 'hsl(0 0% 90%)',
    
    chart: [
      'hsl(202 100% 75%)',
      'hsl(202 100% 64%)',
      'hsl(202 100% 54%)',
      'hsl(202 80% 44%)',
      'hsl(202 60% 34%)',
      'hsl(202 40% 24%)',
    ],
    
    line: 'hsl(202 100% 64%)',
    positive: 'hsl(142 76% 36%)',
    negative: 'hsl(0 84% 60%)',
  },
  
  effects: {
    shimmer: false,
    glass: false,
    shadows: 'subtle',
  },
};
