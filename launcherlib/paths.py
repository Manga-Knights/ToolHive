# SPDX-License-Identifier: GPL-3.0-or-later
# ToolHive Launcherlib paths
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
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

MAX_PATH = 260

def resolve_path(path):
    if isinstance(path, Path):
        return path
    path = Path(path)
    if path.is_absolute():
        return path
    return BASE_DIR / path
