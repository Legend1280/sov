/**
 * Text - Simple text display component
 * 
 * A basic component for rendering text with optional styling.
 * 
 * Props:
 * - text: The text content to display
 * - className: Optional CSS classes for styling
 * - as: HTML element to render as (default: "span")
 */

import { createElement, ReactNode } from 'react';
import { cn } from '@/lib/utils';

interface TextProps {
  text?: string;
  className?: string;
  as?: 'span' | 'p' | 'div' | 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6';
  children?: ReactNode;
  dataContext?: any;
  eventBus?: any;
}

export function Text({
  text,
  className,
  as = 'span',
  children,
}: TextProps) {
  const content = children || text || '';
  
  return createElement(
    as,
    { className: cn(className) },
    content
  );
}

export default Text;
