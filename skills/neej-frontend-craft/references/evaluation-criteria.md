# Frontend Evaluation Criteria

Inspired by Anthropic's generator/evaluator harness pattern. These criteria decompose the subjective question "is this design good?" into concrete, gradable dimensions.

## How to Use

Before delivering ANY frontend output, evaluate against all four criteria. Each has a 1-5 scale. The minimum acceptable score is 3 on every criterion. If any criterion scores below 3, iterate before showing the human.

## Criterion 1: Design Quality (weight: 30%)

Does the design feel like a coherent whole rather than a collection of components?

| Score | Description |
|-------|-------------|
| 1 | Random mishmash — no consistent color, spacing, or typography decisions |
| 2 | Somewhat coherent but clearly default/template — looks like every other shadcn app |
| 3 | Intentional decisions visible — consistent palette, typography hierarchy present, spacing system evident |
| 4 | Strong cohesion — design has a clear identity, every element feels like it belongs |
| 5 | Exceptional — could pass as a professionally designed interface, has character and confidence |

**Check for:**
- Is there ONE dominant background color anchoring everything?
- Do surfaces layer cleanly (background → surface → elevated)?
- Is the typography hierarchy clear (display > heading > body > caption)?
- Are borders, radii, and shadows consistent across similar elements?
- Does the page have a clear visual entry point (what do you see first)?

## Criterion 2: Originality (weight: 25%)

Does this avoid looking like generic AI-generated output?

| Score | Description |
|-------|-------------|
| 1 | Pure AI slop — purple gradients, Inter font, centered cards, could be any template |
| 2 | Mostly generic with one or two custom touches |
| 3 | Recognizably custom — clear font choice, custom colors, some layout personality |
| 4 | Distinctive — someone would notice this looks different from typical AI output |
| 5 | Genuinely creative — has at least one "wow" moment (typography, layout, interaction, color) |

**AI Slop Patterns (auto-fail if 3+ present):**
- Purple/violet gradient backgrounds
- Inter, Roboto, or Arial as primary font
- Perfect center-aligned everything
- Identical rounded rectangle cards in a grid
- Generic hero with "Transform your [noun]" headline
- Blue-to-purple gradient CTAs
- Floating abstract shape decorations
- "Trusted by 1000+ companies" without real logos
- Default shadcn gray theme with zero customization
- Stock-looking placeholder images

## Criterion 3: Craft (weight: 25%)

Is the technical implementation polished and production-ready?

| Score | Description |
|-------|-------------|
| 1 | Broken — layout issues, missing responsive behavior, no hover states |
| 2 | Functional but rough — basic layout works, but details are missing |
| 3 | Solid — responsive works, hover states present, forms have basic validation |
| 4 | Polished — smooth transitions, proper loading states, accessible focus rings, consistent spacing |
| 5 | Professional — every edge case handled, motion is fluid, feels like a shipped product |

**Check for:**
- Do ALL interactive elements have hover, focus, active, and disabled states?
- Are animations using proper easing (not `linear`)?
- Does responsive behavior work at mobile (375px), tablet (768px), and desktop (1280px)?
- Are images properly sized (not stretched, have alt text)?
- Do forms have labels, placeholders, error messages, and focus rings?
- Are loading states implemented (skeleton, not spinner)?
- Is there proper contrast ratio (use WCAG AA as minimum)?
- Are there no z-index stacking issues?
- Do modals/drawers trap focus properly?
- Is `prefers-reduced-motion` respected for all animations?
- Is `prefers-contrast: more` handled (bump font weight, increase border contrast)?

## Criterion 4: Functionality (weight: 20%)

Does the frontend serve its actual purpose?

| Score | Description |
|-------|-------------|
| 1 | Non-functional — can't complete the primary user task |
| 2 | Partially functional — main flow works but secondary actions broken |
| 3 | Functional — primary user tasks completable, navigation clear |
| 4 | Well-considered — user flows feel natural, edge cases handled, clear feedback |
| 5 | Exceptional UX — anticipates user needs, delightful micro-interactions, zero confusion |

**Check for:**
- Can the user complete the PRIMARY task on this page?
- Is the navigation clear — does the user know where they are and where they can go?
- Are CTAs specific (not "Learn More" but "Start Free Trial" or "View Dashboard")?
- Is the information hierarchy correct — most important info most prominent?
- Are error states handled gracefully?
- Is the page accessible via keyboard navigation?

## Scoring Calculation

```
total = (design_quality × 0.30) + (originality × 0.25) + (craft × 0.25) + (functionality × 0.20)

3.0-3.4 = Acceptable (ship if under time pressure)
3.5-3.9 = Good (standard quality bar)
4.0-4.4 = Strong (client-facing ready)
4.5-5.0 = Exceptional (portfolio-worthy)
```

## Common Failure Modes (and Fixes)

