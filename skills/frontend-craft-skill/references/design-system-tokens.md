# Design System Tokens

Token architecture and CSS variable system for shadcn/ui + Tailwind CSS v4 projects.

---

## 3-Tier Token Architecture

Design tokens flow through three layers. Each layer adds meaning and reduces coupling.

```
PRIMITIVE TOKENS          SEMANTIC TOKENS           COMPONENT TOKENS
(raw values)              (purpose/intent)          (scoped to component)

--blue-500: #3b82f6  -->  --primary: var(--blue-500)  -->  --button-bg: var(--primary)
--gray-100: #f3f4f6  -->  --muted: var(--gray-100)    -->  --card-bg: var(--muted)
--radius-md: 0.5rem  -->  --radius: var(--radius-md)  -->  --dialog-radius: var(--radius)
```

### Why Three Tiers?

- **Primitive tokens** are raw design values. They never appear in component code directly.
- **Semantic tokens** describe purpose (`--primary`, `--destructive`), not appearance. Theme switching only changes this layer.
- **Component tokens** scope decisions to a single component. Optional---use only when a component diverges from semantic defaults.

shadcn/ui operates primarily at the **semantic** tier. CSS variables in `:root` define the semantic tokens. Component code references them through Tailwind classes (`bg-primary`, `text-muted-foreground`).

---

## CSS Variable Reference

shadcn/ui expects these CSS variables defined in `globals.css`. All values use **HSL channels** format (without the `hsl()` wrapper) so Tailwind can apply opacity modifiers.

**Full starter file with all variables:** See `assets/globals-template.css` — copy to `app/globals.css` and customize.

### Required Semantic Tokens

| Token | Light Default | Purpose |
|-------|--------------|---------|
| `--background` / `--foreground` | `0 0% 100%` / `240 10% 3.9%` | Page surface + default text |
| `--card` / `--card-foreground` | `0 0% 100%` / `240 10% 3.9%` | Card/elevated surfaces |
| `--popover` / `--popover-foreground` | `0 0% 100%` / `240 10% 3.9%` | Dropdowns, tooltips |
| `--primary` / `--primary-foreground` | `240 5.9% 10%` / `0 0% 98%` | Primary actions (buttons, links) |
| `--secondary` / `--secondary-foreground` | `240 4.8% 95.9%` / `240 5.9% 10%` | Secondary actions |
| `--muted` / `--muted-foreground` | `240 4.8% 95.9%` / `240 3.8% 46.1%` | Subtle backgrounds, placeholders |
| `--accent` / `--accent-foreground` | `240 4.8% 95.9%` / `240 5.9% 10%` | Hover/active states |
| `--destructive` / `--destructive-foreground` | `0 84.2% 60.2%` / `0 0% 98%` | Error/delete actions |
| `--border` | `240 5.9% 90%` | Default borders |
| `--input` | `240 5.9% 90%` | Input field borders |
| `--ring` | `240 5.9% 10%` | Focus ring color |
| `--radius` | `0.5rem` | Base border-radius |

Every token needs both `:root` (light) and `.dark` values. The `.dark` class is toggled by `next-themes`.

---

## Color Generation

How to generate a full theme from a single brand color.

### Step-by-Step Process

**1. Pick your brand color and express in oklch:**
```
Brand: oklch(0.637 0.237 25.331)  /* A vibrant red-orange */
```

**2. Generate a lightness scale (keep hue + chroma, vary lightness):**
```
50:  oklch(0.97 0.02 25)   /* Near-white tint */
100: oklch(0.93 0.04 25)
200: oklch(0.87 0.08 25)
300: oklch(0.78 0.13 25)
400: oklch(0.70 0.18 25)
500: oklch(0.637 0.237 25) /* Brand color = 500 */
600: oklch(0.55 0.20 25)
700: oklch(0.45 0.17 25)
800: oklch(0.35 0.12 25)
900: oklch(0.25 0.08 25)   /* Near-black shade */
950: oklch(0.17 0.05 25)
```

**3. Reduce chroma at extremes** --- Very light and very dark shades need lower chroma to avoid oversaturation.

