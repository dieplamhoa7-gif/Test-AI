# Component Patterns Reference

Concrete implementation patterns for the most common UI components. Each pattern encodes the aesthetic from the design brief and avoids known AI slop patterns.

## Navigation / Header

### SaaS App Header (Dashboard Context)
```
Structure:
├── Logo (left) — 24px icon + wordmark, text-primary
├── Nav links (center or left-of-center) — text-secondary, hover:text-primary, active has bottom border accent
├── Search (center) — cmd+K trigger, subtle border, rounded-lg
└── Right cluster — notifications icon + avatar dropdown

Design rules:
- Height: 56-64px
- Background: var(--surface) or var(--background) with border-bottom
- NO hamburger menu on desktop
- Active link: text-primary + 2px bottom border in accent color (not background highlight)
- Search: ghost style (border only, no fill) with keyboard shortcut badge (⌘K)
- Avatar: 32px circle, ring-2 ring-border on hover
- Sticky: yes, with backdrop-blur-sm if transparent
```

### Landing Page Header
```
Structure:
├── Logo (left)
├── Nav links (center) — 4-5 max
├── CTA cluster (right) — ghost "Sign In" + solid "Get Started"

Design rules:
- Height: 64-72px
- Background: transparent initially, blur + surface on scroll (use useScroll)
- Max-width container (1280px) centered
- CTA button: accent background, 600 weight, px-5 py-2.5, rounded-lg
- Sign in: ghost (text only, no border), text-secondary hover:text-primary
- Mobile: hamburger below 768px, slide-in drawer (NOT dropdown)
- Transition on scroll: 300ms ease-out for background change
```

## Hero Sections

### SaaS Hero (Conversion-Focused)
```
Layout: LEFT-ALIGNED text (not centered), with product screenshot/mockup on right
         OR full-width centered text with product screenshot below

Content stack:
├── Badge/tag — "New: Feature X" in small pill, accent-muted bg, accent text, font-mono xs
├── H1 headline — 3xl-4xl, font-bold, text-primary, max-w-[600px]
│   (specific, not "Transform your workflow" — say what the product does)
├── Subtitle — lg, text-secondary, max-w-[500px], 1-2 sentences
├── CTA cluster — primary button + secondary link/button, gap-3
│   Primary: accent bg, white text, px-6 py-3, rounded-lg, font-medium
│   Secondary: ghost or outline, text-secondary
├── Social proof — small logos or "Used by X teams" with real numbers
└── Product visual — screenshot with subtle shadow + border, or 3D-ish perspective

Animation:
- Stagger reveal: badge → h1 → subtitle → CTA → social proof (80ms stagger)
- Product visual: fade in + slight y translate, 600ms, 200ms delay after text
- DO NOT float or bobble the product image

NEVER:
- "Welcome to [product]" as headline
- Abstract illustrations instead of real product screenshots
- More than 2 CTA buttons
- Gradient mesh background (unless it's very subtle and purpose-driven)
```

### Editorial Hero (Brand/Content)
```
Layout: Full-width, text centered or dramatically left-offset

Content stack:
├── Eyebrow — uppercase xs, letter-spacing 0.1em, text-secondary
├── H1 headline — 4xl+, display font (serif or distinctive sans), tight leading (1.1)
├── Divider — thin accent line, 64px wide, centered
└── Subtitle — base-lg, text-secondary, max-w-[480px]

Background: Dark (near-black) or dramatic gradient within ONE hue family
Animation: Fade up with stagger, 100ms between elements
Typography: This is where Pair B (Instrument Serif + Satoshi) shines
```

## Cards

### Feature/Info Card
```
Structure:
├── Icon — 40px container, accent-muted bg, accent icon, rounded-lg
├── Title — lg, font-semibold, text-primary
├── Description — sm, text-secondary, 2-3 lines max
└── Optional link — sm, accent color, "Learn more →"

Styling:
- Background: var(--surface)
- Border: 1px solid var(--border)
- Padding: 24px
- Border-radius: 8px
- NO box-shadow (use border for definition)
- Hover: border-color transitions to border-subtle or accent/20

Layout in grid:
- 3 columns on lg, 2 on md, 1 on sm
- Gap: 16-24px
- Cards should NOT all be identical height unless using grid auto-rows
```

