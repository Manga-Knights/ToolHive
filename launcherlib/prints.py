# SPDX-License-Identifier: GPL-3.0-or-later
# ToolHive Launcherlib prints
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




import colorama
colorama.init(autoreset=False)
from pathlib import Path


class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    CYAN = "\033[36m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    MAGENTA = "\033[35m"

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
    print(f"{Colors.YELLOW}{num}.{Colors.RESET} {label}")
