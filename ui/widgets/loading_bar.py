from PyQt5.QtWidgets import QDialog, QVBoxLayout, QProgressBar, QLabel
from PyQt5.QtCore import QTimer

class LoadingBar(QDialog):
    def __init__(self, parent = None, title='Wait', message="", time=2000):
        super().__init__()
        self.title = title
        self.message = message

        self.setWindowTitle(self.title)
        self.setFixedSize(300, 100)

        layout = QVBoxLayout()

        self.label = QLabel(self.message)
        self.progress = QProgressBar()

        # indeterminate mode (infinite animation)
        self.progress.setRange(0, 0)

        layout.addWidget(self.label)
        layout.addWidget(self.progress)
        self.setLayout(layout)

        QTimer.singleShot(time, self.close)