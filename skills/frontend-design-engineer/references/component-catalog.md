# Component Catalog — Source Decision Tree & Mapping

## Decision tree

```
What type of component do I need?
|
+-- Base structure (input, select, dialog, table, tabs)
|   -> shadcn/ui
|      npx shadcn@latest add [component]
|
+-- Visual effect / landing animation (beam, shimmer, spotlight, particles)
|   -> Magic UI (MIT, React+Tailwind+Motion)
|      npx shadcn@latest add "https://magicui.design/r/[component]"
|
+-- Animated text / micro-interaction (split text, blur text, scroll effects)
|   -> React Bits (MIT+Commons Clause, TS+TW variant recommended)
|      npx shadcn@latest add "https://reactbits.dev/r/[Component]-TS-TW"
|
+-- Premium community components (navbars, pricing, testimonials, hero blocks)
|   -> 21st.dev (verify MIT license per component)
|      npx shadcn@latest add "https://21st.dev/r/[author]/[component]"
|
+-- Advanced animations / unique effects (glassmorphism, 3D, scroll-linked)
    -> Aceternity UI (verify if component is free or Pro)
       URL raw: https://ui.aceternity.com/components/[component]
       Copy source code manually
```

## Component mapping by need

### Backgrounds and textures

- Animated grid -> `animated-grid-pattern` (MagicUI)
- Dots pattern -> `dot-pattern` (MagicUI)
- Interactive grid -> `interactive-grid-pattern` (MagicUI)
- Light rays -> `light-rays` (MagicUI)
- Warp effect -> `warp-background` (MagicUI)
- Particles -> `particles` (MagicUI)
- Meteors -> `meteors` (MagicUI)
- Ripple background -> `ripple` (MagicUI)

### Hero sections

- Video hero -> `hero-video-dialog` (MagicUI)
- Interactive globe -> `globe` (MagicUI) / `Globe` (Aceternity)
- Spotlight text -> `SpotlightNew` (Aceternity)
- Parallax depth -> `parallax-scroll` (Aceternity)
- Speed beam -> `cover` (Aceternity)

### Animated text

- Scroll reveal -> `text-reveal` (MagicUI) / `TextReveal` (Aceternity)
- Scramble type -> `hyper-text` (MagicUI)
- Rotating words -> `word-rotate` (MagicUI)
- Morphing text -> `morphing-text` (MagicUI)
- Split on enter -> `SplitText` (ReactBits TS-TW)
- Blur entrance -> `BlurText` (ReactBits TS-TW)
- Animated counter -> `number-ticker` (MagicUI)
- Aurora glow -> `aurora-text` (MagicUI)

### Cards and containers

- Bento grid -> `bento-grid` (MagicUI) / `BentoGrid` (Aceternity)
- Hover card -> `magic-card` (MagicUI)
- Tiltable card -> `CardSpotlight` (Aceternity)
- Perspective card -> `3d-card-effect` (Aceternity)
- Focus hover effect -> `HoverEffect` (Aceternity)

### Navigation

- macOS-style dock -> `dock` (MagicUI) / `FloatingDock` (Aceternity)
- Sticky hide/show navbar -> `StickyNavbar` (Aceternity)
- Logo marquee -> `marquee` (MagicUI)

### Border effects

- Animated border -> `border-beam` (MagicUI)
- Shine border -> `shine-border` (MagicUI)
- Moving border -> `MovingBorder` (Aceternity)

### Buttons

- Rainbow -> `rainbow-button` (MagicUI)
- Shimmer -> `shimmer-button` (MagicUI)
- Ripple -> `ripple-button` (MagicUI)
- Pulsating -> `pulsating-button` (MagicUI)
- Interactive hover -> `interactive-hover-button` (MagicUI)

### Micro-interactions and utilities

- Custom cursor -> `smooth-cursor` (MagicUI) / `FollowingPointer` (Aceternity)
- Animated beam between elements -> `animated-beam` (MagicUI)
- Orbiting circles -> `orbiting-circles` (MagicUI)
- Confetti on event -> `confetti` (MagicUI)
- Circular progress -> `animated-circular-progress-bar` (MagicUI)
- Scroll progress -> `scroll-progress` (MagicUI)
- Lens / zoom -> `lens` (MagicUI)
- Progressive blur -> `progressive-blur` (MagicUI)
- Avatar stack -> `avatar-circles` (MagicUI)
- Icon cloud -> `icon-cloud` (MagicUI)
- Simulated terminal -> `terminal` (MagicUI)
- Code comparison -> `code-comparison` (MagicUI)
- Backlight glow -> `backlight` (MagicUI)

### Device mocks

- Safari browser -> `safari` (MagicUI)
- iPhone -> `iphone` (MagicUI)
- Android -> `android` (MagicUI)

## Approved sources

| Source | License | CLI |
|--------|---------|-----|
| shadcn/ui | MIT | `npx shadcn@latest add [comp]` |
| Magic UI | MIT | `npx shadcn@latest add "https://magicui.design/r/[comp]"` |
| React Bits | MIT + Commons Clause | `npx shadcn@latest add "https://reactbits.dev/r/[Comp]-TS-TW"` |
| 21st.dev | MIT (verify per component) | `npx shadcn@latest add "https://21st.dev/r/[author]/[comp]"` |
| Aceternity UI | Free: MIT / Pro: commercial | Copy from `ui.aceternity.com/components/[comp]` |

## Not allowed

- GPL libraries (incompatible with commercial projects)
- Last commit > 12 months (abandonment signal)
- Libraries that force webpack as only bundler
- Invented URLs — if not sure the component exists, use the decision tree and verify
