# SEO Portfolio — Session Notes

**Last updated:** 2026-04-22 (end-of-day)
**Next session:** resume from "Tomorrow starts here" section at bottom.

---

## 2026-04-22 — Fast Track Sprint 1 finalised + Sprint 2 code shipped

### Sprint 1 completion (branch `seo/fast-track-sprint-1`, PR #2)

PR #2 picked up 2 new commits today, bringing it to 8 commits:

```
16cf552  feat(seo): branded 1200x630 OG image (FAST_TRACK-FIX-004)
8fcf51d  fix(seo): restore src/config/site.config.ts removed in d182b8e
d2517f6  feat(seo): schema.org JSON-LD (FIX-005)
98786f0  feat(seo): canonicals + hreflang + OG (FIX-002/003/004)
48af484  feat(seo): dynamic sitemap.xml + robots.txt (FIX-001)
a9a3fe0  feat(seo): localePrefix as-needed + 301 /en/* → /* (PREREQ)
90798c3  chore(seo): metadataBase + robots defaults
d182b8e  chore(seo): shared site config + pageMetadata helper
```

- **Build-break fix** — the original `d182b8e` deleted
  `src/config/site.config.ts` on the premise that `site.ts` replaced it,
  but 20+ files still imported `siteConfig` (pricing, api.baseUrl, etc.)
  that `site.ts` doesn't export. Restored the file verbatim; both now
  coexist with clear separation.
- **Branded OG image** — `public/og/fast-track-default.png`, 1200×630,
  356 KB, resized from the user-supplied TravelSynch card. Closed the
  last unchecked acceptance box on `FAST_TRACK-FIX-004`.

### Sprint 2 code shipped (branch `seo/fast-track-sprint-2`, stacked on sprint-1)

**NOT pushed.** Awaits Sprint 1 merge so Sprint 2's PR can rebase onto
`main` cleanly. Four commits, one per ticket:

```
(pending push) feat(seo): legacy-host 301 redirect config + flag (FAST_TRACK-ARCH-009)
(pending push) fix(seo): x-default in sitemap, DRY via languageAlternatesFor (FAST_TRACK-ARCH-008)
(pending push) perf(images): AVIF+WebP config + CLS dims on checkout SVGs (FAST_TRACK-ARCH-007)
(pending push) perf(seo): lazy-load below-fold + route-split landings (FAST_TRACK-ARCH-006)
```

Full detail: `audits/seo-pagespeed-audit/fast_track-sprint-2-handoff.md`.

### Portfolio kanban

- `status_overrides.json` bumped to `schema_version: 4`
- `FAST_TRACK-ARCH-006..009` seeded as `in_progress`
- `portfolio.html` regenerated (58 tickets total)

### Known blocker for verification

- **Node 25 vs Next 16.2.1 edge-runtime bug** prevented `next build` /
  `next dev` from completing locally after the first successful run. The
  error (`TypeError: (0 , import_load.load) is not a function`) does not
  occur on Vercel's CI (Node 20/22). Re-run the audit after deploy to
  verify Sprint 2's perf gains.

---

## Tomorrow starts here

Open `FILE_GUIDE.md` first — it indexes every .md in this folder and
says which are active vs historical.

### User actions still blocking both Fast Track PRs

1. **Merge PR #2** (`seo/fast-track-sprint-1`) → https://github.com/Sanjow-Ventures/fast-track-ai/pull/2
2. **Mark PR #3 ready for review** once #2 has merged
   (GitHub will auto-retarget its base from `seo/fast-track-sprint-1`
   to `main`): https://github.com/Sanjow-Ventures/fast-track-ai/pull/3
3. **Vercel env var:** `NEXT_PUBLIC_SITE_URL=https://travel-synch.com`
   (production + preview + development).
4. **ARCH-009 activation** — only after PR #3 is merged and DNS is
   wired. Full checklist:
   `fast-track-ai/docs/arch-009-legacy-migration.md`.

### After PR #2 + #3 both deploy

```bash
cd audits/seo-pagespeed-audit
python3 scripts/run_audit.py --product fast_track
```

Expected deltas from this morning's baseline (SEO 49.7 / Perf 60.7):
- SEO  → **≥ 80** (all five FIX + ARCH-008 + ARCH-009 after activation)
- Perf → **≥ 75** (ARCH-006 code-split + ARCH-007 AVIF/WebP)

### Still-open, lower priority

- Publishing + update workflow for the portfolio kanban (4 options
  still on the table from 2026-04-21 — see `git log 6a01e00..` for
  context). Not blocking Fast Track; defer until Fast Track deploys.
- Other products' tickets (WePDF, TOPUP, VISA_PORTALS, AIRPORT_CHECKIN)
  have audit artefacts but no sprint branches yet.

---

## What's done this session

### Repo 1 — `fast-track-ai` (SEO Sprint 1 implementation)

- **Branch:** `seo/fast-track-sprint-1` pushed to origin
- **PR:** https://github.com/Sanjow-Ventures/fast-track-ai/pull/2 (open, awaiting review)
- **Base:** `main`
- **6 ticket-aligned commits:**
  ```
  d2517f6  feat(seo): schema.org JSON-LD (FIX-005)
  98786f0  feat(seo): canonicals + hreflang + OG (FIX-002/003/004)
  48af484  feat(seo): dynamic sitemap.xml + robots.txt (FIX-001)
  a9a3fe0  feat(seo): localePrefix as-needed + 301s (PREREQ)
  90798c3  chore(seo): metadataBase + robots defaults
  d182b8e  chore(seo): shared site config + pageMetadata helper
  ```