### Pricing Card
```
Structure:
├── Plan name — sm font-semibold, uppercase, text-secondary
├── Price — 3xl font-bold + /mo in sm text-secondary
├── Description — sm text-secondary, 1 line
├── Divider — border-t
├── Feature list — check icons (accent) + feature text, gap-3
└── CTA button — full width

Highlighted plan:
- Border: 2px solid accent (not just thicker shadow)
- Badge: "Most Popular" pill, accent bg, top-right or above plan name
- Background: surface-elevated (slight lift)

NOT highlighted:
- Border: 1px solid border
- Background: surface

NEVER:
- 3 pricing cards all the same visual weight — ONE must dominate
- Strikethrough pricing unless it's a real discount
- More than 8 features listed — link to full comparison for more
```

### Testimonial Card
```
Structure:
├── Quote text — base, text-primary, italic optional, leading-relaxed
├── Divider or spacing
├── Author row:
│   ├── Avatar — 40px circle
│   ├── Name — sm font-semibold
│   └── Role/Company — xs text-secondary

Styling:
- Background: surface
- Border: 1px solid border
- Padding: 24px
- Opening quote mark: 3xl text-border/30 absolute -top-2 left-4 (decorative)
- NO star ratings unless from a real review platform
```

## Forms

### Input Field
```
Anatomy:
├── Label — sm font-medium text-primary, mb-1.5
├── Input — h-10, px-3, bg-surface, border border-border, rounded-md
│   Focus: ring-2 ring-accent/20 border-accent, outline-none
│   Error: border-destructive, ring-destructive/20
│   Disabled: opacity-50 cursor-not-allowed
├── Helper text — xs text-secondary, mt-1.5
└── Error message — xs text-destructive, mt-1.5 (replaces helper when error)

Rules:
- ALWAYS have a visible label (not just placeholder)
- Placeholder text: text-tertiary, should be example data not instruction
- Password fields: toggle visibility icon
- Required indicator: asterisk in text-destructive after label
- Max width for inputs: 400px for single-line, full-width for textareas
```

### Form Layout
```
Rules:
- Single column for most forms (don't split name into first/last side by side on mobile)
- Group related fields with subtle border or background section
- Primary submit button: right-aligned or full-width on mobile
- Cancel/back: ghost button, left of submit
- Form-level error: alert banner at top with destructive background
- Loading state on submit: button shows spinner + disabled state
- Success: redirect or inline success message (green accent)
```

## Tables (Dashboard Context)

### Data Table (Use TanStack Table)

Always use **TanStack Table v8** for data tables. It's headless (full markup control), 10-15kb, type-safe, and supports sorting, filtering, pagination, row selection, and column resizing.

```tsx
// Basic setup pattern
import { useReactTable, getCoreRowModel, getSortedRowModel, getPaginationRowModel, flexRender } from "@tanstack/react-table";

const table = useReactTable({
  data,
  columns,
  getCoreRowModel: getCoreRowModel(),
  getSortedRowModel: getSortedRowModel(),
  getPaginationRowModel: getPaginationRowModel(),
});
```

Pair with shadcn/ui's `<Table>` component for the visual layer.

```
Visual Structure:
├── Table header — bg-surface, text-xs uppercase text-secondary, font-medium
│   Sortable columns: cursor-pointer, hover shows sort icon
├── Table body — bg-background (alternating rows optional: surface/background)
│   Row hover: bg-surface
│   Row height: 48-56px
│   Cell padding: px-4 py-3
├── Pagination — bottom, right-aligned, prev/next + page numbers
└── Optional: checkbox column (left), actions column (right)

Styling:
- Borders: border-b only (horizontal lines), no vertical borders
- Header: sticky if table scrolls
- Empty state: centered text + illustration/icon, "No data yet"
- Loading: skeleton rows (3-5 rows of shimmer)
- Overflow: horizontal scroll on mobile with sticky first column

NEVER:
- Zebra striping with high-contrast alternating colors
- Borders on every cell (grid look)
- Wrapping text that makes rows different heights (truncate with tooltip)
```

## Sidebar (Dashboard Context)

