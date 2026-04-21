"""
Turn audit findings into a sprint-ready fix plan.

Outputs two artifacts per product:
  - fix-seo-plans/{product_id}.md   — copy-pasteable ticket list (Linear/GitHub)
  - fix-seo-plans/{product_id}.html — standalone kanban board (To-do / In-progress / Done)

The plan layers two categories of tickets:
  1. **In-place fixes** — one ticket per distinct (field, fix) pair from the
     audit's P0/P1/P2 findings. These map directly to the audit's "fixable-in-place" set.
  2. **Architectural tickets** — synthesised only when `strategic["supports"]` is
     "B" or "C". These reflect the rebuild-path work (bundle split, image
     modernisation, i18n middleware, legacy sunset, LCP rewrite) and are
     intentionally coarser — each owns a multi-day workstream, not a 1h ticket.

Tickets get a deterministic ID (`{PRODUCT}-FIX-{###}`) so they can be referenced
across PRs, Linear issues, and weekly reviews without renumbering.
"""
from __future__ import annotations

import html
import json
from datetime import datetime, timezone


# ─── heuristics (owner / effort / lift / description) ─────────────────────
# Keyed by the finding's `field` so we stay concrete. The lift is an estimate
# of score points gained if fixed — matches report.py's _FIELD_HEURISTICS.
_FIELD_HEUR = {
    "sitemap.xml":               {"owner": "Frontend", "effort": "1h",  "lift": 4,  "area": "SEO"},
    "Sitemap directive":         {"owner": "DevOps",   "effort": "10m", "lift": 2,  "area": "SEO"},
    "Strict-Transport-Security": {"owner": "DevOps",   "effort": "30m", "lift": 1,  "area": "SEO"},
    "meta robots":               {"owner": "Frontend", "effort": "30m", "lift": 15, "area": "SEO"},
    "<title>":                   {"owner": "Content",  "effort": "1h",  "lift": 5,  "area": "SEO"},
    "<title> length":            {"owner": "Content",  "effort": "30m", "lift": 2,  "area": "SEO"},
    "meta description":          {"owner": "Content",  "effort": "1h",  "lift": 4,  "area": "SEO"},
    "canonical link":            {"owner": "Frontend", "effort": "30m", "lift": 3,  "area": "SEO"},
    "h1 count":                  {"owner": "Frontend", "effort": "1h",  "lift": 2,  "area": "SEO"},
    "Open Graph":                {"owner": "Frontend", "effort": "1h",  "lift": 2,  "area": "SEO"},
    "JSON-LD":                   {"owner": "Frontend", "effort": "2h",  "lift": 4,  "area": "SEO"},
    "hreflang coverage":         {"owner": "Frontend", "effort": "3h",  "lift": 8,  "area": "SEO"},
    "mobile LCP p75":            {"owner": "Frontend", "effort": "1d",  "lift": 12, "area": "Perf"},
    "CLS p75":                   {"owner": "Frontend", "effort": "4h",  "lift": 6,  "area": "Perf"},
    "INP p75":                   {"owner": "Frontend", "effort": "1d",  "lift": 8,  "area": "Perf"},
}
_DEFAULT_HEUR = {"owner": "Frontend", "effort": "?", "lift": 1, "area": "SEO"}


# ─── public entry point ────────────────────────────────────────────────────
def render_fix_plan(
    *,
    product_id: str,
    product_name: str,
    findings_by_severity: dict,
    strategic: dict,
    perf_breakdown: dict,
    seo_score: float,
    perf_score: float,
    domains: list[dict],
    url_rows: list[dict] | None = None,
    audit_date: str | None = None,
) -> tuple[str, str, dict]:
    """Return (markdown, html, data_dict). Caller writes each to disk.

    The data_dict is a structured snapshot of the plan — useful for the
    portfolio aggregator (`build_portfolio_kanban.py`) which reads one
    .json sidecar per product and merges them into a cross-product board.
    """
    audit_date = audit_date or datetime.now(timezone.utc).isoformat(timespec="seconds")

    tickets = _build_tickets(
        product_id=product_id,
        findings_by_severity=findings_by_severity,
        strategic=strategic,
        perf_breakdown=perf_breakdown,
        domains=domains,
    )

    data = {
        "meta": {
            "product_id": product_id,
            "product_name": product_name,
            "audit_date": audit_date,
            "seo_score": seo_score,
            "perf_score": perf_score,
            "decision": strategic.get("supports", "?"),
            "triggered_rules": strategic.get("triggered_rules", []),
        },
        "tickets": tickets,
    }

    md = _render_md(
        product_id=product_id, product_name=product_name,
        tickets=tickets, strategic=strategic,
        seo_score=seo_score, perf_score=perf_score,
        audit_date=audit_date,
    )
    html_out = _render_html(
        product_id=product_id, product_name=product_name,
        tickets=tickets, strategic=strategic,
        seo_score=seo_score, perf_score=perf_score,
        audit_date=audit_date,
    )
    return md, html_out, data


