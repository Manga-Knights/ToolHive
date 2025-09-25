# SPDX-License-Identifier: GPL-3.0-or-later
# ToolHive ImageCount Reporter
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

import sys
import argparse
import subprocess
from pathlib import Path

# --- Setup guard ---
setup_incomplete = False  # Flipped to False by setup.py

if setup_incomplete:
    print(f"⚠️ Setup has not been run yet. Please run the setup script first.")

    script_name = Path(__file__).stem
    setup_path = Path(__file__).resolve().parent / f"setup_{script_name}.py"

    if setup_path.exists():
        print(f"Launching {setup_path}...")
        subprocess.run([sys.executable, str(setup_path)])
    else:
        print(f"❌ Setup script not found: {setup_path}")

    sys.exit(1)

# --- launcherlib import ---
try:
    from launcherlib.prints import (
        print_error,
        print_warning,
        print_success,
        print_info,
        print_menu_header,
    )
    from launcherlib.dialogs import ask_directory, ask_saveas_filename
except ImportError:
    print("❌ launcherlib not found. Please run setup_imagecount_reporter.py first.")
    sys.exit(1)

IMAGE_EXTS_DEFAULT = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff', '.gif', '.tif'}


def parse_extensions(ext_arg):
    if not ext_arg or not ext_arg.strip():
        return IMAGE_EXTS_DEFAULT
    cleaned = {
        ("." + e.lower().lstrip("."))
        for e in (ext.strip() for ext in ext_arg.split(",")) if e
    }
    return cleaned or IMAGE_EXTS_DEFAULT


def log_error_to_file(msg, log_file):
    try:
        import datetime
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.datetime.now()}] {msg}\n")
    except Exception:
        pass  # don’t break script if logging fails


def scan_folders(root_folder, extensions, args):
    root_folder = Path(root_folder)
    folder_info = {}

    def helper(folder, depth):
        folder = Path(folder)
        direct_count = 0
        children = []

        try:
            for entry in folder.iterdir():
                if entry.is_file() and entry.suffix.lower() in extensions:
                    direct_count += 1
                elif entry.is_dir():
                    children.append(entry)
        except Exception as e:
            msg = f"Could not access {folder}: {e}"
            print_error(msg)
            if getattr(args, "log", None):
                log_error_to_file(msg, args.log)
            if getattr(args, "debug", False):
                import traceback
                traceback.print_exc()

        total = direct_count
        for child in children:
            total += helper(child, depth + 1)

        folder_info[str(folder)] = {
            'depth': depth,
            'direct_count': direct_count,
            'total_count': total,
        }
        return total

    helper(root_folder, 0)
    return folder_info


def format_output(folder_info, root_folder, ascending=True):
    root_folder = Path(root_folder)
    folders = [(Path(f), info['direct_count'], info['total_count'])
               for f, info in folder_info.items()]
    folders.sort(key=lambda x: x[2], reverse=not ascending)

    lines = []
    for f, direct, total in folders:
        name = str(f.relative_to(root_folder))
        if name == ".":
            name = str(root_folder.name)
        lines.append(f"{name}: {direct} images (total: {total})")
    return "\n".join(lines)


def run_cli(args):
    try:
        extensions = parse_extensions(args.ext)
        folder_info = scan_folders(args.input, extensions, args)

        if args.asc:
            ascending = True
        elif args.des:
            ascending = False
        else:
            # ask interactively
            while True:
                order = input("Sort by total images ascending or descending? (a/d): ").strip().lower()
                if order in ('a', 'd'):
                    ascending = (order == 'a')
                    break
                print_warning("Invalid input. Enter 'a' or 'd'.")

        output_text = format_output(folder_info, args.input, ascending)
        print_info("\n=== Image counts by folder (ranked) ===\n")
        print_info(output_text)

        if args.output:
            try:
                output_path = Path(args.output)
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(output_text)
                print_success(f"Output saved to: {output_path}")
            except Exception as e:
                msg = f"Failed to save file: {e}"
                print_error(msg)
                if args.log:
                    log_error_to_file(msg, args.log)
                if args.debug:
                    import traceback
                    traceback.print_exc()

    except Exception as e:
        msg = f"Unexpected error: {e}"
        print_error(msg)
        if args.log:
            log_error_to_file(msg, args.log)
        if args.debug:
            import traceback
            traceback.print_exc()


def run_gui():
    main_folder = ask_directory("Select Main Folder")
    if not main_folder:
        print_warning("Cancelled.")
        return 1

    main_folder = Path(main_folder)
    extensions = IMAGE_EXTS_DEFAULT
    folder_info = scan_folders(main_folder, extensions, argparse.Namespace(debug=False, log=None))

    while True:
        order = input("Sort by total images ascending or descending? (a/d): ").strip().lower()
        if order in ('a', 'd'):
            ascending = (order == 'a')
            break
        print_warning("Invalid input. Enter 'a' or 'd'.")

    output_text = format_output(folder_info, main_folder, ascending)
    print_menu_header("\n=== Image counts by folder (ranked) ===\n")
    print_info(output_text)

    save_choice = input("\nSave output to text file? (y/n): ").strip().lower()
    if save_choice == 'y':
        save_path = ask_saveas_filename(
            "Save output as...",
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if save_path:
            save_path = Path(save_path)
            try:
                with open(save_path, "w", encoding="utf-8") as f:
                    f.write(output_text)
                print_success(f"Output saved to: {save_path}")
            except Exception as e:
                print_error(f"Failed to save file: {e}")
        else:
            print_warning("Save cancelled.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Scan image counts by folder (ranked).",
        epilog="""Examples:
  python imagecount_reporter.py --input "C:/Images" --ext jpg,png --asc
  python imagecount_reporter.py --input ./photos --des --output result.txt --log errors.log --debug
  python imagecount_reporter.py   # GUI mode""",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("--input", help="Main folder path (skips GUI if provided)")
    parser.add_argument("--ext", help="Comma-separated extensions (default common image types)")
    parser.add_argument("--asc", action="store_true", help="Sort ascending by total images")
    parser.add_argument("--des", action="store_true", help="Sort descending by total images")
    parser.add_argument("--output", help="Save output to a text file (CLI mode only)")
    parser.add_argument("--log", help="Save all errors + tracebacks to log file (CLI mode only)")
    parser.add_argument("--debug", action="store_true", help="Show full traceback in console")

    args = parser.parse_args()

    if args.input:
        run_cli(args)
    else:
        run_gui()
