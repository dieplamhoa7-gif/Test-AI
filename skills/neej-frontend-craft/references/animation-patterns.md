# Animation Patterns Reference

## Animation Strategy: CSS-First, Motion for Complex

Use the lightest tool that gets the job done:

1. **CSS Transitions** — hover states, focus rings, color changes, simple state toggles
2. **CSS Scroll-Driven Animations** — scroll reveals, parallax, progress indicators (zero JS, GPU-accelerated)
3. **CSS View Transitions API** — page/route transitions (zero JS, browser-native morphing)
4. **Motion (formerly Framer Motion)** — complex orchestrated animations, spring physics, shared layout, gesture-driven interactions

Install Motion: `npm install motion`
Import: `import { motion, AnimatePresence, useScroll, useTransform } from "motion/react"`

GSAP is NOT needed unless building a marketing-heavy scroll experience with complex timelines. For 95% of SaaS/dashboard/landing page work, CSS + Motion is sufficient.

## Animation Principles

1. **Purpose over decoration** — every animation must serve one of these UX goals:
   - Guide attention (reveal important content)
   - Confirm action (button click, form submit)
   - Show state change (loading → loaded, collapsed → expanded)
   - Create spatial context (where something came from, where it went)

2. **Performance constraints:**
   - ONLY animate `transform` and `opacity` — these are GPU-composited
   - NEVER animate `width`, `height`, `top`, `left`, `margin`, `padding` — these trigger layout recalc
   - Use `will-change: transform` sparingly and only on elements that will animate
   - Lazy-load Motion components below the fold

3. **Timing:**
   - UI transitions: 150-300ms (faster = snappier, more professional)
   - Page reveals: 400-600ms with stagger
   - Hover effects: 150ms
   - Spring animations: `{ type: "spring", stiffness: 300, damping: 30 }` for snappy, `{ stiffness: 100, damping: 15 }` for bouncy
   - NEVER use `linear` easing for UI — use `easeOut` for enter, `easeIn` for exit, spring for interactive

4. **Restraint:**
   - Dashboards: almost zero animation beyond state transitions
   - Landing pages: scroll reveals + hero animation + hover states, nothing more
   - Modals/drawers: slide + fade, 200ms, done
   - If you're adding animation and can't articulate why, don't add it

## Pattern Library

### Page Load Reveal (Landing Pages)
```tsx
const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.08,
      delayChildren: 0.1,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.5, ease: [0.25, 0.46, 0.45, 0.94] },
  },
};

// Usage
<motion.div variants={containerVariants} initial="hidden" animate="visible">
  <motion.h1 variants={itemVariants}>Heading</motion.h1>
  <motion.p variants={itemVariants}>Subtext</motion.p>
  <motion.div variants={itemVariants}>CTA Button</motion.div>
</motion.div>
```

### Scroll-Triggered Section Reveal
```tsx
const sectionVariants = {
  hidden: { opacity: 0, y: 40 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.6, ease: [0.25, 0.46, 0.45, 0.94] },
  },
};

// Usage — use whileInView, NOT intersection observer manually
<motion.section
  variants={sectionVariants}
  initial="hidden"
  whileInView="visible"
  viewport={{ once: true, margin: "-100px" }}
>
  {/* section content */}
</motion.section>
```

### Button Interactions
```tsx
// Subtle scale on hover/tap — DO NOT overdo this
<motion.button
  whileHover={{ scale: 1.02 }}
  whileTap={{ scale: 0.98 }}
  transition={{ type: "spring", stiffness: 400, damping: 25 }}
>
  Get Started
</motion.button>
```

### Card Hover Effect
```tsx
// Slight lift + border glow — NOT shadow change (too heavy)
<motion.div
  whileHover={{
    y: -2,
    transition: { duration: 0.2, ease: "easeOut" },
  }}
  className="border border-border hover:border-accent/50 transition-colors"
>
  {/* card content */}
</motion.div>
```

### Modal / Dialog Entry
```tsx
// Backdrop
<motion.div
  initial={{ opacity: 0 }}
  animate={{ opacity: 1 }}
  exit={{ opacity: 0 }}
  transition={{ duration: 0.2 }}
  className="fixed inset-0 bg-black/60"
/>

// Modal content
<motion.div
  initial={{ opacity: 0, scale: 0.95, y: 10 }}
  animate={{ opacity: 1, scale: 1, y: 0 }}
  exit={{ opacity: 0, scale: 0.95, y: 10 }}
  transition={{ duration: 0.2, ease: [0.25, 0.46, 0.45, 0.94] }}
>
  {/* modal content */}
</motion.div>
```

### Sidebar Collapse/Expand
```tsx
<motion.aside
  animate={{ width: isCollapsed ? 64 : 256 }}
  transition={{ duration: 0.2, ease: "easeInOut" }}
>
  {/* Use AnimatePresence for text labels */}
  <AnimatePresence>
    {!isCollapsed && (
      <motion.span
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        transition={{ duration: 0.15 }}
      >
        {label}
      </motion.span>
    )}
  </AnimatePresence>
</motion.aside>
```

