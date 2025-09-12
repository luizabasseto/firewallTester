# ui/main_window.py
import sys
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTabWidget, QMessageBox

from core.container_manager import ContainerManager
from core.test_runner import TestRunner

from .hosts_tab import HostsTab
from .firewallRules_tab import FirewallRulesTab
from .firewallTests_tab import FirewallTestsTab 
from .settings_tab import SettingsTab
from .help_tab import HelpTab
from .about_tab import AboutTab

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Firewall Tester")
        self.setGeometry(100, 100, 1200, 800)

        self.container_manager = ContainerManager()
        self.test_runner = TestRunner()

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        self._create_tabs()

        bottom_layout = QHBoxLayout()
        btn_update_hosts = QPushButton("Atualizar Hosts")
        btn_update_hosts.clicked.connect(self._update_all_hosts)
        btn_exit = QPushButton("Sair")
        btn_exit.clicked.connect(self.close)
        
        bottom_layout.addWidget(btn_update_hosts)
        bottom_layout.addStretch(1)
        bottom_layout.addWidget(btn_exit)
        main_layout.addLayout(bottom_layout)

    def _create_tabs(self):

        hosts_data = self.container_manager.get_hosts_for_combobox()

        self.hosts_tab = HostsTab(self.container_manager)
        self.tab_widget.addTab(self.hosts_tab, "Hosts")
        
        self.firewall_tab = FirewallRulesTab(self.container_manager)
        self.tab_widget.addTab(self.firewall_tab, "Regras de Firewall")

        self.tests_tab = FirewallTestsTab(self.test_runner, hosts_data)
        self.tab_widget.addTab(self.tests_tab, "Testes de Firewall")

        self.settings_tab = SettingsTab()
        self.tab_widget.addTab(self.settings_tab, "Configurações")

        self.help_tab = HelpTab()
        self.tab_widget.addTab(self.help_tab, "Ajuda")

        self.about_tab = AboutTab()
        self.tab_widget.addTab(self.about_tab, "Sobre")
        
        self.hosts_tab.update_hosts_display(self.container_manager.get_all_containers_data())

    def _update_all_hosts(self):
        self.hosts_tab.update_hosts_display(self.container_manager.get_all_containers_data())
        QMessageBox.information(self, "Sucesso", "Informações dos hosts atualizadas.")

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Confirmação', 'Deseja realmente sair do programa?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()