# Animation & Motion Reference

Patterns for CSS transitions, Framer Motion, and anime.js v4 in Next.js applications.

---

## Decision Tree

| Scenario | Use | Why |
|---|---|---|
| Hover effects, color changes, opacity | **Tailwind transitions** | Zero JS, best performance |
| Simple state changes (show/hide, expand) | **Tailwind transitions** | CSS handles enter/exit with group/peer |
| Page transitions, route animations | **Framer Motion** | AnimatePresence handles mount/unmount |
| Layout animations, smooth reflows | **Framer Motion** | `layout` prop automates FLIP |
| Gesture-based (drag, pan, pinch) | **Framer Motion** | Built-in gesture recognition |
| Shared element transitions | **Framer Motion** | `layoutId` morphs between views |
| Complex orchestrated sequences | **anime.js v4** | Timeline API with precise control |
| SVG path animation | **anime.js v4** | Native SVG property support |
| Staggered reveals (lists, grids) | **anime.js v4** | `stagger()` with grid support |

**Rule of thumb:** Start with Tailwind. Reach for Framer Motion when you need mount/unmount or layout animation. Use anime.js for orchestration beyond what Framer Motion handles cleanly.

---

## Tailwind Transitions

### Key classes

| Class | What it does |
|---|---|
| `transition-all` | Transitions all properties |
| `transition-colors` | Transitions color properties only |
| `transition-transform` | Transitions transform only |
| `duration-150` / `duration-200` / `duration-300` | Snappy / default / smooth |
| `ease-in-out` / `ease-out` | Standard / decelerate (for enter) |

### Common patterns

```tsx
{/* Hover scale */}
<button className="transition-transform duration-200 hover:scale-105">

{/* Fade + slide on conditional render */}
<div className={cn(
  "transition-all duration-300 ease-out",
  isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-2"
)}>

{/* Group hover -- parent hover affects child */}
<div className="group cursor-pointer">
  <span className="transition-colors group-hover:text-primary">Label</span>
  <ChevronRight className="transition-transform group-hover:translate-x-1" />
</div>
```

### Reduced motion

```tsx
<div className="motion-safe:animate-bounce motion-reduce:animate-none">
```

---

## Framer Motion Patterns

> Every component using Framer Motion must have `"use client"` at the top of the file.

### 1. Fade in / AnimatePresence (mount/unmount)

```tsx
"use client"
import { AnimatePresence, motion } from "framer-motion"

// Simple fade in on mount
export function FadeIn({ children }: { children: React.ReactNode }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
    >
      {children}
    </motion.div>
  )
}

// Page transitions — wrap in layout, key by pathname
// AnimatePresence mode="wait" ensures exit completes before enter starts
```

### 2. Layout animation + shared layout (layoutId)

```tsx
"use client"
import { motion } from "framer-motion"

// layout prop: auto-animates position/size changes via FLIP technique
<motion.div layout className={cn("rounded-lg border p-4", isExpanded && "col-span-2")}>
  <motion.h3 layout="position">Card Title</motion.h3>
</motion.div>

// layoutId: morphs between positions when active element changes
{activeTab === tab && (
  <motion.div
    layoutId="active-tab"
    className="absolute inset-0 rounded-md bg-primary/10"
    transition={{ type: "spring", bounce: 0.2, duration: 0.4 }}
  />
)}
```

### 3. Scroll-triggered with useInView

```tsx
"use client"
import { motion, useInView } from "framer-motion"
import { useRef } from "react"

export function ScrollReveal({ children }: { children: React.ReactNode }) {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: "-100px" })

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 40 }}
      animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 40 }}
      transition={{ duration: 0.5, ease: "easeOut" }}
    >
      {children}
    </motion.div>
  )
}
```

---

## anime.js v4 Quick-Ref

### CRITICAL: v4 syntax only

anime.js v4 has a completely different API from v3. Do not mix them.

```ts
// v4 -- CORRECT
import { animate, createTimeline, stagger } from 'animejs'

// v3 -- WRONG (do NOT use)
// import anime from 'animejs'
```

### Basic animation

```ts
import { animate } from 'animejs'

animate('.card', {
  x: 250,
  opacity: [0, 1],
  duration: 0.5,
  ease: 'outQuad',
})
```

### Timeline

```ts
import { createTimeline } from 'animejs'

const tl = createTimeline({
  defaults: { duration: 0.5, ease: 'outQuad' },
})

tl.add('.header', { y: [-20, 0], opacity: [0, 1] })
  .add('.content', { y: [20, 0], opacity: [0, 1] }, '-=0.2')
  .add('.footer', { opacity: [0, 1] })
```

### Stagger

```ts
import { animate, stagger } from 'animejs'

// Sequential stagger
animate('.list-item', {
  x: [50, 0],
  opacity: [0, 1],
  delay: stagger(0.1),
  duration: 0.4,
  ease: 'outQuad',
})

// Grid stagger (from center)
animate('.grid-item', {
  scale: [0, 1],
  delay: stagger(0.05, { grid: [4, 4], from: 'center' }),
  duration: 0.3,
})
```

### v3 → v4 migration cheatsheet

| v3 | v4 |
|---|---|
| `import anime from 'animejs'` | `import { animate } from 'animejs'` |
| `anime({ targets: '.el', ... })` | `animate('.el', { ... })` |
| `easing: 'easeOutQuad'` | `ease: 'outQuad'` |
| `anime.timeline()` | `createTimeline()` |
| `anime.stagger(100)` | `stagger(0.1)` (if timeUnit='s') |

---

## Performance Rules

### Only animate cheap properties

GPU-accelerated (no layout recalculation):
- `transform` (translate, scale, rotate) — via Tailwind: `translate-x-*`, `scale-*`, `rotate-*`
- `opacity` — via Tailwind: `opacity-*`

Avoid animating: `width`, `height`, `top`, `left`, `margin`, `padding`. These trigger layout reflows.

### Respect prefers-reduced-motion

```tsx
// Tailwind
<div className="motion-safe:animate-slide-up motion-reduce:opacity-100">

// Framer Motion respects prefers-reduced-motion by default

// anime.js -- check manually
const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches
if (!prefersReduced) { animate('.el', { x: 100, duration: 0.5 }) }
```

### Batch animations in timelines

Individual `animate()` calls each set up their own requestAnimationFrame loop. Use `createTimeline()` to batch related animations into a single render cycle.