### Skeleton Loading (CSS-only — don't use Motion for this)
```css
@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

.skeleton {
  background: linear-gradient(
    90deg,
    var(--surface) 25%,
    var(--surface-elevated) 50%,
    var(--surface) 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s ease-in-out infinite;
  border-radius: 6px;
}
```

### Number Counter (for stats/metrics)
```tsx
import { useMotionValue, useTransform, animate } from "motion/react";
import { useEffect } from "react";

function Counter({ target }: { target: number }) {
  const count = useMotionValue(0);
  const rounded = useTransform(count, (v) => Math.round(v));

  useEffect(() => {
    const controls = animate(count, target, { duration: 1.5 });
    return controls.stop;
  }, [target]);

  return <motion.span>{rounded}</motion.span>;
}
```

### Scroll-Driven Parallax (Landing Pages Only)
```tsx
import { useScroll, useTransform, motion } from "motion/react";
import { useRef } from "react";

function ParallaxSection() {
  const ref = useRef(null);
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start end", "end start"],
  });

  const y = useTransform(scrollYProgress, [0, 1], [60, -60]);
  const opacity = useTransform(scrollYProgress, [0, 0.3, 0.7, 1], [0, 1, 1, 0]);

  return (
    <div ref={ref}>
      <motion.div style={{ y, opacity }}>
        {/* parallax content */}
      </motion.div>
    </div>
  );
}
```

### Async Data List Stagger (Dashboard/Feed pattern)
When data loads from an API and renders a list/grid, stagger the items in.
This is different from page-load reveal — it happens when data arrives, not on mount.
```tsx
// Wrap the list container
<motion.div
  initial="hidden"
  animate="show"
  variants={{ hidden: {}, show: { transition: { staggerChildren: 0.04 } } }}
>
  {items.map(item => (
    <motion.div
      key={item.id}
      variants={{ hidden: { opacity: 0, x: -8 }, show: { opacity: 1, x: 0 } }}
      transition={{ duration: 0.3, ease: [0.25, 0.46, 0.45, 0.94] as const }}
    >
      <ItemCard item={item} />
    </motion.div>
  ))}
</motion.div>
```
Key differences from page-load stagger:
- Use `x: -8` (slide from left) for list rows, `y: 12` (slide up) for grid cards
- Tighter stagger (0.04-0.05s) for lists, wider (0.06-0.08s) for grids
- `as const` on ease array to satisfy Motion's TypeScript types

### Accordion / Expand Panel (AnimatePresence)
For expandable rows (tables, accordions, FAQ):
```tsx
<AnimatePresence>
  {isExpanded && (
    <motion.div
      initial={{ height: 0, opacity: 0 }}
      animate={{ height: 'auto', opacity: 1 }}
      exit={{ height: 0, opacity: 0 }}
      transition={{ duration: 0.25, ease: [0.25, 0.46, 0.45, 0.94] }}
      className="overflow-hidden"
    >
      <div className="px-4 py-5">{/* expanded content */}</div>
    </motion.div>
  )}
</AnimatePresence>
```
Note: The inner `<div>` with padding is important — padding on the `motion.div` itself
will animate and look wrong. Keep padding on a static inner wrapper.

### Scale Pulse on Data Complete
When a number counter finishes, add a subtle scale pulse:
```tsx
const controls = useAnimation();

function onCountComplete() {
  controls.start({
    scale: [1, 1.04, 1],
    transition: { duration: 0.3, ease: 'easeOut' },
  });
}

<motion.div animate={controls} whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
  {/* metric card content */}
</motion.div>
```

### Reusable Stagger Components
For projects with multiple staggered grids, create shared components:
```tsx
// StaggerReveal.tsx — reusable wrapper pair
export function StaggerGrid({ children, className }) {
  return (
    <motion.div
      variants={{ hidden: {}, show: { transition: { staggerChildren: 0.06 } } }}
      initial="hidden"
      animate="show"
      className={className}
    >
      {children}
    </motion.div>
  );
}

export function StaggerItem({ children, className }) {
  return (
    <motion.div
      variants={{
        hidden: { opacity: 0, y: 8 },
        show: { opacity: 1, y: 0, transition: { duration: 0.3, ease: [0.25, 0.46, 0.45, 0.94] as const } },
      }}
      className={className}
    >
      {children}
    </motion.div>
  );
}
```
Use: wrap any grid of cards (pricing tiers, feature cards, stat panels) without
rewriting variant objects every time.

### Orchestrated Demo Reveal
For demo/recording modes where panels should cascade in after a hero element:
```tsx
const stagger = {
  hidden: {},
  show: { transition: { staggerChildren: 0.08, delayChildren: 0.3 } },
};

const fadeUp = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0, transition: { duration: 0.5, ease: [0.25, 0.46, 0.45, 0.94] as const } },
};

// Hero element animates first
<motion.div initial={{ opacity: 0, scale: 0.8 }} animate={{ opacity: 1, scale: 1 }}
  transition={{ duration: 0.8 }}>
  {/* hero content */}
</motion.div>

// Dashboard panels cascade in 300ms later
<motion.div variants={stagger} initial="hidden" animate="show">
  <motion.div variants={fadeUp}>{metrics}</motion.div>
  <motion.div variants={fadeUp}>{charts}</motion.div>
  <motion.div variants={fadeUp}>{table}</motion.div>
</motion.div>
```

