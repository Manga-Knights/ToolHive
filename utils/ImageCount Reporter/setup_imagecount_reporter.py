import subprocess
import sys
import os

MAIN_SCRIPT = "imagecount_reporter.py"

# --- Step 0: Check Python version ---
MIN_PYTHON = (3, 9)
if sys.version_info < MIN_PYTHON:
    sys.stderr.write(f"ERROR: Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+ is required.\n")
    sys.exit(1)

# --- Step 1: Locate launcherlib.py exactly 2 directories above ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
two_up_dir = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))
launcherlib_path = os.path.join(two_up_dir, "launcherlib.py")

if not os.path.exists(launcherlib_path):
    sys.exit(f"ERROR: launcherlib.py not found 2 directories above {BASE_DIR} (checked {two_up_dir}).")
print(f"✅ Found launcherlib.py at {launcherlib_path}\n")

# Add its folder to sys.path for import
sys.path.insert(0, two_up_dir)
import launcherlib

# --- Step 2: Flip setup_incomplete flag in main script safely ---
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

# --- Step 3: Victory message ---
print(rf"""
🎉 Setup complete! 🎉
You may now run {MAIN_SCRIPT} safely.
""")

# --- Step 4: Auto-run main script ---
try:
    print(f"\n🚀 Launching {MAIN_SCRIPT} ...\n")
    subprocess.check_call([sys.executable, target_file])
except Exception as e:
    print(f"[!] Could not launch {MAIN_SCRIPT}: {e}")
