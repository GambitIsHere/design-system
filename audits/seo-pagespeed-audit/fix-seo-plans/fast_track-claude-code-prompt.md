# Fast Track — SEO Sprint 1 · Claude Code Execution Prompt

> **Target repo:** `/Users/srikan/Documents/GitHub/Sanjow/Sanjow-Ventures/fast-track-ai`
> **Scope:** 5 in-place tickets (`FAST_TRACK-FIX-001` → `FAST_TRACK-FIX-005`) from
> `design-system/audits/seo-pagespeed-audit/fix-seo-plans/fast_track.md`.
> **Out of scope this sprint:** 4 architectural tickets (`ARCH-006` bundle,
> `ARCH-007` image pipeline, `ARCH-008` hreflang middleware, `ARCH-009` legacy
> domain sunset) — each is a dedicated follow-up sprint.
> **Estimated effort:** ~7.5h sequential / ~1 focused session.
> **Estimated lift:** +21 audit points (from SEO 49.7 / Perf 60.7 baseline).

---

## ✅ CONFIRMED — canonical production host

- **Canonical host:** `https://travel-synch.com`
- **Default locale:** `en` serves bare (`/`, `/faq`), not `/en/*`
- **Other locales:** `/fr/…`, `/es/…`, `/pt/…`, `/it/…`, `/de/…`, `/tr/…`, `/pl/…`
- **Legacy/white-label hosts** (`aifasttrack.vercel.app`, `airport-fast-track.trip-sorted.com`, white-label portals) stay indexable until ARCH-009; they're out of scope for Sprint 1.

```env
# .env.local (add to .env.example too)
NEXT_PUBLIC_SITE_URL=https://travel-synch.com
```

The current production deployment serves `/en/*` on English. Task 1.0
(new — see below) flips `localePrefix` to `"as-needed"` and adds a permanent
301 from `/en/*` to `/*` so existing Google-indexed URLs don't break.

---

## 0 · Pre-flight — read before writing any code

```bash
cd /Users/srikan/Documents/GitHub/Sanjow/Sanjow-Ventures/fast-track-ai
cat AGENTS.md                # "This is NOT the Next.js you know"
cat CLAUDE.md 2>/dev/null
```

AGENTS.md warns that Next.js 16 has breaking API changes. Before touching
metadata/sitemap/robots APIs, consult the in-tree docs:

```bash
ls node_modules/next/dist/docs/ 2>/dev/null || ls node_modules/next/docs 2>/dev/null
find node_modules/next -path '*/docs/*' \( -name '*metadata*' -o -name '*sitemap*' -o -name '*robots*' \) 2>/dev/null
```

Confirm the current surface area you'll be touching:

```bash
cat src/app/layout.tsx
cat src/app/\[locale\]/layout.tsx
cat src/i18n/routing.ts
cat src/i18n/navigation.ts
cat public/robots.txt
find src/app/\[locale\] -maxdepth 3 -name 'page.tsx' | sort
```

Expected route inventory (8 locales × 10 public routes each):
`/`, `/how-it-works`, `/faq`, `/contact`, `/privacy`, `/terms`,
`/subscription-terms`, `/unsubscribe`, `/thankyou`, `/fast-track-form`.
Exclude from the sitemap: `/admin`, `/auth`, `/airport-scan`,
`/application`, `/checkout/*` (not indexable).

Create a feature branch:

```bash
git checkout -b seo/fast-track-sprint-1
```

---

## 1 · Shared config (do this once, reuse across all 5 tasks)

### 1a. `src/config/site.ts`