### App Sidebar
```
Structure:
├── Logo area — h-16, px-4, border-b
├── Main nav — py-4, flex-1 overflow-y-auto
│   ├── Section label — xs uppercase text-tertiary, px-4, mb-2
│   └── Nav items — px-3, py-2, rounded-md, gap-1
│       Icon (20px) + Label (sm)
│       Active: bg-surface-elevated, text-primary
│       Inactive: text-secondary, hover:bg-surface hover:text-primary
├── Divider — border-t
└── Footer — user avatar + name + settings cog, px-4, py-3

Styling:
- Width: 256px expanded, 64px collapsed
- Background: var(--surface) or var(--background)
- Border-right: 1px solid var(--border)
- Collapse trigger: button at bottom or top of sidebar, or auto-collapse on md breakpoint

Animation:
- Width transition: 200ms ease-in-out
- Labels: AnimatePresence fade in/out on collapse toggle
- Tooltip on collapsed items: show label on hover
```

## Modals / Dialogs

### Standard Modal
```
Structure:
├── Overlay — fixed inset-0, bg-black/60, backdrop-blur-sm (optional)
├── Modal container — centered, max-w-md, bg-surface, rounded-xl, border
│   ├── Header — px-6 pt-6, title (lg font-semibold) + close button (X icon, top-right)
│   ├── Body — px-6 py-4, content
│   └── Footer — px-6 pb-6, flex justify-end gap-3
│       Cancel: ghost button
│       Confirm: primary button (accent or destructive depending on action)

Rules:
- ALWAYS have a close button (X) in top-right
- ALWAYS closeable by clicking overlay
- ALWAYS closeable by pressing Escape
- Focus trap: tab cycles within modal
- Return focus to trigger element on close
- Destructive actions: confirm button is destructive color, add warning text

Animation:
- Overlay: fade in 200ms
- Modal: scale(0.95) + opacity(0) → scale(1) + opacity(1), 200ms
- Exit: reverse, 150ms (exits should be faster than enters)
```

## Toast Notifications

Use **Sonner** library — don't build custom toasts.

```tsx
import { toast } from "sonner";

// Success
toast.success("Changes saved");

// Error
toast.error("Failed to update", { description: "Please try again" });

// Loading → Success
const id = toast.loading("Saving...");
// later:
toast.success("Saved!", { id });
```

Position: bottom-right for dashboards, top-center for landing pages.

## Empty States

```
Structure (centered in container):
├── Icon or illustration — 48-64px, text-tertiary
├── Title — lg font-semibold text-primary
├── Description — sm text-secondary, max-w-[360px]
└── CTA — primary button or link to take action

Rules:
- Keep illustrations simple — line icons from Lucide, not elaborate graphics
- Description should tell user WHAT to do, not just that nothing is here
- CTA should be the most logical next action
- Example: "No agents yet" → "Create your first AI agent" → [Create Agent] button
```

## Loading States

### Skeleton Screen (preferred over spinners)
```
Rules:
- Match the EXACT layout of the loaded content
- Skeleton elements should be the same size/position as real content
- Use CSS shimmer animation (from animation-patterns.md)
- Show 3-5 skeleton items for lists
- Transition: skeleton → real content with 200ms fade

NEVER:
- Full-page spinner with "Loading..."
- Skeleton that doesn't match the final layout
- Loading states longer than 3s without a progress indicator or retry option
```

### Button Loading
```
- Replace button text with spinner (16px) + "Saving..." text
- Button stays same width (prevent layout shift)
- Disabled state during loading
- Use pointer-events-none + opacity-80
```

## Data Visualization (Charts)

### Library Selection

| Library | Best For | Max Data Points | Rendering |
|---------|----------|-----------------|-----------|
| **Recharts** | Standard SaaS dashboards, quick delivery | ~5K | SVG |
| **Nivo** | Presentation-quality, many chart types, server-side rendering | ~5K (Canvas mode for more) | SVG/Canvas |
| **Chart.js** | Real-time monitoring, massive datasets | 1M+ | Canvas |

Default: **Recharts** for dashboards. Use **Nivo** when you need stunning charts for demos/pitches or many chart types on the same page.

### Chart Theming (CRITICAL)

NEVER use default chart colors. Theme every chart with project CSS variables:

