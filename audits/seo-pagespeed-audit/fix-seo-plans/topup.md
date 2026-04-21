# TopUp — SEO + PageSpeed Fix Plan

_Generated 2026-04-21T09:00:31+00:00 · [audit report](../products/topup.md) · [dashboard](../products/topup.jsx)_

## Sprint summary

- **Total tickets:** 15 (10 in-place, 5 architectural)
- **By priority:** P0=1, P1=9, P2=5
- **By owner:** Content=3, DevOps=1, Frontend=11
- **Estimated total lift:** +128 score points (current: SEO 15.7, Perf 11.8)
- **Audit decision:** Option **B** — architectural workstreams included

## In-place fixes

### P1 — Should-fix

#### `TOPUP-FIX-001` — canonical link — Emit a self-referential `<link rel='canonical'>` via metadata.

**Priority:** P1 · **Owner:** Frontend · **Effort:** 30m · **Est. lift:** +3 · **Area:** SEO · **Type:** fixable-in-place

**Problem**

Current: `missing`. Target: `self-referential canonical`.

**Fix**

Emit a self-referential `<link rel='canonical'>` via metadata.

**Affected**

  - `topup.com/`
  - `topup.com/fr/`
  - `new-topup.com/`
  - `new-topup.com/fr/`

**Acceptance criteria**

- [ ] Every indexable page emits a self-referential `<link rel="canonical">`
- [ ] Canonical URL uses the clean-domain host and correct locale

---

#### `TOPUP-FIX-002` — hreflang coverage — Emit hreflang for every locale route + x-default.

**Priority:** P1 · **Owner:** Frontend · **Effort:** 3h · **Est. lift:** +8 · **Area:** SEO · **Type:** fixable-in-place

**Problem**

Current: `0 of 2 locales`. Target: `2 hreflang tags + x-default`.

**Fix**

Emit hreflang for every locale route + x-default.

**Affected**

  - `topup.com/`
  - `topup.com/fr/`
  - `new-topup.com/`
  - `new-topup.com/fr/`

**Acceptance criteria**

- [ ] All configured locales emit `<link rel="alternate" hreflang=...>`
- [ ] `x-default` hreflang is present
- [ ] Each hreflang URL returns 200 (no redirects)

---

#### `TOPUP-FIX-003` — <title> — Add a page-level title via Next.js metadata.

**Priority:** P1 · **Owner:** Content · **Effort:** 1h · **Est. lift:** +5 · **Area:** SEO · **Type:** fixable-in-place

**Problem**

Current: `missing`. Target: `30–60 char unique title`.

**Fix**

Add a page-level title via Next.js metadata.

**Affected**

  - `topup.com/fr/`
  - `new-topup.com/`
  - `new-topup.com/fr/`

**Acceptance criteria**

- [ ] `<title>` is present and 30–60 chars
- [ ] Title is unique per route

---

#### `TOPUP-FIX-004` — meta description — Add a description via Next.js metadata.

**Priority:** P1 · **Owner:** Content · **Effort:** 1h · **Est. lift:** +4 · **Area:** SEO · **Type:** fixable-in-place

**Problem**

Current: `missing`. Target: `120–160 char unique description`.

**Fix**

Add a description via Next.js metadata.

**Affected**

  - `topup.com/fr/`
  - `new-topup.com/`
  - `new-topup.com/fr/`

**Acceptance criteria**

- [ ] `<meta name="description">` is present and 50–160 chars on every page
- [ ] Description is unique per route

---

#### `TOPUP-FIX-005` — mobile LCP p75 — Optimise LCP element (image preload, size, format).

**Priority:** P1 · **Owner:** Frontend · **Effort:** 1d · **Est. lift:** +12 · **Area:** Perf · **Type:** fixable-in-place

**Problem**

Current: `4397ms`. Target: `<2500ms`.

**Fix**

Optimise LCP element (image preload, size, format).

**Affected**

  - `topup.com/`

**Acceptance criteria**

- [ ] CrUX mobile LCP p75 ≤ 2.5s after 28-day window
- [ ] Lab LCP ≤ 2.5s on Lighthouse mobile run

---

