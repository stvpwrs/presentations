# Bug 1 — Badge can be taller than its container (resource-box)

**Area:** resource-box · **Severity:** High

## Symptom

On a `resource-box` slide, a box with a **single row** renders its gradient badge
visibly taller than the box itself — the badge sticks out above *and* below the
rounded rectangle. Two-row (and taller) boxes look fine.

Evidence in the reviewed deck: **Slide 24** ("Getting started"), third box
("Presentations"), which has one row.

## Root cause

In `add_resource_box_slide` (`src/presentations/slides.py`):

- Container height grows with the row count (`slides.py:353`):

  ```python
  container_height = Inches(0.5 * num_rows + 0.35)
  ```

  → 1 row = **0.85"**, 2 rows = 1.35", 3 rows = 1.85".

- Badge height is a fixed style value, default **1.1"** (`badge_height`,
  `style.py:13`; spec front-matter `badge_height: 1.1`).

- The badge is vertically centered in the container (`slides.py:444`):

  ```python
  badge_y = box_top + Inches((container_height / Inches(1) - badge_h) / 2)
  ```

When `badge_h (1.1) > container_height (0.85)`, the offset is **negative**
(`(0.85 - 1.1) / 2 = -0.125"`), so the badge starts above the box top and
extends below the box bottom.

The condition `badge_h > container_height` holds whenever a box has a single row
(0.85" < 1.1") — and would also trigger for any future short box.

## Fix direction

Either:

- **Clamp** the badge height to the container: `badge_h = min(badge_h, container_height)`, or
- **Enforce a minimum** container height of at least the badge height, e.g.
  `container_height = max(0.5 * num_rows + 0.35, badge_h + 0.1)`.

The second option keeps the badge fully framed and also removes the overflow for
any future one-row box.

## How to reproduce

Render [`spec.md`](spec.md) in this folder. The deck has three boxes — two with a
single row. With the default `badge_height: 1.1`, each one-row badge overflows
the 0.85"-tall container top and bottom. (The repro keeps the default
`badge_height` so the bug is visible out of the box.)
