#!/usr/bin/env python3
"""
AI-powered Git commit message generator using Anthropic Claude.
Generates conventional commit messages using Anthropic's models.
"""

# --- 🛡️ Self-Healing Header ---
# 1. Import your local manager
try:
    import dependency_manager
except ImportError:
    # Fallback if the manager itself is missing (optional safety net)
    print("🚨 Critical: 'dependency_manager.py' is missing from this folder.")
    import sys
    sys.exit(1)

# 2. Declare needs - Anthropic SDK
dependency_manager.require(["anthropic", "httpx"])

# ------------------------------

# --- 🚀 Normal Imports (Guaranteed to work now) ---
import os
import sys
import argparse
import subprocess
import warnings
import msvcrt  # For single-character input on Windows
import tempfile  # For securely creating temporary files
import anthropic
import httpx

# --- Configuration: Suppress SSL Warnings ---
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- Configuration: API Key ---
try:
    API_KEY = os.environ["ANTHROPIC_API_KEY"]
except KeyError:
    print("\n🚨 Error: ANTHROPIC_API_KEY environment variable is not set.")
    print("   Please set ANTHROPIC_API_KEY in your environment.")
    print("   Get your API key from: https://console.anthropic.com/")
    sys.exit(1)

# Initialize Anthropic client with SSL verification disabled
# This fixes certificate verification issues on Windows
http_client = httpx.Client(verify=False)
client = anthropic.Anthropic(api_key=API_KEY, http_client=http_client)

# --- Default model: cheapest & fastest Claude (ideal for commit messages) ---
DEFAULT_MODEL = "claude-haiku-4-5-20251001"

# --- Main Functions ---

def get_available_models():
    """Fetches list of available Claude models from Anthropic API."""
    try:
        models_data = client.models.list()
        # Filter for Claude generation models
        generation_models = [
            m for m in models_data.data
            if m.id.startswith('claude-')
        ]
        # Sort by ID descending for consistent display
        generation_models.sort(key=lambda x: x.id, reverse=True)
        return generation_models
    except Exception as e:
        print(f"\n🚨 Error fetching models: {e}")
        return []

def select_custom_model():
    """Interactively allows user to select an Anthropic Claude model."""
    print("🔍 Fetching available models for your API key...")
    models = get_available_models()

    if not models:
        print("⚠️ Could not fetch models or no Claude models found.")
        print(f"   Falling back to default: {DEFAULT_MODEL}")
        return DEFAULT_MODEL

    print("\n--- 🤖 Available Anthropic Claude Models ---")
    for idx, model in enumerate(models, 1):
        model_id = model.id
        display_name = getattr(model, 'display_name', model_id)
        print(f"  [{idx:2}] {model_id:<45} | {display_name}")

    while True:
        try:
            choice = input(f"\nSelect model [1-{len(models)}] or press Enter for default ({DEFAULT_MODEL}): ").strip()

            if not choice:
                print(f"✅ Using default: {DEFAULT_MODEL}")
                return DEFAULT_MODEL

            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(models):
                selected = models[choice_idx].id
                print(f"✅ Selected: {selected}")
                return selected
            else:
                print(f"❌ Please enter a number between 1 and {len(models)}")
        except ValueError:
            print("❌ Invalid input. Please enter a number.")
        except KeyboardInterrupt:
            print(f"\n\n⚠️ Selection cancelled. Using default: {DEFAULT_MODEL}")
            return DEFAULT_MODEL

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

        # Check if this is the "dubious ownership" error (exit code 128)
        if e.returncode == 128 and 'dubious ownership' in e.stderr:
            print(f"🔧 Detected Git ownership issue during {operation_description}.")
            print("   Configuring repository-local safe.directory...")

            # Try to get repository path, but fallback to current directory if that fails too
            repo_path = None
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
        # Check if this is a "not a git command" error and provide helpful context
        if "is not a git command" in e.stderr:
            print(f"\n🚨 Error: 'git {alias_name}' is not recognized as a git command or alias.")
            print(f"   Make sure the '{alias_name}' alias is configured in your git config.")
            print(f"   You may need to run 'gitinit.cmd' to set up your git aliases.")
            sys.exit(0)

        print(f"\n🚨 Error running 'git {alias_name}': {e.stderr}")
        sys.exit(1)

