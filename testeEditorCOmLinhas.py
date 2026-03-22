from PyQt5.QtWidgets import QApplication, QPlainTextEdit, QWidget, QVBoxLayout, QTextEdit
from PyQt5.QtGui import QPainter, QColor, QTextFormat
from PyQt5.QtCore import Qt, QRect

class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.code_editor = editor

    def sizeHint(self):
        return self.code_editor.lineNumberAreaWidth(), 0

    def paintEvent(self, event):
        self.code_editor.lineNumberAreaPaintEvent(event)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            line = self.getLineFromY(event.pos().y())
            print(f"Clique direito na linha {line}")
    
    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            line = self.getLineFromY(event.pos().y())
            if line != -1:
                self.code_editor.highlightLine(line)
    
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
        self.cursorPositionChanged.connect(self.highlightCurrentLine)
        self.updateLineNumberAreaWidth(0)

    def lineNumberAreaWidth(self):
        digits = len(str(max(1, self.blockCount())))
        space = 3 + self.fontMetrics().width('9') * digits
        return space

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
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height()))

    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor(Qt.lightGray))
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(Qt.black)
                painter.drawText(
                                0,
                                int(top),
                                int(self.line_number_area.width()),
                                int(self.fontMetrics().height()),
                                Qt.AlignRight,
                                number
                            )
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1

    def highlightCurrentLine(self):
        extra_selections = []
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            selection.format.setBackground(QColor(Qt.yellow).lighter(160))
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)
        self.setExtraSelections(extra_selections)
        
    def highlightLine(self, line_number):
        self.highlighted_line = line_number
        self.updateHighlight()
    
    def updateHighlight(self):
        extra_selections = []

        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            selection.format.setBackground(QColor(Qt.yellow).lighter(160))
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)

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
    editor.show()
    editor.setPlainText("\n".join([f"Linha {i+1}" for i in range(20)]))
    sys.exit(app.exec_())   