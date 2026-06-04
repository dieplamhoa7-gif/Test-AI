---
name: neej-frontend-craft
description: Comprehensive frontend design and implementation skill for building production-grade, visually distinctive UIs. Combines design intelligence, personal aesthetic preferences, animation patterns, and self-evaluation into a single unified workflow. Use this skill whenever the task involves building, designing, reviewing, or improving any frontend — landing pages, dashboards, SaaS interfaces, marketing pages, component libraries, or full application UIs. Triggers on any mention of UI, frontend, landing page, dashboard, design, layout, styling, animation, component design, or visual polish. Also triggers when reviewing or critiquing existing frontend code for quality. This skill should be used INSTEAD of frontend-design, ui-ux-pro-max, or ui-animation when they are available — it supersedes and unifies all three.
---

# Neej Frontend Craft

A unified frontend design + implementation skill that produces distinctive, production-grade interfaces. Combines design intelligence, a personal design system, animation best practices, and a self-evaluation loop into one workflow.

## Core Philosophy

Great frontend is not about stacking libraries. It's about:
1. **Context-aware design decisions** — every project has a different audience, tone, and purpose
2. **Encoded taste** — specific, concrete preferences rather than vague "be bold" instructions
3. **Self-evaluation before delivery** — catch AI slop patterns before the human sees them
4. **Restraint over excess** — the best designs feel intentional, not decorated

## Workflow (Follow Every Time)

### Step 1: Read the Design Brief + Gather References
Before writing ANY frontend code, read `references/design-brief.md` in this skill's directory. It contains the personal design system, preferred aesthetic, font pairings, color systems, and anti-patterns. This is the source of truth for all visual decisions.

**Reference URL Analysis (optional but recommended):**
Ask the human: *"Any reference sites or designs you want this to feel like?"*
If they provide a URL:
1. Use Defuddle (or WebFetch if Defuddle unavailable) to scrape the site
2. Extract and note: color palette, font families, layout structure, spacing patterns, animation style
3. Merge these observations with the design brief — the brief is the foundation, the reference is directional influence
4. If the reference conflicts with the design brief (e.g., they show a pastel site but brief says dark-first), ask which to prioritize

If they provide a Figma file URL and Figma MCP is connected:
1. Read the Figma file for design tokens, component structures, and layout data
2. Use Figma tokens as the primary source for Step 3 (design token generation)
3. Note any gaps where Figma doesn't define tokens — fill from design brief

**Growing the Inspiration Library:**
When the human says "add [url] to inspiration" or "save this as reference":
1. Use Defuddle to analyze the site
2. Append to `references/inspiration-sites.md` with: URL, what to study, what to steal, tier classification
3. Note the date added so stale references can be cleaned up

### Step 2: Classify the Project Context
Determine which category this frontend falls into, as it changes everything:

| Context | Aesthetic Direction | Animation Level | Component Density |
|---------|-------------------|-----------------|-------------------|
| **SaaS Dashboard** | Clean, data-first, functional | Minimal — transitions only | High — tables, charts, sidebars |
| **Landing Page** | Bold, conversion-focused, atmospheric | Medium — scroll reveals, hero animations | Low — sections, CTAs, social proof |
| **Marketing/Brand** | Expressive, editorial, immersive | High — scroll-driven, parallax, micro-interactions | Low — storytelling sections |
| **Client Portal** | Professional, trustworthy, clear | Minimal — state transitions | Medium — forms, status, navigation |
| **Developer Tool** | Technical, information-dense, precise | Minimal — feedback only | Very High — code, configs, logs |

### Step 3: Generate Design Tokens
For every new project or page, generate a design token block before writing UI code.

If a **Figma MCP** is connected and a Figma file exists for this project, read tokens from Figma first and use them as the source of truth. Otherwise, generate from the design brief.

