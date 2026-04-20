#!/usr/bin/env python3
"""
Build the portfolio README summary + summary-matrix.md from per-product reports
and scores.csv. Run after `run_audit.py --all` finishes.
"""
from __future__ import annotations

import csv
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PRODUCTS_DIR = ROOT / "products"
SCORES_CSV = ROOT / "data" / "scores.csv"
README = ROOT / "README.md"
MATRIX = ROOT / "summary-matrix.md"


def load_scores() -> list[dict]:
    if not SCORES_CSV.exists():
        return []
    with SCORES_CSV.open() as fh:
        return list(csv.DictReader(fh))


def extract_score(md_path: Path, pattern: str) -> float | None:
    m = re.search(pattern, md_path.read_text())
    return float(m.group(1)) if m else None


def build() -> None:
    reports = sorted(PRODUCTS_DIR.glob("*.md"))
    rows = []
    for p in reports:
        product = p.stem
        seo = extract_score(p, r"SEOScore:\*\*\s*([\d.]+)")
        perf = extract_score(p, r"PerfScore:\*\*\s*([\d.]+)")
        # Pull first mobile CWV from scores.csv
        mobile_lcp, cls = None, None
        for r in load_scores():
            if r["product"] == product and r["strategy"] == "mobile" and r.get("lcp_field"):
                mobile_lcp = float(r["lcp_field"])
                cls = float(r["cls_field"]) if r["cls_field"] else None
                break
        rows.append({
            "product": product, "seo": seo, "perf": perf,
            "mobile_lcp": mobile_lcp, "cls": cls, "report": p,
        })

    # Score matrix
    lines: list[str] = []
    lines.append("# Sanjow Portfolio — SEO + PageSpeed Audit Summary\n")
    lines.append(f"> Generated: {datetime.now(timezone.utc).isoformat(timespec='seconds')}\n")
    lines.append(f"**Products covered:** {len(rows)} / 14\n")
    lines.append("## Score matrix\n")
    lines.append("| Product | SEOScore | PerfScore | Mobile LCP p75 | CLS p75 | Report |")
    lines.append("|---|---:|---:|---:|---:|---|")
    for r in sorted(rows, key=lambda x: -(x["seo"] or 0)):
        lines.append(f"| {r['product']} | {r['seo'] or '–'} | {r['perf'] or '–'} | "
                     f"{f'{r[\"mobile_lcp\"]:.0f}ms' if r['mobile_lcp'] else '–'} | "
                     f"{f'{r[\"cls\"]:.2f}' if r['cls'] is not None else '–'} | "
                     f"[{r['product']}.md](products/{r['report'].name}) |")
    lines.append("")

    # Ranks
    ranked_seo = sorted((r for r in rows if r["seo"] is not None),
                        key=lambda x: -x["seo"])
    ranked_perf = sorted((r for r in rows if r["perf"] is not None),
                         key=lambda x: -x["perf"])

    lines.append("## Products ranked best to worst (SEOScore)\n")
    for i, r in enumerate(ranked_seo, 1):
        lines.append(f"{i}. **{r['product']}** — {r['seo']}")
    lines.append("")

    lines.append("## Products ranked best to worst (PerfScore)\n")
    for i, r in enumerate(ranked_perf, 1):
        lines.append(f"{i}. **{r['product']}** — {r['perf']}")
    lines.append("")

    README.write_text("\n".join(lines) + "\n")
    MATRIX.write_text("\n".join(lines[:20]) + "\n")
    print(f"✓ wrote {README.name} + {MATRIX.name} ({len(rows)} products)")


if __name__ == "__main__":
    build()
