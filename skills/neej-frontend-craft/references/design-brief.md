# Neej's Design Brief — Source of Truth

This document encodes specific aesthetic preferences. Read this BEFORE writing any frontend code.

## Aesthetic Identity

The target aesthetic sits at the intersection of **Linear**, **Vercel**, **Attio**, and **Raycast** — modern B2B SaaS with editorial confidence. The look is:

- **Dark-first** — dark backgrounds with carefully controlled light surfaces for cards/modals
- **High information density** with breathing room (dense ≠ cramped)
- **Surgical precision** — every pixel is intentional, no decorative filler
- **Subtle depth** — layered surfaces using opacity and subtle borders, not heavy shadows
- **Monochromatic base** with a single accent color that pops

This is NOT healthcare UI. NOT enterprise-bland. NOT consumer-playful. It's **technical and refined**, the kind of interface that makes developers trust it immediately.

## Typography System

### Variable Font Strategy (2026 Best Practice)
Always use variable fonts when available. Benefits:
- Single WOFF2 file replaces multiple weight files — faster LCP, lower CLS
- Smooth weight transitions for hover effects with zero layout shift
- Optical size (`opsz`) axis auto-adjusts readability at different sizes
- Dark mode: use slightly lighter `font-weight` (e.g., 380 instead of 400) for identical perceived heaviness on dark backgrounds

**Key variable font axes to leverage:**
- `wght` (weight): Use exact values like 450, 550 — not just 400/600/700 increments
- `opsz` (optical size): Let the browser auto-optimize — small text gets thicker strokes, large headings get thinner strokes. Set via `font-optical-sizing: auto`
- `GRAD` (grade): Adjust visual weight without changing layout — perfect for hover states with zero layout shift

**Loading strategy:**
```css
/* Define variable font with fallback for non-supporting browsers */
@supports (font-variation-settings: normal) {
  :root { font-family: 'Geist Sans Variable', system-ui, sans-serif; }
}
```

### Preferred Font Pairings (pick ONE per project, don't mix across projects)

**Pair A — Technical Confidence (default for SaaS/dashboards):**
- Display/Headings: **Geist Sans** (variable, wght 100-900) at weight 600-700
- Body: **Geist Sans** at weight 400 (380 in dark mode)
- Mono: **Geist Mono** (variable) or **JetBrains Mono** (variable, wght 100-800)
- Load from: `@fontsource-variable/geist-sans` or `next/font/local`
- Note: Geist is a variable font — use `@fontsource-variable` not `@fontsource`

**Pair B — Editorial Authority (for landing pages, marketing):**
- Display: **Instrument Serif** or **Playfair Display** (variable, wght+opsz) at weight 700
- Headings: **Satoshi** (variable, wght 300-900) or **General Sans** at weight 600
- Body: **Satoshi** at weight 400 / **General Sans** at weight 400
- Mono: **IBM Plex Mono** (variable)
- Load from: Google Fonts (variable) + fontshare.com (Satoshi, General Sans are variable)

**Pair C — Minimal & Sharp (for developer tools, docs):**
- Display/Headings: **Inter Tight** (variable, wght+opsz) at weight 600-700 — yes, Inter Tight is different from Inter
- Body: **Inter Tight** at weight 400
- Mono: **Fira Code** (variable, wght 300-700) or **Berkeley Mono**
- Load from: Google Fonts (variable)

**Pair D — Premium & Distinctive (for client-facing portals, high-end):**
- Display: **Neue Montreal** or **Cabinet Grotesk** (variable) at weight 700
- Headings: **Neue Montreal** at weight 500
- Body: **Neue Montreal** at weight 400
- Load from: fontshare.com (both are variable fonts)

### Typography Scale
Base: 16px, scale ratio 1.25 (Major Third)
```
xs:    12px / 0.75rem  — captions, labels
sm:    14px / 0.875rem — secondary text, table cells
base:  16px / 1rem     — body text
lg:    20px / 1.25rem  — subheadings, card titles
xl:    25px / 1.563rem — section headings
2xl:   31px / 1.953rem — page headings
3xl:   39px / 2.441rem — hero headings
4xl:   49px / 3.052rem — display text (landing pages only)
```

