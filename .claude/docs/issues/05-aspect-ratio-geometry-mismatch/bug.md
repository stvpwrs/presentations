# Bug 5 — Latent 4:3-vs-16:9 geometry mismatch (renderer / core builders)

**Area:** renderer / core builders · **Severity:** Medium (latent)

## Symptom

Not visible in the reviewed test deck — it uses only core 4:3 layouts, so the
canvas stayed 10" × 7.5" and all core defaults lined up. It is a **latent trap**:
a deck that mixes a `content` / `two-column` / `resource-box` slide with **any**
rich layout would render the core slides with a large empty right margin and
off-center titles.

## Root cause

`renderer.render` flips the **whole deck** to 16:9 (13.333" wide) if *any* slide
uses a rich layout type (`src/presentations/renderer.py:105-114`):

```python
_RICH_TYPES = {"hero-title", "stat-cards", "status-table",
               "stack-table", "priority-table", "timeline-cards"}
want_widescreen = (size_pref == "widescreen"
                   or (size_pref == "" and any(s["type"] in _RICH_TYPES for s in slides)))
```

But the core builders' default positions are hard-coded for a **10"** slide
(`src/presentations/slides.py:112-124`):

```python
_CONTENT_DEFAULTS = {
    "title":   {"left": 0.5, "top": 0.2, "width": 8.5, "height": 0.8},
    "content": {"left": 0.5, "top": 1.2, "width": 6.5, "height": 5.5},
}
_TWO_COL_DEFAULTS = { "right": {"left": 5.0, ...}, ... }
```

On a 13.333" canvas an 8.5"-wide title no longer spans the slide, and a content
block ending at 7.0" leaves ~6" of empty space on the right. The rich builders,
meanwhile, hard-code 13.333"-based literals
(`src/presentations/rich_layouts.py:37` and throughout), so the two layout
families only look correct on their **own** canvas size.

## Fix direction

- Derive the core defaults from `prs.slide_width` (as `add_resource_box_slide`
  already does with `slide_w = prs.slide_width`) so they scale to whichever canvas
  is active, **or**
- Explicitly document that core and rich layouts must not be mixed in one deck.

See `docs/ARCHITECTURE.md` §4 ("two coexisting coordinate worlds").

## How to reproduce

Render [`spec.md`](spec.md) in this folder. It mixes a core `content` slide with a
rich `hero-title` slide. The presence of the rich slide flips the deck to 16:9
(13.333" wide), so the core `content` slide's 8.5"-wide title and 6.5"-wide body
— sized for a 10" canvas — sit against a large empty right margin instead of
spanning the slide.
