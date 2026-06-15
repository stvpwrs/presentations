# Finding 6 — Missing images (context, NOT a layout bug)

**Area:** images · **Severity:** N/A

> ⚠️ This is **not a code defect**. It is included for completeness and labelled
> clearly so the empty right-hand space isn't mistaken for an alignment bug.

## Symptom

Every content slide renders with a large blank region on the right where an
illustration was specified, and the title slide's neural-network image is absent.

## Cause (expected behavior)

The spec references generated images under `output\images\*.png`, but those files
are not present in the repo. `_add_image` (`src/presentations/slides.py:45-60`)
checks `os.path.isfile(path)`, prints `Warning: image not found ... skipping`, and
returns.

This is **expected** when images haven't been generated (image generation
requires Azure AI access) — not an alignment bug.

Note: the text-positioning logic that reserves space for the image (e.g.
constraining content width when an image is present, `slides.py:143-147`) still
runs, which is why the bullet columns stay narrow even though no image appears.
That is correct behavior — the layout reserves the slot whether or not the asset
is rendered.

## "Fix"

No code change required. To populate the images, generate them via the Azure AI
endpoint (see the README's *Image Generation* section) so the referenced
`output\images\*.png` files exist at render time.

## How to reproduce

Render [`spec.md`](spec.md) in this folder. It references an image path that does
not exist. The build prints `Warning: image not found ... skipping`, the image
slot stays blank, and the bullet column remains narrow because the layout still
reserves space for the (absent) image.
