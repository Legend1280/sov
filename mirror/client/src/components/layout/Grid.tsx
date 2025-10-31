/**
 * Grid - Grid layout container
 * 
 * Arranges child components in a responsive grid.
 * 
 * Props:
 * - columns: Number of columns (default: 2)
 * - gap: Gap between items in Tailwind units (default: 4)
 * - responsive: Enable responsive breakpoints (default: true)
 */

import { ReactNode } from 'react';
import { cn } from '@/lib/utils';

interface GridProps {
  columns?: number;
  gap?: number;
  responsive?: boolean;
  className?: string;
  children?: ReactNode;
  dataContext?: any;
  eventBus?: any;
}

export function Grid({
  columns = 2,
  gap = 4,
  responsive = true,
  className,
  children,
}: GridProps) {
  const gridClasses = cn(
    'grid',
    responsive && columns === 2 && 'grid-cols-1 md:grid-cols-2',
    responsive && columns === 3 && 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3',
    responsive && columns === 4 && 'grid-cols-1 md:grid-cols-2 lg:grid-cols-4',
    !responsive && `grid-cols-${columns}`,
    `gap-${gap}`,
    className
  );

  return (
    <div className={gridClasses}>
      {children}
    </div>
  );
}

export default Grid;
