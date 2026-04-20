"""
Scoring model for the Sanjow SEO + PageSpeed audit.

Weights are LOCKED from prompt §Step 5. Do not change without PM approval —
they feed directly into the portfolio audit's A/B/C decision matrix.

All score functions:
  * take the extracted PSI result + HTML audit dict for a single URL/form-factor
  * return `(score_0_100, breakdown_dict)` so the report can show arithmetic
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


# ─── WEIGHTS (locked) ───────────────────────────────────────────────────────
SEO_WEIGHTS = {
    "technical_seo": 25,
    "crawlability": 20,
    "content_structure": 15,
    "structured_data": 15,
    "programmatic_scalability": 25,
}
assert sum(SEO_WEIGHTS.values()) == 100

PERF_WEIGHTS = {
    "crux_field_p75": 35,         # mobile-weighted 70/30 inside the function
    "lh_mobile_perf": 30,
    "lh_desktop_perf": 15,
    "bundle_size": 10,
    "image_optimisation": 10,
}
assert sum(PERF_WEIGHTS.values()) == 100

# Tier weights (prompt §Step 5 last paragraph)
TIER_WEIGHTS = {1: 2, 2: 1, 3: 2, 4: 1}


# ─── SEVERITY (prompt §Step 6) ──────────────────────────────────────────────
SEVERITY = {
    "P0": "blocker — breaks SEO indexing or loses real money",
    "P1": "high — measurable ranking or conversion impact",
    "P2": "medium — compounds over time",
    "P3": "low — polish",
}


# ─── HELPERS ────────────────────────────────────────────────────────────────
def _lerp(value: float, lo_bad: float, hi_good: float) -> float:
    """Map value → 0..100 where lo_bad=0 and hi_good=100. Clamps either end.
    If hi_good < lo_bad, the mapping is inverted (lower=better, e.g. LCP).
    """
    if hi_good == lo_bad:
        return 100.0
    if hi_good > lo_bad:
        # higher value is better
        score = (value - lo_bad) / (hi_good - lo_bad) * 100
    else:
        # lower value is better
        score = (lo_bad - value) / (lo_bad - hi_good) * 100
    return max(0.0, min(100.0, score))


# ─── SEO SUB-SCORES ─────────────────────────────────────────────────────────
def score_technical_seo(html_audit: dict) -> tuple[float, dict]:
    """
    title/meta/canonical/viewport/lang — present, unique, correct length.
    10 distinct checks, each worth 10 points.
    """
    checks = {
        "title_present": bool(html_audit.get("title")),
        "title_length_ok": 30 <= len(html_audit.get("title") or "") <= 60,
        "meta_description_present": bool(html_audit.get("meta_description")),
        "meta_description_length_ok": 120 <= len(html_audit.get("meta_description") or "") <= 160,
        "canonical_present": bool(html_audit.get("canonical")),
        "canonical_self_referential": html_audit.get("canonical_self_referential", False),
        "viewport_present": bool(html_audit.get("viewport")),
        "viewport_mobile_friendly": html_audit.get("viewport_mobile_friendly", False),
        "html_lang_present": bool(html_audit.get("html_lang")),
        "robots_not_noindex": not html_audit.get("robots_noindex", False),
    }
    passed = sum(1 for v in checks.values() if v)
    score = (passed / len(checks)) * 100
    return score, {"checks": checks, "passed": passed, "total": len(checks)}


def score_crawlability(html_audit: dict, site_audit: dict) -> tuple[float, dict]:
    """robots.txt, sitemap, 404s, redirect chains."""
    checks = {
        "robots_txt_exists": site_audit.get("robots_txt_exists", False),
        "robots_has_sitemap_directive": site_audit.get("robots_has_sitemap", False),
        "sitemap_exists": site_audit.get("sitemap_exists", False),
        "sitemap_valid_xml": site_audit.get("sitemap_valid", False),
        "sitemap_has_hreflang": site_audit.get("sitemap_hreflang", False),
        "http_to_https_redirects": site_audit.get("https_redirect", False),
        "no_redirect_chains": not html_audit.get("redirect_chain", False),
        "no_broken_canonical_loops": not html_audit.get("canonical_loop", False),
    }
    passed = sum(1 for v in checks.values() if v)
    score = (passed / len(checks)) * 100
    return score, {"checks": checks, "passed": passed, "total": len(checks)}


def score_content_structure(html_audit: dict) -> tuple[float, dict]:
    h1_count = html_audit.get("h1_count", 0)
    word_count = html_audit.get("word_count", 0)
    internal_links = html_audit.get("internal_link_count", 0)
    heading_hierarchy_ok = html_audit.get("heading_hierarchy_valid", False)

    checks = {
        "exactly_one_h1": h1_count == 1,
        "word_count_500_plus": word_count >= 500,
        "heading_hierarchy_valid": heading_hierarchy_ok,
        "internal_links_10_plus": internal_links >= 10,
    }
    passed = sum(1 for v in checks.values() if v)
    score = (passed / len(checks)) * 100
    return score, {
        "checks": checks,
        "h1_count": h1_count,
        "word_count": word_count,
        "internal_links": internal_links,
    }


def score_structured_data(html_audit: dict) -> tuple[float, dict]:
    checks = {
        "json_ld_present": bool(html_audit.get("json_ld_types")),
        "json_ld_valid": html_audit.get("json_ld_valid", False),
        "og_title": bool(html_audit.get("og_title")),
        "og_description": bool(html_audit.get("og_description")),
        "og_image": bool(html_audit.get("og_image")),
        "og_type": bool(html_audit.get("og_type")),
        "og_url": bool(html_audit.get("og_url")),
        "twitter_card": bool(html_audit.get("twitter_card")),
        "twitter_title": bool(html_audit.get("twitter_title")),
        "twitter_image": bool(html_audit.get("twitter_image")),
    }
    passed = sum(1 for v in checks.values() if v)
    score = (passed / len(checks)) * 100
    return score, {"checks": checks, "json_ld_types": html_audit.get("json_ld_types", [])}


def score_programmatic_scalability(html_audit: dict, site_audit: dict) -> tuple[float, dict]:
    """
    Route patterns, hreflang coverage. Key question: can this ship programmatic
    SEO at scale, or is the structure flat?
    """
    alt_count = html_audit.get("hreflang_count", 0)
    expected_locales = site_audit.get("expected_locales_count", 1)

    hreflang_coverage = (
        min(alt_count / expected_locales, 1.0) if expected_locales > 0 else 0
    )
    hreflang_valid = html_audit.get("hreflang_all_valid", False)
    has_xdefault = html_audit.get("hreflang_xdefault", False)
    parameterised_routes = site_audit.get("parameterised_routes", False)

    # 40 pts for hreflang coverage+validity, 30 for x-default, 30 for parameterised routes
    score = (
        hreflang_coverage * 40
        + (hreflang_valid * 20)
        + (has_xdefault * 10)
        + (parameterised_routes * 30)
    )
    return score, {
        "hreflang_coverage": hreflang_coverage,
        "hreflang_valid": hreflang_valid,
        "has_xdefault": has_xdefault,
        "parameterised_routes": parameterised_routes,
        "alt_count": alt_count,
        "expected_locales": expected_locales,
    }


def compute_seo_score(html_audit: dict, site_audit: dict) -> tuple[float, dict]:
    tech, tech_b = score_technical_seo(html_audit)
    crawl, crawl_b = score_crawlability(html_audit, site_audit)
    content, content_b = score_content_structure(html_audit)
    struct, struct_b = score_structured_data(html_audit)
    prog, prog_b = score_programmatic_scalability(html_audit, site_audit)

    weighted = (
        tech * SEO_WEIGHTS["technical_seo"]
        + crawl * SEO_WEIGHTS["crawlability"]
        + content * SEO_WEIGHTS["content_structure"]
        + struct * SEO_WEIGHTS["structured_data"]
        + prog * SEO_WEIGHTS["programmatic_scalability"]
    ) / 100

    return round(weighted, 1), {
        "technical_seo": {"score": round(tech, 1), "weight": SEO_WEIGHTS["technical_seo"], **tech_b},
        "crawlability": {"score": round(crawl, 1), "weight": SEO_WEIGHTS["crawlability"], **crawl_b},
        "content_structure": {"score": round(content, 1), "weight": SEO_WEIGHTS["content_structure"], **content_b},
        "structured_data": {"score": round(struct, 1), "weight": SEO_WEIGHTS["structured_data"], **struct_b},
        "programmatic_scalability": {"score": round(prog, 1), "weight": SEO_WEIGHTS["programmatic_scalability"], **prog_b},
    }


# ─── PERF SUB-SCORES ────────────────────────────────────────────────────────
def score_crux_field(crux_mobile: dict | None, crux_desktop: dict | None) -> tuple[float, dict]:
    """
    CrUX field p75, mobile-weighted 70/30 per prompt §Step 5.
    LCP <2.5s = 100, >4s = 0. CLS <0.1 = 100, >0.25 = 0. INP <200ms = 100, >500ms = 0.
    Returns average of the three vitals, weighted 70% mobile / 30% desktop.
    """
    def device_score(crux: dict | None) -> float:
        if not crux:
            return 0  # insufficient data — penalised
        lcp_ms = crux.get("lcp_p75_ms", 99999)
        cls = crux.get("cls_p75", 1.0)
        inp_ms = crux.get("inp_p75_ms", 99999)
        lcp_s = _lerp(lcp_ms, 4000, 2500)
        cls_s = _lerp(cls, 0.25, 0.1)
        inp_s = _lerp(inp_ms, 500, 200)
        return (lcp_s + cls_s + inp_s) / 3

    mobile_s = device_score(crux_mobile)
    desktop_s = device_score(crux_desktop)
    weighted = mobile_s * 0.70 + desktop_s * 0.30
    return round(weighted, 1), {
        "mobile_score": round(mobile_s, 1),
        "desktop_score": round(desktop_s, 1),
        "crux_mobile_available": crux_mobile is not None,
        "crux_desktop_available": crux_desktop is not None,
    }


def score_lh_perf(perf_0_1: float | None) -> float:
    """Lighthouse returns 0..1; map 0.40 → 0 and 0.90 → 100."""
    if perf_0_1 is None:
        return 0
    return _lerp(perf_0_1 * 100, 40, 90)


def score_bundle_size(total_js_kb: float | None) -> tuple[float, dict]:
    if total_js_kb is None:
        return 0, {"total_js_kb": None}
    s = _lerp(total_js_kb, 1024, 200)
    return round(s, 1), {"total_js_kb": total_js_kb}


def score_image_optimisation(image_audit: dict) -> tuple[float, dict]:
    """
    4 checks: modern formats (WebP/AVIF), lazy-loaded, properly sized, no layout
    shift images. Each worth 25.
    """
    checks = {
        "modern_formats_all": image_audit.get("modern_formats_pct", 0) >= 0.9,
        "lazy_loaded_all": image_audit.get("lazy_loaded_pct", 0) >= 0.9,
        "properly_sized": image_audit.get("properly_sized", False),
        "no_layout_shift": image_audit.get("no_layout_shift", False),
    }
    passed = sum(1 for v in checks.values() if v)
    score = (passed / len(checks)) * 100
    return score, {"checks": checks, **image_audit}


def compute_perf_score(
    crux_mobile: dict | None,
    crux_desktop: dict | None,
    lh_mobile_perf: float | None,
    lh_desktop_perf: float | None,
    total_js_kb: float | None,
    image_audit: dict,
) -> tuple[float, dict]:
    crux_s, crux_b = score_crux_field(crux_mobile, crux_desktop)
    lh_m_s = round(score_lh_perf(lh_mobile_perf), 1)
    lh_d_s = round(score_lh_perf(lh_desktop_perf), 1)
    bundle_s, bundle_b = score_bundle_size(total_js_kb)
    img_s, img_b = score_image_optimisation(image_audit)

    # If CrUX field data is missing (new domain, low traffic), redistribute the
    # 35% weight proportionally to the lab-based categories rather than scoring
    # 0/35 and unfairly penalising the URL. Flag this in the breakdown.
    crux_unavailable = not crux_b.get("crux_mobile_available") and not crux_b.get("crux_desktop_available")
    if crux_unavailable:
        weights = dict(PERF_WEIGHTS)
        redistribute = weights.pop("crux_field_p75")
        # Redistribute proportionally to lab-perf categories
        lab_total = sum(weights.values())
        scale = (lab_total + redistribute) / lab_total if lab_total else 1.0
        weights = {k: round(v * scale, 1) for k, v in weights.items()}
        weighted = (
            lh_m_s * weights["lh_mobile_perf"]
            + lh_d_s * weights["lh_desktop_perf"]
            + bundle_s * weights["bundle_size"]
            + img_s * weights["image_optimisation"]
        ) / 100
        crux_block = {"score": None, "weight": 0,
                      "note": "CrUX p75 unavailable — weight redistributed to lab categories",
                      **crux_b}
    else:
        weights = PERF_WEIGHTS
        weighted = (
            crux_s * weights["crux_field_p75"]
            + lh_m_s * weights["lh_mobile_perf"]
            + lh_d_s * weights["lh_desktop_perf"]
            + bundle_s * weights["bundle_size"]
            + img_s * weights["image_optimisation"]
        ) / 100
        crux_block = {"score": crux_s, "weight": weights["crux_field_p75"], **crux_b}

    return round(weighted, 1), {
        "crux_field_p75": crux_block,
        "lh_mobile_perf": {"score": lh_m_s, "weight": weights.get("lh_mobile_perf", 0), "raw": lh_mobile_perf},
        "lh_desktop_perf": {"score": lh_d_s, "weight": weights.get("lh_desktop_perf", 0), "raw": lh_desktop_perf},
        "bundle_size": {"score": bundle_s, "weight": weights.get("bundle_size", 0), **bundle_b},
        "image_optimisation": {"score": round(img_s, 1), "weight": weights.get("image_optimisation", 0), **img_b},
    }


# ─── PRODUCT-LEVEL AGGREGATION ─────────────────────────────────────────────
def aggregate_product_score(url_scores: list[dict], metric: str) -> float:
    """
    Weighted average across tiers — Tier 1 and 3 count 2×, Tier 2 and 4 count 1×.
    metric is 'seo_score' or 'perf_score'. Each dict in url_scores must have
    'tier' and `metric`.
    """
    if not url_scores:
        return 0.0
    numer = sum(r[metric] * TIER_WEIGHTS.get(r["tier"], 1) for r in url_scores)
    denom = sum(TIER_WEIGHTS.get(r["tier"], 1) for r in url_scores)
    return round(numer / denom, 1) if denom else 0.0


# ─── DECISION THRESHOLDS (prompt §Step 7) ──────────────────────────────────
def classify_strategic_implication(seo_score: float, perf_score: float,
                                    is_legacy: bool, mobile_lcp_ms: float,
                                    worst_cls: float, hreflang_errors: bool) -> dict:
    """Return the Option A/B/C hint + which thumb rules fired."""
    fired: list[str] = []
    if seo_score < 50 and is_legacy:
        fired.append("SEOScore<50 on legacy domain → strong Option B candidate")
    if perf_score < 40:
        fired.append("PerfScore<40 on mobile-heavy traffic → strong Option B candidate")
    if mobile_lcp_ms > 4000:
        fired.append(f"Mobile LCP p75 {mobile_lcp_ms:.0f}ms > 4s → CPA tax flag")
    if worst_cls > 0.25:
        fired.append(f"CLS {worst_cls:.2f} > 0.25 anywhere in checkout → P0, revenue-impacting")
    if hreflang_errors:
        fired.append("Hreflang errors across locales → multi-locale EU traffic bleed")

    # Final hint
    if any("Option B" in x for x in fired):
        supports = "B"
    elif seo_score >= 70 and perf_score >= 70:
        supports = "A"
    else:
        supports = "A/B (needs human judgement)"

    return {"supports": supports, "triggered_rules": fired}
