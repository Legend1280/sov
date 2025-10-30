import { create } from 'zustand';

/**
 * LayoutManager - Centralized state management for Mirror's layout system
 * 
 * Manages:
 * - Panel visibility (Navigator, Surface Viewer)
 * - Panel dimensions (widths, heights)
 * - View modes (split, full, left-only)
 * - Focus mode (viewport expansion)
 * - Temporal mode (past, present, future)
 */

export type ViewMode = 'full' | 'split' | 'left-only';
export type FocusMode = 'viewport1' | 'viewport2' | null;
export type TemporalMode = 'past' | 'present' | 'future';

interface LayoutState {
  // Panel Visibility
  navigatorVisible: boolean;
  surfaceViewerVisible: boolean;
  
  // Panel Dimensions
  navigatorWidth: number;
  surfaceViewerWidth: number;
  viewport1Height: number; // percentage (0-100)
  
  // View Modes
  viewMode: ViewMode;
  focusMode: FocusMode;
  temporalMode: TemporalMode;
  
  // Actions
  setNavigatorVisible: (visible: boolean) => void;
  setSurfaceViewerVisible: (visible: boolean) => void;
  setNavigatorWidth: (width: number) => void;
  setSurfaceViewerWidth: (width: number) => void;
  setViewport1Height: (height: number) => void;
  setViewMode: (mode: ViewMode) => void;
  setFocusMode: (mode: FocusMode) => void;
  setTemporalMode: (mode: TemporalMode) => void;
  
  // Resize Handlers
  resizeNavigator: (delta: number) => void;
  resizeSurfaceViewer: (delta: number) => void;
  resizeViewport: (delta: number, containerHeight: number) => void;
  
  // Toggle Actions
  toggleNavigator: () => void;
  toggleSurfaceViewer: () => void;
  toggleFocus: (viewport: 'viewport1' | 'viewport2') => void;
}

export const useLayoutStore = create<LayoutState>((set, get) => ({
  // Initial State
  navigatorVisible: true,
  surfaceViewerVisible: true,
  navigatorWidth: 192, // 12rem
  surfaceViewerWidth: 320, // 20rem
  viewport1Height: 50, // 50% of container
  viewMode: 'split',
  focusMode: null,
  temporalMode: 'present',
  
  // Setters
  setNavigatorVisible: (visible: boolean) => set({ navigatorVisible: visible }),
  setSurfaceViewerVisible: (visible: boolean) => set({ surfaceViewerVisible: visible }),
  setNavigatorWidth: (width: number) => set({ navigatorWidth: width }),
  setSurfaceViewerWidth: (width: number) => set({ surfaceViewerWidth: width }),
  setViewport1Height: (height: number) => set({ viewport1Height: height }),
  setViewMode: (mode: ViewMode) => set({ viewMode: mode }),
  setFocusMode: (mode: FocusMode) => set({ focusMode: mode }),
  setTemporalMode: (mode: TemporalMode) => set({ temporalMode: mode }),
  
  // Resize Handlers
  resizeNavigator: (delta: number) => {
    const current = get().navigatorWidth;
    const newWidth = Math.max(200, Math.min(400, current + delta));
    set({ navigatorWidth: newWidth });
  },
  
  resizeSurfaceViewer: (delta: number) => {
    const current = get().surfaceViewerWidth;
    const newWidth = Math.max(300, Math.min(800, current - delta));
    set({ surfaceViewerWidth: newWidth });
  },
  
  resizeViewport: (delta: number, containerHeight: number) => {
    const current = get().viewport1Height;
    const deltaPercent = (delta / containerHeight) * 100;
    const newHeight = Math.max(20, Math.min(80, current + deltaPercent));
    set({ viewport1Height: newHeight });
  },
  
  // Toggle Actions
  toggleNavigator: () => set((state: LayoutState) => ({ navigatorVisible: !state.navigatorVisible })),
  toggleSurfaceViewer: () => set((state: LayoutState) => ({ surfaceViewerVisible: !state.surfaceViewerVisible })),
  toggleFocus: (viewport: 'viewport1' | 'viewport2') => {
    const current = get().focusMode;
    set({ focusMode: current === viewport ? null : viewport });
  },
}));
