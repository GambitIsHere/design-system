# VISA_PORTALS — SEO Audit Fix Handoff

**Branch:** `seo/visa-portals-audit-fixes` in `Sanjow-Ventures/global-visa-portal`
**Base audit:** 2026-04-22, SEO 49.2 / Perf 49.2
**Scope:** Option B — all fixes possible in the code

## What shipped

| Ticket | Status | Files touched |
|---|---|---|
| FIX-001 sitemap.xml | ✅ | `public/sitemap.xml` (new), `public/robots.txt` (sitemap + disallows for private routes) |
| FIX-002 canonical | ✅ | `src/components/seo/SEO.tsx` (new), `src/lib/seo-config.ts` (new), wired into all public pages |
| FIX-003 hreflang + x-default | ✅ with caveat | Emitted via `<SEO>` on every public route. **Only `en` + `x-default` since no `/fr` routes exist in the clean repo.** |
| FIX-004 one h1 per route | ✅ no-op | Audited — every public page has exactly one h1. The audit's "0 h1" finding is the SPA/SSR problem (see below), not a DOM issue. |
| FIX-005 JSON-LD | ✅ | `Organization` + `WebSite` on `/`, `Service` + `FAQPage` on country landings, `FAQPage` on `/faq`, `ContactPage` on `/contact`, `Organization` on `/about` |
| ARCH-006 bundle split | ✅ | `src/App.tsx` — all routes except `/` and `NotFound` are now `React.lazy` with `<Suspense>` fallback. `vite.config.ts` — manual vendor chunks for react/radix/supabase/forms. |
| ARCH-007 image pipeline | ✅ partial | Added `width`/`height`/`loading="lazy"`/`decoding="async"` to public `<img>` in `Header.tsx`, `DestinationsSection.tsx`, `SafeJourneySection.tsx`. Header logos get `fetchPriority="high"`. **Not done:** AVIF/WebP conversion, responsive `srcset` — needs `vite-imagetools` or equivalent (see follow-up). |
| ARCH-008 locale middleware | ⛔ blocked | Repo has zero French translations or `/fr` routes. Can't ship locale routing without content. See blocker below. |
| ARCH-009 301-migrate legacy | ⛔ out of scope | DevOps + Google Search Console work, not a code change. See runbook below. |
| ARCH-010 static prerender (new) | ✅ | `scripts/prerender.mjs` + `postbuild` runs Playwright against a local static server and writes per-route `<route>/index.html`. 20 routes prerendered. `vercel.json` updated to serve static files first (`cleanUrls`, filtered rewrite). JS-less crawlers now see full title / h1 / canonical / hreflang / JSON-LD for every indexable route. |

**Bundle impact** (homepage `/` first load, gzipped):
- Before: `index` + `react-vendor` + `radix-vendor` + `charts` preloaded (~252 KB gzip)
- After: `index` + `react-vendor` + `radix-vendor` only (**~148 KB gzip**), Supabase/forms/charts deferred to routes that need them

## SPA empty-shell problem — resolved via static prerendering (ARCH-010)

Previously every route returned the same `index.html` shell, so JS-less crawlers (social-card scrapers, LLM bots, older SEO tools, the audit itself) saw nothing meaningful. Fixed by a Playwright-based prerender step.

**How it works**
- `scripts/prerender.mjs` runs as `postbuild`. After `vite build`, it:
  1. Boots a tiny static HTTP server against `dist/`.
  2. Launches headless Chromium (from the already-present `@playwright/test` devDep — no new runtime deps).
  3. Visits each route in the include list, waits for `networkidle` + 200ms, snapshots `document.documentElement.outerHTML`.
  4. Writes `dist/<route>/index.html` for each route. `/` overwrites `dist/index.html`.
- `main.tsx` uses `hydrateRoot` when `#root` already has children (prerendered), otherwise `createRoot` (direct visit to a non-prerendered route).
- `vercel.json` is updated: `cleanUrls: true` + rewrite pattern `/((?!.*\\.).*)` → `/index.html`. Vercel's filesystem resolution runs before rewrites, so `/about` serves `dist/about/index.html`; `/application` falls through to the SPA shell.

**Routes prerendered (20):** `/`, `/about`, `/faq`, `/contact`, `/terms`, `/privacy`, `/legal-disclaimer`, plus all 13 country landings. Edit the `ROUTES` array in `scripts/prerender.mjs` to add more.

**Dynamic routes (`/:country` fallback, `/application`, admin, portal)** are not prerendered. They serve the SPA shell, which is correct — `robots.txt` blocks admin/portal/application, and every indexable country path is already in the prerender list.

**Verification (what a JS-less curl sees):**
```
GET /canada/ →
  <title>Canada eTA — Apply Online | Online Visas</title>
  <link rel="canonical" href="https://global-visa-portal.vercel.app/canada" data-rh="true">
  <h1>Apply for your Canada Electronic Travel Authorization (eTA)</h1>
  + Service + FAQPage JSON-LD + hreflang + OG/Twitter
```

**Build cost:** ~6–10 seconds added to `npm run build` (one Chromium launch, 20 route visits).

**Known quirks:**
- `vite preview` (the CLI command) rewrites every path to `index.html` regardless of filesystem. It's useless for testing prerender output. Use `python3 -m http.server 7123 --directory dist` or any filesystem-first server to verify locally. Vercel behaves correctly in prod.
- On a CI box with no browser cache, the first prerender run must also run `npx playwright install chromium` (~90 MB download, one-time).

