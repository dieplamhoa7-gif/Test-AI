# Complete Usage Examples

## Example 1 — SaaS Productivity Tool (Claude Code)

**Input:** "I need a landing page for my task management SaaS for teams"

**Fase 1:**
- Direction chosen: **Swiss Minimal**
- Reason: B2B SaaS + productivity = clarity over expression. Nothing distracts from the CTA.

**Fase 2 — Components selected:**

```bash
# Base structural
npx shadcn@latest add button card badge

# Visual effects
npx shadcn@latest add "https://magicui.design/r/bento-grid"
npx shadcn@latest add "https://magicui.design/r/animated-beam"
npx shadcn@latest add "https://magicui.design/r/number-ticker"
npx shadcn@latest add "https://magicui.design/r/border-beam"
npx shadcn@latest add "https://magicui.design/r/marquee"
```

**Fase 3 — Swiss Minimal adaptation:**

```tsx
// BEFORE (generic)
<div className="bg-blue-500 text-white rounded-2xl p-8">

// AFTER (Swiss Minimal tokens)
<div
  className="rounded-[4px] p-8"
  style={{
    background: "var(--color-accent)",   // #0055FF
    color: "var(--color-background)",    // #FFFFFF
  }}
>
```

**Fase 4 — Animations:**

```tsx
"use client";
import { useGSAP } from "@gsap/react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useRef } from "react";

gsap.registerPlugin(ScrollTrigger);

export function LandingHero() {
  const container = useRef<HTMLDivElement>(null);

  useGSAP(() => {
    const prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (prefersReduced) return;

    gsap.from(".hero-title", { autoAlpha: 0, y: 24, duration: 0.7, ease: "power2.out" });
    gsap.from(".hero-cta", { autoAlpha: 0, y: 16, duration: 0.6, delay: 0.25, ease: "power2.out" });
    gsap.from(".feature-card", {
      autoAlpha: 0, y: 32, stagger: 0.12, duration: 0.6, ease: "power2.out",
      scrollTrigger: { trigger: ".features-section", start: "top 80%" },
    });
  }, { scope: container });

  return <div ref={container}>...</div>;
}
```

---

## Example 2 — Disruptive Startup (Antigravity/Gemini)

**Input:** "I want a page for my generative AI startup, something eye-catching, different"

**Fase 1:**
- Direction chosen: **Neo-Brutalist**
- Reason: Generative AI + startup + "different" = visual identity that breaks expectations. The user wants impact, not corporate elegance.

**Fase 2 — Ready-to-paste code (no terminal available):**

```tsx
// INSTALLATION REQUIRED: npm install gsap @gsap/react
// COMPONENTS REQUIRED:
//   npx shadcn@latest add "https://magicui.design/r/flickering-grid"
//   npx shadcn@latest add "https://reactbits.dev/r/SplitText-TS-TW"
//   npx shadcn@latest add "https://magicui.design/r/shimmer-button"

"use client";
import { useGSAP } from "@gsap/react";
import gsap from "gsap";
import { useRef } from "react";
import { FlickeringGrid } from "@/components/ui/flickering-grid";
import { ShimmerButton } from "@/components/ui/shimmer-button";

export function NeoBrutalistHero() {
  const container = useRef<HTMLDivElement>(null);

  useGSAP(() => {
    const prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (prefersReduced) return;
    gsap.from(".hero-headline", { autoAlpha: 0, x: -40, duration: 0.6, ease: "power3.out" });
  }, { scope: container });

  return (
    <section
      ref={container}
      style={{
        background: "var(--color-background)",
        border: "4px solid var(--color-primary)",
        boxShadow: "var(--shadow)",
        fontFamily: "var(--font-heading)",
      }}
      className="relative min-h-screen flex flex-col items-center justify-center p-8"
    >
      <FlickeringGrid className="absolute inset-0 opacity-20" color="#000000" />
      <h1
        className="hero-headline text-6xl md:text-9xl font-bold tracking-tighter relative z-10"
        style={{ color: "var(--color-text)" }}
      >
        THE AI THAT<br />DOESN'T ASK<br />PERMISSION
      </h1>
      <ShimmerButton
        className="mt-8 relative z-10"
        style={{
          background: "var(--color-primary)",
          color: "var(--color-secondary)",
          border: "2px solid var(--color-primary)",
        }}
      >
        Enter now
      </ShimmerButton>
    </section>
  );
}
```

**Fase 3 — Neo-Brutalist adaptation applied:**
- No border-radius (`rounded-none` or `rx: 0`)
- Hard shadow `4px 4px 0px #000`
- Typography: Space Grotesk, weight 700, tracking-tighter
- Colors: pure black + saturated yellow + magenta as accent

---

## Example 3 — Specialty Coffee Shop (new project, Claude Code)

**Input:** "I need a website for my coffee shop where we offer specialty coffee"

**Fase 0.1:** No URL -> new project -> flow 0.B

**Intake questions asked in one message, user responds with:**
- Name: Ritmo Negro, artisanal roaster focused on single-origin Latin American coffees
- Target: Professionals and coffee lovers, 25-45
- CTA: Book a table / Visit the store
- Sections: Hero, Our Story, Our Origins (countries map), Coffee Menu (filterable), Preparation Process, Gallery, Hours & Location, Contact
- Has photos and logo
- Reference: Onyx Coffee website
- Colors: dark brown, cream, jungle green
- Needs: Menu filter by method (espresso, pour over, cold brew) and Google Map

**Fase 1:**
- Direction chosen: **Understated Elegance**
- Reason: Single-origin artisanal coffee + refined audience + Onyx Coffee reference = calm editorial aesthetic that communicates care without ostentation.

**Fase 2 — Components:**

```bash
npx shadcn@latest add button card badge tabs
npx shadcn@latest add "https://magicui.design/r/blur-fade"
npx shadcn@latest add "https://magicui.design/r/marquee"
npx shadcn@latest add "https://magicui.design/r/progressive-blur"
npx shadcn@latest add "https://magicui.design/r/lens"
```

**Fase 3 — Token adaptation:**
```
--color-primary:    #4A5D4E  (jungle green)
--color-secondary:  #8B9D8F
--color-background: #F4F1EB  (cream)
--color-text:       #2C352D  (dark brown)
--color-accent:     #D4A373  (warm coffee)
--font-heading:     'Cormorant Garamond', serif
--font-body:        'Lato', sans-serif
```
