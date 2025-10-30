/**
 * ViewportPlaceholder - Animated placeholder for empty viewports
 * 
 * Shows a cool shimmer animation while viewport is empty
 */

export default function ViewportPlaceholder({ label }: { label?: string }) {
  return (
    <div className="w-full h-full bg-card flex items-center justify-center viewport-shimmer viewport-glass">
      <div className="text-center space-y-4 z-10">
        {/* Animated Icon */}
        <div className="mx-auto w-16 h-16 rounded-full bg-muted flex items-center justify-center animate-pulse">
          <svg 
            className="w-8 h-8 text-muted-foreground" 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              strokeWidth={2} 
              d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" 
            />
          </svg>
        </div>
        
        {/* Label */}
        {label && (
          <div className="text-sm font-medium text-foreground">
            {label}
          </div>
        )}
        
        {/* Message */}
        <div className="text-xs text-muted-foreground max-w-xs">
          Viewport ready for content
        </div>
        
        {/* Supported Types */}
        <div className="flex gap-2 justify-center text-xs text-muted-foreground">
          <span className="px-2 py-1 bg-muted rounded">Charts</span>
          <span className="px-2 py-1 bg-muted rounded">3D</span>
          <span className="px-2 py-1 bg-muted rounded">iFrame</span>
          <span className="px-2 py-1 bg-muted rounded">API</span>
        </div>
      </div>
    </div>
  );
}