```ts
import { routing } from "@/i18n/routing";

export const SITE_URL =
  process.env.NEXT_PUBLIC_SITE_URL ?? "https://travel-synch.com";

export const SITE_NAME = "Trip Sorted — Fast Track";

export const DEFAULT_OG_IMAGE = "/og/fast-track-default.png"; // 1200×630, < 1MB

/** Routes that should appear in the sitemap + emit hreflang. */
export const INDEXABLE_ROUTES = [
  "",                       // homepage
  "/how-it-works",
  "/faq",
  "/contact",
  "/privacy",
  "/terms",
  "/subscription-terms",
] as const;

export type IndexableRoute = (typeof INDEXABLE_ROUTES)[number];

/** Build a canonical URL for a given locale + route. */
export function canonicalFor(locale: string, route: IndexableRoute): string {
  const localePrefix = locale === routing.defaultLocale ? "" : `/${locale}`;
  return `${SITE_URL}${localePrefix}${route}`;
}

/** Build the `alternates.languages` map for a given route. */
export function languageAlternatesFor(
  route: IndexableRoute,
): Record<string, string> {
  const map: Record<string, string> = {};
  for (const l of routing.locales) map[l] = canonicalFor(l, route);
  map["x-default"] = canonicalFor(routing.defaultLocale, route);
  return map;
}
```

### 1b. Update `src/app/layout.tsx` — add `metadataBase`

```ts
import type { Metadata } from "next";
import { SITE_URL, SITE_NAME } from "@/config/site";
import "./globals.css";

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: {
    default: `${SITE_NAME} | Airport Fast Track Access`,
    template: `%s | ${SITE_NAME}`,
  },
  description:
    "Skip the queue at 200+ airports worldwide. Fast Track security access, auto check-in, lounge discounts, and flight compensation.",
  icons: {
    icon: [{ url: "/favicon.ico", sizes: "32x32" }],
    apple: [{ url: "/apple-touch-icon.png", sizes: "180x180" }],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: { index: true, follow: true, "max-image-preview": "large" },
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return children;
}
```

Commit: `chore(seo): add metadataBase and robots defaults to root layout`

---

## 1.5 · Task 1.0 · Routing: `localePrefix: "as-needed"` + `/en/*` → `/*` 301s

**Priority:** P1 (prerequisite to every other task) · **Effort:** 1h · **Owner:** Frontend

This isn't a ticket in the audit — it's a prerequisite behaviour change that
every other SEO fix depends on. Without it, canonicals and hreflang will
point to `/faq` while the live URL is `/en/faq`, Google sees a redirect to
canonical instead of a self-reference, and the whole sprint degrades.

### Acceptance

- [ ] `src/i18n/routing.ts` explicitly declares `localePrefix: "as-needed"`
- [ ] `/en` returns 301 → `/`
- [ ] `/en/faq` returns 301 → `/faq` (and same for every other page)
- [ ] Non-default locales (`/fr/…`, `/es/…`, etc.) still return 200 directly
- [ ] GSC inspection of a previously-indexed `/en/…` URL shows "Page with redirect" pointing to canonical, not an error

### Step 1 — update `src/i18n/routing.ts`

```ts
import { defineRouting } from "next-intl/routing";

export const routing = defineRouting({
  locales: ["en", "fr", "pt", "es", "it", "de", "tr", "pl"],
  defaultLocale: "en",
  localePrefix: "as-needed", // ← add this line
});

export type Locale = (typeof routing.locales)[number];
```

### Step 2 — add permanent 301s in `next.config.ts`

next-intl's middleware handles the redirect, but its default is 307 (temporary).
For SEO we need explicit 301s so Google passes link equity. Add them in
`next.config.ts` BEFORE the next-intl wrapper applies — config-level redirects
run first:

```ts
import type { NextConfig } from "next";
import createNextIntlPlugin from "next-intl/plugin";

const withNextIntl = createNextIntlPlugin("./src/i18n/request.ts");

const nextConfig: NextConfig = {
  experimental: { esmExternals: true },
  async redirects() {
    return [
      { source: "/en",        destination: "/",        permanent: true },
      { source: "/en/:path*", destination: "/:path*",  permanent: true },
    ];
  },
};

export default withNextIntl(nextConfig);
```

> **Next 16 check:** confirm `redirects()` shape from
> `node_modules/next/dist/docs/` — the async function signature is stable,
> but `permanent: true` → HTTP 308 in some Next versions. 308 is semantically
> equivalent to 301 for Google, but if you want a strict 301, use
> `statusCode: 301` instead of `permanent: true`.

### Step 3 — verify

```bash
npm run dev &
sleep 5
for URL in /en /en/faq /en/how-it-works /fr/faq /es /; do
  echo "$URL → $(curl -s -o /dev/null -w '%{http_code} %{redirect_url}' http://localhost:3000$URL)"
done
kill %1
```

