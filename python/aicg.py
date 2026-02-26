import sys
import os
import subprocess

# --- 🛡️ Self-Healing Header ---
# 1. Import your local manager
try:
    import dependency_manager
except ImportError:
    # Fallback if the manager itself is missing (optional safety net)
    print("🚨 Critical: 'dependency_manager.py' is missing from this folder.")
    sys.exit(1)

# 2. Declare needs. { "import_name": "pip_package_name" }
# Option A: The Smart List (Use this for 99% of packages)
# It assumes 'import requests' means 'pip install requests'
# The manager automatically checks sys.argv for '--debug'
dependency_manager.require(["requests"])

# Option B: The Explicit Dict (Only use if names differ)
# dependency_manager.require({
#     "requests": "requests",
#     "yaml": "PyYAML",        # Import yaml, install PyYAML
#     "cv2": "opencv-python"   # Import cv2, install opencv-python
# })
# ------------------------------

# --- 🚀 Normal Imports (Guaranteed to work now) ---
import requests
import warnings
import argparse
import msvcrt  # For single-character input on Windows
import tempfile # For securely creating temporary files

# --- Configuration: Suppress Security Warning ---
from urllib3.exceptions import InsecureRequestWarning
warnings.simplefilter('ignore', InsecureRequestWarning)

# --- Configuration: API Key ---
try:
    API_KEY = os.environ["GOOGLE_API_KEY"]
except KeyError:
    try:
        API_KEY = os.environ["GEMINI_API_KEY"]
    except KeyError:
        print("\n🚨 Error: Neither GOOGLE_API_KEY nor GEMINI_API_KEY environment variable is set.")
        print("   Please set GOOGLE_API_KEY (preferred) or GEMINI_API_KEY in your environment.")
        sys.exit(1)

# --- Main Functions ---

def get_available_models():
    """Fetches list of available models from Gemini API."""
    url = "https://generativelanguage.googleapis.com/v1beta/models"
    headers = { 'Content-Type': 'application/json', 'X-goog-api-key': API_KEY }

    try:
        response = requests.get(url, headers=headers, verify=False, timeout=15)
        response.raise_for_status()
        models_data = response.json().get('models', [])

        # Filter for models that support generateContent and are not strictly embeddings/tuned
        generation_models = [
            m for m in models_data
            if 'generateContent' in m.get('supportedGenerationMethods', [])
            and 'models/' in m['name']
            and not any(x in m['name'] for x in ['embedding', 'aqa', 'text-moderation'])
        ]
        return generation_models
    except Exception as e:
        print(f"\n🚨 Error fetching models: {e}")
        return []

