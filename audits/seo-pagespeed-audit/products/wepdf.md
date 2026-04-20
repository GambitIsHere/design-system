# WePDF — SEO + PageSpeed Audit

## 1. Snapshot

- **Domain(s) audited:** https://workspace.we-pdf.com, https://we-pdf.com
- **Locales audited:** en
- **URLs sampled:** 4 (T1=4)
- **Audit date:** 2026-04-20T16:14:25+00:00
- **PSI API run ID:** 20260420T161425+0000

## 2. Headline scores

- **SEOScore:** 58.5 / 100
- **PerfScore:** 25.1 / 100

### Sub-scores (SEO)

| Category | Score | Weight | Breakdown |
|---|---:|---:|---|
| technical seo | 80.0 | 25 | 8/10 checks passed |
| crawlability | 50.0 | 20 | 4/8 checks passed |
| content structure | 25.0 | 15 | ?/? checks passed |
| structured data | 60.0 | 15 | ?/? checks passed |
| programmatic scalability | 90.0 | 25 | hreflang_coverage=1.0, hreflang_valid=True, has_xdefault=False, parameterised_routes=True, alt_count=10, expected_locale |

### Sub-scores (Perf)

| Category | Score | Weight | Breakdown |
|---|---:|---:|---|
| crux field p75 | None | 0 | note=CrUX p75 unavailable — weight redistributed to lab categories, mobile_score=0, desktop_score=0, crux_mobile_availab |
| lh mobile perf | 30.0 | 46.2 | raw=0.55 |
| lh desktop perf | 46.0 | 23.1 | raw=0.63 |
| bundle size | 0.0 | 15.4 | total_js_kb=1093.7 |
| image optimisation | 25.0 | 15.4 | checks={'modern_formats_all': False, 'lazy_loaded_all': False, 'properly_sized': False, 'no_layout_shift': True}, modern |

## 3. Core Web Vitals — CrUX field p75 (28-day)

| URL | Device | LCP | CLS | INP | TTFB | Verdict |
|---|---|---:|---:|---:|---:|---|
| workspace.we-pdf.com/en/ | mobile | – | – | – | – | Insufficient data |
| workspace.we-pdf.com/en/ | desktop | – | – | – | – | Insufficient data |
| we-pdf.com/en/ | mobile | – | – | – | – | Insufficient data |
| we-pdf.com/en/ | desktop | 1871ms | 0.050 | 123ms | 728ms | Good |

## 4. Lighthouse lab scores

| URL | Device | Perf | SEO | A11y | BP |
|---|---|---:|---:|---:|---:|
| workspace.we-pdf.com/en/ | mobile | 55 | 92 | 89 | 100 |
| workspace.we-pdf.com/en/ | desktop | 63 | 92 | 94 | 100 |
| we-pdf.com/en/ | mobile | – | – | – | – |
| we-pdf.com/en/ | desktop | 70 | 100 | 76 | 96 |

## 5. SEO findings (grouped by severity)

### P1

- **sitemap.xml** — `workspace.we-pdf.com`, current `missing`, target `valid XML sitemap at /sitemap.xml` — **fix:** Generate a sitemap (Next.js app router supports `sitemap.ts`). — **fixable-in-place** (Framework-level config — no architectural change needed.)
- **sitemap.xml** — `we-pdf.com`, current `missing`, target `valid XML sitemap at /sitemap.xml` — **fix:** Generate a sitemap (Next.js app router supports `sitemap.ts`). — **fixable-in-place** (Framework-level config — no architectural change needed.)
- **canonical link** — `we-pdf.com/en/`, current `missing`, target `self-referential canonical` — **fix:** Emit a self-referential `<link rel='canonical'>` via metadata. — **fixable-in-place** (Metadata API.)
- **hreflang coverage** — `we-pdf.com/en/`, current `0 of 10 locales`, target `10 hreflang tags + x-default` — **fix:** Emit hreflang for every locale route + x-default. — **fixable-in-place** (Middleware or metadata config.)

### P2