- **Canonical host confirmed:** `https://travel-synch.com`

### Repo 2 — `design-system` (audit artifacts + portfolio)

All pushed to `origin/main`. 9 new commits from the session:

```
07ed736  audits(portfolio): fold status overrides into builder (drift fix)
6a01e00  audits(portfolio): mark FAST_TRACK FIX-001..005 as done
7f4daef  audits: portfolio roll-up — manifest, scores, kanban
e7ac775  audits: visa portals product audit (VISA_PORTALS)
5057507  audits: topup product audit (TOPUP)
aba76ae  audits: airport check-in product audit (AIRPORT_CHECKIN)
8fc9670  audits: wepdf re-audit refresh (WEPDF)
205f839  audits: tooling — portfolio kanban builder + ignore scratch
ddf4f63  audits: fast-track product audit + sprint-1 execution prompt
```

**New source-of-truth file:**
`fix-seo-plans/status_overrides.json` — seeds ticket statuses on fresh
browser loads. Bump `schema_version` when you change the map.

**Portfolio kanban:**
`audits/seo-pagespeed-audit/fix-seo-plans/portfolio.html` — standalone
static HTML; no build required. Regenerate via
`python scripts/build_portfolio_kanban.py`.

---

## Deferred (user-owned, not session work)

- [ ] Merge PR #2 on `fast-track-ai`
- [ ] `NEXT_PUBLIC_SITE_URL=https://travel-synch.com` on Vercel (prod + preview + dev)
- [ ] Submit new sitemap in Google Search Console (travel-synch.com property)
- [ ] Monitor `/en/*` → `/*` 301 report in GSC for 2 weeks post-deploy
- [ ] Branded 1200×630 OG image — handoff prompt ready in
      `audits/seo-pagespeed-audit/fast_track-handoff.md` (for Claude Desktop session)

---

## Status update workflow (today's shape — may get better tomorrow)

Current manual flow to mark a ticket done:

```bash
# 1. Edit the source-of-truth
$EDITOR audits/seo-pagespeed-audit/fix-seo-plans/status_overrides.json
#    - change the ticket's value to "done" (or "in_progress" / "todo")
#    - bump "schema_version" by 1 so browsers migrate

# 2. Regenerate the kanban HTML
cd audits/seo-pagespeed-audit
python scripts/build_portfolio_kanban.py

# 3. Commit + push
cd /Users/srikan/Documents/GitHub/Sanjow/Sanjow-Ventures/design-system
git add audits/seo-pagespeed-audit/fix-seo-plans/{status_overrides.json,portfolio.html}
git commit -m "audits(portfolio): mark <TICKET-ID> as <status>"
git push origin main
```

**Schema-bump caveat:** the migration only rewrites tickets currently at
`todo` (to preserve manual drag-and-drop). Browsers that saw a prior
version with a ticket at `in_progress` will *not* auto-migrate that
ticket to `done` — click "Reset board state" or drag manually.

Option 3 from tomorrow's checklist (`update_status.py`) collapses steps
1 + 2 into one command.

---

## Working tree state (end of session)

```
branch:   main
synced:   origin/main at 07ed736
clean:    yes (except these intentional leftovers)

Untracked (intentionally left alone):
  PDF/                                    # outside audits scope
  audits/seo-pagespeed-audit/fast_track-handoff.md
                                          # handoff for Claude Desktop OG work;
                                          # decide tomorrow: commit, gitignore, or delete

Gitignored (scratch patch artefacts):
  audits/seo-pagespeed-audit/fast_track-prompt-patch*.md
  audits/seo-pagespeed-audit/fast_track-prompt-patch*.zip
```

---

## Key file locations

| Purpose | Path |
|---|---|
| This progress doc | `audits/seo-pagespeed-audit/SESSION-NOTES.md` |
| Portfolio kanban HTML | `audits/seo-pagespeed-audit/fix-seo-plans/portfolio.html` |
| Kanban status source | `audits/seo-pagespeed-audit/fix-seo-plans/status_overrides.json` |
| Kanban builder script | `audits/seo-pagespeed-audit/scripts/build_portfolio_kanban.py` |
| Audit orchestrator | `audits/seo-pagespeed-audit/scripts/run_audit.py` |
| Fast Track sprint prompt | `audits/seo-pagespeed-audit/fix-seo-plans/fast_track-claude-code-prompt.md` |
| OG image handoff prompt | `audits/seo-pagespeed-audit/fast_track-handoff.md` |
| Fast Track codebase | `/Users/srikan/Documents/GitHub/Sanjow/Sanjow-Ventures/fast-track-ai` |

---

## Verification one-liners (if state feels off tomorrow)

```bash
# design-system repo state
cd /Users/srikan/Documents/GitHub/Sanjow/Sanjow-Ventures/design-system
git log --oneline origin/main -10
git status -s

# fast-track-ai repo state
cd /Users/srikan/Documents/GitHub/Sanjow/Sanjow-Ventures/fast-track-ai
git branch --show-current           # → seo/fast-track-sprint-1
git log --oneline main..HEAD        # → 6 sprint commits

# portfolio regen smoke test
cd /Users/srikan/Documents/GitHub/Sanjow/Sanjow-Ventures/design-system/audits/seo-pagespeed-audit
python3 scripts/build_portfolio_kanban.py
# expect: "✓ wrote fix-seo-plans/portfolio.html — 5 product(s), 54 tickets …"
```
