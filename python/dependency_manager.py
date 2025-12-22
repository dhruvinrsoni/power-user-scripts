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
    
    Args:
        dependencies: 
            - Can be a LIST of import names: ["requests", "yaml"]
            - Can be a DICT for explicit control: {"custom_mod": "custom-pkg-v2"}
            - Can be MIXED (not directly supported by python types, so use Dict for overrides)
    """
    print(f"\n🛡️  [DepMgr] Security Scan & Dependency Check...")

    # 1. Normalize Input to a Target Dictionary { import_name: explicit_install_name (or None) }
    targets = {}
    if isinstance(dependencies, list):
        for item in dependencies:
            targets[item] = None # No explicit override provided
    elif isinstance(dependencies, dict):
        targets = dependencies # User provided explicit overrides
    else:
        print("🚨 [DepMgr] Error: Input must be a List or Dictionary.")
        sys.exit(1)

    changes_made = False

    for import_name, explicit_install_name in targets.items():
        # --- Tier 1: The Integrity Check (Native Import) ---
        try:
            importlib.import_module(import_name)
            # If this succeeds, it's either standard lib (json, os) or already installed.
            # We do NOT print "Found" for every standard lib to keep logs clean, 
            # unless it was a recently installed one.
            continue 
        except ImportError:
            pass # Move to resolution logic

        print(f"   🔻 Missing: '{import_name}'. Resolving Package Name...")

        # --- Resolution Logic ---
        candidate_name = None
        source = ""

        # Tier 2: User Explicit Override
        if explicit_install_name:
            candidate_name = explicit_install_name
            source = "User Override"
        
        # Tier 3: Internal Golden Map
        elif import_name in KNOWN_MAPPINGS:
            candidate_name = KNOWN_MAPPINGS[import_name]
            source = "Internal Golden Map"
        
        # Tier 4: Exact Name Match (Standard Convention)
        else:
            candidate_name = import_name
            source = "Standard Name Match"

        # --- Installation Execution ---
        print(f"      🔎 Source: {source} -> Installing '{candidate_name}'...")
        
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", candidate_name],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            # Critical Step: Verify the install actually fixed the import
            try:
                importlib.import_module(import_name)
                print(f"      🎉 Success! '{candidate_name}' installed.")
                changes_made = True
            except ImportError:
                print(f"      ⚠️  Warning: Installed '{candidate_name}' but '{import_name}' is still missing.")
                print(f"      This implies the package name logic was incorrect.")
                
                # --- Tier 5: Heuristics (The "Hail Mary" - Optional/Risky) ---
                # We only try this if Tier 4 failed. 
                # For high security, you might strictly remove this block.
                # However, for convenience, we can try 2 common patterns.
                print(f"      🎲 Attempting Heuristic Fallbacks (Plan B)...")
                
                heuristics = [f"python-{import_name}", f"Py{import_name}"]
                heuristic_success = False
                
                for h_candidate in heuristics:
                    print(f"         🎲 Trying: {h_candidate}...")
                    try:
                        subprocess.check_call([sys.executable, "-m", "pip", "install", h_candidate], 
                                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        importlib.import_module(import_name)
                        print(f"         🎉 Heuristic Match! '{h_candidate}' worked.")
                        changes_made = True
                        heuristic_success = True
                        break
                    except:
                        continue
                
                if not heuristic_success:
                    print(f"\n🚨 [DepMgr] CRITICAL: Could not resolve dependency for '{import_name}'.")
                    print(f"   Please update your script to provide an explicit mapping:")
                    print(f"   dependency_manager.require({{ '{import_name}': 'correct-package-name' }})")
                    sys.exit(1)

        except subprocess.CalledProcessError:
             print(f"\n🚨 [DepMgr] Network/Pip Error: Failed to install '{candidate_name}'.")
             sys.exit(1)

    if changes_made:
        print("🛡️  [DepMgr] Environment healed. Resuming script...\n")
    # else: Silent success is better for CLI tools
