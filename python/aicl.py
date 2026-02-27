#!/usr/bin/env python3
"""
AI-powered Git commit message generator using Ollama (local).
Generates conventional commit messages using locally-running Ollama models.
No API key required — uses the Ollama REST API at localhost:11434.

Smart RAM management:
  - num_ctx is capped (default 8192) to prevent models inflating to 30+ GB RAM
  - PREFERRED_MODELS ordered small→large so lighter models are tried first
  - Automatic fallback: timeout/crash/OOM → retries with next smaller model
"""

import sys
import os
import subprocess

# --- 🛡️ Self-Healing Header ---
try:
    import dependency_manager
except ImportError:
    print("🚨 Critical: 'dependency_manager.py' is missing from this folder.")
    sys.exit(1)

dependency_manager.require(["requests"])

# --- 🚀 Normal Imports (Guaranteed to work now) ---
import requests
import warnings
import argparse
import msvcrt  # For single-character input on Windows
import tempfile  # For securely creating temporary files

# --- Configuration: Suppress SSL Warnings ---
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ---------------------------------------------------------------------------
# Configuration: Ollama endpoint
# Override any of these via environment variables if needed.
# ---------------------------------------------------------------------------
OLLAMA_BASE_URL  = os.environ.get("OLLAMA_BASE_URL",    "http://localhost:11434")

# Context window cap — CRITICAL for RAM control.
# llama3.1:8b with default 131072 ctx → ~31 GB RAM.
# Same model with 8192 ctx → ~6-7 GB RAM.  For commit messages 8192 is plenty.
OLLAMA_NUM_CTX     = int(os.environ.get("OLLAMA_NUM_CTX",     "8192"))

# Max tokens the model will generate. Commit messages are short; 512 is generous.
OLLAMA_NUM_PREDICT = int(os.environ.get("OLLAMA_NUM_PREDICT", "512"))

# Request timeout in seconds. 60s is sufficient with the smaller ctx window.
# On cold-start (model loading from disk) the first call can still be slow.
OLLAMA_TIMEOUT     = int(os.environ.get("OLLAMA_TIMEOUT",     "60"))

# ---------------------------------------------------------------------------
# Preferred models for commit message generation — ordered SMALL → LARGE.
# Smaller models use less RAM and respond faster; larger ones give better quality.
# The script auto-picks the first model from this list that is actually installed.
# Adjust this list to match your preferences.
# ---------------------------------------------------------------------------
PREFERRED_MODELS = [
    "llama3.2:3b",       # 2.0 GB  — fast, compact, solid for commit messages
    "llama3.2:latest",   # 2.0 GB  — same (tag alias for llama3.2:3b)
    "gemma3:4b",         # 3.3 GB  — better quality, still compact
    "codellama:latest",  # 3.8 GB  — code-aware, reliable
    "llama2:latest",     # 3.8 GB  — older but dependable fallback
    "llama3.1:8b",       # 4.9 GB  — best quality (with num_ctx=8192 → ~6-7 GB RAM)
    "gemma3n:e4b",       # 7.5 GB  — high quality
    "gemma3:12b",        # 8.1 GB  — highest quality, heavy
]

# Default used when PREFERRED_MODELS walk fails completely
DEFAULT_MODEL = "llama3.2:3b"

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def format_size(size_bytes):
    """Convert bytes to a human-readable size string (e.g. '2.0 GB', '621 MB')."""
    if not size_bytes:
        return "? GB"
    gb = size_bytes / (1024 ** 3)
    if gb >= 1.0:
        return f"{gb:.1f} GB"
    mb = size_bytes / (1024 ** 2)
    return f"{mb:.0f} MB"

# ---------------------------------------------------------------------------
# Ollama-specific functions
# ---------------------------------------------------------------------------

