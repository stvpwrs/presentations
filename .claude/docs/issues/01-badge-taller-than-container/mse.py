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
