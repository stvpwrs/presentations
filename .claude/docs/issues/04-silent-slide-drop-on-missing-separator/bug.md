# Bug 4 — Silent slide drop on a missing `---` separator (parser)

**Area:** parser · **Severity:** High

## Symptom

A spec that defines N slides (`## [type]` headers) renders only N−1 slides — with
**no warning**. One whole slide is silently dropped, and its content is swallowed
into the previous slide's speaker notes.

Evidence in the reviewed deck: the spec defines **26** slides but the deck
rendered only **25** PNGs. The slide titled **"Enterprise AI vs consumer AI"** is
missing entirely; **Slide 10** is "Where AI helps across departments", which in
the spec comes *after* the missing slide.

## Root cause

In the spec, the "AI Myths vs Reality" block is **not** followed by a `---`
separator before "Enterprise AI vs consumer AI"
(`test_examples/ai_productivity_boost.spec.md`, around lines 273–275):

```markdown
... real value.                              ← end of AI Myths notes

## [content] Enterprise AI vs consumer AI    ← no `---` above this line
```

The parser splits slides **only** on `---` lines
(`_split_slides_fence_aware`, `src/presentations/spec_parser.py:40-57`). With no
separator, both `##` headers land in one chunk. `_parse_slide`
(`spec_parser.py:81`) matches the **first** header (the `two-column` "AI Myths vs
Reality") and treats everything after the first `**Notes**:` as that slide's
notes — so the entire "Enterprise AI vs consumer AI" heading and its bullets get
absorbed into the Myths slide's speaker notes and never become their own slide.

This is partly a spec-authoring error (the missing `---`), but the parser turns a
small typo into a **silently** dropped slide, which is the more serious problem.

## Fix direction

Make the parser resilient:

- Additionally split a chunk when a second `## [type]` header appears mid-chunk, **or**
- At minimum, emit a warning when a single chunk contains more than one `## [type]`
  header (so the author notices).

Either approach would have surfaced this immediately.

## How to reproduce

Render [`spec.md`](spec.md) in this folder. It defines **three** `## [content]`
slides, but the separator between slide 2 and slide 3 is intentionally missing.
The rendered deck contains only **two** slides; the third slide's heading and
bullets are swallowed into slide 2's speaker notes, with no warning emitted.
