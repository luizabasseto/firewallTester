"""Defines the 'About' tab for the Firewall Tester application."""

import pathlib
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QPushButton
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt

class AboutTab(QWidget):
    """A QWidget that displays information about the application and its author."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.create_about_tab()

    def create_about_tab(self):
        """Sets up the UI elements for the 'About' tab."""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        script_dir = pathlib.Path(__file__).parent.resolve()
        github_icon = str(script_dir / "assets" / "github.png")

        lbl_title = QLabel("About the Software")
        lbl_title.setFont(QFont("Arial", 14, QFont.Bold))
        lbl_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_title)
        layout.addSpacing(15)

        description = (
            "This software was developed with the goal of strengthening network security "
            "through practical and efficient firewall testing. More than just a testing "
            "tool, it stands out as a valuable educational resource, designed to "
            "simplify and enhance the learning process about firewalls..."
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
        info_layout.addRow("<b>Developer:</b>", lbl_developer_name)

        email_link = (
            "<a href='mailto:luiz.arthur.feitosa.santos@gmail.com'>"
            "luiz.arthur.feitosa.santos@gmail.com</a>"
        )
        lbl_email = QLabel(email_link)
        lbl_email.setOpenExternalLinks(True)
        info_layout.addRow("<b>Email:</b>", lbl_email)
        
        lbl_developer_name2 = QLabel("Student Luiza Batista Basseto")
        lbl_developer_name2.setFont(QFont("Arial", 12, QFont.Bold))
        info_layout.addRow("<b>Developer:</b>", lbl_developer_name2)

        email_link2 = (
            "<a href='mailto:luizabasseto.1@gmail.com'>"
            "luizabasseto.1@gmail.com</a>"
        )
        lbl_email2 = QLabel(email_link2)
        lbl_email2.setOpenExternalLinks(True)
        info_layout.addRow("<b>Email:</b>", lbl_email2)

        lbl_institution = QLabel("UTFPR-CM")
        lbl_institution.setFont(QFont("Arial", 12, QFont.Bold))
        info_layout.addRow("<b>Institution:</b>", lbl_institution)

        project_link = "<a href='https://github.com/luizsantos/firewallTester'>GitHub Repository</a>"
        lbl_project_link = QLabel(project_link)
        lbl_project_link.setOpenExternalLinks(True)
        info_layout.addRow("<b>Project:</b>", lbl_project_link)

        lbl_license = QLabel("<a href='https://www.gnu.org/licenses/gpl-3.0.html'>GNU GPL v3</a>")
        lbl_license.setOpenExternalLinks(True)
        info_layout.addRow("<b>License:</b>", lbl_license)
        
        # TODO: Check if the button to open the GitHub repository works

        layout.addStretch(1)
