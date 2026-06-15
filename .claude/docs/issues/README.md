# Issues

One folder per finding from [`LAYOUT_REVIEW.md`](../LAYOUT_REVIEW.md). Each
folder contains:

- **`bug.md`** — detailed explanation: symptom, root cause (`file:line`), and a fix direction.
- **`spec.md`** — a minimal spec deck that reproduces the bug when rendered. Build it with the
  normal render entry point (no Azure access or images required) and inspect the resulting
  `.pptx` / PNG export.
- **`fix.md`** — the proposed code change (before/after) plus a ready-to-use commit write-up.
  Present for findings 1–5; finding 6 has no code fix (it is environmental).

## Fix coupling

- **Findings 4 and 5** are fully isolated (different files, no shared state).
- **Finding 2** is isolated within the resource-box function (text/font only).
- **Findings 1 and 3** share the resource-box function. The fixes are written to
  compose: Fix 1 clamps the badge height and Fix 3 centers the rows / draws
  inter-row dividers — **neither changes `container_height`**, so they can land in
  either order.

| Folder | Finding | Area | Severity |
|--------|---------|------|----------|
| [01-badge-taller-than-container](01-badge-taller-than-container/) | Badge taller than its container | resource-box | High |
| [02-badge-label-overflow](02-badge-label-overflow/) | Badge label overflow / mid-word wrapping | resource-box | High |
| [03-stray-divider-and-bottom-deadspace](03-stray-divider-and-bottom-deadspace/) | Stray divider + bottom dead space | resource-box | Medium |
| [04-silent-slide-drop-on-missing-separator](04-silent-slide-drop-on-missing-separator/) | Silent slide drop on missing `---` | parser | High |
| [05-aspect-ratio-geometry-mismatch](05-aspect-ratio-geometry-mismatch/) | Latent 4:3-vs-16:9 geometry mismatch | renderer / core builders | Medium (latent) |
| [06-missing-images](06-missing-images/) | Missing images | images | N/A (context, not a bug) |

> Note: Finding 6 is environmental (images not generated), not a code defect. It is included
> for completeness and clearly labelled as such in its `bug.md`.
