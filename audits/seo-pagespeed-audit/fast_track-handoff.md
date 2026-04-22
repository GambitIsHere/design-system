# Fast Track SEO Sprint 1 — Handoff for Claude Desktop

**Date:** 2026-04-21
**From:** Claude Code session (CLI)
**To:** Claude Desktop
**Status:** Code shipped, PR open, one asset blocker remaining

---

## TL;DR — what Claude Desktop needs to do

**Primary task:** generate a branded 1200×630 OG image at
`public/og/fast-track-default.png` in the `fast-track-ai` repo, then flip
the `DEFAULT_OG_IMAGE` constant in `src/config/site.ts` to point at it.

Everything else in Sprint 1 is already committed, pushed, and in a PR.

---

## Current state (nothing for you to re-do)

### `fast-track-ai` — PR #2

- **PR:** https://github.com/Sanjow-Ventures/fast-track-ai/pull/2
- **Branch:** `seo/fast-track-sprint-1` (6 commits ahead of `main`)
- **Base:** `main`
- **Awaiting:** user review + merge + Vercel env var setup

The 6 commits (in order):

1. `d182b8e` chore(seo): shared site config + pageMetadata helper
2. `90798c3` chore(seo): add metadataBase + robots defaults to root layout
3. `a9a3fe0` feat(seo): localePrefix as-needed + 301 /en/* → /* (PREREQ)
4. `48af484` feat(seo): dynamic sitemap.xml + robots.txt (FIX-001)
5. `98786f0` feat(seo): canonicals + hreflang + OG (FIX-002/003/004)
6. `d2517f6` feat(seo): schema.org JSON-LD (FIX-005)

### `design-system` — `main` pushed

7 commits ahead of the prior state (`4335d82..7f4daef`):
- Fast Track product audit + execution prompt
- Portfolio kanban builder script + scratch gitignore
- WePDF re-audit refresh (SEO 24.9 / Perf 15.4)
- Airport Check-in, Topup, Visa Portals product audits (new)
- Portfolio roll-up (manifest, scores, kanban)

### Canonical decisions (already locked)

- **Host:** `https://travel-synch.com`
- **Routing:** `localePrefix: "as-needed"` — English serves bare
  (`/`, `/faq`); `/en/*` 301-redirects to `/*`
- **Other locales:** `/fr/…`, `/es/…`, `/pt/…`, `/it/…`, `/de/…`,
  `/tr/…`, `/pl/…`

---

## Your task — branded OG image

### 1. Generate the asset

Use Claude Desktop's image generation (or Figma MCP if a brand file
exists) to create:

- **Path:** `public/og/fast-track-default.png` in `fast-track-ai` repo
- **Dimensions:** exactly **1200×630 px** (Facebook / Twitter / LinkedIn
  required size — anything smaller downgrades rich-result eligibility)
- **Size:** under **1 MB**
- **Brand:** "Trip Sorted — Fast Track"
- **Product:** airport fast-track / skip-the-queue service at 200+ airports,
  auto check-in, lounge access, flight compensation
- **Must include:**
  - Trip Sorted wordmark (reference: `public/Trip Sorted - Favicon (1).png`)
  - "Fast Track" label
  - A value-prop line, e.g. "Skip the queue at 200+ airports"
- **Style cues:** clean, premium, travel-brand — think British Airways
  executive lounge, not budget airline. Match the favicon's colour palette.

### 2. Update `src/config/site.ts`

Currently (line with a `//` comment explaining the fallback):

```ts
export const DEFAULT_OG_IMAGE = "/apple-touch-icon.png"; // fallback until branded 1200x630 OG image is provided
```

Change to:

```ts
export const DEFAULT_OG_IMAGE = "/og/fast-track-default.png";
```

### 3. Validate

Before committing:

- [ ] Image is exactly 1200×630 and under 1 MB
- [ ] Test locally: `npm run dev`, then `curl -I http://localhost:3000/og/fast-track-default.png` returns `200`
- [ ] Facebook Sharing Debugger accepts it: https://developers.facebook.com/tools/debug/
- [ ] Twitter Card Validator shows `summary_large_image`: https://cards-dev.twitter.com/validator

### 4. Commit + PR

Since Sprint 1's PR #2 is still open and unmerged, the cleanest path is:

- **Option A (preferred if PR #2 not yet merged):** push this as a 7th
  commit on the existing `seo/fast-track-sprint-1` branch. PR #2 picks
  it up automatically.
- **Option B (if PR #2 already merged):** create a new branch
  `seo/fast-track-og-image` off `main`, commit, open a small follow-up PR.

Commit message:

```
feat(seo): branded 1200×630 OG image for Fast Track

Replaces the /apple-touch-icon.png fallback with a purpose-built
Trip Sorted — Fast Track OG image at /og/fast-track-default.png.
Validated via Facebook Sharing Debugger + Twitter Card Validator.

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Per the user's global CLAUDE.md rules:** never commit or push without
explicit user confirmation. Show the plan, wait for approval.

---

## What you should NOT do

- ❌ Re-run the Sprint 1 code changes — they're committed and in PR #2.
- ❌ Re-run the FAST_TRACK audit (`scripts/run_audit.py --product fast_track`)
  — the audit output is already committed.
- ❌ Set Vercel env vars — user is handling that separately.
- ❌ Touch Sprint 2+ architectural tickets (ARCH-006..009) — each is
  its own follow-up sprint.

---

## Also-pending for the user (not your job, but so you know)

- ⏸️ Merge PR #2 on `fast-track-ai`
- ⏸️ `NEXT_PUBLIC_SITE_URL=https://travel-synch.com` on Vercel
  (production, preview, development)
- ⏸️ Submit the new sitemap in Google Search Console for the
  `travel-synch.com` property
- ⏸️ Monitor `/en/*` → `/*` 301 report in GSC for 2 weeks post-deploy

---

## Reference documents (in `design-system` repo)

- **Execution prompt (source of truth for Sprint 1):**
  `audits/seo-pagespeed-audit/fix-seo-plans/fast_track-claude-code-prompt.md`
- **Audit tickets:**
  `audits/seo-pagespeed-audit/fix-seo-plans/fast_track.md`
- **Portfolio kanban:**
  `audits/seo-pagespeed-audit/fix-seo-plans/portfolio.html`

---

## Sprint 2+ roadmap (context only — not your job)

When Sprint 1 merges, the next tickets queued for FAST_TRACK are:

- **ARCH-006** — JS bundle code-split (+20 perf, 1w, P1)
- **ARCH-007** — Image pipeline `next/image` + AVIF/WebP (+10 perf, 3d, P2)
- **ARCH-008** — Centralise hreflang in middleware (+12 SEO, 4d, P1)
- **ARCH-009** — 301-migrate legacy `airport-fast-track.trip-sorted.com`
  → `travel-synch.com` (biggest single SEO lever, DevOps-owned, 2w)

Each one warrants its own spec + handoff. Don't start any of these from
this handoff.
