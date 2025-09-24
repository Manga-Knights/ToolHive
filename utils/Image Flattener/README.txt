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
