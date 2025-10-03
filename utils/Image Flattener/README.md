# SPDX-License-Identifier: GPL-3.0-or-later
# ToolHive Image Flattener
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




# Image Flattener

**Part of ToolHive Launcher**  
License: GPL-3.0-or-later

---

## Purpose

The Image Flattener moves all images from nested subfolders into a single master folder, optionally renaming files safely and avoiding collisions.  

It supports common image formats: `.jpg`, `.jpeg`, `.png`, `.webp`, `.bmp`, `.tif`, `.tiff`, `.gif`.

---

## Setup
-------------------------------------------------IMPORTANT-----------------------------------------------------
Before running, execute the setup script:

```
python setup_image_flattener.py
```

---------------------------------------------------------------------------------------------------------------

##Usage

Run directly via command line:
eg.

```
python image_flattener.py --input "C:/path/to/master/folder" --ext jpg,png --silent
```
--

##Options
| Flag            | Description                                                                      |
| --------------- | -------------------------------------------------------------------------------- |
| `--input`       | Path to master folder. If omitted, a GUI folder picker will open.                |
| `--ext`         | Comma-separated list of file extensions to include (default: all common images). |
| `--maxfilename` | Maximum filename length (default: 180).                                          |
| `--preview`     | Number of moved files to preview in the console (default: 10).                   |
| `--silent`      | Disable GUI popups for CLI-only usage.                                           |
| `--debug`       | Show full traceback on errors.                                                   |

--

##License

This tool is released under the GNU GPL v3, same as the main ToolHive Launcher.
