#!/usr/bin/env python3
"""
Aggregate per-product fix plans into a single portfolio kanban.

Scans `fix-seo-plans/*.json` (written by run_audit.py), merges every ticket
into one board tagged by product, and writes `fix-seo-plans/portfolio.html`.

Usage:
    python scripts/build_portfolio_kanban.py

The portfolio board has its own localStorage key (`fix-plan:portfolio`) so it
does NOT interfere with per-product boards. You can keep the portfolio open
as your team-wide tracker and still use the per-product boards for focused
sprints on one product.
"""
from __future__ import annotations

import html as html_mod
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLAN_DIR = ROOT / "fix-seo-plans"
OVERRIDES_FILE = PLAN_DIR / "status_overrides.json"


def load_status_overrides() -> dict:
    """Read the seed-overrides file. Missing file is treated as no overrides."""
    if not OVERRIDES_FILE.exists():
        return {"schema_version": 1, "overrides": {}, "seeded_note": ""}
    raw = json.loads(OVERRIDES_FILE.read_text())
    return {
        "schema_version": int(raw.get("schema_version", 1)),
        "overrides": dict(raw.get("overrides", {})),
        "seeded_note": str(raw.get("seeded_note", "")),
    }


def load_all_plans() -> list[dict]:
    plans = []
    for f in sorted(PLAN_DIR.glob("*.json")):
        if f.name == OVERRIDES_FILE.name:
            continue
        try:
            data = json.loads(f.read_text())
            if "meta" not in data or "tickets" not in data:
                continue
            plans.append(data)
        except Exception as e:
            print(f"⚠ skip {f.name}: {e}", file=sys.stderr)
    return plans


def merge_tickets(plans: list[dict]) -> list[dict]:
    """Tag every ticket with its product so the board can filter/group."""
    merged = []
    for plan in plans:
        meta = plan["meta"]
        for t in plan["tickets"]:
            tt = dict(t)
            tt["product_id"] = meta["product_id"]
            tt["product_name"] = meta["product_name"]
            tt["product_decision"] = meta["decision"]
            merged.append(tt)
    return merged


