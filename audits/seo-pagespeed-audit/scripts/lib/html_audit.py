"""
Static SEO audit — pure HTML parse (no JS execution).

Reads the rendered HTML returned by `requests.get` and extracts every signal
listed in prompt §Step 4. Also runs the site-level checks (robots, sitemap,
HTTPS redirect, security headers).
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


USER_AGENT = (
    "Mozilla/5.0 (compatible; SanjowAuditBot/1.0; +https://sanjow.com/audit)"
)
TIMEOUT = 30


# ─── per-URL audit ─────────────────────────────────────────────────────────
def fetch_html(url: str) -> tuple[str, dict, list[str]]:
    """Returns (html, headers, redirect_chain). Raises on non-2xx."""
    r = requests.get(url, timeout=TIMEOUT, allow_redirects=True,
                     headers={"User-Agent": USER_AGENT})
    r.raise_for_status()
    chain = [resp.url for resp in r.history] + [r.url]
    return r.text, dict(r.headers), chain


def audit_url(url: str, expected_locales: list[str]) -> dict:
    """Run the full per-URL static audit. Returns a flat dict ready for scoring."""
    try:
        html, headers, chain = fetch_html(url)
    except requests.RequestException as e:
        return {"url": url, "fetch_error": str(e)}

    soup = BeautifulSoup(html, "lxml")
    base_url = url
    parsed = urlparse(url)

    # ─── title / meta ──────────────────────────────────────────────────
    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else None

    desc_tag = soup.find("meta", attrs={"name": re.compile(r"^description$", re.I)})
    meta_description = desc_tag["content"].strip() if desc_tag and desc_tag.get("content") else None

    canonical_tag = soup.find("link", rel=lambda v: v and "canonical" in v)
    canonical = canonical_tag.get("href") if canonical_tag else None
    canonical_self = (
        canonical is not None
        and (canonical.rstrip("/") == url.rstrip("/")
             or urljoin(base_url, canonical).rstrip("/") == url.rstrip("/"))
    )

    viewport_tag = soup.find("meta", attrs={"name": re.compile(r"^viewport$", re.I)})
    viewport = viewport_tag.get("content") if viewport_tag else None
    viewport_mobile_friendly = (
        viewport is not None
        and "width=device-width" in viewport
        and "initial-scale" in viewport
    )

    robots_tag = soup.find("meta", attrs={"name": re.compile(r"^robots$", re.I)})
    robots_content = (robots_tag.get("content") if robots_tag else "") or ""
    robots_noindex = "noindex" in robots_content.lower()

    html_lang = soup.html.get("lang") if soup.html else None

    # ─── hreflang ──────────────────────────────────────────────────────
    hreflang_tags = soup.find_all("link", rel=lambda v: v and "alternate" in v,
                                  hreflang=True)
    hreflang_locales = [t.get("hreflang") for t in hreflang_tags if t.get("hreflang")]
    hreflang_xdefault = "x-default" in hreflang_locales
    locales_only = [l for l in hreflang_locales if l != "x-default"]
    hreflang_all_valid = (
        len(locales_only) > 0
        and all(re.match(r"^[a-z]{2}(-[A-Z]{2})?$", l) for l in locales_only)
    )

    # ─── Open Graph / Twitter ──────────────────────────────────────────
    def og(p): return _meta(soup, "property", f"og:{p}")
    def tw(p): return _meta(soup, "name", f"twitter:{p}")

    # ─── JSON-LD ───────────────────────────────────────────────────────
    json_ld_types = []
    json_ld_valid = True
    for s in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(s.string or "")
            if isinstance(data, list):
                for d in data:
                    if isinstance(d, dict) and "@type" in d:
                        json_ld_types.append(d["@type"])
            elif isinstance(data, dict) and "@type" in data:
                json_ld_types.append(data["@type"])
        except (json.JSONDecodeError, TypeError):
            json_ld_valid = False

    # ─── headings + content ────────────────────────────────────────────
    h1_count = len(soup.find_all("h1"))
    heading_hierarchy_valid = _check_heading_hierarchy(soup)

    text = soup.get_text(" ", strip=True)
    word_count = len(text.split())

    internal_link_count = 0
    external_link_count = 0
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("#") or href.startswith("javascript:"):
            continue
        absolute = urljoin(base_url, href)
        link_host = urlparse(absolute).netloc
        if link_host == parsed.netloc or link_host == "":
            internal_link_count += 1
        else:
            external_link_count += 1

    # ─── redirect chain ────────────────────────────────────────────────
    redirect_chain = len(chain) > 2

    return {
        "url": url,
        "final_url": chain[-1] if chain else url,
        "fetch_status": "ok",
        # Technical SEO
        "title": title,
        "meta_description": meta_description,
        "canonical": canonical,
        "canonical_self_referential": canonical_self,
        "viewport": viewport,
        "viewport_mobile_friendly": viewport_mobile_friendly,
        "html_lang": html_lang,
        "robots_noindex": robots_noindex,
        # Hreflang
        "hreflang_count": len(hreflang_tags),
        "hreflang_locales": hreflang_locales,
        "hreflang_xdefault": hreflang_xdefault,
        "hreflang_all_valid": hreflang_all_valid,
        # Open Graph / Twitter
        "og_title": og("title"),
        "og_description": og("description"),
        "og_image": og("image"),
        "og_type": og("type"),
        "og_url": og("url"),
        "twitter_card": tw("card"),
        "twitter_title": tw("title"),
        "twitter_description": tw("description"),
        "twitter_image": tw("image"),
        # JSON-LD
        "json_ld_types": list(set(json_ld_types)),
        "json_ld_valid": json_ld_valid,
        # Content
        "h1_count": h1_count,
        "heading_hierarchy_valid": heading_hierarchy_valid,
        "word_count": word_count,
        "internal_link_count": internal_link_count,
        "external_link_count": external_link_count,
        # Redirects
        "redirect_chain": redirect_chain,
        "canonical_loop": False,
        # Headers (for site-level cross-ref)
        "response_headers": {k: v for k, v in headers.items()
                              if k.lower() in ("strict-transport-security",
                                               "x-content-type-options",
                                               "referrer-policy",
                                               "content-security-policy")},
    }


def _meta(soup: BeautifulSoup, attr: str, value: str) -> str | None:
    tag = soup.find("meta", attrs={attr: value})
    if tag and tag.get("content"):
        return tag["content"].strip()
    return None


def _check_heading_hierarchy(soup: BeautifulSoup) -> bool:
    """Return True if no heading skips a level (e.g., h2 → h4)."""
    headings = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
    last = 0
    for h in headings:
        level = int(h.name[1])
        if last and level > last + 1:
            return False
        last = level
    return True


# ─── site-level audit ─────────────────────────────────────────────────────
def audit_site(domain: str, expected_locales_count: int) -> dict:
    """One-shot site-level checks: robots.txt, sitemap.xml, HTTPS redirect."""
    parsed = urlparse(domain)
    origin = f"{parsed.scheme}://{parsed.netloc}"

    result = {
        "origin": origin,
        "expected_locales_count": expected_locales_count,
        "robots_txt_exists": False,
        "robots_has_sitemap": False,
        "sitemap_exists": False,
        "sitemap_valid": False,
        "sitemap_hreflang": False,
        "sitemap_url_count": 0,
        "https_redirect": False,
        "hsts_enabled": False,
        "x_content_type_options": False,
        "referrer_policy_set": False,
        "parameterised_routes": True,  # Next.js dynamic routes — assume true unless proven false
    }

    # robots.txt
    try:
        r = requests.get(f"{origin}/robots.txt", timeout=TIMEOUT,
                         headers={"User-Agent": USER_AGENT})
        if r.status_code == 200 and r.text.strip():
            result["robots_txt_exists"] = True
            result["robots_has_sitemap"] = bool(re.search(r"^Sitemap:\s*", r.text,
                                                          re.IGNORECASE | re.MULTILINE))
            sitemap_match = re.search(r"^Sitemap:\s*(\S+)", r.text,
                                      re.IGNORECASE | re.MULTILINE)
            sitemap_url = (sitemap_match.group(1) if sitemap_match
                           else f"{origin}/sitemap.xml")
        else:
            sitemap_url = f"{origin}/sitemap.xml"
    except requests.RequestException:
        sitemap_url = f"{origin}/sitemap.xml"

    # sitemap.xml
    try:
        r = requests.get(sitemap_url, timeout=TIMEOUT,
                         headers={"User-Agent": USER_AGENT})
        if r.status_code == 200 and "<urlset" in r.text or "<sitemapindex" in r.text:
            result["sitemap_exists"] = True
            result["sitemap_valid"] = "</urlset>" in r.text or "</sitemapindex>" in r.text
            result["sitemap_url_count"] = r.text.count("<loc>")
            result["sitemap_hreflang"] = "xhtml:link" in r.text or 'rel="alternate"' in r.text
    except requests.RequestException:
        pass

    # HTTPS redirect
    if parsed.scheme == "https":
        try:
            http_origin = f"http://{parsed.netloc}"
            r = requests.get(http_origin, timeout=TIMEOUT, allow_redirects=False,
                             headers={"User-Agent": USER_AGENT})
            if r.status_code in (301, 302, 307, 308):
                loc = r.headers.get("Location", "")
                if loc.startswith("https://"):
                    result["https_redirect"] = True
        except requests.RequestException:
            pass

    # security headers — fetch the homepage and read headers
    try:
        r = requests.head(domain, timeout=TIMEOUT, allow_redirects=True,
                          headers={"User-Agent": USER_AGENT})
        h = {k.lower(): v for k, v in r.headers.items()}
        result["hsts_enabled"] = "strict-transport-security" in h
        result["x_content_type_options"] = h.get("x-content-type-options", "").lower() == "nosniff"
        result["referrer_policy_set"] = "referrer-policy" in h
    except requests.RequestException:
        pass

    return result


def save_html_audit(audit_dir: Path, product: str, audits: list[dict]) -> Path:
    audit_dir.mkdir(parents=True, exist_ok=True)
    out = audit_dir / f"{product}.json"
    out.write_text(json.dumps(audits, indent=2))
    return out
