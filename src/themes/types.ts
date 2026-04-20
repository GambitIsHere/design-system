/**
 * A Theme is the brand-specific layer that sits on top of raw tokens.
 * Each theme emits CSS custom properties on the :root or a scoped
 * [data-theme=...] selector, so downstream Tailwind utilities like
 * `bg-primary` pick up the right hue per brand.
 *
 * Colors are expressed as HSL triplets WITHOUT the `hsl(...)` wrapper
 * so they compose with Tailwind opacity modifiers:
 *
 *    color: hsl(var(--primary) / <alpha-value>);
 */
export interface Theme {
  /** Stable key used for [data-theme="..."] selector and lookups. */
  key: string;
  /** Human-readable name. */
  name: string;
  /** Which repo(s) this theme primarily targets. */
  repos: readonly string[];
  /** Short product tagline for reference. */
  tagline?: string;
  /**
   * CSS variables emitted at :root (or [data-theme="<key>"]). Values
   * are either HSL triplets ("221 83% 53%") or plain CSS values.
   */
  cssVars: Readonly<Record<string, string>>;
  /** Type pairing hint copied from brand strategy. */
  typography?: {
    display?: string;
    body?: string;
  };
}
