### Summary
Every `resource-box` box draws exactly one horizontal divider at a fixed offset regardless of row count: in a single-row box it becomes a stray underline beneath the lone row, and all boxes show empty space at the bottom because rows cluster near the top.

### Severity / Impact
Medium — cosmetic but consistently wrong on every resource box (stray line on one-row boxes; unused bottom padding on all).

### Environment
- `ms-presentations` version: 0.1.6
- Python version: 3.10+
- OS / version: reproduces on all (verified on Windows 11)
- Install method: pip / from source
- Relevant deps (if Azure path): n/a — renders fully locally, no Azure
- Azure / model config: n/a

### Steps to Reproduce
1. Author a `resource-box` slide with a mix of one-row and multi-row boxes.
2. Render and open the `.pptx`.

### Minimal Reproducible Example (MRE)

The script below is also checked in as [`mse.py`](mse.py) in this folder.

```python
# /// script
# requires-python = ">=3.10"
# dependencies = ["ms-presentations==0.1.6"]
# ///
"""Self-contained MRE — Bug 3: stray divider + bottom dead space in resource-box.

Run with:  uv run mse.py   (no venv, no Azure, no network)

Bug:      One divider is drawn at a fixed 0.38" offset per box regardless of row
          count, and rows are top-anchored leaving unused bottom padding.
Expected: Dividers separate adjacent rows only (none for a one-row box); rows
          fill the box without bottom dead space.
Actual:   The one-row "Solo" box shows a stray underline with empty space below;
          every box clusters rows at the top with a +0.35" gap at the bottom.
          Open the rendered .pptx and inspect the dividers and bottom margins.
"""
import os
import tempfile

from presentations.cli import main

SPEC = """\
---
title: Repro - Stray divider + bottom dead space
output: Bug03_Stray_Divider_Deadspace.pptx
---

## [resource-box] Getting started

**Subtitle**: Resources

**Box**: Two
- Row One | https://example.com/1
- Row Two | https://example.com/2

**Box**: Solo
- Lonely Row | https://example.com/solo

**Box**: Three
- Row A | https://example.com/a
- Row B | https://example.com/b
- Row C | https://example.com/c
"""

with tempfile.TemporaryDirectory() as d:
    spec_path = os.path.join(d, "minimal.spec.md")
    with open(spec_path, "w", encoding="utf-8") as f:
        f.write(SPEC)
    main([spec_path, "-o", d])
    out = os.path.join(d, "Bug03_Stray_Divider_Deadspace.pptx")
    print("rendered:", os.path.isfile(out))
    print("Inspect 'Solo': stray underline + empty space below; all boxes bottom-heavy.")
```

```bash
uv run mse.py
```

### Expected Behavior
A divider appears only between adjacent rows (none in a single-row box), and rows are distributed so the box isn't bottom-heavy with whitespace.

### Actual Behavior
The one-row "Solo" box has a stray underline with empty space below; "Two" and "Three" cluster rows at the top with a visible gap at the bottom.

### Additional Context
Root cause in `add_resource_box_slide` (`src/presentations/slides.py`):
- Divider drawn once at a fixed offset regardless of row count: `div_y = box_top + Inches(0.38)` (`slides.py:404-411`).
- Rows top-anchored at `box_top + 0.08`, 0.5" apart (`slides.py:415`), while `container_height = 0.5*num_rows + 0.35` — the trailing +0.35" is never used → bottom dead space.

Suggested fix: draw inter-row dividers inside the row loop (skip for `num_rows == 1`) and vertically center the row block within the container. Keep `container_height` unchanged so this composes with the badge-height clamp fix (they touch disjoint lines in the same function).