def build_summary(plans: list[dict], tickets: list[dict]) -> dict:
    total = len(tickets)
    by_product = {}
    for t in tickets:
        by_product[t["product_id"]] = by_product.get(t["product_id"], 0) + 1
    p0 = sum(1 for t in tickets if t["priority"] == "P0")
    p1 = sum(1 for t in tickets if t["priority"] == "P1")
    p2 = sum(1 for t in tickets if t["priority"] == "P2")
    arch = sum(1 for t in tickets if t["kind"] == "architectural")
    total_lift = sum(t["lift"] for t in tickets)

    return {
        "product_count": len(plans),
        "ticket_count": total,
        "by_product": by_product,
        "by_priority": {"P0": p0, "P1": p1, "P2": p2},
        "arch_count": arch,
        "total_lift": total_lift,
        "products": [
            {
                "id": p["meta"]["product_id"],
                "name": p["meta"]["product_name"],
                "seo_score": p["meta"]["seo_score"],
                "perf_score": p["meta"]["perf_score"],
                "decision": p["meta"]["decision"],
                "ticket_count": by_product.get(p["meta"]["product_id"], 0),
            }
            for p in plans
        ],
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def render(plans: list[dict], tickets: list[dict], summary: dict, overrides: dict) -> str:
    payload = json.dumps(
        {"summary": summary, "tickets": tickets, "products": summary["products"]},
        indent=2,
    )
    overrides_json = json.dumps(overrides["overrides"], indent=2)
    seeded_note = overrides["seeded_note"].replace("*/", "*\\/")
    return (
        _TEMPLATE
        .replace("__PAYLOAD__", payload)
        .replace("__SCHEMA_VERSION__", str(overrides["schema_version"]))
        .replace("__INITIAL_STATE_OVERRIDES__", overrides_json)
        .replace("__SEEDED_NOTE__", seeded_note)
    )


_TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<title>Sanjow Portfolio — SEO Fix Plan (Kanban)</title>
<meta name="viewport" content="width=device-width, initial-scale=1" />
<script src="https://cdn.tailwindcss.com"></script>
<style>
  body { font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; }
  .col { min-height: 60vh; }
  .card { transition: transform .08s ease, box-shadow .08s ease; cursor: grab; }
  .card:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(0,0,0,.08); }
  .card.dragging { opacity: .5; cursor: grabbing; }
  details > summary { cursor: pointer; list-style: none; }
  details > summary::-webkit-details-marker { display: none; }
  [data-over="true"] { background: #fef3c7; }
</style>
</head>
<body class="bg-slate-50 text-slate-900">
<div class="max-w-[1400px] mx-auto p-6">

  <header class="flex flex-col md:flex-row md:items-end md:justify-between gap-3 mb-6">
    <div>
      <h1 class="text-2xl font-bold">Sanjow Portfolio — SEO Fix Plan</h1>
      <p id="meta-line" class="text-sm text-slate-600"></p>
    </div>
    <div class="flex items-center gap-3">
      <span id="progress-label" class="text-sm text-slate-600"></span>
      <button id="reset-btn" class="text-xs text-slate-500 hover:text-red-600 underline">
        Reset board state
      </button>
    </div>
  </header>

  <!-- Product summary strip -->
  <section id="product-strip" class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-5"></section>

  <!-- Progress bar -->
  <section class="bg-white rounded-lg border border-slate-200 p-4 mb-5">
    <div class="w-full bg-slate-200 rounded h-2 overflow-hidden">
      <div id="progress-bar" class="bg-emerald-500 h-2 transition-all" style="width:0%"></div>
    </div>
  </section>

  <!-- Filters -->
  <section class="bg-white rounded-lg border border-slate-200 p-4 mb-5 flex flex-wrap gap-4 items-start">
    <div>
      <label class="block text-xs font-semibold text-slate-500 mb-1">Search</label>
      <input id="search" type="search" placeholder="id, field, title…"
             class="border border-slate-300 rounded px-2 py-1 text-sm w-64" />
    </div>
    <div id="filter-product"  class="flex flex-col gap-1">
      <span class="text-xs font-semibold text-slate-500">Product</span>
      <div class="flex gap-1 flex-wrap"></div>
    </div>
    <div id="filter-priority" class="flex flex-col gap-1">
      <span class="text-xs font-semibold text-slate-500">Priority</span>
      <div class="flex gap-1 flex-wrap"></div>
    </div>
    <div id="filter-owner" class="flex flex-col gap-1">
      <span class="text-xs font-semibold text-slate-500">Owner</span>
      <div class="flex gap-1 flex-wrap"></div>
    </div>
    <div id="filter-label" class="flex flex-col gap-1">
      <span class="text-xs font-semibold text-slate-500">Type</span>
      <div class="flex gap-1 flex-wrap"></div>
    </div>
    <div id="filter-area" class="flex flex-col gap-1">
      <span class="text-xs font-semibold text-slate-500">Area</span>
      <div class="flex gap-1 flex-wrap"></div>
    </div>
  </section>

  <!-- Kanban columns -->
  <section class="grid grid-cols-1 md:grid-cols-3 gap-4">
    <div class="col bg-white rounded-lg border-2 border-slate-200 p-3" data-col="todo">
      <header class="flex items-center justify-between mb-2">
        <h2 class="font-semibold text-slate-800">📋 To-do</h2>
        <span class="text-xs text-slate-500 count"></span>
      </header>
      <div class="space-y-2 cards"></div>
    </div>
    <div class="col bg-white rounded-lg border-2 border-amber-200 p-3" data-col="in_progress">
      <header class="flex items-center justify-between mb-2">
        <h2 class="font-semibold text-amber-800">🔨 In progress</h2>
        <span class="text-xs text-slate-500 count"></span>
      </header>
      <div class="space-y-2 cards"></div>
    </div>
    <div class="col bg-white rounded-lg border-2 border-emerald-200 p-3" data-col="done">
      <header class="flex items-center justify-between mb-2">
        <h2 class="font-semibold text-emerald-800">✅ Done</h2>
        <span class="text-xs text-slate-500 count"></span>
      </header>
      <div class="space-y-2 cards"></div>
    </div>
  </section>

  <footer class="mt-8 text-xs text-slate-500">
    Portfolio board state persists in localStorage under <code>fix-plan:portfolio</code>.
    Ticket IDs are stable across audit re-runs, so statuses survive regeneration.
    Rebuild this board anytime with <code>python scripts/build_portfolio_kanban.py</code>.
  </footer>
</div>

<script>
const DATA = __PAYLOAD__;
const STORAGE_KEY = "fix-plan:portfolio";
const VERSION_KEY = STORAGE_KEY + ":version";

// Schema version — bump whenever INITIAL_STATE_OVERRIDES changes.
// Version bump only affects tickets still at "todo"; manual progress is preserved.
const SCHEMA_VERSION = __SCHEMA_VERSION__;

// Seed overrides — sourced from fix-seo-plans/status_overrides.json.
// __SEEDED_NOTE__
const INITIAL_STATE_OVERRIDES = __INITIAL_STATE_OVERRIDES__;

// ─── state ────────────────────────────────────────────────────────
let state = loadState();
const filters = {
  product: new Set(), priority: new Set(), owner: new Set(),
  label: new Set(), area: new Set(), q: "",
};

function loadState() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    const parsed = raw ? JSON.parse(raw) : {};
    const storedVersion = parseInt(localStorage.getItem(VERSION_KEY) || "0", 10);

    // One-time migration per schema bump — only rewrites tickets still at "todo"
    // so any manual drag-and-drop progress is preserved.
    if (storedVersion < SCHEMA_VERSION) {
      Object.entries(INITIAL_STATE_OVERRIDES).forEach(([id, newStatus]) => {
        if (!(id in parsed) || parsed[id] === "todo") parsed[id] = newStatus;
      });
      localStorage.setItem(VERSION_KEY, String(SCHEMA_VERSION));
      localStorage.setItem(STORAGE_KEY, JSON.stringify(parsed));
    }

    DATA.tickets.forEach(t => { if (!(t.id in parsed)) parsed[t.id] = "todo"; });
    return parsed;
  } catch (e) {
    return Object.fromEntries(DATA.tickets.map(t => [t.id, "todo"]));
  }
}
function saveState() { localStorage.setItem(STORAGE_KEY, JSON.stringify(state)); }

