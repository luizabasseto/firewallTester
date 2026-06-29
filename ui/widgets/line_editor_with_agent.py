from PyQt5.QtWidgets import (
    QWidget, QPlainTextEdit, QTextEdit, QMenu, QAction,
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextBrowser, QSizePolicy
)
from PyQt5.QtGui import QPainter, QColor, QTextFormat, QFont
from PyQt5.QtCore import Qt, QRect, QThread, pyqtSignal

from PyQt5.QtGui import QPainter, QColor, QTextFormat
from PyQt5.QtCore import Qt, QRect
import requests
#import os
#from dotenv import load_dotenv
import markdown
import re
import json
import uuid


API_URL = 'http://192.168.2.20:5678/webhook/firewall-chat'

FALLBACK = {"stepbystep": "No answer from agent", "suggestions": ""}

class Conversation:
    def __init__(self, max_retries: int = 2, timeout: int = 60):
        self.max_retries = max_retries
        self.timeout = timeout

    def _parse(self, raw) -> dict:
        if isinstance(raw, dict):
            if "stepbystep" in raw:
                return raw
            raw = json.dumps(raw)

        if not isinstance(raw, str) or not raw.strip():
            return FALLBACK

        raw = raw.strip()

        try:
            data = json.loads(raw)
            if isinstance(data, dict) and "stepbystep" in data:
                return data
        except json.JSONDecodeError:
            pass

        match = re.search(r'\{[\s\S]*?"stepbystep"[\s\S]*?\}', raw)
        if match:
            try:
                data = json.loads(match.group())
                if isinstance(data, dict) and "stepbystep" in data:
                    return data
            except json.JSONDecodeError:
                pass

        return {"stepbystep": raw, "suggestions": ""}

    def _post(self, payload: dict) -> dict:
        payload["sessionId"] = str(uuid.uuid4())
        resp = requests.post(API_URL, json=payload, timeout=self.timeout)
        resp.raise_for_status()

        data = resp.json()
        if isinstance(data, list):
            data = data[0] if data else {}

        return self._parse(data.get("output", ""))

    def ask_to_agent(self, payload: dict) -> dict:
        last_error = None

        for attempt in range(1, self.max_retries + 1):
            try:
                return self._post(payload)
            except requests.Timeout:
                last_error = f"Timeout (tentativa {attempt}/{self.max_retries})."
            except requests.HTTPError as e:
                last_error = f"Erro HTTP {e.response.status_code}: {e.response.text[:300]}"
                break
            except Exception as e:
                last_error = f"Erro: {str(e)}"
                break

        return {"stepbystep": last_error or "Erro desconhecido.", "suggestions": ""}

class AgentWorker(QThread):
    finished = pyqtSignal(dict, str)

    def __init__(self, payload, line_text):
        super().__init__()
        self.payload = payload
        self.line_text = line_text
        self.conversation = Conversation()

    def run(self):
        result = self.conversation.ask_to_agent(self.payload)
        self.finished.emit(result, self.line_text)

class AgentResultDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Agent Analysis")
        self.setMinimumSize(520, 420)
        self.setSizeGripEnabled(True)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        self.line_label = QLabel()
        self.line_label.setStyleSheet(
            "background:#e8e8e8; padding:6px 10px; border-radius:4px;"
            "font-family:monospace; color:#444;"
        )
        self.line_label.setWordWrap(True)
        layout.addWidget(self.line_label)

        self.browser = QTextBrowser()
        self.browser.setOpenExternalLinks(False)
        self.browser.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.browser)

        # botão fechar
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.accept)
        btn_layout.addWidget(btn_close)
        layout.addLayout(btn_layout)

    def show_loading(self, line_text: str):
        self.line_label.setText(f"<b>Linha analisada:</b> <code>{line_text}</code>")
        self.browser.setHtml(
            "<p style='color:#888; font-style:italic;'>Consultando agente...</p>"
        )

    def show_result(self, data: dict, line_text: str):
        self.line_label.setText(f"<b>Linha analisada:</b> <code>{line_text}</code>")
        self.browser.setHtml(_build_html(data))