#### `TOPUP-FIX-006` — sitemap.xml — Generate a sitemap (Next.js app router supports `sitemap.ts`).

**Priority:** P1 · **Owner:** Frontend · **Effort:** 1h · **Est. lift:** +4 · **Area:** SEO · **Type:** fixable-in-place

**Problem**

Current: `missing`. Target: `valid XML sitemap at /sitemap.xml`.

**Fix**

Generate a sitemap (Next.js app router supports `sitemap.ts`).

**Affected**

  - `new-topup.com`

**Acceptance criteria**

- [ ] `/sitemap.xml` returns 200 with valid XML
- [ ] Sitemap lists every locale route
- [ ] Sitemap referenced from `/robots.txt`

---

### P2 — Nice-to-have

#### `TOPUP-FIX-007` — <title> length — Tighten or expand the title to 30–60 characters.

**Priority:** P2 · **Owner:** Content · **Effort:** 30m · **Est. lift:** +2 · **Area:** SEO · **Type:** fixable-in-place

**Problem**

Current: `73 chars`. Target: `30–60 chars`.

**Fix**

Tighten or expand the title to 30–60 characters.

**Affected**

  - `topup.com/`

**Acceptance criteria**

- [ ] `<title>` is 30–60 chars on all audited pages

---

#### `TOPUP-FIX-008` — JSON-LD — Inject JSON-LD for the page's primary entity type.

**Priority:** P2 · **Owner:** Frontend · **Effort:** 2h · **Est. lift:** +4 · **Area:** SEO · **Type:** fixable-in-place

**Problem**

Current: `none`. Target: `relevant schema.org types (Organization, WebSite, Product, FAQ)`.

**Fix**

Inject JSON-LD for the page's primary entity type.

**Affected**

  - `topup.com/`
  - `topup.com/fr/`
  - `new-topup.com/`
  - `new-topup.com/fr/`

**Acceptance criteria**

- [ ] Relevant schema.org type(s) emitted as application/ld+json
- [ ] Google Rich Results Test passes

---

#### `TOPUP-FIX-009` — h1 count — Ensure exactly one h1 per route; demote duplicates to h2.

**Priority:** P2 · **Owner:** Frontend · **Effort:** 1h · **Est. lift:** +2 · **Area:** SEO · **Type:** fixable-in-place

**Problem**

Current: `0 h1 tags`. Target: `exactly 1 h1 per page`.

**Fix**

Ensure exactly one h1 per route; demote duplicates to h2.

**Affected**

  - `topup.com/fr/`
  - `new-topup.com/`
  - `new-topup.com/fr/`

**Acceptance criteria**

- [ ] Exactly one `<h1>` per page
- [ ] h1 text reflects the page's primary entity

---

#### `TOPUP-FIX-010` — Open Graph — Emit full OG tags via Next.js metadata.openGraph.

**Priority:** P2 · **Owner:** Frontend · **Effort:** 1h · **Est. lift:** +2 · **Area:** SEO · **Type:** fixable-in-place

**Problem**

Current: `incomplete`. Target: `og:title + og:description + og:image + og:url + og:type`.

**Fix**

Emit full OG tags via Next.js metadata.openGraph.

**Affected**

  - `topup.com/fr/`
  - `new-topup.com/`
  - `new-topup.com/fr/`

**Acceptance criteria**

- [ ] og:title, og:description, og:image, og:url, og:type all present
- [ ] og:image is ≥ 1200×630 and < 1MB

---

## Architectural workstreams

_These tickets reflect the Option-B rebuild path. Each owns a multi-day workstream rather than a quick fix._

#### `TOPUP-ARCH-014` — Rewrite critical rendering path for mobile LCP

**Priority:** P0 · **Owner:** Frontend · **Effort:** 1w · **Est. lift:** +25 · **Area:** Perf · **Type:** architectural

**Problem**

Mobile Perf below 40 indicates blocking resources in the critical path. Targeted fixes alone won't clear the bar — needs an architectural pass.

**Fix**

Audit the critical chain: inline critical CSS, defer non-critical JS, preload LCP image/font, eliminate redirect chains on the landing URL, move to streaming SSR.

**Affected**

  - `new-topup.com`

**Acceptance criteria**

