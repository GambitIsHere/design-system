# Global Visa Portal — SEO + PageSpeed Audit

_Run 20260421T085955+0000 · 8 URLs · 2 domain(s) · 2 locale(s)_

## Executive summary

- **Headline:** Global Visa Portal scores **SEO 51.8** (weak) and **Perf 49.2** (weak). Audit supports **Option A/B (needs human judgement)**.
- **Findings:** 0 P0 (must-fix), 10 P1 (should-fix). 0 architectural vs 18 fixable-in-place.
- **Clean vs legacy:** `global-visa-portal.vercel.app` Lighthouse perf 71 vs `online-visas.com` 62. This delta is the central input to the Option-B decision.

## Decision: Option **A/B (needs human judgement)**

Triggered by:
- Hreflang errors across locales → multi-locale EU traffic bleed

_See dashboard for full reasoning · `products/visa_portals.jsx`_

## Clean vs Legacy snapshot

| Metric | Clean (`global-visa-portal.vercel.app`) | Legacy (`online-visas.com`) |
|---|---|---|
| Lighthouse perf (mobile, avg) | 60 | 57 |
| Lighthouse perf (desktop, avg) | 82 | 67 |
| Lighthouse SEO (avg) | 100 | 100 |
| CrUX LCP p75 | — | 2087ms |
| CrUX CLS p75 | — | 0.01 |
| JS bundle (mobile, KB) | 1123 | 1183 |
| Composite SEOScore | 51.8 | 51.8 |
| Composite PerfScore | 42.2 | 56.1 |

## Next steps (this sprint)

1. **hreflang coverage — Emit hreflang for every locale route + x-default.** _(Frontend · 3h · +8 score lift est.)_  
   Affects `global-visa-portal.vercel.app/`. Currently `0 of 8 locales`, target `8 hreflang tags + x-default`.
2. **sitemap.xml — Generate a sitemap (Next.js app router supports `sitemap.ts`).** _(Frontend · 1h · +4 score lift est.)_  
   Affects `global-visa-portal.vercel.app`. Currently `missing`, target `valid XML sitemap at /sitemap.xml`.
3. **canonical link — Emit a self-referential `<link rel='canonical'>` via metadata.** _(Frontend · 30m · +3 score lift est.)_  
   Affects `global-visa-portal.vercel.app/`. Currently `missing`, target `self-referential canonical`.

## Where the data lives

- **Interactive dashboard** — `products/visa_portals.jsx` (open as a React artifact for filters + charts)
- **Raw PSI JSON** — `data/psi-raw/visa_portals/`
- **HTML audit** — `data/html-audit/visa_portals-*.json`
- **Scoring CSV** — `data/scores.csv` (filter by product=visa_portals)
- **Audit date** — 2026-04-21T08:59:55+00:00
