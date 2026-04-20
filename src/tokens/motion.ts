/**
 * Motion tokens — durations and easings.
 */

export const duration = {
  instant: "0ms",
  fast: "120ms",
  base: "200ms",
  slow: "320ms",
  slower: "480ms",
} as const;

export const easing = {
  linear: "linear",
  standard: "cubic-bezier(0.2, 0, 0, 1)",
  accelerate: "cubic-bezier(0.4, 0, 1, 1)",
  decelerate: "cubic-bezier(0, 0, 0.2, 1)",
} as const;

export type Duration = typeof duration;
