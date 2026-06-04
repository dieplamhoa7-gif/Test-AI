# Design Philosophy

Anti-generic design principles for building distinctive web interfaces with Next.js, shadcn/ui, and Tailwind CSS.

---

## Anti-Generic Manifesto

Default AI-generated interfaces share a recognizable aesthetic: soft gradients fading into white, Inter font everywhere, purple-to-blue CTAs, centered hero sections with stock illustrations, and generous whitespace that says nothing. This is **AI slop**---technically competent but visually forgettable.

The problem is not capability but **intentionality**. When you prompt "build a landing page," you get the median of every landing page ever indexed. The result is a regression to the mean---clean, safe, and indistinguishable from ten thousand other pages.

**Principles to break free:**

1. **Intentionality over intensity** --- A single deliberate choice (one unusual font, one bold color, one unexpected layout) creates more identity than dozens of "creative" flourishes stacked together.
2. **Constraints create character** --- Limit your palette to 2 colors. Use only one font weight. Remove an element you think is necessary. Restriction forces invention.
3. **Reference the physical world** --- The best digital interfaces borrow from print, architecture, signage, packaging, or textile design---not from other websites.
4. **Reject the template** --- If your first instinct matches a template you have seen, discard it. The second or third idea is where distinction lives.
5. **Design for recognition** --- A user should be able to identify the brand from a 200px screenshot. If they cannot, the design lacks identity.

---

## 12 Tone Directions

Before coding, pick a tone. Each tone implies specific decisions about color, type, spacing, and interaction.

| # | Tone | Description | Colors | Type Feel | Spacing |
|---|------|-------------|--------|-----------|---------|
| 1 | **Brutally Minimal** | Maximum restraint. Near-empty layouts. | Black, white, one accent | Monospace or thin sans | Extreme whitespace |
| 2 | **Maximalist Chaos** | Dense, layered, visually loud. | Clashing neons, deep darks | Mixed weights, overlapping | Tight, overlapping |
| 3 | **Retro-Futuristic** | 70s/80s sci-fi meets modern UI. | Amber, cyan, dark grey | Geometric sans, condensed | Grid-strict |
| 4 | **Organic / Natural** | Earthy, textured, imperfect. | Terracotta, sage, cream | Rounded serif, handwritten accents | Loose, asymmetric |
| 5 | **Luxury / Refined** | Quiet confidence, premium feel. | Black, gold, off-white | Thin serif, wide tracking | Generous, symmetrical |
| 6 | **Playful / Toy-like** | Bouncy, colorful, tactile. | Primaries + pastels | Rounded sans, bold weights | Padded, bubbly |
| 7 | **Editorial / Magazine** | Content-first, typographic hierarchy. | Muted + one pop color | Serif headlines, sans body | Column-based |
| 8 | **Brutalist / Raw** | Exposed structure, anti-polish. | High-contrast primaries | System fonts, monospace | Irregular, dense |
| 9 | **Art Deco / Geometric** | Symmetric patterns, metallic accents. | Gold, navy, emerald | Display serif, geometric sans | Structured, ornamental |
| 10 | **Soft / Pastel** | Calming, approachable, light. | Lavender, mint, peach, sky | Rounded sans, medium weight | Airy, padded |
| 11 | **Industrial / Utilitarian** | Functional, no-nonsense, tool-like. | Grey, yellow caution, steel blue | Condensed sans, tabular nums | Compact, grid-aligned |
| 12 | **Dark Academia** | Scholarly, warm, atmospheric. | Deep brown, burgundy, parchment | Serif with character, italic accents | Traditional margins |

---

## Design Brief Template

Fill in this brief BEFORE writing any component code. Five questions that prevent generic output:

```markdown
## Design Brief

### 1. Purpose
What is the single primary action this interface must accomplish?
> [e.g., "Convert visitors into newsletter subscribers"]

### 2. Audience
Who uses this and what do they value visually?
> [e.g., "Senior developers who respect technical depth over marketing polish"]

### 3. Tone
Which of the 12 tones (or blend of 2) fits? Why?
> [e.g., "Editorial/Magazine + Brutally Minimal --- content authority without noise"]

### 4. Differentiator
Name ONE visual element that makes this feel unlike any template:
> [e.g., "Oversized monospace pull quotes as section dividers"]

### 5. Constraints
Hard requirements (brand colors, existing logos, mobile-first, dark mode):
> [e.g., "Must work in dark mode. Brand color: oklch(0.65 0.2 145)"]
```

If a design brief is not provided, construct one from context before proceeding.

---

## Font Pairing Matrix

10 distinctive pairings using `next/font/google`. Each creates a recognizable typographic identity.

### 1. Scholarly Authority
**Playfair Display** (headlines) + **Crimson Pro** (body) --- Traditional, literary, warm.
```ts
import { Playfair_Display, Crimson_Pro } from "next/font/google";
const display = Playfair_Display({ subsets: ["latin"], variable: "--font-display" });
const body = Crimson_Pro({ subsets: ["latin"], variable: "--font-body" });
```

### 2. Technical Precision
**Space Mono** (headlines) + **Outfit** (body) --- Developer-focused, precise, modern.
```ts
import { Space_Mono, Outfit } from "next/font/google";
const display = Space_Mono({ weight: ["400", "700"], subsets: ["latin"], variable: "--font-display" });
const body = Outfit({ subsets: ["latin"], variable: "--font-body" });
```

### 3. Editorial Warmth
**DM Serif Display** (headlines) + **Plus Jakarta Sans** (body) --- Magazine feel, approachable.
```ts
import { DM_Serif_Display, Plus_Jakarta_Sans } from "next/font/google";
const display = DM_Serif_Display({ weight: "400", subsets: ["latin"], variable: "--font-display" });
const body = Plus_Jakarta_Sans({ subsets: ["latin"], variable: "--font-body" });
```

