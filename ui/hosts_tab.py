"""Defines the 'Hosts' tab for the Firewall Tester application."""

import pathlib
from functools import partial
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QDialog)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt
from .widgets.edit_ports import EditPortsDialog

from ui.widgets.hosts_cards import HostCardWidget

#TODO - Ajustar mudança de portas 
class HostsTab(QWidget):
    """
    A QWidget that displays a card for each available host (Docker container).
    It allows users to see the status of and interact with each host's server.
    (R0903: This class has few public methods as it's primarily a display
    widget updated by the main window, which is an acceptable design.)
    """
    def __init__(self, container_manager, config, parent=None):
        super().__init__(parent)
        self.container_manager = container_manager
        self.config = config
        self.hosts_cards = {}

        self._load_icons()
        self._setup_ui()

    def _load_icons(self):
        base_path = pathlib.Path(__file__).parent.parent.resolve()
        assets_path = base_path / "assets"
        
        power_on_path = assets_path / "power_on.png"
        power_off_path = assets_path / "power_off.png"

        if not power_on_path.exists() or not power_off_path.exists():
            f"WARNING: Icon files not found in '{assets_path}'. Buttons will appear blank."
            self.icons = {"on": QIcon(), "off": QIcon()}
        else:
            self.icons = {
                "on": QIcon(str(power_on_path)),
                "off": QIcon(str(power_off_path))
            }

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)

        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("Hosts (Network Containers):", font=QFont("Arial", 12)))
        top_layout.addStretch(1)
        
        btn_start_all = QPushButton("Start all")
        btn_start_all.clicked.connect(self._start_all_servers)
        
        btn_stop_all = QPushButton("Stop all")
        btn_stop_all.clicked.connect(self._stop_all_servers)
        
        top_layout.addWidget(btn_stop_all)
        top_layout.addWidget(btn_start_all)
        main_layout.addLayout(top_layout)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        main_layout.addWidget(scroll_area)

        content_widget = QWidget()
        self.layout_all_hosts = QVBoxLayout(content_widget)
        self.layout_all_hosts.setAlignment(Qt.AlignTop)
        scroll_area.setWidget(content_widget)

    def update_hosts_display(self, hosts_list):
        """Updates the display with the current list of hosts, adding or removing cards."""
        
        current_host_ids = {host['id'] for host in hosts_list}
        existing_host_ids = set(self.hosts_cards.keys())

        for host_id in existing_host_ids - current_host_ids:
            card_to_remove = self.hosts_cards.pop(host_id)
            card_to_remove.setParent(None)
            card_to_remove.deleteLater()

        for host_data in hosts_list:
            host_id = host_data['id']
            if host_id not in self.hosts_cards:
                new_card = HostCardWidget(host_data, self.icons)
                new_card.btn_toggle.clicked.connect(partial(self._toggle_server, host_id))
                edit_ports_handler = partial(self._edit_ports, host_id, host_data['hostname'])
                new_card.btn_edit_ports.clicked.connect(edit_ports_handler)

                self.layout_all_hosts.addWidget(new_card)
                self.hosts_cards[host_id] = new_card

            success, status = self.container_manager.check_server_status(host_id)
            if success:
                self.hosts_cards[host_id].update_status(status)
            else:
                self.hosts_cards[host_id].update_status("error")

    def _toggle_server(self, host_id):
        success, new_status = self.container_manager.toggle_server(host_id)
        if success and host_id in self.hosts_cards:
            self.hosts_cards[host_id].update_status(new_status)

    def _start_all_servers(self):
        print("Attempting to start all servers that are currently stopped...")
        for host_id in self.hosts_cards:
            success, status = self.container_manager.check_server_status(host_id)
            if success and status == 'off':
                self._toggle_server(host_id)

    def _stop_all_servers(self):
        print("Attempting to stop all servers that are currently running...")
        for host_id in self.hosts_cards:
            success, status = self.container_manager.check_server_status(host_id)
            if success and status == 'on':
                self._toggle_server(host_id)
                
    def _edit_ports(self, container_id, hostname):
        dialog = EditPortsDialog(self.container_manager, container_id, hostname, self.config)
        
        result = dialog.exec_()

        if result == QDialog.Accepted:
            print(f"Ports updated for {hostname}. Updating status.")
            if container_id in self.hosts_cards:
                success, status = self.container_manager.check_server_status(container_id)
                if success:
                    self.hosts_cards[container_id].update_status(status)