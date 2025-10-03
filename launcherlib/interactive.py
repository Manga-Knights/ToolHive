# SPDX-License-Identifier: GPL-3.0-or-later
# ToolHive Launcherlib interactive
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




from collections import defaultdict
from pathlib import Path

from .prints import print_menu_exit, print_menu_header, print_menu_option, print_warning, print_submenu_option, Colors
from .helpers import list_tools
from .main import run_child_script
from .search import search_mode


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