# Airport Check-in — SEO + PageSpeed Audit

_Run 20260421T085944+0000 · 8 URLs · 2 domain(s) · 2 locale(s)_

## Executive summary

- **Headline:** Airport Check-in scores **SEO 40.2** (weak) and **Perf 60.5** (ok). Audit supports **Option B**.
- **Findings:** 0 P0 (must-fix), 10 P1 (should-fix). 0 architectural vs 22 fixable-in-place.
- **Clean vs legacy:** `aicheckin.vercel.app` Lighthouse perf 71 vs `direct-check-in.my-trip-online.com` 85. This delta is the central input to the Option-B decision.

## Decision: Option **B**

Triggered by:
- SEOScore<50 on legacy domain → strong Option B candidate
- Hreflang errors across locales → multi-locale EU traffic bleed

_See dashboard for full reasoning · `products/airport_checkin.jsx`_

## Clean vs Legacy snapshot

| Metric | Clean (`aicheckin.vercel.app`) | Legacy (`direct-check-in.my-trip-online.com`) |
|---|---|---|
| Lighthouse perf (mobile, avg) | 62 | 90 |
| Lighthouse perf (desktop, avg) | 80 | 80 |
| Lighthouse SEO (avg) | 100 | 100 |
| CrUX LCP p75 | — | — |
| CrUX CLS p75 | — | — |
| JS bundle (mobile, KB) | 683 | 674 |
| Composite SEOScore | 40.2 | 40.2 |
| Composite PerfScore | 48.5 | 72.6 |

## Next steps (this sprint)

1. **hreflang coverage — Emit hreflang for every locale route + x-default.** _(Frontend · 3h · +8 score lift est.)_  
   Affects `aicheckin.vercel.app/`. Currently `0 of 8 locales`, target `8 hreflang tags + x-default`.
2. **sitemap.xml — Generate a sitemap (Next.js app router supports `sitemap.ts`).** _(Frontend · 1h · +4 score lift est.)_  
   Affects `aicheckin.vercel.app`. Currently `missing`, target `valid XML sitemap at /sitemap.xml`.
3. **canonical link — Emit a self-referential `<link rel='canonical'>` via metadata.** _(Frontend · 30m · +3 score lift est.)_  
   Affects `aicheckin.vercel.app/`. Currently `missing`, target `self-referential canonical`.

## Where the data lives

- **Interactive dashboard** — `products/airport_checkin.jsx` (open as a React artifact for filters + charts)
- **Raw PSI JSON** — `data/psi-raw/airport_checkin/`
- **HTML audit** — `data/html-audit/airport_checkin-*.json`
- **Scoring CSV** — `data/scores.csv` (filter by product=airport_checkin)
- **Audit date** — 2026-04-21T08:59:44+00:00
