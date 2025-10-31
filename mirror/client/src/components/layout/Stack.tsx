/**
 * Stack - Vertical or horizontal stack layout
 * 
 * Arranges child components in a vertical or horizontal stack.
 * 
 * Props:
 * - direction: "vertical" or "horizontal" (default: "vertical")
 * - gap: Gap between items in Tailwind units (default: 4)
 * - align: Alignment of items (default: "stretch")
 * - justify: Justification of items (default: "start")
 */

import { ReactNode } from 'react';
import { cn } from '@/lib/utils';

interface StackProps {
  direction?: 'vertical' | 'horizontal';
  gap?: number;
  align?: 'start' | 'center' | 'end' | 'stretch';
  justify?: 'start' | 'center' | 'end' | 'between' | 'around';
  className?: string;
  children?: ReactNode;
  dataContext?: any;
  eventBus?: any;
}

export function Stack({
  direction = 'vertical',
  gap = 4,
  align = 'stretch',
  justify = 'start',
  className,
  children,
}: StackProps) {
  const stackClasses = cn(
    'flex',
    direction === 'vertical' ? 'flex-col' : 'flex-row',
    `gap-${gap}`,
    // Alignment
    align === 'start' && 'items-start',
    align === 'center' && 'items-center',
    align === 'end' && 'items-end',
    align === 'stretch' && 'items-stretch',
    // Justification
    justify === 'start' && 'justify-start',
    justify === 'center' && 'justify-center',
    justify === 'end' && 'justify-end',
    justify === 'between' && 'justify-between',
    justify === 'around' && 'justify-around',
    className
  );

  return (
    <div className={stackClasses}>
      {children}
    </div>
  );
}

export default Stack;
