# Layout & Alignment Review

A review of the rendered test deck
(`test_examples/output/Your_AI_Productivity_Boost/Slide*.PNG`, 25 slides)
against the rendering code, looking for alignment and layout bugs.

**Status: findings only — no code has been changed.** Each finding lists the
visible symptom (with slide evidence), the root cause (`file:line`), and a
suggested fix direction. Severity is a rough judgment of visual/functional
impact.

| # | Finding | Area | Severity |
|---|---------|------|----------|
| 1 | Badge taller than its container | resource-box | High |
| 2 | Badge label overflow / mid-word wrapping | resource-box | High |
| 3 | Stray divider + bottom dead space | resource-box | Medium |
| 4 | Silent slide drop on missing `---` | parser | High |
| 5 | Latent 4:3-vs-16:9 geometry mismatch | renderer / core builders | Medium (latent) |
| 6 | Missing images (context, not a bug) | images | N/A |

---

## Finding 1 — Badge can be taller than its container (resource-box)

**Symptom.** On **Slide 24** ("Getting started"), the third box ("Presentations")
has a single row, and its gradient badge is visibly taller than the box —
sticking out above and below the rounded rectangle. The two-row boxes above it
look fine.

**Root cause.** In `add_resource_box_slide`:

- Container height grows with the row count (slides.py:353):
  ```python
  container_height = Inches(0.5 * num_rows + 0.35)
  ```
  → 1 row = **0.85"**, 2 rows = 1.35", 3 rows = 1.85".
- Badge height is a fixed style value, default **1.1"** (`badge_height`,
  style.py:13 / spec front matter `badge_height: 1.1`).
- Badge vertical position centers the badge in the container (slides.py:444):
  ```python
  badge_y = box_top + Inches((container_height / Inches(1) - badge_h) / 2)
  ```
  When `badge_h (1.1) > container_height (0.85)`, the offset is **negative**
  (`(0.85 - 1.1)/2 = -0.125"`), so the badge starts above the box top and
  extends below the box bottom.

**Fix direction.** Either clamp the badge height to the container
(`badge_h = min(badge_h, container_height)`), or enforce a minimum container
height of at least `badge_h` (e.g. `container_height = max(0.5*num_rows + 0.35,
badge_h + 0.1)`). The latter keeps the badge fully framed and also removes the
overflow for any future 1-row box.

---

## Finding 2 — Badge label overflow / mid-word wrapping (resource-box)

**Symptom.** On **Slide 24**, badge labels longer than ~6 characters wrap
awkwardly inside the narrow badge: "Presentations" renders as "Presentat ions"
(broken mid-word) and "Build and Govern" stacks onto three cramped lines. Short
labels ("Learn") look fine.

**Root cause.** The badge is a fixed-width rounded rectangle with word-wrap on
but no auto-fit (slides.py:443, 488-498):

```python
badge_width, badge_height = Inches(badge_w), Inches(badge_h)   # badge_w default 0.9"
...
btf.word_wrap = True
bp.font.size = Pt(badge_font_sz)                                # default 11pt
```

At 0.9" wide / 11 pt there is room for only a few characters per line, and
python-pptx does not shrink text to fit, so PowerPoint hard-wraps the label
(including mid-word when a single word is wider than the box).

**Fix direction.** Any of: (a) enable auto-shrink (`text_frame.auto_size =
MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE` / set a smaller font for long labels), (b) widen
the badge or scale `badge_w` to the longest label, or (c) reduce
`badge_font_size` for labels over a length threshold. Option (a) is the most
robust for arbitrary label text.

---

## Finding 3 — Stray single divider + bottom dead space (resource-box)

**Symptom.** On **Slide 24**, every box draws exactly one horizontal divider line
near its top. In the two-row boxes it sits between the two rows (reasonable), but
in the one-row "Presentations" box it becomes a stray underline beneath the lone
row, with empty space below it. All boxes also have noticeable empty space at the
bottom because the rows cluster near the top.

**Root cause.** Two separate decisions:

- The divider is drawn **once** at a fixed offset regardless of row count
  (slides.py:404-411):
  ```python
  div_y = box_top + Inches(0.38)
  ```
- Rows are **top-anchored** starting at `box_top + 0.08`, each 0.5" apart
  (slides.py:415), while the container height is `0.5*num_rows + 0.35`. The extra
  0.35" of container height is never used, so it shows as dead space at the
  bottom. For a 2-row box: rows occupy ~0.08"–0.93" of a 1.35" container.

**Fix direction.** Decide what the divider means. If it is a row separator, draw
one between each adjacent pair of rows (skip when `num_rows == 1`). If it is a
header rule, the layout needs an actual header row. Separately, either reduce the
trailing `+ 0.35` padding or vertically center the row block within the container
so boxes don't look bottom-heavy with whitespace.

