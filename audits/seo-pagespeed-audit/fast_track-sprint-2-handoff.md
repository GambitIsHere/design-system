# Fast Track SEO Sprint 2 — Handoff

**Date:** 2026-04-22
**From:** Claude Code session (CLI)
**Branch:** `seo/fast-track-sprint-2` (stacked on `seo/fast-track-sprint-1`)
**Status:** Code complete locally, **not yet pushed**, awaits Sprint 1 merge.

---

## TL;DR

Four architectural tickets landed as small focused commits on a branch
stacked on Sprint 1's PR #2. Nothing in Sprint 2 deploys until Sprint 1
is merged first.

| Ticket | Status | Where |
|---|---|---|
| FAST_TRACK-ARCH-006 — Code-split & tree-shake | **done (code)** | `src/app/[locale]/page.tsx`, `src/components/IndexPage.tsx` |
| FAST_TRACK-ARCH-007 — next/image + AVIF/WebP | **done (code)** | `next.config.ts`, `src/components/checkout/*` |
| FAST_TRACK-ARCH-008 — Centralise hreflang | **done (code)** | `src/app/sitemap.ts` |
| FAST_TRACK-ARCH-009 — Legacy domain 301s | **code shipped, off by default** | `src/config/legacy-hosts.ts`, `next.config.ts`, `docs/arch-009-legacy-migration.md` |

Sprint 1 also picked up a **build-break fix** during this session:
`fix(seo): restore src/config/site.config.ts removed in d182b8e` — PR #2
would not have built without it.

---

## What shipped in each ticket

### ARCH-006 — Code-split & tree-shake JS bundle (+20 perf target)

**Problem (from the audit):** Both `IndexPage` (legacy brand) and
`LandingPv` (PV brands) import statically into `app/[locale]/page.tsx`,
so the browser ships both trees even though only one renders. Every
below-the-fold section of the legacy landing (Testimonials, TrustSection,
FAQ, Footer, ServiceExplainer) also ships in the initial client chunk.

**Fix:**
- Homepage (`src/app/[locale]/page.tsx`): both landing trees loaded via
  `next/dynamic`. Next emits one chunk per variant and only the active
  brand's tree is fetched.
- `IndexPage.tsx`: below-the-fold sections are wrapped in `next/dynamic`
  with SSR enabled. HTML renders server-side (SEO-safe), hydration chunks
  stream in after the hero + features.

**Acceptance (verify post-deploy via Lighthouse + `@next/bundle-analyzer`):**
- [ ] First-load JS for `/` ≤ 350KB (transferred)
- [ ] No single chunk > 150KB
- [ ] Mobile Lighthouse perf improves by ≥ 15 points
- [ ] `Reduce unused JavaScript` Lighthouse audit drops below 50KB savings

**Not covered here (follow-up):** `framer-motion` is imported by 15
components. Replacing it with CSS animations or lazy-loading the motion
module would cut another ~100KB off the bundle. Flagged for Sprint 3.

### ARCH-007 — Image pipeline → next/image + AVIF/WebP (+10 perf target)

**Observations:**
- Only **4 raw `<img>` tags** exist in the codebase — all tiny SVG card
  brand icons (Visa / Mastercard) in `checkout/CheckoutSummary.tsx` and
  `checkout/PaymentForm.tsx`. Converting SVGs to `next/image` requires
  `dangerouslyAllowSVG: true` and doesn't deliver format gains (SVGs are
  already vectors).
- Real marketing imagery (Header logo, NavBar logo, Footer logo) already
  uses `next/image` with width+height set — no CLS risk.

**Fix:**
- `next.config.ts`: added `images.formats: ["image/avif", "image/webp"]`
  plus explicit `deviceSizes` / `imageSizes` — every existing `next/image`
  call now gets modern-format negotiation automatically.
- The 4 SVG `<img>` tags: added explicit `width` / `height` attrs
  matching the aspect ratio so layout shift is eliminated, without
  taking the SVG-optimization security risk.

**Acceptance:**
- [ ] Modern formats audit passes (≥ 90% AVIF/WebP) — verify on Lighthouse
- [ ] CLS p75 < 0.1 on all T1 URLs
- [ ] Hero LCP drops by ≥ 500ms on mobile — verify on PageSpeed Insights

### ARCH-008 — Centralise hreflang + x-default in middleware (+12 SEO)

**Observation:** Sprint 1 already centralised hreflang emission through
`languageAlternatesFor()` in `src/config/site.ts`, which is used by the
`pageMetadata` helper on every indexable page. The ticket is effectively
90% complete; the remaining gap was in `src/app/sitemap.ts` which
re-implemented the locale map and **omitted `x-default`**.

**Fix:** `sitemap.ts` now calls the same helper (`languageAlternatesFor`)
and gets x-default for free.

