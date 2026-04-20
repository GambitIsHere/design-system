"""
Render the per-product markdown report — lean exec-summary + next-steps format.

The verbose 10-section template was replaced (2026-04-20) with a tight summary
that points readers at the JSX dashboard for the deep dive. Rationale: most
stakeholders want the headline + the decision + what to do this week, not a
50-row CWV table they can sort interactively in the dashboard.
"""
from __future__ import annotations

from datetime import datetime, timezone


def render_product_report(
    *,
    product_id: str,
    product_name: str,
    domains: list[dict],
    locales_audited: list[str],
    url_rows: list[dict],
    seo_score: float,
    perf_score: float,
    seo_breakdown: dict,
    perf_breakdown: dict,
    findings_by_severity: dict,
    strategic: dict,
    portfolio_rank: dict | None = None,
    audit_date: str | None = None,
    run_id: str | None = None,
) -> str:
    audit_date = audit_date or datetime.now(timezone.utc).isoformat(timespec="seconds")
    run_id = run_id or audit_date.replace(":", "").replace("-", "")
    all_findings = [f for bucket in findings_by_severity.values() for f in bucket]

    lines: list[str] = []
    lines.append(f"# {product_name} — SEO + PageSpeed Audit\n")
    lines.append(f"_Run {run_id} · {len(url_rows)} URLs · "
                 f"{len(domains)} domain(s) · {len(locales_audited)} locale(s)_\n")

    # ─── Executive summary ──────────────────────────────────────────────
    lines.append("## Executive summary\n")
    lines.append(_executive_summary(
        product_name, seo_score, perf_score, strategic,
        domains, url_rows, all_findings,
    ))
    lines.append("")

    # ─── Decision ───────────────────────────────────────────────────────
    lines.append(f"## Decision: Option **{strategic['supports']}**\n")
    if strategic.get("triggered_rules"):
        lines.append("Triggered by:")
        for r in strategic["triggered_rules"]:
            lines.append(f"- {r}")
        lines.append("")
    lines.append(f"_See dashboard for full reasoning · "
                 f"`products/{product_id}.jsx`_\n")

    # ─── Clean vs Legacy at a glance ────────────────────────────────────
    if len(domains) > 1:
        lines.append("## Clean vs Legacy snapshot\n")
        lines.append(_domain_comparison_table(domains, url_rows))
        lines.append("")

    # ─── Next steps ─────────────────────────────────────────────────────
    lines.append("## Next steps (this sprint)\n")
    next_steps = _rank_next_steps(all_findings, perf_score, seo_score)
    if next_steps:
        for i, step in enumerate(next_steps, 1):
            lines.append(f"{i}. **{step['title']}** "
                         f"_({step['owner']} · {step['effort']} · "
                         f"+{step['lift']} score lift est.)_  \n"
                         f"   {step['detail']}")
    else:
        lines.append("_No P0/P1 findings — site is in good shape._")
    lines.append("")

    # ─── Where the data lives ───────────────────────────────────────────
    lines.append("## Where the data lives\n")
    lines.append(f"- **Interactive dashboard** — `products/{product_id}.jsx` "
                 f"(open as a React artifact for filters + charts)")
    lines.append(f"- **Raw PSI JSON** — `data/psi-raw/{product_id}/`")
    lines.append(f"- **HTML audit** — `data/html-audit/{product_id}-*.json`")
    lines.append(f"- **Scoring CSV** — `data/scores.csv` (filter by product={product_id})")
    lines.append(f"- **Audit date** — {audit_date}")

    return "\n".join(lines) + "\n"


