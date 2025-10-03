# SPDX-License-Identifier: GPL-3.0-or-later
# ToolHive CBZ Forger
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




import os
import sys

# --- Setup guard ---
setup_incomplete = True  # Flipped to False by setup.py

if setup_incomplete:
    import subprocess

    print(f"⚠️ Setup has not been run yet. Please run the setup script first.")

    # Determine setup script path dynamically
    script_name = os.path.splitext(os.path.basename(__file__))[0]
    setup_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"setup_{script_name}.py")

    if os.path.exists(setup_path):
        print(f"Launching {setup_path}...")
        subprocess.run([sys.executable, setup_path])
    else:
        print(f"❌ Setup script not found: {setup_path}")

    sys.exit(1)

# --- Original code continues below ---

import zipfile
import argparse
import traceback  # always imported for global error handling
from pathlib import Path
import re
#below are the deffered imports. they are imported only if needed for performance
#from natsort import natsorted
#from PIL import Image, UnidentifiedImageError
#from tqdm import tqdm
#from launcherlib.dialogs import ask_directory

# --------------------- Helper Functions ---------------------
def log_message(logfile, level, msg, log_levels=None):
    if logfile:
        if log_levels and level.upper() not in log_levels:
            return
        try:
            logfile_path = Path(logfile)
            if not logfile_path.parent.exists():
                print(f"[ERROR] Invalid log path: {logfile_path.parent}")
                return
            if not logfile_path.exists():
                logfile_path.touch()
            with open(logfile_path, "a", encoding="utf-8") as f:
                f.write(f"[{level}] {msg}\n")
        except Exception:
            pass


def natsorted_images(folder, exts):
    from natsort import natsorted
    return natsorted([f for f in os.listdir(folder) if f.lower().endswith(exts)])


def sanitize_name(path: Path):
    base, ext = os.path.splitext(path.name)
    parent = path.parent
    n = 1
    while (parent / f"{base}_{n}{ext}").exists():
        n += 1
    return parent / f"{base}_{n}{ext}"


def validate_extensions(ext_string):
    IMAGE_EXTS_DEFAULT = ('.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tif', '.tiff')
    if not ext_string:
        return tuple(IMAGE_EXTS_DEFAULT)

    exts = [e.strip().lower() for e in ext_string.split(",") if e.strip()]
    invalid = [e for e in exts if not re.match(r'^\.[a-z0-9]+$', e)]

    if invalid:
        print(f"[WARNING] Invalid extension(s) detected: {', '.join(invalid)}")
        print_usage_examples()
        print_flag_summary()
        return None

    return tuple(exts)


# --------------------- BMP Conversion ---------------------
def convert_bmp_safe(folder, silent, debug, logfile, log_levels=None):
    from PIL import Image, UnidentifiedImageError

    folder = Path(folder)
    bmp_files = [f for f in folder.iterdir() if f.suffix.lower() == ".bmp"]

    for bmp_path in bmp_files:
        png_path = bmp_path.with_suffix(".png")

        if png_path.exists():
            while True:
                choice = input(
                    f"⚠️ PNG already exists for {bmp_path.name}: {png_path.name}\n"
                    "Choose action: [s]anitize and continue, [c]ancel this conversion: "
                ).strip().lower()
                if choice == 's':
                    n = 1
                    while True:
                        new_png = png_path.with_name(f"{png_path.stem}_{n}{png_path.suffix}")
                        if not new_png.exists():
                            png_path = new_png
                            break
                        n += 1
                    if not silent:
                        print(f"[WARNING] Sanitized PNG name: {png_path.name}")
                    log_message(logfile, "WARNING", f"Sanitized PNG name: {png_path.name}", log_levels)
                    break
                elif choice == 'c':
                    if not silent:
                        print(f"[WARNING] Skipped BMP conversion: {bmp_path.name}")
                    log_message(logfile, "WARNING", f"Skipped BMP conversion: {bmp_path.name}", log_levels)
                    png_path = None
                    break
                else:
                    print("Invalid choice. Enter 's' to sanitize or 'c' to cancel.")

        if not png_path:
            continue

        try:
            with Image.open(bmp_path) as img:
                if img.mode in ("RGBA", "LA"):
                    img = img.convert("RGBA")
                elif img.mode == "P" and "transparency" in img.info:
                    img = img.convert("RGBA")
                else:
                    img = img.convert("RGB")
                dpi = img.info.get("dpi", (600, 600))
                img.save(png_path, format="PNG", dpi=dpi)
            os.remove(bmp_path)
            if not silent:
                print(f"[SUCCESS] Converted {bmp_path.name} → {png_path.name}")
            log_message(logfile, "SUCCESS", f"Converted {bmp_path.name} → {png_path.name}", log_levels)
        except Exception as e:
            if debug and not silent:
                traceback.print_exc()
            elif not silent:
                print(f"[ERROR] Failed conversion {bmp_path.name}: {e}")
            log_message(logfile, "ERROR", f"Failed conversion {bmp_path.name}: {e}", log_levels)


