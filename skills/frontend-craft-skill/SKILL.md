---
name: frontend-craft
argument-hint: "[design|build|test|team|setup]"
description: Unified frontend development for production-grade Next.js applications with shadcn/ui + Tailwind CSS. Use when building web apps, creating UI components, implementing design systems, styling with Tailwind, setting up Next.js projects, running visual QA tests, or coordinating frontend implementation teams.
---

# Frontend Craft

Definitive guide for building distinctive, production-grade Next.js applications with shadcn/ui and Tailwind CSS. Covers the full lifecycle: design philosophy → design system → component architecture → implementation → visual QA → deployment.

## Subcommand Router

Arguments: $ARGUMENTS

**Route based on first argument:**
- `design` → Read `references/design-philosophy.md` and `references/design-system-tokens.md`, then guide design system creation
- `build` → Read `references/shadcn-workflow.md`, `references/nextjs-architecture.md`, `references/tailwind-patterns.md`, then implement
- `test` → Read `references/testing-visual-qa.md`, then run visual QA workflow
- `team` → Read `workflows/team-implementation.md`, then spawn 3-teammate team
- `setup` → Read `workflows/new-project-setup.md`, then set up new project
- *(no argument)* → Assess project state and determine which phase to start with

**On trigger:** Read this SKILL.md. Load reference files ONLY when their topic is needed.

---

## 1. Design Philosophy

Every interface needs a **point of view**. Before writing code, define the aesthetic direction.

### Design Brief (fill before coding)

```
Purpose:      [What problem does this solve?]
Audience:     [Who uses this? Technical, consumer, enterprise?]
Tone:         [Pick ONE: minimal | luxury | brutalist | editorial | playful | organic | retro-futuristic | ...]
Differentiator: [What makes this memorable?]
Constraints:  [Framework, a11y level, perf budget]
```

**Deep reference:** `references/design-philosophy.md` — anti-generic principles, 12 tone directions, 10 font pairings with code, NEVER-use list, color theory.

---

## 2. Design System Architecture

The design system lives in **CSS variables** (globals.css) + **components.json** (shadcn config).

### Token Hierarchy

```
Primitive     →  Semantic        →  Component
--blue-500       --primary           --button-bg
--gray-100       --muted             --card-bg
--space-4        --section-padding   --dialog-padding
```

**Starter file:** `assets/globals-template.css` — copy to `app/globals.css` and customize.

**Deep reference:** `references/design-system-tokens.md` — complete CSS variable list, color generation from brand color, typography scale, spacing system.

---

## 3. Component Workflow (MCP-First)

Use shadcn MCP tools to discover, inspect, and install components. This avoids blind CLI installs and lets you preview before committing.

### 7-Step Workflow

1. **Discover registries:** `mcp__shadcn__get_project_registries`
2. **Browse components:** `mcp__shadcn__list_items_in_registries`
3. **Search by need:** `mcp__shadcn__search_items_in_registries` (e.g., "date picker")
4. **Inspect details:** `mcp__shadcn__view_items_in_registries`
5. **View examples:** `mcp__shadcn__get_item_examples_from_registries`
6. **Get install cmd:** `mcp__shadcn__get_add_command_for_items`
7. **Install:** Run the command via Bash

### File Structure

```
components/
  ui/           ← shadcn primitives (DO NOT modify directly)
  [custom]/     ← composed wrappers (extend here)
features/
  [domain]/
    components/ ← feature-specific UI
    hooks/
    actions/
```

**Rules:** Never edit `components/ui/*` directly — create wrappers. Use `cn()` for class merging. Extend variants with `cva()`.

**Deep reference:** `references/shadcn-workflow.md` — component categories, composition patterns (form+zod, data table, responsive dialog), block patterns.

---

## 4. Next.js Architecture

**Default to Server Components.** Only use `'use client'` when you need hooks, event handlers, or browser APIs. Composition pattern: Server Component fetches data, passes to Client Component for interactivity.

**Deep reference:** `references/nextjs-architecture.md` — project structure, file conventions, server/client decision tree, data fetching, server actions, route organization, metadata/SEO, middleware.

---

## 5. Styling with Tailwind

- **Utility-first.** Apply classes directly — no CSS files for component styles.
- **Mobile-first responsive.** Base styles → `sm:` → `md:` → `lg:` → `xl:`
- **Dark mode via CSS variables.** shadcn components handle dark mode automatically.
- **No inline styles.** Use Tailwind utilities or `cn()` for everything.

**Deep reference:** `references/tailwind-patterns.md` — utility quick-ref, responsive patterns, dark mode strategies, cn() usage, Tailwind v4 @theme, performance rules.

---

## 6. Animation & Motion

| Approach | Use When |
|----------|----------|
| **CSS/Tailwind** | Hover, focus, state transitions |
| **Framer Motion** | Page transitions, layout animations, gestures |
| **anime.js v4** | Complex orchestrated sequences, SVG, scroll-triggered |

**Always respect** `prefers-reduced-motion`. Use `motion-safe:` / `motion-reduce:` Tailwind variants.

