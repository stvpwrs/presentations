# Self-Contained MRE Guide (single-file `uv` script)

This rule explains how to package a **Minimal Reproducible Example (MRE)** for
**`ms-presentations`** as a *single, runnable Python file* using
[PEP 723 inline script metadata](https://peps.python.org/pep-0723/) and
[`uv`](https://docs.astral.sh/uv/). It complements [issue-template.md](issue-template.md),
which defines the MRE requirement; this document defines the **preferred form** of that MRE.

> **Why a single file?** The biggest cost in triaging a bug is the maintainer reassembling the
> reporter's setup — the right version, a spec file, the exact command. A PEP 723 `uv` script
> collapses all of that into one artifact: `uv run repro.py` resolves the pinned dependency into
> an ephemeral environment and runs the repro. Nothing to install, no venv to create, no separate
> spec file to save. If it fails on your machine, it fails on theirs the same way.

---

## When this form applies

A single-file `uv` MRE works for any bug reachable through the package's public surface **without
external services**:

- Spec parsing (`spec_parser`), rendering (`renderer`), slide builders (`slides`,
  `rich_layouts`), animations, styling, spec round-tripping (`spec_writer`).
- Anything you can trigger by feeding a `.spec.md` to the CLI.

**Why it works for this package:**

1. **The CLI is importable.** `presentations.cli.main` accepts an `argv` list
   (`main([spec_path, "-o", out])`), so the script calls it directly — no `subprocess`,
   no shell.
2. **Azure and the network are opt-in.** Enrichment short-circuits when a slide has no
   `**ContentUrls**`; image generation short-circuits when a slide has no `**ImagePrompt**`.
   A minimal spec with neither renders entirely locally (python-pptx + pyyaml + lxml) — no Azure
   credentials, no outbound calls.

### When it does *not* apply

If the bug lives in the Azure path — note enrichment via the text model, or image generation —
the script cannot be self-contained: it needs live credentials and a deployment. **Do not fake
it.** Fall back to the standard MRE in [issue-template.md](issue-template.md): the minimal spec,
the exact command, and a *redacted* description of the deployment/config. Say explicitly that an
Azure call is required to reproduce.

---

## The template

```python
# /// script
# requires-python = ">=3.10"
# dependencies = ["ms-presentations==0.1.6"]
# ///
"""Self-contained MRE for ms-presentations.

Run with:  uv run repro.py
No venv, no Azure, no network — `uv` resolves the pinned version into an
ephemeral environment and runs this file.

Bug: <one sentence — what's wrong>
Expected: <what should happen>
Actual:   <what happens instead — paste the traceback in the issue>
"""
import os
import tempfile

from presentations.cli import main

# The smallest spec that still triggers the bug. Edit THIS to reproduce.
SPEC = """\
---
title: Repro
output: repro.pptx
---

## [content] Slide one

- a bullet
- another bullet

**Notes**: hello
"""

with tempfile.TemporaryDirectory() as d:
    spec_path = os.path.join(d, "minimal.spec.md")
    with open(spec_path, "w", encoding="utf-8") as f:
        f.write(SPEC)

    main([spec_path, "-o", d])  # raises / misbehaves here when the bug is present

    out = os.path.join(d, "repro.pptx")
    print("rendered:", os.path.isfile(out))
```

---

## How to build one

1. **Pin the exact version.** Put the version you reproduced on in `dependencies`
   (`ms-presentations==<version>` — find it with `pip show ms-presentations`). "Latest" is not a
   version; an unpinned MRE rots.
2. **Shrink the spec.** Start from your failing spec and delete slides, fields, and directives
   until the bug disappears — then add back the last thing you removed. That residue is the MRE.
   Aim for one or two slides. Use the documented slide syntax (`## [type] Title`); a bare
   Markdown heading parses to zero slides and renders nothing.
3. **Keep it local.** Remove every `**ContentUrls**` and `**ImagePrompt**` directive unless the
   bug *is* in that path (in which case this form doesn't apply — see above).
4. **Drive it through `main()`.** Write the spec to a temp file and call
   `main([spec_path, "-o", out_dir])`. Pass any flag the repro needs the same way
   (`"--slides", "2-3"`, `"--refetch"`, …). Don't shell out.
5. **Let the bug surface naturally.** If it's a crash, `main()` raises and `uv run` prints the
   traceback — paste that verbatim into the issue. If it's wrong output, `print()` the specific
   observable (slide count, a saved path, a parsed value) so "expected vs. actual" is concrete.

---

## Verify before posting

Run it clean, exactly as the maintainer will:

```bash
uv run repro.py
```

`uv` reads the inline metadata, resolves the pinned `ms-presentations` (and its transitive deps)
into a throwaway environment, and executes the file. Confirm it reproduces with **no** local
`.env`, no Azure variables set, and from a directory with no `output/` folder.

> **Note:** `uv` pulls the full dependency tree (`azure-ai-inference`, `openai`,
> `azure-identity`, …) even though a local-only repro never exercises them — these are hard
> dependencies of the package, so there is no lighter install. The first run is a heavier
> resolve; this is expected, not a defect.

---

## Checklist

- [ ] One file, runnable with `uv run repro.py`.
- [ ] PEP 723 header pins an exact `ms-presentations==<version>`.
- [ ] Spec is inline (a `SPEC` string written to a temp file) — no external files.
- [ ] Smallest spec that still fails; uses `## [type] Title` syntax.
- [ ] No `**ContentUrls**` / `**ImagePrompt**` unless the bug requires them (then this form
      does not apply — use the standard MRE).
- [ ] Reproduces with no `.env` and no Azure env vars set.
- [ ] Bug/Expected/Actual stated in the module docstring; traceback or printed observable shows
      the failure.
- [ ] No secrets, internal URLs, or proprietary content.
