# SPDX-License-Identifier: GPL-3.0-or-later
# ToolHive Renamer
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
import argparse
import traceback

from natsort import natsorted
#import datetime

from launcherlib.prints import print_success, print_warning, print_info, print_error, print_submenu_option, print_menu_header
from launcherlib.dialogs import ask_directory

# --- Setup guard ---
setup_incomplete = True  # Flipped to False by setup.py after first-time run

if setup_incomplete:
    import subprocess

    print("⚠️ Setup has not been run yet. Please run the setup script first.")

    # Determine setup script path dynamically
    script_name = os.path.splitext(os.path.basename(__file__))[0]
    setup_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"setup_{script_name}.py")

    if os.path.exists(setup_path):
        print(f"Launching {setup_path}...")
        subprocess.run([sys.executable, setup_path])
    else:
        print(f"❌ Setup script not found: {setup_path}")

    sys.exit(1)

# Default: process all files. Users can restrict with --ext
DEFAULT_EXTENSIONS = None  # None means "all files"


# ---------------- LOGGING ----------------
def log_error(msg, log_file):
    try:
        import datetime
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.datetime.now()}] {msg}\n")
    except Exception as e:
        print(f"⚠️ Logging failed: {e}")


# ---------------- FILE RENAME ----------------
def rename_images_in_folder(folder_path, extensions, log_file=None, debug=False):
    try:
        # Filter files by extensions if provided; otherwise take all files
        files = sorted([f for f in os.listdir(folder_path)
                        if extensions is None or f.lower().endswith(tuple(extensions))])
        if not files:
            print_warning(f"No files found in: {folder_path}")
            return

        print_info(f"Renaming files in: {folder_path}")
        width = max(3, len(str(len(files))))
        temp_names = []

        for i, filename in enumerate(files, start=1):
            src = os.path.join(folder_path, filename)
            ext = os.path.splitext(filename)[1]
            tmp = os.path.join(folder_path, f"__tmp_{i}{ext}")
            os.rename(src, tmp)
            temp_names.append((tmp, f"{str(i).zfill(width)}{ext}"))

        for tmp, final_name in temp_names:
            dst = os.path.join(folder_path, final_name)
            if os.path.exists(dst):
                print_warning(f"Filename collision during rename: {dst}")
                base, ext = os.path.splitext(final_name)
                n = 1
                while os.path.exists(os.path.join(folder_path, f"{base}_{n}{ext}")):
                    n += 1
                dst = os.path.join(folder_path, f"{base}_{n}{ext}")
            os.rename(tmp, dst)

        print_success(f"Renamed {len(files)} files in {folder_path}\n")
    except Exception as e:
        msg = f"Error renaming files in {folder_path}: {e}"
        print_error(msg)
        if log_file:
            log_error(msg, log_file)
        if debug:
            traceback.print_exc()


# ---------------- FOLDER RENAME ----------------
def rename_subfolders(master_folder, prefix, log_file=None, debug=False):
    try:
        subfolders = [d for d in os.listdir(master_folder)
                      if os.path.isdir(os.path.join(master_folder, d))]
        if not subfolders:
            return

        subfolders = natsorted(subfolders)
        temp_names = []

        for i, folder in enumerate(subfolders, start=1):
            src = os.path.join(master_folder, folder)
            tmp = os.path.join(master_folder, f"__tmp_{i}")
            os.rename(src, tmp)
            temp_names.append((tmp, f"{prefix}{i}"))

        for tmp, final in temp_names:
            dst = os.path.join(master_folder, final)
            if os.path.exists(dst):
                print_warning(f"Folder collision during rename: {dst}")
                base = final
                n = 1
                while os.path.exists(os.path.join(master_folder, f"{base}_{n}")):
                    n += 1
                dst = os.path.join(master_folder, f"{base}_{n}")
            os.rename(tmp, dst)

        print_success(f"Renamed {len(subfolders)} folders in {master_folder}")
    except Exception as e:
        msg = f"Error renaming folders in {master_folder}: {e}"
        print_error(msg)
        if log_file:
            log_error(msg, log_file)
        if debug:
            traceback.print_exc()


