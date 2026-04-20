# Sanjow Design System → Figma

Sync the `@sanjow/design-system` package to Figma without rate-limiting via the Figma MCP.

**Figma File:** https://www.figma.com/design/LfD1cuTJk0io9tewfzEHFZ

---

## Option A: Run build.js in Figma (Recommended, 30 seconds)

This is the fastest way to get a fully populated Figma file with all pages, variables, components, and brand modes.

### Steps

1. **Open the Figma file:**  
   https://www.figma.com/design/LfD1cuTJk0io9tewfzEHFZ

2. **Open the Figma plugin console:**
   - In Figma desktop app: **Plugins → Development → Import plugin from manifest...**
   - Or use the community plugin: **"Figma Plugin API Console"** (easier one-click)

3. **Paste the contents of `build.js` into the console.**

4. **Run it.** Takes ~15–20 seconds. The script creates:
   - ✓ 5 Pages: Cover, Foundations, Themes, Components, Changelog
   - ✓ 3 Variable Collections: Primitives (25 colors), Theme (5 modes), Scale (15 floats)
   - ✓ 4 Component Sets: Button (42 variants), Input, Card, Badge (8 variants)
   - ✓ All brand colors, typography specimens, spacing scales, radius demos, shadows

5. **Re-running is safe.** The script is fully idempotent — running it twice will not create duplicates.

---

## Option B: Import via Token Studio (Manual, 2–3 minutes)

For teams already using Token Studio, you can import `tokens.json` directly.

### Steps

1. **Install Token Studio:**
   - In Figma, search for and install the free "Tokens Studio for Figma" plugin.

2. **Load the tokens file:**
   - Open Token Studio plugin
   - **Settings → Load from file → Select `tokens.json` from this folder**

3. **Create Figma variables:**
   - In Token Studio, click **"Create Variables"**
   - This generates 3 variable collections: Primitives, wepdf, trip-sorted, checkin, topup, admin
   - Note: You'll get 5 separate token sets (one per brand) rather than a single collection with 5 modes

4. **(Optional) Set up themes:**
   - Token Studio has a "Themes" feature that maps brand token sets to Figma variable modes
   - You can manually create a "Brand" theme with 5 modes: wepdf, trip-sorted, checkin, topup, admin
   - Each mode points to the corresponding token set

**Limitation:** Token Studio creates token sets, not Figma mode collections. If you need synchronized Figma modes for brand switching, use **Option A** instead.

---

## What Gets Created

### Pages
- **🌅 Cover** — Title, version, date, 5 brand tiles with color swatches
- **🎨 Foundations** — Grayscale & status color swatches, typography specimens (7 styles), spacing scale (15 items), radius demos (6 sizes), elevation shadows (5 levels)
- **🌈 Themes** — 5 columns (one per brand), each showing: brand name, tagline, repos, 5 color swatches, button preview, card preview
- **🧩 Components** — 4 component sets:
  - **Button:** 7 variants (primary, secondary, accent, outline, ghost, destructive, link) × 3 sizes (sm, md, lg) × 2 fullWidth options = **42 components**
  - **Input:** 1 component with invalid state variant
  - **Card:** 1 component with header + title + description + content
  - **Badge:** 8 variants (default, secondary, accent, outline, success, warning, danger, info)
- **📝 Changelog** — v0.1.0 release notes

### Variable Collections
- **🎯 Primitives** (25 color variables)
  - Grayscale: 12 shades (#FFF to #0B0B0E)
  - Status: success, warning, danger, info + foregrounds
  - Chrome: ink, surface, elevated, text, text-dim

- **🌈 Theme** (20 color + 1 float variables, 5 modes)
  - Colors: background, foreground, card, popover, primary, secondary, accent, muted, destructive, border, input, ring (× foreground variants)
  - Modes: wepdf, trip-sorted, checkin, topup, admin
  - Each mode uses HSL values from `src/themes/*.ts`
  - Float: `radius/base` (12, 14, 10, 16, 8 px respectively)

- **📐 Scale** (15 float variables)
  - Spacing: space/0–32 (0px to 128px)
  - Radius: radius/sm–2xl + pill (4px to 9999px)

---

## Syncing Back from Code

When you update a token value in `src/themes/*.ts` or `src/tokens/*.ts`:

1. **Update `tokens.json` manually** (paste new HSL values from your themes)
2. **Re-run Option A** (fastest), or
3. **Reload `tokens.json` in Token Studio** and re-sync

For a more automated workflow, consider writing a small script (`sync-tokens.js`) that:
- Reads TypeScript theme files
- Generates `tokens.json` 
- Triggers the Figma API via a small plugin

---

## Troubleshooting

### "Inter font not loaded"
If you see a warning about Inter fonts, make sure Inter is installed on your system and available in Figma. The script falls back gracefully, but components may render with system fonts.

### "Variable already exists"
The script checks for and deletes existing collections before recreating them. If you get a collision, make sure no other scripts are running.

### "Component set creation failed"
Component sets require Figma API v2.0+. Ensure your Figma app is up to date.

---

## File Inventory

| File | Purpose |
|------|---------|
| `build.js` | Figma Plugin API script (ES2020, async IIFE, ~1,100 lines) |
| `tokens.json` | W3C DTCG format tokens, compatible with Token Studio |
| `README.md` | This file |

---

## Contact

Questions or feedback? Refer to the Sanjow design system repo:  
`/design-system/src/themes/` for brand definitions  
`/design-system/src/tokens/` for token specs