```tsx
// Recharts — themed with CSS variables
const CHART_COLORS = {
  primary: "var(--accent)",
  secondary: "var(--text-tertiary)",
  grid: "var(--border-subtle)",
  text: "var(--text-secondary)",
  tooltip: {
    bg: "var(--surface-elevated)",
    border: "var(--border)",
    text: "var(--text-primary)",
  },
};

// Apply to Recharts components
<ResponsiveContainer width="100%" height={300}>
  <LineChart data={data}>
    <CartesianGrid stroke="var(--border-subtle)" strokeDasharray="3 3" />
    <XAxis
      dataKey="date"
      tick={{ fill: "var(--text-secondary)", fontSize: 12 }}
      axisLine={{ stroke: "var(--border)" }}
    />
    <YAxis
      tick={{ fill: "var(--text-secondary)", fontSize: 12 }}
      axisLine={{ stroke: "var(--border)" }}
    />
    <Tooltip
      contentStyle={{
        backgroundColor: "var(--surface-elevated)",
        border: "1px solid var(--border)",
        borderRadius: 8,
        color: "var(--text-primary)",
      }}
    />
    <Line
      type="monotone"
      dataKey="value"
      stroke="var(--accent)"
      strokeWidth={2}
      dot={false}
      activeDot={{ r: 4, fill: "var(--accent)" }}
    />
  </LineChart>
</ResponsiveContainer>
```

### Chart Design Rules

1. **One chart, one insight** — don't overload charts with 5+ data series
2. **Label axes clearly** — no abbreviations without context
3. **Use consistent colors** — primary metric = accent color, secondary = text-tertiary
4. **Tooltips on hover** — styled with project design tokens, not library defaults
5. **Responsive** — use `<ResponsiveContainer>` always, never fixed widths
6. **Loading state** — show skeleton matching chart dimensions, not a spinner
7. **Empty state** — "No data for this period" with suggestion to adjust filters
8. **Dark mode** — chart colors must work on both dark and light backgrounds

### Chart Types by Use Case

| Data Story | Chart Type | Library |
|-----------|-----------|---------|
| Trend over time | Line chart | Recharts |
| Comparing categories | Bar chart (horizontal for many categories) | Recharts |
| Part of whole | Donut chart (NOT pie — leave center open for KPI) | Recharts/Nivo |
| Distribution | Area chart or histogram | Recharts |
| Correlation | Scatter plot | Nivo |
| Progress toward goal | Radial progress or gauge | Custom CSS |
| Real-time data stream | Line chart with canvas rendering | Chart.js |

### Dashboard Layout: Bento Grid

For dashboard pages with multiple charts/KPIs, use a **Bento Grid** pattern:
```
Rules:
- CSS Grid with 12 columns
- Limit to 12-15 cards max visible simultaneously
- Vary card sizes (2x1 for KPIs, 4x2 for charts, 6x2 for main chart)
- Uniform gaps: 16-24px
- KPI cards: compact (number + label + trend indicator)
- Chart cards: title + subtitle + chart + optional legend below
```

## Badge / Status Indicators

```
Variants:
- Default:  bg-surface-elevated text-secondary — neutral
- Success:  bg-green-500/10 text-green-500 — active, completed, online
- Warning:  bg-yellow-500/10 text-yellow-500 — pending, expiring
- Error:    bg-red-500/10 text-red-500 — failed, error, overdue
- Info:     bg-blue-500/10 text-blue-500 — new, updated
- Accent:   bg-accent/10 text-accent — featured, highlighted

Sizing: text-xs, px-2 py-0.5, rounded-full, font-medium
Live indicators: 8px circle (bg-green-500 with pulse animation for "online")
```

## Metric Card with Counter Animation

For dashboards where KPIs need to feel alive:

```
Structure:
├── Label — text-[10px] font-semibold uppercase tracking-widest text-muted-foreground/50
├── Value — text-2xl font-semibold tabular-nums (counts up from 0 on mount)
└── Optional change indicator — TrendingUp/TrendingDown icon + percentage

Counter implementation:
- RAF-based useCountUp hook (not Motion's useMotionValue — too heavy for 5+ cards)
- Duration: 800ms with cubic ease-out
- Parse any format: "250,613", "5.0%", "$19" — extract numeric, animate, reformat
- Scale pulse (1.04x → 1x over 300ms) when count completes
- whileHover: scale(1.02), whileTap: scale(0.98) on the card wrapper

Accent variant:
- Primary metric (e.g., Views): border-accent/30 + text-accent on the value
- Other metrics: border-border, text-foreground

NEVER:
- Animate all cards simultaneously — stagger with 60ms delay
- Use spinner during count — the count IS the loading animation
- Count up values that are 0 — just show "0" instantly
```

