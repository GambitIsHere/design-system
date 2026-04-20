import type { Theme } from "./types.js";

/**
 * Admin / Back-Office — neutral dark "dashboard chrome". Uses the
 * ink/surface/elevated values defined in sanjow-brand-strategy.jsx so
 * internal tools share one look across back-office, global-dashboard,
 * etc.
 *
 * Note: back-office currently ships on React 16 + Polaris. Adoption
 * is tokens-first (as CSS vars) — full component usage requires a
 * Tailwind upgrade first. See ADOPTION.md.
 */
export const admin: Theme = {
  key: "admin",
  name: "Sanjow Admin",
  repos: ["back-office", "global-dashboard", "monorepo"],
  tagline: "Internal dashboard chrome.",
  typography: {
    display: "Inter",
    body: "Inter",
  },
  cssVars: {
    // Dark by default — admin surfaces are dense and neutral.
    "--background": "240 10% 4%",   // #0B0B0E ink
    "--foreground": "240 5% 96%",   // #F4F4F5 text

    "--card": "240 10% 9%",         // #131318 surface
    "--card-foreground": "240 5% 96%",
    "--popover": "240 9% 11%",      // #1B1B22 elevated
    "--popover-foreground": "240 5% 96%",

    "--primary": "240 5% 96%",      // text-on-ink CTAs
    "--primary-foreground": "240 10% 4%",

    "--secondary": "240 9% 11%",
    "--secondary-foreground": "240 5% 96%",

    "--accent": "221 83% 60%",      // a single blue accent for links/CTAs
    "--accent-foreground": "240 10% 4%",

    "--muted": "240 9% 11%",
    "--muted-foreground": "240 4% 63%", // #A1A1AA textDim

    "--destructive": "0 72% 51%",
    "--destructive-foreground": "0 0% 98%",

    "--border": "240 5% 15%",       // lineStrong
    "--input": "240 5% 15%",
    "--ring": "221 83% 60%",

    "--shadow-color": "0 0 0",
    "--radius": "0.5rem",           // tight, dense

    "--font-display": "var(--font-inter, system-ui)",
    "--font-body": "var(--font-inter, system-ui)",
  },
};
