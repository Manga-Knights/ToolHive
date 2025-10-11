# SPDX-License-Identifier: GPL-3.0-or-later
# ToolHive Launcher config
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




from pathlib import Path

from .helpers import register_tool

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
}

# --- Tool registration (existing) ---
register_tool(
    "1", 
    "Rename Chapters and Images", 
    Path("Renaming Tools")/"Renamer"/"renamer.py",
    group="Organizing Tools",
    long_desc="Recursively rename subfolders as ch1, ch2… and images as 001.ext, 002.ext"
)


register_tool(
    "2", 
    "Manual Sorter", 
    Path("Renaming Tools")/"Manual Sorter"/"manual_sorter.py",
    blocking=False, group="Organizing Tools",
    long_desc="GUI to manually reorder images and rename them sequentially"
)


register_tool(
    "3", 
    "Matching Renaming", 
    Path("Renaming Tools")/"Matching Renamer"/"matching_renaming.py",
    group="Organizing Tools",
    long_desc="Rename files by fuzzy matching against another folder’s files"
)


register_tool(
    "4",
    "Image Flattener",
    Path("utils") / "Image Flattener" / "image_flattener.py",
    group="Organizing Tools",
    long_desc="Move all images from nested subfolders into the master folder"
)


register_tool(
    "5", 
    "CBZ Forger", 
    Path("CBZ_Forger")/"CBZ_Forger.py",
    group="Archive Tools",
    long_desc="Build one CBZ archive per subfolder of images"
)


register_tool(
    "6", 
    "PDF Forger", 
    Path("PDF_Forger")/"PDF_Forger.py",
    group="Archive Tools",
    long_desc="Advanced PDF creator with optional OCR (Tesseract/PaddleOCR)"
)


register_tool(
    "7", 
    "HTML Converter", 
    Path("HTML Converter")/"html_converter.py",
    group="Archive Tools",
    long_desc="Convert site-specific HTML files to PDFs/EPUBs"
)


register_tool(
    "8", 
    "Manga Reader", 
    Path("Manga Reader")/"mangareader.py",
    group="Viewing Tools",
    long_desc="Open manga from folder, CBZ, RAR, or PDF (auto-extract if needed)"
)


register_tool(
    "9", 
    "Image Comparator", 
    Path("Image Comparator")/"start_with_folder.py",
    group="Viewing Tools",
    long_desc="GUI to compare two image folders side-by-side with metrics"
)


register_tool(
    "10", 
    "Folder Image Count Reporter", 
    Path("utils")/"ImageCount Reporter"/"imagecount_reporter.py",
    group="Viewing Tools",
    long_desc="Recursively count images in a folder and its subfolders"
)