# ToolHive Renamer

A Python tool for **renaming subfolders and files recursively** with a one-time setup mechanism.  
Includes **CLI and GUI support**.

---

## Features

- Takes input folder (CLI or GUI)
- Rename first-level subfolders with a custom prefix
- Rename all files with sequential numbering
- Pre-scan for conflicts before renaming
- GUI prompt if no CLI arguments are provided
- One-time setup with automatic dependency installation and environment preparation
- Safe `setup_incomplete` flag to prevent accidental re-runs

---

## Requirements

- Python 3.9+
- [natsort](https://pypi.org/project/natsort/) >= 8.4.0
- `launcherlib.py` (local module; placed anywhere above the main script)

Other dependencies are installed automatically by the setup script.

---

## Installation / Setup

1. Clone the repository:

```
git clone https://github.com/Manga-Knights/ToolHive.git
```

2.Ensure setup_renamer.py and renamer.py are in the same folder.

3.Run the setup script (first-time run only):
```
python setup_renamer.py
```

##Usage
1.CLI

Basic usage:
```
python renamer.py --input "C:/Images"
```

Specify extensions:
```
python renamer.py --input "C:/Images" --ext jpg,png
```

Change subfolder prefix:
```
python renamer.py --input "C:/Images" --subfolder-prefix chapter
```

Silent mode (no prompts):
```
python renamer.py --input "C:/Images" --silent

```
Log errors and enable debug:
```
python renamer.py --input "C:/Images" --log errors.txt --debug
```

2.GUI
Simply run:
```
python renamer.py
```

##License

This project is licensed under the GNU GPL v3 , same as the launcher.
all third party licences all properly mentioned and credits are given in THIRD_PARTY_LICENCES.md

## Detailed Workflow

1. Pre-scan / setup checks

#When you run renamer.py:

The script first checks if setup_incomplete is True.

-If yes → it runs setup_renamer.py (installs dependencies, locates launcherlib.py, flips the flag to False).

-If no → it proceeds normally.

#Setup ensures:

-Python ≥ 3.9.

-natsort is installed (version ≥ 8.4.0).

-launcherlib.py exists somewhere above the script.

------------------------------------------------------------

2. Input handling

You can run the script in two ways:

#GUI mode (no CLI arguments):

-Prompts user to select a “master folder” using a directory chooser.

#CLI mode (with --input):

-You provide a path to the master folder.

#Optional arguments:

--ext → comma-separated list of extensions. Defaults to: .png, .jpg, .jpeg, .webp, .bmp, .gif.

--subfolder-prefix → prefix for the first-level subfolders below the master folder (default: ch).

--silent → skips prompts if conflicts are detected.

--log → logs errors to a file.

--debug → prints full tracebacks in case of errors.

---------------------------------------------------------------------

3. Pre-scan for conflicts

#Before renaming anything, the script runs a pre-scan:

-Recursively traverses the master folder.

-Checks for mixed folders (folders containing both files and subfolders).

-Checks for file name collisions — whether any files already match the expected sequential numbering.

-Checks for subfolder name collisions (expected prefix + number).

#If issues are found:

-In non-silent mode → displays warnings and prompts user to continue.

-In silent mode → returns True to proceed anyway.

This ensures you are warned before potentially destructive renames.

----------------------------------------------------------------------------

4. Renaming subfolders

#Only renames first-level subfolders under the master folder.

-Uses natsorted() to sort them naturally (e.g., Chapter 1, Chapter 2, Chapter 10).

-Renames each subfolder to:

<prefix><number>

Example: prefix=ch → ch1, ch2, ch3 …

#Uses a temporary renaming step (__tmp_1, __tmp_2, …) to avoid collisions when folder names overlap.

-Handles name collisions gracefully by adding _1, _2, … suffixes.

--------------------------------------------------------------------------------------------------------

6. Recursive operation

The renaming process is fully recursive:

-Subfolder renaming: only one level deep under master folder.

-file renaming: goes through all subfolders, any depth.

-Ensures proper sorted order in both cases (using natsorted for subfolders, alphabetical for files).

---------------------------------------------------------------------------------------------------------

7. CLI / GUI flow

#CLI flow: run_renamer_cli()

-Pre-scan → subfolder rename → recursive file rename

#GUI flow: run_renamer_gui()

-Folder chooser → calls the same CLI function internally.