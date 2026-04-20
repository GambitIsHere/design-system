/**
 * Color tokens — brand-agnostic foundations.
 *
 * Brands override the semantic layer (`semantic.*`) via themes in
 * ../themes. The raw palettes here are reference scales used to compose
 * those brand-specific semantic tokens.
 */

export const grayscale = {
  0: "#FFFFFF",
  50: "#FAFAFB",
  100: "#F4F4F5",
  200: "#E4E4E7",
  300: "#D4D4D8",
  400: "#A1A1AA",
  500: "#71717A",
  600: "#52525B",
  700: "#3F3F46",
  800: "#27272A",
  900: "#18181B",
  950: "#0B0B0E",
} as const;

/** Status colors — the same across brands. */
export const status = {
  success: "#10B981",
  successForeground: "#052E1A",
  warning: "#F59E0B",
  warningForeground: "#3B2208",
  danger: "#EF4444",
  dangerForeground: "#450A0A",
  info: "#0284C7",
  infoForeground: "#052033",
} as const;

/**
 * The neutral "dashboard chrome" palette used by internal tools
 * (admin, back-office). Matches the `ink/surface/elevated/line/text*`
 * constants at the top of sanjow-brand-strategy.jsx so the two stay
 * in sync.
 */
export const chrome = {
  ink: "#0B0B0E",
  surface: "#131318",
  elevated: "#1B1B22",
  line: "rgba(255,255,255,0.06)",
  lineStrong: "rgba(255,255,255,0.12)",
  text: "#F4F4F5",
  textDim: "#A1A1AA",
  textMute: "#71717A",
} as const;

export type Grayscale = typeof grayscale;
export type Status = typeof status;
export type Chrome = typeof chrome;
