from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

def create_about_tab(self):
        self.about_frame = QWidget()
        layout = QVBoxLayout(self.about_frame)
        layout.setAlignment(Qt.AlignTop)
        self.notebook.addTab(self.about_frame, "About")

        lbl_title = QLabel("About the Software")
        lbl_title.setFont(QFont("Arial", 14, QFont.Bold))
        lbl_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_title)

        description = "This software was developed with the goal of strengthening network security through practical and efficient firewall testing. More than just a testing tool, it stands out as a valuable educational resource, designed to simplify and enhance the learning process about firewalls. Through an intuitive and interactive interface, students can visualize and experiment with the creation and application of firewall rules, making it easier to understand complex concepts and promoting deeper and more effective learning."
        
        lbl_description = QLabel(textwrap.fill(description, width=100))
        lbl_description.setWordWrap(True)
        lbl_description.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_description)
        
        info_layout = QFormLayout()
        info_layout.setContentsMargins(0, 20, 0, 20)
        info_layout.setAlignment(Qt.AlignCenter)
        layout.addLayout(info_layout)
        
        lbl_developer_name = QLabel("Prof. Luiz Arthur Feitosa dos Santos")
        lbl_developer_name.setFont(QFont("Arial", 12, QFont.Bold))
        info_layout.addRow("<b>Developer:</b>", lbl_developer_name)

        lbl_email = QLabel("<a href='mailto:luiz.arthur.feitosa.santos@gmail.com'>luiz.arthur.feitosa.santos@gmail.com</a>")
        lbl_email.setOpenExternalLinks(True)
        info_layout.addRow("<b>Email:</b>", lbl_email)

        lbl_institution = QLabel("UTFPR-CM")
        lbl_institution.setFont(QFont("Arial", 12, QFont.Bold))
        info_layout.addRow("<b>Institution:</b>", lbl_institution)

        lbl_project_link = QLabel("<a href='https://github.com/luizsantos/firewallTester'>https://github.com/luizsantos/firewallTester</a>")
        lbl_project_link.setOpenExternalLinks(True)
        info_layout.addRow("<b>Project Link:</b>", lbl_project_link)
        
        lbl_license = QLabel("<a href='https://www.gnu.org/licenses/gpl-3.0.html'>GNU GPL v3</a>")
        lbl_license.setOpenExternalLinks(True)
        info_layout.addRow("<b>License:</b>", lbl_license)

        btn_help = QPushButton("Help")
        btn_help.clicked.connect(self.open_help)
        
        help_layout = QHBoxLayout()
        help_layout.addStretch(1)
        help_layout.addWidget(btn_help)
        help_layout.addStretch(1)
        layout.addLayout(help_layout)

        layout.addStretch(1)

def open_help(self):
    webbrowser.open_new_tab("https://github.com/luizsantos/firewallTester")