# ─── ticket builder ────────────────────────────────────────────────────────
def _build_tickets(
    *,
    product_id: str,
    findings_by_severity: dict,
    strategic: dict,
    perf_breakdown: dict,
    domains: list[dict],
) -> list[dict]:
    tickets: list[dict] = []
    seen: set[tuple] = set()
    counter = 1
    prefix = product_id.upper().replace("-", "")

    # (1) In-place fix tickets — one per (field, fix) pair, ranked by severity
    for sev in ("P0", "P1", "P2"):
        for f in findings_by_severity.get(sev, []):
            key = (f["field"], f["fix"])
            if key in seen:
                # accumulate affected URLs on the existing ticket
                for t in tickets:
                    if t["_key"] == key:
                        if f["url"] not in t["affected_urls"]:
                            t["affected_urls"].append(f["url"])
                        break
                continue
            seen.add(key)
            h = _FIELD_HEUR.get(f["field"], _DEFAULT_HEUR)
            tickets.append({
                "id": f"{prefix}-FIX-{counter:03d}",
                "kind": "in_place",
                "severity": sev,
                "priority": sev,
                "area": h["area"],
                "field": f["field"],
                "title": f"{f['field']} — {f['fix']}",
                "problem": f"Current: `{f['current']}`. Target: `{f['target']}`.",
                "fix": f["fix"],
                "acceptance": _acceptance_for(f),
                "owner": h["owner"],
                "effort": h["effort"],
                "lift": h["lift"],
                "label": f.get("label", "fixable-in-place"),
                "affected_urls": [f["url"]],
                "_key": key,
            })
            counter += 1

    # (2) Architectural tickets — only when audit supports Option B or C
    if strategic.get("supports") in ("B", "C"):
        arch_tickets = _build_architectural_tickets(
            prefix=prefix, counter_start=counter,
            perf_breakdown=perf_breakdown,
            findings_by_severity=findings_by_severity,
            domains=domains, strategic=strategic,
        )
        tickets.extend(arch_tickets)

    # Strip internal key before returning
    for t in tickets:
        t.pop("_key", None)
    return tickets


