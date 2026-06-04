# Accessibility Checklist

Accessibility reference for shadcn/ui + Radix UI projects targeting WCAG 2.1 AA compliance.

---

## WCAG 2.1 AA Top 10

The 10 criteria most relevant to interactive web applications.

| # | Criterion | What It Means | Common Violation |
|---|-----------|---------------|------------------|
| 1 | **1.1.1 Non-text Content** | All images, icons, and media have text alternatives. | Decorative icons missing `aria-hidden="true"`, informative images missing `alt`. |
| 2 | **1.3.1 Info and Relationships** | Structure conveyed visually is also conveyed programmatically. | Using `<div>` styled as heading instead of `<h2>`. Lists without `<ul>`/`<ol>`. |
| 3 | **1.4.3 Contrast (Minimum)** | Text has at least 4.5:1 contrast ratio against background. | Light grey placeholder text. Muted foreground on muted background in dark mode. |
| 4 | **1.4.11 Non-text Contrast** | UI components and graphics have 3:1 contrast. | Input borders too faint. Icon-only buttons with low-contrast icons. |
| 5 | **2.1.1 Keyboard** | All functionality available via keyboard. | Custom dropdowns, sliders, or toggles only respond to mouse. |
| 6 | **2.4.3 Focus Order** | Tab order follows logical reading sequence. | Modal opens but focus stays behind the overlay. Tab order jumps erratically. |
| 7 | **2.4.7 Focus Visible** | Keyboard focus indicator is always visible. | `outline: none` without replacement. Focus ring removed for aesthetics. |
| 8 | **3.3.1 Error Identification** | Form errors are identified and described in text. | Red border only (no text message). Error shown far from the field. |
| 9 | **3.3.2 Labels or Instructions** | Form inputs have visible, associated labels. | Placeholder used as the only label. Label visually present but not `<label htmlFor>`. |
| 10 | **4.1.2 Name, Role, Value** | Custom components expose name, role, and state to assistive tech. | Custom toggle has no `role="switch"` or `aria-checked`. Tab component missing `role="tablist"`. |

---

## What Radix Handles

shadcn/ui is built on Radix UI primitives. Radix provides these accessibility features automatically:

- **Focus trapping** in Dialog, AlertDialog, and Sheet. Focus cycles within the overlay and cannot escape to the page behind it.
- **Scroll lock** when modals are open. Background content cannot be scrolled.
- **Keyboard navigation** in DropdownMenu, Select, Combobox, and NavigationMenu. Arrow keys move through options, Enter selects, Escape dismisses.
- **Roving tabindex** in RadioGroup, Tabs, and ToolBar. Only the active item is in the tab order; arrow keys move between items.
- **ARIA attributes** managed automatically: `aria-expanded`, `aria-selected`, `aria-checked`, `aria-haspopup`, `role` assignments.
- **Escape to close** for all overlay components (Dialog, Popover, DropdownMenu, Tooltip, Sheet).
- **Click outside to close** for Popover and DropdownMenu.
- **Type-ahead** in Select and Combobox---typing characters jumps to matching options.
- **Focus restoration** when overlays close, focus returns to the trigger element.

**What Radix does NOT handle** (your responsibility):
- Providing meaningful labels (`aria-label` on icon-only buttons).
- Contrast ratios in your color theme.
- Heading hierarchy and semantic HTML structure.
- Live region announcements for dynamic content updates.
- Skip links and landmark roles.

---

## Keyboard Patterns

Required keyboard support by component type.

| Component | Keys | Behavior |
|-----------|------|----------|
| **Button / Link** | `Enter`, `Space` | Activate. Both keys should work for buttons. Links respond to `Enter` only. |
| **Dialog / Sheet** | `Escape` | Close. Focus returns to trigger. |
| **Dropdown Menu** | `Enter`/`Space` open, `Arrow` navigate, `Escape` close | Arrow keys cycle through items. Home/End jump to first/last. |
| **Tabs** | `Arrow Left`/`Right` | Move between tabs. `Tab` key exits the tab list to content. |
| **Accordion** | `Enter`/`Space` toggle, `Arrow` navigate | Arrow keys move between headers. |
| **Select / Combobox** | `Enter`/`Space` open, `Arrow` navigate, `Escape` close | Type characters for type-ahead. |
| **Checkbox** | `Space` | Toggle checked state. |
| **Switch / Toggle** | `Space`, `Enter` | Toggle on/off. |
| **Slider** | `Arrow Left`/`Right`, `Home`/`End` | Adjust value. Home = min, End = max. |
| **Toast** | `Escape` | Dismiss. Focus should not be captured by toasts. |

### Universal Keys
- **`Tab`** / **`Shift+Tab`**: Move focus forward/backward through interactive elements.
- **`Escape`**: Dismiss the topmost overlay (modal, popover, dropdown).
- All interactive elements must have a visible focus indicator.

---

## Contrast Requirements

### Ratios

