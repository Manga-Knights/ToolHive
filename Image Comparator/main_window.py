"""
Main window for Image Comparator application
"""
import os
import logging
import sys
from PyQt5.QtCore import Qt, QThreadPool, QTimer
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog,
    QLabel, QScrollArea, QComboBox, QCheckBox, QStatusBar, 
    QMessageBox, QLineEdit
)
from PyQt5.QtGui import QKeySequence, QPixmap, QIntValidator, QMovie, QColor
from PyQt5.QtWidgets import QShortcut
from pathlib import Path

from graphics_view import GraphicsView
from workers import ImageLoadWorker, MetricsWorker
from cache import ImageCache
from constants import *
from utils import get_sorted_image_files, format_file_size, colorize_metrics

logger = logging.getLogger(__name__)

def resource_path(relative_path: str) -> Path:
    """Resolve resource path for PyInstaller compatibility."""
    # When running in PyInstaller bundle, sys._MEIPASS points to the temp dir
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / relative_path
    # Otherwise, use the current script’s directory (not the CWD)
    return Path(__file__).resolve().parent / relative_path

class ImageCompareWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.image_views = []
        self.image_pairs = []
        self.current_index = 0
        self.sync_enabled = True  # Zoom and scroll sync state
        
        # Caching and loading
        self.cache = ImageCache()
        self.thread_pool = QThreadPool()
        self.thread_pool.setMaxThreadCount(MAX_THREAD_COUNT)
        self.active_workers = []
        
        # Timers
        self.navigation_timer = QTimer()
        self.navigation_timer.setSingleShot(True)
        self.navigation_timer.timeout.connect(self._load_full_quality)
        
        self.preload_timer = QTimer()
        self.preload_timer.setSingleShot(True)
        self.preload_timer.timeout.connect(self._start_preloading)
        
        logger.info("Image Comparator initialized")
        
        self._init_ui()
        self._setup_shortcuts()
        self.add_image_view()

    def _init_ui(self):
        """Initialize the user interface"""
        self.setStyleSheet(DARK_THEME)
        self.setWindowTitle("Image Comparator")
        self.setMinimumSize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)

        # Main layout
        self.layout = QVBoxLayout(self)
        
        # Scrollable images area
        self.images_widget = QWidget()
        self.images_layout = QVBoxLayout(self.images_widget)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.images_widget)
        self.layout.addWidget(self.scroll_area)

        # Controls in separate widget for easy show/hide
        self.controls_widget = QWidget()
        self.controls_layout = QVBoxLayout(self.controls_widget)
        self.controls_layout.setContentsMargins(0, 0, 0, 0)
        
        self._create_controls()
        self.controls_layout.addLayout(self.button_layout)
        
        self.layout.addWidget(self.controls_widget)

        # Status bar
        self._create_status_bar()
        self.layout.addWidget(self.status_bar)

    def _create_controls(self):
        """Create control buttons and widgets"""
        self.button_layout = QHBoxLayout()

        # Resolution controls
        self.resolution_label = QLabel("Resolution")
        self.resolution_combo = QComboBox()
        self.resolution_combo.setFixedWidth(120)
        self.resolution_combo.currentTextChanged.connect(self.set_resolution)

        # Antialiasing toggle
        self.antialiasing_checkbox = QCheckBox("Antialiasing")
        self.antialiasing_checkbox.setChecked(True)
        self.antialiasing_checkbox.stateChanged.connect(self.toggle_antialiasing)

        # Sync lock/unlock toggle
        self.sync_checkbox = QCheckBox("Sync Lock")
        self.sync_checkbox.setChecked(True)
        self.sync_checkbox.setStyleSheet("color: #00FF00; font-weight: bold;")
        self.sync_checkbox.stateChanged.connect(self.toggle_sync)

        # Image counter with editable input
        self.counter_input = QLineEdit()
        self.counter_input.setFixedWidth(50)
        self.counter_input.setAlignment(Qt.AlignCenter)
        # Don't use validator - we'll validate manually to allow empty state
        # self.counter_input.setValidator(QIntValidator(1, 99999))
        self.counter_input.returnPressed.connect(self.jump_to_input_page)
        self.counter_input.editingFinished.connect(self.reset_counter_display)
        self.counter_input.setStyleSheet("color: #00FFFF; font-weight: bold; background-color: #1e1e1e;")
        
        self.counter_total = QLabel("/ 0")
        self.counter_total.setStyleSheet("color: #00FFFF; font-weight: bold;")

        # Path labels
        self.left_path_label = QLabel("")
        self.right_path_label = QLabel("")

        # Action buttons
        self.save_button = QPushButton("Save comparison")
        self.next_button = QPushButton("Next →")
        self.prev_button = QPushButton("← Prev")

        # Apply styles
        for button in [self.save_button, self.next_button, self.prev_button]:
            button.setStyleSheet(COMMON_BUTTON_STYLE)

        # Layout arrangement
        self.button_layout.addWidget(self.resolution_label)
        self.button_layout.addWidget(self.resolution_combo)
        self.button_layout.addWidget(self.antialiasing_checkbox)
        self.button_layout.addWidget(self.sync_checkbox)
        self.button_layout.addWidget(self.counter_input)
        self.button_layout.addWidget(self.counter_total)
        self.button_layout.addStretch()
        self.button_layout.addWidget(self.left_path_label)
        self.button_layout.addStretch()
        self.button_layout.addWidget(self.right_path_label)
        self.button_layout.addWidget(self.prev_button)
        self.button_layout.addWidget(self.next_button)
        self.button_layout.addWidget(self.save_button)

        # Connect signals
        self.save_button.clicked.connect(self.save_comparison)
        self.next_button.clicked.connect(self.show_next)
        self.prev_button.clicked.connect(self.show_previous)

    def _create_status_bar(self):
        """Create status bar with version and metrics display"""
        self.status_bar = QStatusBar()
        self.version = QLabel(VERSION_STRING)
        self.resolution_status = QLabel("None")
        self.cache_status = QLabel("Cache: 0/0/0")
        self.cache_status.setStyleSheet("color: #888;")
        self.filesize_label = QLabel("Size: -- / --")
        self.filesize_label.setStyleSheet("color: #888;")
        self.metrics_label = QLabel("No metrics yet")
        self.metrics_label.setStyleSheet("padding: 4px;")
        
        self.status_bar.addWidget(self.version)
        self.status_bar.addWidget(self.resolution_status)
        self.status_bar.addWidget(self.cache_status)
        self.status_bar.addWidget(self.filesize_label)
        self.status_bar.addWidget(self.metrics_label, 1)

    def _setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        # Navigation shortcuts
        QShortcut(QKeySequence(Qt.Key_Right), self).activated.connect(self.show_next)
        QShortcut(QKeySequence(Qt.Key_Left), self).activated.connect(self.show_previous)
        
        # Jump shortcuts
        QShortcut(QKeySequence(Qt.Key_Home), self).activated.connect(self.jump_to_first)
        QShortcut(QKeySequence(Qt.Key_End), self).activated.connect(self.jump_to_last)
        
        # Page navigation (10 images)
        QShortcut(QKeySequence(Qt.Key_PageUp), self).activated.connect(self.jump_backward_10)
        QShortcut(QKeySequence(Qt.Key_PageDown), self).activated.connect(self.jump_forward_10)
        
        # Fullscreen toggle
        QShortcut(QKeySequence(Qt.Key_F), self).activated.connect(self.toggle_fullscreen)
        
        # Sync lock/unlock toggle
        QShortcut(QKeySequence(Qt.Key_L), self).activated.connect(self.toggle_sync_shortcut)
        
        # Save shortcut (Ctrl+S)
        QShortcut(QKeySequence.Save, self).activated.connect(self.save_comparison)

    def add_image_view(self):
        """Add a new pair of image views"""
        row = QHBoxLayout()
        left_view = GraphicsView()
        right_view = GraphicsView()

        # Configure views
        for view in [left_view, right_view]:
            view.image_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            view.image_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            view.image_view.photoAdded.connect(self.add_resolution)

        # Store references for sync control
        self.left_view_ref = left_view.image_view
        self.right_view_ref = right_view.image_view
        
        # Connect sync
        self._connect_sync_with_flag()

        row.addWidget(left_view)
        row.addWidget(right_view)
        self.images_layout.addLayout(row)
        self.image_views.append((left_view, right_view))
        
        logger.info("Image view pair added")
    
    def _connect_sync_with_flag(self):
        """Connect scroll and zoom sync with flag checking"""
        view1 = self.left_view_ref
        view2 = self.right_view_ref
        
        # Scroll sync with flag checking
        updating = {"horizontal": False, "vertical": False}

        def sync_scroll(orientation, value, source_view):
            if not self.sync_enabled:
                return
                
            if updating[orientation]:
                return

            updating[orientation] = True
            for target in [view1, view2]:
                if target == source_view:
                    continue
                scrollbar = target.verticalScrollBar() if orientation == "vertical" else target.horizontalScrollBar()
                source_scrollbar = source_view.verticalScrollBar() if orientation == "vertical" else source_view.horizontalScrollBar()
                if source_scrollbar.maximum() == 0:
                    scrollbar.setValue(0)
                else:
                    fraction = value / source_scrollbar.maximum()
                    scrollbar.setValue(int(fraction * scrollbar.maximum()))
            updating[orientation] = False

        for view in [view1, view2]:
            view.horizontalScrollBar().valueChanged.connect(
                lambda val, v=view: sync_scroll("horizontal", val, v)
            )
            view.verticalScrollBar().valueChanged.connect(
                lambda val, v=view: sync_scroll("vertical", val, v)
            )
        
        # Zoom sync
        view1.transformChanged.connect(lambda t: self.sync_enabled and view2.set_transform(t))
        view2.transformChanged.connect(lambda t: self.sync_enabled and view1.set_transform(t))

    def iter_all_views(self):
        """Iterator for all image views"""
        for left, right in self.image_views:
            yield left.image_view
            yield right.image_view

    def set_transform(self, transform):
        """Apply transform to all views"""
        for view in self.iter_all_views():
            view.set_transform(transform)

    def toggle_antialiasing(self, state):
        """Toggle antialiasing on all views"""
        enabled = state == Qt.Checked
        for view in self.iter_all_views():
            view.set_antialiasing(enabled)
        logger.info(f"Antialiasing {'enabled' if enabled else 'disabled'}")
    
    def toggle_sync(self, state):
        """Toggle sync lock/unlock"""
        self.sync_enabled = state == Qt.Checked
        color = "#00FF00" if self.sync_enabled else "#FF5555"
        self.sync_checkbox.setStyleSheet(f"color: {color}; font-weight: bold;")
        logger.info(f"Sync {'LOCKED' if self.sync_enabled else 'UNLOCKED'}")
    
    def toggle_sync_shortcut(self):
        """Toggle sync via keyboard shortcut"""
        self.sync_checkbox.setChecked(not self.sync_checkbox.isChecked())

    def add_resolution(self, width, height):
        """Add resolution option to combo box"""
        resolution = f"{width}x{height}"
        if self.resolution_combo.findText(resolution) == -1:
            self.resolution_combo.addItem(resolution)

    def set_resolution(self, resolution):
        """Set resolution for all images"""
        try:
            w, h = map(int, resolution.split("x"))
        except ValueError:
            return
        
        for view in self.iter_all_views():
            if view.scene().items():
                view.scene().items()[0].setPixmap(
                    view.original_pixmap.scaled(w, h, Qt.KeepAspectRatio)
                )
                view.setSceneRect(0, 0, w, h)
        
        self.resolution_status.setText(resolution)
        self.resolution_status.setStyleSheet("color: lime")

    def save_comparison(self):
        """Save comparison screenshot"""
        file_path, _ = QFileDialog.getSaveFileName(
            None, "Save Comparison Screenshot", "", "JPEG Image Files (*.jpg)"
        )
        if file_path:
            try:
                screenshot = self.images_widget.grab()
                screenshot.save(file_path, "jpg")
                logger.info(f"Saved screenshot as {file_path}")
                from PyQt5.QtWidgets import QApplication
                QApplication.exit(99)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to save screenshot: {e}")

    # Navigation methods
    def show_next(self):
        if self.current_index + 1 < len(self.image_pairs):
            self.current_index += 1
            self._navigate_to_current()

    def show_previous(self):
        if self.current_index - 1 >= 0:
            self.current_index -= 1
            self._navigate_to_current()
    
    def jump_to_first(self):
        if self.image_pairs and self.current_index != 0:
            self.current_index = 0
            self._navigate_to_current()
    
    def jump_to_last(self):
        if self.image_pairs and self.current_index != len(self.image_pairs) - 1:
            self.current_index = len(self.image_pairs) - 1
            self._navigate_to_current()
    
    def jump_forward_10(self):
        if self.image_pairs:
            self.current_index = min(self.current_index + 10, len(self.image_pairs) - 1)
            self._navigate_to_current()
    
    def jump_backward_10(self):
        if self.image_pairs:
            self.current_index = max(self.current_index - 10, 0)
            self._navigate_to_current()
    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        if self.isFullScreen():
            self.showNormal()
            self.controls_widget.show()
            self.status_bar.show()
            logger.info("Exited fullscreen")
        else:
            self.showFullScreen()
            self.controls_widget.hide()
            self.status_bar.hide()
            logger.info("Entered fullscreen")

    def _navigate_to_current(self):
        """Navigate to current index with smart loading"""
        self.preload_timer.stop()
        self.navigation_timer.stop()
        
        self._display_cached_or_placeholder()
        
        evicted = self.cache.evict_distant(self.current_index)
        if evicted > 0:
            self._update_cache_status()
        
        self.navigation_timer.start(NAVIGATION_DELAY_MS)
        self.preload_timer.start(PRELOAD_DELAY_MS)
        self._update_counter()

    def _update_counter(self):
        """Update image counter display"""
        if self.image_pairs:
            self.counter_input.setText(str(self.current_index + 1))
            self.counter_total.setText(f"/ {len(self.image_pairs)}")
        else:
            self.counter_input.setText("0")
            self.counter_total.setText("/ 0")
    
    def jump_to_input_page(self):
        """Jump to page number entered in input field"""
        try:
            text = self.counter_input.text().strip()
            if not text:
                self.reset_counter_display()
                return
                
            page_num = int(text)
            if 1 <= page_num <= len(self.image_pairs):
                self.current_index = page_num - 1
                self._navigate_to_current()
                logger.info(f"Jumped to page {page_num}")
            else:
                logger.warning(f"Invalid page number: {page_num}")
                self.reset_counter_display()
        except ValueError:
            logger.error("Invalid input in page counter")
            self.reset_counter_display()
    
    def reset_counter_display(self):
        """Reset counter to current page if editing was cancelled"""
        # When focus is lost, always reset to show current page
        # This handles all cases: empty input, invalid input, or user clicking away
        self._update_counter()

    def _update_cache_status(self):
        """Update cache status display"""
        stats = self.cache.get_cache_stats()
        self.cache_status.setText(
            f"Cache: {stats['full_images']}F / {stats['thumbnails']}T / {stats['metrics']}M"
        )
    
    def _update_filesize(self):
        """Update file size display"""
        if not self.image_pairs or self.current_index >= len(self.image_pairs):
            self.filesize_label.setText("Size: -- / --")
            return
        
        left_path, right_path = self.image_pairs[self.current_index]
        left_size = format_file_size(left_path)
        right_size = format_file_size(right_path)
        self.filesize_label.setText(f"Size: {left_size} / {right_size}")

    def _display_cached_or_placeholder(self):
        """Display best available cached image or placeholder"""
        index = self.current_index
        
        if not self.image_pairs or index >= len(self.image_pairs):
            logger.warning("No image pairs or invalid index")
            return
        
        left_path, right_path = self.image_pairs[index]
        
        # Handle missing files
        if not os.path.exists(left_path) or not os.path.exists(right_path):
            error_msg = "File not found"
            logger.error(f"{error_msg}: {left_path} or {right_path}")
            QMessageBox.warning(self, "Error", error_msg)
            self._show_error_placeholder("File Not Found")
            return
        
        left_view, right_view = self.image_views[0]
        
        # Update path labels and file sizes
        self.left_path_label.setText(os.path.basename(left_path))
        self.right_path_label.setText(os.path.basename(right_path))
        self._update_filesize()
        
        # Check cache for images
        if self.cache.has_full_image(index):
            left_pixmap = self.cache.get_image(index, 'left', prefer_full=True)
            right_pixmap = self.cache.get_image(index, 'right', prefer_full=True)
            
            if left_pixmap and right_pixmap:
                self._set_view_images(left_view, right_view, left_pixmap, right_pixmap)
                self.resolution_status.setText("Cached (Full)")
                self.resolution_status.setStyleSheet("color: #00FF00")
        elif self.cache.has_thumbnail(index):
            left_pixmap = self.cache.get_image(index, 'left', prefer_full=False)
            right_pixmap = self.cache.get_image(index, 'right', prefer_full=False)
            
            if left_pixmap and right_pixmap:
                self._set_view_images(left_view, right_view, left_pixmap, right_pixmap)
                self.resolution_status.setText("Thumbnail")
                self.resolution_status.setStyleSheet("color: #FFA500")
        else:
            self.resolution_combo.clear()
            self._show_placeholder(left_view, right_view)
            self.resolution_status.setText("Loading...")
            self.resolution_status.setStyleSheet("color: #FF5555")
            self._load_thumbnail(index)
        
        # Display metrics
        if self.cache.has_metrics(index):
            self.update_metrics_display(index, self.cache.get_metrics(index))
        else:
            self.metrics_label.setText("Computing metrics...")
            self._compute_metrics(index)


    def _show_placeholder(self, left_view, right_view):
        """Show loading placeholder with animated GIF or fallback color"""
        gif_path = resource_path("assets/loading.gif")

        movie = QMovie(str(gif_path))
        valid = movie.isValid()  # check if GIF is loadable

        for iv in [left_view.image_view, right_view.image_view]:
            iv.scene().clear()

            if valid:
                # Animated loading GIF
                label = QLabel()
                label.setMovie(movie)
                item = iv.scene().addWidget(label)
                iv.pixmap_item = item
                movie.start()
            else:
                # Fallback: solid black (#000000)
                pixmap = QPixmap(800, 600)
                pixmap.fill(QColor("#000000"))
                item = iv.scene().addPixmap(pixmap)
                iv.pixmap_item = item

            iv.fitInView(iv.pixmap_item, Qt.KeepAspectRatio)


    def _show_error_placeholder(self, error_text):
        """Show error placeholder with animated GIF or fallback color"""
        gif_path = resource_path("assets/error.webp")

        movie = QMovie(str(gif_path))
        valid = movie.isValid()

        left_view, right_view = self.image_views[0]

        for iv in [left_view.image_view, right_view.image_view]:
            iv.scene().clear()

            if valid:
                label = QLabel()
                label.setMovie(movie)
                item = iv.scene().addWidget(label)
                iv.pixmap_item = item
                movie.start()
            else:
                # Fallback: solid red
                pixmap = QPixmap(800, 600)
                pixmap.fill(QColor("#FF0000"))
                item = iv.scene().addPixmap(pixmap)
                iv.pixmap_item = item

            iv.fitInView(iv.pixmap_item, Qt.KeepAspectRatio)

        self.metrics_label.setText(
            f"<span style='color:#FF5555'>ERROR: {error_text}</span>"
        )

    def _set_view_images(self, left_view, right_view, left_pixmap, right_pixmap):
        """Set images in views"""
        try:
            self.resolution_combo.blockSignals(True)
            self.resolution_combo.clear()
            
            resolutions = []
            
            for iv, pixmap in [(left_view.image_view, left_pixmap), (right_view.image_view, right_pixmap)]:
                if pixmap:
                    iv.scene().clear()
                    item = iv.scene().addPixmap(pixmap)
                    iv.pixmap_item = item
                    iv.original_pixmap = pixmap
                    iv.fitInView(item, Qt.KeepAspectRatio)
                    resolutions.append((pixmap.width(), pixmap.height()))
            
            # Add unique resolutions
            unique_resolutions = list(set(resolutions))
            for width, height in unique_resolutions:
                self.add_resolution(width, height)
            
            # Auto-select highest resolution
            if unique_resolutions:
                highest_res = max(unique_resolutions, key=lambda r: r[0] * r[1])
                self.resolution_combo.setCurrentText(f"{highest_res[0]}x{highest_res[1]}")
            
            self.resolution_combo.blockSignals(False)
            
        except Exception as e:
            logger.error(f"Error setting view images: {e}")
            self._show_error_placeholder("Display Error")

    # Worker management methods
    def _load_thumbnail(self, index):
        """Load thumbnail quality images"""
        if index >= len(self.image_pairs):
            return
        
        left_path, right_path = self.image_pairs[index]
        worker = ImageLoadWorker(index, left_path, right_path, quality='thumbnail')
        worker.signals.image_loaded.connect(self._on_image_loaded)
        worker.signals.error.connect(self._on_worker_error)
        self.active_workers.append(worker)
        self.thread_pool.start(worker)

    def _load_full_quality(self):
        """Load full quality images after navigation settles"""
        index = self.current_index
        
        if self.cache.has_full_image(index) or index >= len(self.image_pairs):
            return
        
        left_path, right_path = self.image_pairs[index]
        logger.info(f"Loading full quality for index {index}")
        
        worker = ImageLoadWorker(index, left_path, right_path, quality='full')
        worker.signals.image_loaded.connect(self._on_image_loaded)
        worker.signals.error.connect(self._on_worker_error)
        self.active_workers.append(worker)
        self.thread_pool.start(worker)

    def _compute_metrics(self, index):
        """Compute metrics for image pair"""
        if index >= len(self.image_pairs):
            return
        
        left_path, right_path = self.image_pairs[index]
        worker = MetricsWorker(index, left_path, right_path)
        worker.signals.metrics_ready.connect(self._on_metrics_ready)
        worker.signals.error.connect(self._on_worker_error)
        self.active_workers.append(worker)
        self.thread_pool.start(worker)

    def _on_image_loaded(self, index, side, pixmap, quality):
        """Handle image loaded signal"""
        self.cache.set_image(index, side, pixmap, quality)
        self._update_cache_status()
        
        if index == self.current_index:
            left_view, right_view = self.image_views[0]
            
            if side == 'left':
                left_pixmap = pixmap
                right_pixmap = self.cache.get_image(index, 'right')
            else:
                left_pixmap = self.cache.get_image(index, 'left')
                right_pixmap = pixmap
            
            if left_pixmap and right_pixmap:
                self._set_view_images(left_view, right_view, left_pixmap, right_pixmap)
                status = "Full Quality" if quality == 'full' else "Thumbnail"
                color = "lime" if quality == 'full' else "#FFA500"
                self.resolution_status.setText(status)
                self.resolution_status.setStyleSheet(f"color: {color}")

    def _on_metrics_ready(self, index, metrics):
        """Handle metrics ready signal"""
        self.cache.set_metrics(index, metrics)
        self._update_cache_status()
        
        if index == self.current_index:
            self.update_metrics_display(index, metrics)

    def _on_worker_error(self, error_msg):
        """Handle worker errors"""
        logger.error(f"Worker error: {error_msg}")
        if self.current_index is not None:
            self.resolution_status.setText("Error")
            self.resolution_status.setStyleSheet("color: #FF5555")

    def _start_preloading(self):
        """Start preloading adjacent images"""
        for i in range(1, MAX_PRELOAD_FORWARD + 1):
            next_idx = self.current_index + i
            if next_idx < len(self.image_pairs):
                if not self.cache.has_thumbnail(next_idx):
                    self._load_thumbnail(next_idx)
                if not self.cache.has_full_image(next_idx):
                    self._load_full_quality_index(next_idx)
                if not self.cache.has_metrics(next_idx):
                    self._compute_metrics(next_idx)
        
        for i in range(1, MAX_PRELOAD_BACKWARD + 1):
            prev_idx = self.current_index - i
            if prev_idx >= 0:
                if not self.cache.has_thumbnail(prev_idx):
                    self._load_thumbnail(prev_idx)
                if not self.cache.has_full_image(prev_idx):
                    self._load_full_quality_index(prev_idx)
                if not self.cache.has_metrics(prev_idx):
                    self._compute_metrics(prev_idx)

    def _load_full_quality_index(self, index):
        """Load full quality for specific index"""
        if index >= len(self.image_pairs) or self.cache.has_full_image(index):
            return
        
        left_path, right_path = self.image_pairs[index]
        worker = ImageLoadWorker(index, left_path, right_path, quality='full')
        worker.signals.image_loaded.connect(self._on_image_loaded)
        worker.signals.error.connect(self._on_worker_error)
        self.active_workers.append(worker)
        self.thread_pool.start(worker)

    def load_folders(self, folder1, folder2):
        """Load image pairs from two folders"""
        if not os.path.exists(folder1) or not os.path.exists(folder2):
            error_msg = "One or both folders don't exist"
            logger.error(f"{error_msg}: {folder1}, {folder2}")
            QMessageBox.warning(self, "Error", error_msg)
            return

        try:
            files1 = get_sorted_image_files(folder1)
            files2 = get_sorted_image_files(folder2)
            
            if not files1 or not files2:
                error_msg = "No valid image files found in one or both folders"
                logger.error(error_msg)
                QMessageBox.warning(self, "Error", error_msg)
                return
            
            if len(files1) != len(files2):
                warning_msg = (f"Folder mismatch: {len(files1)} vs {len(files2)} images.\n"
                              f"Only {min(len(files1), len(files2))} pairs will be shown.")
                logger.warning(warning_msg)
                QMessageBox.warning(self, "Warning", warning_msg)
            
            self.image_pairs = list(zip(files1, files2))
            self.current_index = 0
            self.cache.clear()
            self._update_cache_status()
            self._navigate_to_current()
            logger.info(f"Loaded {len(self.image_pairs)} image pairs from folders")
        except Exception as e:
            error_msg = f"Failed to load folders: {e}"
            logger.error(error_msg)
            QMessageBox.warning(self, "Error", error_msg)

    def update_metrics_display(self, index, metrics):
        """Update metrics display with computed values"""
        if index != self.current_index:
            return
        
        # Colorize metrics
        psnr_c1, psnr_c2 = colorize_metrics(metrics['psnr1'], metrics['psnr2'])
        sharp_c1, sharp_c2 = colorize_metrics(metrics['sharpness1'], metrics['sharpness2'])
        noise_c1, noise_c2 = colorize_metrics(metrics['noise1'], metrics['noise2'], higher_is_better=False)

        # Format segments
        left_segment = (
            f'<span style="color:{psnr_c1}">PSNR: {metrics["psnr1"]:.2f}</span> | '
            f'<span style="color:{sharp_c1}">Sharp: {metrics["sharpness1"]:.2f}</span> | '
            f'<span style="color:{noise_c1}">Noise: {metrics["noise1"]:.2f}</span>'
        )

        center_segment = f'<span style="color:{COLOR_SSIM}">SSIM: {metrics["ssim"]:.4f}</span>'

        right_segment = (
            f'<span style="color:{psnr_c2}">PSNR: {metrics["psnr2"]:.2f}</span> | '
            f'<span style="color:{sharp_c2}">Sharp: {metrics["sharpness2"]:.2f}</span> | '
            f'<span style="color:{noise_c2}">Noise: {metrics["noise2"]:.2f}</span>'
        )

        html = f"""
        <div style="width:100%">
            <div style="float:left">{left_segment}</div>
            <div style="text-align:center">{center_segment}</div>
            <div style="float:right">{right_segment}</div>
        </div>
        """
        
        self.metrics_label.setText(html)
    
    def closeEvent(self, event):
        """Handle window close event - cleanup threads"""
        logger.info("Closing application, cleaning up...")
        
        self.navigation_timer.stop()
        self.preload_timer.stop()
        
        for worker in self.active_workers:
            if hasattr(worker, 'cancel'):
                worker.cancel()
        
        self.thread_pool.waitForDone(2000)
        logger.info("Application closed successfully")
        event.accept()
    
    def resizeEvent(self, event):
        """Handle window resize - refit images"""
        super().resizeEvent(event)
        
        if self.image_views and self.image_pairs:
            left_view, right_view = self.image_views[0]
            for view in [left_view.image_view, right_view.image_view]:
                if view.pixmap_item:
                    view.fitInView(view.pixmap_item, Qt.KeepAspectRatio)