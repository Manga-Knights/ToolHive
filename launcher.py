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
import traceback
import os
from launcherlib import (
    list_tools,
    launch_tool,
    register_tool,
    print_menu_header,
    print_menu_option,
    print_menu_exit,
    print_error,
    print_warning,
    print_success,
    print_info,
    print_submenu_option,
    Colors,
    search_tools,
    TOOLS,
    BASE_DIR,
)
from collections import defaultdict

# --- Map subcommand names to registered tool keys ---
SUBCOMMANDS = {
    "renamer": "1",
    "manual-sort": "2",
    "match-rename": "3",
    "flatten": "4",
    "forge-cbz": "5",
    "forge-pdf": "6",
    "convert-html": "7",
    "view": "8",
    "compare": "9",
    "count": "10",
    #"your-tool": "11",
}

# --- Tool registration (existing) ---
register_tool(
    "1", "Rename Chapters and Images", "Renaming Tools/Renamer/renamer.py",
    group="Organizing Tools",
    long_desc="Recursively rename subfolders as ch1, ch2… and images as 001.ext, 002.ext"
)
register_tool(
    "2", "Manual Sorter", "Renaming Tools/Manual Sorter/manual_sorter.py",
    blocking=False, group="Organizing Tools",
    long_desc="GUI to manually reorder images and rename them sequentially"
)
register_tool(
    "3", "Matching Renaming", "Renaming Tools/Matching Renamer/matching_renaming.py",
    group="Organizing Tools",
    long_desc="Rename files by fuzzy matching against another folder’s files"
)
register_tool(
    "4", "Image Flattener", "utils/Image Flattener/image_flattener.py",
    group="Organizing Tools",
    long_desc="Move all images from nested subfolders into the master folder"
)
register_tool(
    "5", "CBZ Forger", "CBZ_Forger/CBZ_Forger.py",
    group="Archive Tools",
    long_desc="Build one CBZ archive per subfolder of images"
)
register_tool(
    "6", "PDF Forger", "PDF_Forger/PDF_Forger.py",
    group="Archive Tools",
    long_desc="Advanced PDF creator with optional OCR (Tesseract/PaddleOCR)"
)
register_tool(
    "7", "HTML Converter", "HTML Converter/html_converter.py",
    group="Archive Tools",
    long_desc="Convert site-specific HTML files to PDFs/EPUBs"
)
register_tool(
    "8", "Manga Reader", "manga reader/mangareader.py",
    group="Viewing Tools",
    long_desc="Open manga from folder, CBZ, RAR, or PDF (auto-extract if needed)"
)
register_tool(
    "9", "Image Comparator", "Image_Comparator/start_with_folder.py",
    group="Viewing Tools",
    long_desc="GUI to compare two image folders side-by-side with metrics"
)
register_tool(
    "10", "Folder Image Count Reporter", "utils/ImageCount Reporter/imagecount_reporter.py",
    group="Viewing Tools",
    long_desc="Recursively count images in a folder and its subfolders"
)

"""
register_tool(
    "11", "your tool", "ToolHive/path to your_tool.py",
    group="Media Tools",
    long_desc="add details about your tool here"
)
"""

# --- Helper functions ---

def run_child_script(tool_key, extra_args=None):
    """
    Run a registered tool by key.
    - Scripts: forwarded with CLI args, respect blocking.
    - Callable tools: run directly in the same process.
    - Friendly warnings on non-zero exit codes (blocking only).
    """
    tool = TOOLS.get(tool_key)
    if not tool:
        print_error(f"Tool not found: {tool_key}")
        return

    entry = tool["entry"]
    blocking = tool.get("blocking", True)
    extra_args = extra_args or []

    if callable(entry):
        # Callable tools run directly (old behavior)
        try:
            entry()
        except Exception:
            print_error("Error while running callable tool:")
            traceback.print_exc()
        return

    elif isinstance(entry, str):
        path = resolve_path(entry)
        if not os.path.exists(path):
            print_error(f"Tool script not found: {path}")
            return

        try:
            env = os.environ.copy()
            env["PYTHONPATH"] = os.pathsep.join([BASE_DIR, env.get("PYTHONPATH", "")])

            if blocking:
                # blocking = old synchronous run
                proc = subprocess.run([sys.executable, path, *extra_args], env=env)
                if proc.returncode != 0:
                    print_warning(f"Tool exited with code {proc.returncode}")
            else:
                # non-blocking = old Popen run
                subprocess.Popen([sys.executable, path, *extra_args], env=env)

        except Exception as e:
            print_error(f"Failed to run script: {e}")
            traceback.print_exc()

    else:
        print_error(f"Unsupported tool entry: {entry}")


