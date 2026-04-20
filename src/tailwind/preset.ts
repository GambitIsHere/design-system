/**
 * Tailwind v3 preset for Sanjow apps.
 *
 * Usage in a repo's `tailwind.config.ts`:
 *
 *   import preset from "@sanjow/design-system/tailwind-preset";
 *   export default {
 *     presets: [preset],
 *     content: ["./src/**\/*.{ts,tsx}"],
 *   } satisfies Config;
 *
 * Colors are wired to the CSS vars emitted by themes (see
 * ../themes). Repos still need to import `theme.css` once at root so
 * the `:root` vars exist.
 *
 * For Tailwind v4 apps (checkin-ai), skip the preset — use the
 * tailwind-v4.css entry instead, which uses the @theme directive.
 */

// Typed loosely to avoid a hard dependency on `tailwindcss` types at
// the library level (Tailwind isn't a runtime dep — it's a peer).
type Config = {
  darkMode?: unknown;
  content?: unknown;
  theme?: Record<string, unknown>;
  plugins?: unknown[];
};

import { fontSize, fontWeight, lineHeight, letterSpacing } from "../tokens/typography.js";
import { container, spacing } from "../tokens/spacing.js";
import { duration, easing } from "../tokens/motion.js";

const preset: Config = {
  darkMode: ["class", '[data-theme="admin"]'],
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": container["2xl"],
      },
    },
    extend: {
      fontFamily: {
        sans: ["var(--font-body)", "system-ui", "sans-serif"],
        display: ["var(--font-display)", "system-ui", "sans-serif"],
        mono: ["var(--font-mono)", "ui-monospace", "monospace"],
      },
      fontSize,
      fontWeight,
      lineHeight,
      letterSpacing,
      colors: {
        border: "hsl(var(--border) / <alpha-value>)",
        input: "hsl(var(--input) / <alpha-value>)",
        ring: "hsl(var(--ring) / <alpha-value>)",
        background: "hsl(var(--background) / <alpha-value>)",
        foreground: "hsl(var(--foreground) / <alpha-value>)",
        primary: {
          DEFAULT: "hsl(var(--primary) / <alpha-value>)",
          foreground: "hsl(var(--primary-foreground) / <alpha-value>)",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary) / <alpha-value>)",
          foreground: "hsl(var(--secondary-foreground) / <alpha-value>)",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive) / <alpha-value>)",
          foreground: "hsl(var(--destructive-foreground) / <alpha-value>)",
        },
        muted: {
          DEFAULT: "hsl(var(--muted) / <alpha-value>)",
          foreground: "hsl(var(--muted-foreground) / <alpha-value>)",
        },
        accent: {
          DEFAULT: "hsl(var(--accent) / <alpha-value>)",
          foreground: "hsl(var(--accent-foreground) / <alpha-value>)",
        },
        popover: {
          DEFAULT: "hsl(var(--popover) / <alpha-value>)",
          foreground: "hsl(var(--popover-foreground) / <alpha-value>)",
        },
        card: {
          DEFAULT: "hsl(var(--card) / <alpha-value>)",
          foreground: "hsl(var(--card-foreground) / <alpha-value>)",
        },
        // Travel-specific aliases — wired to the same vars used by
        // fast-track-ai today so `bg-ocean`/`text-gold` keep working.
        ocean: "hsl(var(--ocean, var(--primary)) / <alpha-value>)",
        "ocean-light": "hsl(var(--ocean-light, var(--primary)) / <alpha-value>)",
        "ocean-dark": "hsl(var(--ocean-dark, var(--primary)) / <alpha-value>)",
        sky: "hsl(var(--sky, var(--secondary)) / <alpha-value>)",
        gold: "hsl(var(--gold, var(--accent)) / <alpha-value>)",
        sand: "hsl(var(--sand, var(--muted)) / <alpha-value>)",
      },
      borderRadius: {
        sm: "calc(var(--radius) - 4px)",
        md: "calc(var(--radius) - 2px)",
        lg: "var(--radius)",
        xl: "calc(var(--radius) + 4px)",
        "2xl": "calc(var(--radius) + 8px)",
      },
      boxShadow: {
        xs: "var(--shadow-xs, 0 1px 2px 0 rgb(var(--shadow-color) / 0.04))",
        sm: "var(--shadow-sm, 0 1px 3px 0 rgb(var(--shadow-color) / 0.08))",
        md: "var(--shadow-md, 0 4px 6px -1px rgb(var(--shadow-color) / 0.10))",
        lg: "var(--shadow-lg, 0 10px 15px -3px rgb(var(--shadow-color) / 0.12))",
        xl: "var(--shadow-xl, 0 20px 25px -5px rgb(var(--shadow-color) / 0.14))",
        glow: "0 0 0 1px rgb(var(--ring) / 0.20), 0 8px 24px -4px rgb(var(--shadow-color) / 0.35)",
      },
      spacing,
      transitionDuration: duration,
      transitionTimingFunction: easing,
      keyframes: {
        "accordion-down": {
          from: { height: "0" },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: "0" },
        },
        "fade-in": {
          from: { opacity: "0" },
          to: { opacity: "1" },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
        "fade-in": "fade-in 0.2s ease-out",
      },
    },
  },
};

export default preset;
