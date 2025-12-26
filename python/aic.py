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
    print("\n🚨 Error: GOOGLE_API_KEY environment variable not set.")
    sys.exit(1)

# --- Main Functions ---

def interactive_add(debug_mode=False):
    """
    Triggers 'git adi' (interactive fzf staging) with improved UX.
    Shows status before and summary after.
    """
    print("\n✅ --interactive-add flag detected.")
    
    # 1. Pre-Flight: Show user what is available
    print("\n📂 Current Status (Untracked/Modified):")
    try:
        # -s: Short format, -b: Show branch info
        subprocess.run(['git', 'status', '-sb', '-uall'], check=True)
    except subprocess.CalledProcessError:
        pass # Ignore errors here, fzf will handle the main logic
        
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

def generate_commit_message(prompt, include_signature=True):
    """Sends prompt to Gemini API."""
    print("✨ Asking Gemini to generate the commit message...")
    
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

    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
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
    except Exception as e:
        print(f"\n🚨 An error occurred with the Gemini API: {e}")
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
        
        # Display 'g' option only if regeneration is allowed (token guardrail)
        options_text = "(y/n/e/g)" if can_regenerate else "(y/n/e)"
        print(f"Proceed with this commit? {options_text}: ", end='', flush=True)
        
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
        elif can_regenerate and key_press.lower() == b'g':
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
    # epilog_text = """
                     # Usage Examples & Workflows