def show_help():
    print("""
ToolHive

Usage:
    ToolHive [subcommand] [flags...]

Subcommands:
    renamer          Rename Chapters and Images
    manual-sort      Manual Sorter
    match-rename     Matching Renaming
    flatten          Image Flattener
    forge-cbz        CBZ Forger
    forge-pdf        PDF Forger
    convert-html     HTML Converter
    view             Manga Reader
    compare          Image Comparator
    count            Folder Image Count Reporter
    your-tool        your tool

Examples:
    python launcher.py renamer --subfolder-prefix ch --debug
    python launcher.py forge-cbz --overwrite

Notes:
    - Flags after subcommand are forwarded to the tool directly.
    - Interactive menu runs if no subcommand is provided.
""")

def search_mode():
    while True:
        query = input("🔍 Type tool name to search (m for manual, 0 to exit): ").strip().lower()
        if query == "0":
            return "EXIT"
        if query == "m":
            return None
        matches = search_tools(query)
        if not matches:
            print_warning("No match found. Try again.")
            continue
        print_menu_header("Search results")
        for idx, (ratio, key, tool) in enumerate(matches, start=1):
            print_submenu_option(idx, f"{tool['desc']} ({int(ratio*100)}%)")
        choice = input("Select a tool (r to retry, m for manual, 0 to exit): ").strip().lower()
        if choice == "r":
            continue
        if choice == "m":
            return None
        if choice == "0":
            return "EXIT"
        try:
            sel = int(choice)
            if 1 <= sel <= len(matches):
                _, key, tool = matches[sel-1]
                return key
        except ValueError:
            pass
        print_warning("Invalid choice. Try again.")

def interactive_menu():
    tools = list_tools()
    try:  # wrap the whole interactive menu
        while True:
            key = search_mode()
            if key == "EXIT":
                print_menu_exit("👋 Exiting ToolHive.")
                break
            if key:
                run_child_script(key)
                continue

            # Manual menu
            groups = defaultdict(list)
            for k, tool in tools.items():
                groups[tool["group"]].append((k, tool))
            print_menu_header("🛠️ ToolHive")
            group_names = sorted(groups.keys())
            for idx, gname in enumerate(group_names, start=1):
                print_menu_option(idx, gname)
            print_menu_exit("Exit")
            gchoice = input("Select a group: ").strip()
            if gchoice == "0":
                print_menu_exit("👋 Exiting ToolHive.")
                break
            if not gchoice.isdigit() or int(gchoice) < 1 or int(gchoice) > len(group_names):
                print_warning("Invalid choice. Try again.")
                continue
            group_name = group_names[int(gchoice) - 1]

            # Tool chooser inside group
            while True:
                print_menu_header(f"[{group_name}]")
                group_tools = sorted(groups[group_name], key=lambda x: int(x[0]))
                for k, tool in group_tools:
                    print_submenu_option(k, tool["desc"])
                    print(f"   → {Colors.CYAN}{tool['long_desc']}{Colors.RESET}")
                print_menu_exit("Back")
                choice = input("Select a tool: ").strip()
                if choice == "0":
                    break
                if choice in tools and tools[choice]["group"] == group_name:
                    run_child_script(choice)
                else:
                    print_warning("Invalid choice. Try again.")
    except KeyboardInterrupt:
        print("\n👋 Interrupted. Exiting.")


# --- Main entry ---
def main():
    # CLI mode
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        extra_args = sys.argv[2:] if len(sys.argv) > 2 else None
        if arg in ("-h", "--help"):
            show_help()
            sys.exit(0)
        elif arg in SUBCOMMANDS:
            tool_key = SUBCOMMANDS[arg]
            run_child_script(tool_key, extra_args)
            sys.exit(0)
        else:
            print_error(f"Unknown subcommand '{arg}'. Use -h for help.")
            sys.exit(1)
    # Interactive mode
    interactive_menu()

if __name__ == "__main__":
    main()

