import type { Theme } from "./types.js";

/**
 * Trip Sorted — travel-first brand used by fast-track-ai (and
 * shareable with other travel products). Ocean blue + gold warmth.
 *
 * Derived from fast-track-ai's existing tailwind brand-navy / ocean /
 * gold palette so dropping in the design system is non-destructive.
 * Repo: fast-track-ai.
 */
export const tripSorted: Theme = {
  key: "trip-sorted",
  name: "Trip Sorted",
  repos: ["fast-track-ai", "new-fast-track", "travel-dashboard"],
  tagline: "Travel, sorted.",
  typography: {
    display: "Space Grotesk",
    body: "Inter",
  },
  cssVars: {
    "--background": "0 0% 100%",
    "--foreground": "215 60% 12%",

    "--card": "0 0% 100%",
    "--card-foreground": "215 60% 12%",
    "--popover": "0 0% 100%",
    "--popover-foreground": "215 60% 12%",

    "--primary": "215 72% 24%", // ocean / brand-navy
    "--primary-foreground": "200 100% 97%",

    "--secondary": "199 93% 65%", // sky
    "--secondary-foreground": "215 60% 12%",

    "--accent": "37 92% 50%", // gold / cta
    "--accent-foreground": "30 100% 10%",

    "--muted": "210 40% 96%",
    "--muted-foreground": "215 16% 47%",

    "--destructive": "0 84% 60%",
    "--destructive-foreground": "0 0% 98%",

    "--border": "214 32% 91%",
    "--input": "214 32% 91%",
    "--ring": "215 72% 24%",

    // Extras used by fast-track-ai today — keep them wired so existing
    // utilities (`bg-ocean`, `text-gold`) don't break.
    "--brand-navy": "215 72% 24%",
    "--brand-accent": "37 92% 50%",
    "--brand-sky": "199 93% 65%",
    "--cta-start": "37 92% 50%",
    "--cta-end": "25 95% 53%",
    "--ocean": "215 72% 24%",
    "--ocean-light": "215 55% 40%",
    "--ocean-dark": "215 80% 14%",
    "--sky": "199 93% 65%",
    "--gold": "37 92% 50%",
    "--sand": "40 40% 92%",

    "--shadow-color": "32 56 128",
    "--radius": "0.875rem",

    "--font-display":
      "var(--font-space-grotesk, var(--font-inter, system-ui))",
    "--font-body": "var(--font-inter, system-ui)",
  },
};
