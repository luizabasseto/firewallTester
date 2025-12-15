"""Defines the 'Settings' tab for the Firewall Tester application."""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QPushButton, QLineEdit, QCheckBox,
    QGroupBox, QMessageBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt


class SettingsTab(QWidget):
    """
    A QWidget for viewing and editing application settings.

    (R0902): This class has many instance attributes, which is acceptable for a
    UI class that manages numerous configuration widgets.
    (R0903): This class has few public methods as it's primarily a self-contained
    UI component for data entry, which is an acceptable design.
    """
    DEFAULT_SETTINGS = {
        "firewall_directory": "/etc/",
        "reset_rules_file": "",
        "firewall_rules_file": "",
        "server_ports_file": "",
        "docker_image": "firewall_tester",
        "show_container_id": False,
        "include_filter_table": True,
        "include_nat_table": True,
        "include_mangle_table": False
    }

    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self._create_ui()

    def _create_ui(self):
        main_layout = QVBoxLayout(self)

        title = QLabel("Software settings")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        main_layout.addSpacing(15)

        form_layout = QFormLayout()
        self.config_firewall_dir_entry = QLineEdit()
        self.config_firewall_reset_rules_entry = QLineEdit()
        self.config_firewall_rules_entry = QLineEdit()
        self.config_server_ports_entry = QLineEdit()
        self.config_docker_image_entry = QLineEdit()

        form_layout.addRow("Firewall directory (inside container):", self.config_firewall_dir_entry)
        form_layout.addRow("Firewall rules reset file (local):",
                           self.config_firewall_reset_rules_entry)
        form_layout.addRow("Firewall rules file (local):",
                           self.config_firewall_rules_entry)
        form_layout.addRow("Server Ports file (local):", self.config_server_ports_entry)
        form_layout.addRow("Default Docker image name:", self.config_docker_image_entry)
        main_layout.addLayout(form_layout)

        checkbox_group = QGroupBox("Interface and listing options")
        checkbox_layout = QVBoxLayout(checkbox_group)

        self.config_show_container_id_check = QCheckBox("Show Container ID in the Hosts tab")
        self.config_include_filter_check = QCheckBox("Include 'Filter' table in the listing")
        self.config_include_nat_check = QCheckBox("Include 'Filter' table in the listing")
        self.config_include_mangle_check = QCheckBox("Include 'Mangle' table in the listing")

        checkbox_layout.addWidget(self.config_show_container_id_check)
        checkbox_layout.addWidget(self.config_include_filter_check)
        checkbox_layout.addWidget(self.config_include_nat_check)
        checkbox_layout.addWidget(self.config_include_mangle_check)
        main_layout.addWidget(checkbox_group)

        main_layout.addStretch(1)

        buttons_layout = QHBoxLayout()
        save_button = QPushButton("Save Settings")
        save_button.clicked.connect(self._save_settings)
        restore_button = QPushButton("Restore Defaults")
        restore_button.clicked.connect(self._restore_defaults)

        buttons_layout.addStretch(1)
        buttons_layout.addWidget(save_button)
        buttons_layout.addWidget(restore_button)
        buttons_layout.addStretch(1)
        main_layout.addLayout(buttons_layout)

        self._load_settings()

    def _load_settings(self):
        self.config_firewall_dir_entry.setText(self.config.get("firewall_directory", "/etc/"))
        self.config_firewall_reset_rules_entry.setText(self.config.get("reset_rules_file", ""))
        self.config_firewall_rules_entry.setText(self.config.get("firewall_rules_file", ""))
        self.config_server_ports_entry.setText(self.config.get("server_ports_file", ""))
        self.config_docker_image_entry.setText(self.config.get("docker_image", "firewall_tester"))

        self.config_show_container_id_check.setChecked(self.config.get("show_container_id", False))
        self.config_include_filter_check.setChecked(self.config.get("include_filter_table", True))
        self.config_include_nat_check.setChecked(self.config.get("include_nat_table", True))
        self.config_include_mangle_check.setChecked(self.config.get("include_mangle_table", False))

    def _save_settings(self):
        self.config["firewall_directory"] = self.config_firewall_dir_entry.text()
        self.config["reset_rules_file"] = self.config_firewall_reset_rules_entry.text()
        self.config["firewall_rules_file"] = self.config_firewall_rules_entry.text()
        self.config["server_ports_file"] = self.config_server_ports_entry.text()
        self.config["docker_image"] = self.config_docker_image_entry.text()

        self.config["show_container_id"] = self.config_show_container_id_check.isChecked()
        self.config["include_filter_table"] = self.config_include_filter_check.isChecked()
        self.config["include_nat_table"] = self.config_include_nat_check.isChecked()
        self.config["include_mangle_table"] = self.config_include_mangle_check.isChecked()

        QMessageBox.information(self,  "Success","Settings saved successfully!")

    def _restore_defaults(self):
        reply = QMessageBox.question(
            self,
            "Confirmation",
            "Are you sure you want to restore the default settings?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.config = self.DEFAULT_SETTINGS.copy()
            self._load_settings()
            self._save_settings()
