# Fix 2 — Auto-shrink badge labels (with deterministic fallback)

**File:** `src/presentations/slides.py` · **Function:** `add_resource_box_slide`

## Approach

Primary fix is the review's option (a): enable auto-shrink so PowerPoint scales
long labels down to fit the fixed-width badge. Because `python-pptx` writes the
`<a:normAutofit>` element but does **not** compute the shrink factor itself (only
PowerPoint/renderer does on open), we pair it with a deterministic font-size
reduction for long labels so the result is correct even in renderers that don't
recompute autofit. This keeps short labels at full size.

## The change

At `slides.py:488-498`:

```python
# BEFORE
btf = badge.text_frame
btf.word_wrap = True
from pptx.enum.text import MSO_ANCHOR
btf.paragraphs[0].alignment = PP_ALIGN.CENTER
btf.vertical_anchor = MSO_ANCHOR.MIDDLE
bp = btf.paragraphs[0]
bp.text = label
bp.font.size = Pt(badge_font_sz)
bp.font.color.rgb = badge_text_color
bp.font.bold = True
bp.alignment = PP_ALIGN.CENTER
```

```python
# AFTER
btf = badge.text_frame
btf.word_wrap = True
from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE
# Let PowerPoint shrink labels that don't fit the fixed-width badge...
btf.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE
btf.paragraphs[0].alignment = PP_ALIGN.CENTER
btf.vertical_anchor = MSO_ANCHOR.MIDDLE
bp = btf.paragraphs[0]
bp.text = label
# ...and apply a deterministic step-down for long labels so the fit is correct
# even in renderers that don't recompute autofit (python-pptx writes the
# normAutofit element but not the scale factor).
fitted_font_sz = badge_font_sz
if len(label) > 10:
    fitted_font_sz = max(7, int(badge_font_sz * 0.7))
elif len(label) > 6:
    fitted_font_sz = max(8, int(badge_font_sz * 0.85))
bp.font.size = Pt(fitted_font_sz)
bp.font.color.rgb = badge_text_color
bp.font.bold = True
bp.alignment = PP_ALIGN.CENTER
```

The thresholds (6 / 10 chars) match the observed wrap point of a 0.9" badge at
11 pt. Labels ≤ 6 chars ("Learn") are untouched.

## Verification

Render [`spec.md`](spec.md). "Presentations" and "Build and Govern" fit on fewer
lines without mid-word breaks; "Learn" is unchanged.

## Interactions

- **Independent** of Fixes 1, 3, 4, 5 — this touches only the badge text frame and
  font size, not any geometry (`container_height`, `badge_y`, dividers, rows).
- If option (b) "widen the badge" is ever preferred instead, note the badge sits at
  `left=0.3"` and the container at `left=1.6"`, leaving only ~0.4" of horizontal
  slack before the badge collides with the container.

---

## Commit write-up

```
fix(resource-box): shrink long badge labels to fit the badge

Badge labels render in a fixed 0.9"-wide rounded rectangle at 11pt with
word-wrap on but no auto-fit, so labels longer than ~6 characters wrap
awkwardly — "Presentations" breaks mid-word as "Presentat ions" and "Build
and Govern" stacks onto three cramped lines.

Enable TEXT_TO_FIT_SHAPE autofit on the badge text frame, and add a
deterministic font step-down for labels over 6/10 characters so the fit is
correct even in renderers that don't recompute python-pptx's normAutofit.
Short labels keep their original size.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
```
