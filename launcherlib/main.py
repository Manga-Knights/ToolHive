# SPDX-License-Identifier: GPL-3.0-or-later
# ToolHive Launcherlib main
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
import subprocess
import traceback
from pathlib import Path

from .paths import resolve_path, BASE_DIR
from .prints import print_error, print_menu_exit, print_menu_header, print_menu_option, print_warning
from .helpers import TOOLS


def run_script(path, args=None, blocking=True):
    """Run a Python script or executable, return exit code."""
    args = args or []
    full_path = resolve_path(path)
    
    if not full_path.exists():
        print(f"❌ Tool not found: {full_path}")
        return -1

    try:
        env = os.environ.copy()
        # Convert BASE_DIR to str for PYTHONPATH
        env["PYTHONPATH"] = str(BASE_DIR) + os.pathsep + env.get("PYTHONPATH", "")

        # Convert full_path to str for subprocess
        cmd = [sys.executable, str(full_path), *args]

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
        print_error("Error while running tool:")
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
            print_warning(f"Invalid choice. Please enter 1, 2 or 0.")

def launch_tool(tool):
    entry = tool["entry"]
    blocking = tool["blocking"]

    while True:
        if callable(entry):
            rc = run_callable(entry)  # callables always blocking

        # Accept both str and Path
        elif isinstance(entry, (str, Path)):
            rc = run_script(entry, blocking=blocking)

        else:
            print_error(f"Unsupported tool entry: {entry}")
            return

        if blocking:
            if rc == 100:
                break
            elif rc != 0:
                print_warning(f"Tool exited with error code {rc}.")
            action = prompt_post_run()
            if action == "rerun":
                continue
            elif action == "launcher":
                break
        else:
            # Non-blocking: immediately return to launcher
            break

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
        try:
            entry()
        except Exception:
            print_error("Error while running callable tool:")
            traceback.print_exc()
        return

    # Accept both str and Path
    elif isinstance(entry, (str, Path)):
        path = resolve_path(entry)
        if not path.exists():
            print_error(f"Tool script not found: {path}")
            return

        try:
            env = os.environ.copy()
            # Convert Path to str only here
            env["PYTHONPATH"] = os.pathsep.join([str(BASE_DIR), env.get("PYTHONPATH", "")])

            cmd = [sys.executable, str(path), *extra_args]

            if blocking:
                proc = subprocess.run(cmd, env=env)
                if proc.returncode != 0:
                    print_warning(f"Tool exited with code {proc.returncode}")
            else:
                subprocess.Popen(cmd, env=env)

        except Exception as e:
            print_error(f"Failed to run script: {e}")
            traceback.print_exc()

    else:
        print_error(f"Unsupported tool entry: {entry}")




    