def _build_architectural_tickets(
    *, prefix: str, counter_start: int,
    perf_breakdown: dict, findings_by_severity: dict,
    domains: list[dict], strategic: dict,
) -> list[dict]:
    """Synthesise rebuild-path tickets when the audit supports Option B/C."""
    tickets = []
    c = counter_start

    # Bundle split — triggered when bundle_size sub-score < 50
    bundle_info = (perf_breakdown or {}).get("bundle size", {}) or \
                  (perf_breakdown or {}).get("bundle_size", {})
    bundle_score = bundle_info.get("score")
    bundle_kb = (bundle_info.get("breakdown") or {}).get("total_js_kb")
    if bundle_score is not None and bundle_score < 50:
        tickets.append({
            "id": f"{prefix}-ARCH-{c:03d}",
            "kind": "architectural",
            "severity": "P1",
            "priority": "P1",
            "area": "Perf",
            "field": "JS bundle",
            "title": "Code-split and tree-shake the JS bundle",
            "problem": (
                f"Total JS {bundle_kb}KB is above the 350KB budget. Unused JS "
                f"ships on every page load and drags mobile Perf below 40."
            ),
            "fix": (
                "Introduce route-level dynamic imports, audit heavy deps "
                "(replace or lazy-load), enable tree-shaking, split vendor chunks."
            ),
            "acceptance": [
                "First-load JS for `/` route ≤ 350KB (transferred)",
                "No single chunk > 150KB",
                "Mobile Lighthouse perf improves by ≥ 15 points",
                "`Reduce unused JavaScript` Lighthouse audit drops below 50KB savings",
            ],
            "owner": "Frontend",
            "effort": "1w",
            "lift": 20,
            "label": "architectural",
            "affected_urls": [d["url"] for d in domains if d.get("role") == "clean"] or
                             [d["url"] for d in domains],
        })
        c += 1

    # Image modernisation — triggered when image score < 60
    img_info = (perf_breakdown or {}).get("image optimisation", {}) or \
               (perf_breakdown or {}).get("image_optimisation", {})
    img_score = img_info.get("score")
    if img_score is not None and img_score < 60:
        tickets.append({
            "id": f"{prefix}-ARCH-{c:03d}",
            "kind": "architectural",
            "severity": "P2",
            "priority": "P2",
            "area": "Perf",
            "field": "Image pipeline",
            "title": "Migrate image pipeline to next/image with AVIF+WebP",
            "problem": (
                "Images aren't served in modern formats, aren't lazy-loaded "
                "below the fold, and aren't responsively sized. LCP and CLS "
                "both suffer."
            ),
            "fix": (
                "Replace <img> with next/image across the app. Configure "
                "next.config.js for AVIF+WebP, set width/height everywhere, "
                "add blur placeholders for hero images."
            ),
            "acceptance": [
                "All product images use next/image",
                "Modern formats audit passes (≥ 90% AVIF/WebP)",
                "CLS p75 < 0.1 on all T1 URLs",
                "Hero LCP drops by ≥ 500ms on mobile",
            ],
            "owner": "Frontend",
            "effort": "3d",
            "lift": 10,
            "label": "architectural",
            "affected_urls": [d["url"] for d in domains if d.get("role") == "clean"] or
                             [d["url"] for d in domains],
        })
        c += 1

    # i18n middleware rewrite — triggered when any hreflang finding exists
    all_findings = [f for b in findings_by_severity.values() for f in b]
    if any("hreflang" in f.get("field", "") for f in all_findings):
        tickets.append({
            "id": f"{prefix}-ARCH-{c:03d}",
            "kind": "architectural",
            "severity": "P1",
            "priority": "P1",
            "area": "SEO",
            "field": "i18n middleware",
            "title": "Rewrite locale routing to emit hreflang + x-default centrally",
            "problem": (
                "Per-route hreflang scattershot across pages. An architectural "
                "fix centralises the map so adding a locale is a one-line change "
                "instead of N page edits."
            ),
            "fix": (
                "Move locale detection + hreflang emission into Next.js "
                "middleware. Generate `<link rel=alternate>` for every locale "
                "route + x-default at build time from a single source."
            ),
            "acceptance": [
                "All T1/T2 URLs emit hreflang tags for every configured locale + x-default",
                "Adding a new locale requires only a config entry",
                "Google Search Console `Hreflang` report shows 0 errors after 2 weeks",
            ],
            "owner": "Frontend",
            "effort": "4d",
            "lift": 12,
            "label": "architectural",
            "affected_urls": [d["url"] for d in domains],
        })
        c += 1

    # LCP critical path rewrite — when mobile LH perf is critical
    if strategic.get("supports") == "B" and \
       any("PerfScore<40" in r for r in strategic.get("triggered_rules", [])):
        tickets.append({
            "id": f"{prefix}-ARCH-{c:03d}",
            "kind": "architectural",
            "severity": "P0",
            "priority": "P0",
            "area": "Perf",
            "field": "Critical rendering path",
            "title": "Rewrite critical rendering path for mobile LCP",
            "problem": (
                "Mobile Perf below 40 indicates blocking resources in the "
                "critical path. Targeted fixes alone won't clear the bar — "
                "needs an architectural pass."
            ),
            "fix": (
                "Audit the critical chain: inline critical CSS, defer non-"
                "critical JS, preload LCP image/font, eliminate redirect "
                "chains on the landing URL, move to streaming SSR."
            ),
            "acceptance": [
                "Mobile Lighthouse perf ≥ 70",
                "CrUX LCP p75 ≤ 2.5s (mobile)",
                "No redirect chain > 1 hop from primary landing URLs",
                "Critical CSS inlined ≤ 14KB",
            ],
            "owner": "Frontend",
            "effort": "1w",
            "lift": 25,
            "label": "architectural",
            "affected_urls": [d["url"] for d in domains if d.get("role") == "clean"] or
                             [d["url"] for d in domains],
        })
        c += 1

    # Legacy sunset — when a legacy domain exists alongside clean
    legacy = [d for d in domains if d.get("role") == "legacy"]
    clean = [d for d in domains if d.get("role") == "clean"]
    if legacy and clean:
        tickets.append({
            "id": f"{prefix}-ARCH-{c:03d}",
            "kind": "architectural",
            "severity": "P1",
            "priority": "P1",
            "area": "SEO",
            "field": "Legacy sunset",
            "title": f"301-migrate and sunset legacy domain {legacy[0]['url']}",
            "problem": (
                f"Maintaining both {legacy[0]['url']} and {clean[0]['url']} "
                f"splits link equity and confuses canonicalisation. The audit "
                f"supports consolidating onto the clean domain."
            ),
            "fix": (
                "Map every legacy URL to its clean equivalent, issue 301s, "
                "update canonicals, submit change-of-address in Google Search "
                "Console, keep the legacy cert valid for 12 months post-cut."
            ),
            "acceptance": [
                "All legacy URLs 301 to clean equivalents (no 302s, no chains)",
                "Canonicals on clean pages are self-referential",
                "GSC change-of-address submitted and accepted",
                "Organic traffic on clean domain ≥ 80% of legacy baseline within 90 days",
            ],
            "owner": "DevOps",
            "effort": "2w",
            "lift": 15,
            "label": "architectural",
            "affected_urls": [legacy[0]["url"], clean[0]["url"]],
        })
        c += 1

    return tickets


