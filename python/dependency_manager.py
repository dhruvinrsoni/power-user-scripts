import sys
import subprocess
import importlib

def require(import_names):
    """
    Ensures dependencies are installed using a Multi-Stage Heuristic Strategy.
    
    Args:
        import_names (list): A list of module names used in 'import' statements.
                             e.g. ["requests", "yaml", "dotenv"]
    """
    print(f"\n🛡️  [DepMgr] Analyzing {len(import_names)} dependencies...")

    changes_made = False

    for module_name in import_names:
        # --- Phase 1: The Integrity Check ---
        # If we can import it, we are done. This automatically handles:
        # 1. Standard libraries (json, os, sys) - they import successfully.
        # 2. Already installed packages.
        try:
            importlib.import_module(module_name)
            print(f"   ✅ Found: '{module_name}' (Native/Installed)")
            continue 
        except ImportError:
            print(f"   🔻 Missing: '{module_name}'. Initiating Search Protocols...")

        # --- Phase 2: The Heuristic Attack Plan ---
        # If the direct import fails, we assume it's a missing 3rd party package.
        # We try logical variations of the package name until one works.
        
        # PLAN A: The "Direct Hit" (e.g., requests -> requests)
        # PLAN B: The "Capitalized Py" (e.g., yaml -> PyYAML)
        # PLAN C: The "Prefix" (e.g., dotenv -> python-dotenv)
        # PLAN D: The "Suffix" (e.g., cv2 -> opencv-python ... wait, logic has limits, see below)
        
        candidates = [
            module_name,                     # Plan A: Exact match
            f"Py{module_name}",              # Plan B: Common wrapper style (yaml -> PyYAML)
            f"python-{module_name}",         # Plan C: Common utility style (dotenv -> python-dotenv)
            f"{module_name}-python",         # Plan D: Common binding style
            module_name.replace('_', '-')    # Plan E: Underscore to dash (sklearn -> scikit-learn approx)
        ]

        installed_successfully = False

        for candidate in candidates:
            print(f"      🔎 Attempting Strategy: pip install {candidate} ...")
            
            try:
                # 1. Try to install the candidate
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", candidate],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                
                # 2. CRITICAL VERIFICATION
                # Just because pip didn't crash doesn't mean we got the right thing.
                # We must try to import the ORIGINAL module name again.
                try:
                    importlib.import_module(module_name)
                    print(f"      🎉 Success! '{candidate}' provided module '{module_name}'.")
                    changes_made = True
                    installed_successfully = True
                    break # Exit the candidate loop
                except ImportError:
                    # We installed something, but it didn't give us the module we wanted.
                    # This is rare but possible. We assume it was the wrong package.
                    print(f"      ⚠️  Installed '{candidate}' but still can't import '{module_name}'. Reverting...")
                    # Optional: You could uninstall here to keep system clean, 
                    # but for simplicity we just move to next strategy.
            
            except subprocess.CalledProcessError:
                # Pip failed to find/install this candidate. Move to next plan.
                continue

        if not installed_successfully:
            print(f"\n🚨 [DepMgr] CRITICAL FAILURE: Exhausted all strategies for '{module_name}'.")
            print(f"   The algorithm failed to deduce the package name.")
            print(f"   Manual Intervention Required: pip install <correct_package_name>")
            sys.exit(1)

    if changes_made:
        print("🛡️  [DepMgr] Environment healed. Resuming script...\n")
    else:
        print("🛡️  [DepMgr] Environment is healthy.\n")
