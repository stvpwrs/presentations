# Fix 4 — Split (and warn) on a second slide header in one chunk

**File:** `src/presentations/spec_parser.py` · **Function:** `_split_slides_fence_aware`

## Approach

Make the parser resilient to a missing `---`. When a second `## [type]` header
appears inside a chunk that already has one, start a new chunk *and* print a
warning. This both prevents the silent slide drop and surfaces the authoring
typo. Fence-awareness is preserved (a `##` inside a code block is ignored because
the check is gated on `not in_fence`).

## The change

Add a module-level header pattern near the top of the file (after the imports):

```python
_HEADER_RE = re.compile(r"^##\s+\[\w[\w-]*\]")
```

Then replace `_split_slides_fence_aware` (`spec_parser.py:40-57`):

```python
# BEFORE
def _split_slides_fence_aware(body: str) -> list[str]:
    """Split *body* on ``\n---\n`` lines, ignoring fenced code blocks."""
    lines = body.split("\n")
    chunks: list[str] = []
    current: list[str] = []
    in_fence = False
    for line in lines:
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            current.append(line)
            continue
        if not in_fence and line.strip() == "---":
            chunks.append("\n".join(current))
            current = []
            continue
        current.append(line)
    chunks.append("\n".join(current))
    return chunks
```

```python
# AFTER
def _split_slides_fence_aware(body: str) -> list[str]:
    """Split *body* on ``\n---\n`` lines, ignoring fenced code blocks.

    Also splits defensively when a second ``## [type]`` header appears inside a
    chunk that already has one — this means the author forgot a ``---`` — so the
    second slide is not silently swallowed into the first slide's notes.
    """
    lines = body.split("\n")
    chunks: list[str] = []
    current: list[str] = []
    in_fence = False
    current_has_header = False
    for line in lines:
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            current.append(line)
            continue
        if not in_fence and line.strip() == "---":
            chunks.append("\n".join(current))
            current = []
            current_has_header = False
            continue
        if not in_fence and _HEADER_RE.match(line):
            if current_has_header:
                print(
                    "Warning: missing '---' separator before "
                    f"'{line.strip()}' — starting a new slide anyway."
                )
                chunks.append("\n".join(current))
                current = []
            current_has_header = True
        current.append(line)
    chunks.append("\n".join(current))
    return chunks
```

Now two adjacent `## [type]` headers with no `---` between them become two slides,
and the author sees a warning pointing at the offending header.

## Verification

Render [`spec.md`](spec.md). It defines three `## [content]` slides with the
separator before slide 3 intentionally missing. Before: 2 slides, no warning.
After: 3 slides, plus a `Warning: missing '---' separator before ...` line.

## Interactions

- **Fully independent** — different file (`spec_parser.py`) and no shared state with
  any other fix. Ship anytime.

---

## Commit write-up

```
fix(parser): split on a second slide header when '---' is missing

The parser split slides only on '---' lines. If an author omitted the
separator between two '## [type]' headers, both landed in one chunk;
_parse_slide matched only the first header and folded the second slide's
heading and bullets into the first slide's speaker notes — silently
dropping a slide (e.g. "Enterprise AI vs consumer AI" vanished from the
sample deck with no warning).

Detect a second '## [type]' header within a chunk that already has one,
start a new chunk there, and print a warning naming the header so the typo
is visible. Fenced code blocks are still ignored.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
```