def _acceptance_for(finding: dict) -> list[str]:
    """Generate testable acceptance criteria from a finding."""
    field = finding["field"]
    target = finding["target"]
    generic = [f"{field} matches target: {target}", "Re-run audit confirms the check passes"]

    per_field = {
        "sitemap.xml": [
            "`/sitemap.xml` returns 200 with valid XML",
            "Sitemap lists every locale route",
            "Sitemap referenced from `/robots.txt`",
        ],
        "meta robots": [
            "No `<meta name=\"robots\" content=\"noindex\">` on indexable routes",
            "Lighthouse SEO 'Page isn't blocked from indexing' passes",
        ],
        "canonical link": [
            "Every indexable page emits a self-referential `<link rel=\"canonical\">`",
            "Canonical URL uses the clean-domain host and correct locale",
        ],
        "hreflang coverage": [
            "All configured locales emit `<link rel=\"alternate\" hreflang=...>`",
            "`x-default` hreflang is present",
            "Each hreflang URL returns 200 (no redirects)",
        ],
        "<title>": [
            "`<title>` is present and 30–60 chars",
            "Title is unique per route",
        ],
        "<title> length": [
            "`<title>` is 30–60 chars on all audited pages",
        ],
        "meta description": [
            "`<meta name=\"description\">` is present and 50–160 chars on every page",
            "Description is unique per route",
        ],
        "Open Graph": [
            "og:title, og:description, og:image, og:url, og:type all present",
            "og:image is ≥ 1200×630 and < 1MB",
        ],
        "JSON-LD": [
            "Relevant schema.org type(s) emitted as application/ld+json",
            "Google Rich Results Test passes",
        ],
        "h1 count": [
            "Exactly one `<h1>` per page",
            "h1 text reflects the page's primary entity",
        ],
        "mobile LCP p75": [
            "CrUX mobile LCP p75 ≤ 2.5s after 28-day window",
            "Lab LCP ≤ 2.5s on Lighthouse mobile run",
        ],
        "CLS p75": [
            "CrUX CLS p75 < 0.1",
            "No layout-shift debug overlay warnings in DevTools",
        ],
        "INP p75": [
            "CrUX INP p75 < 200ms",
        ],
    }
    return per_field.get(field, generic)