# ─── exec-summary builders ─────────────────────────────────────────────────
def _executive_summary(
    product_name: str,
    seo_score: float,
    perf_score: float,
    strategic: dict,
    domains: list[dict],
    url_rows: list[dict],
    all_findings: list[dict],
) -> str:
    p0 = sum(1 for f in all_findings if f["severity"] == "P0")
    p1 = sum(1 for f in all_findings if f["severity"] == "P1")
    arch = sum(1 for f in all_findings if f.get("label") == "architectural")

    perf_word = "critical" if perf_score < 40 else "weak" if perf_score < 60 else "ok" if perf_score < 80 else "strong"
    seo_word = "critical" if seo_score < 40 else "weak" if seo_score < 60 else "ok" if seo_score < 80 else "strong"

    bullets = []
    bullets.append(f"- **Headline:** {product_name} scores **SEO {seo_score}** ({seo_word}) "
                   f"and **Perf {perf_score}** ({perf_word}). "
                   f"Audit supports **Option {strategic['supports']}**.")
    bullets.append(f"- **Findings:** {p0} P0 (must-fix), {p1} P1 (should-fix). "
                   f"{arch} architectural vs {len(all_findings) - arch} fixable-in-place.")

    # Clean vs legacy bullet, if both
    legacy = [d for d in domains if d.get("role") == "legacy"]
    clean = [d for d in domains if d.get("role") == "clean"]
    if legacy and clean:
        leg_url = legacy[0]["url"].replace("https://", "")
        cln_url = clean[0]["url"].replace("https://", "")
        # quick lh-perf comparison if available
        leg_perf = _avg_lh_perf(url_rows, legacy[0]["url"])
        cln_perf = _avg_lh_perf(url_rows, clean[0]["url"])
        bullets.append(f"- **Clean vs legacy:** `{cln_url}` Lighthouse perf {cln_perf or '—'} "
                       f"vs `{leg_url}` {leg_perf or '—'}. "
                       f"This delta is the central input to the Option-B decision.")

    return "\n".join(bullets)


def _avg_lh_perf(url_rows: list[dict], domain: str) -> int | None:
    scores = [
        (r.get("lh_scores") or {}).get("performance")
        for r in url_rows if r["url"].startswith(domain)
    ]
    scores = [s for s in scores if s is not None]
    if not scores:
        return None
    return int(round(sum(scores) / len(scores) * 100))


def _domain_comparison_table(domains: list[dict], url_rows: list[dict]) -> str:
    lines = []
    lines.append("| Metric | " + " | ".join(
        f"{d.get('role','?').capitalize()} (`{d['url'].replace('https://','')}`)"
        for d in domains
    ) + " |")
    lines.append("|---" + "|---" * len(domains) + "|")

    def domain_metric(domain_url: str, fn) -> str:
        rows = [r for r in url_rows if r["url"].startswith(domain_url)]
        v = fn(rows)
        return v if v is not None else "—"

    metrics = [
        ("Lighthouse perf (mobile, avg)", lambda rows: _fmt_avg_lh(rows, "performance", "mobile")),
        ("Lighthouse perf (desktop, avg)", lambda rows: _fmt_avg_lh(rows, "performance", "desktop")),
        ("Lighthouse SEO (avg)",          lambda rows: _fmt_avg_lh(rows, "seo")),
        ("CrUX LCP p75",                  lambda rows: _fmt_avg_field(rows, "lcp_p75_ms", "ms")),
        ("CrUX CLS p75",                  lambda rows: _fmt_avg_field(rows, "cls_p75", "")),
        ("JS bundle (mobile, KB)",        lambda rows: _fmt_avg_bundle(rows, "mobile")),
        ("Composite SEOScore",            lambda rows: _fmt_avg_score(rows, "seo_score")),
        ("Composite PerfScore",           lambda rows: _fmt_avg_score(rows, "perf_score")),
    ]
    for label, fn in metrics:
        cells = [domain_metric(d["url"], fn) for d in domains]
        lines.append(f"| {label} | " + " | ".join(cells) + " |")
    return "\n".join(lines)


def _fmt_avg_lh(rows, key, strategy=None):
    rows = [r for r in rows if (strategy is None or r.get("strategy") == strategy)]
    vals = [(r.get("lh_scores") or {}).get(key) for r in rows]
    vals = [v for v in vals if v is not None]
    if not vals:
        return None
    return f"{int(round(sum(vals) / len(vals) * 100))}"


