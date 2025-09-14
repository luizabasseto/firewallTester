import pathlib
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QScrollArea, QMessageBox)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt

from ui.widgets.hosts_cards import HostCardWidget # type: ignore

class HostsTab(QWidget):
    def __init__(self, container_manager, config, parent=None):
        super().__init__(parent)
        self.container_manager = container_manager
        self.config = config 
        self.hosts_cards = {}  
        
        self._load_icons()
        self._setup_ui()

    def _load_icons(self):
        base_path = pathlib.Path(__file__).parent.parent.parent.resolve()
        assets_path = base_path / "assets"
        
        self.icons = {
            "on": QIcon(str(assets_path / "power_on.png")),
            "off": QIcon(str(assets_path / "power_off.png"))
        }

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        
        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("Hosts (Containers de Rede):", font=QFont("Arial", 12)))
        top_layout.addStretch(1)
        btn_start_all = QPushButton("Ligar Servidores de Todos")
        btn_start_all.clicked.connect(self._start_all_servers)
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
                new_card.btn_toggle.clicked.connect(lambda _, cid=host_id: self._toggle_server(cid))
                new_card.btn_edit_ports.clicked.connect(lambda _, cid=host_id, hname=host_data['hostname']: self._edit_ports(cid, hname))
                
                self.layout_all_hosts.addWidget(new_card)
                self.host_cards[host_id] = new_card
            
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
        for host_id in self.hosts_cards.keys():
            self._toggle_server(host_id) 

    def _edit_ports(self, container_id, hostname):
        QMessageBox.information(self, "Não Implementado", f"A edição de portas para {hostname} ({container_id}) seria aberta aqui.")