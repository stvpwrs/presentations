---
title: Repro — Silent slide drop on missing separator
subtitle: Bug 4 reproduction
output: Bug04_Silent_Slide_Drop.pptx
text_model: gpt-5-mini
image_model: gpt-image-1.5
---

## [content] Slide One (renders)

- This slide is correctly separated by a --- below.
- It renders as expected.

**Notes**: First slide. Properly terminated by a separator.

---

## [content] Slide Two (absorbs slide three)

- This slide IS followed by a `## [content]` header below,
- but there is NO `---` separator between them.

**Notes**: This is slide two's notes. Because the separator before "Slide Three"
is missing, everything below — including the entire "Slide Three" heading and its
bullets — gets swallowed into THIS slide's speaker notes.

## [content] Slide Three (silently dropped)

- These bullets never become their own slide.
- No warning is emitted about the dropped slide.

**Notes**: This third slide is silently lost. Expected: 3 slides. Actual: 2.
