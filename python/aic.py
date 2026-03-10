#!/usr/bin/env python3
"""
Smart AI commit wrapper — auto-selects the cheapest available provider.

Priority order (most preferred → least preferred):
  0. Ollama (local)    (auto-detected at localhost:11434) → aicl.py
  1. Anthropic Claude  (ANTHROPIC_API_KEY)   → aica.py
  2. Google Gemini     (GOOGLE_API_KEY / GEMINI_API_KEY) → aicg.py
  3. OpenAI            (OPENAI_API_KEY)       → aico.py

This is a thin wrapper: it detects which provider is available, prints one
line showing the chosen provider, then hands full control to the backend script.
All CLI flags (-a, -d, -r, -i, -p, -f, -m, -v, -w, FILES...) are forwarded
unchanged so every feature of the underlying script is available.

Override flags (consumed by this wrapper, NOT forwarded to the backend):
  -c, --cloud   Skip Ollama even when it is running; use best available cloud
                provider instead (Anthropic → Gemini → OpenAI).
"""

import os
import sys
import subprocess
import time
import urllib.request
import urllib.error

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


def is_ollama_available(base_url="http://localhost:11434", timeout=2):
    """
    Probes GET /api/tags to check if Ollama is running.
    Uses only stdlib (urllib) — no extra dependencies.
    2-second timeout: localhost should respond in milliseconds if up.
    Returns (True, None) on success, or (False, reason_string) on failure.
    """
    try:
        req = urllib.request.urlopen(f"{base_url}/api/tags", timeout=timeout)
        return (True, None) if req.status == 200 else (False, f"Ollama returned HTTP {req.status}")
    except urllib.error.HTTPError as e:
        return (False, f"Ollama returned HTTP {e.code}")
    except urllib.error.URLError as e:
        if isinstance(e.reason, ConnectionRefusedError):
            return (False, "Connection refused (Ollama not running?)")
        if isinstance(e.reason, (TimeoutError, OSError)) and 'timed out' in str(e.reason):
            return (False, f"Connection timed out after {timeout}s (Ollama unresponsive?)")
        return (False, f"Network error: {e.reason}")
    except Exception as e:
        return (False, f"Unexpected error: {e}")


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


def ollama_retry_or_exit(ollama_reason, ollama_base_url, auto_retries=1):
    """
    Show why Ollama failed, auto-retry once, then exit.
    No interactive prompt — git alias shells freeze on input().

    Returns True if Ollama came back (caller should re-run), False to exit.
    """
    print_status(f"\n⚠️  Ollama: {ollama_reason}")

    # --- Auto-retry phase (non-interactive, safe everywhere) ---
    for attempt in range(1, auto_retries + 1):
        print_status(f"🔄 Retrying Ollama... (attempt {attempt})")
        time.sleep(2)
        ok, reason = is_ollama_available(base_url=ollama_base_url)
        if ok:
            print_status("✅ Ollama is back!")
            return True
        ollama_reason = reason
        print_status(f"⚠️  Ollama: {ollama_reason}")

    # --- No interactive prompt — just show guidance and exit ---
    print_status("   Auto-retry exhausted.")
    print_status("   To use cloud instead: aic --cloud  (or aic -c)")
    print_status("   To fix Ollama: ollama serve  (then re-run aic)")
    return False


def run_ollama(forward_args, ollama_base_url, debug_mode):
    """Launch aicl.py and return the subprocess result."""
    script_path = os.path.join(SCRIPT_DIR, 'aicl.py')
    if not os.path.isfile(script_path):
        print_status(f"\n🚨 Backend script not found: {script_path}")
        print_status("   Make sure aicl.py is in the same directory as aic.py.")
        sys.exit(1)
    if debug_mode:
        print_status(f"🤖 [aic] Provider  : 🟣 Ollama (local)")
        print_status(f"🤖 [aic] Endpoint  : {ollama_base_url}")
        print_status(f"🤖 [aic] Script    : {script_path}")
        print_status(f"🤖 [aic] Args      : {forward_args}")
    else:
        print_status(f"🤖 via Ollama (local)")
    return subprocess.run([sys.executable, script_path] + forward_args)


