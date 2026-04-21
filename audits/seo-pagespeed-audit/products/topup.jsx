import { useState, useMemo } from "react";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  Legend, CartesianGrid,
} from "recharts";
import {
  AlertTriangle, CheckCircle2, AlertCircle, Info, Filter,
  ArrowUp, ArrowDown, Minus,
} from "lucide-react";

const DATA = {
  "meta": {
    "product_id": "topup",
    "product_name": "TopUp",
    "audit_date": "2026-04-21T09:00:31+00:00",
    "run_id": "20260421T090031+0000",
    "locales": [
      "en",
      "fr"
    ],
    "url_count": 8,
    "domain_count": 2
  },
  "scores": {
    "seo": 15.7,
    "perf": 11.8,
    "seo_breakdown": {
      "technical_seo": {
        "score": 70.0,
        "weight": 25,
        "checks": {
          "title_present": true,
          "title_length_ok": false,
          "meta_description_present": true,
          "meta_description_length_ok": true,
          "canonical_present": false,
          "canonical_self_referential": false,
          "viewport_present": true,
          "viewport_mobile_friendly": true,
          "html_lang_present": true,
          "robots_not_noindex": true
        },
        "passed": 7,
        "total": 10
      },
      "crawlability": {
        "score": 87.5,
        "weight": 20,
        "checks": {
          "robots_txt_exists": true,
          "robots_has_sitemap_directive": true,
          "sitemap_exists": true,
          "sitemap_valid_xml": true,
          "sitemap_has_hreflang": false,
          "http_to_https_redirects": true,
          "no_redirect_chains": true,
          "no_broken_canonical_loops": true
        },
        "passed": 7,
        "total": 8
      },
      "content_structure": {
        "score": 75.0,
        "weight": 15,
        "checks": {
          "exactly_one_h1": true,
          "word_count_500_plus": true,
          "heading_hierarchy_valid": false,
          "internal_links_10_plus": true
        },
        "h1_count": 1,
        "word_count": 1111,
        "internal_links": 67
      },
      "structured_data": {
        "score": 60.0,
        "weight": 15,
        "checks": {
          "json_ld_present": false,
          "json_ld_valid": true,
          "og_title": true,
          "og_description": true,
          "og_image": true,
          "og_type": true,
          "og_url": true,
          "twitter_card": false,
          "twitter_title": false,
          "twitter_image": false
        },
        "json_ld_types": []
      },
      "programmatic_scalability": {
        "score": 30.0,
        "weight": 25,
        "hreflang_coverage": 0.0,
        "hreflang_valid": false,
        "has_xdefault": false,
        "parameterised_routes": true,
        "alt_count": 0,
        "expected_locales": 2
      }
    },
    "perf_breakdown": {
      "crux_field_p75": {
        "score": 70.4,
        "weight": 35,
        "mobile_score": 62.6,
        "desktop_score": 88.9,
        "crux_mobile_available": true,
        "crux_desktop_available": true
      },
      "lh_mobile_perf": {
        "score": 30.0,
        "weight": 30,
        "raw": 0.55
      },
      "lh_desktop_perf": {
        "score": 54.0,
        "weight": 15,
        "raw": 0.67
      },
      "bundle_size": {
        "score": 29.5,
        "weight": 10,
        "total_js_kb": 780.9
      },
      "image_optimisation": {
        "score": 25.0,
        "weight": 10,
        "checks": {
          "modern_formats_all": false,
          "lazy_loaded_all": false,
          "properly_sized": false,
          "no_layout_shift": true
        },
        "modern_formats_pct": 0,
        "lazy_loaded_pct": 0,
        "properly_sized": false,
        "no_layout_shift": true
      }
    }
  },
  "decision": {
    "option": "B",
    "rules": [
      "SEOScore<50 on legacy domain \u2192 strong Option B candidate",
      "PerfScore<40 on mobile-heavy traffic \u2192 strong Option B candidate",
      "Mobile LCP p75 4397ms > 4s \u2192 CPA tax flag",
      "Hreflang errors across locales \u2192 multi-locale EU traffic bleed"
    ],
    "rationale": "Architectural drag and/or perf floor low enough that a clean-domain rebuild beats incremental fixes."
  },
  "domains": [
    {
      "url": "https://topup.com",
      "host": "topup.com",
      "role": "legacy",
      "metrics": {
        "lh_perf_mobile": 60,
        "lh_perf_desktop": 70,
        "lh_seo": 100,
        "cwv_lcp": 3510.8,
        "cwv_cls": 0.0,
        "cwv_inp": 148.5,
        "js_kb_mobile": 767.4,
        "seo_score": 31.4,
        "perf_score": 23.6
      }
    },
    {
      "url": "https://new-topup.com",
      "host": "new-topup.com",
      "role": "clean",
      "metrics": {
        "lh_perf_mobile": null,
        "lh_perf_desktop": null,
        "lh_seo": null,
        "cwv_lcp": null,
        "cwv_cls": null,
        "cwv_inp": null,
        "js_kb_mobile": null,
        "seo_score": 0.0,
        "perf_score": 0.0
      }
    }
  ],
  "lighthouse": [
    {
      "url": "topup.com/",
      "strategy": "mobile",
      "perf": 55,
      "seo": 100,
      "a11y": 86,
      "bp": 81
    },
    {
      "url": "topup.com/",
      "strategy": "desktop",
      "perf": 67,
      "seo": 100,
      "a11y": 86,
      "bp": 81
    },
    {
      "url": "topup.com/fr/",
      "strategy": "mobile",
      "perf": 56,
      "seo": 92,
      "a11y": 91,
      "bp": 77
    },
    {
      "url": "topup.com/fr/",
      "strategy": "desktop",
      "perf": 67,
      "seo": 92,
      "a11y": 91,
      "bp": 77
    },
    {
      "url": "new-topup.com/",
      "strategy": "mobile",
      "perf": null,
      "seo": null,
      "a11y": null,
      "bp": null
    },
    {
      "url": "new-topup.com/",
      "strategy": "desktop",
      "perf": null,
      "seo": null,
      "a11y": null,
      "bp": null
    },
    {
      "url": "new-topup.com/fr/",
      "strategy": "mobile",
      "perf": null,
      "seo": null,
      "a11y": null,
      "bp": null
    },
    {
      "url": "new-topup.com/fr/",
      "strategy": "desktop",
      "perf": null,
      "seo": null,
      "a11y": null,
      "bp": null
    }
  ],
  "cwv": [
    {
      "url": "topup.com/",
      "strategy": "mobile",
      "lcp": 4397.0,
      "cls": 0.01,
      "inp": 237.0,
      "ttfb": 2739.0,
      "verdict": "poor"
    },
    {
      "url": "topup.com/",
      "strategy": "desktop",
      "lcp": 3001.0,
      "cls": 0.01,
      "inp": 82.0,
      "ttfb": 1761.0,
      "verdict": "ni"
    },
    {
      "url": "topup.com/fr/",
      "strategy": "mobile",
      "lcp": 3837.0,
      "cls": 0.01,
      "inp": 210.0,
      "ttfb": 2627.0,
      "verdict": "ni"
    },
    {
      "url": "topup.com/fr/",
      "strategy": "desktop",
      "lcp": 2808.0,
      "cls": 0.01,
      "inp": 65.0,
      "ttfb": 2087.0,
      "verdict": "ni"
    },
    {
      "url": "new-topup.com/",
      "strategy": "mobile",
      "lcp": null,
      "cls": null,
      "inp": null,
      "ttfb": null,
      "verdict": "no-data"
    },
    {
      "url": "new-topup.com/",
      "strategy": "desktop",
      "lcp": null,
      "cls": null,
      "inp": null,
      "ttfb": null,
      "verdict": "no-data"
    },
    {
      "url": "new-topup.com/fr/",
      "strategy": "mobile",
      "lcp": null,
      "cls": null,
      "inp": null,
      "ttfb": null,
      "verdict": "no-data"
    },
    {
      "url": "new-topup.com/fr/",
      "strategy": "desktop",
      "lcp": null,
      "cls": null,
      "inp": null,
      "ttfb": null,
      "verdict": "no-data"
    }
  ],
  "findings": [
    {
      "severity": "P1",
      "area": "seo",
      "label": "fixable-in-place",
      "url": "topup.com/",
      "field": "canonical link",
      "current": "missing",
      "target": "self-referential canonical",
      "fix": "Emit a self-referential `<link rel='canonical'>` via metadata.",
      "rationale": "Metadata API."
    },
    {
      "severity": "P1",
      "area": "locale",
      "label": "fixable-in-place",
      "url": "topup.com/",
      "field": "hreflang coverage",
      "current": "0 of 2 locales",
      "target": "2 hreflang tags + x-default",
      "fix": "Emit hreflang for every locale route + x-default.",
      "rationale": "Middleware or metadata config."
    },
    {
      "severity": "P1",
      "area": "seo",
      "label": "fixable-in-place",
      "url": "topup.com/fr/",
      "field": "<title>",
      "current": "missing",
      "target": "30\u201360 char unique title",
      "fix": "Add a page-level title via Next.js metadata.",
      "rationale": "App router `metadata` is the standard pattern."
    },
    {
      "severity": "P1",
      "area": "seo",
      "label": "fixable-in-place",
      "url": "topup.com/fr/",
      "field": "meta description",
      "current": "missing",
      "target": "120\u2013160 char unique description",
      "fix": "Add a description via Next.js metadata.",
      "rationale": "Metadata API."
    },
    {
      "severity": "P1",
      "area": "seo",
      "label": "fixable-in-place",
      "url": "topup.com/fr/",
      "field": "canonical link",
      "current": "missing",
      "target": "self-referential canonical",
      "fix": "Emit a self-referential `<link rel='canonical'>` via metadata.",
      "rationale": "Metadata API."
    },
    {
      "severity": "P1",
      "area": "locale",
      "label": "fixable-in-place",
      "url": "topup.com/fr/",
      "field": "hreflang coverage",
      "current": "0 of 2 locales",
      "target": "2 hreflang tags + x-default",
      "fix": "Emit hreflang for every locale route + x-default.",
      "rationale": "Middleware or metadata config."
    },
    {
      "severity": "P1",
      "area": "perf",
      "label": "fixable-in-place",
      "url": "topup.com/",
      "field": "mobile LCP p75",
      "current": "4397ms",
      "target": "<2500ms",
      "fix": "Optimise LCP element (image preload, size, format).",
      "rationale": "Standard LCP optimisation."
    },
    {
      "severity": "P1",
      "area": "seo",
      "label": "fixable-in-place",
      "url": "new-topup.com",
      "field": "sitemap.xml",
      "current": "missing",
      "target": "valid XML sitemap at /sitemap.xml",
      "fix": "Generate a sitemap (Next.js app router supports `sitemap.ts`).",
      "rationale": "Framework-level config \u2014 no architectural change needed."
    },
    {
      "severity": "P1",
      "area": "seo",
      "label": "fixable-in-place",
      "url": "new-topup.com/",
      "field": "<title>",
      "current": "missing",
      "target": "30\u201360 char unique title",
      "fix": "Add a page-level title via Next.js metadata.",
      "rationale": "App router `metadata` is the standard pattern."
    },
    {
      "severity": "P1",
      "area": "seo",
      "label": "fixable-in-place",
      "url": "new-topup.com/",
      "field": "meta description",
      "current": "missing",
      "target": "120\u2013160 char unique description",
      "fix": "Add a description via Next.js metadata.",
      "rationale": "Metadata API."
    },
    {
      "severity": "P1",
      "area": "seo",
      "label": "fixable-in-place",
      "url": "new-topup.com/",
      "field": "canonical link",
      "current": "missing",
      "target": "self-referential canonical",
      "fix": "Emit a self-referential `<link rel='canonical'>` via metadata.",
      "rationale": "Metadata API."
    },
    {
      "severity": "P1",
      "area": "locale",
      "label": "fixable-in-place",
      "url": "new-topup.com/",
      "field": "hreflang coverage",
      "current": "0 of 2 locales",
      "target": "2 hreflang tags + x-default",
      "fix": "Emit hreflang for every locale route + x-default.",
      "rationale": "Middleware or metadata config."
    },
    {
      "severity": "P1",
      "area": "seo",
      "label": "fixable-in-place",
      "url": "new-topup.com/fr/",
      "field": "<title>",
      "current": "missing",
      "target": "30\u201360 char unique title",
      "fix": "Add a page-level title via Next.js metadata.",
      "rationale": "App router `metadata` is the standard pattern."
    },
    {
      "severity": "P1",
      "area": "seo",
      "label": "fixable-in-place",
      "url": "new-topup.com/fr/",
      "field": "meta description",
      "current": "missing",
      "target": "120\u2013160 char unique description",
      "fix": "Add a description via Next.js metadata.",
      "rationale": "Metadata API."
    },
    {
      "severity": "P1",
      "area": "seo",
      "label": "fixable-in-place",
      "url": "new-topup.com/fr/",
      "field": "canonical link",
      "current": "missing",
      "target": "self-referential canonical",
      "fix": "Emit a self-referential `<link rel='canonical'>` via metadata.",
      "rationale": "Metadata API."
    },
    {
      "severity": "P1",
      "area": "locale",
      "label": "fixable-in-place",
      "url": "new-topup.com/fr/",
      "field": "hreflang coverage",
      "current": "0 of 2 locales",
      "target": "2 hreflang tags + x-default",
      "fix": "Emit hreflang for every locale route + x-default.",
      "rationale": "Middleware or metadata config."
    },
    {
      "severity": "P2",
      "area": "seo",
      "label": "fixable-in-place",
      "url": "topup.com/",
      "field": "<title> length",
      "current": "73 chars",
      "target": "30\u201360 chars",
      "fix": "Tighten or expand the title to 30\u201360 characters.",
      "rationale": "Copy change."
    },
    {
      "severity": "P2",
      "area": "seo",
      "label": "fixable-in-place",
      "url": "topup.com/",
      "field": "JSON-LD",
      "current": "none",
      "target": "relevant schema.org types (Organization, WebSite, Product, FAQ)",
      "fix": "Inject JSON-LD for the page's primary entity type.",
      "rationale": "Content injection."
    },
    {
      "severity": "P2",
      "area": "seo",
      "label": "fixable-in-place",
      "url": "topup.com/fr/",
      "field": "h1 count",
      "current": "0 h1 tags",
      "target": "exactly 1 h1 per page",
      "fix": "Ensure exactly one h1 per route; demote duplicates to h2.",
      "rationale": "Component-level fix."
    },
    {
      "severity": "P2",
      "area": "seo",
      "label": "fixable-in-place",
      "url": "topup.com/fr/",
      "field": "Open Graph",
      "current": "incomplete",
      "target": "og:title + og:description + og:image + og:url + og:type",
      "fix": "Emit full OG tags via Next.js metadata.openGraph.",
      "rationale": "Metadata API."
    },
    {
      "severity": "P2",
      "area": "seo",
      "label": "fixable-in-place",
      "url": "topup.com/fr/",
      "field": "JSON-LD",
      "current": "none",
      "target": "relevant schema.org types (Organization, WebSite, Product, FAQ)",
      "fix": "Inject JSON-LD for the page's primary entity type.",
      "rationale": "Content injection."
    },
    {
      "severity": "P2",
      "area": "seo",
      "label": "fixable-in-place",
      "url": "new-topup.com/",
      "field": "h1 count",
      "current": "0 h1 tags",
      "target": "exactly 1 h1 per page",
      "fix": "Ensure exactly one h1 per route; demote duplicates to h2.",
      "rationale": "Component-level fix."
    },
    {
      "severity": "P2",
      "area": "seo",
      "label": "fixable-in-place",
      "url": "new-topup.com/",
      "field": "Open Graph",
      "current": "incomplete",
      "target": "og:title + og:description + og:image + og:url + og:type",
      "fix": "Emit full OG tags via Next.js metadata.openGraph.",
      "rationale": "Metadata API."
    },
    {
      "severity": "P2",
      "area": "seo",
      "label": "fixable-in-place",
      "url": "new-topup.com/",
      "field": "JSON-LD",
      "current": "none",
      "target": "relevant schema.org types (Organization, WebSite, Product, FAQ)",
      "fix": "Inject JSON-LD for the page's primary entity type.",
      "rationale": "Content injection."
    },
    {
      "severity": "P2",
      "area": "seo",
      "label": "fixable-in-place",
      "url": "new-topup.com/fr/",
      "field": "h1 count",
      "current": "0 h1 tags",
      "target": "exactly 1 h1 per page",
      "fix": "Ensure exactly one h1 per route; demote duplicates to h2.",
      "rationale": "Component-level fix."
    },
    {
      "severity": "P2",
      "area": "seo",
      "label": "fixable-in-place",
      "url": "new-topup.com/fr/",
      "field": "Open Graph",
      "current": "incomplete",
      "target": "og:title + og:description + og:image + og:url + og:type",
      "fix": "Emit full OG tags via Next.js metadata.openGraph.",
      "rationale": "Metadata API."
    },
    {
      "severity": "P2",
      "area": "seo",
      "label": "fixable-in-place",
      "url": "new-topup.com/fr/",
      "field": "JSON-LD",
      "current": "none",
      "target": "relevant schema.org types (Organization, WebSite, Product, FAQ)",
      "fix": "Inject JSON-LD for the page's primary entity type.",
      "rationale": "Content injection."
    },
    {
      "severity": "P3",
      "area": "security",
      "label": "fixable-in-place",
      "url": "new-topup.com",
      "field": "Strict-Transport-Security",
      "current": "missing",
      "target": "max-age >= 15768000; includeSubDomains",
      "fix": "Add HSTS header at the edge (Vercel/CDN).",
      "rationale": "Edge config change."
    }
  ]
};

