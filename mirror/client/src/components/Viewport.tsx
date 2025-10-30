import { ReactNode } from 'react';

interface ViewportProps {
  title: string;
  children: ReactNode;
  className?: string;
}

export default function Viewport({ title, children, className = '' }: ViewportProps) {
  return (
    <div className={`viewport flex flex-col h-full ${className}`}>
      <div className="viewport-header">
        {title}
      </div>
      <div className="flex-1 overflow-auto p-4">
        {children}
      </div>
    </div>
  );
}
