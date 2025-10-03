# SPDX-License-Identifier: GPL-3.0-or-later
# ToolHive ImageCount Reporter
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




# Image Count Reporter

**Part of ToolHive Launcher**  
License: GPL-3.0-or-later

---

## Purpose

The Image Count Reporter scans a folder and all its subfolders, counting image files by type.  
It produces a ranked list of folders by total image count, helping you quickly identify dense folders or organize content.

Supported image extensions: `.jpg`, `.jpeg`, `.png`, `.webp`, `.bmp`, `.tiff`, `.tif`, `.gif`.

---

## Setup
-------------------------------------------------IMPORTANT-----------------------------------------------------
Before running, execute the setup script:

```
python setup_image_flattener.py
```

---------------------------------------------------------------------------------------------------------------

## Usage

### CLI Mode

```
python imagecount_reporter.py --input "/path/to/folder" --ext jpg,png --asc --output result.txt
```
--

##Options
| Flag       | Description                                                                  |
| ---------- | ---------------------------------------------------------------------------- |
| `--input`  | Path to the main folder. If omitted, GUI mode will start.                    |
| `--ext`    | Comma-separated list of file extensions to include (default: common images). |
| `--asc`    | Sort folders ascending by total images.                                      |
| `--des`    | Sort folders descending by total images.                                     |
| `--output` | Save the ranked output to a text file.                                       |
| `--log`    | Save errors and tracebacks to a log file.                                    |
| `--debug`  | Show full tracebacks on errors for troubleshooting.                          |

--

##GUI Mode

Run without --input to use a simple GUI interface for folder selection and optional saving of results

--

##License

This tool is released under the GNU GPL v3, same as the main ToolHive Launcher.