| Element Type | Minimum Ratio | Examples |
|-------------|---------------|----------|
| **Normal text** (< 18px or < 14px bold) | **4.5:1** | Body text, labels, links, error messages |
| **Large text** (>= 18px or >= 14px bold) | **3:1** | Headings, display text |
| **UI components** | **3:1** | Input borders, button outlines, icon buttons, focus indicators |
| **Decorative / disabled** | No requirement | Disabled buttons, decorative borders |

### Checking Contrast

1. **Chrome DevTools**: Inspect element > color picker shows contrast ratio inline.
2. **Lighthouse**: Run a11y audit in DevTools > Lighthouse tab.
3. **axe DevTools**: Browser extension with detailed violation reports.
4. **Design time**: Use oklch lightness difference > 0.4 as a fast proxy for sufficient contrast.

### Common Dark Mode Pitfalls
- `--muted-foreground` on `--muted` often fails in custom themes. Always verify.
- Colored text on colored backgrounds (e.g., green success text on light green) frequently fails.
- Border-only inputs become invisible when border contrast is below 3:1.

---

## Screen Reader Patterns

### Semantic HTML First
Use native elements whenever possible. `<button>` is always better than `<div role="button">`.

```tsx
// GOOD: Semantic
<nav aria-label="Main navigation">
  <ul>
    <li><a href="/about">About</a></li>
  </ul>
</nav>

// BAD: Div soup
<div className="nav">
  <div onClick={...}>About</div>
</div>
```

### Labeling Patterns

| Technique | When to Use | Example |
|-----------|-------------|---------|
| `aria-label` | Icon-only buttons, unlabeled inputs | `<Button aria-label="Close dialog">` |
| `aria-labelledby` | Label exists elsewhere in the DOM | `<div role="dialog" aria-labelledby="dialog-title">` |
| `aria-describedby` | Additional help text for a control | `<Input aria-describedby="email-hint">` |
| `sr-only` class | Visually hidden text for context | `<span className="sr-only">Open menu</span>` |

### Live Regions for Dynamic Content

```tsx
// Announce toast messages to screen readers
<div aria-live="polite" aria-atomic="true">
  {toastMessage}
</div>

// Announce urgent errors immediately
<div role="alert">
  {errorMessage}
</div>
```

- `aria-live="polite"`: Announced after current speech finishes (toasts, status updates).
- `role="alert"` / `aria-live="assertive"`: Interrupts current speech (errors, urgent messages).

---

## 15-Item Shipping Checklist

Run through this checklist before every production deployment.

| # | Check | How to Verify |
|---|-------|---------------|
| 1 | **Keyboard navigation** works for all interactive elements. | Tab through the entire page without using a mouse. |
| 2 | **Focus indicators** are visible on every focusable element. | Tab through in a well-lit environment. Focus ring must be obvious. |
| 3 | **Color contrast** meets 4.5:1 for text, 3:1 for UI components. | Run Lighthouse a11y audit or axe DevTools scan. |
| 4 | **Alt text** on all informative images. Decorative images have `alt=""`. | Search for `<img` and `<Image` without `alt`. Check all are meaningful. |
| 5 | **Form labels** are associated with inputs via `htmlFor`/`id` or wrapping. | Click each label---does it focus the input? |
| 6 | **Error messages** are text-based, associated with the field, and descriptive. | Submit forms with invalid data. Errors must be visible and announced. |
| 7 | **Heading hierarchy** is logical (`h1` > `h2` > `h3`, no skips). | Use HeadingsMap browser extension or check with screen reader. |
| 8 | **Skip link** allows keyboard users to bypass navigation. | Press Tab on page load. First focus should be "Skip to content". |
| 9 | **Motion preferences** respected via `prefers-reduced-motion`. | Enable "Reduce motion" in OS, verify animations are disabled/reduced. |
| 10 | **Color is not the sole indicator** of state (error, success, active). | View in grayscale. Can you still understand all states? |
| 11 | **Touch targets** are at least 44x44px on mobile. | Inspect button/link sizes in mobile viewport. |
| 12 | **`lang` attribute** set on `<html>` element. | Inspect `<html lang="en">`. Change for non-English content. |
| 13 | **Page titles** are unique and descriptive for every route. | Navigate between pages, check `<title>` in browser tab. |
| 14 | **Landmark roles** define page structure (`<header>`, `<main>`, `<nav>`, `<footer>`). | Use screen reader landmarks navigation (VoiceOver: rotor > landmarks). |
| 15 | **No auto-playing** media with sound. Video/audio requires user-initiated play. | Load every page fresh. Nothing should make sound automatically. |

### Quick Automated Checks
```bash
# Run axe-core on a local dev server
npx @axe-core/cli http://localhost:3000

# Run Lighthouse a11y audit
npx lighthouse http://localhost:3000 --only-categories=accessibility --output=json
```

For shadcn/ui components, most of items 1, 2, and keyboard navigation (partial) are handled by Radix. Items 3-15 are always your responsibility.