# ─── markdown renderer ────────────────────────────────────────────────────
def _render_md(
    *, product_id: str, product_name: str, tickets: list[dict],
    strategic: dict, seo_score: float, perf_score: float, audit_date: str,
) -> str:
    lines: list[str] = []
    lines.append(f"# {product_name} — SEO + PageSpeed Fix Plan\n")
    lines.append(f"_Generated {audit_date} · "
                 f"[audit report](../products/{product_id}.md) · "
                 f"[dashboard](../products/{product_id}.jsx)_\n")

    # Summary block
    lines.append("## Sprint summary\n")
    summary = _compute_summary(tickets, seo_score, perf_score, strategic)
    lines.append(summary)
    lines.append("")

    # Group by kind + priority
    in_place = [t for t in tickets if t["kind"] == "in_place"]
    arch = [t for t in tickets if t["kind"] == "architectural"]

    lines.append("## In-place fixes\n")
    for sev in ("P0", "P1", "P2"):
        sev_tickets = [t for t in in_place if t["priority"] == sev]
        if not sev_tickets:
            continue
        lines.append(f"### {sev} — "
                     f"{'Must-fix' if sev == 'P0' else 'Should-fix' if sev == 'P1' else 'Nice-to-have'}\n")
        for t in sev_tickets:
            lines.append(_format_ticket_md(t))
            lines.append("")

    if arch:
        lines.append("## Architectural workstreams\n")
        lines.append("_These tickets reflect the Option-B rebuild path. "
                     "Each owns a multi-day workstream rather than a quick fix._\n")
        for t in sorted(arch, key=lambda x: {"P0": 0, "P1": 1, "P2": 2}[x["priority"]]):
            lines.append(_format_ticket_md(t))
            lines.append("")

    lines.append("## How to use this plan\n")
    lines.append("1. Copy each ticket into Linear / GitHub Issues — IDs stay "
                 "stable across audit re-runs so you can cross-reference.")
    lines.append(f"2. Track status on the kanban board: "
                 f"`fix-seo-plans/{product_id}.html` (open in a browser — "
                 f"status persists in localStorage).")
    lines.append("3. Re-run `python scripts/run_audit.py --product "
                 f"{product_id}` after shipping — the plan regenerates but "
                 f"IDs remain deterministic so tickets you've already filed "
                 f"can be updated in-place.")
    return "\n".join(lines) + "\n"


def _compute_summary(tickets: list[dict], seo_score: float, perf_score: float,
                     strategic: dict) -> str:
    p0 = sum(1 for t in tickets if t["priority"] == "P0")
    p1 = sum(1 for t in tickets if t["priority"] == "P1")
    p2 = sum(1 for t in tickets if t["priority"] == "P2")
    by_owner: dict[str, int] = {}
    for t in tickets:
        by_owner[t["owner"]] = by_owner.get(t["owner"], 0) + 1
    total_lift = sum(t["lift"] for t in tickets)
    arch_count = sum(1 for t in tickets if t["kind"] == "architectural")

    lines = []
    lines.append(f"- **Total tickets:** {len(tickets)} "
                 f"({len(tickets) - arch_count} in-place, {arch_count} architectural)")
    lines.append(f"- **By priority:** P0={p0}, P1={p1}, P2={p2}")
    lines.append(f"- **By owner:** " +
                 ", ".join(f"{k}={v}" for k, v in sorted(by_owner.items())))
    lines.append(f"- **Estimated total lift:** +{total_lift} score points "
                 f"(current: SEO {seo_score}, Perf {perf_score})")
    lines.append(f"- **Audit decision:** Option **{strategic.get('supports', '?')}**"
                 + (" — architectural workstreams included"
                    if strategic.get("supports") in ("B", "C") else ""))
    return "\n".join(lines)


def _format_ticket_md(t: dict) -> str:
    urls = "\n".join(f"  - `{_short(u)}`" for u in t["affected_urls"])
    accept = "\n".join(f"- [ ] {a}" for a in t["acceptance"])
    return (
        f"#### `{t['id']}` — {t['title']}\n\n"
        f"**Priority:** {t['priority']} · **Owner:** {t['owner']} · "
        f"**Effort:** {t['effort']} · **Est. lift:** +{t['lift']} · "
        f"**Area:** {t['area']} · **Type:** {t['label']}\n\n"
        f"**Problem**\n\n{t['problem']}\n\n"
        f"**Fix**\n\n{t['fix']}\n\n"
        f"**Affected**\n\n{urls}\n\n"
        f"**Acceptance criteria**\n\n{accept}\n\n"
        f"---"
    )


def _short(url: str) -> str:
    return url.replace("https://", "").replace("http://", "")


