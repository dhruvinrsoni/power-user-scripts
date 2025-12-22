import sys
import subprocess
import importlib

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

def require(dependencies):
    """
    Ensures dependencies are installed using a Hierarchy of Trust.
    Auto-detects '--debug' in sys.argv for verbose logging.
    """
    # Check if the user passed --debug flag anywhere in the command line
    debug_mode = "--debug" in sys.argv
    
    if debug_mode:
        print(f"\n🛡️  [DepMgr] Security Scan & Dependency Check (Debug Mode ON)...")

    # Normalize Input
    targets = {}
    if isinstance(dependencies, list):
        for item in dependencies:
            targets[item] = None 
    elif isinstance(dependencies, dict):
        targets = dependencies
    else:
        print("🚨 [DepMgr] Error: Input must be a List or Dictionary.")
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
            pass 

        print(f"   🔻 Missing: '{import_name}'. Resolving Package Name...")

        # --- Resolution Logic ---
        candidate_name = None
        strategy = ""

        # Tier 2: User Explicit Override
        if explicit_install_name:
            candidate_name = explicit_install_name
            strategy = "User Override"
        
        # Tier 3: Internal Golden Map
        elif import_name in KNOWN_MAPPINGS:
            candidate_name = KNOWN_MAPPINGS[import_name]
            strategy = "Internal Golden Map"
        
        # Tier 4: Exact Name Match
        else:
            candidate_name = import_name
            strategy = "Standard Name Match"

        # --- Installation ---
        print(f"      🔎 Strategy: {strategy} -> Installing '{candidate_name}'...")
        
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", candidate_name],
                stdout=subprocess.DEVNULL if not debug_mode else None,
                stderr=subprocess.DEVNULL if not debug_mode else None
            )
            
            # Critical Verification
            try:
                importlib.import_module(import_name)
                print(f"      🎉 Success! '{candidate_name}' installed.")
                changes_made = True
            except ImportError:
                print(f"      ⚠️  Warning: Installed '{candidate_name}' but import failed.")
                sys.exit(1)

        except subprocess.CalledProcessError:
             print(f"\n🚨 [DepMgr] Error: Failed to install '{candidate_name}'.")
             sys.exit(1)

    if changes_made:
        print("🛡️  [DepMgr] Environment healed. Resuming script...\n")
    elif debug_mode:
        print("🛡️  [DepMgr] Environment healthy.\n")
