import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QComboBox, QGroupBox, QTextEdit, QCheckBox, QMessageBox,
    QApplication)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt

class FirewallRulesTab(QWidget):
    def __init__(self, container_manager, hosts_data, config, parent=None):
        super().__init__(parent)
        
        self.container_manager = container_manager
        self.hosts_data = hosts_data 
        self.config = config
        
        self.selected_container_id = None
        self.selected_hostname = None
        
        self._setup_ui()
        self._on_host_selected() 

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)

        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("Editar regras de firewall no host:"))
        self.combo_hosts = QComboBox()
        self.combo_hosts.addItems([hostname for hostname, _ in self.hosts_data])
        self.combo_hosts.setCurrentIndex(-1)
        self.combo_hosts.currentIndexChanged.connect(self._on_host_selected)
        top_layout.addWidget(self.combo_hosts)
        top_layout.addStretch(1)
        main_layout.addLayout(top_layout)

        rules_box = QGroupBox("Regras a serem aplicadas no firewall")
        rules_layout = QVBoxLayout(rules_box)
        self.text_editor_rules = QTextEdit()
        self.text_editor_rules.setFont(QFont("Monospace", 10))
        rules_layout.addWidget(self.text_editor_rules)
        self.check_reset_rules = QCheckBox("Resetar as regras do firewall antes de aplicar as novas")
        rules_layout.addWidget(self.check_reset_rules)
        main_layout.addWidget(rules_box)

        self.output_box = QGroupBox("Saída e Regras Ativas")
        output_layout = QVBoxLayout(self.output_box)
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setFont(QFont("Monospace", 9))
        output_layout.addWidget(self.log_output)
        self.btn_list_rules = QPushButton("Listar Regras Ativas no Host")
        self.btn_list_rules.clicked.connect(self._list_rules)
        output_layout.addWidget(self.btn_list_rules, alignment=Qt.AlignCenter)
        main_layout.addWidget(self.output_box)

        buttons_layout = QHBoxLayout()
        self.btn_retrieve_rules = QPushButton("Carregar Regras do Host")
        self.btn_retrieve_rules.clicked.connect(self._load_rules)
        self.btn_deploy_rules = QPushButton("Aplicar Regras no Host")
        self.btn_deploy_rules.clicked.connect(self._apply_rules)
        btn_toggle_output = QPushButton("Mostrar/Esconder Saída")
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
        if not self.selected_container_id: return
        
        self.log_output.clear()
        self.log_output.append(f"<i>Listando regras para <b>{self.selected_hostname}</b>...</i>")
        QApplication.processEvents()

        tables_to_check = {
            'mangle': self.config.get("include_mangle_table", False),
            'nat': self.config.get("include_nat_table", True),
            'filter': self.config.get("include_filter_table", True)
        }
        
        success, result = self.container_manager.get_firewall_rules(self.selected_container_id, tables_to_check)
        
        self.log_output.clear()
        if not success:
            self.log_output.setHtml(f"<font color='red'><b>Erro ao listar regras:</b><br><pre>{result}</pre></font>")
            return
        
        if not result:
            self.log_output.setText("Nenhuma tabela de firewall selecionada para listagem nas Configurações.")
            return

        html_output = "".join(
            f"<b>&bull; Tabela {table.capitalize()}:</b><br><pre>{content}</pre><br>"
            for table, content in result.items()
        )
        self.log_output.setHtml(html_output)

    def _load_rules(self):
        if not self.selected_container_id: return
        
        reply = QMessageBox.question(self, "Confirmação", 
            "Isso irá sobrescrever o conteúdo do editor com as regras atuais do host. Continuar?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.No:
            return

        container_path = os.path.join(self.config.get("firewall_directory"), "firewall.sh")
        success, content = self.container_manager.get_rules_from_file(self.selected_container_id, container_path)
        
        if success:
            self.text_editor_rules.setPlainText(content)
            self.log_output.append(f"<i>Regras carregadas de '{container_path}' do host {self.selected_hostname}.</i>")
        else:
            QMessageBox.warning(self, "Erro", f"Não foi possível carregar as regras: {content}")

    def _apply_rules(self):
        if not self.selected_container_id: return

        self.log_output.append(f"<i>Aplicando regras no host <b>{self.selected_hostname}</b>...</i>")
        QApplication.processEvents()
        
        rules_text = self.text_editor_rules.toPlainText()
        
        success, message = self.container_manager.apply_firewall_rules(
            host_id=self.selected_container_id,
            hostname=self.selected_hostname,
            rules_string=rules_text,
            local_rules_path=self.config.get("firewall_rules_file"),
            local_reset_path=self.config.get("reset_rules_file"),
            container_dir=self.config.get("firewall_directory"),
            reset_first=self.check_reset_rules.isChecked()
        )
        
        if success:
            self.log_output.append(f"<b>&gt; {message}</b>")
            self._list_rules()
        else:
            self.log_output.append(f"<font color='red'><b>&gt; Erro ao aplicar regras:</b><br><pre>{message}</pre></font>")
            QMessageBox.warning(self, "Erro", "Algo deu errado ao executar as regras. Verifique a saída.")

    def update_hosts_list(self, hosts_data_tuples):
        self.hosts_data = hosts_data_tuples
        
        host_names = [name for name, _ in self.hosts_data]
        
        self.combo_hosts.clear()
        self.combo_hosts.addItems(host_names)
        self.combo_hosts.setCurrentIndex(-1)