### 4. Bold Contemporary
**Sora** (headlines) + **Libre Baskerville** (body) --- Geometric meets classic tension.
```ts
import { Sora, Libre_Baskerville } from "next/font/google";
const display = Sora({ subsets: ["latin"], variable: "--font-display" });
const body = Libre_Baskerville({ weight: ["400", "700"], subsets: ["latin"], variable: "--font-body" });
```

### 5. Eclectic Craft
**Bricolage Grotesque** (headlines) + **Crimson Pro** (body) --- Quirky yet readable.
```ts
import { Bricolage_Grotesque, Crimson_Pro } from "next/font/google";
const display = Bricolage_Grotesque({ subsets: ["latin"], variable: "--font-display" });
const body = Crimson_Pro({ subsets: ["latin"], variable: "--font-body" });
```

### 6. Clean Authority
**Manrope** (headlines) + **Libre Baskerville** (body) --- Modern sans with classic serif body.
```ts
import { Manrope, Libre_Baskerville } from "next/font/google";
const display = Manrope({ subsets: ["latin"], variable: "--font-display" });
const body = Libre_Baskerville({ weight: ["400", "700"], subsets: ["latin"], variable: "--font-body" });
```

### 7. Geometric Elegance
**Outfit** (headlines) + **DM Serif Display** (body accents) --- Inverted pairing, modern layouts.
```ts
import { Outfit, DM_Serif_Display } from "next/font/google";
const display = Outfit({ subsets: ["latin"], variable: "--font-display" });
const body = DM_Serif_Display({ weight: "400", subsets: ["latin"], variable: "--font-body" });
```

### 8. Warm Minimal
**Plus Jakarta Sans** (headlines) + **Crimson Pro** (body) --- Friendly tech, humanist.
```ts
import { Plus_Jakarta_Sans, Crimson_Pro } from "next/font/google";
const display = Plus_Jakarta_Sans({ subsets: ["latin"], variable: "--font-display" });
const body = Crimson_Pro({ subsets: ["latin"], variable: "--font-body" });
```

### 9. Retro Technical
**Space Mono** (headlines) + **Sora** (body) --- Terminal meets geometric, developer tools.
```ts
import { Space_Mono, Sora } from "next/font/google";
const display = Space_Mono({ weight: ["400", "700"], subsets: ["latin"], variable: "--font-display" });
const body = Sora({ subsets: ["latin"], variable: "--font-body" });
```

### 10. Art Deco Revival
**Playfair Display** (headlines) + **Manrope** (body) --- Ornate meets geometric clean.
```ts
import { Playfair_Display, Manrope } from "next/font/google";
const display = Playfair_Display({ subsets: ["latin"], variable: "--font-display" });
const body = Manrope({ subsets: ["latin"], variable: "--font-body" });
```

---

## NEVER Use List

These choices signal "AI-generated template." Actively avoid them:

### Fonts
- **Inter** --- The default of defaults. Used by every scaffold and template.
- **Roboto** --- Google's system font. Invisible in the worst way.
- **Arial / Helvetica** --- Zero typographic identity for web.
- **Poppins** as a solo font --- Overused in startup templates since 2020.
- **Montserrat** for headings + **Open Sans** for body --- The 2018 generic pairing.

### Color Patterns
- Purple-to-blue gradient on white background --- The "SaaS hero" cliche.
- `#6C63FF` (the illustration purple) --- Signals unDraw/stock illustration default.
- All-grey-with-one-blue-accent --- The "corporate safe" palette.
- Rainbow gradients on text --- The "Web3 landing page" look.

### Layout Patterns
- Centered hero with gradient background + floating mockup image.
- Three-column feature grid with icons from the same icon set.
- Testimonial carousel with circular avatars.
- "Trusted by" logo bar directly under the hero.
- Footer with 4 equal-width link columns.

When you catch yourself reaching for any of these, stop and choose something deliberately different.

---

## Color Theory Quick-Ref

### The 60-30-10 Rule
- **60%** --- Dominant color (backgrounds, large surfaces). Usually neutral.
- **30%** --- Secondary color (cards, sections, supporting elements). Provides depth.
- **10%** --- Accent color (CTAs, highlights, interactive elements). Creates focus.

### Deriving a Palette from One Brand Color
1. **Start with brand hue** --- Express in oklch: `oklch(L C H)` where L=lightness, C=chroma, H=hue.
2. **Generate lightness scale** --- Keep H and C fixed, vary L from 0.15 (darkest) to 0.97 (lightest) in 9 steps.
3. **Create complement** --- Rotate H by 180 degrees for accent. Rotate by 30 degrees for analogous harmony.
4. **Map to semantic tokens** --- Darkest shades become text/foreground. Lightest become backgrounds. Mid-range becomes primary/interactive.
5. **Verify contrast** --- Primary text on background must hit 4.5:1 (WCAG AA). Use oklch lightness difference > 0.4 as a quick proxy.

### Using oklch() in CSS
oklch produces perceptually uniform colors --- equal lightness steps look equally bright to human eyes, unlike HSL.

```css
:root {
  --brand: oklch(0.65 0.2 250);        /* Vibrant blue */
  --brand-light: oklch(0.92 0.05 250); /* Tinted background */
  --brand-dark: oklch(0.35 0.15 250);  /* Dark variant */
  --accent: oklch(0.7 0.2 70);         /* Rotated hue for accent */
}
```

Prefer oklch over HSL for palette generation. The perceptual uniformity eliminates the "some shades look muddy" problem inherent in HSL interpolation.
