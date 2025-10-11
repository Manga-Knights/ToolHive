from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QMessageBox
from PyQt5.QtGui import QPixmap, QImage, QWheelEvent, QPainter, QTransform
from PyQt5.QtCore import Qt, pyqtSignal
from PIL import Image
import os

class ImageView(QGraphicsView):
    transformChanged = pyqtSignal(QTransform)
    multipleUrls = pyqtSignal(list)
    photoAdded = pyqtSignal(int, int)

    def __init__(self, parent=None):
        super(ImageView, self).__init__(parent)
        self.scene_obj = QGraphicsScene(self)
        self.setScene(self.scene_obj)

        # Render hints
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)

        # Interaction
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.ScrollHandDrag)

        self.zoom = 0
        self.original_pixmap = None
        self.pixmap_item = None
        self.url = None

        # Optional zoom limits
        self._max_zoom = 20
        self._min_zoom = -10

    def set_image(self, path):
        self.scene_obj.clear()
        self.pixmap_item = None
        if not os.path.exists(path):
            self.pixmap_item = self.scene_obj.addText("Image not found.")
            return

        try:
            image = Image.open(path).convert("RGBA")
            data = image.tobytes("raw", "RGBA")
            qimage = QImage(data, image.width, image.height, QImage.Format_RGBA8888)
            pixmap = QPixmap.fromImage(qimage)
            self.original_pixmap = pixmap
            self.pixmap_item = self.scene_obj.addPixmap(pixmap)
            self.zoom = 0
            self.setTransform(QTransform())
            self.photoAdded.emit(pixmap.width(), pixmap.height())
            self.url = path

            # Center and fit
            self.fit_pixmap()
        except Exception as e:
            self.pixmap_item = self.scene_obj.addText(f"Error: {e}")

    def wheelEvent(self, event: QWheelEvent):
        if not self.pixmap_item:
            return

        zoom_in = event.angleDelta().y() > 0
        if zoom_in and self.zoom >= self._max_zoom:
            return
        if not zoom_in and self.zoom <= self._min_zoom:
            return

        zoom_factor = 1.25 if zoom_in else 0.8
        self.zoom += 1 if zoom_in else -1
        self.scale(zoom_factor, zoom_factor)
        self.transformChanged.emit(self.transform())

    def set_transform(self, transform: QTransform):
        h_scroll, v_scroll = self.horizontalScrollBar(), self.verticalScrollBar()
        h_prev, v_prev = h_scroll.blockSignals(True), v_scroll.blockSignals(True)
        self.setTransform(transform)
        h_scroll.blockSignals(h_prev)
        v_scroll.blockSignals(v_prev)

    def set_antialiasing(self, enabled: bool):
        self.setRenderHint(QPainter.Antialiasing, enabled)
        self.setRenderHint(QPainter.SmoothPixmapTransform, enabled)
        if self.pixmap_item and self.original_pixmap:
            self.reload_pixmap()

    def reload_pixmap(self):
        if self.pixmap_item and self.original_pixmap:
            # Save current transform
            current_transform = self.transform()
            self.pixmap_item.setPixmap(self.original_pixmap)
            mode = Qt.SmoothTransformation if self.renderHints() & QPainter.SmoothPixmapTransform else Qt.FastTransformation
            self.pixmap_item.setTransformationMode(mode)
            # Restore transform
            self.setTransform(current_transform)


    def fit_pixmap(self):
        """Fit and center the pixmap in the view."""
        if not self.pixmap_item:
            return
        self.setSceneRect(self.pixmap_item.boundingRect())
        self.fitInView(self.pixmap_item, Qt.KeepAspectRatio)
        self.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