Expect:
- `/en` → 308 http://localhost:3000/
- `/en/faq` → 308 http://localhost:3000/faq
- `/en/how-it-works` → 308 http://localhost:3000/how-it-works
- `/fr/faq` → 200 (empty redirect_url)
- `/es` → 200
- `/` → 200

Commit: `feat(seo): localePrefix as-needed + 301 /en/* → /* (FAST_TRACK-PREREQ)`

> **Note:** this task isn't in `fix_seo_plans/fast_track.md` because the audit
> observed the site at its current `/en/*` state and generated tickets against
> that shape. Once this task ships + Sprint 1 lands + a re-audit runs, the
> audit will regenerate cleanly against the bare default locale.

---

## 2 · Task 1.1 · `FAST_TRACK-FIX-001` — sitemap.xml

**Priority:** P1 · **Effort:** 1h · **Lift:** +4 · **Owner:** Frontend

### Acceptance

- [ ] `/sitemap.xml` returns 200 with valid XML
- [ ] Every locale × every indexable route is listed
- [ ] `/robots.txt` references `/sitemap.xml` on the correct host

### File: `src/app/sitemap.ts`

```ts
import type { MetadataRoute } from "next";
import { routing } from "@/i18n/routing";
import { INDEXABLE_ROUTES, SITE_URL, canonicalFor } from "@/config/site";

export default function sitemap(): MetadataRoute.Sitemap {
  const now = new Date();

  return INDEXABLE_ROUTES.flatMap((route) =>
    routing.locales.map((locale) => ({
      url: canonicalFor(locale, route),
      lastModified: now,
      changeFrequency: route === "" ? "weekly" : "monthly",
      priority: route === "" ? 1.0 : 0.7,
      alternates: {
        languages: Object.fromEntries(
          routing.locales.map((l) => [l, canonicalFor(l, route)]),
        ),
      },
    })),
  );
}
```

> **Note for Next 16:** confirm `MetadataRoute.Sitemap` shape from
> `node_modules/next/dist/lib/metadata/types/metadata-interface.d.ts` —
> if `changeFrequency` or `alternates.languages` has moved, match the current type.

### File: `src/app/robots.ts` (replace the static `public/robots.txt`)

```ts
import type { MetadataRoute } from "next";
import { SITE_URL } from "@/config/site";

export default function robots(): MetadataRoute.Robots {
  return {
    rules: [
      { userAgent: "*", allow: "/", disallow: ["/admin", "/checkout", "/auth"] },
    ],
    sitemap: `${SITE_URL}/sitemap.xml`,
    host: SITE_URL,
  };
}
```

After this ships, **delete `public/robots.txt`** — the static file will shadow
the dynamic route. Verify with:

```bash
rm public/robots.txt
npm run dev
curl -s http://localhost:3000/robots.txt
curl -s http://localhost:3000/sitemap.xml | head -50
```

Commit: `feat(seo): add dynamic sitemap.xml and robots.txt (FAST_TRACK-FIX-001)`

---

## 3 · Task 1.2 · `FAST_TRACK-FIX-002` — canonical link

**Priority:** P1 · **Effort:** 30m · **Lift:** +3 · **Owner:** Frontend

### Acceptance

- [ ] Every indexable page emits a self-referential `<link rel="canonical">`
- [ ] Canonical URL uses the configured host and correct locale prefix

### Approach

`metadataBase` is already set in the root layout (Sprint step 1b), so
per-route `alternates.canonical` only needs the **path** — Next.js resolves it
against `metadataBase`. Do this per indexable page via `generateMetadata`.

### Pattern — apply to each page listed in `INDEXABLE_ROUTES`

For pages that already have a static `metadata` export, convert to
`generateMetadata`. Example for `src/app/[locale]/faq/page.tsx`:

