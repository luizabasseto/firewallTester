"""
Main window for the Firewall Tester application.

This module defines the main graphical user interface, which includes the
tabbed layout for all features, and orchestrates the core components like
the ContainerManager and TestRunner.
"""

import json
import pathlib
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QPushButton, QTabWidget, QMessageBox, QFrame, QApplication)
from PyQt5.QtGui import QIcon

from core.container_manager import ContainerManager
from core.test_runner import TestRunner

from .hosts_tab import HostsTab
from .firewall_rules_tab import FirewallRulesTab
from .firewall_tests_tab import FirewallTestsTab
from .settings_tab import SettingsTab
from .help_tab import HelpTab
from .about_tab import AboutTab
from .widgets.header import Header


#!/usr/bin/env python
"""
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

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

Program Name: Firewall Tester - Graphical Interface
    Description: This is the graphical interface and the main part of the firewall rule testing software.
    Author: Luiz Arthur Feitosa dos Santos - luiz.arthur.feitosa.santos@gmail.com / luizsantos@utfpr.edu.br
    License: GNU General Public License v3.0
    Version: 1.1 (Ported to PyQt5)
"""

class MainWindow(QMainWindow):
    """
    The main window of the application, which contains all UI elements.

    (R0902): This class has many instance attributes, which is acceptable for a
    main window that manages multiple tabs and core components.
    (R0903): This class has few public methods as it's the top-level widget.
    Its primary role is orchestration, handled by private methods.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FirewallTester")
        self.setGeometry(100, 100, 1200, 800)
        self._set_window_icon()

        self.config = self._load_app_config()
        docker_image = self.config.get("docker_image", "firewall_tester")
        self.container_manager = ContainerManager(docker_image)
        self.test_runner = TestRunner()

        # Initialize tab attributes
        self.tests_tab = None
        self.tab_widget = None
        self.hosts_tab = None
        self.firewall_rules_tab = None
        self.settings_tab = None
        self.help_tab = None
        self.about_tab = None

        self._setup_ui()

        self._update_all_hosts(is_initial_load=True)

    def _setup_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        app_header = Header("assets/logo.png", "FirewallTester")
        main_layout.addWidget(app_header)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line)

        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        self._create_tabs()

        bottom_layout = QHBoxLayout()
        btn_update_hosts = QPushButton("Refresh Hosts")
        btn_update_hosts.clicked.connect(self._update_all_hosts)
        btn_exit = QPushButton("Exit")
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

        all_hosts_data = self.container_manager.get_all_containers_data()
        print(f"Detected host data: {all_hosts_data}", file=sys.stderr)
        sys.stderr.flush()
        
        self.hosts_tab = HostsTab(self.container_manager, self.config)
        self.firewall_rules_tab = FirewallRulesTab(
            self.container_manager, hosts_for_combobox, self.config
        )
        self.tests_tab = FirewallTestsTab(self.test_runner, all_hosts_data, self.config)
        self.settings_tab = SettingsTab(self.config)
        self.help_tab = HelpTab()
        self.about_tab = AboutTab()

        self.tab_widget.addTab(self.tests_tab, "Firewall Tests")
        self.tab_widget.addTab(self.firewall_rules_tab, "Firewall Rules")
        self.tab_widget.addTab(self.hosts_tab, "Hosts")
        self.tab_widget.addTab(self.settings_tab, "Settings")
        self.tab_widget.addTab(self.help_tab, "Help")
        self.tab_widget.addTab(self.about_tab, "About")

    def _update_all_hosts(self, is_initial_load=False):
        all_hosts_data = self.container_manager.get_all_containers_data()
        hosts_for_combobox = self.container_manager.get_hosts_for_combobox()

        self.hosts_tab.update_hosts_display(all_hosts_data)
        self.firewall_rules_tab.update_hosts_list(hosts_for_combobox)
        self.tests_tab.update_hosts_list(all_hosts_data)

        if is_initial_load:
            if not all_hosts_data:
                QMessageBox.warning(
                    self,
                    "No Hosts Detected",
                    "The software did not detect any active hosts.\n\n"
                    "Make sure the GNS3 project is running (Play).\n"
                    "Also verify that the Docker image name in the 'Settings' tab is correct."
                )
            else:
                servers_on = 0
                
                QApplication.setOverrideCursor(Qt.WaitCursor)
                for host in all_hosts_data:
                    host_id = host['id']
                    _, status = self.container_manager.check_server_status(host_id)
                    if status == 'off':
                        success, _ = self.container_manager.start_server(host_id)
                        if success:
                            servers_on += 1
                
                QApplication.restoreOverrideCursor()

                if servers_on > 0:
                    self.hosts_tab.update_hosts_display(all_hosts_data)
                    self.statusBar().showMessage(
                        f"{len(all_hosts_data)} hosts detected. "
                        f"{servers_on} servers started.",
                        5000
                    )
                else:
                    self.statusBar().showMessage(
                        f"{len(all_hosts_data)} hosts detected and ready.",
                        5000
                    )
        elif not is_initial_load:
            QMessageBox.information(
                self,
                "Success",
                "Host information has been successfully updated."
            )


    def _set_window_icon(self):
        try:
            script_dir = pathlib.Path(__file__).parent.parent.resolve()
            icon_path = script_dir / "assets" / "logo.png"
            if icon_path.exists():
                self.setWindowIcon(QIcon(str(icon_path)))
        except FileNotFoundError as e:
            print(f"Error loading icon: {e}")

    def closeEvent(self, event):
        """
        Overrides the default close event to show a confirmation dialog.
        The name 'closeEvent' is a PyQt convention and must be kept.
        """
        reply = QMessageBox.question(
            self, "Confirmation",
            "Do you really want to exit the application?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()