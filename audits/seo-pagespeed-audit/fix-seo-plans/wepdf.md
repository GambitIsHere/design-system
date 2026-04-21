# WePDF — SEO + PageSpeed Fix Plan

_Generated 2026-04-21T08:07:24+00:00 · [audit report](../products/wepdf.md) · [dashboard](../products/wepdf.jsx)_

## Sprint summary

- **Total tickets:** 12 (7 in-place, 5 architectural)
- **By priority:** P0=1, P1=6, P2=5
- **By owner:** Content=1, DevOps=1, Frontend=10
- **Estimated total lift:** +107 score points (current: SEO 58.5, Perf 25.1)
- **Audit decision:** Option **B** — architectural workstreams included

## In-place fixes

### P1 — Should-fix

#### `WEPDF-FIX-001` — sitemap.xml — Generate a sitemap (Next.js app router supports `sitemap.ts`).

**Priority:** P1 · **Owner:** Frontend · **Effort:** 1h · **Est. lift:** +4 · **Area:** SEO · **Type:** fixable-in-place

**Problem**

Current: `missing`. Target: `valid XML sitemap at /sitemap.xml`.

**Fix**

Generate a sitemap (Next.js app router supports `sitemap.ts`).

**Affected**

  - `workspace.we-pdf.com`
  - `we-pdf.com`

**Acceptance criteria**

- [ ] `/sitemap.xml` returns 200 with valid XML
- [ ] Sitemap lists every locale route
- [ ] Sitemap referenced from `/robots.txt`

---

#### `WEPDF-FIX-002` — canonical link — Emit a self-referential `<link rel='canonical'>` via metadata.

**Priority:** P1 · **Owner:** Frontend · **Effort:** 30m · **Est. lift:** +3 · **Area:** SEO · **Type:** fixable-in-place

**Problem**

Current: `missing`. Target: `self-referential canonical`.

**Fix**

Emit a self-referential `<link rel='canonical'>` via metadata.

**Affected**

  - `we-pdf.com/en/`

**Acceptance criteria**

- [ ] Every indexable page emits a self-referential `<link rel="canonical">`
- [ ] Canonical URL uses the clean-domain host and correct locale

---

#### `WEPDF-FIX-003` — hreflang coverage — Emit hreflang for every locale route + x-default.

**Priority:** P1 · **Owner:** Frontend · **Effort:** 3h · **Est. lift:** +8 · **Area:** SEO · **Type:** fixable-in-place

**Problem**

Current: `0 of 10 locales`. Target: `10 hreflang tags + x-default`.

**Fix**

Emit hreflang for every locale route + x-default.

**Affected**

  - `we-pdf.com/en/`

**Acceptance criteria**

- [ ] All configured locales emit `<link rel="alternate" hreflang=...>`
- [ ] `x-default` hreflang is present
- [ ] Each hreflang URL returns 200 (no redirects)

---

### P2 — Nice-to-have

#### `WEPDF-FIX-004` — h1 count — Ensure exactly one h1 per route; demote duplicates to h2.

**Priority:** P2 · **Owner:** Frontend · **Effort:** 1h · **Est. lift:** +2 · **Area:** SEO · **Type:** fixable-in-place

**Problem**

Current: `0 h1 tags`. Target: `exactly 1 h1 per page`.

**Fix**

Ensure exactly one h1 per route; demote duplicates to h2.

**Affected**

  - `workspace.we-pdf.com/en/`
  - `we-pdf.com/en/`

**Acceptance criteria**

- [ ] Exactly one `<h1>` per page
- [ ] h1 text reflects the page's primary entity

---

#### `WEPDF-FIX-005` — Open Graph — Emit full OG tags via Next.js metadata.openGraph.

**Priority:** P2 · **Owner:** Frontend · **Effort:** 1h · **Est. lift:** +2 · **Area:** SEO · **Type:** fixable-in-place

**Problem**

Current: `incomplete`. Target: `og:title + og:description + og:image + og:url + og:type`.

**Fix**

Emit full OG tags via Next.js metadata.openGraph.

**Affected**

  - `workspace.we-pdf.com/en/`

**Acceptance criteria**

- [ ] og:title, og:description, og:image, og:url, og:type all present
- [ ] og:image is ≥ 1200×630 and < 1MB

---

#### `WEPDF-FIX-006` — JSON-LD — Inject JSON-LD for the page's primary entity type.

**Priority:** P2 · **Owner:** Frontend · **Effort:** 2h · **Est. lift:** +4 · **Area:** SEO · **Type:** fixable-in-place

**Problem**

Current: `none`. Target: `relevant schema.org types (Organization, WebSite, Product, FAQ)`.

**Fix**

Inject JSON-LD for the page's primary entity type.

**Affected**

  - `workspace.we-pdf.com/en/`
  - `we-pdf.com/en/`

**Acceptance criteria**

- [ ] Relevant schema.org type(s) emitted as application/ld+json
- [ ] Google Rich Results Test passes

---

#### `WEPDF-FIX-007` — <title> length — Tighten or expand the title to 30–60 characters.

**Priority:** P2 · **Owner:** Content · **Effort:** 30m · **Est. lift:** +2 · **Area:** SEO · **Type:** fixable-in-place

**Problem**

Current: `6 chars`. Target: `30–60 chars`.

