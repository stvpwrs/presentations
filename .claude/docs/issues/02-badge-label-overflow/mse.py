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