### Typography Rules
- Line height: 1.5 for body, 1.2 for headings, 1.1 for display
- Letter spacing: -0.01em for headings, 0 for body, 0.05em for uppercase labels
- Max line width: 65-75ch for body text
- NEVER use font-weight below 400 for body text
- NEVER use ALL CAPS for more than 2 words (labels and tags only)
- Enable `font-optical-sizing: auto` globally for fonts with opsz axis
- Dark mode: reduce body weight by ~20 units (400→380) for perceived consistency
- Accessibility: use `@media (prefers-contrast: more)` to bump weight +100 and increase letter-spacing

## Color Systems

All colors defined in OKLCH for perceptual uniformity. Hex fallbacks in comments for reference.
OKLCH format: `oklch(Lightness Chroma Hue)` — Lightness 0-1, Chroma 0-0.4, Hue 0-360.

**Why OKLCH over hex/HSL:** Equal lightness values produce equal perceived brightness across all hues. This makes generating accessible palettes trivial — you can guarantee contrast ratios mathematically instead of eyeballing.

### System A — Obsidian (default dark theme)
```css
--background:       oklch(0.145 0.005 286);   /* #09090b — near-black */
--surface:          oklch(0.21 0.006 286);     /* #18181b — zinc-900 */
--surface-elevated: oklch(0.274 0.006 286);    /* #27272a — zinc-800 */
--border:           oklch(0.37 0.013 286);     /* #3f3f46 — zinc-700 */
--border-subtle:    oklch(0.274 0.006 286);    /* #27272a — zinc-800 */
--text-primary:     oklch(0.985 0.002 286);    /* #fafafa — zinc-50 */
--text-secondary:   oklch(0.705 0.015 286);    /* #a1a1aa — zinc-400 */
--text-tertiary:    oklch(0.552 0.016 286);    /* #71717a — zinc-500 */
--accent:           oklch(0.637 0.237 260);    /* #3b82f6 — blue-500 */
--accent-hover:     oklch(0.707 0.191 260);    /* #60a5fa — blue-400 */
--accent-muted:     oklch(0.32 0.08 260);      /* #1e3a5f — blue tinted dark */
--destructive:      oklch(0.637 0.237 25);     /* #ef4444 — red-500 */
--success:          oklch(0.723 0.219 149);    /* #22c55e — green-500 */
--warning:          oklch(0.795 0.184 86);     /* #eab308 — yellow-500 */
```

### System B — Snow (light variant)
```css
--background:       oklch(1.0 0 0);            /* #ffffff */
--surface:          oklch(0.985 0.002 286);    /* #fafafa */
--surface-elevated: oklch(0.967 0.003 286);    /* #f4f4f5 */
--border:           oklch(0.919 0.005 286);    /* #e4e4e7 */
--border-subtle:    oklch(0.967 0.003 286);    /* #f4f4f5 */
--text-primary:     oklch(0.145 0.005 286);    /* #09090b */
--text-secondary:   oklch(0.552 0.016 286);    /* #71717a */
--text-tertiary:    oklch(0.705 0.015 286);    /* #a1a1aa */
--accent:           oklch(0.546 0.245 263);    /* #2563eb — blue-600 */
--accent-hover:     oklch(0.488 0.243 264);    /* #1d4ed8 — blue-700 */
--accent-muted:     oklch(0.932 0.048 260);    /* #dbeafe — blue-100 */
--destructive:      oklch(0.577 0.245 27);     /* #dc2626 */
--success:          oklch(0.627 0.194 149);    /* #16a34a */
--warning:          oklch(0.681 0.162 80);     /* #ca8a04 */
```

### System C — Ink (high-contrast editorial)
```css
--background:       oklch(0.13 0 0);           /* #0a0a0a */
--surface:          oklch(0.18 0 0);           /* #141414 */
--surface-elevated: oklch(0.20 0 0);           /* #1a1a1a */
--border:           oklch(0.26 0 0);           /* #262626 */
--text-primary:     oklch(0.95 0 0);           /* #ededed */
--text-secondary:   oklch(0.60 0 0);           /* #888888 */
--accent:           oklch(1.0 0 0);            /* #ffffff — white as accent */
--accent-hover:     oklch(0.93 0 0);           /* #e5e5e5 */
--destructive:      oklch(0.637 0.3 25);       /* #ff4444 */
--success:          oklch(0.72 0.22 155);      /* #00cc66 */
```

