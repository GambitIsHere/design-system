# Sanjow SEO + PageSpeed Audit — Claude Code Execution Prompt

> Run this in Claude Code with network access and the PSI + CrUX API keys in env.
> Output: one markdown report per product + a portfolio-wide score matrix.
> Time estimate: 3–5 hours of agent execution (rate-limited by PSI API).
> **Companion to** `PORTFOLIO-AUDIT-PROMPT.md` — scores produced here feed the A/B/C decision there.

---

## Context you need before starting

You are auditing the technical SEO health and real-world page performance of the full
Sanjow Ventures product portfolio. Sanjow is a European digital venture studio
(Lisbon/London/Paris) operating a house-of-brands model. The PM is Srikant.

### Why this audit exists
Sanjow is in Q2 2026 STANDARDIZE + LAUNCH mode. The portfolio audit produces strategic
A/B/C recommendations per product (keep, new domain, new domain + app). Those decisions
need evidence from real technical signals — not vibes. This audit is that evidence layer.

### 2026 strategic pressures (keep in mind throughout)
- **SEO mix target:** 60% SEO / 30% paid by Q4 (currently 100% paid on most products)
- **Mobile share:** >70% of Sanjow traffic → mobile CWV carry the most weight
- **E-reputation tax:** legacy domains carry a CPA penalty; clean-domain moves only
  pay off if the technical foundation is right on day one
- **Multi-locale reality:** TopUp, WePDF, Travel products all run en-GB + 3–10 other
  locales; hreflang correctness compounds across them

### The two numbers this audit produces per product
1. **SEOScore (0–100)** — composite of technical SEO signals (see scoring model below)
2. **PerfScore (0–100)** — composite of CrUX field + Lighthouse lab metrics

