# Fix 5 — Scale core layout defaults to the active canvas width

**File:** `src/presentations/slides.py` · **Functions:** `add_content_slide`,
`add_two_column_slide`, `add_section_header_slide`

## Approach

The core builders' default positions are authored for a 10"-wide (4:3) canvas, but
the renderer flips the deck to 13.333" (16:9) whenever any rich layout is present.
Derive the defaults from `prs.slide_width` so horizontal values scale to whichever
canvas is active. Only **horizontal** values (`left`, `width`) are scaled — both
canvases are 7.5" tall, so `top`/`height` must stay as-is. On a 4:3 deck the scale
factor is exactly 1.0, so existing decks are byte-for-byte unchanged.

## The change

### 1. Add a scaling helper (near the defaults at `slides.py:111-124`)

```python
_BASE_SLIDE_W = 10.0  # inches — the canvas width the core defaults were authored for


def _scaled_defaults(defaults: dict, slide_w_in: float) -> dict:
    """Scale horizontal (left/width) default values from the 10" authoring canvas
    to the active canvas, so core layouts fill a 16:9 deck instead of leaving a
    large right-hand gap. Vertical values are unchanged (height is constant at
    7.5" across 4:3 and 16:9)."""
    factor = slide_w_in / _BASE_SLIDE_W
    out: dict = {}
    for key, pos in defaults.items():
        scaled = dict(pos)
        if "left" in scaled:
            scaled["left"] *= factor
        if "width" in scaled:
            scaled["width"] *= factor
        out[key] = scaled
    return out
```

### 2. Use it in `add_content_slide` (`slides.py:139-141`)

```python
# BEFORE
_apply_position(slide.shapes.title, positions.get("title") or _CONTENT_DEFAULTS["title"])
body_ph = slide.shapes.placeholders[1]
content_pos = positions.get("content") or _CONTENT_DEFAULTS["content"].copy()
```

```python
# AFTER
defaults = _scaled_defaults(_CONTENT_DEFAULTS, prs.slide_width.inches)
_apply_position(slide.shapes.title, positions.get("title") or defaults["title"])
body_ph = slide.shapes.placeholders[1]
content_pos = positions.get("content") or dict(defaults["content"])
```

### 3. Use it in `add_two_column_slide` (`slides.py:199-212`)

```python
# BEFORE
_apply_position(slide.shapes.title, positions.get("title") or _TWO_COL_DEFAULTS["title"])
...
_apply_position(left_placeholder, positions.get("left") or _TWO_COL_DEFAULTS["left"])
...
_apply_position(right_placeholder, positions.get("right") or _TWO_COL_DEFAULTS["right"])
```

```python
# AFTER
defaults = _scaled_defaults(_TWO_COL_DEFAULTS, prs.slide_width.inches)
_apply_position(slide.shapes.title, positions.get("title") or defaults["title"])
...
_apply_position(left_placeholder, positions.get("left") or defaults["left"])
...
_apply_position(right_placeholder, positions.get("right") or defaults["right"])
```

### 4. (Optional, for consistency) `add_section_header_slide` (`slides.py:174-179`)

```python
defaults = _scaled_defaults(_SECTION_DEFAULTS, prs.slide_width.inches)
_apply_position(slide.shapes.title, positions.get("title") or defaults["title"])
...
_apply_position(slide.placeholders[1], positions.get("subtitle") or defaults["subtitle"])
```

> Note: the image-overlap guard at `slides.py:144-146` keys off `content_pos["left"]`
> and the image's `left`. Because the content left now scales too, the guard keeps
> working on both canvas sizes.

## Verification

Render [`spec.md`](spec.md) (mixes a `hero-title` rich slide with a `content` core
slide → forces 16:9). Before: the content slide's title/body hug the left with a
~6" right gap. After: title and body span the 13.333" canvas. Re-render a pure 4:3
deck to confirm it is unchanged (scale factor 1.0).

## Interactions

- **Independent** of Fixes 1–4. It touches the core content/two-column/section
  builders and a new helper; the resource-box builder already derives from
  `prs.slide_width` and is untouched.
- This is the latent finding — worth landing before anyone authors a mixed-layout
  deck, but not urgent for the current 4:3-only decks.

---

## Commit write-up

```
fix(renderer): scale core layout defaults to the active canvas width

The renderer flips the whole deck to 16:9 (13.333") when any rich layout is
present, but the content/two-column/section builders hard-code default
positions for a 10" (4:3) canvas. On a widescreen deck this left core
slides with an off-center title and ~6" of empty space on the right.

Derive the core defaults from prs.slide_width via a _scaled_defaults helper
that scales only horizontal (left/width) values — height is constant at
7.5" across both aspect ratios. The scale factor is exactly 1.0 on a 4:3
deck, so existing 4:3 output is unchanged; mixed-layout decks now fill the
widescreen canvas. The resource-box builder already scaled off slide_width
and is untouched.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
```
