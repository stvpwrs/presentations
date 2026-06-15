# Bug 2 — Badge label overflow / mid-word wrapping (resource-box)

**Area:** resource-box · **Severity:** High

## Symptom

On a `resource-box` slide, badge labels longer than ~6 characters wrap awkwardly
inside the narrow badge:

- "Presentations" renders as "Presentat ions" (broken **mid-word**).
- "Build and Govern" stacks onto three cramped lines.
- Short labels ("Learn") look fine.

Evidence in the reviewed deck: **Slide 24** ("Getting started").

## Root cause

The badge is a fixed-width rounded rectangle with word-wrap enabled but **no
auto-fit** (`src/presentations/slides.py:443, 488-498`):

```python
badge_width, badge_height = Inches(badge_w), Inches(badge_h)   # badge_w default 0.9"
...
btf.word_wrap = True
bp.font.size = Pt(badge_font_sz)                                # default 11pt
```

At 0.9" wide / 11 pt there is room for only a few characters per line, and
python-pptx does not shrink text to fit. PowerPoint therefore hard-wraps the
label — including **mid-word** when a single word is wider than the box.

## Fix direction

Any of:

- **(a)** Enable auto-shrink: set
  `text_frame.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE` (or apply a smaller font
  for long labels). *Most robust for arbitrary label text.*
- **(b)** Widen the badge or scale `badge_w` to the longest label.
- **(c)** Reduce `badge_font_size` for labels over a length threshold.

## How to reproduce

Render [`spec.md`](spec.md) in this folder. It uses the default
`badge_width: 0.9` / `badge_font_size: 11` with deliberately long box labels
("Presentations", "Build and Govern"). The labels wrap mid-word inside the narrow
badge, while the short "Learn" label renders cleanly.
