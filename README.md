# @sanjow/design-system

Shared design tokens, brand themes, Tailwind preset, and base components for Sanjow ventures. One package, one look per brand, picked up by every consumer via CSS variables.

## What's in the box

- `tokens/` — foundational scales (colors, typography, spacing, radii, shadows, motion). Brand-agnostic.
- `themes/` — five brand themes: `wepdf`, `trip-sorted`, `checkin`, `topup`, `admin`. Each emits a set of CSS variables; swap between them with `data-theme="…"` on `<html>`.
- `tailwind/preset.ts` — drop-in Tailwind v3 preset. Wires `bg-primary`, `text-accent`, etc. to the theme variables.
- `tailwind/theme.css` — the `:root` + `[data-theme]` blocks, plus an optional `@theme` block for Tailwind v4.
- `components/` — `Button`, `Input`, `Card`, `Badge`. Minimal, themeable, built on `class-variance-authority` + `tailwind-merge`.
- `utils/cn.ts` — the standard `cn()` helper.

## Install

The package is consumed as a local workspace today. From a sibling repo:

```bash
# Option A — npm file: dependency
npm install file:../design-system

# Option B — pnpm/yarn workspace
# Add "@sanjow/design-system": "workspace:*" to package.json
```

## Usage — Tailwind v3 repos (pdf-ai, fast-track-ai)

1. Add the preset to `tailwind.config.ts`:

   ```ts
   import preset from "@sanjow/design-system/tailwind-preset";

   export default {
     presets: [preset],
     content: [
       "./src/**/*.{ts,tsx}",
       "../design-system/src/components/**/*.{ts,tsx}",
     ],
   } satisfies Config;
   ```

2. Import the theme CSS once in your root layout / `globals.css`:

   ```css
   @import "@sanjow/design-system/theme.css";
   ```

3. Set the theme on `<html>` in your root layout:

   ```tsx
   <html lang="en" data-theme="wepdf">…</html>
   ```

4. Use the components:

   ```tsx
   import { Button, Card, CardHeader, CardTitle } from "@sanjow/design-system/components";
   ```

## Usage — Tailwind v4 repos (checkin-ai)

Tailwind v4 reads its config from CSS. Skip the JS preset and import the CSS directly in `app/globals.css`:

```css
@import "tailwindcss";
@import "@sanjow/design-system/theme.css";
```

Then set `data-theme="checkin"` on `<html>` as above. The `@theme` block inside `theme.css` registers `bg-primary`, `text-accent`, etc. with Tailwind v4.

## Usage — legacy repos (back-office)

Back-office runs React 16 + Polaris and does not use Tailwind. Consume the tokens as CSS variables only:

```tsx
import "@sanjow/design-system/theme.css";
// then <html data-theme="admin">
```

Then read values in styled-components / inline styles via `var(--primary)`, `var(--foreground)`, etc. The base components require React 18+ and Tailwind, so skip them until the repo is upgraded.

## Theme keys → repo mapping

| Theme | Primary repos |
|-------|---------------|
| `wepdf` | `pdf-ai` |
| `trip-sorted` | `fast-track-ai`, `new-fast-track`, `travel-dashboard` |
| `checkin` | `checkin-ai`, `airport-checkin`, `new-airport-checkin` |
| `topup` | `top-up`, `topup` |
| `admin` | `back-office`, `global-dashboard`, `monorepo` |

## Adding a new theme

1. Copy `src/themes/checkin.ts` as a starting point.
2. Update `cssVars` with your HSL triplets (not the `hsl(...)` wrapper — the preset adds that).
3. Add a matching `[data-theme="<key>"]` block to `src/tailwind/theme.css`.
4. Register the theme in `src/themes/index.ts`.
5. Bump the version.

## Conventions

- Colors are HSL triplets (`"221 83% 53%"`). This lets Tailwind's `<alpha-value>` work — `bg-primary/40` gets you transparency for free.
- `--radius` is the single dial for "how rounded the brand feels". Everything else is derived from it.
- `--shadow-color` is tinted per brand (as an RGB triplet without commas: `"37 99 235"`) so elevation feels on-brand.
- Status colors (`success`, `warning`, `danger`, `info`) are cross-brand. Don't override them in themes.

## See also

- `ADOPTION.md` — per-repo checklists for rolling this out.
- `../sanjow-brand-strategy.jsx` — the source of truth for brand personality, TOV, and anti-patterns. Visual tokens here must reflect that file.