### System D — Warm Neutral (for client-facing, approachable)
```css
--background:       oklch(0.98 0.005 80);      /* #faf9f7 */
--surface:          oklch(0.965 0.007 80);     /* #f5f4f0 */
--surface-elevated: oklch(0.948 0.008 80);     /* #eeedea */
--border:           oklch(0.895 0.01 80);      /* #dddcd8 */
--text-primary:     oklch(0.18 0.01 60);       /* #1a1918 */
--text-secondary:   oklch(0.50 0.015 60);      /* #6b6966 */
--accent:           oklch(0.55 0.16 45);       /* #c05621 — warm orange */
--accent-hover:     oklch(0.47 0.14 45);       /* #9a4518 */
--destructive:      oklch(0.52 0.2 25);        /* #c53030 */
--success:          oklch(0.55 0.15 155);      /* #2f855a */
```

### Generating Custom Accent Colors with OKLCH
To create a new accent that matches a system's perceived brightness:
1. Keep the same Lightness as the existing accent
2. Adjust Hue (0-360) for the color you want
3. Adjust Chroma (0-0.3) for saturation
Example: Change blue accent to teal: `oklch(0.637 0.2 185)` — same L as blue-500, hue shifted to teal

### Color Rules
- NEVER use more than ONE accent color per project (plus its hover/muted variants)
- Backgrounds should be TRUE darks (#09-#18 range) or TRUE lights (#fa-#ff range) — no murky mid-grays
- Borders should be barely visible — they define space, not decorate
- Use opacity for layering (e.g., surface = background + white at 4% opacity) rather than separate colors when possible
- Status colors (destructive, success, warning) should only appear contextually, never as decoration

## Spacing & Layout

### Spacing Scale (4px base)
```
0.5: 2px   — tight optical adjustments
1:   4px   — icon padding, inline gaps
1.5: 6px   — compact list items
2:   8px   — small padding, tag gaps
3:   12px  — input padding, card inner gaps
4:   16px  — standard element spacing
5:   20px  — section inner padding
6:   24px  — card padding, group gaps
8:   32px  — section gaps
10:  40px  — major section spacing
12:  48px  — page section dividers
16:  64px  — hero/landing section spacing
20:  80px  — major landing page gaps
24:  96px  — hero top/bottom padding
```

### Layout Patterns
- Max content width: 1280px for dashboards, 1024px for marketing/content
- Sidebar width: 240-280px (collapsible to 64px icon-only)
- Grid: 12-column for dashboards, content + aside for marketing
- Cards: 1px border, 6-8px radius, no box-shadow (or very subtle 0 1px 2px rgba(0,0,0,0.05))
- Modals: 12px radius, overlay at rgba(0,0,0,0.6)
- ASYMMETRIC layouts are preferred over centered-everything for landing pages

## Shadows & Depth
- Prefer border-based separation over shadows
- When shadows are needed: `0 1px 2px rgba(0,0,0,0.05)` for subtle, `0 4px 12px rgba(0,0,0,0.1)` for elevated
- Dark mode: shadows are nearly invisible — use border opacity + surface color changes instead
- Layering order: background → surface → surface-elevated → popover/modal

## Iconography
- Default: Lucide React (consistent, clean, 24px)
- Size: 16px inline, 20px in buttons, 24px standalone
- Stroke width: 1.5px (Lucide default) — never change this
- Color: text-secondary by default, text-primary on hover/active

## Anti-Patterns (NEVER DO THESE)

1. **Purple gradients on white** — the #1 "made by AI" signal
2. **Inter/Roboto/Arial as primary font** — screams generic
3. **Centered hero with stock illustration** — zero personality
4. **Rainbow gradient text** — tacky unless it's a creative/art project
5. **Uniform 16px rounded corners on everything** — vary radii by element purpose
6. **Drop shadows on every card** — prefer borders for structure
7. **Emoji as section headers** — this isn't a Notion doc
8. **"Trusted by 1000+ companies" with no logos** — either show real logos or don't claim it
9. **Hamburger menu on desktop** — only acceptable below 768px
10. **White text on light gray background** — insufficient contrast
11. **Decorative blobs/circles in background** — unless highly intentional and on-brand
12. **More than 3 font weights on one page** — pick 2-3 and commit
13. **Button with both icon AND text AND arrow** — pick two max
14. **Gradients that go from one random color to another** — if using gradients, stay within one hue family
15. **"Click here" or "Submit" as button text** — be specific about the action

## Project-Specific Overrides

When building for these known projects, apply these overrides:

**LeadPulse (Senior Living AI Platform):**
- Color System: A (Obsidian) with accent #3b82f6
- Typography: Pair A (Geist Sans / Plus Jakarta Sans)
- Aesthetic: Linear/Vercel — clean, modern B2B SaaS
- EXPLICITLY NOT healthcare-looking (no blue/green medical vibes)
- Can expand to other verticals — keep it industry-agnostic

**OpenClaw (AI Employee Dashboard):**
- Color System: A (Obsidian) with accent per agent personality
- Typography: Pair A or C
- Aesthetic: Technical, developer-friendly, information-dense
- Reference: StartClaw.com for visual direction
- Future: retro pixel-art agent world layer (separate aesthetic for that feature)

**Met Global Mobility (Dispatch Platform):**
- Color System: A or B depending on portal
  - Ops/Dispatch: Dark (A)
  - Driver PWA: Light (B) for outdoor readability
  - Client Portal: D (Warm Neutral) for premium feel
- Typography: Pair A (Geist Sans)
- Aesthetic: Professional, trustworthy, real-time data emphasis

**@buildwithneej (Content/Personal Brand):**
- Color System: C (Ink) — high contrast editorial
- Typography: Pair B (Instrument Serif + Satoshi)
- Aesthetic: Bold, editorial, developer-influencer energy
- This is the ONE context where more expressive design is encouraged

**Content Command (SaaS Analytics Dashboard):**
- Color System: C (Ink) with warm orange accent (#ff6b2b)
- Typography: Pair B (Instrument Serif display + Satoshi body + JetBrains Mono data)
- Accent: #ff6b2b (orange) — single accent, used for CTAs, active states, primary metrics
- Card treatment: `rounded-lg border border-border bg-card p-5` — no shadows, border-only
- Section headers: `text-xs font-medium uppercase tracking-widest text-muted-foreground/50`
- Page headers: `font-display text-2xl tracking-tight` + `text-[13px] text-muted-foreground/60 mt-0.5` subtitle
- Demo mode: Toggle between normal dashboard and TikTok-recording mode (orb hero, aggressive animations)
- Chart tokens: `--chart-1` through `--chart-5` in CSS vars, themed tooltips

## Reusable Design Conventions

These conventions emerged from building Content Command and should be applied to ALL dashboard projects:

### Page Header Pattern
Every dashboard page should have a consistent header:
```tsx
<div>
  <h1 className="font-display text-2xl tracking-tight text-foreground">Page Title</h1>
  <p className="text-[13px] text-muted-foreground/60 mt-0.5">Brief description of this page</p>
</div>
```

### Accent Hierarchy
Use accent color to establish visual hierarchy in data-heavy pages:
- **Primary metric**: `border-accent/30` border + `text-accent` value
- **#1 ranked item**: Accent border, accent-tinted rank badge (`bg-accent/15 text-accent`)
- **Secondary items**: Default border, muted rank badges (`bg-secondary text-muted-foreground`)
- **Featured pricing tier**: `border-2 border-accent` + `accent-glow` utility

### Confidence/Status Badges (Translucent Pattern)
Never use solid-color badges in dashboards — use translucent backgrounds:
```
high:    bg-success/10 text-success border-0
medium:  bg-chart-4/10 text-chart-4 border-0   (amber/warning)
low:     bg-muted-foreground/10 text-muted-foreground border-0
```

### Demo Mode Pattern
Any SaaS product built for @buildwithneej should support a "demo mode" toggle:
- Simple `useState` toggle, not URL params (persists across navigation)
- Demo mode restructures the page layout for TikTok recording
- Key feature/hero element becomes center stage (larger, more prominent)
- Dashboard data panels stagger-reveal below with orchestrated cascade
- Normal mode is what paying users see — clean, functional, fast
- Toggle button: subtle, top-right, uses `Sparkles` icon for demo, `LayoutDashboard` for normal
