"""Defines the HostCardWidget for displaying individual host information."""

from PyQt5.QtWidgets import (
    QGroupBox,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLabel,
    QPushButton,
)

class HostCardWidget(QGroupBox):
    """
    Displays host information and controls in a card-like widget.

    This widget presents details about a host, including interfaces and status,
    and provides controls for interaction.
    (R0903): This class has few public methods as it's primarily a display
    widget updated by its parent, which is an acceptable design.
    """

    def __init__(self, host_data, icons, parent=None):
        title = f"{host_data.get('hostname', 'N/A')} ({host_data.get('ip', 'N/A')})"
        super().__init__(title, parent)

        self.host_id = host_data.get("id")
        self.hostname = host_data.get("hostname")
        self.icons = icons

        main_layout = QVBoxLayout(self)
        info_layout = QFormLayout()
        status_layout = QHBoxLayout()
        main_layout.addLayout(info_layout)
        main_layout.addLayout(status_layout)

        info_layout.addRow("Container:", QLabel(f"{self.host_id} - {host_data.get('full_name', '')}"))
        
        info_layout.addRow("Interfaces:", QLabel("Nenhuma ou Desligada"))
        
        if interfaces := host_data.get('interfaces', []):
            for interface in interfaces:
                if_name = interface.get('nome', 'N/A')
                ips = ", ".join(interface.get('ips', [])) or "Sem IP"
                info_layout.addRow(f"Interface {if_name}:", QLabel(ips))
        else:
            info_layout.addRow("Interfaces:", QLabel("Nenhuma ou Desligada"))

        self.lbl_status = QLabel()
        self.btn_toggle = QPushButton()
        self.btn_toggle.setFixedSize(32, 32)

        self.btn_edit_ports = QPushButton("Editar Portas")

        status_layout.addWidget(self.lbl_status)
        status_layout.addStretch(1)
        status_layout.addWidget(self.btn_edit_ports)
        status_layout.addWidget(self.btn_toggle)

    def update_status(self, status):
        """Updates the displayed server status and toggle button icon.

        Args:
            status (str): The current status of the server, typically 'on' or 'off'.
        """
        self.lbl_status.setText(f"Server Status: <b>{status}</b>")
        icon = self.icons.get('on') if status == 'on' else self.icons.get('off')
        if icon:
            self.btn_toggle.setIcon(icon)