"""
🛡️ Dependency Manager (Self-Healing Environment Engine)
------------------------------------------------------
A drop-in module to ensure Python scripts automatically install their own 
dependencies before execution. It uses a "Hierarchy of Trust" security model 
to prevent dependency confusion attacks.

Usage:
    import dependency_manager

    # Method 1: The Smart List (Recommended)
    # Automatically resolves pip names using the Internal Golden Map.
    dependency_manager.require(["requests", "cv2", "yaml"])

    # Method 2: The Explicit Override (For private packages or version pinning)
    dependency_manager.require({
        "my_module": "my-private-package>=1.0.0",
        "legacy_lib": "legacy-pkg==2.4.1"
    })

Debug Mode:
    Run your main script with '--debug' to see verbose installation logs.
    e.g., python my_script.py --debug
"""

import sys
import subprocess
import importlib
from typing import Union, List, Dict

# --- 📚 Tier 3: The Internal "Golden" Knowledge Base ---
# A comprehensive, vetted list of packages where Import Name != Install Name.
# This prevents the script from guessing wrong for known community packages.
KNOWN_MAPPINGS = {
    # Image Processing
    "cv2": "opencv-python",
    "PIL": "Pillow",
    "skimage": "scikit-image",
    
    # Data Science & ML
    "sklearn": "scikit-learn",
    "yaml": "PyYAML",
    "bs4": "beautifulsoup4",
    
    # Utilities
    "dotenv": "python-dotenv",
    "dateutil": "python-dateutil",
    "jwt": "PyJWT",
    "usb": "pyusb",
    "serial": "pyserial",
    "docx": "python-docx",
    "websocket": "websocket-client",
    "crypto": "pycryptodome",
    "dns": "dnspython",
    
    # Add more vetted mappings here as you discover them.
}

def require(dependencies: Union[List[str], Dict[str, str]]) -> None:
    """
    Ensures dependencies are installed using a Hierarchy of Trust.
    Auto-detects '--debug' in sys.argv for verbose logging.

    Args:
        dependencies: 
            List[str]: e.g., ["requests", "cv2"]
            Dict[str, str]: e.g., {"import_name": "install_name"}
    """
    # Check if the user passed --debug flag anywhere in the command line
    debug_mode = "--debug" in sys.argv
    
    if debug_mode:
        print(f"\n🛡️  [DepMgr] Security Scan & Dependency Check (Debug Mode ON)...")

    # Normalize Input to a Target Dictionary
    targets = {}
    if isinstance(dependencies, list):
        for item in dependencies:
            targets[item] = None # Logic will rely on Golden Map or Standard Name
    elif isinstance(dependencies, dict):
        targets = dependencies   # User provided explicit overrides
    else:
        print("🚨 [DepMgr] Error: Input must be a List (smart) or Dictionary (explicit).")
        sys.exit(1)

    changes_made = False

    for import_name, explicit_install_name in targets.items():
        # --- Tier 1: The Integrity Check (Native Import) ---
        try:
            importlib.import_module(import_name)
            if debug_mode:
                print(f"   ✅ Found: '{import_name}' [Strategy: Native/Installed]")
            continue 
        except ImportError:
            pass # Move to resolution logic

        if debug_mode:
            print(f"   🔻 Missing: '{import_name}'. Resolving Package Name...")

        # --- Resolution Logic ---
        candidate_name = None
        strategy = ""

        # Tier 2: User Explicit Override (Highest Priority after Native)
        if explicit_install_name:
            candidate_name = explicit_install_name
            strategy = "User Override"
        
        # Tier 3: Internal Golden Map (Community Vetted)
        elif import_name in KNOWN_MAPPINGS:
            candidate_name = KNOWN_MAPPINGS[import_name]
            strategy = "Internal Golden Map"
        
        # Tier 4: Exact Name Match (Standard Convention)
        else:
            candidate_name = import_name
            strategy = "Standard Name Match"

        # --- Installation Execution ---
        if debug_mode:
            print(f"      🔎 Strategy: {strategy} -> Installing '{candidate_name}'...")
        
        try:
            # We use sys.executable to ensure we install to the RUNNING environment.
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", candidate_name],
                stdout=subprocess.DEVNULL if not debug_mode else None,
                stderr=subprocess.DEVNULL if not debug_mode else None
            )
            
            # Critical Verification: Did the install actually fix the import?
            try:
                importlib.import_module(import_name)
                if debug_mode:
                    print(f"      🎉 Success! '{candidate_name}' installed.")
                changes_made = True
            except ImportError:
                print(f"      ⚠️  Warning: Installed '{candidate_name}' successfully, but 'import {import_name}' still failed.")
                print(f"      Possible Cause: The package name '{candidate_name}' does not provide the module '{import_name}'.")
                print(f"      Fix: Use dictionary syntax: dependency_manager.require({{'{import_name}': 'correct-package-name'}})")
                sys.exit(1)

        except subprocess.CalledProcessError:
             print(f"\n🚨 [DepMgr] Error: Failed to install '{candidate_name}'.")
             print(f"   Check your internet connection or package name spelling.")
             sys.exit(1)

    if changes_made:
        print("🛡️  [DepMgr] Environment healed. Resuming script...\n")
    elif debug_mode:
        print("🛡️  [DepMgr] Environment healthy.\n")
