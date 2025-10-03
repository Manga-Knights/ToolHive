# SPDX-License-Identifier: GPL-3.0-or-later
# ToolHive Renamer setup
# Copyright (C) 2025 Manga-Knights
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See https://www.gnu.org/licenses/gpl-3.0.en.html for details.




import subprocess
import sys
import os
import importlib.util

MAIN_SCRIPT = "renamer.py"

# --- Step 0: Check Python version ---
MIN_PYTHON = (3, 9)
if sys.version_info < MIN_PYTHON:
    sys.stderr.write(f"ERROR: Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+ is required.\n")
    sys.exit(1)

# --- Step 1: Required dependencies ---
REQUIRED = {
    "launcherlib": None,  # local file, ensure presence
    "natsort": "8.4.0"
}

def ensure_package(pkg, version=None):
    target = f"{pkg}=={version}" if version else pkg
    try:
        import importlib.metadata as importlib_metadata
        try:
            installed = importlib_metadata.version(pkg)
            if version and installed != version:
                print(f"[!] {pkg} version mismatch: installed {installed}, expected {version}")
                subprocess.check_call([sys.executable, "-m", "pip", "install", target])
            else:
                print(f"[+] {pkg} is present (version: {installed})")
        except importlib_metadata.PackageNotFoundError:
            print(f"[!] {pkg} not installed. Installing {target} ...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", target])
    except Exception:
        print(f"[!] Could not check {pkg} via importlib.metadata. Installing {target} ...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", target])

print("Checking dependencies...\n")
for pkg, version in REQUIRED.items():
    if pkg != "launcherlib":  # skip local file
        try:
            ensure_package(pkg, version)
        except Exception as e:
            print(f"[!] Failed to ensure {pkg}: {e}")
print("\n✅ Dependency checks complete.\n")

# --- Step 2: Locate and import launcherlib dynamically ---
def find_and_import_launcherlib():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    while True:
        candidate = os.path.join(current_dir, "launcherlib.py")
        if os.path.isfile(candidate):
            sys.path.append(current_dir)
            spec = importlib.util.spec_from_file_location("launcherlib", candidate)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            sys.modules["launcherlib"] = module
            return module
        parent = os.path.dirname(current_dir)
        if parent == current_dir:  # reached root
            sys.exit("ERROR: launcherlib.py not found in current or parent folders.")
        current_dir = parent

launcherlib = find_and_import_launcherlib()
print("✅ launcherlib.py successfully imported.\n")

# --- Step 3: Flip setup_incomplete flag safely ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
target_file = os.path.join(BASE_DIR, MAIN_SCRIPT)

if os.path.exists(target_file):
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        with open(target_file, "w", encoding="utf-8") as f:
            flipped = False
            for line in lines:
                if line.strip() == "setup_incomplete = True":
                    f.write("setup_incomplete = False\n")
                    flipped = True
                else:
                    f.write(line)
        if flipped:
            print(f"✅ Flipped setup_incomplete from True → False in {target_file}")
        else:
            print(f"⚠️ setup_incomplete was not True; flag not modified.")
    except Exception as e:
        print(f"[!] Could not update {target_file}: {e}")
else:
    print(f"[!] Warning: {target_file} not found. Skipping flag update.")

# --- Step 4: Victory message ---
print(rf"""
🎉 Setup complete! 🎉
You may now run {MAIN_SCRIPT} safely.
""")

# --- Step 5: Auto-run main script ---
try:
    print(f"\n🚀 Launching {MAIN_SCRIPT} ...\n")
    subprocess.check_call([sys.executable, target_file])
except Exception as e:
    print(f"[!] Could not launch {MAIN_SCRIPT}: {e}")
    sys.exit(1)
