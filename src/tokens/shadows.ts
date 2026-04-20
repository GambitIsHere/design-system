/**
 * Shadow tokens.
 *
 * `--shadow-color` is brand-tinted — brands with a strong primary
 * (e.g. WePDF blue) set it to their primary hue so elevation feels
 * on-brand rather than generic gray.
 */

export const shadow = {
  none: "none",
  xs: "0 1px 2px 0 rgb(var(--shadow-color) / 0.04)",
  sm: "0 1px 3px 0 rgb(var(--shadow-color) / 0.08), 0 1px 2px -1px rgb(var(--shadow-color) / 0.08)",
  md: "0 4px 6px -1px rgb(var(--shadow-color) / 0.10), 0 2px 4px -2px rgb(var(--shadow-color) / 0.10)",
  lg: "0 10px 15px -3px rgb(var(--shadow-color) / 0.12), 0 4px 6px -4px rgb(var(--shadow-color) / 0.12)",
  xl: "0 20px 25px -5px rgb(var(--shadow-color) / 0.14), 0 8px 10px -6px rgb(var(--shadow-color) / 0.14)",
  glow: "0 0 0 1px rgb(var(--ring) / 0.20), 0 8px 24px -4px rgb(var(--shadow-color) / 0.35)",
  inner: "inset 0 1px 2px 0 rgb(0 0 0 / 0.06)",
} as const;

export type Shadow = typeof shadow;
