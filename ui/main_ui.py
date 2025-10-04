# Salve como: ui/main_window.py
import sys
import json
import pathlib
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTabWidget, QMessageBox, QFrame
from PyQt5.QtGui import QIcon

from core.container_manager import ContainerManager
from core.test_runner import TestRunner
from core.ai_assistance import AIAssistant

from .hosts_tab import HostsTab
from .firewall_rules_tab import FirewallRulesTab
from .firewall_tests_tab import FirewallTestsTab 
from .settings_tab import SettingsTab
from .help_tab import HelpTab
from .about_tab import AboutTab
from .widgets.header import Header


#!/usr/bin/env python

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

"""
    Program Name: Firewall Tester - Graphical Interface
    Description: This is the graphical interface and the main part of the firewall rule testing software.
    Author: Luiz Arthur Feitosa dos Santos - luiz.arthur.feitosa.santos@gmail.com / luizsantos@utfpr.edu.br
    License: GNU General Public License v3.0
    Version: 1.1 (Ported to PyQt5)
"""



# TODO - Standardize variable and function names - use English names.
# TODO - Leave all print and graphical messages in English - buttons, labels, etc...
# TODO - Refactor the code - remove duplicate code, see what can be improved, perhaps with the concept of object-oriented programming.
# TODO - Remove variables and code that are not being used - there may be useless code, especially since the change from label to treeview.
# TODO - Configuration tab - see if it is necessary and what to put there (e.g., location where rules should be loaded in the container; whether or not to display the container ID column, whether or not to start the servers, list iptables mangle rules, maybe list or not iptables nat or filter rules - now interface list filter and nat rules by default).
# TODO - Create a help for the user.
# TODO - When performing tests, check for errors such as testing a closed port on the server, the interface could warn about this (leave it, but warn).
# TODO - Verify the message flow, such as, it arrived at the server but did not return, indicate this in the interface.
# TODO - Think about how to show the execution logs, which go to the text console, to the interface, this helps a lot in showing problems and the test flow.
# TODO - Think about how to show "packet" details - JSON objects returned by client/server in tests.
# TODO - In the container.py file - when starting a server on a port already in use by another program other than server.py, verify if it can really kill that process.
# TODO - Think about how to access some real services, such as HTTP, SSH, MYSQL, etc., and how to show this in the interface, currently outside of client.py/server.py only ICMP can be accessed externally.
# TODO - Think about tests of malformed packets such as those from nmap or scapy.
# TODO - Suggest tests that may be common in corporate environments.
# TODO - Suggest tests based on the services running in the environment.
# TODO - Suggest tests based on the tests proposed by the user, such as: if they asked host1 to access HTTP on host3, do the opposite as well.
# TODO - Perhaps it would be nice to have options to wait for test success considering DNAT, that is, to have an option that when enabled waits for the flow to go through a DNAT, otherwise the test would be considered failed!
# TODO - The scroll of the firewall tests is not working properly and is cutting off the last column of the tree. (Note: PyQt's QTreeWidget handles this better).
# TODO - Check if scroll is needed in other areas of the program (vertical and horizontal). (Note: PyQt handles this better with layouts and QScrollArea).
# TODO - Is it interesting to have a button to save firewall rules on the host? the user can do ctrl+c and ctrl+v - remembering that the rules are already saved in the container.
# TODO - if only the host or all hosts in the scenario are turned off, there is no problem for the interface, but if GNS3 is turned off and the same scenario is turned on again, the interface becomes inconsistent, even the host update button does not work properly! Also, the rules deployed in the firewall are lost.
# TODO - when saving and opening tests - do not reference the container ID, only the names and perhaps IPs (I think IPs are unavoidable for now), and when the rules are opened, the interface must relate or re-relate the hostname with the container_id, and perhaps the IPs (it would be nice not to relate with the IPs, because in the scenario the user could create or change the hostname to another IP and the test would continue to work).
# TODO - the combobox of "Edit firewall rules on host" should not show multiple lines for the same host (it shows one per host IP), but rather only one name.
# TODO - You need a scroll on the tabs and it also limits their size, because when you put too many hosts (about 7) the buttons to update hosts and exit the program disappeared, because the tabs pushed them off the screen. (Note: QTabWidget can handle this with scroll buttons).
# TODO - The information regarding docker containers is being performed three times in a row at the beginning, see if this is really necessary or if it can be done just once.
# TODO - relate the name of the docker image with the name used in the configuration tab.
# TODO -

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Firewall Tester")
        self.setGeometry(100, 100, 1200, 800)
        self._set_window_icon()

        self.config = self._load_app_config()
        self.container_manager = ContainerManager(self.config.get("docker_image", "firewall_tester"))
        self.test_runner = TestRunner()
        self.ai_assistant = AIAssistant()
        
        self._setup_ui()
        
        self._update_all_hosts(is_initial_load=True)

    def _setup_ui(self):
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

    def _load_app_config(self):
        try:
            with open("config/config.json", "r", encoding="utf-8") as f:
                default_settings = SettingsTab.DEFAULT_SETTINGS.copy()
                loaded_settings = json.load(f)
                default_settings.update(loaded_settings)
                return default_settings
        except (FileNotFoundError, json.JSONDecodeError):
            return SettingsTab.DEFAULT_SETTINGS.copy()

    def _create_tabs(self):
        hosts_for_combobox = self.container_manager.get_hosts_for_combobox()

        self.hosts_tab = HostsTab(self.container_manager, self.config)
        self.firewall_rules_tab = FirewallRulesTab(self.container_manager, hosts_for_combobox, self.config, self.ai_assistant)
        
        self.tests_tab = FirewallTestsTab(self.test_runner, hosts_for_combobox, self.config)
        
        self.settings_tab = SettingsTab(self.config)
        self.help_tab = HelpTab()
        
        self.about_tab = AboutTab()
        
        self.tab_widget.addTab(self.hosts_tab, "Hosts")
        self.tab_widget.addTab(self.firewall_rules_tab, "Regras de Firewall")
        self.tab_widget.addTab(self.tests_tab, "Testes de Firewall")
        self.tab_widget.addTab(self.settings_tab, "Configurações")
        self.tab_widget.addTab(self.help_tab, "Ajuda")
        self.tab_widget.addTab(self.about_tab, "Sobre")
        
    def _update_all_hosts(self, is_initial_load=False):
        all_hosts_data = self.container_manager.get_all_containers_data()
        hosts_for_combobox = self.container_manager.get_hosts_for_combobox()

        self.hosts_tab.update_hosts_display(all_hosts_data)
        self.firewall_rules_tab.update_hosts_list(hosts_for_combobox)
        self.tests_tab.update_hosts_list(hosts_for_combobox)
        
        if not is_initial_load:
            QMessageBox.information(self, "Sucesso", "Informações dos hosts atualizadas.")

    def _set_window_icon(self):
        try:
            script_dir = pathlib.Path(__file__).parent.parent.resolve()
            icon_path = script_dir / "assets" / "logo.png"
            if icon_path.exists():
                self.setWindowIcon(QIcon(str(icon_path)))
        except Exception as e:
            print(f"Erro ao carregar o ícone: {e}")

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Confirmação', 'Deseja realmente sair do programa?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()