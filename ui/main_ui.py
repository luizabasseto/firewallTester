import json
import sys
import pathlib
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTabWidget, QMessageBox, QFrame
from PyQt5.QtGui import QIcon

from core.container_manager import ContainerManager
from core.test_runner import TestRunner
from .hosts_tab import HostsTab
from .firewallRules_tab import FirewallRulesTab
from .firewallTests_tab import FirewallTestsTab 
from .settings_tab import SettingsTab
from .help_tab import HelpTab
from .about_tab import AboutTab
from .widgets.header import Header

class MainWindow(QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Firewall Tester")
        self.setGeometry(100, 100, 1200, 800)
        
        try:
            base_dir = pathlib.Path(__file__).parent.parent.resolve()
            icon_path = base_dir / "assets" / "logo.png"
            if icon_path.exists():
                self.setWindowIcon(QIcon(str(icon_path)))
            else:
                print("Aviso: Arquivo de ícone não encontrado em:", icon_path)
        except Exception as e:
            print(f"Erro ao carregar o ícone: {e}")

        self.container_manager = ContainerManager()
        self.test_runner = TestRunner()
        self.config = self._load_app_config() 
        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        app_header = Header("assets/logo.png", "Firewall Tester")
        main_layout.addWidget(app_header)
        
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line)

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
        
        self._update_all_hosts(is_initial_load=True)
        
    def _load_app_config(self):
        try:
            with open("config/config.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {} 
        
    def _update_all_hosts(self, is_initial_load=False):
        all_hosts_data = self.container_manager.get_all_containers_data()
        hosts_for_combobox = self.container_manager.get_hosts_for_combobox()

        self.hosts_tab.update_hosts_display(all_hosts_data)
        self.firewall_rules_tab.update_hosts_list(hosts_for_combobox)
        self.tests_tab.update_hosts_list(hosts_for_combobox)
        
        if not is_initial_load:
            QMessageBox.information(self, "Sucesso", "Informações dos hosts atualizadas.")

    def _create_tabs(self):
        self.hosts_tab = HostsTab(self.container_manager, self.config)
        self.tab_widget.addTab(self.hosts_tab, "Hosts")

        hosts_for_combobox = self.container_manager.get_hosts_for_combobox()
        self.firewall_rules_tab = FirewallRulesTab(self.container_manager, hosts_for_combobox, self.config)
        self.tab_widget.addTab(self.firewall_rules_tab, "Regras de Firewall")

        self.tests_tab = FirewallTestsTab(self.test_runner, self.config)
        self.tab_widget.addTab(self.tests_tab, "Testes de Firewall")

        self.settings_tab = SettingsTab(self.config)
        self.tab_widget.addTab(self.settings_tab, "Configurações")

        self.help_tab = HelpTab()
        self.tab_widget.addTab(self.help_tab, "Ajuda")

        self.about_tab = AboutTab(self.tab_widget)
        self.tab_widget.addTab(self.about_tab, "Sobre")

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Confirmação', 'Deseja realmente sair do programa?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()