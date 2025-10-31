/**
 * NavigatorItem - Navigator item button component
 * 
 * Displays a clickable item in the navigator sidebar.
 * Can show an icon, label, and optional badge.
 * 
 * Props:
 * - id: Unique identifier for the item
 * - label: Display label
 * - icon: Icon name (lucide-react)
 * - badge: Optional badge text
 * - active: Whether the item is currently active
 * - onClick: Click handler
 */

import { useState } from 'react';
import { cn } from '@/lib/utils';
import * as Icons from 'lucide-react';

interface NavigatorItemProps {
  id: string;
  label: string;
  icon?: string;
  badge?: string;
  active?: boolean;
  onClick?: () => void;
  className?: string;
  dataContext?: any;
  eventBus?: any;
}

export function NavigatorItem({
  id,
  label,
  icon,
  badge,
  active: initialActive = false,
  onClick,
  className,
  eventBus,
}: NavigatorItemProps) {
  const [active, setActive] = useState(initialActive);

  const handleClick = () => {
    setActive(true);
    if (eventBus) {
      eventBus.emit('navigatorItemClicked', { id, label });
    }
    if (onClick) {
      onClick();
    }
  };

  // Get the icon component from lucide-react
  const IconComponent = icon ? (Icons as any)[icon] : null;

  return (
    <button
      onClick={handleClick}
      className={cn(
        'w-full flex items-center gap-3 px-3 py-2 text-sm rounded-md transition-colors',
        active
          ? 'bg-primary/10 text-primary font-medium'
          : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground',
        className
      )}
    >
      {IconComponent && <IconComponent className="h-4 w-4 flex-shrink-0" />}
      <span className="flex-1 text-left">{label}</span>
      {badge && (
        <span className="px-2 py-0.5 text-xs rounded-full bg-primary/20 text-primary">
          {badge}
        </span>
      )}
    </button>
  );
}

export default NavigatorItem;
