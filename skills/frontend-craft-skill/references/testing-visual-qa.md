# Visual QA & Testing Reference

Workflows for visual testing, responsive validation, and performance auditing using browser MCP tools.

---

## Two MCP Approaches

### Chrome DevTools MCP (`mcp__chrome-devtools__*`)

Programmatic browser automation. Best for: screenshots at specific viewports, performance tracing, network monitoring, scripted interactions. Connects to Chrome via DevTools Protocol.

### Claude-in-Chrome MCP (`mcp__claude-in-chrome__*`)

Interactive page reading and manipulation. Best for: reading page text content, filling complex forms, understanding page structure, visual navigation. Operates through an active Chrome tab.

**When to use each:**

| Task | Chrome DevTools | Claude-in-Chrome |
|---|---|---|
| Screenshot capture | `take_screenshot` | -- |
| Viewport resizing | `resize_page`, `emulate` | `resize_window` |
| Click/navigate | `click`, `navigate_page` | `navigate`, `computer` |
| Read page content | `take_snapshot` (DOM) | `read_page`, `get_page_text` |
| Form filling | `fill`, `fill_form` | `form_input` |
| Console monitoring | `list_console_messages` | `read_console_messages` |
| Performance traces | `performance_*` tools | -- |
| Run JS in page | `evaluate_script` | `javascript_tool` |

---

## 5-Step Visual QA Workflow

### Step 1: Start the dev server

```bash
cd /path/to/project && npm run dev
```

Ensure the server is running and accessible at `http://localhost:3000` (or your configured port).

### Step 2: Navigate to the target page

```
mcp__chrome-devtools__navigate_page
  url: "http://localhost:3000/dashboard"
```

Or with Claude-in-Chrome:

```
mcp__claude-in-chrome__navigate
  url: "http://localhost:3000/dashboard"
```

Wait for the page to fully load. For pages with dynamic content, add a wait:

```
mcp__chrome-devtools__wait_for
  selector: "[data-loaded='true']"
  timeout: 5000
```

### Step 3: Take a screenshot

```
mcp__chrome-devtools__take_screenshot
```

Captures the current viewport. For full-page screenshots, evaluate scroll height first.

### Step 4: Analyze the screenshot

Review the captured image for:

- **Layout** -- elements aligned properly, no overflow, correct grid structure
- **Spacing** -- consistent padding/margins, no elements colliding
- **Color contrast** -- text readable against backgrounds, WCAG AA minimum (4.5:1 for text)
- **Text readability** -- appropriate font sizes, line heights, no text cutoff
- **Visual hierarchy** -- headings prominent, CTAs visible, clear information flow
- **Component state** -- hover/focus/disabled states render correctly
- **Dark mode** -- if applicable, verify both themes

### Step 5: Report issues with specific fixes

For each issue found, provide:
1. What's wrong (describe the visual problem)
2. Where it is (component name, approximate location)
3. The fix (specific Tailwind classes, CSS changes, or component prop adjustments)

---

## Responsive Testing

### Test at 4 standard breakpoints

| Device | Width x Height | Tailwind breakpoint |
|---|---|---|
| Mobile | 375 x 812 | Default (no prefix) |
| Tablet | 768 x 1024 | `md:` |
| Desktop | 1280 x 800 | `xl:` |
| Wide | 1920 x 1080 | `2xl:` |

### Resize and capture at each breakpoint

```
mcp__chrome-devtools__resize_page
  width: 375
  height: 812
```

Then take a screenshot. Repeat for each breakpoint.

### Device emulation

For mobile-specific testing (touch, device pixel ratio, user agent):

```
mcp__chrome-devtools__emulate
  device: "iPhone 14"
```

Common devices to test:
- `iPhone 14` -- standard iOS phone
- `iPad` -- tablet baseline
- `Pixel 7` -- standard Android phone

### What to check at each breakpoint

**Mobile (375px):**
- Navigation collapses to hamburger menu or bottom nav
- Cards stack vertically (`flex-col`)
- Text doesn't overflow horizontally
- Touch targets are at least 44x44px
- No horizontal scrollbar

**Tablet (768px):**
- 2-column layouts appear where appropriate
- Sidebar may be collapsible or hidden
- Images scale appropriately
- Tables remain readable or switch to card view

**Desktop (1280px):**
- Full layout renders (sidebar + content + optional aside)
- Grid layouts expand to 3-4 columns
- Hover states work on interactive elements
- Sufficient whitespace -- content doesn't stretch too wide