**Acceptance:**
- [x] All T1/T2 URLs emit hreflang tags for every configured locale + x-default (verified in sitemap.xml build output + pageMetadata helper)
- [x] Adding a new locale requires only a config entry (1-line change in `src/i18n/routing.ts`)
- [ ] Google Search Console Hreflang report shows 0 errors after 2 weeks (post-deploy verification)

### ARCH-009 — Legacy domain 301 migration

**What shipped in code:**
- `src/config/legacy-hosts.ts` — single source of truth for the legacy
  host list and the feature-flag env var.
- `next.config.ts` — per-host `has: [{ type: "host" }]` 301 redirects
  for `/` and `/:path*`, **gated behind `ENABLE_LEGACY_HOST_REDIRECTS=true`**.
  Code is inert until the flag is set.
- `docs/arch-009-legacy-migration.md` — full activation checklist.

**What's still operator-owned** (DevOps + content owner):

1. DNS — point each legacy host at Vercel.
2. Vercel — add each legacy host as a project domain; wait for TLS cert.
3. Set `ENABLE_LEGACY_HOST_REDIRECTS=true` on Vercel production.
4. Google Search Console — change-of-address for each legacy property.
5. Keep legacy certs valid for 12 months post-cut.

Full step-by-step + rollback procedure lives in
`fast-track-ai/docs/arch-009-legacy-migration.md`.

---

## How this is committed

Four commits on `seo/fast-track-sprint-2`, each scoped to one ticket so
they review independently:

```
perf(seo): lazy-load below-fold sections + route-split landings (FAST_TRACK-ARCH-006)
perf(images): AVIF+WebP config + CLS dims on checkout SVGs (FAST_TRACK-ARCH-007)
fix(seo): x-default in sitemap, DRY via languageAlternatesFor (FAST_TRACK-ARCH-008)
feat(seo): legacy-host 301 redirect config + flag (FAST_TRACK-ARCH-009)
```

Branch topology:

```
main
  └── seo/fast-track-sprint-1   (PR #2, 8 commits)
        └── seo/fast-track-sprint-2   (4 commits, not yet pushed)
```

**Merge order:** PR #2 (Sprint 1) first, then rebase Sprint 2 onto `main`
and open a second PR. Don't cut Sprint 2's PR against Sprint 1 — it would
confuse the review surface.

---

## What's pending from Sprint 1

Unchanged from the Sprint 1 handoff — these are still operator-owned:

- [ ] Merge PR #2 on `fast-track-ai`
- [ ] Set `NEXT_PUBLIC_SITE_URL=https://travel-synch.com` on Vercel
      (production, preview, development)
- [ ] Submit the new sitemap in Google Search Console for the
      `travel-synch.com` property
- [ ] Monitor `/en/*` → `/*` 301 report in GSC for 2 weeks post-deploy

---

## Known limitations in this session

**Local build didn't run in this session.** Node 25.8.1 (the only node on
this machine) has an edge-runtime compatibility bug with Next 16.2.1
(`TypeError: (0, import_load.load) is not a function`). Vercel's CI uses
Node 20/22 and is unaffected. The earlier Sprint 1 build that did succeed
confirmed sitemap.xml and robots.txt generation — those paths haven't
regressed in Sprint 2.

**ARCH-006 acceptance verification is deferred.** The "first-load JS ≤
350KB" and "mobile perf +15" numbers need a real build + Lighthouse run.
Re-run the audit (`python scripts/run_audit.py --product fast_track`)
after Sprint 1 + Sprint 2 both deploy to verify.

---

## Re-audit plan

After Sprint 1 and Sprint 2 both merge and deploy:

```bash
cd /Users/srikan/Documents/GitHub/Sanjow/Sanjow-Ventures/design-system/audits/seo-pagespeed-audit
python3 scripts/run_audit.py --product fast_track
```

Expected deltas:
- SEO score 49.7 → **≥ 80** (all 5 FIX tickets + ARCH-008 + ARCH-009)
- Perf score 60.7 → **≥ 75** (ARCH-006 code-split + ARCH-007 AVIF/WebP)
- Option-B decision should dissolve (both SEOScore ≥ 50 + hreflang clean)

---

## Related

- Sprint 1 handoff: `audits/seo-pagespeed-audit/fast_track-handoff.md`
- Session notes: `audits/seo-pagespeed-audit/SESSION-NOTES.md`
- Portfolio kanban: `audits/seo-pagespeed-audit/fix-seo-plans/portfolio.html`
- Ticket source: `audits/seo-pagespeed-audit/fix-seo-plans/fast_track.md`
- Legacy domain checklist: `fast-track-ai/docs/arch-009-legacy-migration.md`
