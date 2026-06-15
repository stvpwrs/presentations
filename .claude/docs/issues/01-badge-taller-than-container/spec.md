---
title: Repro — Badge taller than container
subtitle: Bug 1 reproduction
output: Bug01_Badge_Taller_Than_Container.pptx
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

**Box**: Learn
- One Row Only | https://example.com/one

**Box**: Build
- Also One Row | https://example.com/two

**Box**: Reference
- First Row | https://example.com/a
- Second Row | https://example.com/b

**Notes**: The two single-row boxes ("Learn", "Build") have a 0.85" container,
which is shorter than the default 1.1" badge — so their badges overflow the box
top and bottom. The two-row "Reference" box (1.35" container) frames its badge
correctly. Compare the badges to confirm the overflow.