**Wide (1920px):**
- Content has a max-width constraint (not full-bleed text)
- Layout centers properly with `container mx-auto`
- No excessive empty space on large monitors

---

## Console Error Monitoring

### Check for runtime errors

```
mcp__chrome-devtools__list_console_messages
```

Or with Claude-in-Chrome:

```
mcp__claude-in-chrome__read_console_messages
```

### Common errors to watch for

- **React hydration mismatch** -- `Text content does not match server-rendered HTML`. Fix: ensure server and client render the same content. Use `suppressHydrationWarning` only for intentional differences (e.g., dates, timestamps).
- **Missing key prop** -- `Each child in a list should have a unique "key" prop`. Fix: add stable unique keys to mapped elements.
- **Failed fetch** -- `Failed to fetch` or `NetworkError`. Fix: check API routes, CORS config, environment variables.
- **Next.js warnings** -- `Image with src ... has no width/height`, missing metadata exports. Fix: follow Next.js Image and metadata conventions.
- **404 resources** -- missing fonts, images, or API endpoints in the Network tab.

---

## Performance Vitals

### Capture a performance trace

```
mcp__chrome-devtools__performance_start_trace
```

Navigate the page or interact with it to capture user flows. Then:

```
mcp__chrome-devtools__performance_stop_trace
```

### Analyze the trace

```
mcp__chrome-devtools__performance_analyze_insight
```

### Key metrics and targets

| Metric | Target | What it measures |
|---|---|---|
| **LCP** (Largest Contentful Paint) | < 2.5s | How fast the main content loads |
| **FID** (First Input Delay) | < 100ms | How fast the page responds to interaction |
| **CLS** (Cumulative Layout Shift) | < 0.1 | How much the layout shifts during load |
| **TTFB** (Time to First Byte) | < 800ms | Server response time |
| **INP** (Interaction to Next Paint) | < 200ms | Overall responsiveness |

### Common performance fixes

- **Slow LCP** -- optimize images (next/image with priority), reduce bundle size, use streaming SSR
- **High CLS** -- set explicit width/height on images, use skeleton loaders, avoid injecting content above the fold
- **Poor FID/INP** -- reduce JavaScript execution, defer non-critical scripts, use `React.lazy()` and `Suspense`

---

## Interactive Testing

### Click testing

```
mcp__chrome-devtools__click
  selector: "button[data-testid='submit']"
```

Verify: navigation occurs, modals open, form submits, toast notifications appear.

### Form testing

```
mcp__chrome-devtools__fill
  selector: "input[name='email']"
  value: "test@example.com"
```

For complex multi-field forms:

```
mcp__chrome-devtools__fill_form
  fields: [
    { selector: "input[name='email']", value: "test@example.com" },
    { selector: "input[name='password']", value: "TestPass123!" }
  ]
```

Or use Claude-in-Chrome for more natural form interaction:

```
mcp__claude-in-chrome__form_input
  instruction: "Fill in the registration form with test data"
```

### Verification after interaction

After clicking or submitting, verify the result:
1. Take a screenshot to confirm visual state changed
2. Check console for errors: `mcp__chrome-devtools__list_console_messages`
3. Check network for API calls: `mcp__chrome-devtools__list_network_requests`
4. Verify URL changed (for navigation): `mcp__chrome-devtools__list_pages`

---

## Accessibility Checks

### Automated audit with axe-core

```
mcp__chrome-devtools__evaluate_script
  expression: |
    const script = document.createElement('script');
    script.src = 'https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.7.0/axe.min.js';
    document.head.appendChild(script);
    await new Promise(r => script.onload = r);
    const results = await axe.run();
    JSON.stringify({
      violations: results.violations.map(v => ({
        impact: v.impact,
        description: v.description,
        nodes: v.nodes.length
      }))
    });
```

### Keyboard navigation

Test focus flow by simulating Tab keypresses:

```
mcp__chrome-devtools__press_key
  key: "Tab"
```

Take a screenshot after each Tab press to verify:
- Focus indicator is visible (ring/outline)
- Focus order is logical (top to bottom, left to right)
- No focus traps (except modals, which should trap intentionally)
- All interactive elements are reachable

### ARIA verification

Use a page snapshot to inspect the accessibility tree:

```
mcp__chrome-devtools__take_snapshot
```

Check that:
- Interactive elements have accessible names (`aria-label`, visible text, or `aria-labelledby`)
- Images have meaningful alt text (or `alt=""` for decorative images)
- Modals have `role="dialog"` and `aria-modal="true"`
- Live regions use `aria-live` for dynamic content updates
- Form inputs are associated with labels