## Kanban Board (Content Pipeline)

```
Structure:
├── 5 columns: Ideas → Scripted → Ready → Posted → Analyzing
├── Each column:
│   ├── Header: colored dot + label + count
│   └── Card stack: items with forward/back navigation

Column headers:
- Colored dot (w-2 h-2 rounded-full) — unique color per status
- Status label — text-xs font-medium text-muted-foreground
- Count — text-[10px] font-mono text-muted-foreground/30 tabular-nums ml-auto

Card treatment:
- rounded-lg border border-border bg-card p-3
- Topic: font-medium text-[13px] leading-snug
- Notes: text-[11px] text-muted-foreground/50 line-clamp-2
- Navigation: border-t separator, forward/back buttons always visible (not hover-only)

Status navigation buttons:
- Back: text-[11px] min-h-6 px-1.5 text-muted-foreground/40 hover:text-foreground
- Forward: text-[11px] min-h-6 px-1.5 text-accent/60 hover:text-accent font-medium
- Forward is accent-colored (CTA direction), back is neutral
- WCAG: min 24px touch target (min-h-6 = 24px)

Color mapping (recommended):
  idea:      bg-chart-4 (amber) — brainstorming
  script:    bg-chart-3 (blue) — writing
  ready:     bg-accent (orange) — ready to go
  posted:    bg-success (green) — published
  analyzing: bg-chart-5 (purple) — processing

NEVER:
- Hide navigation buttons behind hover — users need to see they can move items
- Use drag-and-drop as the ONLY move mechanism — always provide button fallback
- Show all target statuses as buttons — only show forward/back (adjacent steps)
```

## Quick-Capture Textarea (Notes/Ideas)

```
Structure:
├── Textarea — resize-none, text-[13px], placeholder "What's on your mind?..."
├── Footer row:
│   ├── Character count (left) — text-[10px] font-mono tabular-nums
│   └── Submit button (right) — accent CTA

Character count:
- Format: "42/500"
- Color: text-muted-foreground/30 normally
- Color: text-destructive/60 when within 50 chars of limit
- Enforce limit in onChange: e.target.value.slice(0, 500)

Empty state (below textarea):
- Icon: relevant Lucide icon at h-8 w-8 text-muted-foreground/30 strokeWidth={1.5}
- Title: text-sm font-medium text-foreground mb-1
- Description: text-[13px] text-muted-foreground/50, explain what the data feeds into
```

## Ranked Opportunity List (Daily Brief pattern)

```
Structure per item:
├── Rank badge (left) — w-9 h-9 rounded-lg, centered number
├── Content (right):
│   ├── Title + confidence badge inline
│   ├── Reasoning text
│   └── Sub-items (e.g., draft hooks) with accent left border

#1 ranked item:
- Border: border-accent/30 on the card
- Rank badge: bg-accent/15 text-accent
- Overall card: p-5 (slightly more padding than others)

#2+ ranked items:
- Border: border-border
- Rank badge: bg-secondary text-muted-foreground

Confidence badges use translucent pattern (see Badge section above).

CTA button (e.g., "Generate Script"):
- bg-accent hover:bg-accent/90 text-accent-foreground
- Positioned top-right of the content area
- shrink-0 to prevent wrapping
```

## Demo Mode Toggle

For products that need TikTok/demo recordings:

```
Position: top-right of the page, below the header
Style: text-[11px] min-h-7 px-2.5 rounded-md
  Active: bg-accent/15 text-accent
  Inactive: text-muted-foreground/40 hover:text-muted-foreground

Icons:
  Normal → Demo: Sparkles icon
  Demo → Normal: LayoutDashboard icon

Implementation:
- Simple useState toggle (NOT URL params — too fragile with navigation)
- Wrap page content in a client component that switches layouts
- Normal mode: standard dashboard layout
- Demo mode: hero element center stage, panels stagger-reveal below
```
