from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QPushButton,
    QMessageBox, QApplication
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCursor


class AgentIA(QDialog):
    """
    Dialog window for interacting with AgentIA helper.
    """
    def __init__(self, container_manager, config, parent=None):
        super().__init__(parent)

        self.container_manager = container_manager
        self.config = config

        self.setWindowTitle("AgentIA Helper")
        self.setMinimumSize(500, 500)
        self.setLayout(QVBoxLayout())

        # === Message Area ===
        self.msg_area = QTextEdit()
        self.msg_area.setReadOnly(True)
        self.layout().addWidget(self.msg_area)

        # === Input Area ===
        input_layout = QHBoxLayout()

        self.entry = QLineEdit()
        self.entry.setPlaceholderText("Write your question...")
        self.entry.returnPressed.connect(self._send_message)

        btn_send = QPushButton("Send")
        btn_send.clicked.connect(self._send_message)

        input_layout.addWidget(self.entry)
        input_layout.addWidget(btn_send)

        self.layout().addLayout(input_layout)

        # === Bottom Buttons ===
        buttons_layout = QHBoxLayout()

        btn_clear = QPushButton("Clear chat")
        btn_clear.clicked.connect(self._clear_chat)

        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.reject)

        buttons_layout.addStretch()
        buttons_layout.addWidget(btn_clear)
        buttons_layout.addWidget(btn_close)

        self.layout().addLayout(buttons_layout)

    # ==============================
    # Internal Methods
    # ==============================

    def _format_message(self, message, sent=False):
        if sent:
            return f"""
            <div style='text-align: right; margin: 5px;'>
                <span style='background-color:#3a86ff; padding:8px; border-radius:10px; color:white;'>
                    {message}
                </span>
            </div>
            """
        else:
            return f"""
            <div style='text-align: left; margin: 5px;'>
                <span style='background-color:#444; padding:8px; border-radius:10px; color:white;'>
                    {message}
                </span>
            </div>
            """

    def _send_message(self):
        msg = self.entry.text().strip()
        if not msg:
            return

        # Exemplo temporário:
        response = f"Agent response to: {msg}"

        self.msg_area.insertHtml(self._format_message(msg, sent=True))
        self.msg_area.insertHtml(self._format_message(response, sent=False))
        self.msg_area.moveCursor(QTextCursor.End)

        self.entry.clear()

    def _clear_chat(self):
        self.msg_area.clear()