---
name: openclaw-ui-ux-frontend-master
description: "Lightweight router skill for UI/UX/design/frontend tasks in OpenClaw. Use for pages, components, landing pages, dashboards, mobile/web interfaces, charts, visual polish, branding, banners, slides, accessibility, design systems, Tailwind/shadcn/frontend styling, and avoiding generic AI-looking design. Do not load the full consolidated reference unless needed; route to the smallest relevant source skill first."
---

# OpenClaw UI/UX Frontend Master — Lightweight Router

## Why this skill exists

This is a **context-safe router**, not a giant encyclopedia. OpenClaw can become slow or confused when huge skill files are loaded into context. For UI/UX/frontend work, start here, then read only the smallest relevant source file/reference.

## Default behavior

1. **Do not read `references/FULL_CONSOLIDATED.md` by default.** It is an archive for preservation/search, not normal working context.
2. Pick the smallest relevant skill/source below.
3. Read only the necessary `SKILL.md` or reference files for the current task.
4. If details conflict, prefer concrete implementation guidance over generic design advice.
5. For large redesign/build tasks, spawn a sub-agent or split into phases: audit → design plan → implementation → visual QA.

## Routing map

- General UI/UX/frontend polish: `skills/ui-ux-pro-max/SKILL.md`
- Tailwind, shadcn/ui, styling implementation: `skills/ui-styling/SKILL.md`
- Design tokens/component systems: `skills/design-system/SKILL.md`
- Landing/front-end visual sections: `skills/21st-frontend-design/SKILL.md`
- Avoiding generic AI-looking design: `skills/avoid-ai-design/SKILL.md`
- Brand identity, logo rules, voice, palettes: `skills/brand/SKILL.md`
- Logo/icon/CIP/social visual design: `skills/design/SKILL.md`
- Banners/ads/social covers: `skills/banner-design/SKILL.md`
- Slides/decks/presentation pages: `skills/slides/SKILL.md`
- Tasteful redesign quick rules: `skills/taste-redesign-skill/SKILL.md`
- Vietnamese/frontend encoding safety: `skills/utf8-frontend-guard/SKILL.md`

## Context discipline for OpenClaw

Use this when OpenClaw feels slow, confused, or over-contexted:

- Prefer **router/index skills** over giant all-in-one skill files.
- Keep `SKILL.md` short; put large knowledge in `references/*.md`.
- Load references only on demand.
- Avoid automatic rules that force huge files into every UI task.
- Use sub-agents for deep audits or large refactors so the main chat stays clean.
- Summarize long findings into a short working brief before coding.
- Commit completed changes, then reset/start a fresh session for the next major phase.

## Preserved archive

The previous full merged file is preserved at:

`skills/openclaw-ui-ux-frontend-master/references/FULL_CONSOLIDATED.md`

Source/deduplication index:

`skills/openclaw-ui-ux-frontend-master/SOURCE_INDEX.md`

Only open the full archive for exhaustive search, migration, or when Hòa Đại ka explicitly asks for “toàn bộ chi tiết trong một file”.