These two numbers feed directly into the portfolio audit's decision matrix as new
columns. Their absolute values also trigger specific thresholds (see "Decision
thresholds" below).

---

## Prerequisites

Before running, confirm the following are in the env:

```bash
# Google PageSpeed Insights API (free tier: 25,000 queries/day, 400 QPS)
# Get: https://developers.google.com/speed/docs/insights/v5/get-started
PSI_API_KEY=...

# Chrome UX Report API (free; same key often works)
# Get: https://developer.chrome.com/docs/crux/api
CRUX_API_KEY=...

# Optional: GA4 access token if you want traffic-weighted URL sampling
GA4_ACCESS_TOKEN=...
GA4_PROPERTY_IDS=...  # comma-separated, one per Sanjow product
```

If `PSI_API_KEY` is missing, stop and ask the user before continuing — the audit is
meaningless without it.

---

## Execution instructions

### Step 1: Discover products and their live domains

Reuse the repo list from `PORTFOLIO-AUDIT-PROMPT.md`. For each product:

1. Read `package.json` and `.env.example` to identify the production domain(s).
2. Check `next.config.js` / `next.config.mjs` for `i18n.locales` and `domains`.
3. If the repo reveals multiple domains (old legacy + new clean brand), audit both
   separately — the comparison is part of the strategic value.
4. If a product has no discoverable live domain, log it and skip PSI calls for it;
   still produce the static SEO audit section from the repo alone.

Output a domain manifest:

```yaml
# seo-pagespeed-audit/data/domain-manifest.yml
products:
  wepdf:
    domains:
      - https://we-pdf.com
    locales: [en-GB, en-US, fr-FR, de-DE, es-ES, it-IT]
    repo: pdf/we-pdf
    stack: next.js-16
  topup:
    domains:
      - https://topup.com       # legacy
      - https://new-topup.com   # if clean brand exists
    locales: [en-GB, fr-FR]
    repo: topup
    stack: next.js-15
  # ... 14 products total
```

### Step 2: Build the URL tier list per product

For each product, sample URLs using this **4-tier strategy** (do NOT audit every route
× every locale — quota waste and signal noise):

| Tier | What | Example (WePDF) | Rationale |
|------|------|-----------------|-----------|
| 1. Homepage | `/` | `https://we-pdf.com/` | Brand-level baseline |
| 2. Top transactional | Pricing / checkout landing | `/pricing` | Conversion path perf |
| 3. Top SEO landing | Highest-traffic organic route | `/compress-pdf` | Organic acquisition |
| 4. Deep programmatic | Locale × feature combination | `/fr/merger-pdf` | Tests i18n + scale |

**Locale sampling:**
- Default: `en-GB` (Sanjow's primary market)
- Second: highest-traffic non-English locale from GA4 if available, else `fr-FR`
- Skip locales with <5% traffic share

**Form factors:** every URL runs twice — `strategy=mobile` and `strategy=desktop`.

**Budget per product:** 4 URLs × 2 locales × 2 form factors = 16 PSI calls per product.
For 14 products: ~224 PSI calls per run. Well within the 25,000/day quota.

### Step 3: Fetch PageSpeed Insights + CrUX data

For each URL in the tier list:

```bash
curl "https://www.googleapis.com/pagespeedonline/v5/runPagespeed?\
url=${URL}&\
strategy=${STRATEGY}&\
category=PERFORMANCE&\
category=SEO&\
category=ACCESSIBILITY&\
category=BEST_PRACTICES&\
locale=${LOCALE}&\
key=${PSI_API_KEY}"
```

**Rules:**
- 200ms delay between calls (even though quota allows more — be a good citizen)
- Retry once on 5xx with exponential backoff (1s, then 3s)
- On 429 (rate limit), wait 60s and retry once
- Save raw JSON to `seo-pagespeed-audit/data/psi-raw/${product}/${url-hash}-${strategy}.json`
  for reproducibility
- If CrUX field data is missing (low-traffic URL), log it as a finding — "insufficient
  real-user data" is itself a signal that the page isn't getting organic visibility

**Extract from each response:**
- Lighthouse scores: `performance`, `seo`, `accessibility`, `best-practices` (0–100)
- Lab CWV: LCP, CLS, INP (or TBT if INP not computed), FCP, TTFB, Speed Index
- CrUX field CWV (28-day p75): LCP, CLS, INP, FCP, TTFB
- Top 5 Lighthouse opportunities (by estimated savings in ms)
- Top 5 Lighthouse diagnostics
- Main-thread work total (ms)
- Total JavaScript bundle size (transferred + unused)
- Image audit findings (modern formats, sizing, lazy-loading)

### Step 4: Static SEO audit (HTML parsing, not PSI)

For each URL in the tier list, fetch the raw HTML (no JS execution) and extract:

```
- <title> — present, length 30–60 chars, unique per page
- <meta name="description"> — present, length 120–160 chars, unique
- <link rel="canonical"> — present, self-referential or upstream
- <link rel="alternate" hreflang="..."> — count, validity (locales match)
- <meta name="robots"> — not noindex unless intentional
- <meta name="viewport"> — present and mobile-friendly
- <html lang="..."> — matches locale
- <script type="application/ld+json"> — parse and validate schema.org types
- Open Graph: og:title, og:description, og:image, og:type, og:url
- Twitter Card: twitter:card, twitter:title, twitter:description, twitter:image
- <h1> count — exactly 1 per page
- Heading hierarchy — no h3 before h2, etc.
- Internal link count + external link count
- Canonical HTTPS redirects (http → https)
```

Then, site-level, fetch once per domain:

```
- /robots.txt — exists, has Sitemap directive, not blocking important paths
- /sitemap.xml — exists, valid XML, URL count, hreflang alternates present
- HTTP security headers: HSTS, X-Content-Type-Options, Referrer-Policy
- HTTP/2 or HTTP/3 enabled
- IPv6 enabled
```

### Step 5: Apply the scoring model

Use these weights (finalised with PM; do not change without approval):

**SEOScore = sum of weighted category scores, normalised to 0–100**

| Category | Weight | 0 points | 100 points |
|----------|--------|----------|------------|
| Technical SEO (title/meta/canonical/viewport/lang) | 25 | All missing or broken | All present, unique, correct length |
| Crawlability (robots, sitemap, 404s, redirects) | 20 | No sitemap, blocked by robots, chain redirects | Valid sitemap, clean robots, direct redirects |
| Content structure (h1/h2 hierarchy, word count, internal links) | 15 | No h1, thin content | Clear hierarchy, 500+ words, good interlinking |
| Structured data (JSON-LD schema, Open Graph, Twitter) | 15 | None present | Rich JSON-LD + full OG/Twitter tags |
| Programmatic SEO scalability (route patterns, hreflang coverage) | 25 | Flat routes, hreflang errors | Parameterised routes, all locales linked correctly |
| **Total** | **100** | | |

**PerfScore = sum of weighted category scores, normalised to 0–100**

| Category | Weight | 0 points | 100 points |
|----------|--------|----------|------------|
| CrUX field p75 (mobile-weighted 70/30) | 35 | LCP >4s, CLS >0.25, INP >500ms | LCP <2.5s, CLS <0.1, INP <200ms |
| Lighthouse mobile Performance category | 30 | <40 | >=90 |
| Lighthouse desktop Performance category | 15 | <40 | >=90 |
| Bundle size (JS transferred) | 10 | >1MB | <200KB |
| Image optimisation (modern formats, lazy-load, sized) | 10 | No optimisations | All images WebP/AVIF + lazy-loaded + sized |
| **Total** | **100** | | |

For each URL, compute both scores. For each **product**, the reported score is the
**weighted average** across tiers, with Tier 1 (homepage) and Tier 3 (top SEO landing)
weighted 2×, and Tier 2 (transactional) and Tier 4 (deep programmatic) weighted 1×.

**Show your arithmetic** in the report — no opaque scoring. Every number cites the
URL and field it came from.

### Step 6: Flag findings with severity

Severity scale:

- **P0 (blocker)** — breaks SEO indexing or loses real money. Noindex on prod,
  broken canonical loops, CLS >0.25 on checkout, hreflang pointing to non-existent
  locales, LCP >6s on mobile homepage.
- **P1 (high)** — measurable ranking or conversion impact. Missing meta description,
  CLS 0.1–0.25, mobile LCP 3–4s, no Open Graph, sitemap not submitted in robots.txt.
- **P2 (medium)** — compounds over time. Suboptimal h1 hierarchy, non-WebP images,
  thin content, missing Twitter Cards.
- **P3 (low)** — polish. Security headers missing, no HTTP/3, IPv6 off.

### Step 7: Decide strategic implication per finding

For every finding, answer one question: **is this fixable in-place on the current
domain, or does it argue for a clean-domain restart?**

- **"Fixable in-place" findings** support Option A in the portfolio audit. They can
  be YouTrack tickets.
- **"Architectural" findings** support Option B/C. Examples: flat route structure
  that can't do programmatic SEO without a rewrite; legacy domain with negative
  autofill suggestions; bundle size dictated by an old framework version.

This labelling is the handoff back to the portfolio audit.

### Decision thresholds — thumb rules

| Condition | Implication |
|-----------|-------------|
| SEOScore < 50 AND legacy domain | Strong Option B candidate |
| PerfScore < 40 AND mobile-heavy traffic | Strong Option B candidate |
| Mobile LCP p75 > 4s on homepage | CPA tax — flag even if other scores are OK |
| CLS p75 > 0.25 anywhere in checkout | P0, revenue-impacting |
| Hreflang errors across locales | Multi-locale product bleeding EU traffic |
| No sitemap OR sitemap not in robots.txt | Crawl budget wasted, P1 fix |
| All four category scores < 60 | Product may be deprecation candidate — flag for portfolio audit sunset list |

### Step 8: Produce the per-product report

Use this template (one file per product in `seo-pagespeed-audit/products/`):

```markdown
# [Product name] — SEO + PageSpeed Audit

## 1. Snapshot
- **Domain(s) audited:** [list]
- **Locales audited:** [primary, secondary]
- **URLs sampled:** [N] (Tier 1/2/3/4 breakdown)
- **Audit date:** [ISO]
- **PSI API run ID:** [hash or timestamp for reproducibility]

## 2. Headline scores
- **SEOScore:** X / 100
- **PerfScore:** X / 100
- **Portfolio rank (SEO):** [Nth of 14]
- **Portfolio rank (Perf):** [Nth of 14]

### Sub-scores
[Table: each scoring category, points earned, max, brief justification citing URL]

## 3. Core Web Vitals — CrUX field p75 (28-day)
| URL | Device | LCP | CLS | INP | TTFB | Verdict |
| ... | ... | ... | ... | ... | ... | Good/Needs improvement/Poor |

## 4. Lighthouse lab scores
| URL | Device | Perf | SEO | A11y | BP |
| ... | ... | ... | ... | ... | ... |

## 5. SEO findings (grouped by severity)
### P0
- [Finding] — URL, field, current value, target value, fixable/architectural
### P1
- ...
### P2
- ...

## 6. Performance findings
### Top 5 opportunities (from Lighthouse)
- [Opportunity name] — est. savings Xms, URL, fix recommendation
### Bundle analysis
- Total JS transferred: X KB across N requests
- Largest single bundle: [name] — X KB
- Unused JS: X KB (Y% of total)

## 7. Locale health
| Locale | SEOScore | PerfScore | Hreflang valid | Notes |
| ... | ... | ... | ... | ... |

## 8. Mobile vs desktop delta
- Mobile PerfScore: X, Desktop PerfScore: Y, Delta: Z
- Mobile-specific issues: [list]

## 9. Strategic implication
**This audit supports:** [Option A / Option B / Option C] — [1-paragraph rationale]
**Key architectural findings (argue for Option B/C):** [list]
**Fixable in-place findings (support Option A):** [list]
**Cross-reference:** see portfolio audit decision for this product in
`portfolio-audit/products/[product].md`

## 10. Raw data
- PSI JSON dumps: `seo-pagespeed-audit/data/psi-raw/[product]/`
- Static HTML audit: `seo-pagespeed-audit/data/html-audit/[product].json`
```

### Step 9: Portfolio summary

One summary document at `seo-pagespeed-audit/README.md`:

```markdown
# Sanjow Portfolio — SEO + PageSpeed Audit Summary

## Score matrix
| Product | Domain | SEOScore | PerfScore | Mobile LCP p75 | CLS p75 | Top finding | Supports |
|---------|--------|----------|-----------|----------------|---------|-------------|----------|
| WePDF | we-pdf.com | ... | ... | ... | ... | ... | B |
| TopUp | ... | ... | ... | ... | ... | ... | ... |
| ... × 14 rows | | | | | | | |

## Products ranked best to worst (SEOScore)
[Ranked list with 1-line commentary each]

## Products ranked best to worst (PerfScore)
[Ranked list]

## Top 10 P0 findings across the portfolio
[Ranked by estimated revenue/traffic impact]

## Hreflang audit — multi-locale products only
[Table showing which products have clean hreflang vs broken]

## CrUX data coverage
[Products where CrUX returned "insufficient data" — these have low organic traffic]

## Mobile-first verdict
[Products where mobile PerfScore lags desktop by >20 points — mobile-critical fixes]

## Scoring audit
- Weights used: [list the weights from the scoring model]
- URL sampling strategy: [confirm 4-tier + locale rules were applied]
- Products where sampling was incomplete and why: [list]

## Handoff to portfolio audit
[Explicit list of which products' SEO/PSI data flipped or strengthened their
A/B/C recommendation in the portfolio audit]
```

Also produce a **machine-readable CSV** at `seo-pagespeed-audit/data/scores.csv`:

```csv
product,domain,locale,tier,url,strategy,seo_score,perf_score,lcp_field,cls_field,inp_field,lh_perf,lh_seo,lh_a11y,lh_bp,audit_date
wepdf,we-pdf.com,en-GB,1,https://we-pdf.com/,mobile,58,42,3.8,0.18,280,45,88,92,87,2026-04-21
...
```

This CSV is the data layer the portfolio audit and Optimiser.Pro both read from.

### Step 10: Commit and push

Save everything to a dedicated directory structure:

```
seo-pagespeed-audit/
├── README.md                       # Portfolio summary
├── products/
│   ├── wepdf.md
│   ├── topup.md
│   ├── airport-checkin.md
│   ├── fast-track.md
│   ├── airport-lounges.md
│   ├── global-tickets.md
│   ├── cv-builder.md
│   ├── visa-portals.md
│   ├── driving-licence.md
│   ├── gift-card.md
│   ├── iq-test.md
│   ├── reverse-lookup.md
│   ├── pdf-ai.md
│   └── ai-chat.md
├── data/
│   ├── domain-manifest.yml
│   ├── psi-raw/                    # raw PSI JSON per URL
│   ├── html-audit/                 # static HTML parse per URL
│   └── scores.csv                  # machine-readable matrix
└── summary-matrix.md               # same as README but table-first
```

Commit message: `docs(audit): SEO + PageSpeed audit with per-product scores and portfolio matrix`

---

## Verification checklist

After completing all reports, verify:

- [ ] Every product has both SEOScore and PerfScore
- [ ] Every score cites the URLs and fields it was computed from
- [ ] `data/scores.csv` is complete with no empty cells
- [ ] Every P0 finding has a fix recommendation AND an architectural/fixable label
- [ ] Hreflang audit run for every multi-locale product
- [ ] Mobile and desktop both captured for every URL in the tier list
- [ ] CrUX "insufficient data" cases are logged, not silently skipped
- [ ] Cross-reference block present in every product report pointing to the matching
      portfolio audit entry
- [ ] Summary matrix sortable by either score
- [ ] Raw PSI JSON dumps present for reproducibility

```bash
# Final verification commands
find seo-pagespeed-audit/products -name "*.md" | wc -l       # Should be 14
grep -l "SEOScore:" seo-pagespeed-audit/products/*.md | wc -l  # Should match above
grep -l "PerfScore:" seo-pagespeed-audit/products/*.md | wc -l # Should match above
wc -l seo-pagespeed-audit/data/scores.csv                    # Should be (products × URLs × form factors) + 1 header
grep -c "^P0" seo-pagespeed-audit/products/*.md              # Portfolio-wide P0 count
```

---

## Edge cases and handling

- **Product with no live domain (pre-launch):** run static SEO audit from the repo
  only; mark PerfScore as "N/A — not yet launched" and score only SEO sub-categories
  that can be inferred from code (route structure, planned hreflang, JSON-LD in
  components).
- **Product on two domains (legacy + clean):** audit both, report them side-by-side
  in the same product file. The delta is the single most important number for the
  portfolio audit's Option B decision.
- **PSI returns an error repeatedly:** log the URL with the error and skip — do not
  invent scores. The report should show which URLs were attempted vs scored.
- **CrUX returns "ORIGIN" fallback instead of URL-level data:** use origin-level data
  but clearly label it; origin-level p75 is directionally useful but hides per-page
  problems.
- **Non-HTML responses (PDFs, images):** if a sampled URL returns a non-HTML
  content-type, log it and sample a different route at the same tier.

---

## What this audit deliberately does NOT do

- Backlink analysis (requires Ahrefs/SEMrush — not free, not agent-runnable)
- Keyword rank tracking (separate tool, separate quota)
- Competitor SEO comparison (use `competitor-alternatives` skill in the portfolio audit)
- Content quality scoring (subjective — needs editorial review)
- Trustpilot / e-reputation (portfolio audit covers this)
- Code quality review (portfolio audit covers this)
- Broken-link crawl of entire site (too slow; PSI samples are the shortcut)

If any of these become needed later, they go in a separate audit prompt — keep this
one focused on the two scores it produces.
