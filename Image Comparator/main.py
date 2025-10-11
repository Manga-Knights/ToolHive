import sys
import os
import argparse
import traceback
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QPalette, QColor
import logging

# Import your core GUI class
from main_window import ImageCompareWindow, resource_path


# --- Environment setup ---
os.environ['QT_LOGGING_RULES'] = '*.debug=false;*.warning=false'
os.environ['QT_QPA_PLATFORM'] = 'windows:darkmode=1'


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('image_comparator.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def run_app(folder1: str, folder2: str):
    """
    Launch the image comparator GUI with two folders.
    Preserves dark mode and visual styling.
    """
    app = QApplication(sys.argv)

    # --- Dark mode palette ---
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor("#000000"))
    palette.setColor(QPalette.Base, QColor("#000000"))
    palette.setColor(QPalette.AlternateBase, QColor("##000000"))
    palette.setColor(QPalette.Button, QColor("#000000"))
    palette.setColor(QPalette.Text, QColor("#ffffff"))
    palette.setColor(QPalette.ButtonText, QColor("#ffffff"))
    palette.setColor(QPalette.WindowText, QColor("#ffffff"))
    app.setPalette(palette)

    # --- Initialize GUI ---
    window = QMainWindow()
    gui = ImageCompareWindow()
    gui.load_folders(folder1, folder2)
    window.setCentralWidget(gui)
    window.show()

    # --- Run event loop ---
    exit_code = app.exec_()

    # Handle abnormal Qt exit codes
    if exit_code == 3221225477:
        exit_code = 0
    return exit_code


def parse_args():
    parser = argparse.ArgumentParser(
        description="Image comparison GUI entry point",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--input",
        nargs=2,
        metavar=("FOLDER1", "FOLDER2"),
        help="Specify two folders or image paths to compare."
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Show full traceback on errors."
    )
    return parser.parse_args()


def main_entry():
    """
    Allow launching via CLI, or safely from import (launcher.py).
    """
    args = parse_args()

    if not args.input:
        print("Usage: python main.py --input <folder_or_image_path1> <folder_or_image_path2>")
        sys.exit(1)

    try:
        # Resolve to parent folders if image files are given
        path1 = Path(args.input[0])
        path2 = Path(args.input[1])

        folder1 = path1 if path1.is_dir() else path1.parent
        folder2 = path2 if path2.is_dir() else path2.parent

        if not folder1.exists() or not folder2.exists():
            raise ValueError("Both input paths must exist.")

        exit_code = run_app(str(folder1), str(folder2))
        sys.exit(exit_code)

    except Exception as e:
        print(f"Error: {e}")
        if args.debug:
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main_entry()
