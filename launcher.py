# SPDX-License-Identifier: GPL-3.0-or-later
# ToolHive Launcher
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
from pathlib import Path

from launcherlib.prints import print_error
from launcherlib.config import SUBCOMMANDS
from launcherlib.main import run_child_script
from launcherlib.help import show_help
from launcherlib.search import search_mode
from launcherlib.interactive import interactive_menu


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

