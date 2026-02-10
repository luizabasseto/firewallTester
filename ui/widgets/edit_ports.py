import os
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QAbstractItemView, QLineEdit, 
                             QComboBox, QPushButton, QMessageBox, QApplication)
from PyQt5.QtCore import Qt

class EditPortsDialog(QDialog):
    """
    Janela de diálogo para visualizar, adicionar e remover as portas que o
    servidor de um host específico irá escutar.
    """
    def __init__(self, container_manager, host_id, hostname, config, parent=None):
        super().__init__(parent)
        self.container_manager = container_manager
        self.host_id = host_id
        self.config = config 
        
        self.setWindowTitle(f"Edit Ports for {hostname}")
        self.setMinimumSize(400, 300)
        self.setLayout(QVBoxLayout())

        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Protocol", "Port"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.layout().addWidget(self.table)
        
        self._populate_table()

        controls_layout = QHBoxLayout()
        self.protocol_combo = QComboBox()
        self.protocol_combo.addItems(["TCP", "UDP"])
        self.port_input = QLineEdit()
        self.port_input.setPlaceholderText("Port (1-65535)")
        
        btn_add = QPushButton("Add")
        btn_add.clicked.connect(self._add_port)
        btn_delete = QPushButton("Remove selected")
        btn_delete.clicked.connect(self._delete_port)

        controls_layout.addWidget(self.protocol_combo)
        controls_layout.addWidget(self.port_input)
        controls_layout.addWidget(btn_add)
        controls_layout.addStretch()
        controls_layout.addWidget(btn_delete)
        self.layout().addLayout(controls_layout)

        buttons_layout = QHBoxLayout()
        btn_save = QPushButton("Save and restart server")
        btn_save.clicked.connect(self._save_changes)
        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)

        buttons_layout.addStretch()
        buttons_layout.addWidget(btn_cancel)
        buttons_layout.addWidget(btn_save)
        self.layout().addLayout(buttons_layout)

    def _populate_table(self):
        ports = self.container_manager.get_host_ports(self.host_id)
        self.table.setRowCount(len(ports))
        for row, (protocol, port) in enumerate(ports):
            self.table.setItem(row, 0, QTableWidgetItem(protocol))
            self.table.setItem(row, 1, QTableWidgetItem(port))
        self.table.resizeColumnsToContents()

    def _add_port(self):
        protocol = self.protocol_combo.currentText()
        port_str = self.port_input.text().strip()

        try:
            port = int(port_str)
            if not (1 <= port <= 65535):
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Invalid entry", "Please enter a valid port number (1-65535).")
            return

        row_count = self.table.rowCount()
        self.table.insertRow(row_count)
        self.table.setItem(row_count, 0, QTableWidgetItem(protocol))
        self.table.setItem(row_count, 1, QTableWidgetItem(str(port)))
        self.port_input.clear()

    def _delete_port(self):
        selected_row = self.table.currentRow()
        if selected_row >= 0:
            self.table.removeRow(selected_row)
        else:
            QMessageBox.warning(self, "No selection", "Please select a port from the table to remove.")
            
    def _save_changes(self):
        new_ports_list = []
        for row in range(self.table.rowCount()):
            protocol = self.table.item(row, 0).text()
            port = self.table.item(row, 1).text()
            new_ports_list.append((protocol, port))
            
        QApplication.setOverrideCursor(Qt.WaitCursor)
        
        local_path = self.config.get("server_ports_file")
        if not local_path:
            QMessageBox.critical(self, "Configuration error", "The path to 'server_ports_file' is not defined in config.json.")
            QApplication.restoreOverrideCursor()
            return

        success, message = self.container_manager.update_host_ports(
            self.host_id, new_ports_list, local_path
        )
        
        QApplication.restoreOverrideCursor()

        if success:
            QMessageBox.information(self, "Sucess", message)
            self.accept()
        else:
            QMessageBox.critical(self, "Error", message)