def select_custom_model():
    """Interactively allows user to select a Gemini model."""
    print("🔍 Fetching available models for your API key...")
    models = get_available_models()

    if not models:
        print("⚠️ Could not fetch models or no generation models found.")
        print("   Falling back to default: gemini-2.0-flash")
        return "gemini-2.0-flash"

    print("\n--- 🤖 Available Gemini Models ---")
    for idx, model in enumerate(models, 1):
        # Strip 'models/' prefix for display
        model_id = model['name'].replace('models/', '')
        display_name = model.get('displayName', 'No name')
        print(f"  [{idx:2}] {model_id:<25} | {display_name}")

    while True:
        try:
            choice = input(f"\nSelect a model (1-{len(models)}) or press Enter for default [gemini-2.0-flash]: ").strip()
            if not choice:
                return "gemini-2.0-flash"

            idx = int(choice) - 1
            if 0 <= idx < len(models):
                selected = models[idx]['name'].replace('models/', '')
                print(f"✅ Model set to: {selected}")
                return selected
            else:
                print(f"❌ Invalid selection. Please enter 1-{len(models)}.")
        except ValueError:
            print("❌ Please enter a number.")

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
                print(f"🐛 [DEBUG] stdout: {result.stdout}")
        return result
    except subprocess.CalledProcessError as e:
        if debug:
            print(f"🐛 [DEBUG] Command failed: {' '.join(git_command)}")
            print(f"🐛 [DEBUG] Exit code: {e.returncode}")
            print(f"🐛 [DEBUG] stderr: {e.stderr}")

        # Check if this is the "dubious ownership" error (exit code 128)
        if e.returncode == 128 and 'dubious ownership' in e.stderr:
            print(f"🔧 Detected Git ownership issue during {operation_description}.")
            print("   Configuring repository-local safe.directory...")

            # Try to get repository path, but fallback to current directory if that fails too
            repo_path = None
            try:
                repo_path = subprocess.run(
                    ['git', 'rev-parse', '--show-toplevel'],
                    capture_output=True, text=True, check=True
                ).stdout.strip()
                if debug:
                    print(f"🐛 [DEBUG] Repository path from git: {repo_path}")
            except subprocess.CalledProcessError as rev_error:
                # git rev-parse also failed due to ownership - use current directory
                repo_path = os.getcwd().replace('\\', '/')
                if debug:
                    print(f"🐛 [DEBUG] git rev-parse failed, using cwd: {repo_path}")
                    print(f"🐛 [DEBUG] rev-parse error: {rev_error.stderr}")

            try:
                # IMPORTANT: We must use --global because Git won't recognize this as a repo yet.
                # This is still safe and portable - it only whitelists THIS specific directory.
                # It doesn't disable the security feature globally, just allows this one path.
                config_result = subprocess.run(
                    ['git', 'config', '--global', '--add', 'safe.directory', repo_path],
                    check=True, capture_output=True, text=True
                )
                if debug:
                    print(f"🐛 [DEBUG] Global config command succeeded")

                print(f"✅ Added '{repo_path}' to safe.directory config.")
                print(f"🔄 Retrying {operation_description}...")

                # Retry the original command
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
            # Some other error - re-raise it with context
            print(f"🚨 Error during {operation_description}: {e.stderr}")
            raise

def interactive_add(debug_mode=False):
    """
    Triggers 'git adi' (interactive fzf staging) with improved UX.
    Shows status before and summary after.
    """
    print("\n✅ --interactive-add flag detected.")

    # 1. Pre-Flight: Show user what is available
    print("\n📂 Current Status (Untracked/Modified):")
    try:
        run_git_with_ownership_fix(
            ['git', 'status', '-sb', '-uall'],
            operation_description="status check",
            debug=debug_mode
        )
    except subprocess.CalledProcessError:
        # Ignore errors here, fzf will handle the main logic
        pass

    print("\n🚀 Launching interactive staging (fzf)...")
    try:
        # Run the user's custom alias.
        subprocess.run(['git', 'adi'], capture_output=True, text=True, encoding='utf-8')

        # 2. Post-Flight: Check if anything happened
        result = subprocess.run(['git', 'diff', '--staged', '--quiet'])

        if result.returncode == 0:
            print("\n🤷 No files were staged. Aborting commit process.")
            sys.exit(0)

        # 3. The "Receipt": Show what was staged
        print("\n✅ Staged Changes Summary:")
        subprocess.run(['git', 'diff', '--staged', '--stat'], check=True)

        # 4. Debug Mode: Deep Inspection
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
        print(f"\n🚨 Error running 'git {alias_name}': {e.stderr}")
        sys.exit(1)

