"""
Render a self-contained React JSX dashboard for one product audit.

The output is a single .jsx file that can be opened as a Claude artifact (no
build step, no external state). All audit data is JSON-embedded into the file
so it stays portable.

Widgets (per user spec):
  1. Decision banner (Option A/B/C, coloured)
  2. Headline score cards (SEO + Perf)
  3. Clean vs Legacy side-by-side cards
  4. CWV + Lighthouse charts (recharts)
  5. Findings table with severity/area/label filters
"""
from __future__ import annotations

import json
from datetime import datetime, timezone


# ─── public entry point ────────────────────────────────────────────────────
def render_dashboard(
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
    audit_date: str | None = None,
    run_id: str | None = None,
) -> str:
    audit_date = audit_date or datetime.now(timezone.utc).isoformat(timespec="seconds")
    run_id = run_id or audit_date.replace(":", "").replace("-", "")

    data = _build_data_payload(
        product_id=product_id, product_name=product_name,
        domains=domains, locales_audited=locales_audited,
        url_rows=url_rows, seo_score=seo_score, perf_score=perf_score,
        seo_breakdown=seo_breakdown, perf_breakdown=perf_breakdown,
        findings_by_severity=findings_by_severity, strategic=strategic,
        audit_date=audit_date, run_id=run_id,
    )

    payload_json = json.dumps(data, default=_json_default, indent=2)
    return _JSX_TEMPLATE.replace("__DATA_PAYLOAD__", payload_json)


# ─── data shaping ──────────────────────────────────────────────────────────
def _build_data_payload(**kw) -> dict:
    url_rows = kw["url_rows"]
    domains = kw["domains"]
    findings_by_severity = kw["findings_by_severity"]
    all_findings = [f for bucket in findings_by_severity.values() for f in bucket]

    return {
        "meta": {
            "product_id": kw["product_id"],
            "product_name": kw["product_name"],
            "audit_date": kw["audit_date"],
            "run_id": kw["run_id"],
            "locales": kw["locales_audited"],
            "url_count": len(url_rows),
            "domain_count": len(domains),
        },
        "scores": {
            "seo": kw["seo_score"],
            "perf": kw["perf_score"],
            "seo_breakdown": kw["seo_breakdown"],
            "perf_breakdown": kw["perf_breakdown"],
        },
        "decision": {
            "option": kw["strategic"]["supports"],
            "rules": kw["strategic"].get("triggered_rules", []),
            "rationale": _decision_rationale(kw["strategic"]),
        },
        "domains": [
            {
                "url": d["url"],
                "host": d["url"].replace("https://", "").replace("http://", ""),
                "role": d.get("role", "unknown"),
                "metrics": _domain_metrics(url_rows, d["url"]),
            }
            for d in domains
        ],
        "lighthouse": [
            {
                "url": _short(r["url"]),
                "strategy": r["strategy"],
                "perf": _pct(r.get("lh_scores", {}).get("performance")),
                "seo": _pct(r.get("lh_scores", {}).get("seo")),
                "a11y": _pct(r.get("lh_scores", {}).get("accessibility")),
                "bp": _pct(r.get("lh_scores", {}).get("best-practices")),
            }
            for r in url_rows
        ],
        "cwv": [
            {
                "url": _short(r["url"]),
                "strategy": r["strategy"],
                "lcp": (r.get("field_cwv") or {}).get("lcp_p75_ms"),
                "cls": (r.get("field_cwv") or {}).get("cls_p75"),
                "inp": (r.get("field_cwv") or {}).get("inp_p75_ms"),
                "ttfb": (r.get("field_cwv") or {}).get("ttfb_p75_ms"),
                "verdict": _verdict_cwv(
                    (r.get("field_cwv") or {}).get("lcp_p75_ms"),
                    (r.get("field_cwv") or {}).get("cls_p75"),
                    (r.get("field_cwv") or {}).get("inp_p75_ms"),
                ),
            }
            for r in url_rows
        ],
        "findings": [
            {
                "severity": f["severity"],
                "area": f["area"],
                "label": f["label"],
                "url": _short(f["url"]),
                "field": f["field"],
                "current": f["current"],
                "target": f["target"],
                "fix": f["fix"],
                "rationale": f["rationale"],
            }
            for f in all_findings
        ],
    }