// ─── product strip ───────────────────────────────────────────────
function renderProductStrip() {
  const strip = document.getElementById("product-strip");
  strip.innerHTML = DATA.products.map(p => {
    const productTickets = DATA.tickets.filter(t => t.product_id === p.id);
    const done = productTickets.filter(t => state[t.id] === "done").length;
    const pct = productTickets.length ? Math.round((done / productTickets.length) * 100) : 0;
    const decisionColour = ({"A": "bg-emerald-100 text-emerald-800",
                             "B": "bg-amber-100 text-amber-800",
                             "C": "bg-red-100 text-red-800"})[p.decision] || "bg-slate-100";
    return `
      <div class="bg-white border border-slate-200 rounded-lg p-3">
        <div class="flex items-center justify-between mb-1">
          <div class="font-semibold text-sm text-slate-900">${p.name}</div>
          <span class="text-[10px] px-1.5 py-0.5 rounded ${decisionColour}">Opt ${p.decision}</span>
        </div>
        <div class="text-[11px] text-slate-500 mb-2">
          SEO ${p.seo_score} · Perf ${p.perf_score}
        </div>
        <div class="w-full bg-slate-200 rounded h-1.5 overflow-hidden">
          <div class="bg-emerald-500 h-1.5" style="width:${pct}%"></div>
        </div>
        <div class="text-[10px] text-slate-500 mt-1">${done} / ${productTickets.length} complete</div>
      </div>`;
  }).join("");
}

