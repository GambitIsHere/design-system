# File guide — open this first

Last updated **2026-04-22**. This file is the TL;DR index for every loose
`.md` in `audits/seo-pagespeed-audit/`. If any .md falls out of the table
below, add it here before committing.

## Start here

| File | When to open |
|---|---|
| [`SESSION-NOTES.md`](SESSION-NOTES.md) | Running session log. The "Tomorrow starts here" section is always current. |
| [`README.md`](README.md) | Repo-wide scaffold. Explains the audit pipeline (`scripts/run_audit.py`) and scoring methodology — read once, then rarely. |

## Active sprint artefacts

| File | Status | What it covers |
|---|---|---|
| [`fast_track-sprint-2-handoff.md`](fast_track-sprint-2-handoff.md) | **active** — Sprint 2 code shipped, PR #3 open | ARCH-006/007/008/009 — code complete, operator work pending |
| [`visa_portals-handoff.md`](visa_portals-handoff.md) | **active** — Option B fixes shipping on `seo/visa-portals-audit-fixes` in `global-visa-portal` | Separate from Fast Track; unrelated branch |
| [`fix-seo-plans/fast_track-claude-code-prompt.md`](fix-seo-plans/fast_track-claude-code-prompt.md) | **historical** — Sprint 1 execution prompt, now shipped | Reference only. Do not re-run — Sprint 1 code lives in `seo/fast-track-sprint-1`. |

## Done / historical reference only

Keeping these committed as the trail of decisions; none of them describe
work that's still open.

| File | Why kept |
|---|---|
| [`fast_track-handoff.md`](fast_track-handoff.md) | Sprint 1 handoff — asked Claude Desktop to produce a branded OG image. Superseded by commit `16cf552` in `fast-track-ai` (branded OG now shipped from `public/og/fast-track-default.png`). **Nothing to do here.** |

## Auto-generated (regen, don't hand-edit)

| Path | Regenerate with |
|---|---|
| `products/<product>.{md,jsx}` | `python3 scripts/run_audit.py --product <product>` |
| `fix-seo-plans/<product>.{md,html,json}` | same command (produced alongside) |
| `fix-seo-plans/portfolio.html` | `python3 scripts/build_portfolio_kanban.py` |
| `data/scores.csv` | per-product audit run |

## Source-of-truth (hand-edit, keep in git)

| File | Purpose |
|---|---|
| `fix-seo-plans/status_overrides.json` | Kanban seed map. Bump `schema_version` when the overrides change so browsers pick up the migration. |
| `data/og-mocks/` | Reference 1200×630 OG mocks (compressed). See `data/og-mocks/README.md`. |

## Scratch (gitignored, safe to nuke)

| Path | Notes |
|---|---|
| `fast_track-prompt-patch*.md`, `*.zip` | Scratch patches from 2026-04-21 Sprint 1 planning. Gitignored. |
| `PDF/` | Personal — not audit-related. |
| `.claude/` | Session scratch. |

---

## Rule for tomorrow

If a new `.md` lands in this folder, **add a row to one of the tables
above before committing**. A bare filename in git history = confusion
two weeks from now. A one-line entry here = orientation in 10 seconds.
