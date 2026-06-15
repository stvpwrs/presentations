# /// script
# requires-python = ">=3.10"
# dependencies = ["ms-presentations==0.1.6"]
# ///
"""Self-contained MRE — Bug 4: silent slide drop on a missing '---' separator.

Run with:  uv run mse.py   (no venv, no Azure, no network)

Bug:      When the '---' separator between two '## [type]' headers is missing,
          the second slide is folded into the first slide's notes and dropped.
Expected: 3 slides parsed (and ideally a warning about the missing separator).
Actual:   2 slides parsed, no warning. The printed slide count below is the
          deterministic observable: expected 3, actual 2.
"""
import os
import tempfile

from presentations.spec_parser import parse_spec
from presentations.cli import main

SPEC = """\
---
title: Repro - Silent slide drop
output: Bug04_Silent_Slide_Drop.pptx
---

## [content] Slide One (renders)

- Properly separated by a --- below.

**Notes**: First slide.

---

## [content] Slide Two (absorbs slide three)

- This slide is followed by a '## [content]' header below,
- but there is NO '---' separator between them.

**Notes**: Everything below, including Slide Three, gets swallowed here.

## [content] Slide Three (silently dropped)

- These bullets never become their own slide.

**Notes**: Expected 3 slides, actual 2.
"""

with tempfile.TemporaryDirectory() as d:
    spec_path = os.path.join(d, "minimal.spec.md")
    with open(spec_path, "w", encoding="utf-8") as f:
        f.write(SPEC)

    parsed = parse_spec(spec_path)
    print("slides parsed:", len(parsed["slides"]), "(expected 3)")

    main([spec_path, "-o", d])  # renders without error or warning
    print("rendered:", os.path.isfile(os.path.join(d, "Bug04_Silent_Slide_Drop.pptx")))
