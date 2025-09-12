from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QPushButton, QLineEdit, QCheckBox,
    QGroupBox, QMessageBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt


class SettingsTab(QWidget):
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

        title = QLabel("Configurações do Software")
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

        form_layout.addRow("Diretório do Firewall (no container):", self.config_firewall_dir_entry)
        form_layout.addRow("Arquivo de Reset de Regras (local):", self.config_firewall_reset_rules_entry)
        form_layout.addRow("Arquivo de Regras de Firewall (local):", self.config_firewall_rules_entry)
        form_layout.addRow("Arquivo de Portas do Servidor (local):", self.config_server_ports_entry)
        form_layout.addRow("Nome da Imagem Docker Padrão:", self.config_docker_image_entry)
        main_layout.addLayout(form_layout)

        checkbox_group = QGroupBox("Opções de Interface e Listagem")
        checkbox_layout = QVBoxLayout(checkbox_group)

        self.config_show_container_id_check = QCheckBox("Exibir coluna de ID do Container na aba de Hosts")
        self.config_include_filter_check = QCheckBox("Incluir tabela 'Filter' na listagem de regras")
        self.config_include_nat_check = QCheckBox("Incluir tabela 'NAT' na listagem de regras")
        self.config_include_mangle_check = QCheckBox("Incluir tabela 'Mangle' na listagem de regras")

        checkbox_layout.addWidget(self.config_show_container_id_check)
        checkbox_layout.addWidget(self.config_include_filter_check)
        checkbox_layout.addWidget(self.config_include_nat_check)
        checkbox_layout.addWidget(self.config_include_mangle_check)
        main_layout.addWidget(checkbox_group)

        main_layout.addStretch(1)

        buttons_layout = QHBoxLayout()
        save_button = QPushButton("Salvar Configurações")
        save_button.clicked.connect(self._save_settings)
        restore_button = QPushButton("Restaurar Padrões")
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

        QMessageBox.information(self, "Sucesso", "Configurações salvas com sucesso!")

    def _restore_defaults(self):
        reply = QMessageBox.question(
            self,
            "Confirmação",
            "Tem certeza que deseja restaurar as configurações padrão?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.config = self.DEFAULT_SETTINGS.copy()
            self._load_settings()
            self._save_settings()