def _fmt_avg_field(rows, key, unit):
    vals = [(r.get("field_cwv") or {}).get(key) for r in rows]
    vals = [v for v in vals if v is not None]
    if not vals:
        return None
    avg = sum(vals) / len(vals)
    return f"{avg:.0f}{unit}" if unit == "ms" else f"{avg:.2f}"


def _fmt_avg_bundle(rows, strategy):
    rows = [r for r in rows if r.get("strategy") == strategy]
    vals = [(r.get("bundle_info") or {}).get("js_transferred_kb") for r in rows]
    vals = [v for v in vals if v is not None]
    if not vals:
        return None
    return f"{int(round(sum(vals) / len(vals)))}"


def _fmt_avg_score(rows, key):
    vals = [r.get(key) for r in rows]
    vals = [v for v in vals if v is not None]
    if not vals:
        return None
    return f"{round(sum(vals) / len(vals), 1)}"


# ─── ranking the next-steps list ───────────────────────────────────────────
# Owner / effort / lift heuristics — keyed by finding `field` to keep things
# concrete. The lift is "expected score points if fixed", not authoritative.
_FIELD_HEURISTICS = {
    "sitemap.xml":         {"owner": "Frontend", "effort": "1h",   "lift": 4},
    "Sitemap directive":   {"owner": "DevOps",   "effort": "10m",  "lift": 2},
    "Strict-Transport-Security": {"owner": "DevOps", "effort": "30m", "lift": 1},
    "meta robots":         {"owner": "Frontend", "effort": "30m",  "lift": 15},  # P0 fix
    "<title>":             {"owner": "Content",  "effort": "1h",   "lift": 5},
    "<title> length":      {"owner": "Content",  "effort": "30m",  "lift": 2},
    "meta description":    {"owner": "Content",  "effort": "1h",   "lift": 4},
    "canonical link":      {"owner": "Frontend", "effort": "30m",  "lift": 3},
    "h1 count":            {"owner": "Frontend", "effort": "1h",   "lift": 2},
    "Open Graph":          {"owner": "Frontend", "effort": "1h",   "lift": 2},
    "JSON-LD":             {"owner": "Frontend", "effort": "2h",   "lift": 4},
    "hreflang coverage":   {"owner": "Frontend", "effort": "3h",   "lift": 8},
    "mobile LCP p75":      {"owner": "Frontend", "effort": "1d",   "lift": 12},
    "CLS p75":             {"owner": "Frontend", "effort": "4h",   "lift": 6},
    "INP p75":             {"owner": "Frontend", "effort": "1d",   "lift": 8},
}
_DEFAULT_HEUR = {"owner": "Frontend", "effort": "?", "lift": 1}


def _rank_next_steps(all_findings: list[dict], perf_score: float,
                     seo_score: float, max_items: int = 5) -> list[dict]:
    # Take only P0/P1, dedupe by (field, fix), rank by severity then heuristic lift.
    seen: set[tuple] = set()
    candidates: list[dict] = []
    for f in all_findings:
        if f["severity"] not in ("P0", "P1"):
            continue
        key = (f["field"], f["fix"])
        if key in seen:
            continue
        seen.add(key)
        h = _FIELD_HEURISTICS.get(f["field"], _DEFAULT_HEUR)
        candidates.append({
            "title": f"{f['field']} — {f['fix']}",
            "detail": f"Affects `{_short(f['url'])}`. Currently `{f['current']}`, target `{f['target']}`.",
            "owner": h["owner"],
            "effort": h["effort"],
            "lift": h["lift"],
            "severity": f["severity"],
            "_sev_rank": 0 if f["severity"] == "P0" else 1,
        })
    candidates.sort(key=lambda x: (x["_sev_rank"], -x["lift"]))
    return candidates[:max_items]


def _short(url: str) -> str:
    return url.replace("https://", "").replace("http://", "")