def get_available_models():
    """
    Fetches list of installed models from the local Ollama server.

    Returns:
        None          — Ollama is not running (connection refused)
        []            — Ollama is running but no models are installed
        list[dict]    — [{"name": str, "size_bytes": int, "size_str": str}, ...]
    """
    url = f"{OLLAMA_BASE_URL}/api/tags"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        models_data = response.json().get("models", [])
        return [
            {
                "name":       m["name"],
                "size_bytes": m.get("size", 0),
                "size_str":   format_size(m.get("size", 0)),
            }
            for m in models_data
        ]
    except requests.exceptions.ConnectionError:
        return None  # Signals: Ollama not running (distinct from empty list)
    except Exception as e:
        print(f"\n🚨 Error fetching Ollama models: {e}")
        return []


def select_custom_model(available_models=None):
    """
    Interactively allows user to select an Ollama model from the installed list.
    Displays model size alongside each name.
    Falls back to auto-selection (smallest preferred model) if user presses Enter/Ctrl-C.
    """
    if available_models is None:
        print("🔍 Fetching available models from Ollama...")
        available_models = get_available_models()

    if available_models is None:
        print(f"\n🚨 Error: Could not connect to Ollama at {OLLAMA_BASE_URL}")
        print("   Make sure Ollama is running: run 'ollama serve' or start the Ollama app.")
        sys.exit(1)

    if not available_models:
        print("\n🚨 Error: Ollama is running but no models are installed.")
        print("   Install a model first, e.g.: ollama pull llama3.2:3b")
        sys.exit(1)

    available_names = [m["name"] for m in available_models]

    # Determine auto-pick target for display in prompt
    auto_pick = next(
        (m for m in PREFERRED_MODELS if m in available_names),
        available_names[0]
    )
    auto_pick_size = next(
        (m["size_str"] for m in available_models if m["name"] == auto_pick),
        "?"
    )

    print(f"\n--- 🤖 Available Ollama Models ({len(available_models)}) ---")
    for idx, m in enumerate(available_models, 1):
        preferred_marker = "  ⭐ preferred" if m["name"] in PREFERRED_MODELS else ""
        print(f"  [{idx:2}] {m['name']:<40} {m['size_str']:>8}{preferred_marker}")

    while True:
        try:
            choice = input(
                f"\nSelect model [1-{len(available_models)}] or press Enter for auto ({auto_pick}, {auto_pick_size}): "
            ).strip()

            if not choice:
                print(f"✅ Using: {auto_pick} ({auto_pick_size})")
                return auto_pick

            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(available_models):
                selected = available_models[choice_idx]
                print(f"✅ Selected: {selected['name']} ({selected['size_str']})")
                return selected["name"]
            else:
                print(f"❌ Please enter a number between 1 and {len(available_models)}")
        except ValueError:
            print("❌ Invalid input. Please enter a number.")
        except KeyboardInterrupt:
            print(f"\n\n⚠️ Selection cancelled. Using: {auto_pick} ({auto_pick_size})")
            return auto_pick


