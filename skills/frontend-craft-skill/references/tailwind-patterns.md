# Tailwind CSS Patterns Reference

Quick reference optimized for the shadcn/ui + Next.js stack.

---

## Utility Quick-Ref by Category

### Layout

| Utility | What it does | Common values |
|---|---|---|
| `flex` | Flexbox container | `flex-row`, `flex-col`, `flex-wrap` |
| `grid` | Grid container | `grid-cols-1`, `grid-cols-2`, `grid-cols-3`, `grid-cols-12` |
| `gap-*` | Gap between flex/grid children | `gap-2` (8px), `gap-4` (16px), `gap-6` (24px) |
| `items-*` | Align items (cross axis) | `items-center`, `items-start`, `items-stretch` |
| `justify-*` | Justify content (main axis) | `justify-center`, `justify-between`, `justify-end` |
| `container` | Responsive max-width | Pair with `mx-auto` for centering |
| `mx-auto` | Auto horizontal margin | Centers block elements |

### Spacing

| Utility | What it does | Common values |
|---|---|---|
| `p-*` | Padding all sides | `p-4` (16px), `p-6` (24px), `p-8` (32px) |
| `px-*` / `py-*` | Horizontal / vertical padding | `px-4 py-2` for buttons |
| `m-*` | Margin all sides | `m-0`, `m-4`, `-m-2` (negative) |
| `space-x-*` | Horizontal gap between children | `space-x-2`, `space-x-4` |
| `space-y-*` | Vertical gap between children | `space-y-4`, `space-y-6` |

### Typography

| Utility | What it does | Common values |
|---|---|---|
| `text-*` | Font size | `text-sm`, `text-base`, `text-lg`, `text-xl`, `text-2xl` |
| `font-*` | Font weight | `font-normal`, `font-medium`, `font-semibold`, `font-bold` |
| `leading-*` | Line height | `leading-tight`, `leading-normal`, `leading-relaxed` |
| `tracking-*` | Letter spacing | `tracking-tight`, `tracking-normal`, `tracking-wide` |
| `truncate` | Ellipsis overflow | Single line truncation |
| `line-clamp-*` | Multi-line truncation | `line-clamp-2`, `line-clamp-3` |
| `text-muted-foreground` | Semantic muted color | shadcn CSS variable |

### Colors (shadcn semantic tokens)

| Utility | What it does | Common values |
|---|---|---|
| `bg-background` | Page background | Default app bg |
| `bg-card` | Card background | Slightly elevated surface |
| `bg-primary` | Primary brand color | Buttons, highlights |
| `bg-muted` | Muted background | Secondary surfaces |
| `text-foreground` | Primary text color | Default readable text |
| `text-muted-foreground` | Secondary text | Descriptions, hints |
| `border-border` | Default border color | Dividers, outlines |
| `ring-ring` | Focus ring color | Focus indicators |
| `bg-destructive` | Error/danger color | Delete buttons, alerts |

### Sizing

| Utility | What it does | Common values |
|---|---|---|
| `w-*` | Width | `w-full`, `w-1/2`, `w-64`, `w-screen` |
| `h-*` | Height | `h-full`, `h-screen`, `h-10`, `h-auto` |
| `min-w-*` | Minimum width | `min-w-0` (flex child fix), `min-w-full` |
| `max-w-*` | Maximum width | `max-w-sm`, `max-w-md`, `max-w-2xl`, `max-w-prose` |
| `min-h-*` | Minimum height | `min-h-screen`, `min-h-0` |
| `aspect-*` | Aspect ratio | `aspect-video` (16:9), `aspect-square` |

### Borders & Effects

| Utility | What it does | Common values |
|---|---|---|
| `border` | 1px border | `border-2`, `border-b`, `border-t` |
| `rounded-*` | Border radius | `rounded-md`, `rounded-lg`, `rounded-full` |
| `divide-*` | Borders between children | `divide-y`, `divide-x` |
| `ring-*` | Box-shadow ring | `ring-2 ring-ring` for focus |
| `shadow-*` | Box shadow | `shadow-sm`, `shadow-md`, `shadow-lg` |
| `opacity-*` | Opacity | `opacity-50`, `opacity-75` |

### Transitions & Animation

| Utility | What it does | Common values |
|---|---|---|
| `transition-*` | Transition property | `transition-all`, `transition-colors`, `transition-transform` |
| `duration-*` | Transition duration | `duration-150`, `duration-200`, `duration-300` |
| `ease-*` | Easing function | `ease-in`, `ease-out`, `ease-in-out` |
| `animate-*` | Keyframe animation | `animate-spin`, `animate-pulse`, `animate-bounce` |

---

## Responsive Breakpoints

| Prefix | Min-width | Typical device |
|---|---|---|
| (none) | 0px | Mobile (default) |
| `sm:` | 640px | Large phone / small tablet |
| `md:` | 768px | Tablet |
| `lg:` | 1024px | Laptop |
| `xl:` | 1280px | Desktop |
| `2xl:` | 1536px | Large monitor |

### Mobile-first pattern

Always write base styles for mobile, then layer on breakpoints:

