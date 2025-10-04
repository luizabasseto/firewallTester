"""
Main entry point for the Firewall Tester application.

This script initializes the PyQt5 application, creates the main window,
and starts the event loop.
"""

import sys
from PyQt5.QtWidgets import QApplication
from ui.main_ui import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())