# shadcn/ui Workflow Reference

## MCP-First Philosophy

Use MCP tools instead of `npx shadcn` CLI for component management. Benefits:

- **No terminal required** -- discover, inspect, and plan installations without leaving the conversation
- **Inspect before install** -- view component source, props, dependencies, and examples before committing
- **Registry discovery** -- browse custom registries beyond the default shadcn/ui set
- **Safer installs** -- understand exactly what files will be created/modified
- **Block awareness** -- discover pre-built page templates (dashboards, auth, settings) alongside primitives

The CLI is only needed for the final install step. Everything else happens through MCP introspection.

> Always run `mcp__shadcn__get_project_registries` first to confirm the project is configured before searching.

---

## 7-Step Discovery Workflow

### Step 1: Check configured registries

```
mcp__shadcn__get_project_registries
```

Returns the registries configured in `components.json`. Confirms shadcn is initialized and shows available sources (default, custom, or third-party registries).

### Step 2: Browse available components

```
mcp__shadcn__list_items_in_registries
```

Lists every component, block, and hook available across all configured registries. Use this for a full inventory -- helpful when planning a new page or feature.

### Step 3: Search by keyword

```
mcp__shadcn__search_items_in_registries
  query: "date picker"
```

Fuzzy-search across component names and descriptions. Use when you know what you need but not the exact component name.

### Step 4: View component details

```
mcp__shadcn__view_items_in_registries
  names: ["dialog", "form"]
```

Returns full component documentation: props, sub-components, variants, accessibility notes, and dependency information. **Always view before installing** to understand what you're adding.

### Step 5: See usage examples

```
mcp__shadcn__get_item_examples_from_registries
  names: ["dialog"]
```

Returns real code examples showing composition patterns, common configurations, and integration with other components.

### Step 6: Get install command

```
mcp__shadcn__get_add_command_for_items
  names: ["dialog", "form"]
```

Returns the exact CLI command to install the components, including all dependencies.

### Step 7: Run install

```bash
npx shadcn@latest add dialog form
```

Execute the install command via Bash. This creates files in `components/ui/` and installs any npm dependencies.

---

## Component Categories

| Category | Components | Notes |
|---|---|---|
| **Form & Input** | `button`, `input`, `textarea`, `select`, `checkbox`, `radio-group`, `switch`, `slider`, `date-picker`, `form` | `form` integrates react-hook-form + zod |
| **Layout & Navigation** | `card`, `tabs`, `accordion`, `navigation-menu`, `breadcrumb`, `sidebar`, `separator`, `collapsible` | `sidebar` is a full layout primitive |
| **Overlays & Dialogs** | `dialog`, `drawer`, `sheet`, `popover`, `tooltip`, `dropdown-menu`, `context-menu`, `command`, `alert-dialog` | `command` powers search palettes (cmdk) |
| **Feedback & Status** | `alert`, `badge`, `progress`, `skeleton`, `sonner`, `carousel` | `sonner` replaces the old toast component |
| **Data Display** | `table`, `data-table`, `avatar`, `calendar`, `chart` | `data-table` uses @tanstack/react-table |

### Common dependency chains

- `form` requires: `label`, `button`, plus `react-hook-form` and `@hookform/resolvers`
- `data-table` requires: `table`, plus `@tanstack/react-table`
- `date-picker` requires: `calendar`, `popover`, `button`, plus `date-fns`
- `command` requires: `dialog` (for command palette pattern), plus `cmdk`
- `chart` requires: `card`, plus `recharts`

---

## Composition Patterns

### 1. Form + Zod Validation

The canonical form pattern using react-hook-form with zod schema validation:

```tsx
"use client"

import { z } from "zod"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { Button } from "@/components/ui/button"
import {
  Form, FormControl, FormField, FormItem,
  FormLabel, FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"

const schema = z.object({
  email: z.string().email("Invalid email"),
  name: z.string().min(2, "Name must be at least 2 characters"),
})

export function ProfileForm() {
  const form = useForm<z.infer<typeof schema>>({
    resolver: zodResolver(schema),
    defaultValues: { email: "", name: "" },
  })

  function onSubmit(values: z.infer<typeof schema>) {
    // Server action or API call
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        <FormField control={form.control} name="name" render={({ field }) => (
          <FormItem>
            <FormLabel>Name</FormLabel>
            <FormControl><Input {...field} /></FormControl>
            <FormMessage />
          </FormItem>
        )} />
        <Button type="submit">Save</Button>
      </form>
    </Form>
  )
}
```

