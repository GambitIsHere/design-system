/**
 * Border-radius tokens.
 *
 * The `--radius` CSS variable drives sm/md/lg — brands override it in
 * ../themes to tune "how rounded" the brand feels. Pill is constant.
 */

export const radii = {
  none: "0",
  sm: "calc(var(--radius) - 4px)",
  md: "calc(var(--radius) - 2px)",
  lg: "var(--radius)",
  xl: "calc(var(--radius) + 4px)",
  "2xl": "calc(var(--radius) + 8px)",
  pill: "9999px",
  full: "9999px",
} as const;

/** Default --radius value if no theme is applied. */
export const radiusBase = "0.75rem";

export type Radii = typeof radii;
