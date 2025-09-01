# Não se esqueça de adicionar QTextBrowser aos seus imports
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextBrowser
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

def create_help_tab(self):
    self.help_frame = QWidget()
    main_layout = QVBoxLayout(self.help_frame)
    main_layout.setAlignment(Qt.AlignTop)
    self.notebook.addTab(self.about_frame, QIcon("assets/info.png"), "Help")
    
    

    help_text_browser = QTextBrowser()
    help_text_browser.setOpenExternalLinks(True) 
    
    try:
        with open('ui/help_content.html', 'r', encoding='utf-8') as f:
            help_content = f.read()
        help_text_browser.setHtml(help_content)
    except FileNotFoundError:
        help_text_browser.setHtml("<h1>Erro</h1><p>Arquivo de ajuda não encontrado.</p>")
        
    main_layout.addWidget(help_text_browser)