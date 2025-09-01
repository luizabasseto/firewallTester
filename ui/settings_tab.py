from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QPushButton, QLineEdit, QCheckBox)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

def create_settings_tab(self):
    self.config_frame = QWidget()
    layout = QVBoxLayout(self.config_frame)
    self.notebook.addTab(self.config_frame, "Settings")

    title = QLabel("Software Settings")
    title.setFont(QFont("Arial", 14, QFont.Bold))
    title.setAlignment(Qt.AlignCenter)
    layout.addWidget(title)

    form_widget = QWidget()
    form_layout = QFormLayout(form_widget)
    layout.addWidget(form_widget)

    self.config_firewall_dir_entry = QLineEdit()
    self.config_firewall_reset_rules_entry = QLineEdit()
    self.config_firewall_rules_entry = QLineEdit()
    self.config_server_ports_entry = QLineEdit()
    self.config_docker_image_entry = QLineEdit()
    
    self.config_show_container_id_check = QCheckBox("Show Container ID Column")
    self.config_include_filter_check = QCheckBox("Include Filter Table in Firewall Listing")
    self.config_include_nat_check = QCheckBox("Include NAT Table in Firewall Listing")
    self.config_include_mangle_check = QCheckBox("Include Mangle Table in Firewall Listing")

    form_layout.addRow("Firewall Directory in Containers:", self.config_firewall_dir_entry)
    form_layout.addRow("Reset Rules File:", self.config_firewall_reset_rules_entry)
    form_layout.addRow("Firewall Rules File:", self.config_firewall_rules_entry)
    form_layout.addRow("Server Ports File:", self.config_server_ports_entry)
    form_layout.addRow("Docker Image Name:", self.config_docker_image_entry)
    form_layout.addRow(self.config_show_container_id_check)
    form_layout.addRow(self.config_include_filter_check)
    form_layout.addRow(self.config_include_nat_check)
    form_layout.addRow(self.config_include_mangle_check)
    
    buttons_layout = QHBoxLayout()
    layout.addLayout(buttons_layout)

    save_button = QPushButton("Save Settings")
    save_button.clicked.connect(self.save_settings)
    restore_button = QPushButton("Restore Defaults")
    restore_button.clicked.connect(self.restore_default_settings)
    
    buttons_layout.addStretch(1)
    buttons_layout.addWidget(save_button)
    buttons_layout.addWidget(restore_button)
    buttons_layout.addStretch(1)

    layout.addStretch(1)