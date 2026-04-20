"""
Findings classifier — translate raw audit output into severity-ranked findings
with fixable-in-place vs architectural labels.

Every finding is a dict with:
  severity:   P0 / P1 / P2 / P3
  area:       seo / perf / locale / security
  url:        the URL where the finding was observed
  field:      the specific field or metric
  current:    current value
  target:     target value
  fix:        one-line fix recommendation
  label:      "fixable-in-place" or "architectural"
  rationale:  why it's labelled that way
"""
from __future__ import annotations

from typing import Any


def classify_findings(
    product: str,
    per_url: list[dict],       # [{url, strategy, html_audit, psi_scores, ...}]
    site_audit: dict,
    perf_scores: list[dict],   # [{url, strategy, perf_sub, lab_cwv, field_cwv}]
) -> list[dict]:
    findings: list[dict] = []

    # SEO findings are URL-level, not strategy-level — dedupe per_url to one
    # entry per unique URL so we don't emit duplicate findings for mobile+desktop.
    seen_urls: set[str] = set()
    deduped_per_url: list[dict] = []
    for row in per_url:
        if row["url"] not in seen_urls:
            seen_urls.add(row["url"])
            deduped_per_url.append(row)
    per_url = deduped_per_url

    # ─── site-level ───────────────────────────────────────────────────
    if not site_audit.get("sitemap_exists"):
        findings.append({
            "severity": "P1", "area": "seo", "url": site_audit["origin"],
            "field": "sitemap.xml",
            "current": "missing", "target": "valid XML sitemap at /sitemap.xml",
            "fix": "Generate a sitemap (Next.js app router supports `sitemap.ts`).",
            "label": "fixable-in-place",
            "rationale": "Framework-level config — no architectural change needed.",
        })
    elif not site_audit.get("robots_has_sitemap"):
        findings.append({
            "severity": "P1", "area": "seo", "url": f"{site_audit['origin']}/robots.txt",
            "field": "Sitemap directive",
            "current": "missing in robots.txt", "target": "Sitemap: <url> line present",
            "fix": "Add a `Sitemap:` line to robots.txt pointing to /sitemap.xml.",
            "label": "fixable-in-place",
            "rationale": "One-line config change.",
        })

    if not site_audit.get("hsts_enabled"):
        findings.append({
            "severity": "P3", "area": "security", "url": site_audit["origin"],
            "field": "Strict-Transport-Security",
            "current": "missing", "target": "max-age >= 15768000; includeSubDomains",
            "fix": "Add HSTS header at the edge (Vercel/CDN).",
            "label": "fixable-in-place",
            "rationale": "Edge config change.",
        })

    # ─── per-URL SEO ──────────────────────────────────────────────────
    for row in per_url:
        ha = row.get("html_audit", {})
        url = row["url"]

        if ha.get("robots_noindex"):
            findings.append({
                "severity": "P0", "area": "seo", "url": url,
                "field": "meta robots",
                "current": "noindex", "target": "no noindex on production pages",
                "fix": "Remove the noindex directive — confirm it wasn't left from a staging config.",
                "label": "fixable-in-place",
                "rationale": "Config or env-leak bug.",
            })

        if not ha.get("title"):
            findings.append({
                "severity": "P1", "area": "seo", "url": url, "field": "<title>",
                "current": "missing", "target": "30–60 char unique title",
                "fix": "Add a page-level title via Next.js metadata.",
                "label": "fixable-in-place",
                "rationale": "App router `metadata` is the standard pattern.",
            })
        elif not (30 <= len(ha.get("title", "")) <= 60):
            findings.append({
                "severity": "P2", "area": "seo", "url": url, "field": "<title> length",
                "current": f"{len(ha.get('title',''))} chars",
                "target": "30–60 chars",
                "fix": "Tighten or expand the title to 30–60 characters.",
                "label": "fixable-in-place",
                "rationale": "Copy change.",
            })

        if not ha.get("meta_description"):
            findings.append({
                "severity": "P1", "area": "seo", "url": url, "field": "meta description",
                "current": "missing", "target": "120–160 char unique description",
                "fix": "Add a description via Next.js metadata.",
                "label": "fixable-in-place",
                "rationale": "Metadata API.",
            })

        if not ha.get("canonical"):
            findings.append({
                "severity": "P1", "area": "seo", "url": url, "field": "canonical link",
                "current": "missing", "target": "self-referential canonical",
                "fix": "Emit a self-referential `<link rel='canonical'>` via metadata.",
                "label": "fixable-in-place",
                "rationale": "Metadata API.",
            })

        if ha.get("h1_count", 0) != 1:
            findings.append({
                "severity": "P2", "area": "seo", "url": url, "field": "h1 count",
                "current": f"{ha.get('h1_count', 0)} h1 tags",
                "target": "exactly 1 h1 per page",
                "fix": "Ensure exactly one h1 per route; demote duplicates to h2.",
                "label": "fixable-in-place",
                "rationale": "Component-level fix.",
            })

        if not ha.get("og_title") or not ha.get("og_image"):
            findings.append({
                "severity": "P2", "area": "seo", "url": url, "field": "Open Graph",
                "current": "incomplete", "target": "og:title + og:description + og:image + og:url + og:type",
                "fix": "Emit full OG tags via Next.js metadata.openGraph.",
                "label": "fixable-in-place",
                "rationale": "Metadata API.",
            })

        if not ha.get("json_ld_types"):
            findings.append({
                "severity": "P2", "area": "seo", "url": url, "field": "JSON-LD",
                "current": "none", "target": "relevant schema.org types (Organization, WebSite, Product, FAQ)",
                "fix": "Inject JSON-LD for the page's primary entity type.",
                "label": "fixable-in-place",
                "rationale": "Content injection.",
            })

        # hreflang
        expected = site_audit.get("expected_locales_count", 1)
        if expected > 1 and ha.get("hreflang_count", 0) < expected:
            findings.append({
                "severity": "P1", "area": "locale", "url": url,
                "field": "hreflang coverage",
                "current": f"{ha.get('hreflang_count', 0)} of {expected} locales",
                "target": f"{expected} hreflang tags + x-default",
                "fix": "Emit hreflang for every locale route + x-default.",
                "label": "fixable-in-place",
                "rationale": "Middleware or metadata config.",
            })

    # ─── perf — CWV thresholds from prompt §Decision thresholds ───────
    for row in perf_scores:
        url = row["url"]
        strategy = row["strategy"]
        field = row.get("field_cwv") or {}
        lcp = field.get("lcp_p75_ms")
        cls = field.get("cls_p75")
        inp = field.get("inp_p75_ms")

        if strategy == "mobile" and lcp and lcp > 6000:
            findings.append({
                "severity": "P0", "area": "perf", "url": url,
                "field": "mobile LCP p75",
                "current": f"{lcp:.0f}ms", "target": "<2500ms",
                "fix": "Preload hero image, defer non-critical JS, check LCP candidate via Lighthouse report.",
                "label": "architectural" if lcp > 8000 else "fixable-in-place",
                "rationale": ("LCP > 8s is almost always framework/bundle-level — "
                              "flag for clean-domain restart consideration.")
                              if lcp > 8000 else "Component-level perf work.",
            })
        elif strategy == "mobile" and lcp and lcp > 4000:
            findings.append({
                "severity": "P1", "area": "perf", "url": url,
                "field": "mobile LCP p75",
                "current": f"{lcp:.0f}ms", "target": "<2500ms",
                "fix": "Optimise LCP element (image preload, size, format).",
                "label": "fixable-in-place",
                "rationale": "Standard LCP optimisation.",
            })

        if cls is not None and cls > 0.25:
            findings.append({
                "severity": "P0", "area": "perf", "url": url,
                "field": "CLS p75",
                "current": f"{cls:.2f}", "target": "<0.1",
                "fix": "Reserve space for images/ads/fonts; audit dynamic content insertion.",
                "label": "fixable-in-place",
                "rationale": "Usually CSS/JSX fix; becomes architectural if layout lib is the cause.",
            })

        if inp and inp > 500:
            findings.append({
                "severity": "P1", "area": "perf", "url": url,
                "field": "INP p75",
                "current": f"{inp:.0f}ms", "target": "<200ms",
                "fix": "Break up long tasks; defer analytics; consider React 19 transitions.",
                "label": "fixable-in-place",
                "rationale": "JS refactor.",
            })

    return findings


def group_by_severity(findings: list[dict]) -> dict[str, list[dict]]:
    groups: dict[str, list[dict]] = {"P0": [], "P1": [], "P2": [], "P3": []}
    for f in findings:
        groups.setdefault(f["severity"], []).append(f)
    return groups
