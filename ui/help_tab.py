"""Defines the 'Help' tab for the Firewall Tester application."""

import pathlib
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextBrowser
from PyQt5.QtCore import Qt


class HelpTab(QWidget):
    """
    A QWidget that displays help content loaded from an HTML file.
    (R0903: This is a simple display widget with no public methods
    needed beyond its initialization, which is acceptable for this use case.)
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self._create_ui()

    def _create_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignTop)

        help_text_browser = QTextBrowser()
        help_text_browser.setOpenExternalLinks(True)

        try:
            script_dir = pathlib.Path(__file__).parent.resolve()
            help_file_path = script_dir / "widgets/help_frame.html"

            with open(help_file_path, 'r', encoding="utf-8") as f:
                help_content = f.read()
            help_text_browser.setHtml(help_content)

        except FileNotFoundError:
            error_html = "<h1>Error</h1><p>Help file 'help_frame.html' not found.</p>"
            help_text_browser.setHtml(error_html)

        main_layout.addWidget(help_text_browser)
