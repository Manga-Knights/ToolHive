# SPDX-License-Identifier: GPL-3.0-or-later
# ToolHive Manual Sorter setup
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

MAIN_SCRIPT = "manual_sorter.py"

# --- Step 0: Check Python version ---
MIN_PYTHON = (3, 9)
if sys.version_info < MIN_PYTHON:
    sys.stderr.write(f"ERROR: Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+ is required.\n")
    sys.exit(1)

# --- Step 1: Required dependencies ---
REQUIRED = {
    "launcherlib": None,  # just ensure presence
    "PyQt5": "5.15.11"
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
    try:
        ensure_package(pkg, version)
    except Exception as e:
        print(f"[!] Failed to ensure {pkg}: {e}")
print("\n✅ Dependency checks complete.\n")

# --- Step 2: Locate launcherlib.py dynamically 2 directories above ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
two_levels_up = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))
launcherlib_path = os.path.join(two_levels_up, "launcherlib.py")

if not os.path.exists(launcherlib_path):
    sys.exit(f"ERROR: launcherlib.py not found 2 directories above ({two_levels_up})")

# Add the folder containing launcherlib.py to sys.path
if two_levels_up not in sys.path:
    sys.path.insert(0, two_levels_up)

print(f"✅ Found launcherlib.py at {launcherlib_path}\n")

# --- Step 3: Flip setup_incomplete flag in main script ---
target_file = os.path.join(BASE_DIR, MAIN_SCRIPT)
if os.path.exists(target_file):
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        with open(target_file, "w", encoding="utf-8") as f:
            replaced = False
            for line in lines:
                if line.strip().startswith("setup_incomplete"):
                    f.write("setup_incomplete = False\n")
                    replaced = True
                else:
                    f.write(line)
        if replaced:
            print(f"✅ Updated setup_incomplete flag in {target_file}")
        else:
            print(f"⚠️ No setup_incomplete assignment found in {target_file}; skipping flag update.")
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