```ts
import type { Metadata } from "next";
import { getTranslations, setRequestLocale } from "next-intl/server";
import {
  canonicalFor,
  languageAlternatesFor,
} from "@/config/site";
import type { Locale } from "@/i18n/routing";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: Locale }>;
}): Promise<Metadata> {
  const { locale } = await params;
  setRequestLocale(locale);
  const t = await getTranslations({ locale, namespace: "Faq.meta" });

  return {
    title: t("title"),
    description: t("description"),
    alternates: {
      canonical: canonicalFor(locale, "/faq"),
      languages: languageAlternatesFor("/faq"),
    },
  };
}
```

### Routes that need `generateMetadata` added (or updated)

| Route | Page file | Route key for `canonicalFor` |
|---|---|---|
| Homepage | `src/app/[locale]/page.tsx` | `""` |
| How it works | `src/app/[locale]/how-it-works/page.tsx` | `"/how-it-works"` |
| FAQ | `src/app/[locale]/faq/page.tsx` | `"/faq"` |
| Contact | `src/app/[locale]/contact/page.tsx` | `"/contact"` |
| Privacy | `src/app/[locale]/privacy/page.tsx` | `"/privacy"` |
| Terms | `src/app/[locale]/terms/page.tsx` | `"/terms"` |
| Subscription terms | `src/app/[locale]/subscription-terms/page.tsx` | `"/subscription-terms"` |

> **i18n messages:** add a `"meta"` key per page in each `messages/<locale>.json`
> (en first; use a placeholder like `"TODO: translate"` for the other 7 — Srikant
> will route translation through the standard next-intl flow). Don't block the
> PR on translation coverage.

Commit: `feat(seo): emit self-referential canonicals per locale (FAST_TRACK-FIX-002)`

---

## 4 · Task 1.3 · `FAST_TRACK-FIX-003` — hreflang coverage

**Priority:** P1 · **Effort:** 3h · **Lift:** +8 · **Owner:** Frontend

### Acceptance

- [ ] Every indexable page emits `<link rel="alternate" hreflang="…">` for all
      8 configured locales
- [ ] `x-default` hreflang is present and points to the default-locale URL
- [ ] Every hreflang URL returns 200 (no 301/302 chains)

### Approach

The `languageAlternatesFor(route)` helper (Sprint step 1a) already produces
the full map including `x-default`. Wire it into `alternates.languages` for
every indexable page — this is already in the template from Task 1.2.

### Verification — no redirect chains

Because the default locale (`en`) serves at the bare path (no `/en` prefix),
make sure `languageAlternatesFor` doesn't emit `/en/faq` when the live URL is
`/faq`. The helper in step 1a already handles this, but verify with:

```bash
npm run dev
for L in en fr pt es it de tr pl; do
  URL=$(curl -s "http://localhost:3000/$L/faq" -o /dev/null -w "%{http_code} %{url_effective}\n" -L)
  echo "$L -> $URL"
done
```

Every locale should return 200 on first hit — no 308/307/301.

### Edge case — default locale in next-intl

Confirm `routing.ts` `localePrefix` behaviour. If the project uses
`localePrefix: "always"` (not the default), the helper needs to emit `/en/…`
for `en` too. Read `src/i18n/routing.ts` and adjust `canonicalFor` accordingly
if that flag is set.

Commit: `feat(seo): emit hreflang + x-default for all locales (FAST_TRACK-FIX-003)`

---

## 5 · Task 1.4 · `FAST_TRACK-FIX-004` — Open Graph

**Priority:** P2 · **Effort:** 1h · **Lift:** +2 · **Owner:** Frontend

### Acceptance

- [ ] `og:title`, `og:description`, `og:image`, `og:url`, `og:type` all present
- [ ] `og:image` is ≥ 1200×630 and < 1MB
- [ ] Twitter card (`twitter:card`, `twitter:title`, `twitter:description`,
      `twitter:image`) also present

### File — add default OG image

Place a branded 1200×630 PNG at:

```
public/og/fast-track-default.png
```

If one doesn't exist yet, flag back to Srikant and use `/apple-touch-icon.png`
as a temporary fallback (Google will downgrade rich-result eligibility but the
tag will still validate). Do not block the PR.

### Pattern — extend the per-page `generateMetadata` from Task 1.2

