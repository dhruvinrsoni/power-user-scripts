# Python AI commit tools

A single self-healing script (`aic.py`) that turns `git diff --cached` into a
clean, conventional commit message. One CLI, four providers — Anthropic Claude,
Google Gemini, OpenAI, and Ollama (local) — selected by auto-detection (Ollama →
Anthropic → Gemini → OpenAI) or forced with `--provider`. Flags work the same for
every provider.

For a side-by-side comparison of providers, flags, costs, and setup, see
the bundled comparison guide:

??? note "AI commit comparison guide (full text)"

    --8<-- "_imported/ai-commit-comparison.md"

---

## The tool

### aic.py

`git aic` auto-detects; `git aica` / `git aicg` / `git aico` / `git aicl` are
thin aliases that pin Anthropic / Gemini / OpenAI / Ollama via `--provider`. The
provider classes (`AnthropicProvider`, `GeminiProvider`, `OpenAIProvider`,
`OllamaProvider`) all live inside this one module.

::: aic
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