def generate_commit_message(prompt, include_signature=True, model_name=DEFAULT_MODEL):
    """Sends prompt to Anthropic API using Messages API."""
    print(f"✨ Asking {model_name} to generate the commit message...")

    # --- 🧠 Architected Prompt ---
    strict_instructions = (
        "You are an expert developer writing a semantic git commit message. "
        "Follow conventional commit format (type: subject). "
        "OUTPUT ONLY the raw commit message. "
        "Do NOT add any markdown formatting (like ```). "
        "Do NOT add any introductory words (like 'Here is the message'). "
        "Start your response DIRECTLY with the commit type (e.g., feat:, fix:, docs:)."
    )

    context_input = f"Analyze the following git context and generate the message.\n\n--- START GIT CONTEXT ---\n{prompt}\n--- END GIT CONTEXT ---"

    try:
        response = client.messages.create(
            model=model_name,
            max_tokens=1024,
            system=strict_instructions,
            messages=[{"role": "user", "content": context_input}]
        )

        raw_text = response.content[0].text.strip()

        # Clean up artifacts
        clean_text = raw_text.replace("```", "").strip()
        if clean_text.lower().startswith("text:"):
            clean_text = clean_text[5:].strip()
        if clean_text.lower().startswith("commit message:"):
            clean_text = clean_text[15:].strip()

        if include_signature:
            clean_text += "\n\n--Generated by Anthropic Claude."

        return clean_text

    except anthropic.RateLimitError:
        print("\n🚨 Rate Limit Exceeded (429 Too Many Requests)")
        print("   You've hit the Anthropic API rate limit. This can happen due to:")
        print("   • Too many requests in a short time period")
        print("   • Exceeding your API quota")
        print("   • Insufficient credits in your account")
        print("\n💡 Solutions:")
        print("   1. Wait a few minutes before trying again")
        print("   2. Check your API usage and limits at: https://console.anthropic.com/")
        print("   3. Add credits to your account if needed")
        print("   4. Consider upgrading to a higher tier plan")
        sys.exit(1)
    except anthropic.APIError as e:
        print(f"\n🚨 Anthropic API Error: {e}")
        sys.exit(1)
    except anthropic.AnthropicError as e:
        print(f"\n🚨 Anthropic Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n🚨 An unexpected error occurred: {e}")
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
            print("  [r] Regenerate - Request a new AI-generated message (costs additional API token)")
        print()

        # Display 'r' option only if regeneration is allowed (token guardrail)
        options_text = "(y/n/e/r)" if can_regenerate else "(y/n/e)"
        print(f"Enter your choice {options_text}: ", end='', flush=True)

        key_press = msvcrt.getch()
        # Echo pressed key for visibility
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
            # Avoid duplicating commit flags if they were already added in the review branch
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
            # Show the last commit details
            try:
                subprocess.run([
                    'git', '--no-pager', 'log', '-1',
                    '--pretty=format:%C(yellow)%h%Creset %s %C(green)(%ar) %C(bold blue)<%an>%Creset%n%B%n'
                ], check=True)
            except Exception:
                # Non-fatal: if displaying the log fails, continue normally
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
    epilog_text = """
                      Usage Examples & Workflows
|-------------------------------------------------------------------------------------------------------------------------------|
| Command       | Use Case                                 | User Flow Visualization                                             |
|---------------|------------------------------------------|---------------------------------------------------------------------|
| git aica      | Quick Commit (files already staged)      | AI Generates > Commit                                               |
| git aica file | Stage specific file(s) & Commit          | git add file > AI Generates > Commit                                |
| git aica -d   | Dry Run (see message only)               | AI Generates > Show Message                                         |
| git aica -r   | Review & Commit (approve AI message)     | AI Generates > Review                                               |
|               |                                          | (y>Commit / e>Edit / r>Regen / n>Abort)                            |
| git aica -i   | Interactive Staging & Commit             | Select Files (fzf) > AI Generates > Commit                          |
| git aica -a   | Add & Commit (stage and commit)          | Add All > AI Generates > Commit                                     |
| git aica -p   | Commit & Push (commit staged, then push) | AI Generates > Commit > Push                                        |
|---------------|------------------------------------------|---------------------------------------------------------------------|
| git aica -ar  | Add & Review (stage all, then approve)   | Add All > AI... > Review                                            |
|               |                                          | (y>Commit / e>Edit / r>Regen / n>Unstage)                          |
| git aica -ir  | Interactively Stage, then Review         | Select Files (fzf) > AI... > Review                                 |
|               |                                          | (y>Commit / e>Edit / r>Regen / n>Abort)                            |
| git aica -ap  | The "One-Shot" (add, commit, push)       | Add All > AI... > Commit > Push                                     |
| git aica -ad  | Safe Preview (see msg for all changes)   | Add All > AI... > Show > Unstage                                    |
| git aica -rp  | Review & Push (approve msg, then push)   | AI... > Review                                                      |
|               |                                          | (y>Commit > Push / e>Edit / r>Regen / n>Abort)                     |
|---------------|------------------------------------------|---------------------------------------------------------------------|
| git aica -irp | Ultimate Control Workflow                | Select Files (fzf) > AI... > Review > Commit > Push                 |
| git aica -arp | The Ultimate Workflow                    | Add All > AI... > Review                                            |
|               |                                          | (y>Commit > Push / e>Edit / r>Regen / n>Unstage)                   |
|-------------------------------------------------------------------------------------------------------------------------------|
    """

    parser = argparse.ArgumentParser(
        description="Generate and execute a git commit using Anthropic Claude.",
        epilog=epilog_text,
        formatter_class=argparse.RawTextHelpFormatter
    )

    # --- Positional Arguments for Files ---
    parser.add_argument('files', metavar='FILES', nargs='*', help="Specific files to add/stage automatically.")

    # Collect arguments to sort alphabetically by long option
    arg_specs = [
        (['-a', '--add-all'], {'action': 'store_true', 'help': "Stage all changes before committing (git add .)."}),
        (['-aa'], {'action': 'store_true', 'help': argparse.SUPPRESS}),
        (['-d', '-n', '--dry-run'], {'action': 'store_true', 'help': "Print message without committing."}),
        (['-f', '--fill-placeholders'], {'action': 'store_true', 'help': "Prompt to fill placeholders in the cinfo prompt for additional context."}),
        (['-i', '--interactive-add'], {'action': 'store_true', 'help': "Interactively stage files using 'git adi' (fzf)."}),
        (['-m', '--model'], {'action': 'store_true', 'help': "Interactively select a custom Anthropic Claude model from your available list."}),
        (['-p', '--push'], {'action': 'store_true', 'help': "Push after a successful commit."}),
        (['-r', '--review'], {'action': 'store_true', 'help': "Review message before committing [y/n/e/r]."}),
        (['-v', '--debug'], {'action': 'store_true', 'help': "Enable verbose logging for dependency manager."}),
        (['-w', '--watermark'], {'action': 'store_true', 'help': "Add 'Generated by Anthropic Claude' signature to commit message."})
    ]

    # Sort by the first long option (starting with '--'), or first short if no long
    arg_specs.sort(key=lambda x: next((opt for opt in x[0] if opt.startswith('--')), x[0][0]))

    for flags, kwargs in arg_specs:
        parser.add_argument(*flags, **kwargs)

    args = parser.parse_args()

    # --- Model Selection ---
    target_model = DEFAULT_MODEL  # Default: cheapest & fastest Claude
    if args.model:
        target_model = select_custom_model()
        print(f"🎯 Using model: {target_model}\n")

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
    alias_name = 'cinfo'
    prompt = get_prompt_from_git(alias_name)

    # If user asked to fill placeholders, show placeholders and let them enter values,
    # then append filled placeholders to the prompt.
    if args.fill_placeholders:
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

    # --- Regeneration Loop ---
    MAX_RETRIES = 2
    attempt = 0

    while attempt <= MAX_RETRIES:
        commit_message = generate_commit_message(
            prompt,
            include_signature=args.watermark,
            model_name=target_model
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
