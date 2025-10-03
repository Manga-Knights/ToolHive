# Run this script to check and install dependencies for the OCR tool.
# It will suggest installations if something is missing or mismatched.
# Make sure you have internet access if you choose to install any packages.

import subprocess
import sys
from importlib.util import find_spec
from importlib.metadata import version, PackageNotFoundError
import shutil
from pathlib import Path

DEPENDENCIES = [
    {
        "name": "Pillow",
        "package": "Pillow",
        "module": "PIL",
        "version": "11.3.0",
        "install_cmd": "pip install Pillow==11.3.0",
        "note": "Used for image handling (reading, processing, drawing boxes/text etc.)"
    },
    {
        "name": "tqdm",
        "package": "tqdm",
        "module": "tqdm",
        "version": "4.67.1",
        "install_cmd": "pip install tqdm==4.67.1",
        "note": "Used for progress bars during folder processing"
    },
    {
        "name": "natsort",
        "package": "natsort",
        "module": "natsort",
        "version": "8.4.0",
        "install_cmd": "pip install natsort==8.4.0",
        "note": "Used for naturally sorting file names"
    },
    {
        "name": "PyPDF2",
        "package": "PyPDF2",
        "module": "PyPDF2",
        "version": "3.0.1",
        "install_cmd": "pip install PyPDF2==3.0.1",
        "note": "Used for merging multiple PDFs together"
    },
    {
        "name": "img2pdf",
        "package": "img2pdf",
        "module": "img2pdf",
        "version": "0.5.1",
        "install_cmd": "pip install img2pdf==0.5.1",
        "note": "Used for generating image-only PDFs"
    },
    {
        "name": "reportlab",
        "package": "reportlab",
        "module": "reportlab",
        "version": "4.4.3",
        "install_cmd": "pip install reportlab==4.4.3",
        "note": "Used for overlaying OCR text and rectangles"
    },
    {
        "name": "pytesseract",
        "package": "pytesseract",
        "module": "pytesseract",
        "version": "0.3.13",
        "install_cmd": "pip install pytesseract==0.3.13",
        "note": "Python wrapper for Tesseract OCR (requires Tesseract executable)"
    },
    {
        "name": "paddleocr",
        "package": "paddleocr",
        "module": "paddleocr",
        "version": "3.2.0.dev23",
        "install_cmd": "pip install git+https://github.com/PaddlePaddle/PaddleOCR.git@develop",
        "note": "Used for PaddleOCR (detect + recognize text)"
    },
    {
        "name": "paddlepaddle",
        "package": "paddlepaddle",
        "module": "paddle",
        "version": "3.1.0",
        "install_cmd": "pip install paddlepaddle==3.1.0",
        "note": "Backend engine for PaddleOCR"
    },
    {
        "name": "launcherlib",
        "package": None,
        "module": "launcherlib",
        "version": None,
        "install_cmd": None,
        "note": "Custom utility module (must exist one directory up as launcherlib.py)"
    },
]

def check_and_install(dep):
    name = dep["name"]
    pkg = dep["package"]
    module = dep["module"]
    expected = dep["version"]
    note = dep["note"]

    print(f"\n📦 {name}")

    # --- Special handling for launcherlib ---
    if name == "launcherlib":
        parent_dir = Path(__file__).resolve().parent.parent
        lib_path = parent_dir / "launcherlib.py"

        if lib_path.exists():
            print(f"✔️ Found launcherlib at: {lib_path}")
        else:
            print("❌ launcherlib.py not found in parent directory.")
            print("Expected path:", lib_path)
            print(note)
        return

    # --- Normal dependency check ---
    try:
        if not find_spec(module):
            raise ModuleNotFoundError
        installed_version = version(pkg)
        if not installed_version.startswith(expected):
            print(f"⚠️  Version mismatch: installed {installed_version}, expected {expected}")
            print(f"Installing required version: {expected}")
            subprocess.run(dep["install_cmd"], shell=True)
        else:
            print(f"✔️  Already installed. Version: {installed_version}")
    except (PackageNotFoundError, ModuleNotFoundError):
        print(f"❌ Not installed.")
        print(note)
        print(f"Installing version: {expected}")
        subprocess.run(dep["install_cmd"], shell=True)

def check_tesseract():
    """Verify that Tesseract executable is installed."""
    print("\n🔍 Checking Tesseract OCR executable...")
    if shutil.which("tesseract") is None:
        print("❌ Tesseract not found on system PATH.")
        print("Download and install Tesseract OCR: https://github.com/tesseract-ocr/tesseract")
        print("After installation, ensure 'tesseract' is in your PATH.")
    else:
        print("✔️ Tesseract executable found.")

if __name__ == "__main__":
    print("📋 Dependency Checker & Installer\n")
    for dep in DEPENDENCIES:
        check_and_install(dep)
    check_tesseract()
    print("\n✅ All checks complete. Your main script is ready to run!")