// ─── small utilities ────────────────────────────────────────────────────
const SCORE_COLOR = (v) =>
  v >= 80 ? "text-emerald-600" : v >= 60 ? "text-amber-500" : v >= 40 ? "text-orange-500" : "text-red-600";
const SCORE_BG = (v) =>
  v >= 80 ? "bg-emerald-50 border-emerald-200" :
  v >= 60 ? "bg-amber-50 border-amber-200" :
  v >= 40 ? "bg-orange-50 border-orange-200" : "bg-red-50 border-red-200";
const SEV_BG = {
  P0: "bg-red-100 text-red-700 border-red-200",
  P1: "bg-orange-100 text-orange-700 border-orange-200",
  P2: "bg-amber-100 text-amber-700 border-amber-200",
  P3: "bg-slate-100 text-slate-600 border-slate-200",
};
const AREA_BG = {
  seo:      "bg-blue-50 text-blue-700",
  perf:     "bg-purple-50 text-purple-700",
  locale:   "bg-pink-50 text-pink-700",
  security: "bg-slate-50 text-slate-700",
};
const VERDICT_BADGE = {
  good: { label: "Good",     cls: "bg-emerald-100 text-emerald-700" },
  ni:   { label: "Needs imp.", cls: "bg-amber-100 text-amber-700" },
  poor: { label: "Poor",     cls: "bg-red-100 text-red-700" },
  "no-data": { label: "No CrUX data", cls: "bg-slate-100 text-slate-500" },
};
const OPTION_THEME = {
  A: { bg: "bg-emerald-600", title: "Option A — Fix in place",     icon: CheckCircle2 },
  B: { bg: "bg-amber-600",   title: "Option B — Clean-domain rebuild", icon: AlertTriangle },
  C: { bg: "bg-red-600",     title: "Option C — Sunset",           icon: AlertCircle },
};

