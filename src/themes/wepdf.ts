import type { Theme } from "./types.js";

/**
 * WePDF — clean, calm, functional. Trust blue + affordable green.
 * Source: sanjow-brand-strategy.jsx (lines 14–66).
 * Repo: pdf-ai.
 */
export const wepdf: Theme = {
  key: "wepdf",
  name: "WePDF",
  repos: ["pdf-ai"],
  tagline: "The PDF toolkit that never surprises you.",
  typography: {
    display: "Fraunces",
    body: "Söhne, Geist, Inter",
  },
  cssVars: {
    // HSL triplets — used by Tailwind via hsl(var(--primary) / <alpha>).
    "--background": "0 0% 100%",
    "--foreground": "222 47% 11%",

    "--card": "0 0% 100%",
    "--card-foreground": "222 47% 11%",
    "--popover": "0 0% 100%",
    "--popover-foreground": "222 47% 11%",

    "--primary": "221 83% 53%", // #2563EB
    "--primary-foreground": "210 40% 98%",
    "--secondary": "210 40% 96%",
    "--secondary-foreground": "222 47% 11%",

    "--accent": "160 84% 39%", // #10B981
    "--accent-foreground": "160 100% 9%",

    "--muted": "210 40% 96%",
    "--muted-foreground": "215 16% 47%",

    "--destructive": "0 84% 60%",
    "--destructive-foreground": "0 0% 98%",

    "--border": "214 32% 91%",
    "--input": "214 32% 91%",
    "--ring": "221 83% 53%",

    // Brand-tinted elevation.
    "--shadow-color": "37 99 235", // rgb of #2563EB

    // Radius + density.
    "--radius": "0.75rem",

    // Font wiring — repos set the actual --font-* vars via next/font.
    "--font-display": "var(--font-fraunces, Georgia, serif)",
    "--font-body":
      "var(--font-sohne, var(--font-geist, var(--font-inter, system-ui)))",
  },
};
