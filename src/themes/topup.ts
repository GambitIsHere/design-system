import type { Theme } from "./types.js";

/**
 * TopUp — warm diaspora orange + deep green. Not adopted by any of
 * the 4 v1 repos, but included so the theme set stays complete.
 * Source: sanjow-brand-strategy.jsx (lines 68–120).
 */
export const topup: Theme = {
  key: "topup",
  name: "TopUp",
  repos: ["top-up", "topup"],
  tagline: "Credit home in 30 seconds. No subscription. Never.",
  typography: {
    display: "General Sans",
    body: "Inter",
  },
  cssVars: {
    "--background": "0 0% 100%",
    "--foreground": "20 50% 10%",

    "--card": "0 0% 100%",
    "--card-foreground": "20 50% 10%",
    "--popover": "0 0% 100%",
    "--popover-foreground": "20 50% 10%",

    "--primary": "22 96% 46%", // #E85D04
    "--primary-foreground": "30 100% 98%",

    "--secondary": "20 20% 96%",
    "--secondary-foreground": "20 50% 10%",

    "--accent": "125 44% 33%", // #2E7D32
    "--accent-foreground": "120 60% 96%",

    "--muted": "20 20% 96%",
    "--muted-foreground": "20 15% 40%",

    "--destructive": "0 84% 60%",
    "--destructive-foreground": "0 0% 98%",

    "--border": "20 15% 88%",
    "--input": "20 15% 88%",
    "--ring": "22 96% 46%",

    "--shadow-color": "232 93 4",
    "--radius": "1rem", // rounded, friendly

    "--font-display":
      "var(--font-general-sans, var(--font-inter, system-ui))",
    "--font-body": "var(--font-inter, system-ui)",
  },
};