# ---------------- PRE-SCAN ----------------
def prescan(master_folder, extensions, prefix, silent=False, log_file=None, debug=False):
    issues = []
    try:
        for root, dirs, files in os.walk(master_folder):
            filtered_files = [f for f in files if extensions is None or f.lower().endswith(tuple(extensions))]
            if filtered_files and dirs:
                issues.append(f"Mixed folder (files + subfolders): {root}")

        for root, dirs, files in os.walk(master_folder):
            filtered_files = sorted([f for f in files if extensions is None or f.lower().endswith(tuple(extensions))])
            width = max(3, len(str(len(filtered_files)))) if filtered_files else 0
            expected = {f"{str(i).zfill(width)}{os.path.splitext(f)[1]}" for i, f in enumerate(filtered_files, start=1)}
            existing = set(filtered_files)
            collisions = expected & existing
            for c in collisions:
                issues.append(f"File name collision: {os.path.join(root, c)}")

        subfolders = [d for d in os.listdir(master_folder) if os.path.isdir(os.path.join(master_folder, d))]
        for i, folder in enumerate(natsorted(subfolders), start=1):
            expected = f"{prefix}{i}"
            if folder.lower() == expected.lower():
                issues.append(f"Folder name collision: {os.path.join(master_folder, folder)}")

        if issues:
            print_menu_header("⚠️ Pre-scan warnings:")
            for i, issue in enumerate(issues, start=1):
                print_submenu_option(i, issue)
            if silent:
                return True
            choice = input("\nContinue anyway? (y/n): ").strip().lower()
            return choice == "y"
        return True
    except Exception as e:
        msg = f"Error during prescan: {e}"
        print_error(msg)
        if log_file:
            log_error(msg, log_file)
        if debug:
            traceback.print_exc()
        return False


# ---------------- MAIN RENAME ----------------
def rename_files_recursively(master_folder, extensions, prefix, log_file=None, debug=False):
    rename_subfolders(master_folder, prefix, log_file, debug)
    for root, dirs, files in os.walk(master_folder):
        rename_images_in_folder(root, extensions, log_file, debug)


def run_renamer_cli(input_folder, extensions, silent, subfolder_prefix, log_file=None, debug=False):
    if not prescan(input_folder, extensions, subfolder_prefix, silent, log_file, debug):
        print_error("Cancelled due to conflicts.")
        sys.exit(1)
    rename_files_recursively(input_folder, extensions, subfolder_prefix, log_file, debug)


def run_renamer_gui():
    input_folder = ask_directory("Select Master Folder")
    if not input_folder:
        print_error("Cancelled.")
        sys.exit(1)
    run_renamer_cli(input_folder, DEFAULT_EXTENSIONS, silent=False, subfolder_prefix="ch")


# ---------------- ENTRY POINT ----------------
if __name__ == "__main__":
    example_text = """Examples:
  python %(prog)s --input "C:/Folder" --ext txt,pdf --subfolder-prefix chapter --silent
  python %(prog)s --input ./docs --log errors.txt --debug
  python %(prog)s  # launches GUI

Defaults:
  --ext: all files
  --subfolder-prefix: ch"""

    parser = argparse.ArgumentParser(
        description="Rename subfolders and files in a folder.",
        epilog=example_text,
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("--input", help="Master folder path (skips GUI)")
    parser.add_argument("--ext", help="Comma-separated extensions (optional; default = all files)")
    parser.add_argument("--silent", action="store_true", help="Continue without prompting even on conflicts")
    parser.add_argument("--subfolder-prefix", default="ch", help="Prefix for subfolders (default: ch)")
    parser.add_argument("--log", help="Log all errors to file")
    parser.add_argument("--debug", action="store_true", help="Show full tracebacks in console")
    
    args = parser.parse_args()

    extensions = tuple(
        e.strip().lower() if e.startswith(".") else f".{e.strip().lower()}"
        for e in (args.ext.split(",") if args.ext else [])
    ) or None  # None = all files

    if args.input:
        run_renamer_cli(args.input, extensions, args.silent, args.subfolder_prefix, args.log, args.debug)
    else:
        run_renamer_gui()
