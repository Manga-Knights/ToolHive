# SPDX-License-Identifier: GPL-3.0-or-later
# ToolHive Launcherlib search
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

from .prints import print_warning, print_menu_header, print_submenu_option
from .helpers import search_tools


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