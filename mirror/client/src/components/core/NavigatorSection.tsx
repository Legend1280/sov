/**
 * NavigatorSection - Navigator section header component
 * 
 * Displays a section header in the navigator sidebar.
 * Used to group related navigation items.
 * 
 * Props:
 * - title: Section title text
 * - className: Optional CSS classes
 * - children: NavigatorItem components
 */

import { ReactNode } from 'react';
import { cn } from '@/lib/utils';

interface NavigatorSectionProps {
  title: string;
  className?: string;
  children?: ReactNode;
  dataContext?: any;
  eventBus?: any;
}

export function NavigatorSection({
  title,
  className,
  children,
}: NavigatorSectionProps) {
  return (
    <div className={cn('navigator-section', className)}>
      <div className="px-3 py-2">
        <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
          {title}
        </h3>
      </div>
      <div className="space-y-1">
        {children}
      </div>
    </div>
  );
}

export default NavigatorSection;
