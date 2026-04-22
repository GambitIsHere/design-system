# OG image reference mocks

Branded 1200×630 Open Graph mocks used as visual references when commissioning per-product OG images. These are **reference/style** assets — the canonical OG files that actually ship live in each product's repo under `public/og/…`.

| File | Product | Shipped as |
|---|---|---|
| `TravelSynch-1000x630.png` | Fast Track | `fast-track-ai:public/og/fast-track-default.png` (re-rendered to 1200×630, 356 KB) |
| `OnlineVisas-1000x630.png` | Visa Portals | _not yet shipped — pending ARCH-like OG ticket_ |

All reference mocks here are:

- Resampled to exactly **1200 × 630 px** (Facebook / Twitter / LinkedIn canonical size).
- Palette-quantised PNGs (≤ 500 KB) — full-resolution originals are not checked in to avoid repo bloat.
- Style-consistent: navy → teal horizontal gradient, world-map silhouette watermark, centred minimal line-art icon, bold sans-serif heading, soft subline, sparkle motif bottom-right.

To generate a new product OG mock that matches this family, use the prompt in `../../../fast_track-sprint-2-handoff.md` → _Fast Track OG image — generation prompt_ as a starting point and swap the headline / icon / subline.