## Animation by Project Context

| Context | What to Animate | What NOT to Animate |
|---------|----------------|---------------------|
| Dashboard (normal) | Metric count-up, list stagger on data load, sidebar toggle, accordion expand | Chart redraws, static tables, background |
| Dashboard (demo mode) | EVERYTHING — hero reveal, orchestrated cascade, count-up + pulse, row stagger, micro-interactions | Nothing — go maximalist for recording |
| Landing | Hero reveal, section scroll-in, CTA hover, testimonial carousel | Background decorations, floating elements, particle effects |
| Portal | Page transitions, form states, status badges | Navigation, static content, logos |
| Dev Tool | Command palette open, tab switches, code highlights | File trees, config panels, log streams |

**Dashboard animation philosophy (revised):** The old rule was "almost zero animation for dashboards." This is wrong for products that need TikTok demos. The correct rule is: **normal mode should be fast and professional (subtle transitions only), demo mode should be maximalist (stagger everything, count up numbers, cascade panels).** Both modes use the same components — the animation intensity is the variable.

## Libraries to AVOID

- **React Transition Group** — unmaintained, deprecated patterns
- **React Move** — niche D3 use case only
- **Animate.css** — class-based, not React-idiomatic, cheap-looking
- **Lottie** — unless you have actual designer-made Lottie files (don't generate them)
- **Three.js / PixiJS** — unless the project specifically requires 3D/WebGL (none of the current projects do)

## CSS-Native Animation Patterns (Preferred for Simple Cases)

### CSS Scroll-Driven Section Reveal (Zero JS)
```css
/* Fade-up on scroll — no JavaScript needed */
@supports (animation-timeline: view()) {
  .scroll-reveal {
    animation: scroll-fade-up linear both;
    animation-timeline: view();
    animation-range: entry 0% entry 100%;
  }

  @keyframes scroll-fade-up {
    from {
      opacity: 0;
      transform: translateY(30px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
}

/* Fallback for Firefox (behind flag) — use Motion's whileInView */
@supports not (animation-timeline: view()) {
  .scroll-reveal {
    opacity: 1; /* don't hide content if no JS fallback loaded */
  }
}
```

### CSS Scroll Progress Indicator
```css
/* Progress bar at top of page tied to scroll position */
.scroll-progress {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 3px;
  background: var(--accent);
  transform-origin: left;
  animation: scroll-progress linear;
  animation-timeline: scroll(root);
}

@keyframes scroll-progress {
  from { transform: scaleX(0); }
  to { transform: scaleX(1); }
}
```

### CSS View Transitions (Page/Route Transitions)
```css
/* Enable View Transitions in Next.js App Router */
/* In layout.tsx or next.config.js — experimental viewTransition flag */

/* Default cross-fade (works out of the box) */
::view-transition-old(root) {
  animation: 200ms ease-out fade-out;
}
::view-transition-new(root) {
  animation: 300ms ease-out fade-in;
}

/* Named transitions for specific elements (e.g., hero image morphing between pages) */
.hero-image {
  view-transition-name: hero;
}
::view-transition-old(hero) {
  animation: 300ms ease-out scale-down;
}
::view-transition-new(hero) {
  animation: 300ms ease-in scale-up;
}

@keyframes fade-out { to { opacity: 0; } }
@keyframes fade-in { from { opacity: 0; } }
@keyframes scale-down { to { transform: scale(0.95); opacity: 0; } }
@keyframes scale-up { from { transform: scale(0.95); opacity: 0; } }
```

### When to Use CSS vs Motion

| Effect | Use CSS | Use Motion |
|--------|---------|-----------|
| Hover/focus states | Always CSS | Never |
| Simple scroll reveal | CSS `animation-timeline: view()` | Fallback only |
| Scroll progress bar | CSS `animation-timeline: scroll()` | Never |
| Page route transitions | CSS View Transitions API | Complex shared-element only |
| Spring physics | Never | Always |
| Gesture/drag interactions | Never | Always |
| Staggered list reveals | CSS if simple | Motion for orchestrated timing |
| Layout animations | Never | `layout` prop on motion.div |
| Parallax | CSS for simple | Motion for progress-linked |

## Supplementary Animation Libraries (Use Alongside Motion)

- **tailwindcss-motion** — for simple CSS-only transitions (hover states, focus rings). 5KB, zero JS.
- **Sonner** — for toast animations specifically. Already optimized, don't reinvent.
- **Vaul** — for drawer/bottom-sheet animations. Better than building from scratch.

## Accessibility: Motion

Always respect user preferences:
```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

In Motion components:
```tsx
import { useReducedMotion } from "motion/react";

function AnimatedComponent() {
  const shouldReduceMotion = useReducedMotion();
  return (
    <motion.div
      animate={{ y: shouldReduceMotion ? 0 : 20 }}
      transition={shouldReduceMotion ? { duration: 0 } : { type: "spring" }}
    />
  );
}
```
