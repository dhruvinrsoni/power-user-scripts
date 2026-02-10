#!/usr/bin/env python3
"""
AI-powered Git commit message generator using OpenAI.
Generates conventional commit messages using OpenAI's models.
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

# 2. Declare needs - OpenAI SDK
dependency_manager.require(["openai", "httpx"]) 

# ------------------------------

# --- 🚀 Normal Imports (Guaranteed to work now) ---
import os
import sys
import argparse
import subprocess
import warnings
import msvcrt  # For single-character input on Windows
import tempfile # For securely creating temporary files
import httpx
from openai import OpenAI, OpenAIError, APIError, RateLimitError

# --- Configuration: Suppress SSL Warnings ---
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- Configuration: API Key ---
try:
    API_KEY = os.environ["OPENAI_API_KEY"]
except KeyError:
    print("\n🚨 Error: OPENAI_API_KEY environment variable is not set.")
    print("   Please set OPENAI_API_KEY in your environment.")
    print("   Get your API key from: https://platform.openai.com/api-keys")
    sys.exit(1)

# Initialize OpenAI client with SSL verification disabled
# This fixes certificate verification issues on Windows
http_client = httpx.Client(verify=False)
client = OpenAI(api_key=API_KEY, http_client=http_client)

# --- Main Functions ---

def get_available_models():
    """Fetches list of available models from OpenAI API."""
    try:
        models_data = client.models.list()
        
        # Filter for models that support text generation (gpt models primarily)
        # Filter out embedding, moderation, whisper, tts, dall-e models
        generation_models = [
            m for m in models_data.data
            if any(prefix in m.id for prefix in ['gpt-', 'o1-', 'o3-'])
            and not any(x in m.id for x in ['whisper', 'tts', 'dall-e', 'embedding'])
        ]
        
        # Sort by ID for consistent display
        generation_models.sort(key=lambda x: x.id, reverse=True)
        return generation_models
    except Exception as e:
        print(f"\n🚨 Error fetching models: {e}")
        return []

def select_custom_model():
    """Interactively allows user to select an OpenAI model."""
    print("🔍 Fetching available models for your API key...")
    models = get_available_models()
    
    if not models:
        print("⚠️ Could not fetch models or no generation models found.")
        print("   Falling back to default: gpt-5")
        return "gpt-5"
    
    print("\n--- 🤖 Available OpenAI Models ---")
    for idx, model in enumerate(models, 1):
        model_id = model.id
        created = model.created if hasattr(model, 'created') else 'N/A'
        print(f"  [{idx:2}] {model_id:<30} | Created: {created}")
    
    while True:
        try:
            choice = input(f"\nSelect model [1-{len(models)}] or press Enter for default (gpt-4o): ").strip()
            
            if not choice:
                print("✅ Using default: gpt-5")
                return "gpt-5"
            
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
            print("\n\n⚠️ Selection cancelled. Using default: gpt-5")
            return "gpt-5"

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
            except subprocess.CalledProcessError as rev_error:
                print("⚠️ Could not determine repository path. Using current directory.")
                repo_path = os.getcwd()
            
            try:
                if debug:
                    print(f"🐛 [DEBUG] Adding '{repo_path}' to safe.directory")
                    
                config_result = subprocess.run(
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

def generate_commit_message(prompt, include_signature=True, model_name="gpt-5"):
    """Sends prompt to OpenAI API using Responses API."""
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
        # Using the new Responses API
        response = client.responses.create(
            model=model_name,
            instructions=strict_instructions,
            input=context_input
        )
        
        # Extract text from response
        if hasattr(response, 'output_text') and response.output_text:
            raw_text = response.output_text.strip()
        elif hasattr(response, 'output') and response.output:
            # Fallback: extract from output array
            text_parts = []
            for item in response.output:
                if hasattr(item, 'content'):
                    for content_part in item.content:
                        if hasattr(content_part, 'text'):
                            text_parts.append(content_part.text)
            raw_text = '\n'.join(text_parts).strip()
        else:
            print("\n🚨 API Error: No content found in response.")
            sys.exit(1)
        
        # Clean up artifacts
        clean_text = raw_text.replace("```", "").strip()
        if clean_text.lower().startswith("text:"):
            clean_text = clean_text[5:].strip()
        if clean_text.lower().startswith("commit message:"):
            clean_text = clean_text[15:].strip()

        if include_signature:
            clean_text += "\n\n--Generated by OpenAI."
        
        return clean_text
        
    except RateLimitError as e:
        print("\n🚨 Rate Limit Exceeded (429 Too Many Requests)")
        print("   You've hit the OpenAI API rate limit. This can happen due to:")
        print("   • Too many requests in a short time period")
        print("   • Exceeding your API quota")
        print("   • Insufficient credits in your account")
        print("\n💡 Solutions:")
        print("   1. Wait a few minutes before trying again")
        print("   2. Check your API usage and limits at: https://platform.openai.com/usage")
        print("   3. Add credits to your account if needed")
        print("   4. Consider upgrading to a higher tier plan")
        sys.exit(1)
    except APIError as e:
        print(f"\n🚨 OpenAI API Error: {e}")
        sys.exit(1)
    except OpenAIError as e:
        print(f"\n🚨 OpenAI Error: {e}")
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
        decoded_key = key_press.decode('utf-8') # Decode for printing
        print(decoded_key) # Echo the pressed key
        
        if decoded_key.lower() == 'y':
            should_commit = True
        elif decoded_key.lower() == 'n':
            print("\n❌ Commit aborted by user.")
            if add_all:
                print("🧹 Unstaging all files (since --add-all was used)...")
                subprocess.run(['git', 'reset', 'HEAD'], check=False)
            sys.exit(0)
        elif decoded_key.lower() == 'e':
            should_commit = True
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as temp_file:
                temp_file.write(message)
                temp_file_name = temp_file.name
            print(f"\n📝 Opening editor to modify commit message...")
        elif decoded_key.lower() == 'r' and can_regenerate:
            return 'regenerate'
        else:
            print(f"\n❌ Invalid choice '{decoded_key}'. Commit aborted.")
            sys.exit(0)
    else:
        should_commit = True

    if should_commit:
        try:
            if temp_file_name:
                commit_command.extend(['--file', temp_file_name, '--edit'])
            else:
                commit_command.extend(['--message', message])
            
            print("\n🚀 Executing commit...")
            result = subprocess.run(commit_command, check=True, text=True, encoding='utf-8')
            
            if temp_file_name:
                try:
                    os.unlink(temp_file_name)
                except:
                    pass
            
            print("\n✅ Commit successful!")
            
            if push:
                print("\n📤 Pushing to remote...")
                push_result = subprocess.run(['git', 'push', '--verbose', '--progress'], check=True, text=True, encoding='utf-8')
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
| git aico      | Quick Commit (files already staged)      | AI Generates > Commit                                               |
| git aico file | Stage specific file(s) & Commit          | git add file > AI Generates > Commit                                |
| git aico -d   | Dry Run (see message only)               | AI Generates > Show Message                                         |
| git aico -r   | Review & Commit (approve AI message)     | AI Generates > Review                                               |
|               |                                          | (y>Commit / e>Edit / r>Regen / n>Abort)                            |
| git aico -i   | Interactive Staging & Commit             | Select Files (fzf) > AI Generates > Commit                          |
| git aico -a   | Add & Commit (stage and commit)          | Add All > AI Generates > Commit                                     |
| git aico -p   | Commit & Push (commit staged, then push) | AI Generates > Commit > Push                                        |
|---------------|------------------------------------------|---------------------------------------------------------------------|
| git aico -ar  | Add & Review (stage all, then approve)   | Add All > AI... > Review                                            |
|               |                                          | (y>Commit / e>Edit / r>Regen / n>Unstage)                          |
| git aico -ir  | Interactively Stage, then Review         | Select Files (fzf) > AI... > Review                                 |
|               |                                          | (y>Commit / e>Edit / r>Regen / n>Abort)                            |
| git aico -ap  | The "One-Shot" (add, commit, push)       | Add All > AI... > Commit > Push                                     |
| git aico -ad  | Safe Preview (see msg for all changes)   | Add All > AI... > Show > Unstage                                    |
| git aico -rp  | Review & Push (approve msg, then push)   | AI... > Review                                                      |
|               |                                          | (y>Commit > Push / e>Edit / r>Regen / n>Abort)                     |
|---------------|------------------------------------------|---------------------------------------------------------------------|
| git aico -irp | Ultimate Control Workflow                | Select Files (fzf) > AI... > Review > Commit > Push                 |
| git aico -arp | The Ultimate Workflow                    | Add All > AI... > Review                                            |
|               |                                          | (y>Commit > Push / e>Edit / r>Regen / n>Unstage)                   |
|-------------------------------------------------------------------------------------------------------------------------------|
    """
    
    parser = argparse.ArgumentParser(
        description="Generate and execute a git commit using OpenAI.",
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
        (['-m', '--model'], {'action': 'store_true', 'help': "Interactively select a custom OpenAI model from your available list."}),
        (['-p', '--push'], {'action': 'store_true', 'help': "Push after a successful commit."}),
        (['-r', '--review'], {'action': 'store_true', 'help': "Review message before committing [y/n/e/r]."}),
        (['-v', '--debug'], {'action': 'store_true', 'help': "Enable verbose logging for dependency manager."}),
        (['-w', '--watermark'], {'action': 'store_true', 'help': "Add 'Generated by OpenAI' signature to commit message."})
    ]
    
    # Sort by the first long option (starting with '--'), or first short if no long
    arg_specs.sort(key=lambda x: next((opt for opt in x[0] if opt.startswith('--')), x[0][0]))
    
    for flags, kwargs in arg_specs:
        parser.add_argument(*flags, **kwargs)
    
    args = parser.parse_args()

    # --- Model Selection ---
    target_model = "gpt-5"  # Default model
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
        print("📂 Staging all changes (git add .)...")
        try:
            run_git_with_ownership_fix(
                ['git', 'add', '.'],
                operation_description="staging all files",
                debug=args.debug
            )
            print("✅ All changes staged.\n")
        except subprocess.CalledProcessError as e:
            print(f"\n🚨 Failed to stage changes: {e}")
            sys.exit(1)
    
    # --- Prompt Generation ---
    alias_name = 'cinfoshort' if args.fill_placeholders else 'cinfocore'
    prompt = get_prompt_from_git(alias_name)
    
    if args.debug:
        print("\n🐛 [DEBUG] Generated Prompt Preview:")
        print(f"{prompt[:500]}...\n" if len(prompt) > 500 else f"{prompt}\n")
    
    # --- Regeneration Loop ---
    MAX_RETRIES = 2
    attempt = 0
    
    while attempt <= MAX_RETRIES:
        # Generate commit message
        commit_message = generate_commit_message(
            prompt, 
            include_signature=args.watermark,
            model_name=target_model
        )
        
        # Commit or review
        result = make_git_commit(
            commit_message, 
            dry_run=args.dry_run,
            review=args.review,
            push=args.push,
            add_all=(args.add_all or args.aa),
            can_regenerate=(attempt < MAX_RETRIES)
        )
        
        if result == 'regenerate':
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
