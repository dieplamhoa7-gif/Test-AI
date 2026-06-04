# Next.js Architecture

App Router architecture patterns for production Next.js + shadcn/ui applications.

---

## Project Structure Template

```
my-app/
├── app/
│   ├── (marketing)/           # Route group: public pages
│   │   ├── page.tsx           # Home / landing
│   │   ├── about/page.tsx
│   │   ├── pricing/page.tsx
│   │   └── layout.tsx         # Marketing layout (nav + footer)
│   ├── (app)/                 # Route group: authenticated app
│   │   ├── dashboard/page.tsx
│   │   ├── settings/page.tsx
│   │   └── layout.tsx         # App layout (sidebar + header)
│   ├── api/                   # Route handlers (when needed)
│   │   └── webhooks/route.ts
│   ├── layout.tsx             # Root layout (html, body, fonts, providers)
│   ├── globals.css            # CSS variables, Tailwind imports
│   ├── loading.tsx            # Global loading fallback
│   ├── not-found.tsx          # Global 404
│   └── error.tsx              # Global error boundary
├── components/
│   ├── ui/                    # shadcn/ui primitives (managed by CLI)
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   └── dialog.tsx
│   ├── layout/                # Shared layout components
│   │   ├── site-header.tsx
│   │   ├── site-footer.tsx
│   │   └── sidebar-nav.tsx
│   └── shared/                # Shared composed components
│       ├── data-table.tsx
│       └── user-avatar.tsx
├── features/                  # Feature modules (domain-organized)
│   ├── auth/
│   │   ├── components/        # Feature-specific components
│   │   ├── actions/           # Server actions
│   │   ├── hooks/             # Feature-specific hooks
│   │   └── types.ts
│   └── billing/
│       ├── components/
│       ├── actions/
│       └── types.ts
├── lib/                       # Shared utilities
│   ├── utils.ts               # cn() helper, formatters
│   ├── constants.ts           # App-wide constants
│   └── validations.ts         # Shared Zod schemas
├── hooks/                     # Global custom hooks
│   ├── use-media-query.ts
│   └── use-debounce.ts
├── types/                     # Global TypeScript types
│   └── index.ts
├── public/                    # Static assets
│   ├── og-image.png
│   └── favicon.ico
├── components.json            # shadcn/ui configuration
├── next.config.ts
├── tailwind.config.ts         # (v3) or absent (v4 uses CSS)
├── tsconfig.json
└── package.json
```

### Organization Rules
- **`components/ui/`** is managed by the shadcn CLI. Do not manually edit files here.
- **`components/shared/`** holds composed components used across multiple features.
- **`features/`** groups domain logic. Each feature owns its components, actions, and types.
- **`lib/`** is for stateless utilities. No React imports, no hooks.

---

## File Conventions

Every file in the `app/` directory has special meaning to the App Router.

| File | Purpose | Renders When |
|------|---------|-------------|
| `page.tsx` | Route UI | URL matches the segment |
| `layout.tsx` | Shared wrapper | Wraps page + nested layouts. Persists across navigations. |
| `loading.tsx` | Loading UI | Suspense fallback while page/layout loads |
| `error.tsx` | Error boundary | Runtime error in the segment (client component) |
| `not-found.tsx` | 404 UI | `notFound()` is called or no matching route |
| `route.ts` | API endpoint | HTTP request to the segment (no UI) |
| `template.tsx` | Re-mounting wrapper | Like layout but re-mounts on every navigation |
| `default.tsx` | Parallel route fallback | Parallel slot has no matching segment |
| `middleware.ts` | Request interceptor | Every request (lives at project root, not in app/) |

### Key Rule
`layout.tsx` does NOT re-render when navigating between child pages. Use `template.tsx` if you need fresh state on each navigation (rare---use for analytics page views or transition animations).

---

## Server vs Client Decision Tree

All components are Server Components by default. Add `"use client"` only when required.

```
Does it need useState, useEffect, useRef, or other React hooks?
├── YES → "use client"
└── NO
    Does it use browser APIs (window, document, localStorage, IntersectionObserver)?
    ├── YES → "use client"
    └── NO
        Does it need event handlers (onClick, onChange, onSubmit)?
        ├── YES → "use client"
        └── NO
            Does it consume a React Context (useContext)?
            ├── YES → "use client"
            └── NO → Keep as Server Component
```

### The Composition Pattern

Push `"use client"` to the leaves. Server components can import and render client components, passing server-fetched data as props.

```tsx
// app/dashboard/page.tsx (Server Component)
import { getMetrics } from "@/features/analytics/actions/get-metrics";
import { MetricsChart } from "@/features/analytics/components/metrics-chart"; // client

export default async function DashboardPage() {
  const metrics = await getMetrics(); // Server-side fetch
  return (
    <div>
      <h1>Dashboard</h1>
      <MetricsChart data={metrics} />
    </div>
  );
}
```

### What Can NOT Cross the Boundary
- Functions, classes, and non-serializable objects cannot be passed as props from server to client.
- Only JSON-serializable data crosses the boundary: strings, numbers, booleans, arrays, plain objects, null, Date (serialized).

---

## Data Fetching Patterns

### Caching Strategies

