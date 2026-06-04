# New Project Setup

Step-by-step workflow for bootstrapping a **Next.js + shadcn/ui + Tailwind CSS v4** project with a production-ready foundation.

---

## Step 1: Create Next.js App

Scaffold the project with all recommended defaults:

```bash
npx create-next-app@latest my-app \
  --typescript \
  --eslint \
  --tailwind \
  --app \
  --src-dir \
  --import-alias "@/*" \
  --use-npm
```

**Flags explained:**
- `--typescript` : Strict TypeScript from the start
- `--eslint` : Built-in ESLint configuration
- `--tailwind` : Pre-configured Tailwind CSS v4
- `--app` : App Router (not Pages Router)
- `--src-dir` : All code lives under `src/` for cleaner root
- `--import-alias "@/*"` : Clean imports like `@/components/Button`

After creation, `cd my-app` and verify with `npm run dev`.

---

## Step 2: Initialize shadcn/ui

Run the shadcn CLI to set up the component system:

```bash
npx shadcn@latest init
```

When prompted, choose:
- **Style:** New York (recommended -- cleaner, more modern aesthetic)
- **Base color:** Neutral (or Zinc/Slate to match your brand)
- **CSS variables:** Yes (required for theme switching)

This creates:
- `components.json` -- shadcn project configuration
- `lib/utils.ts` -- the `cn()` utility for merging Tailwind classes
- `components/ui/` -- directory where installed components land

---

## Step 3: Set Up Design System

### 3a. Copy the globals template

Replace the auto-generated `globals.css` with the skill's design-system-ready template:

```bash
cp ~/.claude/skills/frontend-craft/assets/globals-template.css src/app/globals.css
```

### 3b. Customize brand colors

Edit the CSS variables in `src/app/globals.css` to match the project's brand. Key variables to update:
- `--primary` / `--primary-foreground` : Main brand color
- `--accent` / `--accent-foreground` : Secondary brand color
- `--radius` : Global border radius (`0.5rem` default, `0.75rem` for rounder)

All color values use **HSL triplets without `hsl()` wrapper** (e.g., `240 5.9% 10%`).

### 3c. Configure fonts

In `src/app/layout.tsx`, import fonts using `next/font/google` for automatic optimization:

```tsx
import { Inter, JetBrains_Mono } from "next/font/google";

const inter = Inter({ subsets: ["latin"], variable: "--font-sans" });
const jetbrainsMono = JetBrains_Mono({ subsets: ["latin"], variable: "--font-mono" });
```

Apply the CSS variables to the `<html>` element (shown in Step 6).

---

## Step 4: Install Core Components

Install the essential shadcn components every project needs in a single batch:

```bash
npx shadcn@latest add button card input form label dialog dropdown-menu separator sonner badge
```

**Why these components:**
- `button` : Primary interaction element, used everywhere
- `card` : Content containers and layout sections
- `input` + `form` + `label` : Form handling (form includes react-hook-form + zod integration)
- `dialog` : Modal confirmations, detail views
- `dropdown-menu` : Navigation menus, action menus
- `separator` : Visual dividers between content sections
- `sonner` : Toast notifications (lightweight, accessible)
- `badge` : Status indicators, tags, counts

Install additional components as needed with `npx shadcn@latest add <name>`. Use the shadcn MCP tool `mcp__shadcn__search_items_in_registries` to discover available components.

---

## Step 5: Theme Provider

### 5a. Install next-themes

```bash
npm install next-themes
```

### 5b. Create the theme provider component

Create `src/components/theme-provider.tsx`:

```tsx
"use client";

import * as React from "react";
import { ThemeProvider as NextThemesProvider } from "next-themes";

export function ThemeProvider({
  children,
  ...props
}: React.ComponentProps<typeof NextThemesProvider>) {
  return <NextThemesProvider {...props}>{children}</NextThemesProvider>;
}
```

This wrapper makes `next-themes` compatible with React Server Components by isolating the `"use client"` boundary.

### 5c. (Optional) Add a theme toggle

```bash
npx shadcn@latest add button dropdown-menu
```

Create a `ThemeToggle` component using the `useTheme()` hook from `next-themes` with a dropdown for system/light/dark options.

---

## Step 6: Root Layout

Complete `src/app/layout.tsx` with all integrations:

```tsx
import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import { ThemeProvider } from "@/components/theme-provider";
import { Toaster } from "@/components/ui/sonner";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-sans" });
const jetbrainsMono = JetBrains_Mono({ subsets: ["latin"], variable: "--font-mono" });

export const metadata: Metadata = {
  title: "My App",
  description: "Built with Next.js, shadcn/ui, and Tailwind CSS",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="en"
      className={`${inter.variable} ${jetbrainsMono.variable}`}
      suppressHydrationWarning
    >
      <body className="min-h-screen font-sans antialiased">
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          {children}
          <Toaster />
        </ThemeProvider>
      </body>
    </html>
  );
}
```

**Key details:**
- `suppressHydrationWarning` on `<html>` prevents React warnings from next-themes injecting the theme class before hydration
- `attribute="class"` tells next-themes to toggle via CSS class (matches our `.dark` selector in globals.css)
- `disableTransitionOnChange` prevents a flash of transition when switching themes
- `<Toaster />` from sonner is placed inside ThemeProvider so toasts respect the active theme

---

## Step 7: Project Structure

Create the recommended directory structure:

```bash
mkdir -p src/components/ui    # Auto-created by shadcn
mkdir -p src/components        # Custom composed components (e.g. Navbar, Footer)
mkdir -p src/features          # Domain modules (e.g. features/auth/, features/dashboard/)
mkdir -p src/hooks             # Custom React hooks
mkdir -p src/lib               # Utility functions, API clients, constants
mkdir -p src/types             # Shared TypeScript type definitions
```

**Structure rationale:**
- `components/ui/` : Raw shadcn primitives (never edit these directly)
- `components/` : Composed components built from ui/ primitives
- `features/` : Feature-sliced modules with co-located components, hooks, and utils
- `hooks/` : Shared hooks used across multiple features
- `lib/` : Non-React utilities (API clients, helpers, constants)
- `types/` : Global TypeScript interfaces and type aliases

---

## Step 8: Verify

Run the development server and confirm everything works:

```bash
npm run dev
```

**Verification checklist:**
- [ ] Page loads at `http://localhost:3000` without errors
- [ ] Tailwind utility classes apply correctly (inspect element)
- [ ] Dark mode toggles properly (if ThemeToggle added)
- [ ] shadcn components render with correct styling (try a `<Button>`)
- [ ] Sonner toasts fire correctly (`toast("Hello!")` in a client component)
- [ ] No console errors or hydration warnings
- [ ] Fonts load correctly (check Network tab for font files)

---

## MCP Verification

Use the shadcn MCP tools to validate the project setup:

```
mcp__shadcn__get_project_registries
```
Confirms that `components.json` is valid and the project is correctly configured for shadcn/ui. This should return the registries your project is connected to.

```
mcp__shadcn__get_audit_checklist
```
Returns a checklist of best practices for shadcn/ui projects. Use this as a sanity check to ensure nothing was missed during setup.

If either tool reports errors, revisit Step 2 and re-run `npx shadcn@latest init`.
