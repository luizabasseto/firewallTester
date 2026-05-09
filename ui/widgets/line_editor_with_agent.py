from PyQt5.QtWidgets import (
    QApplication, QPlainTextEdit, QWidget, QTextEdit,
    QMenu, QAction
)
from PyQt5.QtGui import QPainter, QColor, QTextFormat
from PyQt5.QtCore import Qt, QRect
import requests
import os
from dotenv import load_dotenv
import markdown
import re
import json
import uuid

load_dotenv()
API_URL = os.getenv("AGENT_API_URL")

class Conversation:
    def __init__(self):
        self.session_id = str(uuid.uuid4())
        
    def _extract_json_from_text(self, text: str) -> dict:
        match = re.search(r'\{[\s\S]*\}', text)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        return {"stepbystep": text, "suggestions": ""}

    def ask_to_agent(self, payload: dict):
        payload["sessionId"] = self.session_id
        try:
            response = requests.post(API_URL, json=payload, timeout=500)

            if response.status_code == 200:
                data = response.json()

                if isinstance(data, list):
                    data = data[0]

                output = data.get('output', {})
                
                if isinstance(output, str):
                    try:
                        output = json.loads(output)
                    except json.JSONDecodeError:
                        output = self._extract_json_from_text(output)

                if isinstance(output, dict):
                    return output

                return {"stepbystep": str(output), "suggestions": ""}

            else:
                return {"stepbystep": f"Error {response.status_code}: {response.text}", "suggestions": ""}

        except Exception as e:
            return {"stepbystep": f"Request Error: {str(e)}", "suggestions": ""}

class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.code_editor = editor
        self.conversation = Conversation()
        self.output_widget = None
    
    def setOutputWidget(self, widget):
        self.output_widget = widget

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

        action1 = QAction("Ask about this line in the context of all rules", self)
        action2 = QAction("What this line do?", self)

        action1.triggered.connect(lambda: self.askAboutLine(line))
        action2.triggered.connect(lambda: self.askAboutImprove(line))

        menu.addAction(action1)
        menu.addAction(action2)

        menu.exec_(position)

    def getLineText(self, line):
        block = self.code_editor.document().findBlockByNumber(line - 1)
        return block.text()

    def getAllText(self):
        return self.code_editor.document().toPlainText()   

    def askAboutLine(self, line):
        text = self.getLineText(line)
        text_all = self.getAllText()
        
        payload = {
            "type": "conflict_analysis",
            "code": text,
            "existing_rules": text_all.split('\n'),
        }

        answer = self.conversation.ask_to_agent(payload)
        html = self.buildHtml(answer, text)
        self.output_widget.setHtml(html)

    def askAboutImprove(self, line):
        text = self.getLineText(line)
        
        payload = {
            "type": "explanation",
            "code": text,
        }

        answer = self.conversation.ask_to_agent(payload)
        html = self.buildHtml(answer, text)
        self.output_widget.setHtml(html)
        
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
    
    def buildHtml(self, data, line_text: str) -> str:
        if isinstance(data, str):
            data = {"stepbystep": data, "suggestions": ""}
        elif not isinstance(data, dict):
            data = {"stepbystep": str(data), "suggestions": ""}

        stepbystep = data.get("stepbystep", "Sem resposta")
        suggestions = data.get("suggestions", "")

        steps_html = markdown.markdown(
            stepbystep, output_format='html5', extensions=['extra']
        )
        suggestions_html = markdown.markdown(
            suggestions, output_format='html5', extensions=['extra']
        ) if suggestions else ""

        suggestion_block = f"""
            <div style="margin-top:16px; padding:12px;">
                <b>Sugestões</b>
                {suggestions_html}
            </div>
        """ if suggestions_html else ""

        return f"""
        <html><body style="font-family:sans-serif; font-size:13px; color:#222; padding:8px;">
            <div style="background:#e8e8e8; padding:6px 10px;
                        border-radius:4px; font-family:monospace;
                        margin-bottom:12px; color:#444;">
                <b>Linha analisada:</b> <code>{line_text}</code>
            </div>
            <div>
                <b style="color:#333;">Explicação</b>
                {steps_html}
            </div>
            {suggestion_block}
        </body></html>
        """
    
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
            selection.format.setBackground(QColor(Qt.cyan).lighter(160))
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)

            block = self.document().findBlockByNumber(self.highlighted_line - 1)

            cursor = self.textCursor()
            cursor.setPosition(block.position())
            selection.cursor = cursor
            selection.cursor.clearSelection()

            extra_selections.append(selection)

        self.setExtraSelections(extra_selections)

if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)

    editor = CodeEditor()
    editor.setWindowTitle("Editor com IA por linha")
    editor.resize(700, 500)

    editor.show()
    sys.exit(app.exec_())