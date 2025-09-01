from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QPushButton, QScrollArea, QGroupBox, QMessageBox)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt

def create_hosts_tab(self):
    self.hosts_frame = QWidget()
    layout = QVBoxLayout(self.hosts_frame)
    self.notebook.addTab(self.hosts_frame, "Hosts")

    top_layout = QHBoxLayout()
    layout.addLayout(top_layout)

    top_layout.addWidget(QLabel("Network Containers Hosts:", font=QFont("Arial", 12)))
    top_layout.addStretch(1)
    btn_start_all = QPushButton("Turn on all servers")
    btn_start_all.clicked.connect(self.hosts_start_servers)
    top_layout.addWidget(btn_start_all)

    self.scroll_area_hosts = QScrollArea()
    self.scroll_area_hosts.setWidgetResizable(True)
    layout.addWidget(self.scroll_area_hosts)
    
    self.frame_all_hosts_content = QWidget()
    self.layout_all_hosts = QVBoxLayout(self.frame_all_hosts_content)
    self.layout_all_hosts.setAlignment(Qt.AlignTop)
    self.scroll_area_hosts.setWidget(self.frame_all_hosts_content)
    
    # Icons
    self.power_icon = QIcon("img/system-shutdown-symbolic.png")
    self.power_icon_off = QIcon("img/system-shutdown-symbolic-off.png")

def hosts_show_host_informations_in_host_tab(self):
    # Clear previous widgets
    for i in reversed(range(self.layout_all_hosts.count())): 
        self.layout_all_hosts.itemAt(i).widget().setParent(None)
    
    self.list_button_servers_onOff = []
    #cont = containers.getContainersByImageName()

    for host in cont:
        container_id = host["id"]
        hostname = host["hostname"]
        
        host_box = QGroupBox(f"{hostname}")
        host_layout = QVBoxLayout(host_box)
        self.layout_all_hosts.addWidget(host_box)

        info_layout = QFormLayout()
        host_layout.addLayout(info_layout)
        
        info_layout.addRow("Container:", QLabel(f"{host['id']} - {host['nome']}"))

        if not host['interfaces']:
            info_layout.addRow("Interfaces:", QLabel("None or Down"))
        else:
            for interface in host['interfaces']:
                if_name = interface['nome']
                ips = ", ".join(interface['ips']) if interface['ips'] else "No IP"
                info_layout.addRow(f"Interface {if_name}:", QLabel(ips))

        # Status and Controls
        status_layout = QHBoxLayout()
        host_layout.addLayout(status_layout)
        
        status = self.host_check_server_on_off(container_id)
        lbl_status = QLabel(f"Server Status: {status}")
        
        btn_toggle = QPushButton()
        btn_toggle.setIcon(self.power_icon if status == 'on' else self.power_icon_off)
        btn_toggle.setFixedSize(32, 32)
        btn_toggle.clicked.connect(lambda _, cid=container_id: self.host_toggle_server_and_button_between_onOff(cid))
        
        btn_edit_ports = QPushButton("Edit Ports")
        btn_edit_ports.clicked.connect(lambda _, cid=container_id, hname=hostname: self.edit_host_ports(cid, hname))

        status_layout.addWidget(lbl_status)
        status_layout.addStretch(1)
        status_layout.addWidget(btn_edit_ports)
        status_layout.addWidget(btn_toggle)

        self.list_button_servers_onOff.append({"id": container_id, "button": btn_toggle, "label": lbl_status})

def edit_host_ports(self, container_id, hostname):
    # This function would create a new QDialog to edit ports.
    # Implementation is similar to the Tkinter version but with QDialog, QTreeWidget, etc.
    QMessageBox.information(self, "Not Implemented", f"Port editing for {hostname} would open here.")