```
PROJECT: [name]
CONTEXT: [category from Step 2]
FIGMA_SOURCE: [Figma file URL if available, otherwise "none — generating from design brief"]
PALETTE (OKLCH — hex fallback in comments):
  background: oklch([L] [C] [H])   /* #hex */
  surface: oklch([L] [C] [H])      /* #hex */
  text-primary: oklch([L] [C] [H]) /* #hex */
  text-secondary: oklch([L] [C] [H]) /* #hex */
  accent: oklch([L] [C] [H])       /* #hex */
  accent-hover: oklch([L] [C] [H]) /* #hex */
  border: oklch([L] [C] [H])       /* #hex */
  destructive: oklch([L] [C] [H])  /* #hex */
  success: oklch([L] [C] [H])      /* #hex */
TYPOGRAPHY:
  display: [font family] (variable) — [where to load from]
  heading: [font family]
  body: [font family] — dark mode weight adjustment: [e.g., 400→380]
  mono: [font family]
  scale: [base size, e.g., 16px with 1.25 ratio]
  optical-sizing: auto
SPACING: [system, e.g., 4px base, multiples of 4]
RADII: [e.g., 6px default, 8px cards, 12px modals]
SHADOWS: [style description]
ANIMATION: [level from Step 2] — CSS-first, Motion for complex
DATA_VIZ: [chart library if needed — Recharts/Nivo/none]
ACCESSIBILITY: WCAG 2.2 AA, prefers-reduced-motion, prefers-contrast
ANTI-PATTERNS: [list 3-5 specific things to avoid for THIS project]
```

### Step 4: Implement
Build the frontend using these constraints:

**Stack (default unless otherwise specified):**
- Next.js App Router + TypeScript
- Tailwind CSS v4 + CSS variables for theming (OKLCH color space)
- shadcn/ui as component primitives (Radix or Base UI underneath)
- Motion (formerly Framer Motion) for complex animations
- CSS View Transitions API for page transitions
- CSS Scroll-Driven Animations for simple scroll effects (Motion fallback for complex)
- Lucide React for icons
- Google Fonts or Fontsource for typography (variable fonts preferred)
- TanStack Table for data tables
- Recharts (standard dashboards) or Nivo (presentation-quality charts) for data viz

**Project Scaffolding:**
Use `npx shadcn create` (Visual Builder at ui.shadcn.com/create) to generate the initial project with design tokens baked in. Choose Radix UI or Base UI as primitive layer. Customize theme colors, fonts, icons, and border-radius in the builder, then further customize in `globals.css` with your project's design tokens from Step 3.

**Implementation Rules:**
1. Every color must come from CSS variables — never hardcode hex values in components
2. Typography scale must be defined once in globals.css and referenced via Tailwind classes
3. All interactive elements need hover, focus, and active states
4. Dark mode support via CSS variables + `class` strategy (not `media`)
5. Responsive: mobile-first, breakpoints at sm(640), md(768), lg(1024), xl(1280)
6. Loading states for all async operations — skeleton screens, not spinners
7. All text must have sufficient contrast (WCAG AA minimum: 4.5:1 for body, 3:1 for large text)

**Animation Rules (read `references/animation-patterns.md` for full guide):**
- Page load: stagger reveal with `motion.div` variants, 50-80ms stagger delay
- Navigation: CSS View Transitions API for route changes (lighter than AnimatePresence). Fallback to `AnimatePresence` for complex shared-element transitions
- Micro-interactions: `whileHover`, `whileTap` on interactive elements — scale(1.02) max for buttons
- Data loading: skeleton shimmer using CSS animation (not Motion — too heavy for this)
- Scroll-driven: CSS `animation-timeline: view()` for simple reveals. Motion's `useScroll` + `useTransform` for complex parallax/progress-linked effects. Use `@supports (animation-timeline: view())` for progressive enhancement
- NEVER animate layout properties (width, height, top, left) — use transform only
- NEVER add animation that doesn't serve UX purpose (guiding attention, confirming action, showing state)

### Step 5: Self-Evaluate Before Delivery
Before presenting ANY frontend output, run through this checklist mentally. If any item fails, fix it before showing the human.

**AI Slop Detection (CRITICAL — read `references/evaluation-criteria.md`):**
- [ ] No purple gradients on white backgrounds
- [ ] No Inter, Roboto, Arial, or system-ui as primary fonts
- [ ] No centered-everything layouts (asymmetry is almost always better)
- [ ] No generic card grids with uniform rounded corners and shadows
- [ ] No stock-photo-energy hero sections
- [ ] No "Get Started" / "Learn More" as the only CTA text (be specific)
- [ ] No gratuitous glassmorphism or blur effects without purpose
- [ ] No rainbow gradient text
- [ ] No identical spacing between all sections