# --------------------- CBZ Creation ---------------------
def create_cbz(folder, output_dir, exts, silent, debug, logfile, overwrite=False, log_levels=None):
    from natsort import natsorted
    if not silent:
        from tqdm import tqdm

    try:
        images = natsorted([f for f in os.listdir(folder) if f.lower().endswith(exts)])
        if not images:
            if not silent:
                print(f"[WARNING] No images found in folder: {folder}")
            log_message(logfile, "WARNING", f"No images found in folder: {folder}", log_levels)
            return None

        cbz_name = Path(folder).name + ".cbz"
        cbz_path = Path(output_dir) / cbz_name

        if cbz_path.exists():
            if overwrite:
                if not silent:
                    print(f"[WARNING] Overwriting existing CBZ: {cbz_path.name}")
                log_message(logfile, "WARNING", f"Overwriting existing CBZ: {cbz_path.name}", log_levels)
            else:
                cbz_path = sanitize_name(cbz_path)
                if not silent:
                    print(f"[WARNING] CBZ collision: {cbz_name} → {cbz_path.name}")
                log_message(logfile, "WARNING", f"CBZ collision: {cbz_name} → {cbz_path.name}", log_levels)

        with zipfile.ZipFile(cbz_path, 'w') as cbz:
            for img in tqdm(images, desc=f"Creating CBZ: {cbz_path.name}", unit="img", disable=silent):
                cbz.write(Path(folder) / img, arcname=img)

        return cbz_path

    except Exception as e:
        if debug and not silent:
            traceback.print_exc()
        elif not silent:
            print(f"[ERROR] Failed to create CBZ for {folder.name}: {e}")
        log_message(logfile, "ERROR", f"Failed to create CBZ for {folder.name}: {e}", log_levels)
        return None


# --------------------- Usage Examples ---------------------
def print_usage_examples():
    print("\nUsage Examples:")
    print("  python cbz_forger.py --input ./comics")
    print("  python cbz_forger.py --input ./comics --output ./cbz_out")
    print("  python cbz_forger.py --input ./comics --ext .jpg,.png --skip-bmp")
    print("  python cbz_forger.py --input ./comics --silent --log cbz.log")
    print("  python cbz_forger.py --overwrite --log cbz.log")
    print("  python cbz_forger.py --help\n")


# --------------------- Flag Summary ---------------------
def print_flag_summary():
    print("\nFlag Summary:")
    print("------------------------------------------------------------")
    print("{:<15} {:<50}".format("Flag", "Description"))
    print("------------------------------------------------------------")
    print("{:<15} {:<50}".format("--input", "Master folder containing subfolders of images."))
    print("{:<15} {:<50}".format("--output", "Output folder for CBZ files (default = input folder)."))
    print("{:<15} {:<50}".format("--skip-bmp", "Skip BMP conversion step."))
    print("{:<15} {:<50}".format("--ext", "Comma-separated list of extensions to include (e.g., .jpg,.png)."))
    print("{:<15} {:<50}".format("--silent", "Suppress all prints and progress bars (except BMP collision prompt)."))
    print("{:<15} {:<50}".format("--debug", "Print full Python tracebacks on errors (silent takes priority)."))
    print("{:<15} {:<50}".format("--log", "Write all messages to a log file. Default=cbz_forger.log if no file is provided."))
    print("{:<15} {:<50}".format("--overwrite", "Overwrite existing CBZ files instead of sanitizing names."))
    print("{:<15} {:<50}".format("--log-info", "Log INFO messages."))
    print("{:<15} {:<50}".format("--log-warning", "Log WARNING messages."))
    print("{:<15} {:<50}".format("--log-error", "Log ERROR messages."))
    print("------------------------------------------------------------\n")