```ts
import { DEFAULT_OG_IMAGE, SITE_NAME } from "@/config/site";

// inside generateMetadata, merge into the returned object:
openGraph: {
  type: "website",
  url: canonicalFor(locale, "/faq"),
  siteName: SITE_NAME,
  title: t("title"),
  description: t("description"),
  locale,
  images: [
    { url: DEFAULT_OG_IMAGE, width: 1200, height: 630, alt: t("title") },
  ],
},
twitter: {
  card: "summary_large_image",
  title: t("title"),
  description: t("description"),
  images: [DEFAULT_OG_IMAGE],
},
```

Do this for every page in the route table from Task 1.2.

### Verification

```bash
npm run dev
curl -s http://localhost:3000/faq | grep -E 'property="og:|name="twitter:'
```

Expect 9 matches (5 OG + 4 Twitter).

Commit: `feat(seo): emit full OG + Twitter card tags per route (FAST_TRACK-FIX-004)`

---

## 6 · Task 1.5 · `FAST_TRACK-FIX-005` — JSON-LD

**Priority:** P2 · **Effort:** 2h · **Lift:** +4 · **Owner:** Frontend

### Acceptance

- [ ] Relevant schema.org type(s) emitted as `application/ld+json`
- [ ] Google Rich Results Test passes on `/` and `/faq`

### Mapping — which schema per route

| Route | Schema |
|---|---|
| `/` (home) | `Organization` + `WebSite` (with `SearchAction` if site search exists — skip if not) |
| `/faq` | `FAQPage` — generate from the translated FAQ content |
| `/how-it-works` | `HowTo` with numbered steps |
| All other indexable routes | `Organization` only (inherited from layout) |

### File: `src/components/JsonLd.tsx` (new, shared)

```tsx
export function JsonLd({ data }: { data: unknown }) {
  return (
    <script
      type="application/ld+json"
      // biome-ignore lint/security/noDangerouslySetInnerHtml: schema.org payload
      dangerouslySetInnerHTML={{ __html: JSON.stringify(data) }}
    />
  );
}
```

### Homepage — inject Organization + WebSite schema

In `src/app/[locale]/page.tsx`, render at the top of the returned JSX:

```tsx
import { JsonLd } from "@/components/JsonLd";
import { SITE_URL, SITE_NAME } from "@/config/site";

const organization = {
  "@context": "https://schema.org",
  "@type": "Organization",
  name: SITE_NAME,
  url: SITE_URL,
  logo: `${SITE_URL}/apple-touch-icon.png`,
  sameAs: [
    // fill with Trustpilot / LinkedIn / social URLs if available, else omit
  ],
};

const website = {
  "@context": "https://schema.org",
  "@type": "WebSite",
  name: SITE_NAME,
  url: SITE_URL,
  inLanguage: ["en", "fr", "pt", "es", "it", "de", "tr", "pl"],
};

// …then in the component body:
<>
  <JsonLd data={organization} />
  <JsonLd data={website} />
  {/* existing page content */}
</>
```

### FAQ page — generate FAQPage schema from messages

```tsx
// src/app/[locale]/faq/page.tsx
import { getTranslations } from "next-intl/server";
import { JsonLd } from "@/components/JsonLd";

const t = await getTranslations({ locale, namespace: "Faq" });
const raw = t.raw("items"); // expect Array<{ q: string; a: string }>

const faqSchema = {
  "@context": "https://schema.org",
  "@type": "FAQPage",
  mainEntity: (raw as Array<{ q: string; a: string }>).map((x) => ({
    "@type": "Question",
    name: x.q,
    acceptedAnswer: { "@type": "Answer", text: x.a },
  })),
};

return (
  <>
    <JsonLd data={faqSchema} />
    {/* page content */}
  </>
);
```

> If the FAQ messages aren't shaped as an array of `{q, a}`, **do not reshape
> them in this PR** — note it in the PR description and ship Organization-only
> for `/faq`. Srikant will handle the content restructure separately.

### Verification

```bash
npm run dev
curl -s http://localhost:3000/ | grep -o 'application/ld+json'  # expect >=2
curl -s http://localhost:3000/faq | grep -o 'FAQPage'          # expect 1 (or 0 if skipped)
```