| Failure | Root Cause | Fix |
|---------|-----------|-----|
| Looks generic | Using default shadcn theme with no customization | Apply design tokens from design-brief.md BEFORE building |
| No visual hierarchy | Everything same size/weight/color | Make ONE element dramatically larger/bolder, mute everything else |
| Feels flat | No depth or layering | Add subtle surface layers, use border + background-color changes |
| Animation feels cheap | Using linear easing or too-long durations | Switch to spring or ease-out, reduce duration to 150-300ms |
| Responsive is broken | Built desktop-first, media queries bolted on | Start mobile, use Tailwind's sm/md/lg prefixes properly |
| Text is unreadable | Poor contrast or wrong font size | Check contrast ratio, ensure body text is 16px minimum |
| Feels empty | Too much whitespace with nothing to anchor it | Add subtle borders, background textures, or section dividers |
| Feels cluttered | Too many competing elements | Remove the least important 30% of elements, increase spacing |
| Dashboard feels static | Zero animation on data load | Add number counters, list stagger, scale pulse on complete |
| Not demo-able | No visual "wow" moment for recording | Build demo mode with hero element, orchestrated cascade, aggressive animations |
| Touch targets too small | Text-only buttons below 24px | Add min-h-6 px-1.5 to ensure WCAG 2.5.8 compliance |
| Modals not accessible | Raw div overlays, no focus trap | Use shadcn Dialog (Base UI/Radix), never raw div overlays |

## Criterion 5b: Demo-ability (weight: bonus, for @buildwithneej projects)

Does this have a "TikTok moment" — something that makes someone stop scrolling?

| Score | Description |
|-------|-------------|
| 1 | Static dashboard, no motion, nothing to record |
| 2 | Basic transitions but looks like any other dashboard in a recording |
| 3 | Has number counters, stagger animations — looks polished when recorded |
| 4 | Has a hero element (orb, animation, distinctive visual) + orchestrated reveals |
| 5 | The demo writes itself — open app, interact, data reveals, "wait what is that?" moment |

**The TikTok Demo Test:**
Imagine you're recording a 15-second screen recording for TikTok. Does this product:
1. Have a visual hook in the first 2 seconds? (Not a line chart — something distinctive)
2. Have number counters that count up? (Every viral dashboard demo has this)
3. Have a "proof" moment? (Real data, real results — hook library with 144K views)
4. Have one interaction that makes people comment "what app is this?"

If the answer to #1 is no, the product needs a demo mode with a hero element.

**What makes dashboards go viral on TikTok (learned from Content Command):**
- Animated number counters (count up from 0 on page load)
- A distinctive hero element (AI orb, not a chart) as the first thing you see
- Staggered panel reveals (cascade in, not all-at-once)
- Real data that proves something works (view counts, engagement rates)
- One signature interaction unlike anything on other dashboards

## Criterion 5: Accessibility — WCAG 2.2 Level AA (weight: bonus)

Not scored in the main rubric but treated as a **hard gate** — any WCAG AA failure is a bug, not a style choice.

### WCAG 2.2 Requirements (2026 standard)

**Contrast (existing):**
- 4.5:1 for normal text (<24px), 3:1 for large text (24px+ or 18px+ bold)
- 3:1 for UI components and graphical objects (borders, icons, focus rings)
- Use OKLCH lightness values to mathematically verify contrast

**Focus (WCAG 2.2 new — 2.4.11, 2.4.13):**
- Focus indicator must NOT be entirely hidden by sticky headers, cookie banners, or fixed elements
- Focus ring minimum: 2px solid outline, 3:1 contrast against adjacent colors
- Focus ring must have a perimeter at least as large as the unfocused component
- Implementation: `outline: 2px solid var(--accent); outline-offset: 2px;`

**Touch Targets (WCAG 2.2 — 2.5.8):**
- Minimum 24x24px for all interactive elements (buttons, links, form controls)
- 44x44px recommended for mobile

**Motion:**
- Respect `prefers-reduced-motion: reduce` — disable all non-essential animation
- Respect `prefers-contrast: more` — increase border contrast, bump font weight

**Semantic HTML:**
- Use `<nav>`, `<main>`, `<header>`, `<footer>`, `<section>`, `<article>` — not div soup
- Every `<img>` has `alt` text (empty `alt=""` for decorative images)
- Form inputs have associated `<label>` elements (not just placeholder)
- Use `aria-label` only when visible text isn't possible
- Heading hierarchy: one `<h1>`, then `<h2>`, `<h3>` in order — no skipping levels

**Keyboard Navigation:**
- All interactive elements reachable via Tab
- Logical tab order (follows visual flow)
- Modals/drawers trap focus, return focus on close
- Custom components have appropriate ARIA roles
- Skip-to-content link as first focusable element

**Implementation checklist:**
```css
/* Add to globals.css */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}

@media (prefers-contrast: more) {
  :root {
    --border: oklch(0.5 0.02 286); /* stronger borders */
    --text-secondary: oklch(0.6 0.015 286); /* darker secondary text */
  }
}

/* Focus visible for keyboard users only */
:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}
:focus:not(:focus-visible) {
  outline: none;
}
```

## Quick Self-Check (30 seconds)

Before delivery, ask these 8 questions:

1. **Squint test** — if I blur my eyes, can I still tell what's most important on the page?
2. **Font test** — am I using a distinctive font pairing from the design brief, not defaults?
3. **Color test** — is there ONE dominant accent color, not a rainbow?
4. **Animation test** — does every animation have a UX purpose I can articulate?
5. **Keyboard test** — can I Tab through the page in logical order with visible focus rings?
6. **Screenshot test** — would I put a screenshot of this in my portfolio?
7. **Touch target test** — are all interactive elements at least 24px tall (min-h-6)?
8. **Modal test** — do all modals/dialogs use shadcn Dialog (focus trap, Escape, overlay click)?

For @buildwithneej projects, add:
9. **Demo test** — if I screen-recorded this for 15 seconds, would it look impressive?
10. **Counter test** — do KPI numbers count up from 0 on page load?

If any answer is "no", iterate before showing the human.