def _domain_metrics(url_rows, domain_url):
    rows = [r for r in url_rows if r["url"].startswith(domain_url)]
    if not rows:
        return None

    def avg(vals):
        vals = [v for v in vals if v is not None]
        return round(sum(vals) / len(vals), 1) if vals else None

    mobile = [r for r in rows if r["strategy"] == "mobile"]
    desktop = [r for r in rows if r["strategy"] == "desktop"]

    return {
        "lh_perf_mobile":  avg([(r.get("lh_scores") or {}).get("performance") for r in mobile]) and
                            int(round(avg([(r.get("lh_scores") or {}).get("performance") for r in mobile]) * 100)),
        "lh_perf_desktop": avg([(r.get("lh_scores") or {}).get("performance") for r in desktop]) and
                            int(round(avg([(r.get("lh_scores") or {}).get("performance") for r in desktop]) * 100)),
        "lh_seo":          avg([(r.get("lh_scores") or {}).get("seo") for r in rows]) and
                            int(round(avg([(r.get("lh_scores") or {}).get("seo") for r in rows]) * 100)),
        "cwv_lcp":         avg([(r.get("field_cwv") or {}).get("lcp_p75_ms") for r in rows]),
        "cwv_cls":         avg([(r.get("field_cwv") or {}).get("cls_p75") for r in rows]),
        "cwv_inp":         avg([(r.get("field_cwv") or {}).get("inp_p75_ms") for r in rows]),
        "js_kb_mobile":    avg([(r.get("bundle_info") or {}).get("js_transferred_kb") for r in mobile]),
        "seo_score":       avg([r.get("seo_score") for r in rows]),
        "perf_score":      avg([r.get("perf_score") for r in rows]),
    }


def _decision_rationale(strategic: dict) -> str:
    opt = strategic["supports"]
    return {
        "A": "Findings are predominantly fixable in-place — invest in the current site.",
        "B": "Architectural drag and/or perf floor low enough that a clean-domain rebuild beats incremental fixes.",
        "C": "Cost of remediation outweighs likely traffic recovery — consider sunset.",
    }.get(opt, "See triggered thumb-rules.")


# ─── helpers ───────────────────────────────────────────────────────────────
def _short(url: str) -> str:
    return url.replace("https://", "").replace("http://", "")


def _pct(v):
    return int(round(v * 100)) if v is not None else None


def _verdict_cwv(lcp, cls, inp):
    if lcp is None and cls is None and inp is None:
        return "no-data"
    poor = ni = False
    if lcp is not None:
        if lcp > 4000: poor = True
        elif lcp > 2500: ni = True
    if cls is not None:
        if cls > 0.25: poor = True
        elif cls > 0.1: ni = True
    if inp is not None:
        if inp > 500: poor = True
        elif inp > 200: ni = True
    return "poor" if poor else "ni" if ni else "good"


def _json_default(o):
    if hasattr(o, "isoformat"):
        return o.isoformat()
    return str(o)


# ─── JSX template ──────────────────────────────────────────────────────────
# Placeholder __DATA_PAYLOAD__ is replaced with the JSON blob.
# The component is fully self-contained: useState for filters, recharts for
# charts, lucide-react for icons, Tailwind core utilities for styling.
_JSX_TEMPLATE = r"""import { useState, useMemo } from "react";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  Legend, CartesianGrid,
} from "recharts";
import {
  AlertTriangle, CheckCircle2, AlertCircle, Info, Filter,
  ArrowUp, ArrowDown, Minus,
} from "lucide-react";

const DATA = __DATA_PAYLOAD__;

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
"""
