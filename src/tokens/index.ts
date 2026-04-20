import { grayscale, status, chrome } from "./colors.js";
import {
  fontFamily,
  fontSize,
  fontWeight,
  lineHeight,
  letterSpacing,
} from "./typography.js";
import { spacing, container } from "./spacing.js";
import { radii, radiusBase } from "./radii.js";
import { shadow } from "./shadows.js";
import { duration, easing } from "./motion.js";

export * from "./colors.js";
export * from "./typography.js";
export * from "./spacing.js";
export * from "./radii.js";
export * from "./shadows.js";
export * from "./motion.js";

/** Consolidated token object for consumers that want a single import. */
export const tokens = {
  color: { grayscale, status, chrome },
  type: { fontFamily, fontSize, fontWeight, lineHeight, letterSpacing },
  space: spacing,
  container,
  radius: { ...radii, base: radiusBase },
  shadow,
  duration,
  easing,
} as const;

export type Tokens = typeof tokens;