- [ ] Mobile Lighthouse perf ≥ 70
- [ ] CrUX LCP p75 ≤ 2.5s (mobile)
- [ ] No redirect chain > 1 hop from primary landing URLs
- [ ] Critical CSS inlined ≤ 14KB

---

#### `TOPUP-ARCH-011` — Code-split and tree-shake the JS bundle

**Priority:** P1 · **Owner:** Frontend · **Effort:** 1w · **Est. lift:** +20 · **Area:** Perf · **Type:** architectural

**Problem**

Total JS NoneKB is above the 350KB budget. Unused JS ships on every page load and drags mobile Perf below 40.

**Fix**

Introduce route-level dynamic imports, audit heavy deps (replace or lazy-load), enable tree-shaking, split vendor chunks.

**Affected**

  - `new-topup.com`

**Acceptance criteria**

- [ ] First-load JS for `/` route ≤ 350KB (transferred)
- [ ] No single chunk > 150KB
- [ ] Mobile Lighthouse perf improves by ≥ 15 points
- [ ] `Reduce unused JavaScript` Lighthouse audit drops below 50KB savings

---

#### `TOPUP-ARCH-013` — Rewrite locale routing to emit hreflang + x-default centrally

**Priority:** P1 · **Owner:** Frontend · **Effort:** 4d · **Est. lift:** +12 · **Area:** SEO · **Type:** architectural

**Problem**

Per-route hreflang scattershot across pages. An architectural fix centralises the map so adding a locale is a one-line change instead of N page edits.

**Fix**

Move locale detection + hreflang emission into Next.js middleware. Generate `<link rel=alternate>` for every locale route + x-default at build time from a single source.

**Affected**

  - `topup.com`
  - `new-topup.com`

**Acceptance criteria**

- [ ] All T1/T2 URLs emit hreflang tags for every configured locale + x-default
- [ ] Adding a new locale requires only a config entry
- [ ] Google Search Console `Hreflang` report shows 0 errors after 2 weeks

---

#### `TOPUP-ARCH-015` — 301-migrate and sunset legacy domain https://topup.com

**Priority:** P1 · **Owner:** DevOps · **Effort:** 2w · **Est. lift:** +15 · **Area:** SEO · **Type:** architectural

**Problem**

Maintaining both https://topup.com and https://new-topup.com splits link equity and confuses canonicalisation. The audit supports consolidating onto the clean domain.

**Fix**

Map every legacy URL to its clean equivalent, issue 301s, update canonicals, submit change-of-address in Google Search Console, keep the legacy cert valid for 12 months post-cut.

**Affected**

  - `topup.com`
  - `new-topup.com`

**Acceptance criteria**

- [ ] All legacy URLs 301 to clean equivalents (no 302s, no chains)
- [ ] Canonicals on clean pages are self-referential
- [ ] GSC change-of-address submitted and accepted
- [ ] Organic traffic on clean domain ≥ 80% of legacy baseline within 90 days

---

#### `TOPUP-ARCH-012` — Migrate image pipeline to next/image with AVIF+WebP

**Priority:** P2 · **Owner:** Frontend · **Effort:** 3d · **Est. lift:** +10 · **Area:** Perf · **Type:** architectural

**Problem**

Images aren't served in modern formats, aren't lazy-loaded below the fold, and aren't responsively sized. LCP and CLS both suffer.

**Fix**

Replace <img> with next/image across the app. Configure next.config.js for AVIF+WebP, set width/height everywhere, add blur placeholders for hero images.

**Affected**

  - `new-topup.com`

**Acceptance criteria**

- [ ] All product images use next/image
- [ ] Modern formats audit passes (≥ 90% AVIF/WebP)
- [ ] CLS p75 < 0.1 on all T1 URLs
- [ ] Hero LCP drops by ≥ 500ms on mobile

---

## How to use this plan

1. Copy each ticket into Linear / GitHub Issues — IDs stay stable across audit re-runs so you can cross-reference.
2. Track status on the kanban board: `fix-seo-plans/topup.html` (open in a browser — status persists in localStorage).
3. Re-run `python scripts/run_audit.py --product topup` after shipping — the plan regenerates but IDs remain deterministic so tickets you've already filed can be updated in-place.
