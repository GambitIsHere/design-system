import type { Theme } from "./types.js";

/**
 * Check-in — airport-signage feel: functional sky blue + amber accent.
 * Source: sanjow-brand-strategy.jsx (lines 120–172). Repo: checkin-ai.
 */
export const checkin: Theme = {
  key: "checkin",
  name: "Airport Check-in",
  repos: ["checkin-ai", "airport-checkin", "new-airport-checkin"],
  tagline: "Check in. Print. Board. That's it.",
  typography: {
    display: "Space Grotesk Wide / Söhne Breit",
    body: "Söhne, Inter",
  },
  cssVars: {
    "--background": "0 0% 100%",
    "--foreground": "210 75% 8%",

    "--card": "0 0% 100%",
    "--card-foreground": "210 75% 8%",
    "--popover": "0 0% 100%",
    "--popover-foreground": "210 75% 8%",

    "--primary": "201 96% 40%", // #0284C7
    "--primary-foreground": "0 0% 100%",

    "--secondary": "210 40% 96%",
    "--secondary-foreground": "210 75% 8%",

    "--accent": "38 92% 50%", // #F59E0B
    "--accent-foreground": "30 100% 10%",

    "--muted": "210 40% 96%",
    "--muted-foreground": "215 16% 47%",

    "--destructive": "0 84% 60%",
    "--destructive-foreground": "0 0% 98%",

    "--border": "214 32% 91%",
    "--input": "214 32% 91%",
    "--ring": "201 96% 40%",

    "--shadow-color": "2 132 199",
    "--radius": "0.625rem", // slightly tighter — signage feel

    "--font-display":
      "var(--font-space-grotesk, var(--font-inter, system-ui))",
    "--font-body": "var(--font-inter, system-ui)",
  },
};