**Fix**

Tighten or expand the title to 30–60 characters.

**Affected**

  - `we-pdf.com/en/`

**Acceptance criteria**

- [ ] `<title>` is 30–60 chars on all audited pages

---

## Architectural workstreams

_These tickets reflect the Option-B rebuild path. Each owns a multi-day workstream rather than a quick fix._

#### `WEPDF-ARCH-011` — Rewrite critical rendering path for mobile LCP

**Priority:** P0 · **Owner:** Frontend · **Effort:** 1w · **Est. lift:** +25 · **Area:** Perf · **Type:** architectural

**Problem**

Mobile Perf below 40 indicates blocking resources in the critical path. Targeted fixes alone won't clear the bar — needs an architectural pass.

**Fix**

Audit the critical chain: inline critical CSS, defer non-critical JS, preload LCP image/font, eliminate redirect chains on the landing URL, move to streaming SSR.

**Affected**

  - `workspace.we-pdf.com`

**Acceptance criteria**

- [ ] Mobile Lighthouse perf ≥ 70
- [ ] CrUX LCP p75 ≤ 2.5s (mobile)
- [ ] No redirect chain > 1 hop from primary landing URLs
- [ ] Critical CSS inlined ≤ 14KB

---

#### `WEPDF-ARCH-008` — Code-split and tree-shake the JS bundle

**Priority:** P1 · **Owner:** Frontend · **Effort:** 1w · **Est. lift:** +20 · **Area:** Perf · **Type:** architectural

**Problem**

Total JS NoneKB is above the 350KB budget. Unused JS ships on every page load and drags mobile Perf below 40.

**Fix**

Introduce route-level dynamic imports, audit heavy deps (replace or lazy-load), enable tree-shaking, split vendor chunks.

**Affected**

  - `workspace.we-pdf.com`

**Acceptance criteria**

- [ ] First-load JS for `/` route ≤ 350KB (transferred)
- [ ] No single chunk > 150KB
- [ ] Mobile Lighthouse perf improves by ≥ 15 points
- [ ] `Reduce unused JavaScript` Lighthouse audit drops below 50KB savings

---

#### `WEPDF-ARCH-010` — Rewrite locale routing to emit hreflang + x-default centrally

**Priority:** P1 · **Owner:** Frontend · **Effort:** 4d · **Est. lift:** +12 · **Area:** SEO · **Type:** architectural

**Problem**

Per-route hreflang scattershot across pages. An architectural fix centralises the map so adding a locale is a one-line change instead of N page edits.

**Fix**

Move locale detection + hreflang emission into Next.js middleware. Generate `<link rel=alternate>` for every locale route + x-default at build time from a single source.

**Affected**

  - `workspace.we-pdf.com`
  - `we-pdf.com`

**Acceptance criteria**

- [ ] All T1/T2 URLs emit hreflang tags for every configured locale + x-default
- [ ] Adding a new locale requires only a config entry
- [ ] Google Search Console `Hreflang` report shows 0 errors after 2 weeks

---

#### `WEPDF-ARCH-012` — 301-migrate and sunset legacy domain https://we-pdf.com

**Priority:** P1 · **Owner:** DevOps · **Effort:** 2w · **Est. lift:** +15 · **Area:** SEO · **Type:** architectural

**Problem**

Maintaining both https://we-pdf.com and https://workspace.we-pdf.com splits link equity and confuses canonicalisation. The audit supports consolidating onto the clean domain.

**Fix**

Map every legacy URL to its clean equivalent, issue 301s, update canonicals, submit change-of-address in Google Search Console, keep the legacy cert valid for 12 months post-cut.

**Affected**

  - `we-pdf.com`
  - `workspace.we-pdf.com`

**Acceptance criteria**

- [ ] All legacy URLs 301 to clean equivalents (no 302s, no chains)
- [ ] Canonicals on clean pages are self-referential
- [ ] GSC change-of-address submitted and accepted
- [ ] Organic traffic on clean domain ≥ 80% of legacy baseline within 90 days

---

#### `WEPDF-ARCH-009` — Migrate image pipeline to next/image with AVIF+WebP

**Priority:** P2 · **Owner:** Frontend · **Effort:** 3d · **Est. lift:** +10 · **Area:** Perf · **Type:** architectural

**Problem**

Images aren't served in modern formats, aren't lazy-loaded below the fold, and aren't responsively sized. LCP and CLS both suffer.

**Fix**

Replace <img> with next/image across the app. Configure next.config.js for AVIF+WebP, set width/height everywhere, add blur placeholders for hero images.

**Affected**

  - `workspace.we-pdf.com`

**Acceptance criteria**

- [ ] All product images use next/image
- [ ] Modern formats audit passes (≥ 90% AVIF/WebP)
- [ ] CLS p75 < 0.1 on all T1 URLs
- [ ] Hero LCP drops by ≥ 500ms on mobile

---

## How to use this plan

1. Copy each ticket into Linear / GitHub Issues — IDs stay stable across audit re-runs so you can cross-reference.
2. Track status on the kanban board: `fix-seo-plans/wepdf.html` (open in a browser — status persists in localStorage).
3. Re-run `python scripts/run_audit.py --product wepdf` after shipping — the plan regenerates but IDs remain deterministic so tickets you've already filed can be updated in-place.
