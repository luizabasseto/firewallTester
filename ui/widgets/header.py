"""Defines a reusable header widget for the application."""

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt

class Header(QWidget):
    """
    A simple widget to display a logo and a title."""

    def __init__(self, logo_path, title, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        logo_label = QLabel()
        pixmap = QPixmap(logo_path)
        logo_label.setPixmap(pixmap.scaledToHeight(60, Qt.SmoothTransformation))
        layout.addWidget(logo_label)

        layout.addSpacing(15)

        title_label = QLabel(title)
        title_font = QFont("Arial", 16, QFont.Bold)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        layout.addStretch(1)