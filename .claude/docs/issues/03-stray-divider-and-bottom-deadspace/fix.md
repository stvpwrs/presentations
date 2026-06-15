# Fix 3 — Dividers between rows + vertically centered row block

**File:** `src/presentations/slides.py` · **Function:** `add_resource_box_slide`

## Approach

Two coordinated changes, both keeping `container_height` unchanged so this
composes with [Fix 1](../01-badge-taller-than-container/fix.md):

1. **Divider as a row separator.** Draw a divider *between* each adjacent pair of
   rows and skip it entirely for a single-row box (no more stray underline).
2. **Center the row block.** Vertically center the rows within the container
   instead of top-anchoring them, removing the bottom dead space caused by the
   unused `+ 0.35"` padding.

The fixed single-divider block at `slides.py:404-411` is removed; dividers are
drawn inside the row loop instead.

## The change

### 1. Remove the fixed divider (delete `slides.py:404-411`)

```python
# DELETE this block — the single fixed-offset divider
# Horizontal divider line inside container
div_y = box_top + Inches(0.38)
div_line = slide.shapes.add_connector(
    1, container_left + Inches(0.15), div_y,
    container_left + container_width - Inches(0.15), div_y,
)
div_line.line.color.rgb = divider_color
div_line.line.width = Pt(0.75)
```

### 2. Center the row block and draw inter-row dividers (replace the row loop at `slides.py:413-439`)

```python
# BEFORE
# Resource text rows inside the container
for i, row in enumerate(rows):
    row_y = box_top + Inches(0.08 + 0.5 * i)
    ...
```

```python
# AFTER
# Resource text rows, vertically centered within the container so the box
# isn't bottom-heavy with whitespace.
ROW_PITCH = 0.5          # vertical distance between row baselines
ROW_H = 0.35             # height of a single row textbox
container_h_in = container_height / Inches(1)
block_h = ROW_PITCH * (num_rows - 1) + ROW_H
top_pad = max((container_h_in - block_h) / 2, 0.08)

for i, row in enumerate(rows):
    row_y = box_top + Inches(top_pad + ROW_PITCH * i)

    # Divider between this row and the previous one (skipped for the first
    # row, so a single-row box draws no divider at all).
    if i > 0:
        div_y = box_top + Inches(top_pad + ROW_PITCH * i - (ROW_PITCH - ROW_H) / 2)
        div_line = slide.shapes.add_connector(
            1, container_left + Inches(0.15), div_y,
            container_left + container_width - Inches(0.15), div_y,
        )
        div_line.line.color.rgb = divider_color
        div_line.line.width = Pt(0.75)

    # Name text
    name_box = slide.shapes.add_textbox(
        container_left + Inches(0.2), row_y,
        Inches(2.5), Inches(0.35),
    )
    ntf = name_box.text_frame
    ntf.word_wrap = True
    np_ = ntf.paragraphs[0]
    np_.text = row["name"]
    np_.font.size = name_font_size
    np_.font.color.rgb = name_color

    # URL text (right-aligned)
    url_box = slide.shapes.add_textbox(
        container_left + container_width - Inches(4.7), row_y,
        Inches(4.5), Inches(0.35),
    )
    utf = url_box.text_frame
    utf.word_wrap = True
    up = utf.paragraphs[0]
    up.text = row["url"]
    up.font.size = url_font_size
    up.font.color.rgb = url_color
    up.alignment = PP_ALIGN.RIGHT
```

A single-row box now draws **no** divider and centers its one row; multi-row
boxes draw `num_rows - 1` dividers, each midway between adjacent rows, with the
whole block centered.

## Verification

Render [`spec.md`](spec.md). The one-row "Solo" box has no stray underline and its
row is centered; the two- and three-row boxes show dividers only *between* rows
with no bottom dead space.

## Interactions

- **Coupled** with Fix 1 by topic only. This fix never changes `container_height`,
  `badge_h`, or `badge_y`; Fix 1 never changes dividers or row positions. They can
  land in either order. (If both are applied, render the repros for Fix 1 *and*
  Fix 3 — the resource-box slide is now correct on both axes.)
- **Independent** of Fixes 2, 4, 5.

---

## Commit write-up

```
fix(resource-box): center rows and draw dividers between them

Each resource box drew exactly one divider at a fixed 0.38" offset
regardless of row count: fine between two rows, but a stray underline in a
single-row box. Rows were also top-anchored while the container reserved an
extra 0.35", leaving every box bottom-heavy with empty space.

Replace the single fixed divider with inter-row dividers drawn inside the
row loop (none for a one-row box), and vertically center the row block
within the container. Container height is unchanged, so this is orthogonal
to the badge-height clamp fix.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
```
