/**
 * BadgeWrapper - Wrapper for the UI Badge component
 * 
 * Adapts the shadcn/ui Badge component to work with the schema system.
 * 
 * Props:
 * - text: Badge text content
 * - variant: Badge variant (default, secondary, destructive, outline)
 */

import { Badge } from '@/components/ui/badge';

interface BadgeWrapperProps {
  text: string;
  variant?: 'default' | 'secondary' | 'destructive' | 'outline';
  className?: string;
  dataContext?: any;
  eventBus?: any;
}

export function BadgeWrapper({
  text,
  variant = 'default',
  className,
}: BadgeWrapperProps) {
  return (
    <Badge variant={variant} className={className}>
      {text}
    </Badge>
  );
}

export default BadgeWrapper;