| Strategy | Code | Behavior |
|----------|------|----------|
| **Static** (default) | `fetch(url)` | Cached indefinitely. Built at build time. |
| **Time-based** | `fetch(url, { next: { revalidate: 60 } })` | Stale after 60s, revalidates in background. |
| **On-demand** | `fetch(url, { next: { tags: ["products"] } })` | Revalidate via `revalidateTag("products")`. |
| **No cache** | `fetch(url, { cache: "no-store" })` | Fresh on every request. Dynamic rendering. |

### Parallel Fetching

```tsx
// BAD: Sequential (waterfall)
const user = await getUser(id);
const posts = await getPosts(id); // Waits for user to finish

// GOOD: Parallel
const [user, posts] = await Promise.all([
  getUser(id),
  getPosts(id),
]);
```

### When to Use What

| Method | Use When |
|--------|----------|
| Server component fetch | Reading data for page render |
| Server actions | Mutations (create, update, delete) |
| Route handlers (`route.ts`) | Webhooks, third-party callbacks, non-UI endpoints |
| Client-side fetch (SWR/React Query) | Real-time data, polling, optimistic updates |

---

## Server Actions

Server actions are async functions that run on the server, triggered from client or server components.

### Basic Pattern

```tsx
// features/posts/actions/create-post.ts
"use server";

import { revalidatePath } from "next/cache";
import { z } from "zod";

const CreatePostSchema = z.object({
  title: z.string().min(1).max(200),
  content: z.string().min(1),
});

export async function createPost(formData: FormData) {
  const parsed = CreatePostSchema.safeParse({
    title: formData.get("title"),
    content: formData.get("content"),
  });

  if (!parsed.success) {
    return { error: parsed.error.flatten().fieldErrors };
  }

  await db.posts.create({ data: parsed.data });
  revalidatePath("/posts");
}
```

### Form with useActionState

```tsx
"use client";

import { useActionState } from "react";
import { createPost } from "@/features/posts/actions/create-post";

export function CreatePostForm() {
  const [state, formAction, pending] = useActionState(createPost, null);

  return (
    <form action={formAction}>
      <Input name="title" />
      {state?.error?.title && <p className="text-sm text-destructive">{state.error.title}</p>}
      <Button type="submit" disabled={pending}>
        {pending ? "Creating..." : "Create Post"}
      </Button>
    </form>
  );
}
```

### Revalidation Methods
- **`revalidatePath("/posts")`** --- Purge cache for a specific path.
- **`revalidateTag("posts")`** --- Purge all fetches tagged with "posts".
- **`redirect("/posts")`** --- Redirect after mutation (throws, so call last).

---

## Route Organization

### Route Groups `(name)`

Group routes without affecting the URL. Used for separate layouts.

```
app/
├── (marketing)/      → URLs: /, /about, /pricing
│   ├── page.tsx      → /
│   ├── about/page.tsx → /about
│   └── layout.tsx    → Marketing layout
├── (app)/            → URLs: /dashboard, /settings
│   ├── dashboard/page.tsx → /dashboard
│   ├── settings/page.tsx  → /settings
│   └── layout.tsx    → App layout (with sidebar)
```

### Dynamic Routes

| Pattern | Example | Matches |
|---------|---------|---------|
| `[slug]` | `app/blog/[slug]/page.tsx` | `/blog/hello-world` |
| `[...slug]` | `app/docs/[...slug]/page.tsx` | `/docs/a`, `/docs/a/b/c` |
| `[[...slug]]` | `app/docs/[[...slug]]/page.tsx` | `/docs`, `/docs/a`, `/docs/a/b` |

### Parallel Routes `@slot`

Render multiple pages simultaneously in the same layout. Used for modals, split views.

```tsx
// app/layout.tsx
export default function Layout({
  children,
  modal,
}: {
  children: React.ReactNode;
  modal: React.ReactNode;
}) {
  return (
    <>
      {children}
      {modal}
    </>
  );
}
```

---

## Metadata & SEO

### Static Metadata

```tsx
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "My App - Home",
  description: "A brief description for search results.",
  openGraph: {
    title: "My App",
    description: "A brief description for social sharing.",
    images: ["/og-image.png"],
  },
};
```

### Dynamic Metadata

```tsx
export async function generateMetadata({
  params,
}: {
  params: { slug: string };
}): Promise<Metadata> {
  const post = await getPost(params.slug);
  return {
    title: post.title,
    description: post.excerpt,
    openGraph: { images: [post.coverImage] },
  };
}
```

### Metadata Files

| File | Output |
|------|--------|
| `favicon.ico` | `<link rel="icon">` |
| `opengraph-image.tsx` | Dynamic OG image with `ImageResponse` |
| `robots.ts` | `robots.txt` content |
| `sitemap.ts` | XML sitemap |

---

## Middleware

Middleware runs before every request. It lives at the project root (not inside `app/`).

```ts
// middleware.ts
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Authentication check
  const token = request.cookies.get("session")?.value;
  if (pathname.startsWith("/dashboard") && !token) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    "/((?!_next/static|_next/image|favicon.ico|api/webhooks).*)",
  ],
};
```

### Common Middleware Patterns

| Pattern | Implementation |
|---------|---------------|
| **Auth redirect** | Check session cookie, redirect to `/login` |
| **Locale detection** | Read `Accept-Language`, redirect to `/en/...` |
| **A/B testing** | Set cookie with variant, rewrite to variant page |
| **Rate limiting** | Check IP-based counter, return 429 if exceeded |

### Performance Note
Middleware runs on the Edge Runtime. It cannot use Node.js APIs (fs, crypto randomBytes, etc.). Keep it fast---it runs on every matched request.
