# SPDX-License-Identifier: GPL-3.0-or-later
# ToolHive Launcherlib dialogs
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




from tkinter import Tk, filedialog
from pathlib import Path

from .prints import print_error, print_info, print_menu_option, print_warning


def ask_directory(title="Select Folder"):
    """
    Open a folder selection dialog and return a Path object.
    If the user cancels, prints an error and returns None.
    """
    root = Tk()
    root.withdraw()
    root.lift()
    root.attributes("-topmost", True)
    folder = filedialog.askdirectory(title=title)
    root.destroy()

    if folder:  # user selected a folder
        return Path(folder)
    else:       # user cancelled
        print_error("No folder selected. Exiting...")
        return None


def ask_saveas_filename(title="Save As", defaultextension=".txt", filetypes=None):
    root = Tk()
    root.withdraw()
    root.lift()
    root.attributes("-topmost", True)
    path = filedialog.asksaveasfilename(
        title=title,
        defaultextension=defaultextension,
        filetypes=filetypes or [("All Files", "*.*")]
    )
    root.destroy()
    return Path(path) if path else None


def ask_file(title="Select a file", filetypes=(("All Files", "*.*"),)):
    """Open dialog to select a single file."""
    root = Tk()
    root.withdraw()
    root.lift()
    root.attributes("-topmost", True)
    path = filedialog.askopenfilename(title=title, filetypes=filetypes)
    root.destroy()
    return Path(path) if path else None


def ask_files(title="Select files", filetypes=(("All Files", "*.*"),)):
    root = Tk()
    root.withdraw()
    root.lift()
    root.attributes("-topmost", True)
    paths = filedialog.askopenfilenames(title=title, filetypes=filetypes)
    root.destroy()
    return [Path(p) for p in paths] if paths else None


def ask_choice(prompt, options, repeat_option=None):
    """
    Display a menu and return the chosen key.
    
    :param prompt: Heading text (string).
    :param options: dict mapping option keys (strings) -> description.
    :param repeat_option: key that should cause the loop to repeat instead of returning.
    :return: selected option key (string).
    """
    while True:
        print_info(f"\n{prompt}")
        for key, desc in options.items():
            print_menu_option(key, desc)

        choice = input(f"Select ({'/'.join(options.keys())}): ").strip()
        if choice in options:
            if choice == repeat_option:
                continue  # just re-loop
            return choice
        else:
            print_warning(f"Invalid choice, please enter one of: {', '.join(options.keys())}.")

def ask_float(prompt, default):
    while True:
        try:
            t = input(f"{prompt} (default = {default}): ").strip()
            return float(t) if t else default
        except ValueError:
            print_warning("Please enter a valid number.")   

def ask_yes_no(prompt, default=None):
    """
    Ask a yes/no question.
    
    :param prompt: The question string.
    :param default: Optional default ('yes' or 'no') if user presses Enter.
    :return: 'yes' or 'no' (always lowercase)
    """
    yes_options = {"1", "yes", "y"}
    no_options = {"2", "no", "n"}

    while True:
        suffix = f" (default={default})" if default else ""
        choice = input(f"{prompt}{suffix}: ").strip().lower()
        
        if not choice and default:
            return default.lower()
        if choice in yes_options:
            return "yes"
        if choice in no_options:
            return "no"
        print_warning(f"Invalid choice, please enter 1/2 or yes/no.") 