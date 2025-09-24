# ToolHive
Complete Ecosystem for managing and using all your tools.organize tools in types and fuzzy search them. simple and light tool launcher. add your own tools easily, launch them, with argument forwarding support as well as interactive terminal input. Entire manga downloading , managing , reading toolkit included.


# ToolHive Launcher

**ToolHive** is a Python-based launcher for organizing, viewing, and processing various tools in a unified interface. It provides both an interactive menu and command-line subcommands for quickly running your child tools.

---

## Features

- Interactive menu for browsing and launching tools.
- CLI subcommands for fast execution.
- Search mode to quickly find tools.
- Supports callable tools (Python functions) and script-based tools.
- Colored terminal output for better readability (cross-platform).

---

## Installation

1. Clone the repository:

```
git clone https://github.com/Manga-Knights/ToolHive.git
cd ToolHive
```

2. Make sure you have python installed.

3.Dependencies:
```
pip install colorama
```

--> Optional tools (child scripts) may require additional libraries or binaries. See each tool's documentation for details.


##Usage
1.Interactive Mode

Simply run the launcher without arguments:
```
python launcher.py
```
you can search tools by name or type "m" for manual mode.

2.CLI Subcommands

Run tools directly using subcommands:
eg.
```
python launcher.py renamer --subfolder-prefix ch --debug
python launcher.py forge-cbz --overwrite
```

3.Available subcommands:

renamer → Rename Chapters and Images

manual-sort → Manual Sorter

match-rename → Matching Renaming

flatten → Image Flattener

forge-cbz → CBZ Forger

forge-pdf → PDF Forger

convert-html → HTML Converter

view → Manga Reader

compare → Image Comparator

count → Folder Image Count Reporter

--> Flags after the subcommand are forwarded directly to the child tool.


##Adding Your Own Tools

You can add your own tools by registering them in launcher.py:
register_tool(
    "11", "Your Tool Name", "path/to/your_tool.py",
    group="Custom Tools",
    long_desc="Description of what your tool does"
)

--> entry can be a Python callable or a string path to a script.

--> blocking determines whether the launcher waits for the tool to finish.

##
License

This project is licensed under the GNU General Public License v3.0 (GPL-3.0-or-later).

You may use, modify, and redistribute the launcher and your own child tools, provided:

Your modified version is also distributed under GPLv3.

You include proper attribution (copyright notice).

No proprietary redistribution is allowed without following GPL terms.

Full license text: https://www.gnu.org/licenses/gpl-3.0.en.html