def _build_html(data: dict) -> str:
    if isinstance(data, str):
        data = {"stepbystep": data, "suggestions": ""}
    elif not isinstance(data, dict):
        data = {"stepbystep": str(data), "suggestions": ""}

    stepbystep = data.get("stepbystep", "Sem resposta")
    suggestions = data.get("suggestions", "")

    steps_html = markdown.markdown(
        stepbystep, output_format="html5", extensions=["extra"]
    )
    suggestions_html = (
        markdown.markdown(suggestions, output_format="html5", extensions=["extra"])
        if suggestions else ""
    )
    suggestion_block = (
        f"<div style='margin-top:16px; padding:12px; background:#f5f5f5;"
        f"border-radius:4px;'><b>Sugestões</b>{suggestions_html}</div>"
        if suggestions_html else ""
    )

    return f"""
    <html><body style="font-family:sans-serif; font-size:13px; color:#222; padding:8px;">
        <style>
            h2, h3 {{ margin-top: 18px; margin-bottom: 6px; }}
            p {{ margin-bottom: 8px; }}
            ul, ol {{ margin-bottom: 10px; }}
            hr {{ margin: 14px 0; border: none; border-top: 1px solid #ddd; }}
        </style>
        <b style="color:#333;">Explicação</b>
        {steps_html}
        {suggestion_block}
    </body></html>
    """


class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.code_editor = editor
        self._worker = None

    def setOutputWidget(self, widget):
        pass

    def sizeHint(self):
        return self.code_editor.lineNumberAreaWidth(), 0

    def paintEvent(self, event):
        self.code_editor.lineNumberAreaPaintEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            self.handleClick(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.handleClick(event)

    def handleClick(self, event):
        line = self.getLineFromY(event.pos().y())
        if line != -1:
            self.code_editor.highlightLine(line)
            self.showContextMenu(event.globalPos(), line)

    def showContextMenu(self, position, line):
        menu = QMenu()
        action1 = QAction("Analise in the context of all rules", self)
        action2 = QAction("What this line does?", self)
        action1.triggered.connect(lambda: self._open_modal(line, "conflict_analysis"))
        action2.triggered.connect(lambda: self._open_modal(line, "explanation"))
        menu.addAction(action1)
        menu.addAction(action2)
        menu.exec_(position)

    def _open_modal(self, line: int, analysis_type: str):
        line_text = self.getLineText(line)
        if not line_text.strip():
            return

        payload = {"type": analysis_type, "code": line_text}
        if analysis_type == "conflict_analysis":
            payload["existing_rules"] = self.getAllText().split("\n")

        dialog = AgentResultDialog(self.code_editor.window())
        dialog.show_loading(line_text)
        dialog.show()

        self._worker = AgentWorker(payload, line_text)
        self._worker.finished.connect(
            lambda data, lt: dialog.show_result(data, lt)
        )
        self._worker.start()

        dialog.exec_()

    def getLineText(self, line):
        return self.code_editor.document().findBlockByNumber(line - 1).text()

    def getAllText(self):
        return self.code_editor.document().toPlainText()

    def getLineFromY(self, y):
        editor = self.code_editor
        block = editor.firstVisibleBlock()
        block_number = block.blockNumber()
        top = editor.blockBoundingGeometry(block).translated(editor.contentOffset()).top()
        bottom = top + editor.blockBoundingRect(block).height()

        while block.isValid():
            if block.isVisible() and top <= y <= bottom:
                return block_number + 1
            block = block.next()
            top = bottom
            bottom = top + editor.blockBoundingRect(block).height()
            block_number += 1
        return -1
class CodeEditor(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self.line_number_area = LineNumberArea(self)
        self.highlighted_line = None

        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)

        self.updateLineNumberAreaWidth(0)

    def lineNumberAreaWidth(self):
        digits = len(str(max(1, self.blockCount())))
        return 3 + self.fontMetrics().width('9') * digits

    def updateLineNumberAreaWidth(self, _):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    def updateLineNumberArea(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(
            QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height())
        )

    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor(Qt.lightGray))

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()

        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                painter.setPen(Qt.black)
                painter.drawText(
                    0,
                    int(top),
                    int(self.line_number_area.width()),
                    int(self.fontMetrics().height()),
                    Qt.AlignRight,
                    str(block_number + 1)
                )

            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1

    def highlightLine(self, line_number):
        self.highlighted_line = line_number
        self.updateHighlight()

    def updateHighlight(self):
        extra_selections = []

        if self.highlighted_line is not None:
            selection = QTextEdit.ExtraSelection()
            selection.format.setBackground(QColor("#5ea59bac"))
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)

            block = self.document().findBlockByNumber(self.highlighted_line - 1)

            cursor = self.textCursor()
            cursor.setPosition(block.position())
            selection.cursor = cursor
            selection.cursor.clearSelection()

            extra_selections.append(selection)

        self.setExtraSelections(extra_selections)