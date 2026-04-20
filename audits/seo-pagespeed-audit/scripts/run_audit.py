#!/usr/bin/env python3
"""
Orchestrator — run the SEO + PageSpeed audit for one product (or all).

Usage:
    python scripts/run_audit.py --product wepdf
    python scripts/run_audit.py --all

Env (loaded from .env):
    PSI_API_KEY           required
    CRUX_API_KEY          optional (for origin fallback)
    PSI_REQUEST_DELAY_MS  default 200
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml
from dotenv import load_dotenv

# allow `python scripts/run_audit.py` from any cwd
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from lib.psi_client import (
    PSIClient, PSIError,
    extract_lighthouse_scores, extract_lab_cwv, extract_field_cwv,
    extract_top_opportunities, extract_top_diagnostics,
    extract_bundle_info, extract_image_audit,
)
from lib.html_audit import audit_url, audit_site, save_html_audit
from lib.scoring import (
    compute_seo_score, compute_perf_score,
    aggregate_product_score, classify_strategic_implication, TIER_WEIGHTS,
)
from lib.findings import classify_findings, group_by_severity
from lib.report import render_product_report
from lib.dashboard import render_dashboard


MANIFEST_PATH = ROOT / "data" / "domain-manifest.yml"
SCORES_CSV = ROOT / "data" / "scores.csv"


def load_manifest() -> dict:
    with open(MANIFEST_PATH) as fh:
        return yaml.safe_load(fh)


def build_tier_urls(product_cfg: dict, domain_url: str) -> list[dict]:
    """Expand {locale} placeholders and return URL tier list (per locale/form-factor)."""
    tier_routes = product_cfg.get("tier_routes", {})
    locales = product_cfg.get("locales", ["en"])
    default = product_cfg.get("default_locale", locales[0])

    # prompt §Step 2 locale sampling — primary en (map to en-GB) + one other
    primary = "en" if "en" in locales else locales[0]
    secondary = "fr" if "fr" in locales and "fr" != primary else None
    sampled_locales = [primary] + ([secondary] if secondary else [])

    urls = []
    for tier_idx, (name, path) in enumerate(
        [("homepage", tier_routes.get("homepage", "/")),
         ("transactional", tier_routes.get("transactional")),
         ("seo_landing", tier_routes.get("seo_landing")),
         ("deep_programmatic", tier_routes.get("deep_programmatic"))], start=1):
        if not path:
            continue
        for loc in sampled_locales:
            p = path.replace("{locale}", loc)
            # URL assembly: locales are typically prefixed via middleware in Next.js
            # but homepage ("/") typically serves the default locale.
            if tier_idx == 1 and loc == default:
                full = f"{domain_url.rstrip('/')}/"
            elif p.startswith("/"):
                # if the path already contains the locale (deep programmatic), leave it;
                # otherwise add the locale prefix for non-default locales
                if f"/{loc}/" in p or p.startswith(f"/{loc}"):
                    full = f"{domain_url.rstrip('/')}{p}"
                elif loc == default:
                    full = f"{domain_url.rstrip('/')}{p}"
                else:
                    full = f"{domain_url.rstrip('/')}/{loc}{p}"
            else:
                full = f"{domain_url.rstrip('/')}/{p.lstrip('/')}"
            urls.append({
                "tier": tier_idx,
                "tier_name": name,
                "url": full,
                "locale": loc,
            })
    return urls


def run_one_url(psi: PSIClient, product_id: str, row: dict, expected_locales: list[str]) -> list[dict]:
    """Returns one row per form-factor (mobile + desktop)."""
    out = []
    # Shared HTML audit — fetched once, used for both form-factors
    try:
        html = audit_url(row["url"], expected_locales)
    except Exception as e:
        html = {"url": row["url"], "fetch_error": str(e)}

    for strategy in ("mobile", "desktop"):
        try:
            psi_loc = "en-GB" if row["locale"] in ("en", "en-GB") else "fr-FR"
            psi_data = psi.run_pagespeed(
                url=row["url"], strategy=strategy, locale=psi_loc, product=product_id,
            )
        except PSIError as e:
            print(f"  ✗ PSI failed for {row['url']} [{strategy}]: {e}", file=sys.stderr)
            out.append({**row, "strategy": strategy, "psi_error": str(e),
                        "html_audit": html})
            continue

        out.append({
            **row,
            "strategy": strategy,
            "html_audit": html,
            "lh_scores": extract_lighthouse_scores(psi_data),
            "lab_cwv": extract_lab_cwv(psi_data),
            "field_cwv": extract_field_cwv(psi_data),
            "top_opportunities": extract_top_opportunities(psi_data),
            "top_diagnostics": extract_top_diagnostics(psi_data),
            "bundle_info": extract_bundle_info(psi_data),
            "image_audit": extract_image_audit(psi_data),
        })
    return out


def score_urls(url_rows: list[dict], site_audit: dict) -> list[dict]:
    """Add seo_score + perf_score to every row."""
    scored = []
    # Pair mobile and desktop to compute PerfScore correctly per URL
    by_url: dict[str, dict] = {}
    for r in url_rows:
        by_url.setdefault(r["url"], {})[r["strategy"]] = r
    for url, pair in by_url.items():
        m = pair.get("mobile") or {}
        d = pair.get("desktop") or {}
        html = (m or d).get("html_audit", {})
        if html.get("fetch_error"):
            for strategy, row in pair.items():
                scored.append({**row, "seo_score": 0, "perf_score": 0,
                               "seo_breakdown": {}, "perf_breakdown": {}})
            continue

        seo_score, seo_b = compute_seo_score(html, site_audit)
        perf_score, perf_b = compute_perf_score(
            crux_mobile=m.get("field_cwv"),
            crux_desktop=d.get("field_cwv"),
            lh_mobile_perf=(m.get("lh_scores") or {}).get("performance"),
            lh_desktop_perf=(d.get("lh_scores") or {}).get("performance"),
            total_js_kb=(m.get("bundle_info") or d.get("bundle_info") or {}).get("js_transferred_kb"),
            image_audit=(m.get("image_audit") or d.get("image_audit") or {}),
        )
        for strategy, row in pair.items():
            scored.append({
                **row,
                "seo_score": seo_score,
                "perf_score": perf_score,
                "seo_breakdown": seo_b,
                "perf_breakdown": perf_b,
            })
    return scored


def write_csv_rows(csv_path: Path, product_id: str, domain: str, rows: list[dict]) -> None:
    """Append one row per URL/strategy to scores.csv. Headers written on first create."""
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    headers = [
        "product", "domain", "locale", "tier", "url", "strategy",
        "seo_score", "perf_score",
        "lcp_field", "cls_field", "inp_field",
        "lh_perf", "lh_seo", "lh_a11y", "lh_bp",
        "audit_date",
    ]
    new_file = not csv_path.exists()
    now = datetime.now(timezone.utc).date().isoformat()
    with csv_path.open("a", newline="") as fh:
        w = csv.writer(fh)
        if new_file:
            w.writerow(headers)
        for r in rows:
            lh = r.get("lh_scores") or {}
            f = r.get("field_cwv") or {}
            w.writerow([
                product_id, domain, r.get("locale"), r.get("tier"),
                r.get("url"), r.get("strategy"),
                r.get("seo_score"), r.get("perf_score"),
                f.get("lcp_p75_ms"), f.get("cls_p75"), f.get("inp_p75_ms"),
                lh.get("performance"), lh.get("seo"),
                lh.get("accessibility"), lh.get("best-practices"),
                now,
            ])


def run_product(product_id: str, manifest: dict, psi: PSIClient,
                role_filter: str | None = None,
                locale_filter: list[str] | None = None) -> None:
    cfg = manifest["products"].get(product_id)
    if not cfg:
        print(f"✗ unknown product: {product_id}", file=sys.stderr, flush=True)
        return

    domains = cfg.get("domains", [])
    if role_filter:
        domains = [d for d in domains if d.get("role") == role_filter]
    if not domains:
        print(f"⚠ no domains to audit for {product_id}"
              f"{' (role='+role_filter+')' if role_filter else ''}. Skipping.",
              file=sys.stderr, flush=True)
        return

    print(f"\n━━━ {cfg.get('display_name', product_id)} ━━━", flush=True)

    all_scored_rows: list[dict] = []
    per_domain_findings = []
    locales_audited_set: set[str] = set()

    # Pre-count URLs so we can show "[n/total]" progress
    total_urls = 0
    for d in domains:
        tier_urls = build_tier_urls(cfg, d["url"])
        if locale_filter:
            tier_urls = [t for t in tier_urls if t["locale"] in locale_filter]
        total_urls += len(tier_urls)
    done = 0

    t_product = datetime.now(timezone.utc)

    for d in domains:
        domain = d["url"]
        is_legacy = d.get("role") == "legacy"
        print(f"  • {domain} ({d.get('role','?')})", flush=True)

        site = audit_site(domain, expected_locales_count=len(cfg.get("locales", [])))
        tier_urls = build_tier_urls(cfg, domain)
        if locale_filter:
            tier_urls = [t for t in tier_urls if t["locale"] in locale_filter]
        html_audits: list[dict] = []
        url_rows: list[dict] = []
        for tu in tier_urls:
            done += 1
            print(f"    [{done}/{total_urls}] T{tu['tier']} {tu['locale']} {tu['url']}",
                  flush=True)
            rows = run_one_url(psi, product_id, tu, cfg.get("locales", []))
            url_rows.extend(rows)
            for r in rows:
                ha = r.get("html_audit") or {}
                if ha and ha not in html_audits:
                    html_audits.append(ha)
                locales_audited_set.add(r.get("locale", ""))

        save_html_audit(ROOT / "data" / "html-audit", f"{product_id}-{_safe(domain)}", html_audits)

        scored = score_urls(url_rows, site)
        for s in scored:
            s["_domain"] = domain
            s["_role"] = d.get("role")
        all_scored_rows.extend(scored)
        write_csv_rows(SCORES_CSV, product_id, domain, scored)

        findings = classify_findings(product_id, scored, site, scored)
        per_domain_findings.append({"domain": domain, "role": d.get("role"),
                                    "site_audit": site, "findings": findings,
                                    "scored": scored})

    # Aggregate product-level
    seo_avg = aggregate_product_score(all_scored_rows, "seo_score")
    perf_avg = aggregate_product_score(all_scored_rows, "perf_score")

    all_findings = [f for pd in per_domain_findings for f in pd["findings"]]
    findings_by_sev = group_by_severity(all_findings)

    # Strategic
    is_legacy = any(d.get("role") == "legacy" for d in domains)
    mobile_lcps = [(r.get("field_cwv") or {}).get("lcp_p75_ms") or 0
                   for r in all_scored_rows if r["strategy"] == "mobile"]
    worst_cls = max(((r.get("field_cwv") or {}).get("cls_p75") or 0
                     for r in all_scored_rows), default=0)
    hreflang_errors = any(
        not (r.get("html_audit") or {}).get("hreflang_all_valid", True)
        for r in all_scored_rows
    )
    strategic = classify_strategic_implication(
        seo_avg, perf_avg, is_legacy,
        max(mobile_lcps, default=0), worst_cls, hreflang_errors,
    )

    # Render
    # pick breakdown from the first healthy row as illustrative
    example = next((r for r in all_scored_rows if r.get("seo_breakdown")), {})
    md = render_product_report(
        product_id=product_id,
        product_name=cfg.get("display_name", product_id),
        domains=domains,
        locales_audited=sorted(l for l in locales_audited_set if l),
        url_rows=all_scored_rows,
        seo_score=seo_avg,
        perf_score=perf_avg,
        seo_breakdown=example.get("seo_breakdown", {}),
        perf_breakdown=example.get("perf_breakdown", {}),
        findings_by_severity=findings_by_sev,
        strategic=strategic,
    )
    out_path = ROOT / "products" / f"{product_id}.md"
    out_path.write_text(md)

    # JSX dashboard — interactive artifact for the deep dive
    jsx = render_dashboard(
        product_id=product_id,
        product_name=cfg.get("display_name", product_id),
        domains=domains,
        locales_audited=sorted(l for l in locales_audited_set if l),
        url_rows=all_scored_rows,
        seo_score=seo_avg,
        perf_score=perf_avg,
        seo_breakdown=example.get("seo_breakdown", {}),
        perf_breakdown=example.get("perf_breakdown", {}),
        findings_by_severity=findings_by_sev,
        strategic=strategic,
    )
    jsx_path = ROOT / "products" / f"{product_id}.jsx"
    jsx_path.write_text(jsx)

    elapsed = (datetime.now(timezone.utc) - t_product).total_seconds()
    print(f"  ✓ wrote {out_path.relative_to(ROOT)} + {jsx_path.name} — "
          f"SEO={seo_avg} / Perf={perf_avg} (took {elapsed:.0f}s)",
          flush=True)


def _safe(s: str) -> str:
    return s.replace("https://", "").replace("http://", "").replace("/", "_").replace(":", "_")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--product", help="Product ID from domain-manifest.yml")
    parser.add_argument("--all", action="store_true", help="Audit every product with domains")
    parser.add_argument("--role", choices=["clean", "legacy"],
                        help="Only audit domains with this role (skip the others).")
    parser.add_argument("--locale", action="append",
                        help="Only audit URLs in this locale (repeatable). "
                             "Default: all sampled locales.")
    parser.add_argument("--tiers", default="1,2,3,4",
                        help="Comma-separated tier numbers to include "
                             "(default 1,2,3,4 — use '1' for fastest smoke test).")
    args = parser.parse_args()

    load_dotenv(ROOT / ".env")
    api_key = os.getenv("PSI_API_KEY")
    if not api_key:
        print("✗ PSI_API_KEY not set — copy .env.example → .env and paste your key.",
              file=sys.stderr, flush=True)
        sys.exit(2)

    delay_ms = int(os.getenv("PSI_REQUEST_DELAY_MS", "200"))
    manifest = load_manifest()
    psi = PSIClient(api_key=api_key, raw_dir=ROOT / "data" / "psi-raw",
                    delay_ms=delay_ms)

    # tier filter via monkey-patch on build_tier_urls — simplest path
    allowed_tiers = {int(t) for t in args.tiers.split(",")}
    global build_tier_urls
    _orig_build_tier_urls = build_tier_urls
    def _filtered(cfg, domain):
        return [u for u in _orig_build_tier_urls(cfg, domain) if u["tier"] in allowed_tiers]
    build_tier_urls = _filtered

    targets: list[str]
    if args.product:
        targets = [args.product]
    elif args.all:
        targets = [k for k, v in manifest["products"].items() if v.get("domains")]
    else:
        parser.error("provide --product or --all")

    for p in targets:
        try:
            run_product(p, manifest, psi,
                        role_filter=args.role,
                        locale_filter=args.locale)
        except Exception as e:
            print(f"✗ {p} failed: {e}", file=sys.stderr, flush=True)
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
