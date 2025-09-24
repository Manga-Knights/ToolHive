# Matching Renaming Tool

A Python utility for **matching and renaming files between source and target folders** based on filename similarity. Ideal for organizing music libraries, image collections, or any files that need alignment between two folders.

---

## Features

- Compare files in a source folder with files in a target folder using **fuzzy matching**.
- Interactive prompts to approve or skip matches.
- Automatically logs unmatched, skipped, or untouched files.
- Supports configurable similarity thresholds (0–100).
- Handles uniform or mixed file extensions; prompts if uncertain.
- Safe renaming using temporary names to prevent collisions.
- CLI-based with optional debug and logging support.
- Works with multiple file types, including audio, video, images, or documents.

---

## Requirements

- Python 3.9+
- [rapidfuzz](https://pypi.org/project/rapidfuzz/) (v3.13.0 recommended)
- [launcherlib](#) (internal utility; setup script included)
- Compatible with Windows, macOS, and Linux.

---

## Installation

1. Clone or download this repository.
2. Run the setup script to install dependencies and prepare the environment:

```
python setup_matching_renaming.py
```
---

##Usage

Run the script via CLI:
```
python matching_renaming.py --source <source_folder> --target <target_folder>
```
---

##optional Argumengts

| Argument       | Description                                     |
| -------------- | ----------------------------------------------- |
| `--source-ext` | File extension for source files (e.g., `.mp3`)  |
| `--target-ext` | File extension for target files (e.g., `.flac`) |
| `--threshold`  | Similarity threshold 0–100 (default: 50)        |
| `--log`        | File path to save skipped/unmatched logs        |
| `--debug`      | Show full traceback on errors                   |

---

##Example Commands

1.Basic usage:

```
python matching_renaming.py --source ./MP3 --target ./FLAC
```

2.Specify extensions and threshold:

```
python matching_renaming.py --source ./MP3 --target ./FLAC --source-ext .mp3 --target-ext .flac --threshold 60
```

3.Enable logging and debug mode:

```
python matching_renaming.py --source ./MP3 --target ./FLAC --log errors.log --debug
```

---

##How It Works

1.The script scans both source and target folders for files with the given extensions.

2.Each source file is compared against target files using fuzzy matching (rapidfuzz).

3.Users are prompted interactively to accept, skip, or reject matches.

4.Matched files are safely renamed, preserving file extensions.

5.Unmatched or skipped files are logged for review.

---

##License

This script is licensed under GPL v3.
Third-party dependencies (rapidfuzz) are included under their own respective licenses. Please see THIRD_PARTY_LICENSES.md for full attribution.

---

##Notes

1.Always run the setup script before first use.

2.Ensure the target folder does not contain critical files that may be overwritten unintentionally.

3.Works best when filenames are reasonably similar; extremely different names may require manual review.