---
title: Repro — 4:3 vs 16:9 geometry mismatch
subtitle: Bug 5 reproduction (latent)
output: Bug05_Aspect_Ratio_Mismatch.pptx
text_model: gpt-5-mini
image_model: gpt-image-1.5
---

## [hero-title] Rich Layout Forces Widescreen

**Eyebrow**: KEYNOTE
**Subtitle**: This rich slide flips the entire deck to 16:9 (13.333" wide).

**Notes**: Because this `hero-title` slide is one of the `_RICH_TYPES`, the whole
deck is rendered at 13.333" wide — including the core slide below, whose defaults
are hard-coded for a 10" canvas.

---

## [content] Core Slide On The Wrong Canvas

- This is a core `content` slide with default geometry.
- Its title default is 8.5" wide and its body default is 6.5" wide.
- Those were sized for a 10" canvas, not 13.333".

**Notes**: On the widescreen canvas forced by the hero-title slide above, this
title no longer spans the slide and the body block leaves roughly 6" of empty
space on the right, with the title off-center. To see the "correct" version,
render this slide on its own (remove the hero-title slide) so the deck stays 4:3.
