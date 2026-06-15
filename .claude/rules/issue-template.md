# Issue Template & Reporting Guide

This document is the standard for filing issues against **`ms-presentations`**. It captures
industry best practices for actionable bug reports and feature requests, and it requires a
**Minimal Reproducible Example (MRE)** for any behavioral bug.

> **Why this matters:** A good issue is reproducible, scoped, and self-contained. The single
> biggest predictor of how fast an issue gets resolved is whether a maintainer can reproduce it
> from the report alone. Time spent writing a tight MRE is time saved in back-and-forth.

---

## Before you file

Do these first — they resolve or de-duplicate a large share of reports:

- [ ] **Search existing issues** (open *and* closed) for your symptom or error message.
- [ ] **Upgrade to the latest version** (`pip install --upgrade ms-presentations`) and confirm the issue still occurs.
- [ ] **Re-read the relevant docs** ([README](../../README.md), [CONTRIBUTING](../../CONTRIBUTING.md)).
- [ ] **Reduce it to the smallest case** that still shows the problem (see the [MRE guide](#minimal-reproducible-example-mre) below).
- [ ] **Decide the issue type** — bug, feature request, docs, or question — and use the matching template.

One issue per report. If you have three problems, file three issues and cross-link them.

---

## Bug Report

```markdown
### Summary
<!-- One sentence: what is broken, in plain language. -->

### Severity / Impact
<!-- blocker | major | minor — and who/what it affects. -->

### Environment
- `ms-presentations` version:   <!-- pip show ms-presentations -->
- Python version:               <!-- python --version -->
- OS / version:                 <!-- e.g. Windows 11, macOS 14.5, Ubuntu 22.04 -->
- Install method:               <!-- pip from PyPI | from source | editable (-e) -->
- Relevant deps (if Azure path): azure-ai-inference / azure-identity / openai versions
- Azure / model config (if relevant): <!-- e.g. GPT-Image-1.5 deployment, AI Foundry endpoint — REDACT secrets -->

### Steps to Reproduce
1.
2.
3.

### Minimal Reproducible Example (MRE)
<!-- REQUIRED for behavioral bugs. See the MRE guide at the bottom of this file.
     Include the smallest .spec.md and command that triggers the bug. -->

​```markdown
<!-- paste the minimal .spec.md content here -->
​```

​```bash
# the exact command you ran
presentations minimal.spec.md
​```

### Expected Behavior
<!-- What you expected to happen. -->

### Actual Behavior
<!-- What actually happened. Include the FULL, unmodified error output / stack trace
     inside a code block. Do not paraphrase errors. -->

​```
<paste full traceback / output here>
​```

### Additional Context
<!-- Screenshots, the generated .pptx (if shareable), links to related issues,
     what you've already tried, any workaround you found. -->
```

### What makes a bug report good

- **Title** states the symptom, not the guess: *"`presentations` crashes on spec with empty notes block"*, not *"YAML parser bug"*.
- **Full, verbatim error output** in a code block — never a screenshot of text, never paraphrased.
- **Exact versions** of the package, Python, and OS. "Latest" is not a version.
- **One variable changed** — isolate whether it's the spec, the environment, or the Azure config.
- **Secrets redacted** — strip endpoints, keys, tokens, and connection strings before posting.

---

## Feature Request

```markdown
### Problem / Motivation
<!-- What are you trying to accomplish? What's painful today? Describe the problem,
     NOT a pre-chosen solution. -->

### Proposed Solution
<!-- What you'd like to see. Sketch the spec syntax, CLI flag, or API shape if relevant. -->

### Alternatives Considered
<!-- Other approaches and why they fall short. -->

### Scope & Impact
<!-- Who benefits? Is this backward compatible? Any migration concerns? -->

### Additional Context
<!-- Examples, prior art in other tools, mockups, links. -->
```

> Per [CONTRIBUTING.md](../../CONTRIBUTING.md): please open a feature-request issue **before**
> implementing a large feature, so we can confirm it fits the project. Small features can go
> straight to a PR.

---

## Documentation Issue

```markdown
### Location
<!-- File + section or URL of the docs that are wrong, unclear, or missing. -->

### What's wrong
<!-- The inaccuracy, ambiguity, or gap. -->

### Suggested fix
<!-- Proposed wording or the missing content, if you have it. -->
```

---

## Question / Support

GitHub issues are for **bugs and feature requests**. For usage questions, first check the
[README](../../README.md). If you still file an issue, label it clearly as a question and
include your environment and what you've already tried.

---

## Minimal Reproducible Example (MRE)

An MRE is the **smallest, self-contained, runnable** artifact that reproduces the problem.
For this project that almost always means a tiny `.spec.md` plus the command you ran.

### The three properties

| Property         | Meaning                                                                 |
|------------------|-------------------------------------------------------------------------|
| **Minimal**      | Delete everything not required to trigger the bug. Fewest slides, fewest fields. |
| **Reproducible** | It fails the same way every time, on a clean checkout / fresh install.  |
| **Complete**     | Anyone can copy-paste and run it without inventing missing pieces.       |

### How to build one

1. **Start from the failing case**, then remove pieces until the bug disappears — the last
   thing you removed is part of the cause. Add it back; that's your MRE.
2. **Strip unrelated content.** Remove slides, images, notes, and AI-enrichment options that
   aren't needed to trigger the failure.
3. **Inline or stub external inputs.** Replace real reference URLs, large images, and live
   Azure calls with the smallest stand-in that still reproduces the issue. If the bug *requires*
   an Azure model call, say so explicitly and describe the deployment/config (redacted).
4. **Make it copy-pasteable.** Provide the full `.spec.md` content and the exact command in
   fenced code blocks — not "my usual spec" or "a big deck".
5. **Verify on a clean environment.** Reproduce in a fresh virtualenv with a pinned version
   before posting:
   ```bash
   python -m venv .mre && . .mre/bin/activate   # Windows: .mre\Scripts\activate
   pip install ms-presentations==<the version you tested>
   presentations minimal.spec.md
   ```

### MRE checklist

- [ ] Smallest spec that still fails (ideally one or two slides).
- [ ] Exact command included.
- [ ] Full error output / traceback pasted verbatim.
- [ ] No secrets, internal URLs, or proprietary content.
- [ ] Reproduces on a fresh install of a stated version.
- [ ] No external files required that you didn't include or describe.

### Example

​```markdown
<!-- minimal.spec.md -->
---
title: Repro
---

# Slide one

Notes:
​```

​```bash
$ presentations minimal.spec.md
# → paste the full traceback that this produces
​```

> A report with a working MRE typically gets triaged in a fraction of the time of one without.
> If you can't produce an MRE, say so and explain what blocks it — partial repro steps are
> still better than none.