// ─── widgets ────────────────────────────────────────────────────────────
function DecisionBanner({ decision }) {
  const theme = OPTION_THEME[decision.option] || OPTION_THEME.A;
  const Icon = theme.icon;
  return (
    <div className={`${theme.bg} text-white rounded-xl p-6 shadow-md`}>
      <div className="flex items-start gap-4">
        <Icon className="w-8 h-8 mt-1 flex-shrink-0" />
        <div className="flex-1">
          <div className="text-sm uppercase tracking-wider opacity-80">Decision</div>
          <h2 className="text-2xl font-bold mt-1">{theme.title}</h2>
          <p className="mt-2 text-white/90">{decision.rationale}</p>
          {decision.rules?.length > 0 && (
            <div className="mt-4">
              <div className="text-xs uppercase tracking-wider opacity-80 mb-2">Triggered by</div>
              <ul className="space-y-1">
                {decision.rules.map((r, i) => (
                  <li key={i} className="text-sm flex gap-2"><span>•</span><span>{r}</span></li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function ScoreCard({ label, value, max = 100 }) {
  return (
    <div className={`rounded-xl border p-6 ${SCORE_BG(value)}`}>
      <div className="text-sm font-medium text-slate-600 uppercase tracking-wider">{label}</div>
      <div className="mt-2 flex items-baseline gap-2">
        <span className={`text-5xl font-bold ${SCORE_COLOR(value)}`}>{value}</span>
        <span className="text-slate-400 text-lg">/ {max}</span>
      </div>
    </div>
  );
}

function MetricRow({ label, clean, legacy, unit, lowerIsBetter }) {
  const both = clean != null && legacy != null;
  const cleanBetter = both && (lowerIsBetter ? clean < legacy : clean > legacy);
  const Arrow = !both ? Minus : cleanBetter ? ArrowUp : ArrowDown;
  const arrowCls = !both ? "text-slate-300" : cleanBetter ? "text-emerald-500" : "text-red-500";
  const fmt = (v) => v == null ? "—" : (unit ? `${v}${unit}` : v);
  return (
    <tr className="border-t border-slate-100">
      <td className="py-2 text-sm text-slate-600">{label}</td>
      <td className="py-2 text-sm font-mono text-slate-900 text-right">{fmt(clean)}</td>
      <td className="py-2 px-2"><Arrow className={`w-4 h-4 ${arrowCls}`} /></td>
      <td className="py-2 text-sm font-mono text-slate-900 text-right">{fmt(legacy)}</td>
    </tr>
  );
}

function DomainCompare({ domains }) {
  const clean = domains.find((d) => d.role === "clean");
  const legacy = domains.find((d) => d.role === "legacy");
  if (!clean || !legacy) {
    return (
      <div className="grid md:grid-cols-2 gap-4">
        {domains.map((d) => <DomainCard key={d.url} domain={d} />)}
      </div>
    );
  }
  const cm = clean.metrics || {};
  const lm = legacy.metrics || {};
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-6">
      <h3 className="text-lg font-semibold mb-4">Clean vs legacy</h3>
      <table className="w-full">
        <thead>
          <tr className="text-xs uppercase tracking-wider text-slate-500">
            <th className="text-left pb-2">Metric</th>
            <th className="text-right pb-2">Clean<br/><span className="font-normal normal-case text-slate-400">{clean.host}</span></th>
            <th className="pb-2"></th>
            <th className="text-right pb-2">Legacy<br/><span className="font-normal normal-case text-slate-400">{legacy.host}</span></th>
          </tr>
        </thead>
        <tbody>
          <MetricRow label="Lighthouse perf (mobile)"  clean={cm.lh_perf_mobile}  legacy={lm.lh_perf_mobile} />
          <MetricRow label="Lighthouse perf (desktop)" clean={cm.lh_perf_desktop} legacy={lm.lh_perf_desktop} />
          <MetricRow label="Lighthouse SEO"            clean={cm.lh_seo}          legacy={lm.lh_seo} />
          <MetricRow label="CrUX LCP p75"  clean={cm.cwv_lcp}  legacy={lm.cwv_lcp}  unit="ms" lowerIsBetter />
          <MetricRow label="CrUX CLS p75"  clean={cm.cwv_cls}  legacy={lm.cwv_cls}  lowerIsBetter />
          <MetricRow label="CrUX INP p75"  clean={cm.cwv_inp}  legacy={lm.cwv_inp}  unit="ms" lowerIsBetter />
          <MetricRow label="JS bundle (mobile)" clean={cm.js_kb_mobile} legacy={lm.js_kb_mobile} unit=" KB" lowerIsBetter />
          <MetricRow label="Composite SEOScore"  clean={cm.seo_score}  legacy={lm.seo_score} />
          <MetricRow label="Composite PerfScore" clean={cm.perf_score} legacy={lm.perf_score} />
        </tbody>
      </table>
    </div>
  );
}

function DomainCard({ domain }) {
  const m = domain.metrics || {};
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5">
      <div className="text-xs uppercase tracking-wider text-slate-500">{domain.role}</div>
      <div className="font-mono text-sm text-slate-900 mt-1">{domain.host}</div>
      <div className="grid grid-cols-2 gap-3 mt-4 text-sm">
        <div><span className="text-slate-500">Perf (m/d):</span> <span className="font-mono">{m.lh_perf_mobile ?? "—"} / {m.lh_perf_desktop ?? "—"}</span></div>
        <div><span className="text-slate-500">SEO:</span> <span className="font-mono">{m.lh_seo ?? "—"}</span></div>
        <div><span className="text-slate-500">LCP p75:</span> <span className="font-mono">{m.cwv_lcp ? `${m.cwv_lcp}ms` : "—"}</span></div>
        <div><span className="text-slate-500">JS (mobile):</span> <span className="font-mono">{m.js_kb_mobile ? `${m.js_kb_mobile} KB` : "—"}</span></div>
      </div>
    </div>
  );
}

function ChartsPanel({ lighthouse, cwv }) {
  // Pivot lighthouse rows into a per-row bar chart
  const lhData = lighthouse.map((r) => ({
    label: `${r.url.split("/").slice(-2).join("/") || r.url} (${r.strategy.slice(0, 3)})`,
    Perf: r.perf, SEO: r.seo, A11y: r.a11y, BP: r.bp,
  }));

  // CWV chart — only rows with field data
  const cwvData = cwv.filter((r) => r.lcp != null || r.cls != null || r.inp != null)
    .map((r) => ({
      label: `${r.url.split("/").slice(-1)[0] || r.url} (${r.strategy.slice(0, 3)})`,
      LCP: r.lcp, "CLS×100": r.cls != null ? Math.round(r.cls * 100) : null, INP: r.inp,
    }));

  return (
    <div className="grid md:grid-cols-2 gap-4">
      <div className="rounded-xl border border-slate-200 bg-white p-5">
        <h3 className="text-sm font-semibold mb-3">Lighthouse scores per URL</h3>
        <ResponsiveContainer width="100%" height={260}>
          <BarChart data={lhData} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis dataKey="label" tick={{ fontSize: 10 }} interval={0} angle={-15} textAnchor="end" height={60} />
            <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} />
            <Tooltip />
            <Legend wrapperStyle={{ fontSize: 12 }} />
            <Bar dataKey="Perf" fill="#a78bfa" />
            <Bar dataKey="SEO" fill="#60a5fa" />
            <Bar dataKey="A11y" fill="#34d399" />
            <Bar dataKey="BP" fill="#fbbf24" />
          </BarChart>
        </ResponsiveContainer>
      </div>
      <div className="rounded-xl border border-slate-200 bg-white p-5">
        <h3 className="text-sm font-semibold mb-3">CrUX field p75 (where available)</h3>
        {cwvData.length === 0 ? (
          <div className="h-[260px] flex items-center justify-center text-sm text-slate-400">
            No CrUX field data — domain too new or below traffic threshold.
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={cwvData} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="label" tick={{ fontSize: 10 }} interval={0} angle={-15} textAnchor="end" height={60} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Legend wrapperStyle={{ fontSize: 12 }} />
              <Bar dataKey="LCP" fill="#f87171" />
              <Bar dataKey="INP" fill="#fb923c" />
              <Bar dataKey="CLS×100" fill="#a3a3a3" />
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
}

function FindingsTable({ findings }) {
  const [sevFilter, setSevFilter] = useState(new Set());
  const [areaFilter, setAreaFilter] = useState(new Set());
  const [labelFilter, setLabelFilter] = useState(new Set());

  const toggle = (set, setter, v) => {
    const next = new Set(set);
    next.has(v) ? next.delete(v) : next.add(v);
    setter(next);
  };

  const filtered = useMemo(() => {
    return findings.filter((f) =>
      (sevFilter.size === 0 || sevFilter.has(f.severity)) &&
      (areaFilter.size === 0 || areaFilter.has(f.area)) &&
      (labelFilter.size === 0 || labelFilter.has(f.label))
    );
  }, [findings, sevFilter, areaFilter, labelFilter]);

  const sevs   = ["P0", "P1", "P2", "P3"];
  const areas  = [...new Set(findings.map((f) => f.area))];
  const labels = [...new Set(findings.map((f) => f.label))];

  const Chip = ({ active, onClick, children, cls }) => (
    <button
      onClick={onClick}
      className={`px-2.5 py-1 rounded-full text-xs font-medium border transition ${
        active ? cls + " ring-2 ring-offset-1 ring-slate-400" : "bg-white text-slate-500 border-slate-200 hover:bg-slate-50"
      }`}
    >
      {children}
    </button>
  );

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-lg font-semibold">Findings ({filtered.length} of {findings.length})</h3>
        <Filter className="w-4 h-4 text-slate-400" />
      </div>

      <div className="space-y-2 mb-4">
        <div className="flex flex-wrap gap-1.5 items-center">
          <span className="text-xs text-slate-500 mr-1 w-16">Severity</span>
          {sevs.map((s) => (
            <Chip key={s} active={sevFilter.has(s)} onClick={() => toggle(sevFilter, setSevFilter, s)} cls={SEV_BG[s]}>
              {s}
            </Chip>
          ))}
        </div>
        <div className="flex flex-wrap gap-1.5 items-center">
          <span className="text-xs text-slate-500 mr-1 w-16">Area</span>
          {areas.map((a) => (
            <Chip key={a} active={areaFilter.has(a)} onClick={() => toggle(areaFilter, setAreaFilter, a)} cls={AREA_BG[a] || "bg-slate-100 text-slate-700"}>
              {a}
            </Chip>
          ))}
        </div>
        <div className="flex flex-wrap gap-1.5 items-center">
          <span className="text-xs text-slate-500 mr-1 w-16">Label</span>
          {labels.map((l) => (
            <Chip key={l} active={labelFilter.has(l)} onClick={() => toggle(labelFilter, setLabelFilter, l)} cls="bg-indigo-50 text-indigo-700 border-indigo-200">
              {l}
            </Chip>
          ))}
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-xs uppercase tracking-wider text-slate-500 border-b border-slate-200">
              <th className="text-left py-2">Sev</th>
              <th className="text-left py-2">Area</th>
              <th className="text-left py-2">URL · Field</th>
              <th className="text-left py-2">Current → Target</th>
              <th className="text-left py-2">Fix</th>
              <th className="text-left py-2">Label</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((f, i) => (
              <tr key={i} className="border-b border-slate-100 align-top">
                <td className="py-2 pr-2"><span className={`px-2 py-0.5 rounded text-xs font-mono border ${SEV_BG[f.severity]}`}>{f.severity}</span></td>
                <td className="py-2 pr-2"><span className={`px-2 py-0.5 rounded text-xs ${AREA_BG[f.area] || "bg-slate-100 text-slate-700"}`}>{f.area}</span></td>
                <td className="py-2 pr-3">
                  <div className="font-mono text-xs text-slate-500">{f.url}</div>
                  <div className="font-medium text-slate-900">{f.field}</div>
                </td>
                <td className="py-2 pr-3 text-xs">
                  <span className="font-mono text-red-600">{String(f.current)}</span>
                  <span className="text-slate-400 mx-1">→</span>
                  <span className="font-mono text-emerald-700">{String(f.target)}</span>
                </td>
                <td className="py-2 pr-3 text-slate-700">{f.fix}</td>
                <td className="py-2"><span className="text-xs text-slate-500">{f.label}</span></td>
              </tr>
            ))}
            {filtered.length === 0 && (
              <tr><td colSpan={6} className="py-6 text-center text-slate-400 text-sm">No findings match these filters.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// ─── main component ─────────────────────────────────────────────────────
export default function AuditDashboard() {
  const { meta, scores, decision, domains, lighthouse, cwv, findings } = DATA;
  const dateLabel = new Date(meta.audit_date).toLocaleDateString(undefined, {
    year: "numeric", month: "short", day: "numeric",
  });

  return (
    <div className="min-h-screen bg-slate-50 p-6 font-sans">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-baseline justify-between flex-wrap gap-2">
          <div>
            <div className="text-xs uppercase tracking-wider text-slate-500">SEO + PageSpeed Audit</div>
            <h1 className="text-3xl font-bold text-slate-900">{meta.product_name}</h1>
          </div>
          <div className="text-sm text-slate-500">
            {dateLabel} · {meta.url_count} URLs · {meta.domain_count} domain{meta.domain_count > 1 ? "s" : ""} · {meta.locales.join(", ")}
          </div>
        </div>

        {/* Decision banner */}
        <DecisionBanner decision={decision} />

        {/* Score cards */}
        <div className="grid sm:grid-cols-2 gap-4">
          <ScoreCard label="SEO Score" value={scores.seo} />
          <ScoreCard label="Perf Score" value={scores.perf} />
        </div>

        {/* Clean vs legacy */}
        <DomainCompare domains={domains} />

        {/* Charts */}
        <ChartsPanel lighthouse={lighthouse} cwv={cwv} />

        {/* Findings */}
        <FindingsTable findings={findings} />

        <div className="text-center text-xs text-slate-400 pt-6">
          Run ID {meta.run_id} · Generated by Sanjow audit pipeline
        </div>
      </div>
    </div>
  );
}
