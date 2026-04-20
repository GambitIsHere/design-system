/**
 * Typography tokens.
 *
 * Display font is brand-specific (see themes). Body falls back to a
 * cross-brand stack so that untyped apps still render cleanly.
 */

export const fontFamily = {
  body: [
    "var(--font-body, var(--font-inter, var(--font-jakarta)))",
    "ui-sans-serif",
    "system-ui",
    "-apple-system",
    "Segoe UI",
    "Roboto",
    "sans-serif",
  ].join(", "),
  display: [
    "var(--font-display, var(--font-space-grotesk, var(--font-body)))",
    "ui-sans-serif",
    "system-ui",
    "sans-serif",
  ].join(", "),
  mono: [
    "var(--font-mono, ui-monospace)",
    "SFMono-Regular",
    "Menlo",
    "Consolas",
    "monospace",
  ].join(", "),
} as const;

/** Modular type scale — 1.200 (minor third) for UI density. */
export const fontSize = {
  xs: "0.75rem",
  sm: "0.875rem",
  base: "1rem",
  md: "1.125rem",
  lg: "1.25rem",
  xl: "1.5rem",
  "2xl": "1.875rem",
  "3xl": "2.25rem",
  "4xl": "3rem",
  "5xl": "3.75rem",
} as const;

export const fontWeight = {
  regular: 400,
  medium: 500,
  semibold: 600,
  bold: 700,
} as const;

export const lineHeight = {
  tight: "1.1",
  snug: "1.25",
  normal: "1.5",
  relaxed: "1.65",
} as const;

export const letterSpacing = {
  tight: "-0.02em",
  normal: "0",
  wide: "0.02em",
} as const;

export type FontFamily = typeof fontFamily;
export type FontSize = typeof fontSize;