Then run the URL through Google's Rich Results Test:
<https://search.google.com/test/rich-results>

Commit: `feat(seo): inject schema.org JSON-LD per route (FAST_TRACK-FIX-005)`

---

## 7 · Verification gates (run after EVERY task, not just at the end)

Sanjow standard — no commit lands without all three passing:

```bash
npm run build
npm run lint
npx tsc --noEmit
```

If `biome` is the configured linter (check `package.json` scripts), use that
in place of `npm run lint`. Fix any new warnings introduced by your changes
before committing — do not mask them with `// biome-ignore` unless the warning
is unavoidable (e.g. the `dangerouslySetInnerHTML` in `JsonLd.tsx`).

### Additional per-task smoke tests

After Task 1.1 (sitemap/robots):
```bash
npm run dev &
sleep 5
curl -sf http://localhost:3000/sitemap.xml > /dev/null && echo "sitemap OK"
curl -sf http://localhost:3000/robots.txt | grep -q "Sitemap:" && echo "robots OK"
kill %1
```

After Tasks 1.2 / 1.3 (canonical + hreflang):
```bash
npm run dev &
sleep 5
for PATH_ in / /faq /how-it-works; do
  echo "=== $PATH_ ==="
  curl -s "http://localhost:3000$PATH_" \
    | grep -E 'rel="canonical"|rel="alternate"' \
    | head -12
done
kill %1
```

Expect: 1 canonical + 9 alternates (8 locales + x-default) per page.

After Task 1.4 (OG):
```bash
curl -s http://localhost:3000/faq | grep -cE 'property="og:|name="twitter:'
# expect >= 9
```

After Task 1.5 (JSON-LD):
```bash
curl -s http://localhost:3000/ | grep -c 'application/ld+json'
# expect >= 2 (Organization + WebSite)
```

---

## 8 · PR description template

Open the PR against `main` with this body:

