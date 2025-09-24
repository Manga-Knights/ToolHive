# SPDX-License-Identifier: GPL-3.0-or-later
# ToolHive Launcher
# Copyright (C) 2025 Your Name
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
import sys

# --- Setup guard ---
setup_incomplete = True  # Flipped to False by setup.py

if setup_incomplete:
    import os, sys, subprocess

    print(f"⚠️ Setup has not been run yet. Please run the setup script first.")

    # Determine setup script path dynamically
    script_name = os.path.splitext(os.path.basename(__file__))[0]
    setup_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"setup_{script_name}.py")

    if os.path.exists(setup_path):
        print(f"Launching {setup_path}...")
        subprocess.run([sys.executable, setup_path])
    else:
        print(f"❌ Setup script not found: {setup_path}")

    sys.exit(1)

# --- launcherlib import ---
try:
    import launcherlib
    from launcherlib import (
        print_error,
        print_warning,
        print_success,
        print_info,
        print_menu_header,
        ask_directory,
        ask_saveas_filename,
    )
except ImportError:
    print("❌ launcherlib not found. Please run the setup script first.")
    sys.exit(1)

# --- Original code continues below ---

from PyQt5.QtWidgets import (
    QApplication, QWidget, QListWidget, QListWidgetItem,
    QVBoxLayout, QPushButton, QFileDialog, QLabel, QMessageBox
)
from PyQt5.QtGui import QIcon, QPixmap, QImageReader
from PyQt5.QtCore import QSize, Qt, QObject, pyqtSignal, QRunnable, QThreadPool

# All common image extensions
IMAGE_EXTENSIONS = {
    '.jpg', '.jpeg', '.png', '.bmp', '.webp', '.tif', '.tiff',
    '.gif', '.ico', '.heic', '.heif', '.svg', '.avif'
}

# ---------------- Worker ----------------
class ThumbnailWorkerSignals(QObject):
    finished = pyqtSignal(int, QIcon)  # item index, loaded icon

class ThumbnailWorker(QRunnable):
    def __init__(self, index, path, size=128):
        super().__init__()
        self.index = index
        self.path = path
        self.size = size
        self.signals = ThumbnailWorkerSignals()

    def run(self):
        try:
            reader = QImageReader(self.path)
            reader.setScaledSize(QSize(self.size, self.size))  # decode low-res
            image = reader.read()
            if not image.isNull():
                pixmap = QPixmap.fromImage(image)
                icon = QIcon(pixmap.scaled(self.size, self.size, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                self.signals.finished.emit(self.index, icon)
            else:
                placeholder = QPixmap(self.size, self.size)
                placeholder.fill(Qt.gray)
                self.signals.finished.emit(self.index, QIcon(placeholder))
        except Exception:
            placeholder = QPixmap(self.size, self.size)
            placeholder.fill(Qt.gray)
            self.signals.finished.emit(self.index, QIcon(placeholder))

# ---------------- GUI Class ----------------
class DragDropRenamer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Manual Drag-and-Drop Renamer")
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        self.label = QLabel("Select a folder to begin")
        layout.addWidget(self.label)

        self.list_widget = QListWidget()
        self.list_widget.setIconSize(QSize(128, 128))
        self.list_widget.setDragDropMode(QListWidget.InternalMove)
        layout.addWidget(self.list_widget)

        self.load_button = QPushButton("Select Folder and Load Files")
        self.load_button.clicked.connect(self.load_files)
        layout.addWidget(self.load_button)

        self.rename_button = QPushButton("Rename Files to 001.ext, 002.ext, ...")
        self.rename_button.clicked.connect(self.rename_files)
        layout.addWidget(self.rename_button)

        self.setLayout(layout)
        self.folder_path = None
        self.files = []

        self.threadpool = QThreadPool()

    # ---------------- Load Files ----------------
    def load_files(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if not folder:
            return

        self.folder_path = folder
        self.list_widget.clear()

        all_files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
        images = [f for f in all_files if os.path.splitext(f)[1].lower() in IMAGE_EXTENSIONS]
        non_images = [f for f in all_files if os.path.splitext(f)[1].lower() not in IMAGE_EXTENSIONS]

        include_non_images = False
        if non_images:
            reply = QMessageBox.question(
                self, "Non-Image Files Detected",
                f"⚠️ The folder contains {len(non_images)} non-image files.\n"
                "Do you want to include them in renaming?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            include_non_images = reply == QMessageBox.Yes

        self.files = images + non_images if include_non_images else images

        placeholder = QPixmap(128, 128)
        placeholder.fill(Qt.gray)
        placeholder_icon = QIcon(placeholder)

        for i, fname in enumerate(self.files):
            item = QListWidgetItem(fname)
            ext = os.path.splitext(fname)[1].lower()
            item.setData(Qt.UserRole, os.path.join(folder, fname))
            item.setIcon(placeholder_icon)
            self.list_widget.addItem(item)

            if ext in IMAGE_EXTENSIONS:
                worker = ThumbnailWorker(i, os.path.join(folder, fname), size=128)
                worker.signals.finished.connect(self.set_item_icon)
                self.threadpool.start(worker)

        self.label.setText(f"Loaded {len(self.files)} files from:\n{folder}")

    # ---------------- Update Icon ----------------
    def set_item_icon(self, index, icon):
        item = self.list_widget.item(index)
        if item:
            item.setIcon(icon)

    # ---------------- Rename Files ----------------
    def rename_files(self):
        if not self.folder_path or self.list_widget.count() == 0:
            QMessageBox.warning(self, "No Files", "No files loaded to rename.")
            return

        temp_map = []
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            orig_path = item.data(Qt.UserRole)
            ext = os.path.splitext(orig_path)[1]
            n = 0
            while True:
                temp_name = os.path.join(self.folder_path, f"__temp_{i:03d}_{n}{ext}")
                if not os.path.exists(temp_name):
                    break
                n += 1
            os.rename(orig_path, temp_name)
            temp_map.append((temp_name, ext))

        for i, (temp_path, ext) in enumerate(temp_map):
            n = 0
            while True:
                final_name = os.path.join(self.folder_path, f"{i+1:03d}" + (f"_{n}" if n > 0 else "") + ext)
                if not os.path.exists(final_name):
                    break
                n += 1
            os.rename(temp_path, final_name)

        QMessageBox.information(self, "Done", "Files renamed successfully.")
        self.list_widget.clear()
        self.label.setText("Renaming complete. You can close the window.")

# ---------------- Main ----------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DragDropRenamer()
    window.show()
    sys.exit(app.exec_())
