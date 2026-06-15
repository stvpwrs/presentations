### Summary
When a deck mixes a core slide (`content` / `two-column` / `section-header`) with any rich layout, the renderer flips the whole deck to 16:9 (13.333" wide), but the core builders' default positions are hard-coded for a 10" (4:3) canvas — so core slides render with an off-center title and ~6" of empty space on the right.

### Severity / Impact
Medium (latent) — not visible in pure 4:3 decks, but any deck mixing a core and a rich layout is affected. Worth fixing before mixed-layout decks are authored.

### Environment
- `ms-presentations` version: 0.1.6
- Python version: 3.10+
- OS / version: reproduces on all (geometry only; verified on Windows 11)
- Install method: pip / from source
- Relevant deps (if Azure path): n/a — renders fully locally, no Azure
- Azure / model config: n/a

### Steps to Reproduce
1. Author a deck with one rich slide (e.g. `hero-title`) and one core `content` slide.
2. Render and open the `.pptx` (the rich slide forces 16:9).
3. Observe the core slide's title/body sized for 10" against a 13.333" canvas.

### Minimal Reproducible Example (MRE)

The script below is also checked in as [`mse.py`](mse.py) in this folder.

```python
# /// script
# requires-python = ">=3.10"
# dependencies = ["ms-presentations==0.1.6"]
# ///
"""Self-contained MRE — Bug 5: 4:3-vs-16:9 geometry mismatch for core layouts.

Run with:  uv run mse.py   (no venv, no Azure, no network)

Bug:      A rich layout flips the deck to 16:9, but core builders use 10"-canvas
          default positions, so core slides don't span the widescreen canvas.
Expected: On a 13.333" canvas the core title/body scale to fill the slide.
Actual:   The content slide's title stays 8.5" wide on a 13.333" canvas (an
          off-center title + ~6" right gap). The printed widths below are the
          deterministic observable.
"""
import os
import tempfile

from pptx import Presentation
from presentations.cli import main

SPEC = """\
---
title: Repro - Aspect ratio mismatch
output: Bug05_Aspect_Ratio_Mismatch.pptx
---

## [hero-title] Rich Layout Forces Widescreen

**Eyebrow**: KEYNOTE
**Subtitle**: This rich slide flips the deck to 16:9 (13.333" wide).

**Notes**: hero-title is a rich type, so the whole deck renders widescreen.

---

## [content] Core Slide On The Wrong Canvas

- Core content slide with default geometry.
- Its title default is 8.5" wide, sized for a 10" canvas, not 13.333".

**Notes**: On the forced widescreen canvas the title no longer spans the slide.
"""

with tempfile.TemporaryDirectory() as d:
    spec_path = os.path.join(d, "minimal.spec.md")
    with open(spec_path, "w", encoding="utf-8") as f:
        f.write(SPEC)
    main([spec_path, "-o", d])

    prs = Presentation(os.path.join(d, "Bug05_Aspect_Ratio_Mismatch.pptx"))
    print("slide width (in):", round(prs.slide_width / 914400, 3))  # ~13.333
    content_slide = prs.slides[1]
    if content_slide.shapes.title is not None:
        print("core title width (in):", round(content_slide.shapes.title.width / 914400, 3))
    print("Title width ~8.5 on a ~13.333 canvas -> does not span the slide.")
```

```bash
uv run mse.py
# → slide width (in): 13.333
# → core title width (in): 8.5
```

### Expected Behavior
On the widescreen canvas the core title and body scale up to span the 13.333" slide (no large right-hand gap, title centered).

### Actual Behavior
The core slide's title is ~8.5" wide and body ~6.5" wide on a 13.333" canvas, leaving ~6" empty on the right with the title off-center.

### Additional Context
Root cause: `renderer.render` flips the deck to 16:9 when any `_RICH_TYPES` slide is present (`src/presentations/renderer.py:105-114`), but `_CONTENT_DEFAULTS` / `_TWO_COL_DEFAULTS` hard-code 10"-canvas positions (`src/presentations/slides.py:112-124`). Rich builders hard-code 13.333"-based literals (`rich_layouts.py:37` and throughout), so the two families only look right on their own canvas size.

Suggested fix: derive core defaults from `prs.slide_width` via a `_scaled_defaults` helper that scales only horizontal (left/width) values — height is constant at 7.5" across both aspect ratios. Scale factor is exactly 1.0 on a 4:3 deck, so existing 4:3 output is byte-for-byte unchanged. The resource-box builder already derives from `prs.slide_width` and needs no change. Independent of the parser and resource-box fixes.
