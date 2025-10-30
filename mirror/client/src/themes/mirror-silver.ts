import { Theme } from './types';

/**
 * Mirror Silver Theme
 * 
 * Monochromatic grey/silver palette with shimmer effects
 * Inspired by reflective surfaces and metallic finishes
 */

export const mirrorSilverTheme: Theme = {
  id: 'mirror',
  name: 'Mirror',
  description: 'Reflective grey tones with shimmer',
  
  colors: {
    primary: 'hsl(0 0% 60%)',
    primaryForeground: 'hsl(0 0% 100%)',
    
    background: 'hsl(0 0% 98%)',
    foreground: 'hsl(0 0% 20%)',
    
    card: 'hsl(0 0% 100%)',
    cardForeground: 'hsl(0 0% 20%)',
    
    muted: 'hsl(0 0% 94%)',
    mutedForeground: 'hsl(0 0% 50%)',
    accent: 'hsl(0 0% 60%)',
    accentForeground: 'hsl(0 0% 100%)',
    border: 'hsl(0 0% 92%)',
    
    chart: [
      'hsl(0 0% 70%)',
      'hsl(0 0% 60%)',
      'hsl(0 0% 50%)',
      'hsl(0 0% 40%)',
      'hsl(0 0% 35%)',
      'hsl(0 0% 30%)',
    ],
    
    line: 'hsl(0 0% 50%)',
    positive: 'hsl(0 0% 40%)',
    negative: 'hsl(0 0% 60%)',
  },
  
  effects: {
    shimmer: true,
    glass: true,
    shadows: 'subtle',
  },
};
