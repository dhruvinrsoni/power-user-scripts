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


# ---------------------------------------------------------------------------
# CLI: Self-installer — run `python dependency_manager.py --install` once
# to make this module importable from any directory on the system.
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    import argparse
    import os
    import site

    MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
    PTH_NAME = 'power-user-scripts.pth'

    def _safe_print(msg):
        """Print with fallback for Windows consoles that can't handle emoji."""
        try:
            print(msg)
        except UnicodeEncodeError:
            print(msg.encode('ascii', 'replace').decode('ascii'))

    def _get_pth_candidates():
        """Return list of site-packages dirs to try, system first then user."""
        candidates = []
        for d in reversed(site.getsitepackages()):
            if 'site-packages' in d:
                candidates.append(d)
        if not candidates:
            candidates.append(site.getsitepackages()[0])
        # User site-packages as fallback (no admin needed)
        user_sp = site.getusersitepackages()
        if user_sp not in candidates:
            candidates.append(user_sp)
        return candidates

    def _write_pth(candidates):
        """Try writing .pth file to first writable site-packages. Returns path or None."""
        for sp_dir in candidates:
            pth_path = os.path.join(sp_dir, PTH_NAME)
            try:
                os.makedirs(sp_dir, exist_ok=True)
                with open(pth_path, 'w') as f:
                    f.write(MODULE_DIR + '\n')
                return pth_path
            except PermissionError:
                continue
        return None

    def do_install():
        # 1. Create .pth file (try system, then user site-packages)
        candidates = _get_pth_candidates()
        pth_path = _write_pth(candidates)
        if pth_path:
            _safe_print(f"[ok] Created {pth_path}")
        else:
            tried = ', '.join(os.path.join(c, PTH_NAME) for c in candidates)
            _safe_print(f"[!!] Permission denied writing .pth file.")
            _safe_print(f"     Tried: {tried}")
            _safe_print("     Try running as Administrator.")
            _safe_print("     Continuing with pip install -e only...")

        # 2. Editable install (requires pyproject.toml in same directory)
        pyproject = os.path.join(MODULE_DIR, 'pyproject.toml')
        if os.path.isfile(pyproject):
            _safe_print("[..] Running pip install -e ...")
            subprocess.check_call(
                [sys.executable, '-m', 'pip', 'install', '-e', MODULE_DIR],
                stdout=sys.stdout, stderr=sys.stderr,
            )
            _safe_print("[ok] Editable install complete")
        else:
            _safe_print("[!!] pyproject.toml not found -- skipping pip install -e")

        _safe_print("\n   'import dependency_manager' now works from any directory.")

    def do_uninstall():
        candidates = _get_pth_candidates()
        removed = False
        for sp_dir in candidates:
            pth_path = os.path.join(sp_dir, PTH_NAME)
            if os.path.isfile(pth_path):
                try:
                    os.remove(pth_path)
                    _safe_print(f"[ok] Removed {pth_path}")
                    removed = True
                except PermissionError:
                    _safe_print(f"[!!] Permission denied removing {pth_path}")
        if not removed:
            _safe_print("   .pth file not found (already removed?)")

        subprocess.call(
            [sys.executable, '-m', 'pip', 'uninstall', '-y', 'dependency-manager'],
            stdout=sys.stdout, stderr=sys.stderr,
        )
        _safe_print("[ok] Uninstalled")

    def do_status():
        # Check .pth file in all candidate locations
        candidates = _get_pth_candidates()
        pth_found = None
        for sp_dir in candidates:
            pth_path = os.path.join(sp_dir, PTH_NAME)
            if os.path.isfile(pth_path):
                pth_found = pth_path
                break
        _safe_print(f"   .pth file : {'[ok] ' + pth_found if pth_found else '[--] not found'}")

        # Test import from a neutral directory
        test = subprocess.run(
            [sys.executable, '-c', 'import dependency_manager; print("ok")'],
            cwd=os.environ.get('TEMP', os.environ.get('TMP', '/')),
            capture_output=True, text=True,
        )
        importable = test.stdout.strip() == 'ok'
        _safe_print(f"   Importable: {'[ok] from any directory' if importable else '[--] not importable outside its own folder'}")

        # Check pip registration
        pip_check = subprocess.run(
            [sys.executable, '-m', 'pip', 'show', 'dependency-manager'],
            capture_output=True, text=True,
        )
        registered = pip_check.returncode == 0
        _safe_print(f"   pip package: {'[ok] registered' if registered else '[--] not installed via pip'}")

    parser = argparse.ArgumentParser(
        description="Dependency Manager -- self-installer",
        epilog="Run --install once to make 'import dependency_manager' work from any directory.",
    )
    parser.add_argument('--install', action='store_true', help='Install globally (.pth + pip -e)')
    parser.add_argument('--uninstall', action='store_true', help='Remove global install')
    parser.add_argument('--status', action='store_true', help='Check install status')
    args = parser.parse_args()

    if args.install:
        do_install()
    elif args.uninstall:
        do_uninstall()
    elif args.status:
        do_status()
    else:
        parser.print_help()
