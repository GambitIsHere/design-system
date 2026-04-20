# WePDF — SEO + PageSpeed Audit

_Run 20260420T162940+0000 · 4 URLs · 2 domain(s) · 1 locale(s)_

## Executive summary

- **Headline:** WePDF scores **SEO 58.5** (weak) and **Perf 25.1** (critical). Audit supports **Option B**.
- **Findings:** 0 P0 (must-fix), 4 P1 (should-fix). 0 architectural vs 10 fixable-in-place.
- **Clean vs legacy:** `workspace.we-pdf.com` Lighthouse perf 59 vs `we-pdf.com` 70. This delta is the central input to the Option-B decision.

## Decision: Option **B**

Triggered by:
- PerfScore<40 on mobile-heavy traffic → strong Option B candidate
- Hreflang errors across locales → multi-locale EU traffic bleed

_See dashboard for full reasoning · `products/wepdf.jsx`_

## Clean vs Legacy snapshot

| Metric | Clean (`workspace.we-pdf.com`) | Legacy (`we-pdf.com`) |
|---|---|---|
| Lighthouse perf (mobile, avg) | 55 | — |
| Lighthouse perf (desktop, avg) | 63 | 70 |
| Lighthouse SEO (avg) | 92 | 100 |
| CrUX LCP p75 | — | 1871ms |
| CrUX CLS p75 | — | 0.05 |
| JS bundle (mobile, KB) | 1094 | — |
| Composite SEOScore | 65.2 | 51.8 |
| Composite PerfScore | 28.3 | 22.0 |

## Next steps (this sprint)

1. **hreflang coverage — Emit hreflang for every locale route + x-default.** _(Frontend · 3h · +8 score lift est.)_  
   Affects `we-pdf.com/en/`. Currently `0 of 10 locales`, target `10 hreflang tags + x-default`.
2. **sitemap.xml — Generate a sitemap (Next.js app router supports `sitemap.ts`).** _(Frontend · 1h · +4 score lift est.)_  
   Affects `workspace.we-pdf.com`. Currently `missing`, target `valid XML sitemap at /sitemap.xml`.
3. **canonical link — Emit a self-referential `<link rel='canonical'>` via metadata.** _(Frontend · 30m · +3 score lift est.)_  
   Affects `we-pdf.com/en/`. Currently `missing`, target `self-referential canonical`.

## Where the data lives

- **Interactive dashboard** — `products/wepdf.jsx` (open as a React artifact for filters + charts)
- **Raw PSI JSON** — `data/psi-raw/wepdf/`
- **HTML audit** — `data/html-audit/wepdf-*.json`
- **Scoring CSV** — `data/scores.csv` (filter by product=wepdf)
- **Audit date** — 2026-04-20T16:29:40+00:00
