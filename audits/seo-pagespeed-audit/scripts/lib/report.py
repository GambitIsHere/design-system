"""
Render the per-product markdown report following prompt §Step 8 template.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path


def _verdict_cwv(lcp: float | None, cls: float | None, inp: float | None) -> str:
    if lcp is None and cls is None and inp is None:
        return "Insufficient data"
    poor = False
    ni = False
    if lcp is not None:
        if lcp > 4000: poor = True
        elif lcp > 2500: ni = True
    if cls is not None:
        if cls > 0.25: poor = True
        elif cls > 0.1: ni = True
    if inp is not None:
        if inp > 500: poor = True
        elif inp > 200: ni = True
    return "Poor" if poor else "Needs improvement" if ni else "Good"


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

    lines: list[str] = []
    lines.append(f"# {product_name} — SEO + PageSpeed Audit\n")

    # 1. Snapshot
    lines.append("## 1. Snapshot\n")
    lines.append(f"- **Domain(s) audited:** {', '.join(d['url'] for d in domains)}")
    lines.append(f"- **Locales audited:** {', '.join(locales_audited)}")
    tier_counts = {}
    for r in url_rows:
        tier_counts[r["tier"]] = tier_counts.get(r["tier"], 0) + 1
    tiers_str = ", ".join(f"T{t}={n}" for t, n in sorted(tier_counts.items()))
    lines.append(f"- **URLs sampled:** {len(url_rows)} ({tiers_str})")
    lines.append(f"- **Audit date:** {audit_date}")
    lines.append(f"- **PSI API run ID:** {run_id}\n")

    # 2. Headline
    lines.append("## 2. Headline scores\n")
    lines.append(f"- **SEOScore:** {seo_score} / 100")
    lines.append(f"- **PerfScore:** {perf_score} / 100")
    if portfolio_rank:
        lines.append(f"- **Portfolio rank (SEO):** {portfolio_rank.get('seo','?')}")
        lines.append(f"- **Portfolio rank (Perf):** {portfolio_rank.get('perf','?')}")
    lines.append("")

    # Sub-scores
    lines.append("### Sub-scores (SEO)\n")
    lines.append("| Category | Score | Weight | Breakdown |")
    lines.append("|---|---:|---:|---|")
    for cat, data in seo_breakdown.items():
        checks = data.get("checks", {})
        if checks:
            breakdown = f"{data.get('passed','?')}/{data.get('total','?')} checks passed"
        else:
            breakdown = ", ".join(f"{k}={v}" for k, v in data.items()
                                  if k not in ("score", "weight"))[:120]
        lines.append(f"| {cat.replace('_',' ')} | {data['score']} | {data['weight']} | {breakdown} |")
    lines.append("")

    lines.append("### Sub-scores (Perf)\n")
    lines.append("| Category | Score | Weight | Breakdown |")
    lines.append("|---|---:|---:|---|")
    for cat, data in perf_breakdown.items():
        breakdown = ", ".join(f"{k}={v}" for k, v in data.items()
                              if k not in ("score", "weight"))[:120]
        lines.append(f"| {cat.replace('_',' ')} | {data['score']} | {data['weight']} | {breakdown} |")
    lines.append("")

    # 3. CrUX field
    lines.append("## 3. Core Web Vitals — CrUX field p75 (28-day)\n")
    lines.append("| URL | Device | LCP | CLS | INP | TTFB | Verdict |")
    lines.append("|---|---|---:|---:|---:|---:|---|")
    for r in url_rows:
        f = r.get("field_cwv") or {}
        verdict = _verdict_cwv(f.get("lcp_p75_ms"), f.get("cls_p75"), f.get("inp_p75_ms"))
        lines.append(f"| {_short_url(r['url'])} | {r['strategy']} | "
                     f"{_ms(f.get('lcp_p75_ms'))} | {_round(f.get('cls_p75'), 3)} | "
                     f"{_ms(f.get('inp_p75_ms'))} | {_ms(f.get('ttfb_p75_ms'))} | {verdict} |")
    lines.append("")

    # 4. Lighthouse lab
    lines.append("## 4. Lighthouse lab scores\n")
    lines.append("| URL | Device | Perf | SEO | A11y | BP |")
    lines.append("|---|---|---:|---:|---:|---:|")
    for r in url_rows:
        lh = r.get("lh_scores", {})
        lines.append(f"| {_short_url(r['url'])} | {r['strategy']} | "
                     f"{_pct(lh.get('performance'))} | {_pct(lh.get('seo'))} | "
                     f"{_pct(lh.get('accessibility'))} | {_pct(lh.get('best-practices'))} |")
    lines.append("")

    # 5. SEO findings
    lines.append("## 5. SEO findings (grouped by severity)\n")
    for sev in ["P0", "P1", "P2", "P3"]:
        items = findings_by_severity.get(sev, [])
        if not items:
            continue
        lines.append(f"### {sev}\n")
        for f in items:
            if f["area"] != "seo" and f["area"] != "locale":
                continue
            lines.append(f"- **{f['field']}** — `{_short_url(f['url'])}`, "
                         f"current `{f['current']}`, target `{f['target']}` — "
                         f"**fix:** {f['fix']} — **{f['label']}** ({f['rationale']})")
        lines.append("")

    # 6. Performance findings
    lines.append("## 6. Performance findings\n")
    lines.append("### Top 5 opportunities (from Lighthouse)\n")
    # Flatten all opportunities, dedupe by id, sort by savings
    all_opps: dict[str, dict] = {}
    for r in url_rows:
        for o in r.get("top_opportunities", []):
            key = o["id"]
            if key not in all_opps or o["savings_ms"] > all_opps[key]["savings_ms"]:
                all_opps[key] = {**o, "url": r["url"]}
    top = sorted(all_opps.values(), key=lambda x: x["savings_ms"], reverse=True)[:5]
    for o in top:
        lines.append(f"- **{o['title']}** — est. savings {o['savings_ms']}ms at "
                     f"`{_short_url(o['url'])}` — {o.get('description','')}")
    if not top:
        lines.append("- _no opportunities flagged_")
    lines.append("")

    lines.append("### Bundle analysis\n")
    for r in url_rows:
        b = r.get("bundle_info") or {}
        if not b:
            continue
        lines.append(f"- `{_short_url(r['url'])}` ({r['strategy']}): "
                     f"JS {b.get('js_transferred_kb','?')}KB across "
                     f"{b.get('js_request_count','?')} req, "
                     f"largest {b.get('largest_js_bundle',{}).get('kb','?')}KB, "
                     f"unused {b.get('unused_js_kb','?')}KB")
    lines.append("")

    # 7. Locale health — skipped if only one locale
    if len(locales_audited) > 1:
        lines.append("## 7. Locale health\n")
        lines.append("| Locale | SEOScore (avg) | PerfScore (avg) | Hreflang valid | Notes |")
        lines.append("|---|---:|---:|:---:|---|")
        for loc in locales_audited:
            loc_rows = [r for r in url_rows if r.get("locale") == loc]
            seo_avg = round(sum(r["seo_score"] for r in loc_rows) / len(loc_rows), 1) if loc_rows else "–"
            perf_avg = round(sum(r["perf_score"] for r in loc_rows) / len(loc_rows), 1) if loc_rows else "–"
            hl_valid = all(r.get("html_audit", {}).get("hreflang_all_valid") for r in loc_rows)
            lines.append(f"| {loc} | {seo_avg} | {perf_avg} | {'✓' if hl_valid else '✗'} | |")
        lines.append("")

    # 8. Mobile vs desktop
    lines.append("## 8. Mobile vs desktop delta\n")
    mobile_rows = [r for r in url_rows if r["strategy"] == "mobile"]
    desktop_rows = [r for r in url_rows if r["strategy"] == "desktop"]
    m_avg = round(sum(r["perf_score"] for r in mobile_rows) / len(mobile_rows), 1) if mobile_rows else 0
    d_avg = round(sum(r["perf_score"] for r in desktop_rows) / len(desktop_rows), 1) if desktop_rows else 0
    lines.append(f"- Mobile PerfScore: **{m_avg}**, Desktop PerfScore: **{d_avg}**, "
                 f"Delta: **{round(d_avg - m_avg, 1)}** (desktop minus mobile)")
    if d_avg - m_avg > 20:
        lines.append("- ⚠ Mobile lags desktop by >20 points — mobile-critical fixes needed.")
    lines.append("")

    # 9. Strategic implication
    lines.append("## 9. Strategic implication\n")
    lines.append(f"**This audit supports:** Option **{strategic['supports']}**\n")
    if strategic["triggered_rules"]:
        lines.append("**Thumb rules triggered:**\n")
        for r in strategic["triggered_rules"]:
            lines.append(f"- {r}")
        lines.append("")

    # Architectural vs fixable summary
    all_findings = [f for bucket in findings_by_severity.values() for f in bucket]
    arch = [f for f in all_findings if f.get("label") == "architectural"]
    fixable = [f for f in all_findings if f.get("label") == "fixable-in-place"]

    lines.append("**Key architectural findings (argue for Option B/C):**\n")
    if arch:
        for f in arch:
            lines.append(f"- [{f['severity']}] {f['field']} — {f['fix']}")
    else:
        lines.append("- _none — all findings are fixable in-place_")
    lines.append("")

    lines.append("**Fixable-in-place findings (support Option A):**\n")
    if fixable:
        for f in fixable[:10]:
            lines.append(f"- [{f['severity']}] {f['field']} — {f['fix']}")
        if len(fixable) > 10:
            lines.append(f"- _...and {len(fixable) - 10} more_")
    else:
        lines.append("- _none_")
    lines.append("")

    lines.append(f"**Cross-reference:** see portfolio audit decision for this product in "
                 f"`portfolio-audit/products/{product_id}.md`\n")

    # 10. Raw data
    lines.append("## 10. Raw data\n")
    lines.append(f"- PSI JSON dumps: `seo-pagespeed-audit/data/psi-raw/{product_id}/`")
    lines.append(f"- Static HTML audit: `seo-pagespeed-audit/data/html-audit/{product_id}.json`")
    lines.append(f"- Scoring row: `seo-pagespeed-audit/data/scores.csv` (filter by product={product_id})")

    return "\n".join(lines) + "\n"


# ─── formatting helpers ───────────────────────────────────────────────────
def _short_url(url: str) -> str:
    return url.replace("https://", "").replace("http://", "")


def _ms(v: float | None) -> str:
    return f"{v:.0f}ms" if v is not None else "–"


def _round(v: float | None, digits: int = 2) -> str:
    return f"{v:.{digits}f}" if v is not None else "–"


def _pct(v: float | None) -> str:
    return f"{int(v * 100)}" if v is not None else "–"
