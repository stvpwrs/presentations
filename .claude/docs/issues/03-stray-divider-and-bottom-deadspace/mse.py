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
