# SPDX-License-Identifier: GPL-3.0-or-later
# ToolHive Launcherlib helpers
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




import difflib
from pathlib import Path


TOOLS = {}

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
    """
    Register a tool with unique key and description.

    :param entry: either a callable (function) or a string/Path path (relative/absolute)
    """
    # Convert string paths to Path objects
    if isinstance(entry, str):
        entry = Path(entry)

    TOOLS[str(key)] = {
        "desc": description,
        "long_desc": long_desc or description,
        "entry": entry,        # always Path or callable now
        "blocking": blocking,
        "group": group or "Misc"
    }


def list_tools():
    return TOOLS