**Design Quality:**
- [ ] Does the page have visual hierarchy? Can you tell what's most important in 2 seconds?
- [ ] Is there a dominant color that anchors the design, with accents used sparingly?
- [ ] Does the typography create rhythm — clear distinction between display, heading, body, caption?
- [ ] Is negative space used intentionally, not just as leftover?
- [ ] Does the design feel like ONE cohesive decision, not a collection of components?

**Craft:**
- [ ] Are hover states implemented on every interactive element?
- [ ] Do animations have proper easing (never `linear` for UI, use `ease-out` or spring)?
- [ ] Are images/icons properly sized and not stretched?
- [ ] Is the responsive behavior graceful, not just "stack everything vertically"?
- [ ] Do form elements have proper labels, placeholders, error states, and focus rings?

**Originality:**
- [ ] Would someone screenshot this and share it as inspiration?
- [ ] Is there at least ONE unexpected design choice (layout, typography, color, interaction)?
- [ ] Does this look different from the last 3 frontends generated?

## Reference Files

Read these as needed — they provide deep guidance on specific topics:

| File | When to Read |
|------|-------------|
| `references/design-brief.md` | **ALWAYS** — before any frontend work |
| `references/animation-patterns.md` | When implementing any animation or motion |
| `references/evaluation-criteria.md` | Before delivering any frontend output |
| `references/component-patterns.md` | When building specific UI patterns (navbars, heroes, pricing, etc.) |
| `references/inspiration-sites.md` | When stuck on direction or need visual references |

## Integration Notes

**With Figma MCP (if connected):** The official Figma MCP server (`https://mcp.figma.com/mcp`) bridges design and code. Use it to:
- **Read**: Pull design tokens, component structures, layout data, and variables from Figma files before generating design tokens in Step 3. If a Figma file exists for the project, use its tokens as the source of truth instead of generating from scratch.
- **Write**: Push generated design tokens back to Figma canvas for designer handoff. Create/modify frames, components, and variables.
- **Sync**: Keep code-side CSS variables aligned with Figma variables. When updating tokens in code, update Figma too.
- **Rate limits**: Dev/Full seats on Pro/Org/Enterprise plans have per-minute limits. Starter/View seats limited to 6 calls/month — avoid using on free plans.

**With shadcn/ui:** Scaffold projects with `npx shadcn create` (Visual Builder). Choose Radix or Base UI as primitive layer. Always customize beyond defaults — override the theme in `globals.css` with your project's design tokens. Default shadcn looks like every other shadcn app.

**With Motion:** Import only what you need. Use `motion.div` for simple animations, `AnimatePresence` for mount/unmount, `useScroll`/`useTransform` for complex scroll-driven effects. Lazy-load Motion components that aren't above the fold. Prefer CSS View Transitions and CSS Scroll-Driven Animations for simpler cases.

**With 21st.dev Magic MCP (if installed):** Use ONLY for inspiration — fetch component examples to study patterns, then implement your own version using the design tokens from this skill. Never copy 21st.dev output directly without adapting to the project's design system.

**With Tailwind CSS v4:** Use the new CSS-first config model. Define design tokens as CSS custom properties in `@theme` block. Use OKLCH color space for perceptually uniform color manipulation. No `tailwind.config.js` needed — everything lives in CSS.

**With TanStack Table:** Use for all data table implementations. Headless UI gives full markup control — style with your project's design tokens. Pair with shadcn/ui's Table component for the visual layer. Supports sorting, filtering, pagination, row selection, and column resizing out of the box.

**With Recharts / Nivo:** Use Recharts for standard SaaS dashboards (simpler API, faster to ship). Use Nivo when you need presentation-quality charts or many chart types on the same page. Always theme charts with your project's CSS variables — never use default chart colors.

## Quick Commands

When the human says:
- **"make it look good"** → Run full workflow Steps 1-5
- **"review this UI"** → Run Step 5 evaluation only, give specific feedback
- **"design system for [project]"** → Run Steps 1-3, output token block
- **"animate this"** → Read animation-patterns.md, apply contextually appropriate motion
- **"this looks generic"** → Re-run Step 5, identify which AI slop patterns are present, fix them
- **"make it look like [url]"** → Scrape the URL with Defuddle, extract design patterns, merge with design brief, then build
- **"add [url] to inspiration"** → Analyze site and append to inspiration-sites.md with study notes
- **"pull from Figma"** → Read Figma file via MCP, extract tokens, use as source of truth for Step 3
