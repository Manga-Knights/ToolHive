"""
Worker classes for threaded image loading and metrics computation
"""
import os
import logging
from PyQt5.QtCore import pyqtSignal, QRunnable, pyqtSlot, QObject, Qt
from PyQt5.QtGui import QPixmap, QImage
from constants import THUMBNAIL_SIZE
from image_metrics import calculate_metrics

logger = logging.getLogger(__name__)


class WorkerSignals(QObject):
    """Signals for QRunnable workers"""
    image_loaded = pyqtSignal(int, str, object, str)
    metrics_ready = pyqtSignal(int, dict)
    error = pyqtSignal(str)


class ImageLoadWorker(QRunnable):
    """Worker for loading images in thread pool"""
    
    def __init__(self, index, left_path, right_path, quality='full'):
        super().__init__()
        self.index = index
        self.left_path = left_path
        self.right_path = right_path
        self.quality = quality
        self.signals = WorkerSignals()
        self.is_cancelled = False
    
    def cancel(self):
        self.is_cancelled = True
    
    @pyqtSlot()
    def run(self):
        try:
            for side, path in [('left', self.left_path), ('right', self.right_path)]:
                if self.is_cancelled:
                    return
                
                pixmap = self._load_image(path)
                if pixmap and not self.is_cancelled:
                    self.signals.image_loaded.emit(self.index, side, pixmap, self.quality)
        except Exception as e:
            self.signals.error.emit(f"Error loading image: {e}")
    
    def _load_image(self, path):
        """Load image based on quality setting"""
        try:
            if not os.path.exists(path):
                logger.error(f"Image file not found: {path}")
                return None
                
            image = QImage(path)
            if image.isNull():
                logger.error(f"Failed to load image (corrupted?): {path}")
                return None
            
            if self.quality == 'thumbnail':
                image = image.scaled(
                    THUMBNAIL_SIZE, THUMBNAIL_SIZE,
                    Qt.KeepAspectRatio,
                    Qt.FastTransformation
                )
            
            logger.debug(f"Successfully loaded {self.quality} image: {path}")
            return QPixmap.fromImage(image)
        except Exception as e:
            logger.error(f"Error loading {path}: {e}")
            return None


class MetricsWorker(QRunnable):
    """Worker for computing metrics in thread pool"""
    
    def __init__(self, index, left_path, right_path):
        super().__init__()
        self.index = index
        self.left_path = left_path
        self.right_path = right_path
        self.signals = WorkerSignals()
        self.is_cancelled = False
    
    def cancel(self):
        self.is_cancelled = True
    
    @pyqtSlot()
    def run(self):
        try:
            if not self.is_cancelled:
                metrics = calculate_metrics(self.left_path, self.right_path)
                if not self.is_cancelled:
                    self.signals.metrics_ready.emit(self.index, metrics)
        except Exception as e:
            self.signals.error.emit(f"Error calculating metrics: {e}")