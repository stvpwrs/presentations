# Fix 1 — Clamp badge height to its container

**File:** `src/presentations/slides.py` · **Function:** `add_resource_box_slide`

## Approach

Use the **clamp** option from the review (option a). Clamping leaves
`container_height` untouched, so it composes cleanly with [Fix 3](../03-stray-divider-and-bottom-deadspace/fix.md)
(which redistributes rows *within* the container). The alternative — growing the
container to `badge_h + 0.1` — would enlarge every short box and make Fix 3's
dead-space symptom worse, so it is deliberately not used here.

## The change

At `slides.py:443-444`:

```python
# BEFORE
badge_left = Inches(0.3)
badge_width, badge_height = Inches(badge_w), Inches(badge_h)
badge_y = box_top + Inches((container_height / Inches(1) - badge_h) / 2)
```

```python
# AFTER
badge_left = Inches(0.3)
# Clamp the badge height to the container so a short (e.g. single-row) box
# never lets the badge overflow above and below the rounded rectangle.
effective_badge_h = min(badge_h, container_height / Inches(1))
badge_width, badge_height = Inches(badge_w), Inches(effective_badge_h)
badge_y = box_top + Inches((container_height / Inches(1) - effective_badge_h) / 2)
```

With the clamp, `effective_badge_h ≤ container_height`, so the centering offset is
always `≥ 0` and the badge stays fully inside the box. For multi-row boxes
(container ≥ 1.35" > 1.1") nothing changes — `min()` returns the original
`badge_h`.

## Verification

Render [`spec.md`](spec.md). The two single-row badges now fit inside their
0.85"-tall boxes; the two-row "Reference" badge is unchanged.

## Interactions

- **Independent** of Fixes 2, 4, 5.
- **Coupled** with Fix 3 by topic, but not by code: this fix only edits the badge
  height/position; Fix 3 only edits the divider and row positions. Neither changes
  `container_height`, so they can land in either order.

---

## Commit write-up

```
fix(resource-box): clamp badge height to its container

A resource box's container height scales with its row count
(0.5 * num_rows + 0.35), so a single-row box is only 0.85" tall — shorter
than the default 1.1" badge. The badge was centered with
(container_height - badge_h) / 2, which goes negative when the badge is
taller than the container, pushing the badge above the box top and below
its bottom (visible on the "Getting started" slide's one-row box).

Clamp the badge to effective_badge_h = min(badge_h, container_height) and
center using that value, so the centering offset is never negative and the
badge always stays framed. Multi-row boxes are unaffected because their
container already exceeds the badge height.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
```
