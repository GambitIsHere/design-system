# WePDF — SEO + PageSpeed Audit

_Run 20260421T142836+0000 · 32 URLs · 2 domain(s) · 2 locale(s)_

## Executive summary

- **Headline:** WePDF scores **SEO 24.9** (critical) and **Perf 15.4** (critical). Audit supports **Option B**.
- **Findings:** 0 P0 (must-fix), 56 P1 (should-fix). 0 architectural vs 104 fixable-in-place.
- **Clean vs legacy:** `workspace.we-pdf.com` Lighthouse perf 86 vs `we-pdf.com` 91. This delta is the central input to the Option-B decision.

## Decision: Option **B**

Triggered by:
- SEOScore<50 on legacy domain → strong Option B candidate
- PerfScore<40 on mobile-heavy traffic → strong Option B candidate
- Mobile LCP p75 4536ms > 4s → CPA tax flag
- Hreflang errors across locales → multi-locale EU traffic bleed

_See dashboard for full reasoning · `products/wepdf.jsx`_

## Clean vs Legacy snapshot

| Metric | Clean (`workspace.we-pdf.com`) | Legacy (`we-pdf.com`) |
|---|---|---|
| Lighthouse perf (mobile, avg) | 84 | 89 |
| Lighthouse perf (desktop, avg) | 88 | 93 |
| Lighthouse SEO (avg) | 66 | 56 |
| CrUX LCP p75 | — | 3144ms |
| CrUX CLS p75 | — | 0.08 |
| JS bundle (mobile, KB) | 560 | 402 |
| Composite SEOScore | 24.4 | 12.9 |
| Composite PerfScore | 14.5 | 8.6 |

## Next steps (this sprint)

1. **mobile LCP p75 — Optimise LCP element (image preload, size, format).** _(Frontend · 1d · +12 score lift est.)_  
   Affects `we-pdf.com/en/pricing`. Currently `4536ms`, target `<2500ms`.
2. **hreflang coverage — Emit hreflang for every locale route + x-default.** _(Frontend · 3h · +8 score lift est.)_  
   Affects `workspace.we-pdf.com/en/pricing`. Currently `0 of 10 locales`, target `10 hreflang tags + x-default`.
3. **<title> — Add a page-level title via Next.js metadata.** _(Content · 1h · +5 score lift est.)_  
   Affects `workspace.we-pdf.com/en/pricing`. Currently `missing`, target `30–60 char unique title`.
4. **sitemap.xml — Generate a sitemap (Next.js app router supports `sitemap.ts`).** _(Frontend · 1h · +4 score lift est.)_  
   Affects `workspace.we-pdf.com`. Currently `missing`, target `valid XML sitemap at /sitemap.xml`.
5. **meta description — Add a description via Next.js metadata.** _(Content · 1h · +4 score lift est.)_  
   Affects `workspace.we-pdf.com/en/pricing`. Currently `missing`, target `120–160 char unique description`.

## Where the data lives

- **Interactive dashboard** — `products/wepdf.jsx` (open as a React artifact for filters + charts)
- **Raw PSI JSON** — `data/psi-raw/wepdf/`
- **HTML audit** — `data/html-audit/wepdf-*.json`
- **Scoring CSV** — `data/scores.csv` (filter by product=wepdf)
- **Audit date** — 2026-04-21T14:28:36+00:00
