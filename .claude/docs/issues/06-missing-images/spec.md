---
title: Repro — Missing image (context, not a bug)
subtitle: Finding 6 reproduction
output: Bug06_Missing_Images.pptx
text_model: gpt-5-mini
image_model: gpt-image-1.5
---

## [content] Slide With A Missing Image

- This slide references an image that does not exist on disk.
- The build prints "Warning: image not found ... skipping".
- The image slot stays blank and this bullet column stays narrow.

**Image**: output\images\does_not_exist.png, 7.2, 1.5, 2.5, 2.5

**Notes**: Because the referenced image file is absent, `_add_image` warns and
returns without placing anything. The right-hand region is blank, but the
content-width constraint that reserves space for the image still applies — so the
bullets remain in a narrow column. This is expected behavior, not an alignment
bug. Generate the image (Azure AI) to fill the slot.
