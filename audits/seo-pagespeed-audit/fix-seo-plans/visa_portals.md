# Global Visa Portal — SEO + PageSpeed Fix Plan

_Generated 2026-04-21T08:59:55+00:00 · [audit report](../products/visa_portals.md) · [dashboard](../products/visa_portals.jsx)_

## Sprint summary

- **Total tickets:** 5 (5 in-place, 0 architectural)
- **By priority:** P0=0, P1=3, P2=2
- **By owner:** Frontend=5
- **Estimated total lift:** +21 score points (current: SEO 51.8, Perf 49.2)
- **Audit decision:** Option **A/B (needs human judgement)**

## In-place fixes

### P1 — Should-fix

#### `VISA_PORTALS-FIX-001` — sitemap.xml — Generate a sitemap (Next.js app router supports `sitemap.ts`).

**Priority:** P1 · **Owner:** Frontend · **Effort:** 1h · **Est. lift:** +4 · **Area:** SEO · **Type:** fixable-in-place

**Problem**

Current: `missing`. Target: `valid XML sitemap at /sitemap.xml`.

**Fix**

Generate a sitemap (Next.js app router supports `sitemap.ts`).

**Affected**

  - `global-visa-portal.vercel.app`
  - `online-visas.com`

**Acceptance criteria**

- [ ] `/sitemap.xml` returns 200 with valid XML
- [ ] Sitemap lists every locale route
- [ ] Sitemap referenced from `/robots.txt`

---

#### `VISA_PORTALS-FIX-002` — canonical link — Emit a self-referential `<link rel='canonical'>` via metadata.

**Priority:** P1 · **Owner:** Frontend · **Effort:** 30m · **Est. lift:** +3 · **Area:** SEO · **Type:** fixable-in-place

**Problem**

Current: `missing`. Target: `self-referential canonical`.

**Fix**

Emit a self-referential `<link rel='canonical'>` via metadata.

**Affected**

  - `global-visa-portal.vercel.app/`
  - `global-visa-portal.vercel.app/fr/`
  - `online-visas.com/`
  - `online-visas.com/fr/`

**Acceptance criteria**

- [ ] Every indexable page emits a self-referential `<link rel="canonical">`
- [ ] Canonical URL uses the clean-domain host and correct locale

---

#### `VISA_PORTALS-FIX-003` — hreflang coverage — Emit hreflang for every locale route + x-default.

**Priority:** P1 · **Owner:** Frontend · **Effort:** 3h · **Est. lift:** +8 · **Area:** SEO · **Type:** fixable-in-place

**Problem**

Current: `0 of 8 locales`. Target: `8 hreflang tags + x-default`.

**Fix**

Emit hreflang for every locale route + x-default.

**Affected**

  - `global-visa-portal.vercel.app/`
  - `global-visa-portal.vercel.app/fr/`
  - `online-visas.com/`
  - `online-visas.com/fr/`

**Acceptance criteria**

- [ ] All configured locales emit `<link rel="alternate" hreflang=...>`
- [ ] `x-default` hreflang is present
- [ ] Each hreflang URL returns 200 (no redirects)

---

### P2 — Nice-to-have

#### `VISA_PORTALS-FIX-004` — h1 count — Ensure exactly one h1 per route; demote duplicates to h2.

**Priority:** P2 · **Owner:** Frontend · **Effort:** 1h · **Est. lift:** +2 · **Area:** SEO · **Type:** fixable-in-place

**Problem**

Current: `0 h1 tags`. Target: `exactly 1 h1 per page`.

**Fix**

Ensure exactly one h1 per route; demote duplicates to h2.

**Affected**

  - `global-visa-portal.vercel.app/`
  - `global-visa-portal.vercel.app/fr/`
  - `online-visas.com/`
  - `online-visas.com/fr/`

**Acceptance criteria**

- [ ] Exactly one `<h1>` per page
- [ ] h1 text reflects the page's primary entity

---

#### `VISA_PORTALS-FIX-005` — JSON-LD — Inject JSON-LD for the page's primary entity type.

**Priority:** P2 · **Owner:** Frontend · **Effort:** 2h · **Est. lift:** +4 · **Area:** SEO · **Type:** fixable-in-place

**Problem**

Current: `none`. Target: `relevant schema.org types (Organization, WebSite, Product, FAQ)`.

**Fix**

Inject JSON-LD for the page's primary entity type.

**Affected**

  - `global-visa-portal.vercel.app/`
  - `global-visa-portal.vercel.app/fr/`
  - `online-visas.com/`
  - `online-visas.com/fr/`

**Acceptance criteria**

- [ ] Relevant schema.org type(s) emitted as application/ld+json
- [ ] Google Rich Results Test passes

---

## How to use this plan

1. Copy each ticket into Linear / GitHub Issues — IDs stay stable across audit re-runs so you can cross-reference.
2. Track status on the kanban board: `fix-seo-plans/visa_portals.html` (open in a browser — status persists in localStorage).
3. Re-run `python scripts/run_audit.py --product visa_portals` after shipping — the plan regenerates but IDs remain deterministic so tickets you've already filed can be updated in-place.