---

## Finding 4 — Silent slide drop on a missing `---` separator (parser)

**Symptom.** The spec defines **26** slides (`## [type]` headers) but the deck
rendered only **25** PNGs. The slide titled **"Enterprise AI vs consumer AI"** is
missing entirely — and there was no warning. (Confirmed: **Slide 10** is "Where
AI helps across departments", which in the spec comes *after* "Enterprise AI vs
consumer AI".)

**Root cause.** In the spec, the "AI Myths vs Reality" block is **not** followed
by a `---` separator before "Enterprise AI vs consumer AI"
(`test_examples/ai_productivity_boost.spec.md`, around lines 273–275):

```markdown
... real value.                          ← end of AI Myths notes

## [content] Enterprise AI vs consumer AI    ← no `---` above this line
```

The parser splits slides **only** on `---` lines
(`_split_slides_fence_aware`, spec_parser.py:40-57). With no separator, both
`##` headers land in one chunk. `_parse_slide` (spec_parser.py:81) matches the
**first** header (`two-column` "AI Myths vs Reality") and treats everything after
the first `**Notes**:` as that slide's notes — so the entire "Enterprise AI vs
consumer AI" heading and its bullets get swallowed into the Myths slide's speaker
notes and never become their own slide.

This is partly a spec-authoring error (the missing `---`), but the parser turns a
small typo into a silently dropped slide, which is the more serious problem.

**Fix direction.** Make the parser resilient: additionally split a chunk when a
second `## [type]` header appears mid-chunk, **or** at minimum emit a warning
when a single chunk contains more than one `## [type]` header (so the author
notices). Either approach would have surfaced this immediately.

---

## Finding 5 — Latent 4:3-vs-16:9 geometry mismatch (renderer / core builders)

**Symptom.** Not visible in this test deck (it uses only core 4:3 layouts, so the
canvas stayed 10" × 7.5" and all core defaults lined up). It is a latent trap: a
deck that mixes a `content`/`two-column`/`resource-box` slide with **any** rich
layout would render the core slides with a large empty right margin and
off-center titles.

**Root cause.** `renderer.render` flips the whole deck to 16:9 (13.333" wide) if
*any* slide uses a rich layout type (renderer.py:105-114):

```python
_RICH_TYPES = {"hero-title", "stat-cards", "status-table",
               "stack-table", "priority-table", "timeline-cards"}
want_widescreen = (size_pref == "widescreen"
                   or (size_pref == "" and any(s["type"] in _RICH_TYPES for s in slides)))
```

But the core builders' default positions are hard-coded for a 10" slide
(slides.py:112-124):

```python
_CONTENT_DEFAULTS = {
    "title":   {"left": 0.5, "top": 0.2, "width": 8.5, "height": 0.8},
    "content": {"left": 0.5, "top": 1.2, "width": 6.5, "height": 5.5},
}
_TWO_COL_DEFAULTS = { "right": {"left": 5.0, ...}, ... }
```

On a 13.333" canvas an 8.5"-wide title no longer spans the slide and a content
block ending at 7.0" leaves ~6" of empty space on the right. The rich builders,
meanwhile, hard-code 13.333"-based literals (rich_layouts.py:37 and throughout),
so the two layout families only look correct on their own canvas size.

**Fix direction.** Derive the core defaults from `prs.slide_width` (as
`add_resource_box_slide` already does with `slide_w = prs.slide_width`) so they
scale to whichever canvas is active, or explicitly document that core and rich
layouts must not be mixed in one deck. See `ARCHITECTURE.md` §4 ("two coexisting
coordinate worlds").

---

## Finding 6 — Missing images (context, not a layout bug)

**Symptom.** Every content slide renders with a large blank region on the right
where an illustration was specified, and the title slide's neural-network image
is absent.

**Cause.** The spec references generated images under `output\images\*.png`, but
those files are not present in the repo. `_add_image` (slides.py:45-60) checks
`os.path.isfile(path)`, prints `Warning: image not found ... skipping`, and
returns. This is expected behavior when images haven't been generated (it
requires Azure AI access), **not** an alignment bug — noted here so the empty
right-hand space isn't mistaken for one. The text-positioning logic that reserves
space for the image (e.g. constraining content width when an image is present,
slides.py:143-147) still runs, which is why the bullet columns stay narrow even
though no image appears.

---

## Summary

The highest-impact, self-contained fixes are findings **1–3** (all in
`add_resource_box_slide`) and finding **4** (parser robustness). Finding **5** is
a latent architectural issue worth addressing before anyone builds a mixed-layout
deck. Finding **6** is environmental, not a code defect. None of these have been
changed in this pass — see each "Fix direction" for the recommended approach.
