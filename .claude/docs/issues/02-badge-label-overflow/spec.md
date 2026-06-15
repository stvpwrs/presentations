---
title: Repro — Badge label overflow / mid-word wrap
subtitle: Bug 2 reproduction
output: Bug02_Badge_Label_Overflow.pptx
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
- Microsoft AI | https://learn.microsoft.com/ai/
- AI Playbook | https://learn.microsoft.com/ai/playbook/

**Box**: Build and Govern
- Azure AI Services | https://learn.microsoft.com/azure/ai-services/
- Responsible AI | https://www.microsoft.com/ai/responsible-ai

**Box**: Presentations
- Presentations Repo | https://github.com/microsoft/presentations
- Samples | https://github.com/microsoft/presentations/samples

**Notes**: With the default 0.9"-wide badge at 11 pt and no auto-fit, the long
labels "Presentations" (wraps mid-word to "Presentat ions") and "Build and
Govern" (three cramped lines) overflow. The short "Learn" label renders fine —
showing the problem is label length, not the box itself.