def run_git_with_ownership_fix(git_command, operation_description="Git operation", debug=False):
    """
    Executes a git command with automatic ownership error handling.

    This function provides a self-healing mechanism for Git's "dubious ownership"
    security check by automatically configuring the repository-local safe.directory
    setting when needed. This keeps the solution portable without affecting global
    Git configuration.

    Args:
        git_command: List of command arguments (e.g., ['git', 'add', '.', '-v'])
        operation_description: Human-readable description for user-facing messages
        debug: Enable verbose logging of errors and operations

    Returns:
        CompletedProcess object from successful execution

    Raises:
        CalledProcessError: If the command fails for reasons other than ownership
        SystemExit: If ownership fix fails after detection
    """
    try:
        result = subprocess.run(git_command, check=True, capture_output=True, text=True)
        if debug:
            print(f"🐛 [DEBUG] Command succeeded: {' '.join(git_command)}")
            if result.stdout:
                print(f"🐛 [DEBUG] stdout: {result.stdout[:500]}")
        return result
    except subprocess.CalledProcessError as e:
        if debug:
            print(f"🐛 [DEBUG] Command failed: {' '.join(git_command)}")
            print(f"🐛 [DEBUG] Exit code: {e.returncode}")
            print(f"🐛 [DEBUG] stderr: {e.stderr}")

        if e.returncode == 128 and 'dubious ownership' in e.stderr:
            print(f"🔧 Detected Git ownership issue during {operation_description}.")
            print("   Configuring repository-local safe.directory...")

            try:
                repo_result = subprocess.run(
                    ['git', 'rev-parse', '--show-toplevel'],
                    capture_output=True, text=True, check=True
                )
                repo_path = repo_result.stdout.strip()
            except subprocess.CalledProcessError:
                print("⚠️ Could not determine repository path. Using current directory.")
                repo_path = os.getcwd()

            try:
                if debug:
                    print(f"🐛 [DEBUG] Adding '{repo_path}' to safe.directory")

                subprocess.run(
                    ['git', 'config', '--global', '--add', 'safe.directory', repo_path],
                    check=True, capture_output=True, text=True
                )
                if debug:
                    print(f"🐛 [DEBUG] Config add succeeded")

                print(f"✅ Added '{repo_path}' to safe.directory config.")
                print(f"🔄 Retrying {operation_description}...")

                retry_result = subprocess.run(git_command, check=True, capture_output=True, text=True)
                if debug:
                    print(f"🐛 [DEBUG] Retry succeeded")
                return retry_result

            except subprocess.CalledProcessError as retry_error:
                print(f"🚨 Failed to fix ownership issue: {retry_error}")
                if debug:
                    print(f"🐛 [DEBUG] Retry stderr: {retry_error.stderr}")
                sys.exit(1)
        else:
            print(f"🚨 Error during {operation_description}: {e.stderr}")
            raise

def interactive_add(debug_mode=False):
    """
    Triggers 'git adi' (interactive fzf staging) with improved UX.
    Shows status before and summary after.
    """
    print("\n✅ --interactive-add flag detected.")

    print("\n📂 Current Status (Untracked/Modified):")
    try:
        run_git_with_ownership_fix(
            ['git', 'status', '-sb', '-uall'],
            operation_description="status check",
            debug=debug_mode
        )
    except subprocess.CalledProcessError:
        pass

    print("\n🚀 Launching interactive staging (fzf)...")
    try:
        subprocess.run(['git', 'adi'], capture_output=True, text=True, encoding='utf-8')

        result = subprocess.run(['git', 'diff', '--staged', '--quiet'])

        if result.returncode == 0:
            print("\n🤷 No files were staged. Aborting commit process.")
            sys.exit(0)

        print("\n✅ Staged Changes Summary:")
        subprocess.run(['git', 'diff', '--staged', '--stat'], check=True)

        if debug_mode:
            print("\n🐛 [DEBUG] Full Staged Diff:")
            subprocess.run(['git', '--no-pager', 'diff', '--staged'], check=True)

        print("\n---")
    except FileNotFoundError:
        print("\n🚨 Error: 'git' command not found. Is Git installed and in your PATH?")
        sys.exit(1)
    except Exception as e:
        print(f"\n🚨 An unexpected error occurred during interactive add: {e}")
        sys.exit(1)


def get_prompt_from_git(alias_name):
    """Executes the user's git alias to capture the prompt."""
    print(f"🤖 Running 'git {alias_name}' to generate prompt...")
    try:
        result = subprocess.run(['git', alias_name], capture_output=True, text=True, check=True, encoding='utf-8')
        print("---")
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        if "is not a git command" in e.stderr:
            print(f"\n🚨 Error: 'git {alias_name}' is not recognized as a git command or alias.")
            print(f"   Make sure the '{alias_name}' alias is configured in your git config.")
            print(f"   You may need to run 'gitinit.cmd' to set up your git aliases.")
            sys.exit(0)

        print(f"\n🚨 Error running 'git {alias_name}': {e.stderr}")
        sys.exit(1)


