# UI / Frontend Skills Index

Added from GitHub on 2026-06-04 for Hòa Đại ka.

## Core UI / frontend production

- `frontend-craft-skill` — Next.js + shadcn/ui + Tailwind frontend craft workflow, design tokens, accessibility, motion, visual QA.
- `frontend-design-engineer` — art-director + senior frontend engineer style skill for full website/pages; Next.js, Tailwind, GSAP, shadcn/ui.
- `ui-arsenal` — premium React/Next.js/Tailwind component-library guidance, patterns, motion, states, quality gate.
- `baseline-ui` — basic UI foundations and non-generic interface rules.
- `interface-design` — interface design principles and UI execution discipline.
- `neej-frontend-craft` — distinctive frontend workflow with design brief, component patterns, animation, self-evaluation.

## Anti-generic / visual polish

- `avoid-ai-design` — audit/rewrite AI-looking frontend; removes generic purple-gradient/default-shadcn feel.
- `emil-design-eng` — high-craft design engineering style inspired by Emil Kowalski.
- `21st-frontend-design` — 21st.dev / aceternity / magicui style for modern SaaS landing/components.
- `design-awwwards` — expressive, portfolio-grade visual direction.

## Accessibility / performance

- `fixing-accessibility` — accessibility review/fix skill.
- `fixing-motion-performance` — motion/performance fixes.

## Brand/style reference skills

- `design-linear` — clean Linear-style SaaS/product UI.
- `design-stripe` — polished Stripe-style commercial/finance UI.
- `design-apple` — minimal premium Apple-style UI.
- `design-robinhood` — finance/trading app style reference.
- `design-vercel` — modern developer/SaaS minimal UI.
- `design-anthropic` — warm restrained Anthropic-style UI.
- `design-figma` — design-tool/productivity style reference.

## Recommended use for LH Investment / stock dashboard

Use together:

1. `lh-investment-firebase-final-deploy` — protect/deploy the approved frontend; do not overwrite final static HTML blindly.
2. `frontend-craft-skill` or `ui-arsenal` — structure, components, responsive behavior.
3. `avoid-ai-design` — remove generic AI-looking UI.
4. `design-robinhood` + `design-linear` + `design-stripe` — finance dashboard visual direction.
5. `fixing-accessibility` + `fixing-motion-performance` — final QA.

Rule: for existing static Firebase frontend, prefer surgical HTML/CSS/JS edits in `stock-news-backend/firebase_public/` unless the user explicitly asks to rebuild the app stack.