# --------------------- Main Tool ---------------------
def run_cbz_forger(args):
    try:
        log_levels = None
        if args.log_info or args.log_warning or args.log_error:
            levels = []
            if args.log_info:
                levels.append("INFO")
            if args.log_warning:
                levels.append("WARNING")
            if args.log_error:
                levels.append("ERROR")
            log_levels = tuple(levels)

        # ---------------- Input Folder ----------------
        input_path = None
        if args.input:
            input_path = Path(args.input)
            if not input_path.exists() or not input_path.is_dir():
                if not args.silent:
                    print(f"[ERROR] Invalid input path: {args.input}")
                    print_usage_examples()
                    print_flag_summary()
                log_message(args.log, "ERROR", f"Invalid input path: {args.input}", log_levels)
                input_path = None

        if not input_path:
            from launcherlib.dialogs import ask_directory
            input_path_str = ask_directory("Select Master Folder")
            if not input_path_str:
                if not args.silent:
                    print(f"[ERROR] Cancelled by user.")
                log_message(args.log, "ERROR", "Cancelled by user.", log_levels)
                return
            input_path = Path(input_path_str)

        # ---------------- Output Folder ----------------
        output_path = Path(args.output) if args.output else input_path
        if not output_path.exists():
            output_path.mkdir(parents=True, exist_ok=True)

        # ---------------- Extensions ----------------
        exts = None
        if args.ext is not None:
            validated = validate_extensions(args.ext)
            if validated is None:
                return
            exts = validated
        if not exts:
            exts = ('.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tif', '.tiff')

        # ---------------- BMP Conversion ----------------
        if not args.skip_bmp and any(f.lower().endswith(".bmp") for f in os.listdir(input_path)):
            convert_bmp_safe(input_path, args.silent, args.debug, args.log, log_levels)

        # ---------------- Collect Subfolders ----------------
        subfolders = [p for p in input_path.glob("*") if p.is_dir() and any(
            f.lower().endswith(exts) for f in os.listdir(p)
        )]

        if not subfolders:
            if not args.silent:
                print(f"[WARNING] No image folders found in master folder.")
            log_message(args.log, "WARNING", "No image folders found in master folder.", log_levels)
            return
        else:
            if not args.silent:
                print(f"[INFO] 📂 Found {len(subfolders)} folders with images.")
            log_message(args.log, "INFO", f"Found {len(subfolders)} folders with images.", log_levels)

        # ---------------- Create CBZ ----------------
        for folder in subfolders:
            cbz_path = create_cbz(folder, output_path, exts, args.silent, args.debug,
                                   args.log, overwrite=args.overwrite, log_levels=log_levels)
            if cbz_path:
                if not args.silent:
                    print(f"[SUCCESS] Created CBZ: {cbz_path.name}")
                log_message(args.log, "SUCCESS", f"Created CBZ: {cbz_path.name}", log_levels)

        if not args.silent:
            print(f"[SUCCESS] Done. All CBZs saved in output folder.")
        log_message(args.log, "INFO", "Done. All CBZs saved in output folder.", log_levels)

    except Exception as e:
        if args.debug and not args.silent:
            traceback.print_exc()
        elif not args.silent:
            print(f"[ERROR] Fatal error: {e}")
        log_message(args.log, "ERROR", f"Fatal error: {e}", log_levels)


# --------------------- Entry Point ---------------------
class CustomArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        print(f"[ERROR] Argument error: {message}")
        print_usage_examples()
        print_flag_summary()
        sys.exit(2)

    def print_help(self):
        super().print_help()
        print_flag_summary()


if __name__ == "__main__":
    parser = CustomArgumentParser(
        description="CBZ Forger - Convert image folders into CBZ archives with optional BMP conversion, logging, and overwrite."
    )
    parser.add_argument("--input", help="Master folder containing subfolders of images.")
    parser.add_argument("--output", nargs="?", const=None, help="Output folder for CBZ files (default = input folder).")
    parser.add_argument("--skip-bmp", action="store_true", help="Skip BMP conversion step.")
    parser.add_argument("--ext", nargs="?", const="", help="Comma-separated list of extensions to include (e.g., .jpg,.png).")
    parser.add_argument("--silent", action="store_true", help="Suppress all prints and progress bars (except BMP collision prompt).")
    parser.add_argument("--debug", action="store_true", help="Print full Python tracebacks on errors (silent takes priority).")
    parser.add_argument("--log", nargs="?", const="cbz_forger.log", help="Write all messages to a log file. Default=cbz_forger.log if no file is provided.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing CBZ files instead of sanitizing names.")
    parser.add_argument("--log-info", action="store_true", help="Log INFO messages.")
    parser.add_argument("--log-warning", action="store_true", help="Log WARNING messages.")
    parser.add_argument("--log-error", action="store_true", help="Log ERROR messages.")

    args = parser.parse_args()
    run_cbz_forger(args)
