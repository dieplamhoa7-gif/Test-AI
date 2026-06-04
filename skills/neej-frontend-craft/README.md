# neej-frontend-craft

A Claude Code skill for building production-grade, visually distinctive frontends. Combines design intelligence, a personal aesthetic system, animation patterns, and self-evaluation into a single unified workflow.

Use it whenever Claude is designing, building, reviewing, or improving any frontend — landing pages, dashboards, SaaS interfaces, marketing pages, or component libraries. It supersedes the generic `frontend-design`, `ui-ux-pro-max`, and `ui-animation` skills.

## What this skill encodes

- **Design brief** — 4 color systems in OKLCH, 4 variable-font pairings, spacing/radii/shadow rules, and a long anti-pattern list
- **Component patterns** — concrete structures for navbars, heroes, cards, forms, tables (TanStack), modals, toasts, charts (Recharts/Nivo), sidebars, kanban boards, and more
- **Animation patterns** — CSS-first strategy with Motion for complex cases. Includes stagger reveals, scroll-driven animations, View Transitions, counter hooks, and orchestrated demo cascades
- **Evaluation criteria** — 4 scored dimensions (Design Quality, Originality, Craft, Functionality) + a WCAG 2.2 AA gate + AI-slop detection
- **Inspiration library** — curated Tier 1/2/3 references (Linear, Vercel, Attio, Raycast, Stripe, Arc, etc.)

## Default stack

- Next.js App Router + TypeScript
- Tailwind CSS v4 (CSS-first config, OKLCH)
- shadcn/ui primitives (Radix or Base UI)
- Motion (formerly Framer Motion)
- Lucide React icons
- TanStack Table for tables
- Recharts or Nivo for charts
- Variable fonts via `@fontsource-variable` or Fontshare

## Install

### Per-user (all projects)

```bash
mkdir -p ~/.claude/skills
git clone https://github.com/nchemb/neej-frontend-craft.git ~/.claude/skills/neej-frontend-craft
```

### Per-project

```bash
mkdir -p .claude/skills
git clone https://github.com/nchemb/neej-frontend-craft.git .claude/skills/neej-frontend-craft
```

Claude Code picks up the skill automatically from either location. Trigger it by mentioning frontend, UI, design, animation, or by asking Claude to review/build a UI — or just type `/neej-frontend-craft` inside Claude Code.

## File layout

```
SKILL.md                                 # Orchestration + 5-step workflow
references/design-brief.md               # Aesthetic source of truth — READ FIRST
references/component-patterns.md         # Navbars, heroes, cards, tables, charts…
references/animation-patterns.md         # CSS-first + Motion patterns
references/evaluation-criteria.md        # Scoring rubric + WCAG gate
references/inspiration-sites.md          # Tier 1/2/3 references
```

Claude reads `SKILL.md` first, then pulls `references/*.md` on demand via a lookup table.

## Workflow Claude follows

1. Read the design brief + gather references (URL / Figma)
2. Classify the project (SaaS dashboard / landing / marketing / portal / dev tool)
3. Generate a design token block (OKLCH palette + typography + spacing + animation level)
4. Implement using the stack above, following the animation and component patterns
5. Self-evaluate against the scoring rubric — iterate if any dimension scores below 3

## Project-specific overrides

`references/design-brief.md` includes concrete overrides for several of my projects (LeadPulse, OpenClaw, Met Global, Content Command, @buildwithneej). These are kept as **examples of how to encode aesthetic decisions for specific products** — copy the pattern for your own projects, or delete them if you'd rather start blank.

## Customizing for yourself

- Swap out the project-specific overrides in `references/design-brief.md` for your own brands
- Add reference URLs under "Inspiration Library" as you collect them ("add [url] to inspiration")
- Adjust the color systems (A–D) to match your preferred palettes
- Rename the skill if you want it to supersede your own set of skills — just update the `name:` and `description:` in the frontmatter of `SKILL.md`

## License

MIT — see [LICENSE](LICENSE)