def generate_commit_message(prompt, include_signature=True, model_name=DEFAULT_MODEL, fallback_models=None, model_sizes=None):
    """
    Sends prompt to Ollama local API using the /api/chat endpoint.

    Smart fallback: if the primary model times out, crashes, or runs out of memory,
    automatically retries with the next model in fallback_models (ordered small→large).

    Args:
        prompt:           Git context string from 'git cinfo'
        include_signature: Whether to append the '--Generated by...' watermark
        model_name:       Primary model to use
        fallback_models:  Ordered list of model names to try if primary fails
                          (should be sorted small→large for RAM efficiency)
        model_sizes:      Dict of {model_name: size_str} for display (e.g. "2.0 GB")
    """
    strict_instructions = (
        "You are an expert developer writing a semantic git commit message. "
        "Follow conventional commit format (type: subject). "
        "OUTPUT ONLY the raw commit message. "
        "Do NOT add any markdown formatting (like ```). "
        "Do NOT add any introductory words (like 'Here is the message'). "
        "Start your response DIRECTLY with the commit type (e.g., feat:, fix:, docs:)."
    )

    context_input = (
        "Analyze the following git context and generate the message.\n\n"
        "--- START GIT CONTEXT ---\n"
        f"{prompt}\n"
        "--- END GIT CONTEXT ---"
    )

    # Build ordered list: preferred model first, then fallbacks
    models_to_try = [model_name]
    if fallback_models:
        models_to_try.extend(m for m in fallback_models if m != model_name)

    url = f"{OLLAMA_BASE_URL}/api/chat"

    for attempt_idx, current_model in enumerate(models_to_try):
        if attempt_idx > 0:
            size_str = (model_sizes or {}).get(current_model, "")
            size_display = f" ({size_str})" if size_str else ""
            print(f"🔄 Trying next model: {current_model}{size_display}")

        size_str = (model_sizes or {}).get(current_model, "")
        size_display = f" ({size_str})" if size_str else ""
        print(f"✨ Asking {current_model}{size_display} (Ollama local) to generate the commit message...")
        print(f"   [ctx={OLLAMA_NUM_CTX} tokens | timeout={OLLAMA_TIMEOUT}s]")

        payload = {
            "model":    current_model,
            "messages": [
                {"role": "system", "content": strict_instructions},
                {"role": "user",   "content": context_input}
            ],
            "stream":  False,
            "options": {
                "num_ctx":     OLLAMA_NUM_CTX,     # Cap context window → controls RAM usage
                "num_predict": OLLAMA_NUM_PREDICT,  # Cap output length → faster response
            }
        }

        has_more_fallbacks = attempt_idx < len(models_to_try) - 1

        try:
            response = requests.post(url, json=payload, timeout=OLLAMA_TIMEOUT)
            response.raise_for_status()
            json_response = response.json()

            raw_text = json_response["message"]["content"].strip()

            # Clean up artifacts (same pattern as other aic*.py backends)
            clean_text = raw_text.replace("```", "").strip()
            if clean_text.lower().startswith("text:"):
                clean_text = clean_text[5:].strip()
            if clean_text.lower().startswith("commit message:"):
                clean_text = clean_text[15:].strip()

            if include_signature:
                clean_text += "\n\n--Generated by Ollama (local)."

            return clean_text

        except requests.exceptions.Timeout:
            msg = (
                f"⚠️  {current_model} timed out after {OLLAMA_TIMEOUT}s "
                f"(RAM may be full or model still loading)."
            )
            print(f"\n{msg}")
            if has_more_fallbacks:
                print("   Cancelling request and trying a smaller model...")
                continue
            else:
                print("\n🚨 All models timed out. Cannot generate commit message.")
                print(f"   Tip: increase timeout with OLLAMA_TIMEOUT=120 or reduce RAM usage by stopping other apps.")
                sys.exit(1)

        except requests.exceptions.ConnectionError:
            msg = f"⚠️  Connection to Ollama lost (model may have crashed or been evicted from RAM)."
            print(f"\n{msg}")
            if has_more_fallbacks:
                print("   Trying a smaller model...")
                continue
            else:
                print(f"\n🚨 Ollama is not responding. Cannot generate commit message.")
                print("   Try running 'ollama serve' to restart the service.")
                sys.exit(1)

        except requests.exceptions.HTTPError as e:
            status = e.response.status_code
            if status in (500, 503):
                # Server error — commonly OOM or model loading failure
                msg = f"⚠️  {current_model} returned server error {status} (possible OOM or load failure)."
                print(f"\n{msg}")
                if has_more_fallbacks:
                    print("   Trying a smaller model...")
                    continue
                else:
                    print("\n🚨 All models returned server errors.")
                    sys.exit(1)
            elif status == 404:
                msg = f"⚠️  Model '{current_model}' not found in Ollama."
                print(f"\n{msg}")
                if has_more_fallbacks:
                    print("   Trying next available model...")
                    continue
                else:
                    print(f"\n🚨 No usable models found.")
                    print(f"   Install one with: ollama pull llama3.2:3b")
                    sys.exit(1)
            else:
                print(f"\n🚨 HTTP Error {status}: {e.response.text}")
                sys.exit(1)

        except (KeyError, ValueError) as e:
            print(f"\n🚨 Error parsing Ollama response: {e}")
            try:
                print(f"   Raw response: {response.text[:300]}")
            except Exception:
                pass
            sys.exit(1)

        except Exception as e:
            print(f"\n🚨 An unexpected error occurred: {e}")
            sys.exit(1)

    # Should not reach here, but guard anyway
    print("\n🚨 All models exhausted without generating a message.")
    sys.exit(1)


