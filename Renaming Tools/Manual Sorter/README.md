# Manual Sorter

A Python GUI tool for **manually reordering and renaming files** in any folder. Ideal for images, audio, or other file types where order matters or batch renaming is needed.

---

## Features

- Drag-and-drop interface to reorder files visually.
- Supports **image thumbnails** for quick identification.
- Rename files sequentially (`001.ext`, `002.ext`, etc.).
- Optionally include non-image files in renaming.
- Safe renaming with temporary names to prevent collisions.
- Cross-platform support (Windows, macOS, Linux).
- Minimal setup; run `setup_manual_sorter.py` once before first use.

---

## Requirements

- Python 3.9+
- [PyQt5](https://pypi.org/project/PyQt5/) (v5.15.11 recommended)
- [launcherlib](#) (internal utility; setup script included)

---

## Installation

1. Clone or download this repository.
2. Run the setup script:

```
python setup_manual_sorter.py
```

---

##Usage

1.Run the script:

```
python manual_sorter.py
```

2.Click Select Folder and Load Files to choose a folder.

3.Drag and drop files in the desired order.

4.Click Rename Files to 001.ext, 002.ext, ... to apply sequential renaming.

5.The tool automatically generates thumbnails for supported image files:
default formats: .jpg, .jpeg, .png, .bmp, .webp, .tif, .tiff, .gif, .ico, .heic, .heif, .svg, .avif
Non-image files can also be included optionally.

---

##Notes

1.Always run the setup script before first use.

2.Renaming is destructive; make backups if needed.

3.Files are renamed sequentially based on the current order in the list.

---

##License

This script is licensed under GPL v3.
Third-party dependencies (PyQt5) are included under their own licenses. See THIRD_PARTY_LICENSES.md for attribution.