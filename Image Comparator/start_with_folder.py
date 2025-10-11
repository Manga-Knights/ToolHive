import sys
import traceback
from pathlib import Path
import argparse
import natsort
from PyQt5.QtWidgets import QApplication, QFileDialog
import main  # core GUI logic
from typing import Optional


def get_images(folder: Path):
    """Return a naturally sorted list of image files in the folder."""
    if not folder.exists() or not folder.is_dir():
        raise ValueError(f"Invalid folder: {folder}")
    return natsort.natsorted([
        str(p) for p in folder.iterdir()
        if p.suffix.lower() in ('.jpg', '.jpeg', '.png', '.bmp', '.webp', '.tif', '.tiff')
    ])


def select_folder(title: str) -> Optional[Path]:
    """Show folder picker dialog."""
    folder = QFileDialog.getExistingDirectory(None, title)
    return Path(folder) if folder else None


def launch_gui(folder1: Path, folder2: Path, debug: bool):
    """Run the main PyQt GUI safely."""
    try:
        main.run_app(str(folder1), str(folder2))
    except Exception as e:
        print(f"Error launching app: {e}")
        if debug:
            traceback.print_exc()
        input("Press Enter to exit...")


def interactive_mode(debug: bool):
    """Launch folder picker if no CLI inputs provided."""
    app = QApplication(sys.argv)

    folder1 = select_folder("Select Folder 1")
    if not folder1:
        print("No folder selected.")
        sys.exit(1)

    folder2 = select_folder("Select Folder 2")
    if not folder2:
        print("No second folder selected.")
        sys.exit(1)

    try:
        left_images = get_images(folder1)
        right_images = get_images(folder2)
    except Exception as e:
        print(f"Error scanning folders: {e}")
        if debug:
            traceback.print_exc()
        sys.exit(1)

    if not left_images or not right_images:
        print("No matching image pairs found.")
        input("Press Enter to exit...")
        return

    launch_gui(folder1, folder2, debug)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Launch the image comparison tool.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--input",
        nargs=2,
        metavar=("FOLDER1", "FOLDER2"),
        help="Specify two folders directly instead of using the interactive picker."
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Show full traceback on errors."
    )
    return parser.parse_args()


def main_launcher():
    args = parse_args()

    if args.input:
        try:
            folder1 = Path(args.input[0]).resolve()
            folder2 = Path(args.input[1]).resolve()
            if not folder1.is_dir() or not folder2.is_dir():
                raise ValueError("Both paths must be valid directories.")
            launch_gui(folder1, folder2, args.debug)
        except Exception as e:
            print(f"Error: {e}")
            if args.debug:
                traceback.print_exc()
            sys.exit(1)
    else:
        interactive_mode(args.debug)


if __name__ == "__main__":
    main_launcher()
