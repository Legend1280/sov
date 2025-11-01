# Scribe Presentation - Visual Language Design

## Color Palette

### Modality Colors
- **Narrative** (Blue): `#3b82f6` - Story, memory, self-concept
- **Modal** (Green): `#10b981` - Expression, style, behavior
- **Temporal** (Orange): `#f59e0b` - Time, experience, intention
- **Role** (Purple): `#8b5cf6` - Context, relationships, identity

### Semantic States
- **Coherent** (Success): `#22c55e` - High coherence, valid Wisp
- **Drifting** (Warning): `#eab308` - Medium coherence, needs attention
- **Incoherent** (Error): `#ef4444` - Low coherence, fusion failed

### Background & Structure
- **Primary BG**: `linear-gradient(135deg, #1e293b 0%, #0f172a 100%)` - Deep, professional
- **Card BG**: `rgba(255, 255, 255, 0.05)` - Subtle glass morphism
- **Border**: `rgba(255, 255, 255, 0.1)` - Soft separation
- **Text Primary**: `#f1f5f9` - High contrast
- **Text Secondary**: `rgba(241, 245, 249, 0.6)` - Subtle labels

---

## Typography

### Hierarchy
- **H1 (Project Title)**: 28px, 600 weight, -0.5px letter-spacing
- **H2 (Section Title)**: 20px, 600 weight
- **H3 (Subsection)**: 16px, 600 weight
- **Body**: 14px, 400 weight
- **Caption**: 12px, 400 weight, 0.6 opacity
- **Monospace (Data)**: 13px, `'Fira Code', monospace`

### Font Stack
```css
font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif;
```

---

## Animation Principles

### Timing Functions
- **Ease-out**: Default for most animations (feels responsive)
- **Ease-in-out**: For looping animations (smooth cycles)
- **Spring**: For attention-grabbing effects (bouncy, alive)

### Duration Guidelines
- **Micro-interactions**: 150ms (button hovers, highlights)
- **Transitions**: 300ms (panel changes, tab switches)
- **Animations**: 1000-2000ms (fusion process, data updates)
- **Ambient**: 3000-5000ms (pulsing, breathing effects)

### Key Animations
1. **Pulse** - Subtle scale + opacity for "alive" feeling
2. **Flow** - Animated gradient for data transfer
3. **Glow** - Radial gradient for emphasis
4. **Fade-slide** - Opacity + translate for content changes
5. **Morph** - Shape transformation for state changes

---

## Viewport 1: Fusion Visualization

### Layout
```
┌─────────────────────────────────────────┐
│  Fusion Process Visualization           │
├─────────────────────────────────────────┤
│                                         │
│     [Narrative]    [Modal]             │
│          ╲           ╱                  │
│           ╲         ╱                   │
│            ╲       ╱                    │
│             [WISP]                      │
│            ╱       ╲                    │
│           ╱         ╲                   │
│     [Temporal]    [Role]               │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │ Multi-Head Attention Display    │   │
│  │ [H1][H2][H3][H4][H5][H6][H7][H8]│   │
│  └─────────────────────────────────┘   │
│                                         │
│  Coherence: 0.9421  |  Latency: 23ms  │
└─────────────────────────────────────────┘
```

### Visual Elements

**1. Modality Orbs**
- **Shape**: Circle, 80px diameter
- **Fill**: Gradient (modality color → lighter shade)
- **Border**: 2px solid, modality color, 50% opacity
- **Glow**: Box-shadow with modality color, 20px blur
- **Animation**: Pulse (scale 1.0 → 1.05, 2s loop)
- **Content**: Modality name + embedding dimension count

**2. Attention Flow Lines**
- **Shape**: Curved bezier path between orbs
- **Stroke**: 2-4px (thickness = attention weight)
- **Color**: Gradient from source to target modality color
- **Animation**: Dashed line moving along path (flow direction)
- **Opacity**: 0.3-0.8 (based on attention strength)

**3. Central Wisp**
- **Shape**: Circle, 120px diameter
- **Fill**: Animated gradient blending all 4 modality colors
- **Border**: 3px solid white, 80% opacity
- **Glow**: Large radial gradient, 40px blur, pulsing
- **Animation**: 
  - Formation: Scale 0 → 1.0 over 1s
  - Idle: Rotate gradient 360deg over 5s
  - Coherence pulse: Glow intensity tied to coherence score

**4. Multi-Head Attention Display**
- **Layout**: 8 circles in horizontal row, 40px each
- **Fill**: Color shows dominant modality for each head
- **Size**: Proportional to head contribution (0.5-1.0 scale)
- **Label**: "H1" - "H8" in center
- **Tooltip**: Shows attention weights on hover

**5. Metrics Bar**
- **Position**: Bottom of viewport
- **Background**: `rgba(0,0,0,0.3)`
- **Content**: Coherence score, latency, iteration count
- **Animation**: Numbers count up smoothly

---

## Viewport 2: Statistical Analysis

### Layout
```
┌─────────────────────────────────────────┐
│  Statistical Power Analysis             │
├─────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐    │
│  │ Coherence    │  │ Semantic     │    │
│  │ Distribution │  │ Drift        │    │
│  │ (Violin)     │  │ (Line Chart) │    │
│  └──────────────┘  └──────────────┘    │
│  ┌──────────────┐  ┌──────────────┐    │
│  │ Attention    │  │ Category     │    │
│  │ Heatmap      │  │ Performance  │    │
│  │ (8x4 Grid)   │  │ (Radar)      │    │
│  └──────────────┘  └──────────────┘    │
└─────────────────────────────────────────┘
```

