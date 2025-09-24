import subprocess
import sys
import os

MAIN_SCRIPT = "imagecount_reporter.py"

# --- Step 0: Check Python version ---
MIN_PYTHON = (3, 9)
if sys.version_info < MIN_PYTHON:
    sys.stderr.write(f"ERROR: Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+ is required.\n")
    sys.exit(1)

# --- Step 1: Required dependencies ---
REQUIRED = {
    "launcherlib": None  # just ensure presence
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

# --- Step 2: Locate launcherlib.py dynamically in 'tool hive' folder ---
def find_launcherlib(start_dir):
    dir_to_check = os.path.abspath(start_dir)
    while True:
        if os.path.basename(dir_to_check).lower() == "tool hive":
            candidate = os.path.join(dir_to_check, "launcherlib.py")
            if os.path.exists(candidate):
                return candidate
            else:
                return None
        parent = os.path.dirname(dir_to_check)
        if parent == dir_to_check:  # reached root
            return None
        dir_to_check = parent

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
launcherlib_path = find_launcherlib(BASE_DIR)
if not launcherlib_path:
    sys.exit("ERROR: launcherlib.py not found in 'tool hive' folder.")
print(f"✅ Found launcherlib.py at {launcherlib_path}\n")

# --- Step 3: Flip setup_incomplete flag in image_flattener.py ---
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
