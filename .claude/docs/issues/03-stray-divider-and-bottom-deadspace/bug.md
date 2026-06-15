# Bug 3 — Stray single divider + bottom dead space (resource-box)

**Area:** resource-box · **Severity:** Medium

## Symptom

On a `resource-box` slide, every box draws **exactly one** horizontal divider line
near its top:

- In two-row boxes the line sits between the two rows (reasonable).
- In a **one-row** box it becomes a stray underline beneath the lone row, with
  empty space below it.

Separately, **all** boxes show noticeable empty space at the bottom because the
rows cluster near the top.

Evidence in the reviewed deck: **Slide 24** ("Getting started").

## Root cause

Two separate decisions in `add_resource_box_slide` (`src/presentations/slides.py`):

1. The divider is drawn **once** at a fixed offset, regardless of row count
   (`slides.py:404-411`):

   ```python
   div_y = box_top + Inches(0.38)
   ```

2. Rows are **top-anchored** starting at `box_top + 0.08`, each 0.5" apart
   (`slides.py:415`), while the container height is `0.5 * num_rows + 0.35`. The
   extra `+ 0.35"` of container height is never used, so it shows as dead space at
   the bottom. For a 2-row box, rows occupy ~0.08"–0.93" of a 1.35" container.

## Fix direction

Decide what the divider *means*:

- If it is a **row separator**, draw one between each adjacent pair of rows (and
  skip entirely when `num_rows == 1`).
- If it is a **header rule**, the layout needs an actual header row.

Separately, either reduce the trailing `+ 0.35` padding or vertically center the
row block within the container so boxes don't look bottom-heavy with whitespace.

## How to reproduce

Render [`spec.md`](spec.md) in this folder. The one-row "Solo" box shows the stray
divider underneath its single row with empty space below; the two-row boxes show
the unused bottom padding (rows clustered near the top).