**If a Next.js migration later becomes attractive** for other reasons (proper SSR, image pipeline, middleware-based i18n), this prerender layer becomes redundant and can be removed in one commit.

## Blocker: ARCH-008 locale routing needs content first

The audit hit `/fr/` on both `global-visa-portal.vercel.app` and `online-visas.com` and treated them as real locale routes, but **no `/fr` path exists in the clean repo's `App.tsx`**. `date-fns/locale` imports of `fr` are only for admin-side date formatting, not UI translation. Shipping `<link rel="alternate" hreflang="fr">` today would point crawlers at URLs that don't exist.

**Blocker:** need translated FR content for every public page before wiring locale routes. Options:

- Deliver FR copy for Index, each country landing, AboutUs, FAQ, Contact, Terms, Privacy, LegalDisclaimer.
- Introduce `react-i18next` or similar, add `/:locale?` param to routes, expand `SUPPORTED_LOCALES` in `src/lib/seo-config.ts`.
- Update sitemap.xml to list every locale × route combination.
- Update `<SEO>` component to emit the full hreflang map (already supports the loop — just needs the locale list).

## Runbook: ARCH-009 301-migrate legacy

Code-side prerequisites are already done on the clean side (self-ref canonicals, sitemap, robots). The actual migration is DevOps + Search Console:

1. **Inventory legacy URLs** on `online-visas.com`. Map each one to its clean-domain equivalent.
2. **Vercel / upstream proxy**: configure 301s. In `vercel.json` for the legacy deployment (not this repo), add `redirects` entries. Verify no redirect chains.
3. **Canonical swap**: on the legacy deployment, canonicals should point to the clean domain. On clean, canonicals are self-referential (already done).
4. **Submit change-of-address** in Google Search Console from the legacy property to the clean property.
5. **Keep legacy cert + domain live** for at least 12 months post-cut.
6. **Monitor** organic traffic on both sides for 90 days.

The legacy repo (`Sanjow-Ventures/online-visa`) is effectively empty — just `CODEOWNERS`. Wherever the legacy site is actually deployed from is where the redirect config needs to land.

## Follow-ups (not on the original ticket list but worth doing)

1. **`og-default.png`** — referenced in `<SEO>` but **does not exist yet**. Drop a 1200×630 PNG at `public/og-default.png`. Until then social cards will 404.
3. **`VITE_SITE_URL`** — `src/lib/seo-config.ts` reads this env var and falls back to `https://global-visa-portal.vercel.app`. If you want the SEO canonicals/sitemap URLs to pin to the real clean domain (e.g., a bare `online-visas.com` after migration), set `VITE_SITE_URL` at build time on Vercel and update `public/sitemap.xml` + `public/robots.txt` accordingly.
4. **AVIF/WebP + responsive images** — install `vite-imagetools`. Replace raw `<img src={travelerImg}>` with query-param imports (`import img from './x.jpg?w=400;800;1200&format=avif;webp;jpg&as=srcset'`). Gives next/image-level results without a framework migration.
5. **`noindex` on transactional pages** — robots.txt blocks crawl, but adding `<meta name="robots" content="noindex">` via `<SEO noindex />` on `/application`, `/payment-success`, `/thank-you`, `/complete-info/*`, `/*-additional-info` is belt-and-suspenders. The component already supports it — just pass `noindex` to the `<SEO>` element. Currently only set on `/new-zealand-v2` (A/B duplicate).
6. **Organization `sameAs`** — `organizationJsonLd` in `SEO.tsx` has an empty `sameAs: []`. Fill in social profile URLs (LinkedIn, Twitter/X, Facebook) to help Google build the Knowledge Graph entry.
7. **Sitemap + prerender include list automation** — `public/sitemap.xml` and the `ROUTES` array in `scripts/prerender.mjs` both hard-code country slugs. If country slugs change in `src/lib/landing-config.ts`, both drift. A tiny `scripts/generate-routes.ts` run as a `prebuild` step could read `landing-config.ts`, emit `public/sitemap.xml`, and write a JSON file that `prerender.mjs` imports.

## How to verify

```bash
cd /Users/srikan/Documents/GitHub/Sanjow/Sanjow-Ventures/global-visa-portal
npm run build
npm run preview
# then in another terminal:
curl -s http://localhost:4173/sitemap.xml | head -20
curl -s http://localhost:4173/robots.txt
curl -s http://localhost:4173/ | grep -E 'canonical|og:|twitter:|<title>'
```

To see the React-helmet-injected tags (which is what the audit needs to see for most of the SEO points), you need a JS-rendering fetch — Googlebot-style. Use Google's Rich Results Test or the Mobile-Friendly Test against a deployed preview URL; those both render JS before checking.

After deploying this branch to Vercel preview, re-run the audit:

```bash
cd /Users/srikan/Documents/GitHub/Sanjow/Sanjow-Ventures/design-system/audits/seo-pagespeed-audit
python3 scripts/run_audit.py --product visa_portals
```

Expected improvement once deployed: large jump on canonical/hreflang/JSON-LD/sitemap axes. Perf jump modest (bundle split) unless the prerendering follow-up also ships, which would also lift LCP materially.
