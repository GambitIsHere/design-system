# Fast Track — SEO + PageSpeed Fix Plan

_Generated 2026-04-21T09:00:17+00:00 · [audit report](../products/fast_track.md) · [dashboard](../products/fast_track.jsx)_

## Sprint summary

- **Total tickets:** 9 (5 in-place, 4 architectural)
- **By priority:** P0=0, P1=6, P2=3
- **By owner:** DevOps=1, Frontend=8
- **Estimated total lift:** +78 score points (current: SEO 49.7, Perf 60.7)
- **Audit decision:** Option **B** — architectural workstreams included

## In-place fixes

### P1 — Should-fix

#### `FAST_TRACK-FIX-001` — sitemap.xml — Generate a sitemap (Next.js app router supports `sitemap.ts`).

**Priority:** P1 · **Owner:** Frontend · **Effort:** 1h · **Est. lift:** +4 · **Area:** SEO · **Type:** fixable-in-place

**Problem**

Current: `missing`. Target: `valid XML sitemap at /sitemap.xml`.

**Fix**

Generate a sitemap (Next.js app router supports `sitemap.ts`).

**Affected**

  - `aifasttrack.vercel.app`
  - `airport-fast-track.trip-sorted.com`

**Acceptance criteria**

- [ ] `/sitemap.xml` returns 200 with valid XML
- [ ] Sitemap lists every locale route
- [ ] Sitemap referenced from `/robots.txt`

---

#### `FAST_TRACK-FIX-002` — canonical link — Emit a self-referential `<link rel='canonical'>` via metadata.

**Priority:** P1 · **Owner:** Frontend · **Effort:** 30m · **Est. lift:** +3 · **Area:** SEO · **Type:** fixable-in-place

**Problem**

Current: `missing`. Target: `self-referential canonical`.

**Fix**

Emit a self-referential `<link rel='canonical'>` via metadata.

**Affected**

  - `aifasttrack.vercel.app/`
  - `aifasttrack.vercel.app/fr/`
  - `airport-fast-track.trip-sorted.com/`
  - `airport-fast-track.trip-sorted.com/fr/`

**Acceptance criteria**

- [ ] Every indexable page emits a self-referential `<link rel="canonical">`
- [ ] Canonical URL uses the clean-domain host and correct locale

---

#### `FAST_TRACK-FIX-003` — hreflang coverage — Emit hreflang for every locale route + x-default.

**Priority:** P1 · **Owner:** Frontend · **Effort:** 3h · **Est. lift:** +8 · **Area:** SEO · **Type:** fixable-in-place

**Problem**

Current: `0 of 8 locales`. Target: `8 hreflang tags + x-default`.

**Fix**

Emit hreflang for every locale route + x-default.

**Affected**

  - `aifasttrack.vercel.app/`
  - `aifasttrack.vercel.app/fr/`
  - `airport-fast-track.trip-sorted.com/`
  - `airport-fast-track.trip-sorted.com/fr/`

**Acceptance criteria**

- [ ] All configured locales emit `<link rel="alternate" hreflang=...>`
- [ ] `x-default` hreflang is present
- [ ] Each hreflang URL returns 200 (no redirects)

---

### P2 — Nice-to-have

#### `FAST_TRACK-FIX-004` — Open Graph — Emit full OG tags via Next.js metadata.openGraph.

**Priority:** P2 · **Owner:** Frontend · **Effort:** 1h · **Est. lift:** +2 · **Area:** SEO · **Type:** fixable-in-place

**Problem**

Current: `incomplete`. Target: `og:title + og:description + og:image + og:url + og:type`.

**Fix**

Emit full OG tags via Next.js metadata.openGraph.

**Affected**

  - `aifasttrack.vercel.app/`
  - `aifasttrack.vercel.app/fr/`
  - `airport-fast-track.trip-sorted.com/`
  - `airport-fast-track.trip-sorted.com/fr/`

**Acceptance criteria**

- [ ] og:title, og:description, og:image, og:url, og:type all present
- [ ] og:image is ≥ 1200×630 and < 1MB

---

#### `FAST_TRACK-FIX-005` — JSON-LD — Inject JSON-LD for the page's primary entity type.

**Priority:** P2 · **Owner:** Frontend · **Effort:** 2h · **Est. lift:** +4 · **Area:** SEO · **Type:** fixable-in-place

**Problem**

Current: `none`. Target: `relevant schema.org types (Organization, WebSite, Product, FAQ)`.

**Fix**

Inject JSON-LD for the page's primary entity type.

