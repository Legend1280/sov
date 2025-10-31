/**
 * ButtonWrapper - Wrapper for the UI Button component
 * 
 * Adapts the shadcn/ui Button component to work with the schema system.
 * 
 * Props:
 * - label: Button text
 * - variant: Button variant (default, destructive, outline, secondary, ghost, link)
 * - size: Button size (default, sm, lg, icon)
 * - onClick: Click handler
 */

import { Button } from '@/components/ui/button';

interface ButtonWrapperProps {
  label: string;
  variant?: 'default' | 'destructive' | 'outline' | 'secondary' | 'ghost' | 'link';
  size?: 'default' | 'sm' | 'lg' | 'icon';
  onClick?: () => void;
  className?: string;
  dataContext?: any;
  eventBus?: any;
}

export function ButtonWrapper({
  label,
  variant = 'default',
  size = 'default',
  onClick,
  className,
  eventBus,
}: ButtonWrapperProps) {
  const handleClick = () => {
    if (eventBus) {
      eventBus.emit('buttonClicked', { label });
    }
    if (onClick) {
      onClick();
    }
  };

  return (
    <Button
      variant={variant}
      size={size}
      onClick={handleClick}
      className={className}
    >
      {label}
    </Button>
  );
}

export default ButtonWrapper;