def generate_commit_message(prompt, include_signature=True, model_name="gemini-2.0-flash"):
    """Sends prompt to Gemini API."""
    print(f"✨ Asking {model_name} to generate the commit message...")

    # --- 🧠 Architected Prompt ---
    # We remove the word "text" from the end instructions to prevent hallucination.
    # We use a strict "Role > Context > Constraint" structure.
    strict_prompt = (
        "You are an expert developer writing a semantic git commit message.\n"
        "Analyze the following git context and generate the message.\n"
        "--- START GIT CONTEXT ---\n"
        f"{prompt}\n"
        "--- END GIT CONTEXT ---\n"
        "Instructions:\n"
        "1. Follow conventional commit format (type: subject).\n"
        "2. OUTPUT ONLY the raw commit message.\n"
        "3. Do NOT add any markdown formatting (like ```).\n"
        "4. Do NOT add any introductory words (like 'Here is the message' or 'text').\n"
        "5. Start your response DIRECTLY with the commit type (e.g., feat:, fix:, docs:)."
    )

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"
    headers = { 'Content-Type': 'application/json', 'X-goog-api-key': API_KEY }
    data = {"contents": [{"parts": [{"text": strict_prompt}]}]}

    try:
        response = requests.post(url, headers=headers, json=data, verify=False, timeout=30)
        response.raise_for_status()
        json_response = response.json()

        if 'candidates' in json_response and json_response['candidates']:
            raw_text = json_response['candidates'][0]['content']['parts'][0]['text']

            # 1. Clean Markdown & Artifacts
            clean_text = raw_text.strip().replace("```", "")
            if clean_text.lower().startswith("text"): clean_text = clean_text[4:].strip()
            if clean_text.lower().startswith("commit message:"): clean_text = clean_text[15:].strip()

            if include_signature:
                clean_text += "\n--Generated by Google Gemini."

            return clean_text
        else:
            print("\n🚨 API Error: No content candidates found.")
            sys.exit(1)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            print("\n🚨 Rate Limit Exceeded (429 Too Many Requests)")
            print("   You've hit the Gemini API rate limit. This can happen due to:")
            print("   • Too many requests in a short time period")
            print("   • Exceeding your API quota")
            print("   • Using a free tier API key with low limits")
            print("\n💡 Solutions:")
            print("   1. Wait a few minutes before trying again")
            print("   2. Check your Google AI Studio quota at: https://aistudio.google.com/app/apikey")
            print("   3. Consider upgrading to a paid plan for higher limits")
            print("   4. Space out your commit generations")
            sys.exit(1)
        else:
            print(f"\n🚨 HTTP Error {e.response.status_code}: {e.response.text}")
            sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"\n🚨 Network error occurred: {e}")
        print("   Check your internet connection and try again.")
        sys.exit(1)
    except Exception as e:
        print(f"\n🚨 An unexpected error occurred with the Gemini API: {e}")
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

        # Display clear options menu
        print("Choose an action:")
        print("  [y] Yes - Commit with this message")
        print("  [n] No - Abort the commit")
        print("  [e] Edit - Open editor to modify the message")
        if can_regenerate:
            print("  [r] Regenerate - Create a new message")
        print()

        # Display 'r' option only if regeneration is allowed (token guardrail)
        options_text = "(y/n/e/r)" if can_regenerate else "(y/n/e)"
        print(f"Enter your choice {options_text}: ", end='', flush=True)

        key_press = msvcrt.getch()
        decoded_key = key_press.decode('utf-8') # Decode for printing
        print(decoded_key)

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
            return "REGENERATE" # Signal to main loop
        else:
            print("\n❌ Aborted by user.")
            if add_all:
                print("\n🧹 --add-all flag was used. Unstaging files to clean up...")
                subprocess.run(['git', 'restore', '--staged', '.'], check=True)
                print("✅ Cleanup complete.")
            sys.exit(0)
    else:
        commit_command.extend(['-m', message])
        should_commit = True

    if should_commit:
        print("\n✅ Committing...\n")
        try:
            subprocess.run(commit_command, check=True)
            print("\n🎉 Commit successful!\n---")
            # NOTE: We keep this simple log -1. The full unpushed log is handled by the alias if needed,
            # or could be added here if you want it explicitly in the script logic.
            subprocess.run(['git', '--no-pager', 'log', '-1', '--pretty=format:%C(yellow)%h%Creset %s %C(green)(%ar) %C(bold blue)<%an>%Creset%n%B%n'], check=True)
            print("---")

            if push:
                print("\n✅ --push flag detected. Pushing to remote...")
                subprocess.run(['git', 'push'], check=True)
                print("\n🚀 Push successful!\n")

        except subprocess.CalledProcessError:
            print("🚨 Error during git operation (or commit aborted in editor).")
        finally:
            if temp_file_name and os.path.exists(temp_file_name):
                os.remove(temp_file_name)

