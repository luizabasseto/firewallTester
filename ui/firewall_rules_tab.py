"""
Defines the 'Firewall Rules' tab for the Firewall Tester application.

This tab allows users to view, edit, and apply iptables rules to the
Docker containers in the test environment. It also includes an AI feature
to analyze and explain firewall rules.
"""

import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                            QComboBox, QGroupBox, QTextEdit, QCheckBox, QMessageBox,
                            QApplication, QMessageBox, QFileDialog)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class FirewallRulesTab(QWidget):
    """A QWidget for managing firewall rules on selected container hosts."""
    # R0902: Pylint flags too many attributes. This is common for UI classes
    # where widgets are stored as instance attributes for later access.
    # R0913/R0917: Pylint flags too many arguments. These are necessary dependencies
    # passed from the main window.
    def __init__(self, container_manager, hosts_data, config, parent=None):
        super().__init__(parent)
        self.container_manager = container_manager
        self.hosts_data = hosts_data
        self.config = config
        self.selected_container_id = None
        self.selected_hostname = None
        self._setup_ui()
        self._on_host_selected()
        self.save_file_path = None
        

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)

        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("Edit firewall rules on host:"))
        self.combo_hosts = QComboBox()
        self.combo_hosts.addItems([hostname for hostname, _ in self.hosts_data])
        self.combo_hosts.setCurrentIndex(-1)
        self.combo_hosts.currentIndexChanged.connect(self._on_host_selected)
        top_layout.addWidget(self.combo_hosts)
        top_layout.addStretch(1)
        main_layout.addLayout(top_layout)

        rules_box = QGroupBox("Rules to be applied to the firewall")
        rules_layout = QVBoxLayout(rules_box)
        self.text_editor_rules = QTextEdit()
        self.text_editor_rules.setFont(QFont("Monospace", 10))
        rules_layout.addWidget(self.text_editor_rules)
        editor_buttons_layout = QHBoxLayout()
        self.check_reset_rules = QCheckBox("Reset rules before applying")

        editor_buttons_layout.addWidget(self.check_reset_rules)
        editor_buttons_layout.addStretch(1)
        rules_layout.addLayout(editor_buttons_layout)
        main_layout.addWidget(rules_box)
        
        file_buttons_layout = QHBoxLayout()
        main_layout.addLayout(file_buttons_layout)
        self.btn_save = QPushButton("Save Rules")
        self.btn_save_as = QPushButton("Save As...")
        self.btn_load = QPushButton("Open Rules")

        file_buttons_layout.addStretch(1)
        file_buttons_layout.addWidget(self.btn_save)
        file_buttons_layout.addWidget(self.btn_save_as)
        file_buttons_layout.addWidget(self.btn_load)
        file_buttons_layout.addStretch(1)

        self.btn_save.clicked.connect(self._save_rules)
        self.btn_save_as.clicked.connect(self._save_rules_as)
        self.btn_load.clicked.connect(self._open_rules)
        
        
        self.output_box = QGroupBox("Output and Active Rules")
        output_layout = QVBoxLayout(self.output_box)
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setFont(QFont("Monospace", 9))
        output_layout.addWidget(self.log_output)
        
        self.btn_list_rules = QPushButton("List Active Rules on Host")
        self.btn_list_rules.clicked.connect(self._list_rules)
        output_layout.addWidget(self.btn_list_rules, alignment=Qt.AlignCenter)
        main_layout.addWidget(self.output_box)

        buttons_layout = QHBoxLayout()
        self.btn_retrieve_rules = QPushButton("Load Rules from Host")
        self.btn_retrieve_rules.clicked.connect(self._load_rules)
        self.btn_deploy_rules = QPushButton("Load Rules from Host")
        self.btn_deploy_rules.clicked.connect(self._apply_rules)
        btn_toggle_output = QPushButton("Show/Hide Output")
        btn_toggle_output.clicked.connect(lambda: self.output_box.setVisible(not self.output_box.isVisible()))
        
        buttons_layout.addWidget(self.btn_retrieve_rules)
        buttons_layout.addWidget(self.btn_deploy_rules)
        buttons_layout.addStretch(1)
        buttons_layout.addWidget(btn_toggle_output)
        main_layout.addLayout(buttons_layout)

        
    def _on_host_selected(self):
        selected_index = self.combo_hosts.currentIndex()
        is_host_selected = selected_index != -1
        self.btn_retrieve_rules.setEnabled(is_host_selected)
        self.btn_deploy_rules.setEnabled(is_host_selected)
        self.btn_list_rules.setEnabled(is_host_selected)
        if is_host_selected:
            self.selected_hostname, self.selected_container_id = self.hosts_data[selected_index]
        else:
            self.selected_hostname, self.selected_container_id = None, None
        self.text_editor_rules.clear()
        self.log_output.clear()

    def _list_rules(self):
        if not self.selected_container_id:
            return

        self.log_output.clear()
        self.log_output.append(f"<i>Listing rules for <b>{self.selected_hostname}</b>...</i>")
        QApplication.processEvents()

        tables_to_check = {
            'mangle': self.config.get("include_mangle_table", False),
            'nat': self.config.get("include_nat_table", True),
            'filter': self.config.get("include_filter_table", True)
        }

        success, result = self.container_manager.get_firewall_rules(
            self.selected_container_id, tables_to_check
        )

        self.log_output.clear()
        if not success:
            error_html = f"<font color='red'><b>Error listing rules:</b><br><pre>{result}</pre></font>"
            self.log_output.setHtml(error_html)
            return

        if not result:
            self.log_output.setText(
                "No firewall tables selected in Settings."
            )
            return

        html_output = "".join(
            f"<b>&bull; Table  {table.capitalize()}:</b><br><pre>{content}</pre><br>"
            for table, content in result.items()
        )
        self.log_output.setHtml(html_output)

    def _load_rules(self):
        if not self.selected_container_id:
            return

        reply = QMessageBox.question(
            self, "Confirmation",
            "This will overwrite the editor with the current rules from the host. Continue?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.No:
            return

        container_path = os.path.join(self.config.get("firewall_directory", "/etc/"), "firewall.sh")
        success, content = self.container_manager.get_rules_from_file(self.selected_container_id, container_path)

        if success:
            self.text_editor_rules.setPlainText(content)
            log_msg = f"<i>Rules loaded from '{container_path}' on host {self.selected_hostname}.</i>"

            self.log_output.append(log_msg)
        else:
            QMessageBox.warning(self, "Error",
                f"Unable to load rules: {content}"
            )

    def _apply_rules(self):
        if not self.selected_container_id:
            return

        self.log_output.append(f"<i>Applying rules on host <b>{self.selected_hostname}</b>...</i>")
        QApplication.processEvents()
        rules_text = self.text_editor_rules.toPlainText()
        success, message = self.container_manager.apply_firewall_rules(
            host_id=self.selected_container_id,
            hostname=self.selected_hostname,
            rules_string=rules_text,
            reset_first=self.check_reset_rules.isChecked()
        )

        if success:
            self.log_output.append(f"<b>&gt; {message}</b>")
            self._list_rules()
        else:
            error_msg = (
                f"<font color='red'><b>&gt; Error applying rules:</b>"
                f"<br><pre>{message}</pre></font>"
            )
            self.log_output.append(error_msg)
            QMessageBox.warning(self, "Error",
                "Failed to apply the rules. Check the output."
            )

    def update_hosts_list(self, hosts_data_tuples):
        """Updates the dropdown list of hosts."""
        self.hosts_data = hosts_data_tuples
        host_names = [name for name, _ in self.hosts_data]
        current_selection = self.combo_hosts.currentText()
        self.combo_hosts.clear()
        self.combo_hosts.addItems(host_names)
        index = self.combo_hosts.findText(current_selection)
        if index != -1:
            self.combo_hosts.setCurrentIndex(index)
        else:
            self.combo_hosts.setCurrentIndex(-1)

    def _save_rules_as(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Save Rules File",
            "",
            "Shell Scripts (*.sh);;Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            self.save_file_path = file_path
            self._save_rules()

    def _save_rules(self):
        if not self.save_file_path:
            self._save_rules_as()
            return

        rules_data = self.text_editor_rules.toPlainText()

        try:
            with open(self.save_file_path, "w", encoding="utf-8") as f:
                f.write(rules_data)
            QMessageBox.information(
                self,"Success",f"Rules saved to:\n{self.save_file_path}"
            )
        except (IOError, TypeError) as e:
            QMessageBox.critical(
                self,"Error",f"Unable to save the file:\n{e}"
            )

    def _open_rules(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Open Rules File",
            "",
            "Shell Scripts (*.sh);;Text Files (*.txt);;All Files (*)"
        )
        if file_path:
            self.save_file_path = file_path
            self._load_from_file()

    def _load_from_file(self):
        if not self.save_file_path or not os.path.exists(self.save_file_path):
            QMessageBox.warning(self, "Error","Rules file not found.")
            return

        reply = QMessageBox.question(self, "Load Rules",
            "This will overwrite the current editor content. Do you want to continue?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.No:
            return

        try:
            with open(self.save_file_path, "r", encoding="utf-8") as f:
                rules_data = f.read()

            self.text_editor_rules.setPlainText(rules_data)
            QMessageBox.information(self, "Success",
                "Rules loaded successfully.")

        except IOError as e:
            QMessageBox.critical(
                self,"Error",f"Unable to load the file:\n{e}")