// ─── filters ─────────────────────────────────────────────────────
function buildFilters() {
  const groups = {
    product:  DATA.products.map(p => p.id),
    priority: ["P0", "P1", "P2"],
    owner:    [...new Set(DATA.tickets.map(t => t.owner))].sort(),
    label:    [...new Set(DATA.tickets.map(t => t.label))].sort(),
    area:     [...new Set(DATA.tickets.map(t => t.area))].sort(),
  };
  Object.entries(groups).forEach(([key, vals]) => {
    const el = document.querySelector(`#filter-${key} > div`);
    el.innerHTML = "";
    vals.forEach(v => {
      const btn = document.createElement("button");
      btn.textContent = v;
      btn.className = "px-2 py-0.5 text-xs rounded-full border border-slate-300 " +
                      "bg-white text-slate-700 hover:bg-slate-100";
      btn.onclick = () => {
        if (filters[key].has(v)) filters[key].delete(v); else filters[key].add(v);
        btn.classList.toggle("bg-blue-600");
        btn.classList.toggle("text-white");
        btn.classList.toggle("border-blue-600");
        render();
      };
      el.appendChild(btn);
    });
  });
}

// ─── render ──────────────────────────────────────────────────────
function matches(t) {
  const q = filters.q.toLowerCase();
  if (q && !`${t.id} ${t.title} ${t.field} ${t.area} ${t.product_name}`.toLowerCase().includes(q)) return false;
  if (filters.product.size  && !filters.product.has(t.product_id)) return false;
  if (filters.priority.size && !filters.priority.has(t.priority))  return false;
  if (filters.owner.size    && !filters.owner.has(t.owner))        return false;
  if (filters.label.size    && !filters.label.has(t.label))        return false;
  if (filters.area.size     && !filters.area.has(t.area))          return false;
  return true;
}

function priorityClasses(p) {
  return ({
    P0: "bg-red-100 text-red-800 border-red-300",
    P1: "bg-amber-100 text-amber-800 border-amber-300",
    P2: "bg-slate-100 text-slate-700 border-slate-300",
  })[p] || "bg-slate-100";
}

function productColour(pid) {
  // Stable pastel per product based on character codes
  let h = 0; for (const c of pid) h = (h * 31 + c.charCodeAt(0)) >>> 0;
  const hue = h % 360;
  return `hsl(${hue} 70% 92%)`;
}

function cardHtml(t) {
  const urls = t.affected_urls
    .map(u => `<li class="font-mono text-[11px] text-slate-600">${u.replace(/^https?:\/\//, "")}</li>`)
    .join("");
  const accept = t.acceptance
    .map(a => `<li class="text-xs"><input type="checkbox" class="mr-1" /> ${a}</li>`)
    .join("");
  return `
    <details class="card bg-white rounded border border-slate-200 p-3" draggable="true" data-id="${t.id}">
      <summary>
        <div class="flex items-start justify-between gap-2">
          <div class="min-w-0 w-full">
            <div class="flex items-center gap-1 flex-wrap mb-1">
              <span class="text-[10px] px-1.5 py-0.5 rounded font-semibold"
                    style="background:${productColour(t.product_id)}">${t.product_name}</span>
              <span class="font-mono text-[10px] text-slate-500">${t.id}</span>
              <span class="text-[10px] px-1.5 py-0.5 rounded border ${priorityClasses(t.priority)}">${t.priority}</span>
              <span class="text-[10px] px-1.5 py-0.5 rounded bg-slate-100 text-slate-600">${t.area}</span>
              ${t.kind === "architectural"
                ? '<span class="text-[10px] px-1.5 py-0.5 rounded bg-purple-100 text-purple-700">arch</span>'
                : ""}
            </div>
            <div class="text-sm font-medium text-slate-800 leading-snug">${t.title}</div>
            <div class="text-[11px] text-slate-500 mt-1">
              ${t.owner} · ${t.effort} · +${t.lift} lift
            </div>
          </div>
        </div>
      </summary>
      <div class="mt-3 pt-3 border-t border-slate-100 space-y-2">
        <div>
          <div class="text-[11px] font-semibold text-slate-500 uppercase tracking-wide mb-0.5">Problem</div>
          <div class="text-xs text-slate-700">${t.problem}</div>
        </div>
        <div>
          <div class="text-[11px] font-semibold text-slate-500 uppercase tracking-wide mb-0.5">Fix</div>
          <div class="text-xs text-slate-700">${t.fix}</div>
        </div>
        <div>
          <div class="text-[11px] font-semibold text-slate-500 uppercase tracking-wide mb-0.5">Affected URLs</div>
          <ul class="ml-4 list-disc">${urls}</ul>
        </div>
        <div>
          <div class="text-[11px] font-semibold text-slate-500 uppercase tracking-wide mb-0.5">Acceptance</div>
          <ul class="ml-4 list-none space-y-0.5 text-slate-700">${accept}</ul>
        </div>
      </div>
    </details>`;
}

