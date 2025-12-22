import sys
import subprocess
import importlib

def require(dependency_map):
    """
    Ensures that a list of dependencies are installed.
    
    Args:
        dependency_map (dict): A dictionary where keys are the 'import name' 
                               and values are the 'pip package name'.
                               Example: { "yaml": "PyYAML", "requests": "requests" }
    """
    installed_any = False
    
    print("🛡️  Dependency Manager: Checking environment...")

    for import_name, install_name in dependency_map.items():
        try:
            importlib.import_module(import_name)
        except ImportError:
            print(f"📦 Missing module '{import_name}'. Auto-installing '{install_name}'...")
            try:
                # Install to the current environment
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", install_name],
                    stdout=subprocess.DEVNULL, # Keep it clean
                    stderr=subprocess.DEVNULL
                )
                print(f"✅ Installed '{install_name}'.")
                installed_any = True
            except subprocess.CalledProcessError:
                print(f"🚨 Error: Failed to install '{install_name}'.")
                sys.exit(1)

    if installed_any:
        print("🎉 Environment healed. Resuming script...\n")
    # No else needed; silence is golden if everything is fine.
