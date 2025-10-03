# SPDX-License-Identifier: GPL-3.0-or-later
# ToolHive Launcher help
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