**Affected**

  - `aifasttrack.vercel.app/`
  - `aifasttrack.vercel.app/fr/`
  - `airport-fast-track.trip-sorted.com/`
  - `airport-fast-track.trip-sorted.com/fr/`

**Acceptance criteria**

- [ ] Relevant schema.org type(s) emitted as application/ld+json
- [ ] Google Rich Results Test passes

---

## Architectural workstreams

_These tickets reflect the Option-B rebuild path. Each owns a multi-day workstream rather than a quick fix._

#### `FAST_TRACK-ARCH-006` — Code-split and tree-shake the JS bundle

**Priority:** P1 · **Owner:** Frontend · **Effort:** 1w · **Est. lift:** +20 · **Area:** Perf · **Type:** architectural

**Problem**

Total JS NoneKB is above the 350KB budget. Unused JS ships on every page load and drags mobile Perf below 40.

**Fix**

Introduce route-level dynamic imports, audit heavy deps (replace or lazy-load), enable tree-shaking, split vendor chunks.

**Affected**

  - `aifasttrack.vercel.app`

**Acceptance criteria**

- [ ] First-load JS for `/` route ≤ 350KB (transferred)
- [ ] No single chunk > 150KB
- [ ] Mobile Lighthouse perf improves by ≥ 15 points
- [ ] `Reduce unused JavaScript` Lighthouse audit drops below 50KB savings

---

#### `FAST_TRACK-ARCH-008` — Rewrite locale routing to emit hreflang + x-default centrally

**Priority:** P1 · **Owner:** Frontend · **Effort:** 4d · **Est. lift:** +12 · **Area:** SEO · **Type:** architectural

**Problem**

Per-route hreflang scattershot across pages. An architectural fix centralises the map so adding a locale is a one-line change instead of N page edits.

**Fix**

Move locale detection + hreflang emission into Next.js middleware. Generate `<link rel=alternate>` for every locale route + x-default at build time from a single source.

**Affected**

  - `aifasttrack.vercel.app`
  - `airport-fast-track.trip-sorted.com`

**Acceptance criteria**

- [ ] All T1/T2 URLs emit hreflang tags for every configured locale + x-default
- [ ] Adding a new locale requires only a config entry
- [ ] Google Search Console `Hreflang` report shows 0 errors after 2 weeks

---

#### `FAST_TRACK-ARCH-009` — 301-migrate and sunset legacy domain https://airport-fast-track.trip-sorted.com

**Priority:** P1 · **Owner:** DevOps · **Effort:** 2w · **Est. lift:** +15 · **Area:** SEO · **Type:** architectural

**Problem**

Maintaining both https://airport-fast-track.trip-sorted.com and https://aifasttrack.vercel.app splits link equity and confuses canonicalisation. The audit supports consolidating onto the clean domain.

**Fix**

Map every legacy URL to its clean equivalent, issue 301s, update canonicals, submit change-of-address in Google Search Console, keep the legacy cert valid for 12 months post-cut.

**Affected**

  - `airport-fast-track.trip-sorted.com`
  - `aifasttrack.vercel.app`

**Acceptance criteria**

- [ ] All legacy URLs 301 to clean equivalents (no 302s, no chains)
- [ ] Canonicals on clean pages are self-referential
- [ ] GSC change-of-address submitted and accepted
- [ ] Organic traffic on clean domain ≥ 80% of legacy baseline within 90 days

---

#### `FAST_TRACK-ARCH-007` — Migrate image pipeline to next/image with AVIF+WebP

**Priority:** P2 · **Owner:** Frontend · **Effort:** 3d · **Est. lift:** +10 · **Area:** Perf · **Type:** architectural

**Problem**

Images aren't served in modern formats, aren't lazy-loaded below the fold, and aren't responsively sized. LCP and CLS both suffer.

**Fix**

Replace <img> with next/image across the app. Configure next.config.js for AVIF+WebP, set width/height everywhere, add blur placeholders for hero images.

**Affected**

  - `aifasttrack.vercel.app`

**Acceptance criteria**

- [ ] All product images use next/image
- [ ] Modern formats audit passes (≥ 90% AVIF/WebP)
- [ ] CLS p75 < 0.1 on all T1 URLs
- [ ] Hero LCP drops by ≥ 500ms on mobile

---

## How to use this plan

1. Copy each ticket into Linear / GitHub Issues — IDs stay stable across audit re-runs so you can cross-reference.
2. Track status on the kanban board: `fix-seo-plans/fast_track.html` (open in a browser — status persists in localStorage).
3. Re-run `python scripts/run_audit.py --product fast_track` after shipping — the plan regenerates but IDs remain deterministic so tickets you've already filed can be updated in-place.