**Deep reference:** `references/animation-motion.md` — Framer Motion patterns, anime.js v4 quick-ref (CRITICAL: v4 syntax only), performance rules.

---

## 7. Accessibility

shadcn/ui components (built on Radix UI) provide focus trapping, keyboard navigation, ARIA attributes, and roving tabindex automatically.

**Your responsibility:** Semantic HTML, proper headings hierarchy, alt text, sufficient contrast (4.5:1), visible focus indicators, `prefers-reduced-motion` respect.

**Deep reference:** `references/accessibility-checklist.md` — WCAG AA top 10, what Radix handles, keyboard patterns, 15-item shipping checklist.

---

## 8. Visual QA Testing

Test your UI using browser automation MCPs without leaving the conversation.

**Quick Workflow:** Start dev server → Navigate → Screenshot → Resize for responsive (375px, 768px, 1280px, 1920px) → Check console → Performance trace.

**Deep reference:** `references/testing-visual-qa.md` — full workflow with MCP tool names, device emulation, performance vitals (LCP/FID/CLS), interactive testing.

---

## 9. Agent Team Implementation

For large features (3+ pages, complex interactions), spawn a 3-teammate team:

| Role | Owns |
|------|------|
| **design-system-lead** | `globals.css`, `layout.tsx`, `components/ui/*`, `tailwind.config.*` |
| **ui-lead** | `app/(routes)/**`, `components/*`, `features/**/components/**`, `hooks/**` |
| **quality-lead** | `__tests__/**`, `*.test.*`, screenshots |
| **Lead (you)** | `components.json`, `package.json`, `tsconfig.json`, `types/**` |

### TDD-for-UI Pipeline (per page)

1. **quality-lead** defines visual acceptance criteria
2. **design-system-lead** installs shadcn components, configures tokens
3. **ui-lead** implements pages (blocked by step 2)
4. **quality-lead** runs visual QA at 4 breakpoints (blocked by step 3)
5. Fix owner addresses issues → quality-lead re-verifies

**Deep reference:** `workflows/team-implementation.md` — full spawn instructions, file ownership, task templates.
**Spawn prompts:** `workflows/spawn-prompts/` — self-contained prompts for each teammate.

---

## 10. New Project Checklist

Starting a new Next.js + shadcn/ui project? Follow `workflows/new-project-setup.md`:

1. `npx create-next-app@latest` (TypeScript, Tailwind, App Router)
2. `npx shadcn@latest init` (New York style, CSS variables)
3. Copy `assets/globals-template.css` → customize brand colors
4. Install core components (button, card, input, form, dialog, sonner)
5. Set up ThemeProvider with next-themes
6. Configure root layout (fonts, providers, metadata)
7. Create directory structure (components/, features/, hooks/, types/)
8. Verify: `npm run dev` → check dark mode, components, console

---

## Common Issues

- **shadcn install fails**: Run `mcp__shadcn__get_project_registries` first to verify components.json exists
- **Dark mode not working**: Ensure `ThemeProvider` wraps app in root layout, and globals.css has `.dark` class variables
- **"use client" errors**: Only add to components using hooks/events — default to Server Components
- **Tailwind classes not applying**: Check `content` paths in tailwind.config (v3) or CSS imports (v4)
- **Hydration mismatch**: Wrap theme-dependent UI in `mounted` check or use `suppressHydrationWarning` on `<html>`

---

## MCP Quick Reference

| MCP Server | Key Tools | Use For |
|------------|-----------|---------|
| **shadcn** | `get_project_registries`, `list_items_in_registries`, `search_items_in_registries`, `view_items_in_registries`, `get_add_command_for_items`, `get_audit_checklist` | Component discovery, installation, audit |
| **Chrome DevTools** | `navigate_page`, `take_screenshot`, `resize_page`, `emulate`, `evaluate_script`, `list_console_messages`, `performance_*` | Visual QA, responsive testing, performance |
| **Claude-in-Chrome** | `navigate`, `read_page`, `form_input`, `computer`, `get_page_text` | Interactive testing, form filling, page reading |
| **Ref** | `ref_search_documentation`, `ref_read_url` | Look up Next.js, Tailwind, Radix docs |

---

## Reference Navigation

| Need to... | Read |
|------------|------|
| Define aesthetic direction, pick fonts | `references/design-philosophy.md` |
| Configure CSS variables, tokens, colors | `references/design-system-tokens.md` |
| Structure Next.js app, routing, data fetching | `references/nextjs-architecture.md` |
| Find and install shadcn components | `references/shadcn-workflow.md` |
| Tailwind utility classes, responsive, dark mode | `references/tailwind-patterns.md` |
| Add animations and motion | `references/animation-motion.md` |
| Check accessibility requirements | `references/accessibility-checklist.md` |
| Run visual QA tests | `references/testing-visual-qa.md` |
| Set up a new project | `workflows/new-project-setup.md` |
| Spawn implementation team | `workflows/team-implementation.md` |
