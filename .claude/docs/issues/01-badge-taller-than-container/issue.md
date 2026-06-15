### Summary
On a `resource-box` slide, a box with a single row renders its gradient badge taller than the box — the badge sticks out above and below the rounded rectangle.

### Severity / Impact
High — visibly broken layout on any one-row resource box (and any future short box). Affects the `resource-box` slide type with the default `badge_height`.

### Environment
- `ms-presentations` version: 0.1.6
- Python version: 3.10+
- OS / version: reproduces on all (pure python-pptx geometry; verified on Windows 11)
- Install method: pip / from source
- Relevant deps (if Azure path): n/a — renders fully locally, no Azure
- Azure / model config: n/a

### Steps to Reproduce
1. Author a `resource-box` slide with at least one box that has a single row.
2. Keep the default `badge_height` (1.1").
3. Render the spec and open the `.pptx`.

### Minimal Reproducible Example (MRE)

The script below is also checked in as [`mse.py`](mse.py) in this folder.

```python
# /// script
# requires-python = ">=3.10"
# dependencies = ["ms-presentations==0.1.6"]
# ///
"""Self-contained MRE — Bug 1: resource-box badge taller than its container.

Run with:  uv run mse.py   (no venv, no Azure, no network)

Bug:      A single-row resource box renders its gradient badge taller than the
          box; the badge overflows above and below the rounded rectangle.
Expected: The badge is fully framed inside every box, regardless of row count.
Actual:   A one-row box has a 0.85" container, shorter than the default 1.1"
          badge, so the centering offset (container_height - badge_h)/2 goes
          negative and the badge spills out top and bottom. Open the rendered
          .pptx and compare the one-row "Learn" badge to its box.
"""
import os
import tempfile

from presentations.cli import main

SPEC = """\
---
title: Repro - Badge taller than container
output: Bug01_Badge_Taller_Than_Container.pptx
style:
  badge_height: 1.1
---

## [resource-box] Getting started

**Subtitle**: Resources

**Box**: Learn
- One Row Only | https://example.com/one

**Box**: Reference
- First Row | https://example.com/a
- Second Row | https://example.com/b
"""

with tempfile.TemporaryDirectory() as d:
    spec_path = os.path.join(d, "minimal.spec.md")
    with open(spec_path, "w", encoding="utf-8") as f:
        f.write(SPEC)
    main([spec_path, "-o", d])
    out = os.path.join(d, "Bug01_Badge_Taller_Than_Container.pptx")
    print("rendered:", os.path.isfile(out))
    print("Inspect the one-row 'Learn' badge: it overflows its 0.85\" box.")
```

```bash
uv run mse.py
```

### Expected Behavior
The badge stays fully inside the box for every box, including single-row boxes.

### Actual Behavior
The one-row "Learn" badge is ~1.1" tall inside a 0.85" container, so it protrudes above the box top and below the box bottom. The two-row "Reference" badge is fine.

### Additional Context
Root cause in `add_resource_box_slide` (`src/presentations/slides.py`):
- Container height scales with rows: `container_height = Inches(0.5 * num_rows + 0.35)` (`slides.py:353`) → 1 row = 0.85".
- Badge height is fixed at the style default 1.1" (`style.py:13`).
- Badge is centered with `badge_y = box_top + Inches((container_height/Inches(1) - badge_h) / 2)` (`slides.py:444`); when `badge_h > container_height` the offset is negative.

Suggested fix: clamp the badge to `effective_badge_h = min(badge_h, container_height/Inches(1))` and center on that value. Leaves `container_height` untouched, so it composes with the divider/row-centering fix. Multi-row boxes are unaffected (`min()` returns the original `badge_h`).
