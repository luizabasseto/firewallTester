from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QGroupBox)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

def create_firewall_rules_tab(self):
    self.firewall_rules_frame = QWidget()
    layout = QVBoxLayout(self.firewall_rules_frame)
    self.notebook.addTab(self.firewall_rules_frame, "Firewall Rules")

    top_layout = QHBoxLayout()
    top_layout.addWidget(QLabel("Edit firewall rules on host:"))
    self.combobox_firewall_rules_host = QComboBox()
    self.combobox_firewall_rules_host.addItems(self.hosts)
    self.combobox_firewall_rules_host.setCurrentIndex(-1)
    self.combobox_firewall_rules_host.currentIndexChanged.connect(self.selected_host_on_combobox_tab_firewall_rules)
    top_layout.addWidget(self.combobox_firewall_rules_host)
    top_layout.addStretch(1)
    layout.addLayout(top_layout)

    # Rules editor
    rules_box = QGroupBox("Rules to be applied to the firewall")
    rules_layout = QVBoxLayout(rules_box)
    self.text_firewall_rules = QTextEdit()
    self.text_firewall_rules.setFont(QFont("Monospace"))
    rules_layout.addWidget(self.text_firewall_rules)
    self.reset_firewall_check = QCheckBox("Automatically reset firewall rules")
    rules_layout.addWidget(self.reset_firewall_check)
    layout.addWidget(rules_box)

    # Output viewer
    self.output_firewall_rules_box = QGroupBox("Output")
    output_layout = QVBoxLayout(self.output_firewall_rules_box)
    self.text_active_firewall_rules = QTextEdit()
    self.text_active_firewall_rules.setReadOnly(True)
    self.text_active_firewall_rules.setFont(QFont("Monospace"))
    output_layout.addWidget(self.text_active_firewall_rules)
    self.button_list_firewall_rules = QPushButton("List firewall rules")
    self.button_list_firewall_rules.clicked.connect(self.list_firewall_rules_on_output)
    output_layout.addWidget(self.button_list_firewall_rules, alignment=Qt.AlignCenter)
    layout.addWidget(self.output_firewall_rules_box)

    # Main buttons
    buttons_layout = QHBoxLayout()
    self.button_retrieve_firewall_rules = QPushButton("Retrieve firewall rules")
    self.button_retrieve_firewall_rules.clicked.connect(self.load_firewall_rules)
    self.button_deploy_firewall_rules = QPushButton("Deploy firewall rules")
    self.button_deploy_firewall_rules.clicked.connect(self.apply_firewall_rules)
    button_show_output = QPushButton("Toggle Output")
    button_show_output.clicked.connect(lambda: self.output_firewall_rules_box.setVisible(not self.output_firewall_rules_box.isVisible()))
    
    buttons_layout.addWidget(self.button_retrieve_firewall_rules)
    buttons_layout.addWidget(self.button_deploy_firewall_rules)
    buttons_layout.addStretch(1)
    buttons_layout.addWidget(button_show_output)
    layout.addLayout(buttons_layout)
    
    self.selected_host_on_combobox_tab_firewall_rules() # To set initial button states

def selected_host_on_combobox_tab_firewall_rules(self):
    selected_index = self.combobox_firewall_rules_host.currentIndex()
    is_host_selected = selected_index != -1
    
    self.button_retrieve_firewall_rules.setEnabled(is_host_selected)
    self.button_deploy_firewall_rules.setEnabled(is_host_selected)
    self.button_list_firewall_rules.setEnabled(is_host_selected)
    
    if is_host_selected:
        self.container_id_host_regras_firewall = self.container_hostname[selected_index]
    else:
        self.container_id_host_regras_firewall = None

def list_firewall_rules_on_output(self):
    if not self.container_id_host_regras_firewall: return
    
    self.text_active_firewall_rules.clear()
    host_id, host_name = self.container_id_host_regras_firewall
    
    output_text = ""
    
    if self.config_include_mangle_check.isChecked():
        command = ["docker", "exec", host_id, "iptables", "-L", "-n", "-t", "mangle"]
        result = containers.run_command(command)
        output_text += f"<b>&bull; Mangle Rules on {host_name}:</b><br>{result.stdout.replace(os.linesep, '<br>')}<br><br>"
        
    if self.config_include_nat_check.isChecked():
        command = ["docker", "exec", host_id, "iptables", "-L", "-n", "-t", "nat"]
        result = containers.run_command(command)
        output_text += f"<b>&bull; NAT Rules on {host_name}:</b><br>{result.stdout.replace(os.linesep, '<br>')}<br><br>"

    if self.config_include_filter_check.isChecked():
        command = ["docker", "exec", host_id, "iptables", "-L", "-n"]
        result = containers.run_command(command)
        output_text += f"<b>&bull; Filter Rules on {host_name}:</b><br>{result.stdout.replace(os.linesep, '<br>')}<br><br>"
    
    if not output_text:
        output_text = "All firewall rule tables are disabled for listing in the settings tab."
        
    self.text_active_firewall_rules.setHtml(output_text)

def load_firewall_rules(self):
    if not self.container_id_host_regras_firewall: return
    
    reply = QMessageBox.question(self, "Confirmation", "This will overwrite the existing rules in the interface. Continue?",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
    if reply == QMessageBox.Yes:
        host_id, _ = self.container_id_host_regras_firewall
        file = self.config_firewall_dir_entry.text() + "/firewall.sh"
        command = ["docker", "exec", host_id, "cat", file]
        result = containers.run_command(command)
        self.text_firewall_rules.setPlainText(result.stdout)

def apply_firewall_rules(self):
    if not self.container_id_host_regras_firewall: return

    print(f"Apply rules on the firewall of host {self.container_id_host_regras_firewall[1]}")
    rules = self.text_firewall_rules.toPlainText()
    file_rules_path = self.config_firewall_rules_entry.text()
    
    with open(file_rules_path, "w", encoding="utf-8") as file_name:
        file_name.write(rules)

    if self.reset_firewall_check.isChecked():
        self.send_to_host_file_to_execute_firewall_rules(self.config_firewall_reset_rules_entry.text(), True)
    
    self.send_to_host_file_to_execute_firewall_rules(file_rules_path, False)
    
    if self.reset_firewall_check.isChecked():
        self.text_active_firewall_rules.append("\n<b>&gt;&gt;Warning!&lt;&lt;</b> The firewall rules were reset via the interface. This SHOULD be in your script!")

def send_to_host_file_to_execute_firewall_rules(self, file_rules_path, is_reset):
    if not self.container_id_host_regras_firewall: return
    host_id, host_name = self.container_id_host_regras_firewall

    if is_reset:
        container_path = self.config_firewall_dir_entry.text() + "/firewall_reset.sh"
        command_to_run = ["docker", "exec", host_id, "sh", container_path]
    else:
        container_path = self.config_firewall_dir_entry.text() + "/firewall.sh"
        command_to_run = ["docker", "exec", host_id, "sh", container_path]

    containers.copy_host2container(host_id, file_rules_path, container_path)
    result = containers.run_command(command_to_run)
    
    self.text_active_firewall_rules.clear()
    if result.stderr:
        self.text_active_firewall_rules.setHtml(f"<b>* Error applying firewall rules on host {host_name}:</b><br><pre>{result.stderr}</pre>")
        QMessageBox.warning(self, "Warning", "Something went wrong while executing the rules, check the output!")
    else:
        self.list_firewall_rules_on_output()
        self.text_active_firewall_rules.append(f"\n<b>* Firewall status on host {host_name} after rules have been applied.</b>")
