# Fast Track — SEO + PageSpeed Audit

_Run 20260421T090017+0000 · 8 URLs · 2 domain(s) · 2 locale(s)_

## Executive summary

- **Headline:** Fast Track scores **SEO 49.7** (weak) and **Perf 60.7** (ok). Audit supports **Option B**.
- **Findings:** 0 P0 (must-fix), 10 P1 (should-fix). 0 architectural vs 18 fixable-in-place.
- **Clean vs legacy:** `aifasttrack.vercel.app` Lighthouse perf 79 vs `airport-fast-track.trip-sorted.com` 69. This delta is the central input to the Option-B decision.

## Decision: Option **B**

Triggered by:
- SEOScore<50 on legacy domain → strong Option B candidate
- Hreflang errors across locales → multi-locale EU traffic bleed

_See dashboard for full reasoning · `products/fast_track.jsx`_

## Clean vs Legacy snapshot

| Metric | Clean (`aifasttrack.vercel.app`) | Legacy (`airport-fast-track.trip-sorted.com`) |
|---|---|---|
| Lighthouse perf (mobile, avg) | 70 | 68 |
| Lighthouse perf (desktop, avg) | 88 | 71 |
| Lighthouse SEO (avg) | 100 | 100 |
| CrUX LCP p75 | — | 1738ms |
| CrUX CLS p75 | — | 0.00 |
| JS bundle (mobile, KB) | 775 | 1030 |
| Composite SEOScore | 46.5 | 52.8 |
| Composite PerfScore | 58.2 | 63.3 |

## Next steps (this sprint)

1. **hreflang coverage — Emit hreflang for every locale route + x-default.** _(Frontend · 3h · +8 score lift est.)_  
   Affects `aifasttrack.vercel.app/`. Currently `0 of 8 locales`, target `8 hreflang tags + x-default`.
2. **sitemap.xml — Generate a sitemap (Next.js app router supports `sitemap.ts`).** _(Frontend · 1h · +4 score lift est.)_  
   Affects `aifasttrack.vercel.app`. Currently `missing`, target `valid XML sitemap at /sitemap.xml`.
3. **canonical link — Emit a self-referential `<link rel='canonical'>` via metadata.** _(Frontend · 30m · +3 score lift est.)_  
   Affects `aifasttrack.vercel.app/`. Currently `missing`, target `self-referential canonical`.

## Where the data lives

- **Interactive dashboard** — `products/fast_track.jsx` (open as a React artifact for filters + charts)
- **Raw PSI JSON** — `data/psi-raw/fast_track/`
- **HTML audit** — `data/html-audit/fast_track-*.json`
- **Scoring CSV** — `data/scores.csv` (filter by product=fast_track)
- **Audit date** — 2026-04-21T09:00:17+00:00