- **h1 count** — `workspace.we-pdf.com/en/`, current `0 h1 tags`, target `exactly 1 h1 per page` — **fix:** Ensure exactly one h1 per route; demote duplicates to h2. — **fixable-in-place** (Component-level fix.)
- **Open Graph** — `workspace.we-pdf.com/en/`, current `incomplete`, target `og:title + og:description + og:image + og:url + og:type` — **fix:** Emit full OG tags via Next.js metadata.openGraph. — **fixable-in-place** (Metadata API.)
- **JSON-LD** — `workspace.we-pdf.com/en/`, current `none`, target `relevant schema.org types (Organization, WebSite, Product, FAQ)` — **fix:** Inject JSON-LD for the page's primary entity type. — **fixable-in-place** (Content injection.)
- **<title> length** — `we-pdf.com/en/`, current `6 chars`, target `30–60 chars` — **fix:** Tighten or expand the title to 30–60 characters. — **fixable-in-place** (Copy change.)
- **h1 count** — `we-pdf.com/en/`, current `0 h1 tags`, target `exactly 1 h1 per page` — **fix:** Ensure exactly one h1 per route; demote duplicates to h2. — **fixable-in-place** (Component-level fix.)
- **JSON-LD** — `we-pdf.com/en/`, current `none`, target `relevant schema.org types (Organization, WebSite, Product, FAQ)` — **fix:** Inject JSON-LD for the page's primary entity type. — **fixable-in-place** (Content injection.)

## 6. Performance findings

### Top 5 opportunities (from Lighthouse)

- **Reduce unused JavaScript** — est. savings 910ms at `workspace.we-pdf.com/en/` — Reduce unused JavaScript and defer loading scripts until they are required to decrease bytes consumed by network activity.
- **Avoid multiple page redirects** — est. savings 767ms at `workspace.we-pdf.com/en/` — Redirects introduce additional delays before the page can be loaded.
- **Initial server response time was short** — est. savings 167ms at `workspace.we-pdf.com/en/` — Keep the server response time for the main document short because all other requests depend on it.
- **Reduce unused CSS** — est. savings 40ms at `we-pdf.com/en/` — Reduce unused rules from stylesheets and defer CSS not used for above-the-fold content to decrease bytes consumed by network activity.

### Bundle analysis

- `workspace.we-pdf.com/en/` (mobile): JS 1093.7KB across 36 req, largest 174.9KB, unused 296.4KB
- `workspace.we-pdf.com/en/` (desktop): JS 1102.3KB across 36 req, largest 174.8KB, unused 319.8KB
- `we-pdf.com/en/` (desktop): JS 1624.2KB across 61 req, largest 232.7KB, unused 484.6KB

## 8. Mobile vs desktop delta

- Mobile PerfScore: **25.1**, Desktop PerfScore: **25.1**, Delta: **0.0** (desktop minus mobile)

## 9. Strategic implication

**This audit supports:** Option **B**

**Thumb rules triggered:**

- PerfScore<40 on mobile-heavy traffic → strong Option B candidate
- Hreflang errors across locales → multi-locale EU traffic bleed

**Key architectural findings (argue for Option B/C):**

- _none — all findings are fixable in-place_

**Fixable-in-place findings (support Option A):**

- [P1] sitemap.xml — Generate a sitemap (Next.js app router supports `sitemap.ts`).
- [P1] sitemap.xml — Generate a sitemap (Next.js app router supports `sitemap.ts`).
- [P1] canonical link — Emit a self-referential `<link rel='canonical'>` via metadata.
- [P1] hreflang coverage — Emit hreflang for every locale route + x-default.
- [P2] h1 count — Ensure exactly one h1 per route; demote duplicates to h2.
- [P2] Open Graph — Emit full OG tags via Next.js metadata.openGraph.
- [P2] JSON-LD — Inject JSON-LD for the page's primary entity type.
- [P2] <title> length — Tighten or expand the title to 30–60 characters.
- [P2] h1 count — Ensure exactly one h1 per route; demote duplicates to h2.
- [P2] JSON-LD — Inject JSON-LD for the page's primary entity type.

**Cross-reference:** see portfolio audit decision for this product in `portfolio-audit/products/wepdf.md`

## 10. Raw data

- PSI JSON dumps: `seo-pagespeed-audit/data/psi-raw/wepdf/`
- Static HTML audit: `seo-pagespeed-audit/data/html-audit/wepdf.json`
- Scoring row: `seo-pagespeed-audit/data/scores.csv` (filter by product=wepdf)