def make_git_commit(message, dry_run=False, review=False, push=False, add_all=False, can_regenerate=False):
    """Creates the git commit, allowing for a final review and edit."""
    if dry_run:
        print("\n✅ --- DRY RUN: COMMIT MESSAGE --- ✅\n" + message + "\n✅ --- END DRY RUN --- ✅\n")
        return

    commit_command = ['git', 'commit', '--no-quiet', '--verbose', '--branch', '--ahead-behind', '--status', '--signoff']

    should_commit = False
    temp_file_name = None

    if review:
        print("\n🔎 --- REVIEW COMMIT MESSAGE --- 🔎\n" + message + "\n---------------------------------\n")

        print("Choose an action:")
        print("  [y] Yes - Commit with this message")
        print("  [n] No - Abort the commit")
        print("  [e] Edit - Open editor to modify the message")
        if can_regenerate:
            print("  [r] Regenerate - Request a new AI-generated message")
        print()

        options_text = "(y/n/e/r)" if can_regenerate else "(y/n/e)"
        print(f"Enter your choice {options_text}: ", end='', flush=True)

        key_press = msvcrt.getch()
        try:
            print(key_press.decode('utf-8'))
        except Exception:
            print(str(key_press))

        if key_press.lower() == b'y':
            print("\n👍 Approved. Committing...")
            commit_command.extend(['-m', message])
            should_commit = True
        elif key_press.lower() == b'e':
            print("\n📝 Opening editor to edit the message...")
            with tempfile.NamedTemporaryFile(mode='w+', delete=False, encoding='utf-8') as temp_file:
                temp_file.write(message)
                temp_file_name = temp_file.name
            commit_command.extend(['-e', '-F', temp_file_name])
            should_commit = True
        elif can_regenerate and key_press.lower() == b'r':
            return "REGENERATE"
        else:
            print("\n❌ Aborted by user.")
            if add_all:
                print("\n🧹 --add-all flag was used. Unstaging files to clean up...")
                subprocess.run(['git', 'restore', '--staged', '.'], check=True)
                print("✅ Cleanup complete.")
            sys.exit(0)
    else:
        should_commit = True

    if should_commit:
        try:
            if temp_file_name and not any(opt in commit_command for opt in ('-e', '-F', '--file')):
                commit_command.extend(['--file', temp_file_name, '--edit'])
            elif not any(opt in commit_command for opt in ('-m', '--message', '-e', '-F', '--file')):
                commit_command.extend(['-m', message])

            print("\n🚀 Executing commit...")
            subprocess.run(commit_command, check=True, text=True, encoding='utf-8')

            if temp_file_name:
                try:
                    os.unlink(temp_file_name)
                except Exception:
                    pass

            print("\n✅ Commit successful!")
            try:
                subprocess.run([
                    'git', '--no-pager', 'log', '-1',
                    '--pretty=format:%C(yellow)%h%Creset %s %C(green)(%ar) %C(bold blue)<%an>%Creset%n%B%n'
                ], check=True)
            except Exception:
                pass

            if push:
                print("\n📤 Pushing to remote...")
                subprocess.run(['git', 'push', '--verbose', '--progress'], check=True, text=True, encoding='utf-8')
                print("✅ Push successful!")
        except subprocess.CalledProcessError as e:
            print(f"\n🚨 Commit failed: {e}")
            sys.exit(1)


