import sys
import subprocess
import importlib

def require(dependencies):
    """
    Ensures that a list of dependencies are installed.
    
    Args:
        dependencies: Can be a LIST of strings or a DICTIONARY.
                      - List: ['requests', 'pandas'] 
                        (Assumes pip package name is same as import name)
                      - Dict: {'cv2': 'opencv-python', 'yaml': 'PyYAML'}
                        (Maps import name to specific pip package name)
    """
    print(f"\n🛡️  [DepMgr] Starting dependency check...")
    
    # Normalize input to a dictionary
    # If it's a list ['a', 'b'], convert to {'a':'a', 'b':'b'}
    if isinstance(dependencies, list):
        target_map = {item: item for item in dependencies}
    elif isinstance(dependencies, dict):
        target_map = dependencies
    else:
        print("🚨 [DepMgr] Error: Invalid input format. Expected List or Dict.")
        sys.exit(1)

    changes_made = False

    for import_name, install_name in target_map.items():
        # Step 1: Check if installed
        try:
            importlib.import_module(import_name)
            print(f"   ✅ Found: '{import_name}'")
        except ImportError:
            # Step 2: Not found, attempt install
            print(f"   📦 Missing: '{import_name}'. Auto-installing '{install_name}'...")
            try:
                # Run pip install
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", install_name],
                    stdout=subprocess.DEVNULL, # Hide the noisy download logs
                    stderr=subprocess.DEVNULL
                )
                print(f"   🎉 Installed: '{install_name}' successfully.")
                changes_made = True
            except subprocess.CalledProcessError:
                print(f"\n🚨 [DepMgr] CRITICAL FAILURE: Could not install '{install_name}'.")
                print(f"   Please check your internet or run: pip install {install_name}")
                sys.exit(1)

    if changes_made:
        print("🛡️  [DepMgr] Environment healed. Resuming script...\n")
    else:
        print("🛡️  [DepMgr] Environment is healthy. No changes needed.\n")
