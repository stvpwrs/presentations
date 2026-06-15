### Summary
On a `resource-box` slide, badge labels longer than ~6 characters wrap awkwardly inside the narrow fixed-width badge — e.g. "Presentations" breaks mid-word as "Presentat ions" and "Build and Govern" stacks onto three cramped lines.

### Severity / Impact
High — any resource box with a label longer than ~6 characters is hard to read. Short labels are unaffected.

### Environment
- `ms-presentations` version: 0.1.6
- Python version: 3.10+
- OS / version: reproduces on all (verified on Windows 11)
- Install method: pip / from source
- Relevant deps (if Azure path): n/a — renders fully locally, no Azure
- Azure / model config: n/a

### Steps to Reproduce
1. Author a `resource-box` slide with a box label longer than ~6 characters.
2. Keep the default `badge_width` (0.9") and `badge_font_size` (11).
3. Render and open the `.pptx`.

### Minimal Reproducible Example (MRE)

The script below is also checked in as [`mse.py`](mse.py) in this folder.

```python
# /// script
# requires-python = ">=3.10"
# dependencies = ["ms-presentations==0.1.6"]
# ///
"""Self-contained MRE — Bug 2: resource-box badge label overflow / mid-word wrap.

Run with:  uv run mse.py   (no venv, no Azure, no network)

Bug:      Long badge labels wrap mid-word inside the fixed 0.9" badge.
Expected: Labels fit the badge (shrunk if needed) without mid-word breaks.
Actual:   "Presentations" renders as "Presentat ions" and "Build and Govern"
          stacks onto three cramped lines; the short "Learn" label is fine.
          Open the rendered .pptx and compare the three badges.
"""
import os
import tempfile

from presentations.cli import main

SPEC = """\
---
title: Repro - Badge label overflow
output: Bug02_Badge_Label_Overflow.pptx
style:
  badge_width: 0.9
  badge_font_size: 11
---

## [resource-box] Getting started

**Subtitle**: Resources

**Box**: Learn
- Microsoft AI | https://learn.microsoft.com/ai/

**Box**: Build and Govern
- Azure AI Services | https://learn.microsoft.com/azure/ai-services/

**Box**: Presentations
- Samples | https://github.com/microsoft/presentations/samples
"""

with tempfile.TemporaryDirectory() as d:
    spec_path = os.path.join(d, "minimal.spec.md")
    with open(spec_path, "w", encoding="utf-8") as f:
        f.write(SPEC)
    main([spec_path, "-o", d])
    out = os.path.join(d, "Bug02_Badge_Label_Overflow.pptx")
    print("rendered:", os.path.isfile(out))
    print("Inspect badges: 'Presentations' breaks mid-word, 'Learn' is fine.")
```

```bash
uv run mse.py
```

### Expected Behavior
Long labels shrink (or otherwise fit) the badge without breaking words mid-character.

### Actual Behavior
"Presentations" wraps to "Presentat ions"; "Build and Govern" stacks onto three cramped lines; "Learn" renders cleanly — showing the problem is label length, not the box.

### Additional Context
Root cause in `add_resource_box_slide` (`src/presentations/slides.py:443, 488-498`): the badge is a fixed 0.9"-wide rounded rectangle with `word_wrap = True` at 11 pt and **no auto-fit**, and python-pptx does not shrink text to fit. PowerPoint hard-wraps, including mid-word when a single word exceeds the box width.

Suggested fix (most robust): set `text_frame.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE`, paired with a deterministic font step-down for long labels (so the fit is correct even in renderers that don't recompute `normAutofit`). This touches only the badge text frame/font — no geometry — so it's independent of the other resource-box fixes.