# --- Script Execution ---
if __name__ == "__main__":
    # -----------------------------------------------------------------------
    # Startup validation: ensure Ollama is reachable before any git operations
    # -----------------------------------------------------------------------
    _available_at_startup = get_available_models()

    if _available_at_startup is None:
        print(f"\n🚨 Error: Ollama is not running at {OLLAMA_BASE_URL}")
        print("   Start Ollama first:")
        print("     • Run: ollama serve")
        print("     • Or launch the Ollama desktop app")
        print("   Then retry this command.")
        sys.exit(1)

    if not _available_at_startup:
        print("\n🚨 Error: Ollama is running but has no models installed.")
        print("   Install the recommended model:")
        print("     ollama pull llama3.2:3b")
        print("   Or any other model from: https://ollama.com/library")
        sys.exit(1)

    # Flat structures for quick lookups
    _available_names = [m["name"] for m in _available_at_startup]
    _model_sizes     = {m["name"]: m["size_str"] for m in _available_at_startup}

    epilog_text = """
                      Usage Examples & Workflows
|-------------------------------------------------------------------------------------------------------------------------------|
| Command       | Use Case                                 | User Flow Visualization                                             |
|---------------|------------------------------------------|---------------------------------------------------------------------|
| git aicl      | Quick Commit (files already staged)      | AI Generates > Commit                                               |
| git aicl file | Stage specific file(s) & Commit          | git add file > AI Generates > Commit                                |
| git aicl -d   | Dry Run (see message only)               | AI Generates > Show Message                                         |
| git aicl -r   | Review & Commit (approve AI message)     | AI Generates > Review                                               |
|               |                                          | (y>Commit / e>Edit / r>Regen / n>Abort)                            |
| git aicl -i   | Interactive Staging & Commit             | Select Files (fzf) > AI Generates > Commit                          |
| git aicl -a   | Add & Commit (stage and commit)          | Add All > AI Generates > Commit                                     |
| git aicl -p   | Commit & Push (commit staged, then push) | AI Generates > Commit > Push                                        |
| git aicl -m   | Pick model, then commit                  | Select Model > AI Generates > Commit                                |
|---------------|------------------------------------------|---------------------------------------------------------------------|
| git aicl -ar  | Add & Review (stage all, then approve)   | Add All > AI... > Review                                            |
|               |                                          | (y>Commit / e>Edit / r>Regen / n>Unstage)                          |
| git aicl -ir  | Interactively Stage, then Review         | Select Files (fzf) > AI... > Review                                 |
|               |                                          | (y>Commit / e>Edit / r>Regen / n>Abort)                            |
| git aicl -ap  | The "One-Shot" (add, commit, push)       | Add All > AI... > Commit > Push                                     |
| git aicl -ad  | Safe Preview (see msg for all changes)   | Add All > AI... > Show > Unstage                                    |
| git aicl -rp  | Review & Push (approve msg, then push)   | AI... > Review                                                      |
|               |                                          | (y>Commit > Push / e>Edit / r>Regen / n>Abort)                     |
|---------------|------------------------------------------|---------------------------------------------------------------------|
| git aicl -irp | Ultimate Control Workflow                | Select Files (fzf) > AI... > Review > Commit > Push                 |
| git aicl -arp | The Ultimate Workflow                    | Add All > AI... > Review                                            |
|               |                                          | (y>Commit > Push / e>Edit / r>Regen / n>Unstage)                   |
|-------------------------------------------------------------------------------------------------------------------------------|
    """

    parser = argparse.ArgumentParser(
        description="Generate and execute a git commit using Ollama (local LLM).",
        epilog=epilog_text,
        formatter_class=argparse.RawTextHelpFormatter
    )

    # --- Positional Arguments for Files ---
    parser.add_argument('files', metavar='FILES', nargs='*', help="Specific files to add/stage automatically.")

    arg_specs = [
        (['-a', '--add-all'], {'action': 'store_true', 'help': "Stage all changes before committing (git add .)."}),
        (['-aa'], {'action': 'store_true', 'help': argparse.SUPPRESS}),
        (['-d', '-n', '--dry-run'], {'action': 'store_true', 'help': "Print message without committing."}),
        (['-f', '--fill-placeholders'], {'action': 'store_true', 'help': "Prompt to fill placeholders in the cinfo prompt for additional context."}),
        (['-i', '--interactive-add'], {'action': 'store_true', 'help': "Interactively stage files using 'git adi' (fzf)."}),
        (['-m', '--model'], {'action': 'store_true', 'help': "Interactively select a local Ollama model from installed list."}),
        (['-p', '--push'], {'action': 'store_true', 'help': "Push after a successful commit."}),
        (['-r', '--review'], {'action': 'store_true', 'help': "Review message before committing [y/n/e/r]."}),
        (['-v', '--debug'], {'action': 'store_true', 'help': "Enable verbose logging for dependency manager."}),
        (['-w', '--watermark'], {'action': 'store_true', 'help': "Add 'Generated by Ollama (local)' signature to commit message."})
    ]

    arg_specs.sort(key=lambda x: next((opt for opt in x[0] if opt.startswith('--')), x[0][0]))

    for flags, kwargs in arg_specs:
        parser.add_argument(*flags, **kwargs)

    args = parser.parse_args()

    # --- Model Selection ---
    if args.model:
        # Interactive: show numbered list with sizes, let user choose
        target_model = select_custom_model(available_models=_available_at_startup)
        target_size = next(
            (m["size_str"] for m in _available_at_startup if m["name"] == target_model), "?"
        )
        print(f"🎯 Using model: {target_model} ({target_size})\n")
    else:
        # Auto-pick: walk PREFERRED_MODELS, use first one that is installed
        target_model = next(
            (m for m in PREFERRED_MODELS if m in _available_names),
            _available_names[0]  # fallback: first available model
        )
        target_size = next(
            (m["size_str"] for m in _available_at_startup if m["name"] == target_model), "?"
        )
        if target_model not in PREFERRED_MODELS:
            print(f"⚠️  None of the preferred models found. Using first available: {target_model} ({target_size})")
        print(f"🤖 Using model: {target_model} ({target_size}) (Ollama local)\n")

    # --- Build fallback chain: all other available models sorted by size (small → large) ---
    # Used by generate_commit_message() to automatically try lighter models on failure.
    _fallback_chain = [
        m["name"]
        for m in sorted(
            [m for m in _available_at_startup if m["name"] != target_model],
            key=lambda m: m["size_bytes"]
        )
    ]

    # --- Interactive Add Logic ---
    if args.interactive_add:
        interactive_add(debug_mode=args.debug)

    # --- File Staging Logic ---
    if args.files:
        print(f"📂 Staging specified files: {', '.join(args.files)}")
        for file in args.files:
            print(f"   ➕ Adding: {file}")
            try:
                run_git_with_ownership_fix(
                    ['git', 'add', file],
                    operation_description=f"staging {file}",
                    debug=args.debug
                )
            except subprocess.CalledProcessError:
                print(f"\n🚨 Failed to stage file: {file}")
                sys.exit(1)
        print("✅ File staging complete.\n")

    # --- Add All Logic ---
    if args.add_all or args.aa:
        print("\n✅ --add-all flag detected. Staging all changes...")
        try:
            run_git_with_ownership_fix(
                ['git', 'add', '.', '-v'],
                operation_description="staging all changes",
                debug=args.debug
            )
            print("---")
        except subprocess.CalledProcessError as e:
            print(f"\n🚨 Failed to stage changes: {e}")
            sys.exit(1)

    # --- Check staged changes ---
    if subprocess.run(['git', 'diff', '--staged', '--quiet']).returncode == 0:
        print("\n🤷 No changes staged for commit. Use 'git add' or pass filenames to this script.")
        sys.exit(0)

    # --- Prompt Generation ---
    prompt = get_prompt_from_git('cinfo')

    if args.fill_placeholders:
        print("\n📝 Placeholders for additional context:")
        try:
            result = subprocess.run(['git', 'commitplaceholders'], capture_output=True, text=True, check=True)
            placeholders_output = result.stdout
            print(placeholders_output.strip())
            lines = placeholders_output.split('\n')
            placeholders = []
            in_section = False
            for line in lines:
                if line.startswith('## Placeholders for Manual Input:'):
                    in_section = True
                    continue
                if in_section and line.strip().endswith(':') and not line.startswith('##'):
                    placeholders.append(line.strip())
        except subprocess.CalledProcessError as e:
            print(f"🚨 Error displaying placeholders: {e}")
            placeholders = []

        if placeholders:
            filled_values = {}
            print("\nEnter values for each placeholder (press Enter to skip):")
            for ph in placeholders:
                value = input(f"{ph} ").strip()
                if value:
                    filled_values[ph] = value

            if filled_values:
                prompt += "\n\n## Filled Placeholders:"
                for ph, val in filled_values.items():
                    prompt += f"\n{ph} {val}"

    if args.debug:
        print("\n🐛 [DEBUG] Generated Prompt Preview:")
        print(f"{prompt[:500]}...\n" if len(prompt) > 500 else f"{prompt}\n")
        print(f"🐛 [DEBUG] Fallback chain: {_fallback_chain}\n")

    # --- Regeneration Loop ---
    MAX_RETRIES = 2
    attempt = 0

    while attempt <= MAX_RETRIES:
        commit_message = generate_commit_message(
            prompt,
            include_signature=args.watermark,
            model_name=target_model,
            fallback_models=_fallback_chain,
            model_sizes=_model_sizes
        )

        result = make_git_commit(
            commit_message,
            dry_run=args.dry_run,
            review=args.review,
            push=args.push,
            add_all=(args.add_all or args.aa),
            can_regenerate=(attempt < MAX_RETRIES)
        )

        if result == "REGENERATE":
            attempt += 1
            if attempt <= MAX_RETRIES:
                print(f"\n🔄 Regeneration requested (attempt {attempt}/{MAX_RETRIES})...")
            else:
                print(f"\n⚠️ Maximum regeneration attempts ({MAX_RETRIES}) reached.")
                print("   Using the last generated message.")
                make_git_commit(
                    commit_message,
                    dry_run=args.dry_run,
                    review=False,
                    push=args.push,
                    add_all=(args.add_all or args.aa),
                    can_regenerate=False
                )
                break
        else:
            break

    if (args.add_all or args.aa) and args.dry_run:
        print("\n🧹 --add-all and --dry-run detected. Unstaging files to clean up...")
        subprocess.run(['git', 'restore', '--staged', '.'], check=True)
        print("✅ Cleanup complete. Staging area is clean.")