### 2. Data Table with Sorting and Filtering

```tsx
"use client"

import { ColumnDef } from "@tanstack/react-table"
import { DataTable } from "@/components/ui/data-table"
import { Button } from "@/components/ui/button"
import { ArrowUpDown } from "lucide-react"

type User = { id: string; name: string; email: string; role: string }

const columns: ColumnDef<User>[] = [
  {
    accessorKey: "name",
    header: ({ column }) => (
      <Button variant="ghost" onClick={() => column.toggleSorting()}>
        Name <ArrowUpDown className="ml-2 h-4 w-4" />
      </Button>
    ),
  },
  { accessorKey: "email", header: "Email" },
  { accessorKey: "role", header: "Role" },
]

export function UsersTable({ data }: { data: User[] }) {
  return <DataTable columns={columns} data={data} searchKey="name" />
}
```

### 3. Responsive Dialog (Dialog on Desktop, Drawer on Mobile)

```tsx
"use client"

import { useMediaQuery } from "@/hooks/use-media-query"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Drawer, DrawerContent, DrawerHeader, DrawerTitle } from "@/components/ui/drawer"

export function ResponsiveDialog({ open, onOpenChange, title, children }) {
  const isDesktop = useMediaQuery("(min-width: 768px)")

  if (isDesktop) {
    return (
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent>
          <DialogHeader><DialogTitle>{title}</DialogTitle></DialogHeader>
          {children}
        </DialogContent>
      </Dialog>
    )
  }

  return (
    <Drawer open={open} onOpenChange={onOpenChange}>
      <DrawerContent>
        <DrawerHeader><DrawerTitle>{title}</DrawerTitle></DrawerHeader>
        <div className="px-4 pb-4">{children}</div>
      </DrawerContent>
    </Drawer>
  )
}
```

---

## Customization Rules

### Never modify `components/ui/` directly

Files in `components/ui/` are managed by shadcn. They get overwritten on update. Instead:

1. **Create wrappers** in `components/` that import from `components/ui/`
2. **Use `cn()`** for class merging when adding styles via props
3. **Extend variants** with `cva()` in your wrapper, not in the base component

```tsx
// components/fancy-button.tsx -- wrapper, NOT in components/ui/
import { Button, type ButtonProps } from "@/components/ui/button"
import { cn } from "@/lib/utils"

export function FancyButton({ className, ...props }: ButtonProps) {
  return <Button className={cn("rounded-full font-bold", className)} {...props} />
}
```

### Theming with CSS variables

Override the design system by changing CSS variables in `globals.css`, not by modifying component files:

```css
@layer base {
  :root {
    --primary: 220 90% 56%;
    --primary-foreground: 0 0% 100%;
    --radius: 0.75rem;
  }
}
```

All shadcn components read from these variables automatically.

---

## Block Patterns

Blocks are pre-built page templates -- full layouts for common patterns like dashboards, auth pages, and settings panels.

### Discovering blocks

```
mcp__shadcn__list_items_in_registries
```

Filter the results for items categorized as blocks. Common blocks include:

- **Dashboard** -- sidebar + header + content area
- **Login / Register** -- auth form layouts
- **Settings** -- tabbed settings pages
- **Sidebar** -- collapsible navigation layouts

### Adapting blocks

1. Install the block to get the base structure
2. Replace hardcoded content with your data
3. Swap individual components for your wrapper variants
4. Adjust CSS variables to match your design tokens

Blocks are starting points, not finished features. Expect to modify layout and content while keeping the structural patterns.

---

## Verification

### Component audit

```
mcp__shadcn__get_audit_checklist
```

Run after adding or updating components to verify health.

### Manual checks

- **Imports resolve** -- all `@/components/ui/*` imports point to installed components
- **Dark mode works** -- every component renders correctly in both light and dark themes
- **Accessibility maintained** -- keyboard navigation, focus rings, aria attributes are intact
- **No unused installs** -- remove components added during exploration but not used in production
- **Dependencies aligned** -- `package.json` includes all peer dependencies for installed components