# ─── kanban HTML renderer ─────────────────────────────────────────────────
def _render_html(
    *, product_id: str, product_name: str, tickets: list[dict],
    strategic: dict, seo_score: float, perf_score: float, audit_date: str,
) -> str:
    payload = json.dumps({
        "meta": {
            "product_id": product_id,
            "product_name": product_name,
            "audit_date": audit_date,
            "seo_score": seo_score,
            "perf_score": perf_score,
            "decision": strategic.get("supports", "?"),
            "triggered_rules": strategic.get("triggered_rules", []),
        },
        "tickets": tickets,
    }, indent=2)
    safe_name = html.escape(product_name)
    return _HTML_TEMPLATE.replace("__PAYLOAD__", payload)\
                         .replace("__PRODUCT_NAME__", safe_name)\
                         .replace("__PRODUCT_ID__", product_id)


_HTML_TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<title>__PRODUCT_NAME__ — Fix Plan (Kanban)</title>
<meta name="viewport" content="width=device-width, initial-scale=1" />
<script src="https://cdn.tailwindcss.com"></script>
<style>
  body { font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; }
  .col { min-height: 60vh; }
  .card { transition: transform .08s ease, box-shadow .08s ease; cursor: grab; }
  .card:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(0,0,0,.08); }
  .card.dragging { opacity: .5; cursor: grabbing; }
  details > summary { cursor: pointer; list-style: none; }
  details > summary::-webkit-details-marker { display: none; }
  [data-over="true"] { background: #fef3c7; }
</style>
</head>
<body class="bg-slate-50 text-slate-900">
<div class="max-w-7xl mx-auto p-6">

  <header class="flex flex-col md:flex-row md:items-end md:justify-between gap-3 mb-6">
    <div>
      <h1 class="text-2xl font-bold">__PRODUCT_NAME__ — Fix Plan</h1>
      <p id="meta-line" class="text-sm text-slate-600"></p>
    </div>
    <div class="flex items-center gap-2">
      <button id="reset-btn" class="text-xs text-slate-500 hover:text-red-600 underline">
        Reset board state
      </button>
    </div>
  </header>

  <!-- Filters -->
  <section class="bg-white rounded-lg border border-slate-200 p-4 mb-5 flex flex-wrap gap-4 items-center">
    <div>
      <label class="block text-xs font-semibold text-slate-500 mb-1">Search</label>
      <input id="search" type="search" placeholder="field, id, title…"
             class="border border-slate-300 rounded px-2 py-1 text-sm w-64" />
    </div>
    <div id="filter-priority" class="flex flex-col gap-1">
      <span class="text-xs font-semibold text-slate-500">Priority</span>
      <div class="flex gap-1"></div>
    </div>
    <div id="filter-owner" class="flex flex-col gap-1">
      <span class="text-xs font-semibold text-slate-500">Owner</span>
      <div class="flex gap-1"></div>
    </div>
    <div id="filter-label" class="flex flex-col gap-1">
      <span class="text-xs font-semibold text-slate-500">Type</span>
      <div class="flex gap-1"></div>
    </div>
    <div id="filter-area" class="flex flex-col gap-1">
      <span class="text-xs font-semibold text-slate-500">Area</span>
      <div class="flex gap-1"></div>
    </div>
  </section>

  <!-- Progress bar -->
  <section class="bg-white rounded-lg border border-slate-200 p-4 mb-5">
    <div class="flex items-center justify-between mb-2">
      <span class="text-sm font-semibold">Progress</span>
      <span id="progress-label" class="text-sm text-slate-600"></span>
    </div>
    <div class="w-full bg-slate-200 rounded h-2 overflow-hidden">
      <div id="progress-bar" class="bg-emerald-500 h-2 transition-all" style="width:0%"></div>
    </div>
  </section>

  <!-- Kanban columns -->
  <section class="grid grid-cols-1 md:grid-cols-3 gap-4">
    <div class="col bg-white rounded-lg border-2 border-slate-200 p-3" data-col="todo">
      <header class="flex items-center justify-between mb-2">
        <h2 class="font-semibold text-slate-800">📋 To-do</h2>
        <span class="text-xs text-slate-500 count"></span>
      </header>
      <div class="space-y-2 cards"></div>
    </div>
    <div class="col bg-white rounded-lg border-2 border-amber-200 p-3" data-col="in_progress">
      <header class="flex items-center justify-between mb-2">
        <h2 class="font-semibold text-amber-800">🔨 In progress</h2>
        <span class="text-xs text-slate-500 count"></span>
      </header>
      <div class="space-y-2 cards"></div>
    </div>
    <div class="col bg-white rounded-lg border-2 border-emerald-200 p-3" data-col="done">
      <header class="flex items-center justify-between mb-2">
        <h2 class="font-semibold text-emerald-800">✅ Done</h2>
        <span class="text-xs text-slate-500 count"></span>
      </header>
      <div class="space-y-2 cards"></div>
    </div>
  </section>

  <footer class="mt-8 text-xs text-slate-500">
    Board state persists in localStorage under key
    <code>fix-plan:__PRODUCT_ID__</code>. Regenerating the plan keeps ticket IDs
    stable, so statuses are preserved across audit re-runs.
  </footer>
</div>

<script>
const DATA = __PAYLOAD__;
const STORAGE_KEY = "fix-plan:" + DATA.meta.product_id;

// ─── state ────────────────────────────────────────────────────────
let state = loadState();
const filters = { priority: new Set(), owner: new Set(), label: new Set(), area: new Set(), q: "" };

function loadState() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    const parsed = raw ? JSON.parse(raw) : {};
    // Seed any new tickets as "todo"
    DATA.tickets.forEach(t => { if (!(t.id in parsed)) parsed[t.id] = "todo"; });
    return parsed;
  } catch (e) {
    return Object.fromEntries(DATA.tickets.map(t => [t.id, "todo"]));
  }
}
function saveState() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}

