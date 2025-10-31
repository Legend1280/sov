/**
 * LayoutStore - Zustand store for Mirror layout state
 * 
 * Manages navigator visibility/width, surface viewer visibility/width,
 * viewport heights, view modes, and focus modes.
 * 
 * Author: Brady Simmons
 * Copyright: © 2025 Sovereignty Foundation. All rights reserved.
 */

import { create } from 'zustand';

export type ViewMode = 'full' | 'split' | 'left-only';
export type TemporalMode = 'past' | 'present' | 'future';
export type FocusMode = 'viewport1' | 'viewport2' | null;

interface LayoutState {
  // Navigator
  navigatorVisible: boolean;
  navigatorWidth: number;
  
  // Surface Viewer
  surfaceViewerVisible: boolean;
  surfaceViewerWidth: number;
  
  // Viewports
  viewport1Height: number; // percentage
  viewMode: ViewMode;
  focusMode: FocusMode;
  
  // Temporal
  temporalMode: TemporalMode;
  
  // Actions
  toggleNavigator: () => void;
  toggleSurfaceViewer: () => void;
  toggleFocus: (viewport: FocusMode) => void;
  resizeNavigator: (delta: number) => void;
  resizeSurfaceViewer: (delta: number) => void;
  resizeViewport: (delta: number, containerHeight: number) => void;
  setViewMode: (mode: ViewMode) => void;
  setTemporalMode: (mode: TemporalMode) => void;
}

export const useLayoutStore = create<LayoutState>((set) => ({
  // Initial state
  navigatorVisible: true,
  navigatorWidth: 280,
  surfaceViewerVisible: true,
  surfaceViewerWidth: 400,
  viewport1Height: 50,
  viewMode: 'split',
  focusMode: null,
  temporalMode: 'present',
  
  // Actions
  toggleNavigator: () => set((state) => ({ navigatorVisible: !state.navigatorVisible })),
  
  toggleSurfaceViewer: () => set((state) => ({ surfaceViewerVisible: !state.surfaceViewerVisible })),
  
  toggleFocus: (viewport) => set((state) => ({
    focusMode: state.focusMode === viewport ? null : viewport
  })),
  
  resizeNavigator: (delta) => set((state) => ({
    navigatorWidth: Math.max(200, Math.min(600, state.navigatorWidth + delta))
  })),
  
  resizeSurfaceViewer: (delta) => set((state) => ({
    surfaceViewerWidth: Math.max(300, Math.min(800, state.surfaceViewerWidth - delta))
  })),
  
  resizeViewport: (delta, containerHeight) => set((state) => {
    const deltaPercent = (delta / containerHeight) * 100;
    return {
      viewport1Height: Math.max(20, Math.min(80, state.viewport1Height + deltaPercent))
    };
  }),
  
  setViewMode: (mode) => set({ viewMode: mode }),
  
  setTemporalMode: (mode) => set({ temporalMode: mode }),
}));
