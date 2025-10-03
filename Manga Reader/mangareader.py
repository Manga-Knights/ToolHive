import sys
import subprocess
from pathlib import Path
import webbrowser

BASE_DIR = Path(__file__).parent  

# Correct spelling now
VIEWER_HTML = BASE_DIR / "viewer.html"
EXTRACTOR_PY = BASE_DIR / "extractor.py"

def launch_viewer():
    print("Trying to access:", VIEWER_HTML.resolve())

    if VIEWER_HTML.exists():
        webbrowser.open(VIEWER_HTML.resolve().as_uri())
        print("📖 Viewer launched. Please select the folder inside the viewer.")
    else:
        print("⚠️ viewer.html not found.")
        print("Check the file path:", VIEWER_HTML.resolve())

def run_extractor():
    cmd = [sys.executable, str(EXTRACTOR_PY)]
    print(f"📦 Launching extractor: {cmd}")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print("Extractor exited with error.")
    
def main():
    print("Select manga format:")
    print(1, "Image Folder (viewer will open)")
    print(2, "CBZ/PDF/RAR archives (extractor will open)")

    while True:
        choice = input("Choice (1 or 2): ").strip()
        if choice == '1':
            launch_viewer()
            break
        elif choice == '2':
            run_extractor()
            break
        else:
            print("Invalid choice, please enter 1 or 2.")

if __name__ == "__main__":
    main()
