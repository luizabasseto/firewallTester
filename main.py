"""
Main entry point for the Firewall Tester application.

This script initializes the PyQt5 application, creates the main window,
and starts the event loop.
"""
"""To run the application, execute the command `pip3 install -r requirements.txt` on the terminal before execute the software"""

import sys
from PyQt5.QtWidgets import QApplication
from ui.main_ui import MainWindow
import docker

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec_())