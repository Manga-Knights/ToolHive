# SPDX-License-Identifier: GPL-3.0-or-later
# ToolHive Launcher core
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




import subprocess
import traceback
import os
import sys
from pathlib import Path

from launcherlib.prints import print_error, print_warning
from launcherlib.paths import resolve_path, BASE_DIR
from launcherlib.helpers import TOOLS


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
