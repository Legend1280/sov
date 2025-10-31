/**
 * Split - Split pane layout
 * 
 * Divides the space into two resizable panes.
 * 
 * Props:
 * - direction: "horizontal" or "vertical" (default: "horizontal")
 * - initialSize: Initial size of the first pane as percentage (default: 50)
 * - minSize: Minimum size of each pane as percentage (default: 20)
 */

import { ReactNode, useState, useRef, Children } from 'react';
import { cn } from '@/lib/utils';

interface SplitProps {
  direction?: 'horizontal' | 'vertical';
  initialSize?: number;
  minSize?: number;
  className?: string;
  children?: ReactNode;
  dataContext?: any;
  eventBus?: any;
}

export function Split({
  direction = 'horizontal',
  initialSize = 50,
  minSize = 20,
  className,
  children,
}: SplitProps) {
  const [size, setSize] = useState(initialSize);
  const [isDragging, setIsDragging] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  const childArray = Children.toArray(children);
  const firstChild = childArray[0];
  const secondChild = childArray[1];

  const handleMouseDown = () => {
    setIsDragging(true);
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDragging || !containerRef.current) return;

    const container = containerRef.current;
    const rect = container.getBoundingClientRect();

    let newSize: number;
    if (direction === 'horizontal') {
      newSize = ((e.clientX - rect.left) / rect.width) * 100;
    } else {
      newSize = ((e.clientY - rect.top) / rect.height) * 100;
    }

    // Clamp size to min/max
    newSize = Math.max(minSize, Math.min(100 - minSize, newSize));
    setSize(newSize);
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  return (
    <div
      ref={containerRef}
      className={cn(
        'split-container flex',
        direction === 'horizontal' ? 'flex-row' : 'flex-col',
        className
      )}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp}
    >
      {/* First Pane */}
      <div
        className="split-pane overflow-auto"
        style={{
          [direction === 'horizontal' ? 'width' : 'height']: `${size}%`,
        }}
      >
        {firstChild}
      </div>

      {/* Resize Handle */}
      <div
        className={cn(
          'split-handle bg-border hover:bg-primary/50 transition-colors cursor-col-resize',
          direction === 'horizontal' ? 'w-1 cursor-col-resize' : 'h-1 cursor-row-resize',
          isDragging && 'bg-primary'
        )}
        onMouseDown={handleMouseDown}
      />

      {/* Second Pane */}
      <div
        className="split-pane overflow-auto flex-1"
      >
        {secondChild}
      </div>
    </div>
  );
}

export default Split;
