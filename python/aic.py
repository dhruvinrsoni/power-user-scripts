#!/usr/bin/env python3
"""
Smart AI commit wrapper — auto-selects the cheapest available provider.

Priority order (most preferred → least preferred):
  1. Anthropic Claude  (ANTHROPIC_API_KEY)   → aica.py
  2. Google Gemini     (GOOGLE_API_KEY / GEMINI_API_KEY) → aicg.py
  3. OpenAI            (OPENAI_API_KEY)       → aico.py

This is a thin wrapper: it detects which key is set, prints one line
showing the chosen provider, then hands full control to the backend script.
All CLI flags (-a, -d, -r, -i, -p, -f, -m, -v, -w, FILES...) are forwarded
unchanged so every feature of the underlying script is available.
"""

import os
import sys
import subprocess

# ---------------------------------------------------------------------------
# Provider registry — ordered by preference (cheapest / most preferred first)
# ---------------------------------------------------------------------------
PROVIDERS = [
    {
        'name': 'Anthropic Claude',
        'script': 'aica.py',
        'env_vars': ['ANTHROPIC_API_KEY'],
        'icon': '🟠',
    },
    {
        'name': 'Google Gemini',
        'script': 'aicg.py',
        'env_vars': ['GOOGLE_API_KEY', 'GEMINI_API_KEY'],
        'icon': '🔵',
    },
    {
        'name': 'OpenAI',
        'script': 'aico.py',
        'env_vars': ['OPENAI_API_KEY'],
        'icon': '🟢',
    },
]

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def find_provider():
    """Walk PROVIDERS in priority order; return the first one with a key set."""
    for provider in PROVIDERS:
        for env_var in provider['env_vars']:
            if os.environ.get(env_var):
                return provider, env_var
    return None, None


def mask_key(value, show=4):
    """Return a masked version of a secret: first N + *** + last N chars."""
    if not value or len(value) <= show * 2:
        return '***'
    return f"{value[:show]}{'*' * 8}{value[-show:]}"


def print_status(msg):
    """Print to stderr so it doesn't pollute captured output in pipelines."""
    print(msg, file=sys.stderr, flush=True)


if __name__ == '__main__':
    # -----------------------------------------------------------------------
    # 1. Detect provider
    # -----------------------------------------------------------------------
    provider, key_var = find_provider()

    if not provider:
        print_status("\n🚨 No AI provider API key found.")
        print_status("   Set one of the following environment variables:")
        print_status("   • ANTHROPIC_API_KEY  — Anthropic Claude  (preferred)")
        print_status("   • GOOGLE_API_KEY or GEMINI_API_KEY  — Google Gemini")
        print_status("   • OPENAI_API_KEY  — OpenAI")
        print_status("\n   Priority: Anthropic > Google > OpenAI")
        sys.exit(1)

    script_path = os.path.join(SCRIPT_DIR, provider['script'])

    if not os.path.isfile(script_path):
        print_status(f"\n🚨 Backend script not found: {script_path}")
        print_status("   Make sure all ai*.py scripts are in the same directory as aic.py.")
        sys.exit(1)

    # -----------------------------------------------------------------------
    # 2. Announce which provider won (suppressed when -d/--debug not present
    #    to keep the output identical to calling the backend directly)
    # -----------------------------------------------------------------------
    debug_mode = '--debug' in sys.argv or '-v' in sys.argv
    if debug_mode:
        masked = mask_key(os.environ.get(key_var, ''))
        print_status(f"🤖 [aic] Provider  : {provider['icon']} {provider['name']}")
        print_status(f"🤖 [aic] Key var   : {key_var} = {masked}")
        print_status(f"🤖 [aic] Script    : {script_path}")
        print_status(f"🤖 [aic] Args      : {sys.argv[1:]}")
    else:
        print_status(f"🤖 via {provider['name']}")

    # -----------------------------------------------------------------------
    # 3. Hand off to the backend — inherit stdin/stdout/stderr so all
    #    interactive features (msvcrt, fzf, editor) work transparently.
    # -----------------------------------------------------------------------
    result = subprocess.run(
        [sys.executable, script_path] + sys.argv[1:]
    )
    sys.exit(result.returncode)
