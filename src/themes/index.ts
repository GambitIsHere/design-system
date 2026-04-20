import type { Theme } from "./types.js";
import { wepdf } from "./wepdf.js";
import { tripSorted } from "./trip-sorted.js";
import { checkin } from "./checkin.js";
import { topup } from "./topup.js";
import { admin } from "./admin.js";

export type { Theme } from "./types.js";
export { wepdf, tripSorted, checkin, topup, admin };

/** All themes, keyed by their `key`. */
export const themes = {
  wepdf,
  "trip-sorted": tripSorted,
  checkin,
  topup,
  admin,
} as const satisfies Record<string, Theme>;

export type ThemeKey = keyof typeof themes;

/**
 * Render a theme as a CSS block:
 *
 *   :root { ...default vars... }
 *   [data-theme="checkin"] { ...overrides... }
 *
 * Used by src/tailwind/theme.css generation, and available at runtime
 * for apps that want to inject a theme dynamically.
 */
export function themeToCss(theme: Theme, selector: string): string {
  const body = Object.entries(theme.cssVars)
    .map(([k, v]) => `  ${k}: ${v};`)
    .join("\n");
  return `${selector} {\n${body}\n}`;
}

/**
 * Map a repo folder name → theme. Used by the adoption checklist
 * generator and by apps that want to pick a theme by repo name.
 */
export function themeForRepo(repo: string): Theme | undefined {
  return Object.values(themes).find((t) => t.repos.includes(repo));
}
