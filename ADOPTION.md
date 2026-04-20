# Adoption checklist

One short list per repo. Each takes ~15 minutes end to end. Check off as you go.

---

## checkin-ai  →  theme `checkin`

Stack: Next.js 16 · Tailwind v4 · React 19 · shadcn + base-ui.

- [ ] `npm install file:../design-system` (or add workspace dependency).
- [ ] In `app/globals.css`, below `@import "tailwindcss";`, add:

      @import "@sanjow/design-system/theme.css";

- [ ] In `app/layout.tsx`, set `<html lang="en" data-theme="checkin">`.
- [ ] Delete the duplicated `:root` block in `app/globals.css` — `theme.css` owns it now. Keep any app-specific vars not in the design system.
- [ ] In `components.json` (shadcn), keep existing paths — base components from the design system are imported directly:

      import { Button } from "@sanjow/design-system/components";

- [ ] Replace `components/ui/button.tsx` imports one at a time, or keep the local shadcn Button as a thin re-export for gradual migration.
- [ ] Run `npm run build` and visually QA the homepage + one form + one modal.

---

## fast-track-ai  →  theme `trip-sorted`

Stack: Next.js · Tailwind v3 · Supabase.

- [ ] `npm install file:../design-system`.
- [ ] In `tailwind.config.ts`:

      import preset from "@sanjow/design-system/tailwind-preset";
      export default {
        presets: [preset],
        content: [
          "./src/**/*.{ts,tsx}",
          "../design-system/src/components/**/*.{ts,tsx}",
        ],
      } satisfies Config;

      // Keep `content` and any app-specific extensions. Delete the
      // colors/fontFamily/borderRadius blocks that overlap with the
      // preset.

- [ ] In `src/app/globals.css` (or equivalent), replace the hand-rolled `:root { --primary: … }` block with:

      @import "@sanjow/design-system/theme.css";

- [ ] `<html … data-theme="trip-sorted">` in `app/layout.tsx`.
- [ ] Existing `bg-ocean`, `text-gold`, `border-brand-navy` utilities continue to work — the preset aliases them to the trip-sorted theme vars.
- [ ] Migrate `components/ui/button.tsx` → `@sanjow/design-system/components` as above.

---

## pdf-ai  →  theme `wepdf`

Stack: Next.js 16 · Tailwind v3 · Radix · shadcn.

- [ ] `npm install file:../design-system`.
- [ ] Wire `tailwind.config.ts` via `presets: [preset]` and update `content` to include `../design-system/src/components/**`.
- [ ] Remove the duplicated `colors`, `borderRadius`, and `fontFamily.sans` blocks from the local config — the preset provides them.
- [ ] Keep `tailwindcss-animate` plugin; the preset defines the keyframes it expects.
- [ ] In the root layout, import `theme.css` and set `<html data-theme="wepdf">`.
- [ ] Wire brand fonts via `next/font`:

      import { Fraunces, Inter } from "next/font/google";
      const display = Fraunces({ variable: "--font-fraunces", subsets: ["latin"] });
      const body = Inter({ variable: "--font-inter", subsets: ["latin"] });
      <html className={`${display.variable} ${body.variable}`}>

  `theme.css` falls back through `--font-fraunces → Georgia → serif`, so this step is only needed if you want the real display typeface.
- [ ] Spot-check `/editor`, `/checkout`, and one error state — the checkout page is the most reputation-sensitive screen per brand strategy.

---

## back-office  →  theme `admin` (tokens only)

Stack: Next 10 · React 16 · Shopify Polaris · no Tailwind.

- [ ] `npm install file:../design-system`.
- [ ] In `pages/_app.tsx`, `import "@sanjow/design-system/theme.css";`.
- [ ] Set `<html data-theme="admin">` via `_document.tsx`.
- [ ] Consume tokens in styled-components / inline styles via `var(--primary)`, `var(--card)`, etc. Do **not** import components — they require React 18 and Tailwind.
- [ ] **Follow-up (separate ticket):** upgrade this repo to React 18 + Next 14+ and retrofit Tailwind before adopting the component layer. Track as part of the modernization described in `tech-stack-2026.md`.

---

## Rollout order (suggested)

1. `pdf-ai` — cleanest shadcn baseline, fastest payoff.
2. `checkin-ai` — proves the Tailwind v4 path works.
3. `fast-track-ai` — proves the existing travel aliases keep working.
4. `back-office` — tokens only until the stack upgrade lands.

## Sign-off per repo

After adoption, verify:

- [ ] Homepage renders with brand primary on primary CTAs (visual check).
- [ ] Dark mode / theme switching still works if the app supported it.
- [ ] No Tailwind class removed by `content` path changes (check the built CSS size; if it drops by > 30%, a `content` glob is probably missing).
- [ ] `npm run build` green locally.
- [ ] Lighthouse accessibility unchanged or better.
