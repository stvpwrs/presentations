---
title: Repro — Stray divider + bottom dead space
subtitle: Bug 3 reproduction
output: Bug03_Stray_Divider_Deadspace.pptx
text_model: gpt-5-mini
image_model: gpt-image-1.5
style:
  badge_width: 0.9
  badge_height: 1.1
  badge_font_size: 11
  badge_corner_radius: 12000
  badge_gradient_start: '#E3008C'
  badge_gradient_end: '#6B2FA0'
  badge_text_color: '#FFFFFF'
  box_background: '#E8E8E8'
  box_border_color: '#5B5FC7'
  box_corner_radius: 5000
  divider_color: '#D0D0D0'
  name_color: '#000000'
  name_font_size: 14
  url_color: '#0078D4'
  url_font_size: 14
---

## [resource-box] Getting started

**Subtitle**: Resources

**Box**: Two
- Row One | https://example.com/1
- Row Two | https://example.com/2

**Box**: Solo
- Lonely Row | https://example.com/solo

**Box**: Three
- Row A | https://example.com/a
- Row B | https://example.com/b
- Row C | https://example.com/c

**Notes**: Inspect the dividers. Every box gets exactly one divider at a fixed
0.38" offset: in "Two" and "Three" it falls between rows, but in the one-row
"Solo" box it becomes a stray underline with empty space below. Also note the
unused +0.35" bottom padding in every box — rows cluster at the top, leaving dead
space at the bottom.
