# Python AI commit tools

A family of self-healing scripts that turn `git diff --cached` into a clean,
conventional commit message. Five backends — Anthropic Claude, Google
Gemini, OpenAI, Ollama (local), plus a smart wrapper that picks the
cheapest available — share one CLI surface so flags work the same
everywhere.

For a side-by-side comparison of providers, flags, costs, and setup, see
the bundled comparison guide:

??? note "AI commit comparison guide (full text)"

    --8<-- "_imported/ai-commit-comparison.md"

---

## The smart wrapper

### aic.py

::: aic
    options:
      show_source: false

---

## Provider backends

### aica.py — Anthropic Claude

::: aica
    options:
      show_source: false

### aicg.py — Google Gemini

::: aicg
    options:
      show_source: false

### aico.py — OpenAI

::: aico
    options:
      show_source: false

### aicl.py — Ollama (local)

::: aicl
    options:
      show_source: false

---

## Companion utilities

### chat.py

::: chat
    options:
      show_source: false

### aipr.py

::: aipr
    options:
      show_source: false

### dependency_manager.py

::: dependency_manager
    options:
      show_source: false