### Chart Specifications

**1. Coherence Distribution (Violin Plot)**
- **X-axis**: Scribe vs MiniLM
- **Y-axis**: Coherence score (0.0 - 1.0)
- **Colors**: Scribe (blue), MiniLM (gray)
- **Overlays**: Mean line, std deviation bands, confidence intervals
- **Annotation**: p-value, effect size (Cohen's d)

**2. Semantic Drift (Line Chart)**
- **X-axis**: Batch size (10, 50, 100, 200)
- **Y-axis**: Mean semantic drift (L2 distance)
- **Lines**: Scribe (blue, solid), MiniLM (gray, dashed)
- **Error bars**: 95% confidence intervals
- **Annotation**: Highlight where Scribe significantly outperforms

**3. Attention Heatmap (8x4 Grid)**
- **Rows**: 8 attention heads (H1-H8)
- **Columns**: 4 modalities (Narrative, Modal, Temporal, Role)
- **Color scale**: White (0.0) → Modality color (1.0)
- **Labels**: Row/column headers
- **Interaction**: Hover shows exact attention weight

**4. Category Performance (Radar Chart)**
- **Axes**: 4 categories (personal_memory, creative_fiction, conversational, technical)
- **Metrics**: Coherence (0-1 scale)
- **Lines**: Scribe (blue, filled), MiniLM (gray, outline)
- **Points**: Markers at each vertex
- **Legend**: Bottom-right corner

---

## Right Navigator: Research Report

### Tab Design
```
┌─────────────────────────────────────────┐
│ [Theory] [Architecture] [Validation]    │
│          [Results]                      │
├─────────────────────────────────────────┤
│                                         │
│  Tab Content Area                       │
│  (Scrollable)                           │
│                                         │
│  • Rich text                            │
│  • Equations                            │
│  • Tables                               │
│  • Inline visualizations                │
│                                         │
└─────────────────────────────────────────┘
```

### Tab Styling
- **Inactive**: `rgba(255,255,255,0.1)`, 0.6 opacity text
- **Active**: `rgba(255,255,255,0.2)`, 1.0 opacity text, bottom border (3px, accent color)
- **Hover**: `rgba(255,255,255,0.15)`
- **Transition**: 200ms ease-out

### Content Styling
- **Paragraphs**: 16px line-height, 1.6 ratio, justified
- **Headings**: Accent color, bold
- **Code blocks**: `rgba(0,0,0,0.3)` background, monospace font
- **Tables**: Alternating row colors, border-collapse
- **Equations**: LaTeX-style rendering (if possible), or monospace with proper spacing
- **Inline viz**: Small charts/diagrams embedded in text

---

## Interaction Patterns

### Batch Size Selection
- **Control**: Segmented button group (10 | 50 | 100 | 200)
- **State**: Active button has accent color background
- **Feedback**: Immediate update of all visualizations

### Category Filter
- **Control**: Checkbox group (All | Personal Memory | Creative Fiction | etc.)
- **State**: Checked boxes have accent color
- **Feedback**: Charts update with filtered data

### Sample Selection
- **Control**: Click on any data point in charts
- **State**: Selected point highlighted with ring
- **Feedback**: Detailed sample info appears in side panel

### Export Results
- **Control**: Button in top-right corner
- **Action**: Download JSON with all test results
- **Feedback**: Success toast notification

---

## Responsive Behavior

### Viewport Resizing
- **Fusion viz**: Scales proportionally, maintains aspect ratio
- **Charts**: Redraw to fit new dimensions
- **Text**: Reflow, no horizontal scroll

### Performance
- **Target**: 60fps for all animations
- **Strategy**: Use CSS transforms (GPU-accelerated), avoid layout thrashing
- **Fallback**: Reduce animation complexity on slower devices

---

## Accessibility

### Color Contrast
- **Text on dark BG**: >= 7:1 ratio (WCAG AAA)
- **Interactive elements**: >= 4.5:1 ratio (WCAG AA)

### Keyboard Navigation
- **Tab order**: Logical flow (controls → charts → report)
- **Focus indicators**: 2px outline, accent color
- **Shortcuts**: Space (run test), Arrow keys (navigate tabs)

### Screen Readers
- **ARIA labels**: All interactive elements
- **Alt text**: All visualizations describe data
- **Live regions**: Announce test completion

---

## Implementation Notes

### Canvas vs SVG
- **Fusion viz**: Canvas (better for animations, particles)
- **Charts**: SVG (scalable, interactive, accessible)

### Data Update Strategy
- **Real-time**: WebSocket from validation service
- **Batch**: Update all charts simultaneously (smooth transition)
- **Incremental**: Append new data points without redrawing entire chart

### State Management
- **Global state**: Current batch size, selected category, test results
- **Local state**: Chart zoom/pan, tooltip position, tab selection
- **Persistence**: Save state to localStorage for refresh

---

This visual language provides a **complete design system** for building the Scribe Presentation that is:
- **Beautiful**: Professional, modern, aesthetically pleasing
- **Meaningful**: Every visual element represents semantic concepts
- **Functional**: Optimized for understanding complex data
- **Accessible**: Usable by everyone

Next: Define the ontology that encodes this visual language as semantic structure.
