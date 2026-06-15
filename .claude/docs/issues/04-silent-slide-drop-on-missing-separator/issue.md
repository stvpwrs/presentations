### Summary
A spec that defines N slides renders only N−1, with no warning, when the author omits a `---` separator between two `## [type]` headers. The second slide's heading and bullets are silently swallowed into the first slide's speaker notes.

### Severity / Impact
High — a one-character authoring typo causes silent, unreported data loss (a whole slide disappears). Affects all spec parsing.

### Environment
- `ms-presentations` version: 0.1.6
- Python version: 3.10+
- OS / version: reproduces on all (pure parser logic; verified on Windows 11)
- Install method: pip / from source
- Relevant deps (if Azure path): n/a — parser only, no Azure
- Azure / model config: n/a

### Steps to Reproduce
1. Write a spec with two consecutive `## [type]` slides but no `---` between them.
2. Parse/render the spec.
3. Observe the deck has one fewer slide than authored, with no warning.

### Minimal Reproducible Example (MRE)

The script below is also checked in as [`mse.py`](mse.py) in this folder.

```python
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
```

```bash
uv run mse.py
# → slides parsed: 2 (expected 3)
```

### Expected Behavior
The parser produces 3 slides — and ideally emits a warning naming the header that lacked a separator.

### Actual Behavior
`parse_spec` returns 2 slides; "Slide Three" is absorbed into "Slide Two" notes. No warning is printed and rendering succeeds, hiding the loss.

### Additional Context
Root cause: `_split_slides_fence_aware` (`src/presentations/spec_parser.py:40-57`) splits only on `---` lines. With no separator both headers land in one chunk; `_parse_slide` (`spec_parser.py:81`) matches the first header and treats everything after the first `**Notes**:` as that slide's notes.

Suggested fix: when a second `## [type]` header appears in a chunk that already has one (and not inside a code fence), start a new chunk and print a warning naming the offending header. Fully isolated — different file, no shared state with any other fix.