**4. Map to semantic tokens:**
```css
:root {
  --background: /* 50 shade converted to HSL */
  --foreground: /* 950 shade */
  --primary: /* 500 (brand) shade */
  --primary-foreground: /* 50 shade */
  --muted: /* 100 shade */
  --muted-foreground: /* 600 shade */
  --border: /* 200 shade */
  --ring: /* 500 shade */
}
```

**5. Generate accent via hue rotation:**
```
Complement: rotate +180° = oklch(0.637 0.237 205)  /* Teal */
Analogous:  rotate +30°  = oklch(0.637 0.237 55)   /* Warm yellow */
Triadic:    rotate +120° = oklch(0.637 0.237 145)  /* Green */
```

**6. Convert to HSL for shadcn** --- oklch gives perceptually uniform steps; HSL is the final output format for shadcn CSS variables.

---

## Typography Scale

Tailwind's default type scale with semantic usage guidelines.

| Class | Size | Semantic Use |
|-------|------|-------------|
| `text-xs` | 0.75rem (12px) | Captions, badges, metadata |
| `text-sm` | 0.875rem (14px) | Secondary text, table cells, form labels |
| `text-base` | 1rem (16px) | Body text, paragraphs, default |
| `text-lg` | 1.125rem (18px) | Lead paragraphs, card descriptions |
| `text-xl` | 1.25rem (20px) | Card titles, section subheads |
| `text-2xl` | 1.5rem (24px) | Section headings (h3) |
| `text-3xl` | 1.875rem (30px) | Page subheadings (h2) |
| `text-4xl` | 2.25rem (36px) | Page titles (h1) |
| `text-5xl` | 3rem (48px) | Hero headlines |
| `text-6xl` | 3.75rem (60px) | Display / landing hero |

### Line Height Rules
- **Body text** (`text-sm` to `text-lg`): Use `leading-relaxed` (1.625) or default. Never less than 1.4.
- **Headings** (`text-2xl` and up): Use `leading-tight` (1.25) or `leading-none` (1).
- **Single-line UI** (buttons, badges): Use `leading-none`.

---

## Spacing System

Tailwind uses a 4px base unit. `p-1` = 4px, `p-2` = 8px, `p-4` = 16px, etc.

### Common UI Patterns

| Pattern | Value | Notes |
|---------|-------|-------|
| **Card** | `p-6` (24px) | Use `p-4` on mobile via responsive |
| **Dialog** | `p-6` (24px) | Matches shadcn Dialog default |
| **Form fields** | `space-y-4` / `gap-4` | Between label+input groups |
| **Form sections** | `space-y-8` / `gap-8` | Between logical groups |
| **Button group** | `gap-2` to `gap-3` | Inline actions |
| **Page container** | `px-4 md:px-6 lg:px-8` | Responsive horizontal padding |
| **Max content width** | `max-w-7xl mx-auto` | 1280px standard |

### Grid Scale Guide
- **4px** (`gap-1`): Tight---toolbars, icon buttons, badges.
- **8px** (`gap-2`): Standard---form elements, list items, table cells.
- **16px** (`gap-4`): Comfortable---cards, content sections.
- **32px** (`gap-8`): Spacious---hero sections, feature grids.

---

## Shadow & Border Radius

### Elevation Levels

| Level | Class | Use Case |
|-------|-------|----------|
| 0 - Flat | `shadow-none` | Inline elements, list items |
| 1 - Subtle | `shadow-sm` | Cards at rest, input fields |
| 2 - Default | `shadow` | Elevated cards, dropdowns |
| 3 - Medium | `shadow-md` | Popovers, floating elements |
| 4 - Large | `shadow-lg` | Modals, dialogs |

### Border Radius Tokens

shadcn uses `--radius` as a base value and derives others:

| Class | Value | Usage |
|-------|-------|-------|
| `rounded-sm` | `calc(var(--radius) - 4px)` | Chips, badges |
| `rounded-md` | `calc(var(--radius) - 2px)` | Buttons, inputs |
| `rounded-lg` | `var(--radius)` | Cards, dialogs |
| `rounded-xl` | `calc(var(--radius) + 4px)` | Large containers |
| `rounded-full` | `9999px` | Avatars, circular buttons |

Change `--radius` once and the entire system scales proportionally.