# --- Script Execution ---
if __name__ == "__main__":
    epilog_text = """
                      Usage Examples & Workflows
|-------------------------------------------------------------------------------------------------------------------------------|
| Command       | Use Case                                 | User Flow Visualization                                             |
|---------------|------------------------------------------|---------------------------------------------------------------------|
| git aicg      | Quick Commit (files already staged)      | ✨ AI Generates ➔ ✅ Commit                                         |
| git aicg file | Stage specific file(s) & Commit          | ➕ git add file ➔ ✨ AI Generates ➔ ✅ Commit                      |
| git aicg -d   | Dry Run (see message only)               | ✨ AI Generates ➔ 🧪 Show Message                                   |
| git aicg -r   | Review & Commit (approve AI message)     | ✨ AI Generates ➔ 🔎 Review                                         |
|               |                                          | (y➔✅ Commit / e➔📝 Edit / g➔🔄 Regen / n➔❌ Abort)                |
| git aicg -i   | Interactive Staging & Commit             | ➕ Select Files (fzf) ➔ ✨ AI Generates ➔ ✅ Commit                 |
| git aicg -a   | Add & Commit (stage and commit)          | ➕ Add All ➔ ✨ AI Generates ➔ ✅ Commit                            |
| git aicg -p   | Commit & Push (commit staged, then push) | ✨ AI Generates ➔ ✅ Commit ➔ 🚀 Push                               |
|---------------|------------------------------------------|---------------------------------------------------------------------|
| git aicg -ar  | Add & Review (stage all, then approve)   | ➕ Add All ➔ ✨ AI... ➔ 🔎 Review                                   |
|               |                                          | (y➔✅ Commit / e➔📝 Edit / g➔🔄 Regen / n➔🧹 Unstage)              |
| git aicg -ir  | Interactively Stage, then Review         | ➕ Select Files (fzf) ➔ ✨ AI... ➔ 🔎 Review                        |
|               |                                          | (y➔✅ Commit / e➔📝 Edit / g➔🔄 Regen / n➔❌ Abort)                 |
| git aicg -ap  | The "One-Shot" (add, commit, push)       | ➕ Add All ➔ ✨ AI... ➔ ✅ Commit ➔ 🚀 Push                         |
| git aicg -ad  | Safe Preview (see msg for all changes)   | ➕ Add All ➔ ✨ AI... ➔ 🧪 Show ➔ 🧹 Unstage                        |
| git aicg -rp  | Review & Push (approve msg, then push)   | ✨ AI... ➔ 🔎 Review                                                |
|               |                                          | (y➔✅ Commit ➔ 🚀 Push / e➔📝 Edit / g➔🔄 Regen / n➔❌ Abort)       |
|---------------|------------------------------------------|---------------------------------------------------------------------|
| git aicg -irp | Ultimate Control Workflow                | ➕ Select Files (fzf) ➔ ✨ AI... ➔ 🔎 Review ➔ ✅ Commit ➔ 🚀 Push |
| git aicg -arp | The Ultimate Workflow                    | ➕ Add All ➔ ✨ AI... ➔ 🔎 Review                                   |
|               |                                          | (y➔✅ Commit ➔ 🚀 Push / e➔📝 Edit / g➔🔄 Regen / n➔🧹 Unstage)     |
|-------------------------------------------------------------------------------------------------------------------------------|
    """

    parser = argparse.ArgumentParser(
        description="Generate and execute a git commit using Google Gemini.",
        epilog=epilog_text,
        formatter_class=argparse.RawTextHelpFormatter
    )

    # --- CHANGED: Positional Arguments for Files ---
    parser.add_argument('files', metavar='FILES', nargs='*', help="Specific files to add/stage automatically.")

    # Collect arguments to sort alphabetically by long option
    arg_specs = [
        (['-a', '--add-all'], {'action': 'store_true', 'help': "Stage all changes before committing (git add .)."}),
        (['-aa'], {'action': 'store_true', 'help': argparse.SUPPRESS}),
        (['-d', '-n', '--dry-run'], {'action': 'store_true', 'help': "Print message without committing."}),
        (['-f', '--fill-placeholders'], {'action': 'store_true', 'help': "Prompt to fill placeholders in the cinfo prompt for additional context."}),
        (['-i', '--interactive-add'], {'action': 'store_true', 'help': "Interactively stage files using 'git adi' (fzf)."}),
        (['-m', '--model'], {'action': 'store_true', 'help': "Interactively select a custom Gemini model from your available list."}),
        (['-p', '--push'], {'action': 'store_true', 'help': "Push after a successful commit."}),
        (['-r', '--review'], {'action': 'store_true', 'help': "Review message before committing [y/n/e/g]."}),
        (['-v', '--debug'], {'action': 'store_true', 'help': "Enable verbose logging for dependency manager."}),
        (['-w', '--watermark'], {'action': 'store_true', 'help': "Add 'Generated by Google Gemini' signature to commit message."})
]

    # Sort by the first long option (starting with '--'), or first short if no long
    arg_specs.sort(key=lambda x: next((opt for opt in x[0] if opt.startswith('--')), x[0][0]))

    # Add sorted arguments to parser
    for args, kwargs in arg_specs:
        parser.add_argument(*args, **kwargs)

    args = parser.parse_args()

    # --- NEW STAGING LOGIC ---
    # 1. Check for specific files passed as arguments
    if args.files:
        print(f"\n✅ File arguments detected. Staging: {', '.join(args.files)}")
        try:
            run_git_with_ownership_fix(
                ['git', 'add', '-v'] + args.files,
                operation_description="file staging",
                debug=args.debug
            )
            print("---")
        except subprocess.CalledProcessError:
            sys.exit(1)

    # 2. Check for other staging flags
    if args.interactive_add:
        # Pass the debug flag to the function
        interactive_add(debug_mode=args.debug)
    elif args.add_all or args.aa:
        print("\n✅ --add-all flag detected. Staging all changes...")
        try:
            run_git_with_ownership_fix(
                ['git', 'add', '.', '-v'],
                operation_description="staging all changes",
                debug=args.debug
            )
            print("---")
        except subprocess.CalledProcessError:
            sys.exit(1)

    if subprocess.run(['git', 'diff', '--staged', '--quiet']).returncode == 0:
        print("\n🤷 No changes staged for commit. Use 'git add' or pass filenames to this script.")
        sys.exit(0)
    # --- MODEL SELECTION ---
    target_model = "gemini-2.0-flash"
    if args.model:
        target_model = select_custom_model()


    prompt = get_prompt_from_git("cinfo")

    if args.fill_placeholders:
        # Display placeholders for reference and parse them
        print("\n📝 Placeholders for additional context:")
        try:
            result = subprocess.run(['git', 'commitplaceholders'], capture_output=True, text=True, check=True)
            placeholders_output = result.stdout
            print(placeholders_output.strip())

            # Parse placeholders from output
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
            # Prompt for each placeholder value
            filled_values = {}
            print("\nEnter values for each placeholder (press Enter to skip):")
            for ph in placeholders:
                value = input(f"{ph} ").strip()
                if value:
                    filled_values[ph] = value

            # Append filled placeholders to the prompt
            if filled_values:
                prompt += "\n\n## Filled Placeholders:"
                for ph, val in filled_values.items():
                    prompt += f"\n{ph} {val}"

    # --- RETRY LOGIC (Max 2 Retries = 3 total generations) ---
    MAX_RETRIES = 2
    attempts_done = 0

    while True:
        # Pass the watermark flag directly.
        # Signature is added only if --watermark is specified.
        commit_message = generate_commit_message(prompt, include_signature=args.watermark, model_name=target_model)

        # Determine if we allow regeneration (only if we haven't hit the cap)
        allow_regen = (attempts_done < MAX_RETRIES)

        result = make_git_commit(
            commit_message,
            dry_run=args.dry_run,
            review=args.review,
            push=args.push,
            add_all=(args.add_all or args.aa),
            can_regenerate=allow_regen
        )

        if result == "REGENERATE":
            attempts_done += 1
            print(f"\n🔄 Regenerating commit message... (Retry {attempts_done}/{MAX_RETRIES})")
            continue

        # If we got here, it means we committed, dry-run finished, or user aborted inside make_git_commit
        break

    if (args.add_all or args.aa) and args.dry_run:
        print("\n🧹 --add-all and --dry-run detected. Unstaging files to clean up...")
        subprocess.run(['git', 'restore', '--staged', '.'], check=True)
        print("✅ Cleanup complete. Staging area is clean.")
