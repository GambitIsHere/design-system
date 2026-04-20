"""
PageSpeed Insights v5 client.

Wraps the public PSI endpoint with the rate-limit + retry rules from the
prompt §Step 3:
  - 200ms delay between calls (env-overridable)
  - retry once on 5xx with exponential backoff (1s then 3s)
  - on 429, wait 60s and retry once
  - save raw JSON to data/psi-raw/{product}/{url-hash}-{strategy}.json
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

import requests

PSI_ENDPOINT = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
CRUX_ENDPOINT = "https://chromeuxreport.googleapis.com/v1/records:queryRecord"


class PSIError(Exception):
    pass


def url_hash(url: str) -> str:
    return hashlib.sha1(url.encode("utf-8")).hexdigest()[:12]


def _log(msg: str) -> None:
    """Flushed stderr log so progress is visible even when piped."""
    print(msg, file=sys.stderr, flush=True)


class PSIClient:
    def __init__(self, api_key: str, raw_dir: Path,
                 delay_ms: int = 200,
                 connect_timeout: int = 10,
                 read_timeout: int = 60,
                 max_attempts: int = 3):
        if not api_key:
            raise PSIError("PSI_API_KEY missing — set it in .env before running.")
        self.api_key = api_key
        self.raw_dir = Path(raw_dir)
        self.delay_ms = delay_ms
        # (connect, read) per requests docs — connect short, read longer
        self.timeout = (connect_timeout, read_timeout)
        self.max_attempts = max_attempts

    # ─── PSI ──────────────────────────────────────────────────────────────
    def run_pagespeed(self, url: str, *, strategy: str, locale: str,
                      product: str) -> dict:
        """Run PSI for one URL/strategy. Saves raw JSON. Returns parsed dict.

        Reads from cache (data/psi-raw/{product}/{hash}-{strategy}.json) if
        present, so multiple partial runs can accumulate coverage without
        re-spending PSI quota or re-waiting 25-30s per URL.
        """
        out_dir = self.raw_dir / product
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{url_hash(url)}-{strategy}.json"
        err_path = out_dir / f"{url_hash(url)}-{strategy}.error.json"

        if out_path.exists():
            _log(f"  ✓ cache {strategy:7s} {url}")
            return json.loads(out_path.read_text())
        if err_path.exists():
            _log(f"  ✗ cached-err {strategy:7s} {url}")
            cached = json.loads(err_path.read_text())
            raise PSIError(cached.get("error", "cached PSI error"))

        params = {
            "url": url,
            "strategy": strategy,
            "category": ["PERFORMANCE", "SEO", "ACCESSIBILITY", "BEST_PRACTICES"],
            "locale": locale,
            "key": self.api_key,
        }
        # requests handles repeated `category` correctly when given a list
        full_url = f"{PSI_ENDPOINT}?{urlencode(params, doseq=True)}"

        t0 = time.monotonic()
        _log(f"  → PSI {strategy:7s} {url}")
        try:
            data = self._request_with_retry(full_url, label=f"{url} [{strategy}]")
        except PSIError as e:
            # Persist the failure so repeated runs skip it — cheaper than hitting
            # a broken site twice. Callers already treat PSIError as a finding.
            err_path.write_text(json.dumps({"error": str(e)[:500]}, indent=2))
            raise
        elapsed = time.monotonic() - t0
        _log(f"  ← PSI {strategy:7s} done in {elapsed:.1f}s")

        out_path.write_text(json.dumps(data, indent=2))
        return data

    # ─── CrUX (origin fallback) ───────────────────────────────────────────
    def run_crux_origin(self, origin: str, *, form_factor: str = "PHONE") -> dict | None:
        """
        Origin-level CrUX for fallback when URL-level data is missing.
        Returns None on 404 (insufficient data — itself a finding).
        """
        body = {"origin": origin, "formFactor": form_factor}
        try:
            r = requests.post(
                f"{CRUX_ENDPOINT}?key={self.api_key}",
                json=body,
                timeout=self.timeout,
            )
            if r.status_code == 404:
                return None
            r.raise_for_status()
            return r.json()
        except requests.RequestException as e:
            raise PSIError(f"CrUX request failed for {origin}: {e}") from e

    # ─── retry policy ─────────────────────────────────────────────────────
    def _request_with_retry(self, url: str, *, label: str = "") -> dict:
        """
        Bounded retries with visible logging. Hard cap = self.max_attempts.
        429: single 60s retry. 5xx + network errors: exponential 1s, 3s.
        """
        backoffs = [1, 3, 7]
        for attempt in range(1, self.max_attempts + 1):
            try:
                r = requests.get(url, timeout=self.timeout)
            except requests.Timeout as e:
                _log(f"    · timeout (attempt {attempt}/{self.max_attempts}) {label}")
                if attempt >= self.max_attempts:
                    raise PSIError(f"PSI timeout after {attempt} attempts: {label}") from e
                time.sleep(backoffs[min(attempt - 1, len(backoffs) - 1)])
                continue
            except requests.RequestException as e:
                _log(f"    · net error (attempt {attempt}/{self.max_attempts}) {e}")
                if attempt >= self.max_attempts:
                    raise PSIError(f"PSI network error after retries: {e}") from e
                time.sleep(backoffs[min(attempt - 1, len(backoffs) - 1)])
                continue

            if r.status_code == 429:
                _log(f"    · 429 rate-limited (attempt {attempt}) — sleeping 60s")
                if attempt >= self.max_attempts:
                    raise PSIError(f"PSI 429 after {attempt} attempts: {r.text[:200]}")
                time.sleep(60)
                continue

            if 500 <= r.status_code < 600:
                _log(f"    · {r.status_code} (attempt {attempt}/{self.max_attempts})")
                if attempt >= self.max_attempts:
                    raise PSIError(f"PSI {r.status_code} after retries: {r.text[:200]}")
                time.sleep(backoffs[min(attempt - 1, len(backoffs) - 1)])
                continue

            if r.status_code != 200:
                raise PSIError(f"PSI {r.status_code}: {r.text[:300]}")

            # politeness delay before next call
            time.sleep(self.delay_ms / 1000)
            return r.json()

        raise PSIError(f"PSI exhausted retries: {label}")


# ─── extractors ─────────────────────────────────────────────────────────────
def extract_lighthouse_scores(psi_response: dict) -> dict:
    cats = psi_response.get("lighthouseResult", {}).get("categories", {})
    return {
        "performance": cats.get("performance", {}).get("score"),
        "seo": cats.get("seo", {}).get("score"),
        "accessibility": cats.get("accessibility", {}).get("score"),
        "best-practices": cats.get("best-practices", {}).get("score"),
    }


def extract_lab_cwv(psi_response: dict) -> dict:
    audits = psi_response.get("lighthouseResult", {}).get("audits", {})

    def numeric(audit_id: str) -> float | None:
        v = audits.get(audit_id, {}).get("numericValue")
        return float(v) if v is not None else None

    return {
        "lcp_ms": numeric("largest-contentful-paint"),
        "cls": numeric("cumulative-layout-shift"),
        "tbt_ms": numeric("total-blocking-time"),
        "fcp_ms": numeric("first-contentful-paint"),
        "ttfb_ms": numeric("server-response-time"),
        "speed_index_ms": numeric("speed-index"),
        "interactive_ms": numeric("interactive"),
    }


def extract_field_cwv(psi_response: dict) -> dict | None:
    """CrUX p75 from the same PSI call (loadingExperience). None if missing."""
    le = psi_response.get("loadingExperience", {})
    metrics = le.get("metrics")
    if not metrics:
        return None

    def percentile(key: str) -> float | None:
        m = metrics.get(key)
        return float(m["percentile"]) if m and "percentile" in m else None

    return {
        "lcp_p75_ms": percentile("LARGEST_CONTENTFUL_PAINT_MS"),
        "cls_p75": (percentile("CUMULATIVE_LAYOUT_SHIFT_SCORE") or 0) / 100
                    if percentile("CUMULATIVE_LAYOUT_SHIFT_SCORE") is not None else None,
        "inp_p75_ms": percentile("INTERACTION_TO_NEXT_PAINT")
                       or percentile("EXPERIMENTAL_INTERACTION_TO_NEXT_PAINT"),
        "fcp_p75_ms": percentile("FIRST_CONTENTFUL_PAINT_MS"),
        "ttfb_p75_ms": percentile("EXPERIMENTAL_TIME_TO_FIRST_BYTE"),
        "origin_fallback": le.get("origin_fallback", False),
    }


def extract_top_opportunities(psi_response: dict, n: int = 5) -> list[dict]:
    audits = psi_response.get("lighthouseResult", {}).get("audits", {})
    opps = []
    for aid, a in audits.items():
        details = a.get("details") or {}
        if details.get("type") != "opportunity":
            continue
        savings = a.get("numericValue") or 0
        if savings <= 0:
            continue
        opps.append({
            "id": aid,
            "title": a.get("title"),
            "description": a.get("description", "").split("[")[0].strip(),
            "savings_ms": int(savings),
        })
    opps.sort(key=lambda x: x["savings_ms"], reverse=True)
    return opps[:n]


def extract_top_diagnostics(psi_response: dict, n: int = 5) -> list[dict]:
    audits = psi_response.get("lighthouseResult", {}).get("audits", {})
    diags = []
    for aid, a in audits.items():
        details = a.get("details") or {}
        if details.get("type") not in ("table", "debugdata"):
            continue
        # Lighthouse marks diagnostics with score == None or score == 1 with displayValue
        if a.get("score") is None or a.get("scoreDisplayMode") == "informative":
            diags.append({
                "id": aid,
                "title": a.get("title"),
                "displayValue": a.get("displayValue"),
            })
    return diags[:n]


def extract_bundle_info(psi_response: dict) -> dict:
    audits = psi_response.get("lighthouseResult", {}).get("audits", {})
    total_byte_weight = audits.get("total-byte-weight", {}).get("numericValue") or 0
    network_requests = audits.get("network-requests", {}).get("details", {}).get("items", [])

    js_bytes_transferred = 0
    js_request_count = 0
    largest_js = {"url": None, "kb": 0}
    for req in network_requests:
        if req.get("resourceType") == "Script":
            js_request_count += 1
            tb = req.get("transferSize") or 0
            js_bytes_transferred += tb
            if tb > largest_js["kb"] * 1024:
                largest_js = {"url": req.get("url"), "kb": round(tb / 1024, 1)}

    unused_js_kb = (audits.get("unused-javascript", {})
                    .get("details", {}).get("overallSavingsBytes") or 0) / 1024

    return {
        "total_byte_weight_kb": round(total_byte_weight / 1024, 1),
        "js_transferred_kb": round(js_bytes_transferred / 1024, 1),
        "js_request_count": js_request_count,
        "largest_js_bundle": largest_js,
        "unused_js_kb": round(unused_js_kb, 1),
    }


def extract_image_audit(psi_response: dict) -> dict:
    audits = psi_response.get("lighthouseResult", {}).get("audits", {})
    modern_formats = audits.get("modern-image-formats", {}).get("score")
    offscreen = audits.get("offscreen-images", {}).get("score")
    properly_sized = audits.get("uses-responsive-images", {}).get("score")
    no_layout_shift = (audits.get("non-composited-animations", {}).get("score") or 1) >= 0.9

    # Lighthouse scores: 1 = pass, <1 = opportunity. Use them as proxies.
    return {
        "modern_formats_pct": (modern_formats if modern_formats is not None else 0),
        "lazy_loaded_pct": (offscreen if offscreen is not None else 0),
        "properly_sized": (properly_sized or 0) >= 0.9,
        "no_layout_shift": no_layout_shift,
    }