function render() {
  document.querySelectorAll(".col .cards").forEach(el => el.innerHTML = "");
  const counts = { todo: 0, in_progress: 0, done: 0 };
  DATA.tickets.forEach(t => {
    if (!matches(t)) return;
    const status = state[t.id] || "todo";
    counts[status]++;
    const col = document.querySelector(`.col[data-col="${status}"] .cards`);
    col.insertAdjacentHTML("beforeend", cardHtml(t));
  });
  document.querySelectorAll(".col").forEach(col => {
    const s = col.dataset.col;
    col.querySelector(".count").textContent = `${counts[s]} ticket${counts[s] === 1 ? "" : "s"}`;
  });

  const total = DATA.tickets.length;
  const done = DATA.tickets.filter(t => state[t.id] === "done").length;
  const pct = total ? Math.round((done / total) * 100) : 0;
  document.getElementById("progress-bar").style.width = pct + "%";
  document.getElementById("progress-label").textContent =
    `${done} / ${total} complete (${pct}%)`;

  renderProductStrip();
  wireDragDrop();
}

// ─── drag & drop ────────────────────────────────────────────────
function wireDragDrop() {
  document.querySelectorAll(".card").forEach(card => {
    card.addEventListener("dragstart", e => {
      card.classList.add("dragging");
      e.dataTransfer.setData("text/plain", card.dataset.id);
    });
    card.addEventListener("dragend", () => card.classList.remove("dragging"));
  });
  document.querySelectorAll(".col").forEach(col => {
    col.addEventListener("dragover", e => { e.preventDefault(); col.dataset.over = "true"; });
    col.addEventListener("dragleave", () => { col.dataset.over = "false"; });
    col.addEventListener("drop", e => {
      e.preventDefault();
      col.dataset.over = "false";
      const id = e.dataTransfer.getData("text/plain");
      state[id] = col.dataset.col;
      saveState();
      render();
    });
  });
}

// ─── init ────────────────────────────────────────────────────────
document.getElementById("meta-line").innerHTML =
  `${DATA.summary.product_count} product(s) · ${DATA.summary.ticket_count} tickets ` +
  `(P0=${DATA.summary.by_priority.P0}, P1=${DATA.summary.by_priority.P1}, P2=${DATA.summary.by_priority.P2}) · ` +
  `Est. lift +${DATA.summary.total_lift} · Generated ${DATA.summary.generated_at}`;

document.getElementById("search").addEventListener("input", e => {
  filters.q = e.target.value;
  render();
});
document.getElementById("reset-btn").addEventListener("click", () => {
  if (confirm("Reset all tickets across all products to To-do?")) {
    state = Object.fromEntries(DATA.tickets.map(t => [t.id, "todo"]));
    saveState();
    render();
  }
});

buildFilters();
render();
</script>
</body>
</html>
"""


def main():
    plans = load_all_plans()
    if not plans:
        print("✗ No fix-plan .json files found in fix-seo-plans/. "
              "Run the audit first: python scripts/run_audit.py --all",
              file=sys.stderr)
        sys.exit(2)

    tickets = merge_tickets(plans)
    summary = build_summary(plans, tickets)
    overrides = load_status_overrides()
    html = render(plans, tickets, summary, overrides)

    out = PLAN_DIR / "portfolio.html"
    out.write_text(html)
    print(f"✓ wrote {out.relative_to(ROOT)} — "
          f"{summary['product_count']} product(s), "
          f"{summary['ticket_count']} tickets "
          f"(P0={summary['by_priority']['P0']}, "
          f"P1={summary['by_priority']['P1']}, "
          f"P2={summary['by_priority']['P2']})")


if __name__ == "__main__":
    main()
