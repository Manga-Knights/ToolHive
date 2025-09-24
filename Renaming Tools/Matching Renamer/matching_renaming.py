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

import os
import sys

# --- Setup guard ---
setup_incomplete = True  # Flipped to False by setup.py

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

# --- launcherlib import ---
try:
    import launcherlib
    from launcherlib import print_success, print_warning, print_error, print_info, ask_directory
except ImportError:
    print("❌ launcherlib not found. Please run the setup script first.")
    sys.exit(1)

# --- Original code continues below ---
from pathlib import Path

# --- Helper to safely call input() after prints ---
def safe_input(prompt):
    sys.stdout.flush()
    return input(prompt)

# --- Log errors to file with timestamp ---
def log_error(msg, log_file):
    try:
        import datetime
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.datetime.now()}] {msg}\n")
    except Exception:
        pass  # Don't break the script if logging fails

# --- Prompt user to choose matching candidate ---
def prompt_choice(source_name, candidates):
    i = 0
    while i < len(candidates):
        target_name, score, _ = candidates[i]
        print_info(f"\nSource:   {source_name}")
        print_info(f"Candidate: {target_name}  (Match Score: {score:.1f})")
        choice = safe_input("Rename candidate to match source? [y/n/skip]: ").strip().lower()
        if choice == 'y':
            return target_name
        elif choice == 'skip':
            return None
        else:
            i += 1
    return None

# --- Pre-scan folder for unexpected extensions ---
def pre_scan(folder: Path, ext: str, folder_name: str):
    unexpected = [f.name for f in folder.iterdir() if f.is_file() and not f.name.lower().endswith(ext)]
    if unexpected:
        print_warning(f"\n⚠️ {folder_name} folder contains {len(unexpected)} files not matching {ext}:")
        for f in unexpected:
            print_warning(f"  {f}")
        choice = safe_input(f"Do you want to continue including only {ext} files? [y/n]: ").strip().lower()
        if choice != 'y':
            print_error("Aborted by user.")
            return False
    return True

# --- CLI Main function ---
def main_cli(args):
    # Deferred imports
    from rapidfuzz import process, fuzz

    log_path = Path(args.log) if args.log else Path.cwd() / "skipped_log.txt"
    try:
        threshold = float(args.threshold) if args.threshold is not None else 50
    except ValueError:
        print_warning("Invalid threshold, using default 50.")
        threshold = 50
    if not (0 <= threshold <= 100):
        print_warning("Threshold must be 0–100. Using 50.")
        threshold = 50

    # --- Determine source folder ---
    source_folder = Path(args.source) if args.source else Path(ask_directory("Select Source Folder"))
    if not source_folder or not source_folder.exists():
        print_error("Invalid source folder.")
        return

    # --- Determine target folder ---
    target_folder = Path(args.target) if args.target else Path(ask_directory("Select Target Folder"))
    if not target_folder or not target_folder.exists():
        print_error("Invalid target folder.")
        return

    # --- Determine extensions ---
    def detect_ext(folder):
        files = [f.suffix.lower() for f in folder.iterdir() if f.is_file()]
        return files[0] if files and all(f == files[0] for f in files) else None

    source_ext = args.source_ext.lower() if args.source_ext else detect_ext(source_folder)
    target_ext = args.target_ext.lower() if args.target_ext else detect_ext(target_folder)

    if not source_ext:
        source_ext = safe_input("Enter source extension (e.g., .mp3): ").strip().lower()
    if not target_ext:
        target_ext = safe_input("Enter target extension (e.g., .flac): ").strip().lower()
    if not source_ext.startswith(".") or not target_ext.startswith("."):
        print_error("Extensions must start with a dot (e.g., .mp3)")
        return

    # Pre-scan
    if not pre_scan(source_folder, source_ext, "SOURCE"):
        return
    if not pre_scan(target_folder, target_ext, "TARGET"):
        return

    # --- Perform matching/renaming ---
    renamed_targets = set()
    with open(log_path, "w", encoding="utf-8") as log:
        source_files = list(source_folder.glob(f"*{source_ext}"))
        target_files = list(target_folder.glob(f"*{target_ext}"))
        target_stem_map = {f.stem: f.name for f in target_files}
        target_names = [f.name for f in target_files]

        for src_path in source_files:
            src_stem = src_path.stem
            if src_stem in target_stem_map:
                print_warning(f"[SKIP - EXACT MATCH] {src_path.name} ↔ {target_stem_map[src_stem]}")
                continue

            matches = process.extract(src_stem, target_names, scorer=fuzz.partial_token_sort_ratio, limit=5)
            if not matches or matches[0][1] < threshold:
                print_warning(f"\n[NO MATCH] for {src_path.name}")
                log.write(f"[NO MATCH] {src_path.name}\n")
                continue

            print_info(f"\n=== Matching for: {src_path.name} ===")
            chosen_target_name = prompt_choice(src_path.name, matches)
            if chosen_target_name:
                src = target_folder / chosen_target_name
                dst_name = src_stem + target_ext
                dst = target_folder / dst_name
                if dst.exists():
                    print_warning(f"[SKIP] Target {dst.name} already exists! Skipping.")
                    continue
                try:
                    src.rename(dst)
                    renamed_targets.add(chosen_target_name)
                    print_success(f"[RENAMED] {src.name} → {dst.name}")
                except Exception as e:
                    msg = f"Failed to rename {src.name}: {e}"
                    print_error(msg)
                    if args.log:
                        log_error(msg, args.log)
                    if args.debug:
                        import traceback
                        traceback.print_exc()
            else:
                print_warning(f"[SKIPPED] No match chosen for {src_path.name}")
                log.write(f"[SKIPPED] {src_path.name} (no accepted match)\n")

        # Log untouched target files
        matched_stems = set(f.stem for f in source_files)
        for tgt_path in target_files:
            if (tgt_path.name not in renamed_targets) and (tgt_path.stem not in matched_stems):
                log.write(f"[UNTOUCHED] {tgt_path.name}\n")

    print_success(f"\nLog file saved as: {log_path}")
    if args.debug or safe_input("Show logs? (y/n): ").strip().lower() == "y":
        import platform, subprocess
        if platform.system() == "Windows":
            os.startfile(log_path)
        elif platform.system() == "Darwin":
            subprocess.run(["open", log_path])
        else:
            subprocess.run(["xdg-open", log_path])

# --- CLI argument parsing ---
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="Match and rename files between source and target folders based on similarity.",
        epilog="""Example usage:
  python match_rename.py --source ./MP3 --target ./FLAC
  python match_rename.py --source ./MP3 --target ./FLAC --source-ext .mp3 --target-ext .flac --threshold 60
  python match_rename.py --source ./MP3 --target ./FLAC --log errors.log --debug
If extensions are not provided, the script will auto-detect them if uniform; otherwise, prompts for input.""",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("--source", required=True, help="Source folder path (files to match FROM)")
    parser.add_argument("--target", required=True, help="Target folder path (files to rename)")
    parser.add_argument("--source-ext", help="Source file extension (e.g., .mp3)")
    parser.add_argument("--target-ext", help="Target file extension (e.g., .flac)")
    parser.add_argument("--threshold", type=float, help="Similarity threshold (0-100, default 50)")
    parser.add_argument("--log", help="Write all skipped/unmatched files and errors to log file")
    parser.add_argument("--debug", action="store_true", help="Show full traceback on errors")
    args = parser.parse_args()

    main_cli(args)
