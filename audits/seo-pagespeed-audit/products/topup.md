# TopUp — SEO + PageSpeed Audit

_Run 20260421T090031+0000 · 8 URLs · 2 domain(s) · 2 locale(s)_

## Executive summary

- **Headline:** TopUp scores **SEO 15.7** (critical) and **Perf 11.8** (critical). Audit supports **Option B**.
- **Findings:** 0 P0 (must-fix), 16 P1 (should-fix). 0 architectural vs 28 fixable-in-place.
- **Clean vs legacy:** `new-topup.com` Lighthouse perf — vs `topup.com` 61. This delta is the central input to the Option-B decision.

## Decision: Option **B**

Triggered by:
- SEOScore<50 on legacy domain → strong Option B candidate
- PerfScore<40 on mobile-heavy traffic → strong Option B candidate
- Mobile LCP p75 4397ms > 4s → CPA tax flag
- Hreflang errors across locales → multi-locale EU traffic bleed

_See dashboard for full reasoning · `products/topup.jsx`_

## Clean vs Legacy snapshot

| Metric | Legacy (`topup.com`) | Clean (`new-topup.com`) |
|---|---|---|
| Lighthouse perf (mobile, avg) | 56 | — |
| Lighthouse perf (desktop, avg) | 67 | — |
| Lighthouse SEO (avg) | 96 | — |
| CrUX LCP p75 | 3511ms | — |
| CrUX CLS p75 | 0.01 | — |
| JS bundle (mobile, KB) | 767 | — |
| Composite SEOScore | 31.4 | 0.0 |
| Composite PerfScore | 23.6 | 0.0 |

## Next steps (this sprint)

1. **mobile LCP p75 — Optimise LCP element (image preload, size, format).** _(Frontend · 1d · +12 score lift est.)_  
   Affects `topup.com/`. Currently `4397ms`, target `<2500ms`.
2. **hreflang coverage — Emit hreflang for every locale route + x-default.** _(Frontend · 3h · +8 score lift est.)_  
   Affects `topup.com/`. Currently `0 of 2 locales`, target `2 hreflang tags + x-default`.
3. **<title> — Add a page-level title via Next.js metadata.** _(Content · 1h · +5 score lift est.)_  
   Affects `topup.com/fr/`. Currently `missing`, target `30–60 char unique title`.
4. **meta description — Add a description via Next.js metadata.** _(Content · 1h · +4 score lift est.)_  
   Affects `topup.com/fr/`. Currently `missing`, target `120–160 char unique description`.
5. **sitemap.xml — Generate a sitemap (Next.js app router supports `sitemap.ts`).** _(Frontend · 1h · +4 score lift est.)_  
   Affects `new-topup.com`. Currently `missing`, target `valid XML sitemap at /sitemap.xml`.

## Where the data lives

- **Interactive dashboard** — `products/topup.jsx` (open as a React artifact for filters + charts)
- **Raw PSI JSON** — `data/psi-raw/topup/`
- **HTML audit** — `data/html-audit/topup-*.json`
- **Scoring CSV** — `data/scores.csv` (filter by product=topup)
- **Audit date** — 2026-04-21T09:00:31+00:00