if __name__ == '__main__':
    debug_mode = '--debug' in sys.argv or '-v' in sys.argv

    # -----------------------------------------------------------------------
    # Detect and strip wrapper-only flags before building the forwarded args.
    # These flags are meaningful only to aic.py; backends must never see them.
    # -----------------------------------------------------------------------
    # Detect and strip -c/--cloud even when bundled with other flags (e.g. -cap → -ap).
    cloud_mode = False
    forward_args = []
    for _arg in sys.argv[1:]:
        if _arg in ('--cloud', '-c'):
            # Standalone: -c  or  --cloud
            cloud_mode = True
        elif _arg.startswith('-') and not _arg.startswith('--') and 'c' in _arg[1:]:
            # Bundled: -cap, -ac, -vc, etc. — strip the 'c' and keep the rest.
            cloud_mode = True
            _stripped = _arg.replace('c', '', 1)   # -cap → -ap, -ac → -a
            if len(_stripped) > 1:                  # more than just a bare '-' remains
                forward_args.append(_stripped)
        else:
            forward_args.append(_arg)

    # -----------------------------------------------------------------------
    # Priority 0: Ollama (local, free, always preferred when running)
    # Skipped when --cloud / -c is passed.
    # -----------------------------------------------------------------------
    ollama_base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_ok, ollama_reason = is_ollama_available(base_url=ollama_base_url)
    provider, key_var = None, None

    if not cloud_mode:
        # --- Ollama not reachable: auto-retry once, then exit ---
        if not ollama_ok:
            came_back = ollama_retry_or_exit(ollama_reason, ollama_base_url)
            if came_back:
                ollama_ok = True
            else:
                sys.exit(1)

        # --- Ollama reachable: run aicl.py ---
        if ollama_ok:
            result = run_ollama(forward_args, ollama_base_url, debug_mode)
            if result.returncode == 0:
                sys.exit(0)

            # aicl.py failed — auto-retry once, then exit
            came_back = ollama_retry_or_exit(
                "Local generation failed (all models exhausted or error)",
                ollama_base_url,
            )
            if came_back:
                result = run_ollama(forward_args, ollama_base_url, debug_mode)
                sys.exit(result.returncode)
            else:
                sys.exit(result.returncode)

    # -----------------------------------------------------------------------
    # Priority 1-3: Cloud providers — detect by API key
    # -----------------------------------------------------------------------
    if cloud_mode:
        # User explicitly wants cloud — no prompt needed
        provider, key_var = find_provider()

    if not provider:
        print_status("\n🚨 No AI provider available.")
        if cloud_mode:
            print_status("   --cloud mode is active (Ollama bypassed).")
        elif ollama_reason:
            print_status(f"   Ollama: {ollama_reason}")
        print_status("   Option 0 (free, local): start Ollama — no API key needed")
        print_status("     • Run: ollama serve  (or launch the Ollama app)")
        print_status("   Set one of the following environment variables:")
        print_status("   • ANTHROPIC_API_KEY  — Anthropic Claude")
        print_status("   • GOOGLE_API_KEY or GEMINI_API_KEY  — Google Gemini")
        print_status("   • OPENAI_API_KEY  — OpenAI")
        print_status("\n   Full priority: Ollama (local) > Anthropic > Google > OpenAI")
        sys.exit(1)

    script_path = os.path.join(SCRIPT_DIR, provider['script'])

    if not os.path.isfile(script_path):
        print_status(f"\n🚨 Backend script not found: {script_path}")
        print_status("   Make sure all ai*.py scripts are in the same directory as aic.py.")
        sys.exit(1)

    # -----------------------------------------------------------------------
    # Announce which provider won (suppressed when -d/--debug not present
    # to keep the output identical to calling the backend directly)
    # -----------------------------------------------------------------------
    if debug_mode:
        masked = mask_key(os.environ.get(key_var, ''))
        print_status(f"🤖 [aic] Provider  : {provider['icon']} {provider['name']}")
        print_status(f"🤖 [aic] Key var   : {key_var} = {masked}")
        print_status(f"🤖 [aic] Script    : {script_path}")
        print_status(f"🤖 [aic] Cloud mode: {cloud_mode}")
        print_status(f"🤖 [aic] Args      : {forward_args}")
    else:
        cloud_tag = " (--cloud)" if cloud_mode else ""
        print_status(f"🤖 via {provider['name']}{cloud_tag}")

    # -----------------------------------------------------------------------
    # Hand off to the backend — inherit stdin/stdout/stderr so all
    # interactive features (msvcrt, fzf, editor) work transparently.
    # -----------------------------------------------------------------------
    result = subprocess.run(
        [sys.executable, script_path] + forward_args
    )
    sys.exit(result.returncode)
