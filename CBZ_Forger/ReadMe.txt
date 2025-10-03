# SPDX-License-Identifier: GPL-3.0-or-later
# ToolHive CBZ Forger
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




---------------------------------------CBZ Forger----------------------------------------------------------------------------------------------------------------------------------------------------------------

CBZ Forger is a Python tool to convert folders of images into CBZ archives. It supports optional BMP → PNG conversion, extension filtering, overwrite handling, logging, silent mode, and debug output.



1.Features

Convert BMP images to PNG safely.

Natural sorting of images.

Create CBZ archives with optional overwrite.

Supports custom image extensions.

Logging system with selective log levels.

silent mode for automated pipelines.

Full traceback support for debugging.



2.Requirements

you can install these yourselves or can run simply setup.py (see 3.Installation for more details)

Python 3.8+

Pillow (pip install pillow)

natsort (pip install natsort)

tqdm (pip install tqdm)

(Other dependencies are part of standard library.)




3.Installation

Clone or download this repository.

Navigate to the directory:

cd /path/to/cbz_forger


Install dependencies:

python setup.py




4.Usage
Basic Command
python cbz_forger.py --input /path/to/master_folder


This will:

Ask to convert BMP images if present.

Create CBZ files from subfolders of images.

Save CBZ files in the input folder by default.




5.Optional Flags
Flag	Description
--output	Output folder for CBZ files (default = input folder).
--skip-bmp	Skip BMP conversion.
--ext	Comma-separated list of image extensions (e.g., .jpg,.png).
--silent	Suppress all prints and progress bars (except BMP collision prompt).
--debug	Show full Python traceback on errors.
--log [file]	Write log messages to file. Default = cbz_forger.log if file not provided.
--overwrite	Overwrite existing CBZ files instead of sanitizing names.
--log-info	Log INFO messages.
--log-warning	Log WARNING messages.
--log-error	Log ERROR messages.
-h	Show help, usage, and examples.




6.Examples

1) Convert folders to CBZ using default settings

python cbz_forger.py --input ./comics


2) Specify output folder

python cbz_forger.py --input ./comics --output ./cbz_output


3) Skip BMP conversion

python cbz_forger.py --input ./comics --skip-bmp


4) Only include specific image types

python cbz_forger.py --input ./comics --ext .jpg,.png


5) silent mode with logging

python cbz_forger.py --input ./comics --silent --log cbz.log


6) Overwrite existing CBZ files

python cbz_forger.py --input ./comics --overwrite


7) Full debug output

python cbz_forger.py --input ./comics --debug




7.Notes

Interactive BMP prompt: If a BMP converts to PNG but the PNG already exists, you’ll be prompted to sanitize or cancel.

silent mode (--silent) suppresses prints and progress bars but still shows BMP collision prompts.

Logging: The log file is created if it doesn’t exist. Invalid paths will print an error.

Extensions: Invalid extensions halt execution and print usage examples.



8.Logging

Use --log with optional filters:

python cbz_forger.py --input ./comics --log cbz.log --log-info --log-warning


--log-info: Logs INFO messages.

--log-warning: Logs WARNING messages.

--log-error: Logs ERROR messages.



9.Error Handling

--debug prints full Python tracebacks for any error.

--silent overrides debug printing.

Invalid input folder triggers interactive fallback.

Invalid extensions show usage examples and exit.



10.Development / Debugging Tips

developer's guide included in the folder. refer it for more advanced details and further modification help.

Lazy imports reduce startup time (PIL, tqdm, natsorted only load when needed).

Interactive BMP prompts can block scripts; use --skip-bmp for automated runs.

All operations are logged if --log is enabled.

CBZ file collisions are automatically sanitized unless --overwrite is used.



11.License

Free to use, modify, and distribute. Commercial use allowed as long as your tool remains free.