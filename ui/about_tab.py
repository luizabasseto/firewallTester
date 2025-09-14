# ui/about_tab.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QPushButton
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt
import webbrowser
import pathlib


class AboutTab(QWidget):
    def __init__(self, notebook):
        super().__init__()
        self.notebook = notebook
        self.create_about_tab()

    def create_about_tab(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        script_dir = pathlib.Path(__file__).parent.resolve()
        user_icon = str(script_dir / "assets" / "do-utilizador.png")
        github_icon = str(script_dir / "assets" / "github.png")

        self.notebook.addTab(self, QIcon(user_icon), "Sobre")

        lbl_title = QLabel("Sobre o Software")
        lbl_title.setFont(QFont("Arial", 14, QFont.Bold))
        lbl_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_title)
        layout.addSpacing(15)

        description = (
            "Este software foi desenvolvido com o objetivo de fortalecer a segurança de redes "
            "através de testes práticos e eficientes de firewall. Mais do que uma ferramenta "
            "de teste, ele se destaca como um valioso recurso educacional, projetado para "
            "simplificar e aprimorar o processo de aprendizado sobre firewalls..."
        )

        lbl_description = QLabel(description)
        lbl_description.setWordWrap(True)
        lbl_description.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_description)

        info_layout = QFormLayout()
        info_layout.setContentsMargins(0, 20, 0, 20)
        layout.addLayout(info_layout)

        lbl_developer_name = QLabel("Prof. Luiz Arthur Feitosa dos Santos")
        lbl_developer_name.setFont(QFont("Arial", 12, QFont.Bold))
        info_layout.addRow("<b>Desenvolvedor:</b>", lbl_developer_name)

        lbl_email = QLabel("<a href='mailto:luiz.arthur.feitosa.santos@gmail.com'>luiz.arthur.feitosa.santos@gmail.com</a>")
        lbl_email.setOpenExternalLinks(True)
        info_layout.addRow("<b>Email:</b>", lbl_email)

        lbl_institution = QLabel("UTFPR-CM")
        lbl_institution.setFont(QFont("Arial", 12, QFont.Bold))
        info_layout.addRow("<b>Instituição:</b>", lbl_institution)

        lbl_project_link = QLabel("<a href='https://github.com/luizsantos/firewallTester'>Repositório GitHub</a>")
        lbl_project_link.setOpenExternalLinks(True)
        info_layout.addRow("<b>Projeto:</b>", lbl_project_link)

        lbl_license = QLabel("<a href='https://www.gnu.org/licenses/gpl-3.0.html'>GNU GPL v3</a>")
        lbl_license.setOpenExternalLinks(True)
        info_layout.addRow("<b>Licença:</b>", lbl_license)

        btn_repo = QPushButton("Visitar Repositório no GitHub")
        btn_repo.setIcon(QIcon(github_icon))
        btn_repo.clicked.connect(self.open_github_project)

        help_layout = QHBoxLayout()
        help_layout.addStretch(1)
        help_layout.addWidget(btn_repo)
        help_layout.addStretch(1)
        layout.addLayout(help_layout)

        layout.addStretch(1)

    def open_github_project(self):
        webbrowser.open_new_tab("https://github.com/luizsantos/firewallTester")
