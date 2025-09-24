# SPDX-License-Identifier: GPL-3.0-or-later
# ToolHive Launcher
# Copyright (C) 2025 Your Name
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


import sys
import subprocess

# --- Setup guard ---
setup_incomplete = True  # Flipped to False by setup.py . to prevent the script from running unless setup is completed.

if setup_incomplete:
    import os, sys, subprocess

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

import os
import shutil
import re
import argparse
from launcherlib import ask_directory, print_warning, print_error, print_success, Colors, print_info

DEFAULT_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff", ".gif"}


def parse_extensions(ext_arg):
    if not ext_arg or not ext_arg.strip():
        return DEFAULT_EXTENSIONS
    cleaned = {
        ("." + e.lower().lstrip("."))
        for e in (ext.strip() for ext in ext_arg.split(","))
        if e
    }
    return cleaned or DEFAULT_EXTENSIONS


def sanitize_name(name, max_length):
    safe = re.sub(r'[<>:"/\\|?*]', '_', name).strip()
    return safe[:max_length]


def run_image_flattener(args):
    master_folder = args.input or ask_directory("Select Master Folder")
    if not master_folder:
        print_warning("No folder selected. Exiting.")
        return 1

    extensions = parse_extensions(args.ext)
    moved_files = []

    for root_dir, _, files in os.walk(master_folder):
        if root_dir == master_folder:
            continue

        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in extensions:
                safe_name = sanitize_name(file, args.maxfilename)
                src_path = os.path.join(root_dir, file)
                dest_path = os.path.join(master_folder, safe_name)

                counter = 1
                while os.path.exists(dest_path):
                    name_no_ext, file_ext = os.path.splitext(safe_name)
                    dest_path = os.path.join(master_folder, f"{name_no_ext}_{counter}{file_ext}")
                    counter += 1

                try:
                    shutil.move(src_path, dest_path)
                    moved_files.append((src_path, dest_path))
                except Exception as e:
                    if args.debug:
                        import traceback
                        traceback.print_exc()
                    else:
                        print_error(f"Failed to move {src_path}: {e}")

    if moved_files:
        print_success(f"\nMoved {len(moved_files)} files into {master_folder}")
        for src, dest in moved_files[:args.preview]:
            print_info(f"{src} -> {dest}")
        if not args.silent:
            from tkinter import messagebox
            messagebox.showinfo("Done", f"Moved {len(moved_files)} images to {master_folder}")
    else:
        print_warning("\nNo images found in subfolders.")
        if not args.silent:
            from tkinter import messagebox
            messagebox.showinfo("Info", "No images found in subfolders.")

    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Flatten images from subfolders into a master folder.",
        epilog="""Examples:
  python image_flattener.py --input "C:/Images" --ext jpg,png --maxfilename 150
  python image_flattener.py --input /home/user/photos --silent --preview 5
  python image_flattener.py --input ./gallery --debug""",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("--input", help="Master folder path (skips GUI if provided)")
    parser.add_argument("--ext", help="Comma-separated list of extensions (e.g. jpg,png,webp)")
    parser.add_argument("--maxfilename", type=int, default=180, help="Maximum filename length (default 180)")
    parser.add_argument("--preview", type=int, default=10, help="Number of moved files to preview (default 10)")
    parser.add_argument("--silent", action="store_true", help="Disable GUI popups (silent CLI mode)")
    parser.add_argument("--debug", action="store_true", help="Show full traceback on errors")

    args = parser.parse_args()

    # Validate arguments
    if args.maxfilename <= 0:
        parser.error("--maxfilename must be greater than 0")
    if args.preview < 0:
        parser.error("--preview cannot be negative")

    try:
        run_image_flattener(args)
    except Exception as e:
        if args.debug:
            import traceback
            traceback.print_exc()
        else:
            print_error(f"Unexpected error: {e}")