// ─── filter chips ────────────────────────────────────────────────
function buildFilters() {
  const groups = {
    priority: ["P0", "P1", "P2"],
    owner: [...new Set(DATA.tickets.map(t => t.owner))].sort(),
    label: [...new Set(DATA.tickets.map(t => t.label))].sort(),
    area: [...new Set(DATA.tickets.map(t => t.area))].sort(),
  };
  Object.entries(groups).forEach(([key, vals]) => {
    const el = document.querySelector(`#filter-${key} > div`);
    el.innerHTML = "";
    vals.forEach(v => {
      const btn = document.createElement("button");
      btn.textContent = v;
      btn.className = "px-2 py-0.5 text-xs rounded-full border border-slate-300 " +
                      "bg-white text-slate-700 hover:bg-slate-100";
      btn.onclick = () => {
        if (filters[key].has(v)) filters[key].delete(v); else filters[key].add(v);
        btn.classList.toggle("bg-blue-600");
        btn.classList.toggle("text-white");
        btn.classList.toggle("border-blue-600");
        render();
      };
      el.appendChild(btn);
    });
  });
}

// ─── render ──────────────────────────────────────────────────────
function matches(t) {
  const q = filters.q.toLowerCase();
  if (q && !`${t.id} ${t.title} ${t.field} ${t.area}`.toLowerCase().includes(q)) return false;
  if (filters.priority.size && !filters.priority.has(t.priority)) return false;
  if (filters.owner.size    && !filters.owner.has(t.owner))       return false;
  if (filters.label.size    && !filters.label.has(t.label))       return false;
  if (filters.area.size     && !filters.area.has(t.area))         return false;
  return true;
}

function priorityClasses(p) {
  return ({
    P0: "bg-red-100 text-red-800 border-red-300",
    P1: "bg-amber-100 text-amber-800 border-amber-300",
    P2: "bg-slate-100 text-slate-700 border-slate-300",
  })[p] || "bg-slate-100";
}