```tsx
<div className="flex flex-col md:flex-row gap-4 md:gap-8">
  <div className="w-full md:w-1/3">Sidebar</div>
  <div className="w-full md:w-2/3">Content</div>
</div>
```

### Max-width variants

Use `max-*:` to apply styles below a breakpoint:

```tsx
<div className="max-md:hidden">Only visible on md and above</div>
```

### Container queries

Use `@container` for component-scoped responsive design:

```tsx
<div className="@container">
  <div className="@md:flex @md:gap-4">
    Responds to container width, not viewport
  </div>
</div>
```

---

## Dark Mode

### Strategy: class-based with next-themes

shadcn uses class-based dark mode with `next-themes`. The `ThemeProvider` wraps your app:

```tsx
// app/layout.tsx
import { ThemeProvider } from "next-themes"

export default function RootLayout({ children }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
          {children}
        </ThemeProvider>
      </body>
    </html>
  )
}
```

### Pairing light and dark

Always pair light and dark styles when using non-semantic colors:

```tsx
<div className="bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100">
```

### Prefer semantic CSS variables

Instead of manually pairing `dark:` variants everywhere, use shadcn's semantic tokens. These switch automatically:

```tsx
{/* Preferred -- uses CSS variables that auto-switch */}
<div className="bg-background text-foreground border-border">

{/* Avoid -- requires manual dark: pairing */}
<div className="bg-white dark:bg-gray-950 text-black dark:text-white">
```

---

## Tailwind v4 @theme

The `@theme` directive defines custom design tokens in CSS:

```css
/* globals.css */
@import "tailwindcss";

@theme {
  /* Custom colors using oklch for perceptual uniformity */
  --color-brand-50: oklch(0.97 0.02 250);
  --color-brand-500: oklch(0.55 0.18 250);
  --color-brand-900: oklch(0.25 0.10 250);

  /* Custom fonts */
  --font-sans: "Inter", ui-sans-serif, system-ui, sans-serif;
  --font-mono: "JetBrains Mono", ui-monospace, monospace;

  /* Custom spacing */
  --spacing-18: 4.5rem;
  --spacing-88: 22rem;

  /* Custom breakpoints */
  --breakpoint-xs: 475px;

  /* Custom animations */
  --animate-slide-up: slide-up 0.3s ease-out;
}

@keyframes slide-up {
  from { transform: translateY(8px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}
```

Tokens defined in `@theme` become utilities automatically: `bg-brand-500`, `font-mono`, `animate-slide-up`.

---

## cn() Utility

`cn()` combines `clsx` (conditional classes) with `tailwind-merge` (deduplication):

```ts
// lib/utils.ts
import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
```

### When to use

```tsx
// Conditional classes
<div className={cn("rounded-lg border", isActive && "border-primary bg-primary/10")} />

// Component prop className merging (essential for shadcn wrappers)
function Card({ className, ...props }: ComponentProps<"div">) {
  return <div className={cn("rounded-lg border bg-card p-6", className)} {...props} />
}

// Variant overrides without conflicts
cn("px-4 py-2", "px-6")  // => "px-6 py-2" (tailwind-merge resolves conflicts)
```

### Why not just template literals

Template literals cause class conflicts: `${base} ${override}` may produce `px-4 px-6` where both apply. `cn()` ensures the last class wins.

---

## Arbitrary Values

Use square brackets for one-off values not in your design system:

```tsx
<div className="w-[calc(100%-2rem)]">  {/* CSS calc */}
<div className="bg-[#1a1a2e]">         {/* Hex color */}
<div className="text-[var(--custom)]">  {/* CSS variable */}
<div className="grid-cols-[200px_1fr]"> {/* Grid template */}
<div className="top-[117px]">           {/* Pixel value */}
```

### When arbitrary values are OK

- One-off layout adjustments (calc, specific pixel offsets)
- Consuming external CSS variables
- Grid templates with mixed units

### When to add to @theme instead

- Used in 3+ places
- Part of your design language (brand colors, spacing scale)
- Shared across components

---

## Performance Rules

- **No dynamic class construction** -- Tailwind scans source files statically. This breaks:
  ```tsx
  // BROKEN -- Tailwind cannot detect these classes
  const color = "red"
  className={`bg-${color}-500`}
  ```
- **Use safelist for truly dynamic classes** -- add to `tailwind.config.ts` safelist
- **Avoid `@apply` except for truly repeated base styles** -- it defeats Tailwind's purpose. Use `cn()` and component composition instead
- **Keep `globals.css` lean** -- only `@import`, `@theme`, CSS variable definitions, and minimal base styles

---

## Anti-Patterns

| Don't | Do instead |
|---|---|
| Inline `style={{ }}` attributes | Use Tailwind utilities or arbitrary values |
| Mix Tailwind with CSS Modules | Pick one -- Tailwind for everything in shadcn projects |
| Use `!important` or `@apply !` | Use `cn()` for specificity or restructure class order |
| Create utility CSS classes | Use Tailwind utilities directly or define in `@theme` |
| Hardcode colors (`bg-blue-500`) | Use semantic tokens (`bg-primary`) for theme consistency |
| Use `@apply` for component styles | Create React components with `cn()` |
| Nest selectors in CSS | Use Tailwind utilities -- flat is better than nested |
