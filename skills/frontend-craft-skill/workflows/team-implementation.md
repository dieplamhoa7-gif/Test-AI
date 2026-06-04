# Team Implementation Workflow

Orchestrates a 3-teammate team for parallel frontend implementation with visual QA.

## When to Use

- Feature spans 3+ pages or complex interactive components
- Design system setup + page building + QA can run in parallel
- Invoked via `/fc team` or when lead determines parallelization is beneficial

## Team Architecture

```
Lead (coordinator, delegate mode)
  ├── design-system-lead  → Theme, tokens, shadcn installs, layout
  ├── ui-lead             → Pages, composed components, client interactions
  └── quality-lead        → Visual QA, screenshots, a11y, performance
```

**Team Name:** `fc-impl-{feature}`

## File Ownership

**CRITICAL:** Each teammate ONLY modifies files in their domain. Violations cause merge conflicts.

| Domain | Owner | File Patterns |
|--------|-------|---------------|
| Design System | design-system-lead | `app/globals.css`, `app/layout.tsx`, `tailwind.config.*`, `components/theme-provider.tsx`, `components/ui/*`, `public/fonts/` |
| UI Implementation | ui-lead | `app/(routes)/**`, `app/**/page.tsx`, `app/**/loading.tsx`, `app/**/error.tsx`, `components/*` (non-ui), `features/**/components/**`, `hooks/**` |
| Quality Assurance | quality-lead | `__tests__/**`, `*.test.*`, `e2e/**`, `docs/screenshots/**` |
| Shared (Lead Only) | lead | `components.json`, `package.json`, `tsconfig.json`, `next.config.*`, `types/**`, `.env*` |

### Grey Areas

| Pattern | Default Owner | Rationale |
|---------|--------------|-----------|
| `features/**/hooks/*` | ui-lead | React hooks are UI concerns |
| `features/**/actions/*` | ui-lead | Server actions tied to UI forms |
| `lib/utils.ts` | lead (shared) | Used by all domains |

### Shared File Protocol

When a teammate needs a shared file changed:
1. Teammate messages lead: "Need X type definition" or "Need Y package installed"
2. Lead creates/modifies the shared file
3. Lead notifies all affected teammates
4. Teammates import and use

## Step-by-Step Execution

### Step 1: Analyze Feature

Break the feature into pages/components. List required shadcn components, custom components, and data flows.

### Step 2: Create Team

```
TeamCreate({ team_name: "fc-impl-{feature}", description: "Frontend implementation for {feature}" })
```

### Step 3: Create Tasks

For EACH page or major component, create this task set:

| # | Owner | Subject | BlockedBy |
|---|-------|---------|-----------|
| 1 | quality-lead | Define visual acceptance criteria for {page} | — |
| 2 | design-system-lead | Install shadcn components and configure tokens for {page} | — |
| 3 | ui-lead | Implement {page} layout and components | 2 |
| 4 | quality-lead | Visual QA: screenshots at 4 breakpoints, console check, a11y | 1, 3 |
| 5 | (fix owner) | Fix issues from QA | 4 |

**Task description template:**
```
Page: {page name}
Acceptance criteria: {list from spec}
File ownership: {specific files this task creates/modifies}
shadcn components needed: {list}
MCPs available: {list for this role}
```

### Step 4: Spawn Teammates

Spawn all 3 using fully self-contained prompts from `spawn-prompts/`:

| Name | Prompt Source | Model | Mode |
|------|-------------|-------|------|
| design-system-lead | `spawn-prompts/design-system-lead.md` | opus | bypassPermissions |
| ui-lead | `spawn-prompts/ui-lead.md` | opus | bypassPermissions |
| quality-lead | `spawn-prompts/quality-lead.md` | opus | bypassPermissions |

Spawn config for each:
```
Task({
  name: "{role}",
  subagent_type: "general-purpose",
  model: "opus",
  mode: "bypassPermissions",
  team_name: "fc-impl-{feature}",
  prompt: <contents of spawn-prompts/{role}.md + feature-specific context>,
  run_in_background: true
})
```

**IMPORTANT:** Spawn prompts must be fully self-contained. Teammates do NOT inherit conversation history. Append feature-specific context (pages, components, acceptance criteria) to the spawn prompt.

### Step 5: Assign Tasks

```
TaskUpdate({ taskId: "1", owner: "quality-lead" })
TaskUpdate({ taskId: "2", owner: "design-system-lead" })
TaskUpdate({ taskId: "3", owner: "ui-lead" })
TaskUpdate({ taskId: "4", owner: "quality-lead" })
```

### Step 6: TDD-for-UI Pipeline

Per page, the pipeline runs in phases:

1. **DEFINE** (quality-lead + design-system-lead, PARALLEL):
   - quality-lead defines visual acceptance criteria (breakpoints, a11y, perf thresholds)
   - design-system-lead installs components, configures tokens, sets up layout
2. **BUILD** (ui-lead): Implements page using installed components (blocked by design-system-lead)
3. **VERIFY** (quality-lead): Screenshots at 4 breakpoints, console errors, a11y audit, performance trace
   - PASS → page complete
   - FAIL → identify fix owner → fix → re-verify

### Step 7: Lead Coordination

- **Shared types:** Receive type requests → create in `types/` → notify teammates
- **Package installs:** Receive package requests → install → notify teammates
- **QA failures:** Monitor quality-lead reports → route fixes to correct owner
- **API contracts:** Relay mismatches between design-system-lead and ui-lead

### Step 8: Feature Complete

1. quality-lead runs final full-page QA across all pages
2. Lead reviews all files for consistency
3. Git commit: `feat({feature}): implement {feature description}`
4. Cleanup: `shutdown_request` to all 3 → `TeamDelete()`

## Performance Expectations

| Metric | Target |
|--------|--------|
| Per-page pipeline | 10-20 minutes |
| Design system setup | 5-10 minutes |
| Page implementation | 8-15 minutes |
| Visual QA verification | 5-10 minutes |
| Total for 3-page feature | 30-60 minutes |