function cardHtml(t) {
  const urls = t.affected_urls
    .map(u => `<li class="font-mono text-[11px] text-slate-600">${u.replace(/^https?:\/\//, "")}</li>`)
    .join("");
  const accept = t.acceptance
    .map(a => `<li class="text-xs"><input type="checkbox" class="mr-1" /> ${a}</li>`)
    .join("");
  return `
    <details class="card bg-white rounded border border-slate-200 p-3" draggable="true" data-id="${t.id}">
      <summary>
        <div class="flex items-start justify-between gap-2">
          <div class="min-w-0">
            <div class="flex items-center gap-1 flex-wrap mb-1">
              <span class="font-mono text-[10px] text-slate-500">${t.id}</span>
              <span class="text-[10px] px-1.5 py-0.5 rounded border ${priorityClasses(t.priority)}">${t.priority}</span>
              <span class="text-[10px] px-1.5 py-0.5 rounded bg-slate-100 text-slate-600">${t.area}</span>
              ${t.kind === "architectural"
                ? '<span class="text-[10px] px-1.5 py-0.5 rounded bg-purple-100 text-purple-700">arch</span>'
                : ""}
            </div>
            <div class="text-sm font-medium text-slate-800 leading-snug">${t.title}</div>
            <div class="text-[11px] text-slate-500 mt-1">
              ${t.owner} · ${t.effort} · +${t.lift} lift
            </div>
          </div>
        </div>
      </summary>
      <div class="mt-3 pt-3 border-t border-slate-100 space-y-2">
        <div>
          <div class="text-[11px] font-semibold text-slate-500 uppercase tracking-wide mb-0.5">Problem</div>
          <div class="text-xs text-slate-700">${t.problem}</div>
        </div>
        <div>
          <div class="text-[11px] font-semibold text-slate-500 uppercase tracking-wide mb-0.5">Fix</div>
          <div class="text-xs text-slate-700">${t.fix}</div>
        </div>
        <div>
          <div class="text-[11px] font-semibold text-slate-500 uppercase tracking-wide mb-0.5">Affected URLs</div>
          <ul class="ml-4 list-disc">${urls}</ul>
        </div>
        <div>
          <div class="text-[11px] font-semibold text-slate-500 uppercase tracking-wide mb-0.5">Acceptance</div>
          <ul class="ml-4 list-none space-y-0.5 text-slate-700">${accept}</ul>
        </div>
      </div>
    </details>`;
}

function render() {
  document.querySelectorAll(".col .cards").forEach(el => el.innerHTML = "");
  const counts = { todo: 0, in_progress: 0, done: 0 };
  DATA.tickets.forEach(t => {
    if (!matches(t)) return;
    const status = state[t.id] || "todo";
    counts[status]++;
    const col = document.querySelector(`.col[data-col="${status}"] .cards`);
    col.insertAdjacentHTML("beforeend", cardHtml(t));
  });
  document.querySelectorAll(".col").forEach(col => {
    const s = col.dataset.col;
    col.querySelector(".count").textContent = `${counts[s]} ticket${counts[s] === 1 ? "" : "s"}`;
  });

  // Progress bar: done / total (all tickets, not just filtered)
  const total = DATA.tickets.length;
  const done = DATA.tickets.filter(t => state[t.id] === "done").length;
  const pct = total ? Math.round((done / total) * 100) : 0;
  document.getElementById("progress-bar").style.width = pct + "%";
  document.getElementById("progress-label").textContent =
    `${done} / ${total} complete (${pct}%)`;

  wireDragDrop();
}

// ─── drag & drop ────────────────────────────────────────────────
function wireDragDrop() {
  document.querySelectorAll(".card").forEach(card => {
    card.addEventListener("dragstart", e => {
      card.classList.add("dragging");
      e.dataTransfer.setData("text/plain", card.dataset.id);
    });
    card.addEventListener("dragend", () => card.classList.remove("dragging"));
  });
  document.querySelectorAll(".col").forEach(col => {
    col.addEventListener("dragover", e => { e.preventDefault(); col.dataset.over = "true"; });
    col.addEventListener("dragleave", () => { col.dataset.over = "false"; });
    col.addEventListener("drop", e => {
      e.preventDefault();
      col.dataset.over = "false";
      const id = e.dataTransfer.getData("text/plain");
      state[id] = col.dataset.col;
      saveState();
      render();
    });
  });
}

// ─── init ────────────────────────────────────────────────────────
document.getElementById("meta-line").innerHTML =
  `<span class="font-mono">${DATA.meta.product_id}</span> · ` +
  `SEO ${DATA.meta.seo_score} · Perf ${DATA.meta.perf_score} · ` +
  `Decision: <strong>Option ${DATA.meta.decision}</strong> · ` +
  `${DATA.meta.audit_date}`;

document.getElementById("search").addEventListener("input", e => {
  filters.q = e.target.value;
  render();
});
document.getElementById("reset-btn").addEventListener("click", () => {
  if (confirm("Reset all tickets to To-do?")) {
    state = Object.fromEntries(DATA.tickets.map(t => [t.id, "todo"]));
    saveState();
    render();
  }
});

buildFilters();
render();
</script>
</body>
</html>
"""
