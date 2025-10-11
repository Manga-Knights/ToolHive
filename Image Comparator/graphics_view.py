from PyQt5.QtWidgets import QWidget, QVBoxLayout
from image_view import ImageView

class GraphicsView(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.image_view = ImageView(self)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.image_view)