```markdown
## FAST_TRACK SEO Sprint 1 — in-place fixes

Closes 5 tickets from `fix-seo-plans/fast_track.md` (plus one prerequisite):

- [x] FAST_TRACK-PREREQ — routing: `localePrefix: as-needed` + `/en/*` → `/*` 301s
- [x] FAST_TRACK-FIX-001 — sitemap.xml
- [x] FAST_TRACK-FIX-002 — canonical link
- [x] FAST_TRACK-FIX-003 — hreflang coverage
- [x] FAST_TRACK-FIX-004 — Open Graph
- [x] FAST_TRACK-FIX-005 — JSON-LD

Estimated lift: +21 audit points (baseline SEO 49.7, Perf 60.7).

### Decisions needed from @srikant before merge
- [x] Canonical host: `https://travel-synch.com` (confirmed 2026-04-21)
- [ ] Deploy env var `NEXT_PUBLIC_SITE_URL=https://travel-synch.com` set on
      Vercel production, preview, and dev envs.
- [ ] Post-merge: submit the new sitemap in Google Search Console for
      `travel-synch.com` property; monitor the `/en/*` → `/*` 301 report
      for 2 weeks to confirm no crawl errors.
- [ ] Provide branded OG image at `public/og/fast-track-default.png`
      (1200×630, <1MB). Using `apple-touch-icon.png` as fallback for now.
- [ ] Confirm FAQ messages shape — if not `Array<{q, a}>`, FAQPage schema
      is skipped and only Organization JSON-LD ships.

### Out of scope (follow-up sprints)
- FAST_TRACK-ARCH-006 — JS bundle code-split
- FAST_TRACK-ARCH-007 — image pipeline (next/image + AVIF/WebP)
- FAST_TRACK-ARCH-008 — hreflang middleware centralisation
- FAST_TRACK-ARCH-009 — legacy domain 301-migration

### Verification
- `npm run build` ✓
- `npm run lint` ✓
- `npx tsc --noEmit` ✓
- `/sitemap.xml` returns 200 with 56 URLs (8 locales × 7 routes)
- `/robots.txt` references `${SITE_URL}/sitemap.xml`
- Rich Results Test passes for `/` and `/faq`
```

---

## 9 · Marking tickets done in the portfolio board

After the PR merges to `main` and is deployed to the canonical host:

1. Open `design-system/audits/seo-pagespeed-audit/fix-seo-plans/portfolio.html`
2. Drag each of the 5 FIX tickets from "In progress" to "Done"
3. State persists in `localStorage` under `fix-plan:portfolio`

Alternatively, run the re-audit script — the portfolio regenerates but ticket
IDs stay deterministic so statuses survive:

```bash
cd design-system/audits/seo-pagespeed-audit
python scripts/run_audit.py --product fast_track
python scripts/build_portfolio_kanban.py
```

The re-run should show SEO score rising from 49.7 toward ~70. If a ticket's
acceptance criteria are met but the audit still flags it, re-read the audit's
heuristic for that field and adjust — the audit is the source of truth.

---

## 10 · Sprint 2+ — architectural tickets (NOT this sprint, planning notes only)

These four tickets each warrant their own spec + handoff prompt. Brief notes
so Srikant can sequence them:

### FAST_TRACK-ARCH-006 — Code-split and tree-shake JS bundle (P1, 1w, +20)

- Prerequisite: land Sprint 1 first so SEO metadata isn't blocked behind a
  big perf rewrite.
- Discovery step: run `ANALYZE=true npm run build` with `@next/bundle-analyzer`
  wired up; identify chunks > 150KB.
- Likely suspects in this stack: `@reduxjs/toolkit`, `recharts`/`d3-*`
  (admin dashboard only — should be dynamic-imported behind `/admin`),
  `@radix-ui/*` (tree-shake audit).
- Acceptance: first-load JS ≤ 350KB, no chunk > 150KB, mobile Lighthouse
  perf +15 points.

### FAST_TRACK-ARCH-007 — Image pipeline (P2, 3d, +10)

- Replace all `<img>` with `next/image` across `src/page-components/*` and
  `src/components/*`.
- Configure `next.config.ts` with `images.formats: ["image/avif", "image/webp"]`
  (verify API shape in Next 16 docs before writing).
- Add `width`/`height` to eliminate CLS; add `priority` to hero only.
- This ticket interacts with Sprint 1's OG image — both want the same asset
  pipeline, so do ARCH-007 before ordering bespoke OG art.

### FAST_TRACK-ARCH-008 — Centralise hreflang in middleware (P1, 4d, +12)

- Sprint 1 emits hreflang via per-page `generateMetadata` — correct for now
  but every new page has to remember the pattern.
- ARCH-008 moves the hreflang map into a single source (`src/config/site.ts`
  already nearly-there) and has middleware inject `<link>` tags at request
  time, so adding a locale is one config edit instead of N page edits.
- Depends on Sprint 1 landing first (middleware replaces the per-page pattern).

### FAST_TRACK-ARCH-009 — 301-migrate legacy `airport-fast-track.trip-sorted.com`

- **Biggest single SEO lever after Sprint 1.** Splitting link equity across
  two hosts is actively hurting rankings today.
- DevOps-owned (2w): URL-map every legacy path to the clean host, issue 301s
  (no 302, no chains), update canonicals on clean pages to self-reference,
  submit GSC change-of-address, keep legacy cert alive 12 months.
- Gate on canonical host decision (see open question at top of this doc).
- Success metric: clean-domain organic traffic ≥ 80% of legacy baseline
  within 90 days.

### Suggested sequence

1. **Sprint 1** (this doc) — 1 day
2. **ARCH-009** — as soon as canonical host is confirmed; unblocks the rest
3. **ARCH-008** — depends on Sprint 1, simplifies future locale work
4. **ARCH-006 + ARCH-007** — can run in parallel; both perf-focused, neither
   blocks SEO work

---

## 11 · If anything in this prompt is wrong for Next 16

This prompt was written against Next 16 + App Router as of April 2026, but
AGENTS.md explicitly warns the framework has breaking changes. If you hit an
API signature that doesn't match (e.g. `MetadataRoute.Sitemap` shape, `robots.ts`
return type, `alternates.languages` key), **stop and read `node_modules/next/dist/docs/`
for the correct current shape** rather than guessing. Flag the divergence in
the PR description so Srikant can update this prompt for the next sprint.