# -------------------------------------------------------------------------------------------------------------------------------
# | Command      | Use Case                                  | User Flow Visualization                                                                 |
# |--------------|-------------------------------------------|-----------------------------------------------------------------------------------------|
# | git aic      | Quick Commit (files already staged)       | ✨ AI Generates ➔ ✅ Commit                                                                 |
# | git aic file | Stage specific file(s) & Commit          | ➕ git add file ➔ ✨ AI Generates ➔ ✅ Commit                                              |
# | git aic -d   | Dry Run (see message only)                | ✨ AI Generates ➔ 🧪 Show Message                                                           |
# | git aic -i   | Interactive Staging & Commit              | ➕ Select Files (fzf) ➔ ✨ AI Generates ➔ ✅ Commit                                       |
# | git aic -a   | Add All & Commit (stage everything)       | ➕ Add All ➔ ✨ AI Generates ➔ ✅ Commit                                                  |
# |--------------|-------------------------------------------|-----------------------------------------------------------------------------------------|
# | git aic -ir  | Interactively Stage, then Review          | ➕ Select Files (fzf) ➔ ✨ AI... ➔ 🔎 Review (y➔✅ Commit / e➔📝 Edit / n➔❌ Abort) |
# | git aic -ar  | Add All, then Review                      | ➕ Add All ➔ ✨ AI... ➔ 🔎 Review (y➔✅ Commit / e➔📝 Edit / n➔🧹 Unstage)         |
# | git aic -ap  | The "One-Shot" (add, commit, push)        | ➕ Add All ➔ ✨ AI... ➔ ✅ Commit ➔ 🚀 Push                                                |
# | git aic -ad  | Safe Preview (see msg for all changes)    | ➕ Add All ➔ ✨ AI... ➔ 🧪 Show ➔ 🧹 Unstage                                                  |
# |--------------|-------------------------------------------|-----------------------------------------------------------------------------------------|
# | git aic -irp | Ultimate Control Workflow                 | ➕ Select Files (fzf) ➔ ✨ AI... ➔ 🔎 Review ➔ ✅ Commit ➔ 🚀 Push                   |
# | git aic -arp | Ultimate Automation Workflow                | ➕ Add All ➔ ✨ AI... ➔ 🔎 Review (n➔🧹 Unstage) ➔ ✅ Commit ➔ 🚀 Push       |
# -------------------------------------------------------------------------------------------------------------------------------
    # """
    epilog_text = """
                      Usage Examples & Workflows
|-------------------------------------------------------------------------------------------------------------------------------|
| Command      | Use Case                                 | User Flow Visualization                                             |
|--------------|------------------------------------------|---------------------------------------------------------------------|
| git aic      | Quick Commit (files already staged)      | ✨ AI Generates ➔ ✅ Commit                                         |
| git aic file | Stage specific file(s) & Commit          | ➕ git add file ➔ ✨ AI Generates ➔ ✅ Commit                      |
| git aic -d   | Dry Run (see message only)               | ✨ AI Generates ➔ 🧪 Show Message                                   |
| git aic -r   | Review & Commit (approve AI message)     | ✨ AI Generates ➔ 🔎 Review                                         |
|              |                                          | (y➔✅ Commit / e➔📝 Edit / g➔🔄 Regen / n➔❌ Abort)                |
| git aic -i   | Interactive Staging & Commit             | ➕ Select Files (fzf) ➔ ✨ AI Generates ➔ ✅ Commit                 |
| git aic -a   | Add & Commit (stage and commit)          | ➕ Add All ➔ ✨ AI Generates ➔ ✅ Commit                            |
| git aic -p   | Commit & Push (commit staged, then push) | ✨ AI Generates ➔ ✅ Commit ➔ 🚀 Push                               |
|--------------|------------------------------------------|---------------------------------------------------------------------|
| git aic -ar  | Add & Review (stage all, then approve)   | ➕ Add All ➔ ✨ AI... ➔ 🔎 Review                                   |
|              |                                          | (y➔✅ Commit / e➔📝 Edit / g➔🔄 Regen / n➔🧹 Unstage)              |
| git aic -ir  | Interactively Stage, then Review         | ➕ Select Files (fzf) ➔ ✨ AI... ➔ 🔎 Review                        |
|              |                                          | (y➔✅ Commit / e➔📝 Edit / g➔🔄 Regen / n➔❌ Abort)                 |
| git aic -ap  | The "One-Shot" (add, commit, push)       | ➕ Add All ➔ ✨ AI... ➔ ✅ Commit ➔ 🚀 Push                         |
| git aic -ad  | Safe Preview (see msg for all changes)   | ➕ Add All ➔ ✨ AI... ➔ 🧪 Show ➔ 🧹 Unstage                        |
| git aic -rp  | Review & Push (approve msg, then push)   | ✨ AI... ➔ 🔎 Review                                                |
|              |                                          | (y➔✅ Commit ➔ 🚀 Push / e➔📝 Edit / g➔🔄 Regen / n➔❌ Abort)       |
|--------------|------------------------------------------|---------------------------------------------------------------------|
| git aic -irp | Ultimate Control Workflow                | ➕ Select Files (fzf) ➔ ✨ AI... ➔ 🔎 Review ➔ ✅ Commit ➔ 🚀 Push |
| git aic -arp | The Ultimate Workflow                    | ➕ Add All ➔ ✨ AI... ➔ 🔎 Review                                   |
|              |                                          | (y➔✅ Commit ➔ 🚀 Push / e➔📝 Edit / g➔🔄 Regen / n➔🧹 Unstage)     |
|-------------------------------------------------------------------------------------------------------------------------------|
    """
    
    parser = argparse.ArgumentParser(
        description="Generate and execute a git commit using AI.",
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
        (['--debug'], {'action': 'store_true', 'help': "Enable verbose logging for dependency manager."}),
        (['--fill-placeholders'], {'action': 'store_true', 'help': "Prompt to fill placeholders in the cinfo prompt for additional context."}),
        (['-i', '--interactive-add'], {'action': 'store_true', 'help': "Interactively stage files using 'git adi' (fzf)."}),
        (['-p', '--push'], {'action': 'store_true', 'help': "Push after a successful commit."}),
        (['-r', '--review'], {'action': 'store_true', 'help': "Review message before committing [y/n/e/g]."}),
        (['-W', '--no-watermark'], {'action': 'store_true', 'help': "Do not add the 'Generated by Gemini' footer."}),
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
            # We append '-v' to see verbose output of what git is adding
            subprocess.run(['git', 'add', '-v'] + args.files, check=True)
            print("---")
        except subprocess.CalledProcessError:
            print("🚨 Error: Could not add specified files. Check filenames and try again.")
            sys.exit(1)

    # 2. Check for other staging flags
    if args.interactive_add:
        # Pass the debug flag to the function
        interactive_add(debug_mode=args.debug)
    elif args.add_all or args.aa:
        print("\n✅ --add-all flag detected. Staging all changes...")
        subprocess.run(['git', 'add', '.', '-v'], check=True)
        print("---")

    if subprocess.run(['git', 'diff', '--staged', '--quiet']).returncode == 0:
        print("\n🤷 No changes staged for commit. Use 'git add' or pass filenames to this script.")
        sys.exit(0)
    
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
        else:
            if placeholders:
                # Prompt for each placeholder value
                filled_values = {}
                print("\nEnter values for each placeholder (press Enter to skip):")
                for ph in placeholders:
                    value = input(f"{ph} ").strip()
                    filled_values[ph] = value
                
                # Replace empty lines after placeholders in the prompt
                lines = prompt.split('\n')
                new_lines = []
                i = 0
                while i < len(lines):
                    line = lines[i]
                    new_lines.append(line)
                    for ph in placeholders:
                        if ph in line and filled_values[ph]:
                            # Check if next line is empty
                            if i + 1 < len(lines) and lines[i + 1].strip() == '':
                                new_lines.append(filled_values[ph])
                                i += 1  # Skip the empty line
                                break
                    i += 1
                prompt = '\n'.join(new_lines)
    
    # --- RETRY LOGIC (Max 2 Retries = 3 total generations) ---
    MAX_RETRIES = 2
    attempts_done = 0
    
    while True:
        # Pass the INVERSE.
        # If --no-watermark is True, include_signature becomes False.
        commit_message = generate_commit_message(prompt, include_signature=not args.no_watermark)
        
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
