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
import subprocess
import traceback
import webbrowser
import colorama
colorama.init(autoreset=False)
import difflib
from tkinter import Tk, filedialog
from pathlib import Path

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
    return path or None

def ask_file(title="Select a file", filetypes=(("All Files", "*.*"),)):
    """Open dialog to select a single file."""
    root = Tk()
    root.withdraw()
    root.lift()
    root.attributes("-topmost", True)
    path = filedialog.askopenfilename(title=title, filetypes=filetypes)
    root.destroy()
    return path or None


def ask_files(title="Select files", filetypes=(("All Files", "*.*"),)):
    """Open dialog to select multiple files."""
    root = Tk()
    root.withdraw()
    root.lift()
    root.attributes("-topmost", True)
    paths = filedialog.askopenfilenames(title=title, filetypes=filetypes)
    root.destroy()
    return list(paths) if paths else None

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
        
MAX_PATH = 260
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

TOOLS = {}

class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    CYAN = "\033[36m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    MAGENTA = "\033[35m"

def search_tools(query, cutoff=0.5):
    results = []
    q = query.lower()
    for key, tool in TOOLS.items():
        desc = tool["desc"]
        dlow = desc.lower()
        ratio = difflib.SequenceMatcher(None, q, dlow).ratio()
        if q in dlow or ratio >= cutoff:
            results.append((max(ratio, 1.0 if q in dlow else ratio), key, tool))
    results.sort(reverse=True, key=lambda x: x[0])
    return results
    
def register_tool(key, description, entry, blocking=True, group=None, long_desc=None):
    """Register a tool with unique key and description.
    entry: either a callable (function) or string path (relative/absolute).
    """
    TOOLS[str(key)] = {
        "desc": description,
        "long_desc": long_desc or description,
        "entry": entry,
        "blocking": blocking,
        "group": group or "Misc"
    }
                    
                    # color coding
def print_menu_header(text):
    print(f"\n{Colors.MAGENTA}{Colors.BOLD}{text}{Colors.RESET}")

def print_menu_option(num, label, color=None):
    c = color or Colors.GREEN
    print(f"{c}{num}.{Colors.RESET} {label}")

def print_menu_exit(label="Exit"):
    print(f"{Colors.RED}0.{Colors.RESET} {label}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.RESET}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠️ {msg}{Colors.RESET}")

def print_success(msg):
    print(f"{Colors.GREEN}✔️ {msg}{Colors.RESET}")

def print_info(msg):
    print(f"{Colors.CYAN}ℹ️ {msg}{Colors.RESET}")
    
def print_submenu_option(num, label):
    # yellow numbers for submenu tools
    print(f"{Colors.YELLOW}{num}.{Colors.RESET} {label}")
    
    

def list_tools():
    return TOOLS

def resolve_path(path):
    if not isinstance(path, str):
        return path
    if os.path.isabs(path):
        return path
    return os.path.join(BASE_DIR, path)

def run_script(path, args=None, blocking=True):
    """Run a Python script or executable, return exit code."""
    args = args or []
    full_path = resolve_path(path)
    if not os.path.exists(full_path):
        print(f"❌ Tool not found: {full_path}")
        return -1
    try:
        env = os.environ.copy()
        # Ensure all child tools can `import launcherlib` no matter their depth
        env["PYTHONPATH"] = BASE_DIR + os.pathsep + env.get("PYTHONPATH", "")

        cmd = [sys.executable, full_path, *args]
        if blocking:
            proc = subprocess.run(cmd, env=env, check=False)
            return proc.returncode
        else:
            subprocess.Popen(cmd, env=env)
            return 0
    except Exception as e:
        print(f"❌ Failed to run {full_path}: {e}")
        return -1

def run_callable(func):
    """Run a callable tool, return 0 on success, -1 on failure."""
    try:
        func()
        return 0
    except Exception:
        print_error("❌ Error while running tool:")
        traceback.print_exc()
        return -1

def prompt_post_run():
    """Ask user what to do after running a tool."""
    while True:
        print_menu_header("What do you want to do next?")
        print_menu_option("1", "Rerun this tool")
        print_menu_option("2", "Return to launcher")
        print_menu_exit("Exit")

        choice = input("Choose (1/2/0): ").strip()
        if choice == "1":
            return "rerun"
        elif choice == "2":
            return "launcher"
        elif choice == "0":
            sys.exit(0)
        else:
            print_warning(f"❌ Invalid choice. Please enter 1, 2 or 0.")

def launch_tool(tool):
    entry = tool["entry"]
    blocking = tool["blocking"]

    while True:
        if callable(entry):
            rc = run_callable(entry)  # callables always blocking
        elif isinstance(entry, str):
            rc = run_script(entry, blocking=blocking)
        else:
            print_error(f"❌ Unsupported tool entry: {entry}")
            return

        if blocking:
            if rc == 100:
                break
            elif rc != 0:
                print_warning(f"⚠️ Tool exited with error code {rc}.")
            action = prompt_post_run()
            if action == "rerun":
                continue
            elif action == "launcher":
                break
        else:
            # Non-blocking: immediately return to launcher
            break



    