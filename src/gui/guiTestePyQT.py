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

import sys
import os
import json
import re
import threading
import webbrowser
import textwrap
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import containers


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

class Worker(QObject):
    """
    Worker thread for running tests without freezing the GUI.
    """
    progress = pyqtSignal(int, str)
    finished = pyqtSignal()
    update_item = pyqtSignal(QTreeWidgetItem, list, str)

    def __init__(self, tests, parent):
        super().__init__()
        self.tests = tests
        self.parent = parent

    def run(self):
        total_list = len(self.tests)
        for index, test_item in enumerate(self.tests):
            values = [test_item.text(i) for i in range(test_item.columnCount())]
            
            teste_id, container_id, src_ip, dst_ip, protocol, src_port, dst_port, expected, _, _, _ = values
            
            self.progress.emit(int(((index + 1) / total_list) * 100), f"Processing... {index + 1}/{total_list}")

            print(f"Executing test - Container ID:  {container_id}, Data: {src_ip} -> {dst_ip} [{protocol}] {src_port}:{dst_port} (Expected: {expected})")
            
            processed_dst_ip = self.parent.extract_destination_host(dst_ip)
            if processed_dst_ip is None:
                continue

            result_str = containers.run_client_test(container_id, processed_dst_ip, protocol.lower(), dst_port, "1", "2025", "0")

            try:
                result = json.loads(result_str)
                update_values, tag = self.parent.firewall_tests_analyse_results(expected, result, values)
                self.update_item.emit(test_item, update_values, tag)
            except (json.JSONDecodeError, TypeError) as e:
                print("Error processing the JSON received from the host:", e)
                # Optionally emit a signal to show an error
                continue
        
        self.finished.emit()


class FirewallGUI(QMainWindow):
    """
    Class to work with firewall tester interface, now using PyQt5.
    """

    SETTINGS_FILE = "conf/config.json"
    DEFAULT_SETTINGS = {
        "firewall_directory": "/etc/",
        "reset_rules_file": "conf/firewall_reset.sh",
        "firewall_rules_file": "conf/firewall.sh",
        "server_ports_file": "conf/ports.conf",
        "show_container_id": False,
        "docker_image": "firewall_tester",
        "include_mangle_table": False,
        "include_nat_table": True,
        "include_filter_table": True
    }

    def __init__(self):
        """
        Start firewall tester interface with some variables, methods and create default frames.
        """
        super().__init__()
        self.setWindowTitle("Firewall Tester")
        self.setGeometry(100, 100, 1200, 800)

        # Main widget and layout
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.main_layout = QVBoxLayout(self.main_widget)

        # Creating Notebook tab
        self.notebook = QTabWidget()
        self.main_layout.addWidget(self.notebook)

        # file name path
        self.save_file_path = None

        # buttons list from hosts
        self.list_button_servers_onOff = []

        # get data from containers and hosts
        self.containers_data = containers.extract_containerid_hostname_ips()
        self.container_hostname = containers.get_containerid_hostname()
        self.hosts = list(map(lambda x: x[1], self.container_hostname))

        # creating tabs
        self.create_settings_tab()
        self.create_firewall_tab()
        self.create_firewall_rules_tab()
        self.create_hosts_tab()
        self.create_about_tab()
        self.create_help_tab()
        
        # Frame under tabs
        frame_bottom = QWidget()
        self.layout_bottom = QHBoxLayout(frame_bottom)
        self.main_layout.addWidget(frame_bottom)

        self.button_update_host = QPushButton("Update Hosts")
        self.button_update_host.clicked.connect(self.hosts_update)
        self.layout_bottom.addWidget(self.button_update_host)
        
        self.layout_bottom.addStretch(1) # Add spacer

        self.button_quit = QPushButton("Exit")
        self.button_quit.clicked.connect(self.close)
        self.layout_bottom.addWidget(self.button_quit)
        
        # Initial data load and setup
        self.load_settings() # <-- CORREÇÃO: Movido para depois da criação de todas as abas
        self.hosts_show_host_informations_in_host_tab()
        self.hosts_start_servers()

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Confirmation', 'Do you really want to exit the program?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def load_settings(self):
        try:
            with open(self.SETTINGS_FILE, "r") as f:
                settings = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            settings = self.DEFAULT_SETTINGS.copy()
        
        self.config_firewall_dir_entry.setText(settings.get("firewall_directory", ""))
        self.config_firewall_reset_rules_entry.setText(settings.get("reset_rules_file", ""))
        self.config_firewall_rules_entry.setText(settings.get("firewall_rules_file", ""))
        self.config_server_ports_entry.setText(settings.get("server_ports_file", ""))
        self.config_show_container_id_check.setChecked(settings.get("show_container_id", False))
        self.config_docker_image_entry.setText(settings.get("docker_image", ""))
        self.config_include_filter_check.setChecked(settings.get("include_filter_table", True))
        self.config_include_nat_check.setChecked(settings.get("include_nat_table", True))
        self.config_include_mangle_check.setChecked(settings.get("include_mangle_table", False))
        
        # Apply settings immediately
        self.toggle_container_id_column()

    def save_settings(self):
        settings = {
            "firewall_directory": self.config_firewall_dir_entry.text(),
            "reset_rules_file": self.config_firewall_reset_rules_entry.text(),
            "firewall_rules_file": self.config_firewall_rules_entry.text(),
            "server_ports_file": self.config_server_ports_entry.text(),
            "show_container_id": self.config_show_container_id_check.isChecked(),
            "docker_image": self.config_docker_image_entry.text(),
            "include_filter_table": self.config_include_filter_check.isChecked(),
            "include_nat_table": self.config_include_nat_check.isChecked(),
            "include_mangle_table": self.config_include_mangle_check.isChecked()
        }
        with open(self.SETTINGS_FILE, "w") as f:
            json.dump(settings, f, indent=4)
        
        self.toggle_container_id_column()
        QMessageBox.information(self, "Success", "Settings saved successfully.")

    def toggle_container_id_column(self):
        is_visible = self.config_show_container_id_check.isChecked()
        self.tree.setColumnHidden(1, not is_visible) # Column index 1 is "Container ID"

    def restore_default_settings(self):
        reply = QMessageBox.question(self, 'Restore Defaults', 'Are you sure you want to restore default settings?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.DEFAULT_SETTINGS = self.__class__.DEFAULT_SETTINGS 
            with open(self.SETTINGS_FILE, "w") as f:
                 json.dump(self.DEFAULT_SETTINGS, f, indent=4)
            self.load_settings()

    def create_settings_tab(self):
        self.config_frame = QWidget()
        layout = QVBoxLayout(self.config_frame)
        self.notebook.addTab(self.config_frame, "Settings")

        title = QLabel("Software Settings")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        layout.addWidget(form_widget)

        self.config_firewall_dir_entry = QLineEdit()
        self.config_firewall_reset_rules_entry = QLineEdit()
        self.config_firewall_rules_entry = QLineEdit()
        self.config_server_ports_entry = QLineEdit()
        self.config_docker_image_entry = QLineEdit()
        
        self.config_show_container_id_check = QCheckBox("Show Container ID Column")
        self.config_include_filter_check = QCheckBox("Include Filter Table in Firewall Listing")
        self.config_include_nat_check = QCheckBox("Include NAT Table in Firewall Listing")
        self.config_include_mangle_check = QCheckBox("Include Mangle Table in Firewall Listing")

        form_layout.addRow("Firewall Directory in Containers:", self.config_firewall_dir_entry)
        form_layout.addRow("Reset Rules File:", self.config_firewall_reset_rules_entry)
        form_layout.addRow("Firewall Rules File:", self.config_firewall_rules_entry)
        form_layout.addRow("Server Ports File:", self.config_server_ports_entry)
        form_layout.addRow("Docker Image Name:", self.config_docker_image_entry)
        form_layout.addRow(self.config_show_container_id_check)
        form_layout.addRow(self.config_include_filter_check)
        form_layout.addRow(self.config_include_nat_check)
        form_layout.addRow(self.config_include_mangle_check)
        
        buttons_layout = QHBoxLayout()
        layout.addLayout(buttons_layout)

        save_button = QPushButton("Save Settings")
        save_button.clicked.connect(self.save_settings)
        restore_button = QPushButton("Restore Defaults")
        restore_button.clicked.connect(self.restore_default_settings)
        
        buttons_layout.addStretch(1)
        buttons_layout.addWidget(save_button)
        buttons_layout.addWidget(restore_button)
        buttons_layout.addStretch(1)

        layout.addStretch(1)

    def create_about_tab(self):
        self.about_frame = QWidget()
        layout = QVBoxLayout(self.about_frame)
        layout.setAlignment(Qt.AlignTop)
        self.notebook.addTab(self.about_frame, "About")

        lbl_title = QLabel("About the Software")
        lbl_title.setFont(QFont("Arial", 14, QFont.Bold))
        lbl_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_title)

        description = "This software was developed with the goal of strengthening network security through practical and efficient firewall testing. More than just a testing tool, it stands out as a valuable educational resource, designed to simplify and enhance the learning process about firewalls. Through an intuitive and interactive interface, students can visualize and experiment with the creation and application of firewall rules, making it easier to understand complex concepts and promoting deeper and more effective learning."
        
        lbl_description = QLabel(textwrap.fill(description, width=100))
        lbl_description.setWordWrap(True)
        lbl_description.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_description)
        
        # Using a QFormLayout for structured information
        info_layout = QFormLayout()
        info_layout.setContentsMargins(0, 20, 0, 20)
        info_layout.setAlignment(Qt.AlignCenter)
        layout.addLayout(info_layout)
        
        lbl_developer_name = QLabel("Prof. Luiz Arthur Feitosa dos Santos")
        lbl_developer_name.setFont(QFont("Arial", 12, QFont.Bold))
        info_layout.addRow("<b>Developer:</b>", lbl_developer_name)

        lbl_email = QLabel("<a href='mailto:luiz.arthur.feitosa.santos@gmail.com'>luiz.arthur.feitosa.santos@gmail.com</a>")
        lbl_email.setOpenExternalLinks(True)
        info_layout.addRow("<b>Email:</b>", lbl_email)

        lbl_institution = QLabel("UTFPR-CM")
        lbl_institution.setFont(QFont("Arial", 12, QFont.Bold))
        info_layout.addRow("<b>Institution:</b>", lbl_institution)

        lbl_project_link = QLabel("<a href='https://github.com/luizsantos/firewallTester'>https://github.com/luizsantos/firewallTester</a>")
        lbl_project_link.setOpenExternalLinks(True)
        info_layout.addRow("<b>Project Link:</b>", lbl_project_link)
        
        lbl_license = QLabel("<a href='https://www.gnu.org/licenses/gpl-3.0.html'>GNU GPL v3</a>")
        lbl_license.setOpenExternalLinks(True)
        info_layout.addRow("<b>License:</b>", lbl_license)

        btn_help = QPushButton("Help")
        btn_help.clicked.connect(self.open_help)
        
        help_layout = QHBoxLayout()
        help_layout.addStretch(1)
        help_layout.addWidget(btn_help)
        help_layout.addStretch(1)
        layout.addLayout(help_layout)

        layout.addStretch(1)

    def open_help(self):
        webbrowser.open_new_tab("https://github.com/luizsantos/firewallTester")

    def create_help_tab(self):
        self.help_frame = QWidget()
        main_layout = QVBoxLayout(self.help_frame)
        main_layout.setAlignment(Qt.AlignTop)
        self.notebook.addTab(self.help_frame, "Help") 

        help_text_browser = QTextBrowser()
        help_text_browser.setOpenExternalLinks(True) 
        help_content = """
        <html>
        <head>
            <style>
                h1 { color: #2c3e50; }
                h2 { color: #34495e; border-bottom: 1px solid #ccc; }
                p  { font-size: 14px; line-height: 1.6; }
                ul { list-style-type: disc; margin-left: 20px; }
                li { margin-bottom: 10px; }
                code { background-color: #f4f4f4; padding: 2px 5px; border-radius: 4px; font-family: monospace; }
            </style>
        </head>
        <body>
            <h1>Como Usar o Firewall Tester</h1>
            <p>
                Esta ferramenta foi projetada para automatizar testes de regras de firewall
                em um ambiente de laboratório usando GNS3 e Docker.
            </p>

            <h2> Guia de Início Rápido</h2>
            <ul>
                <li>
                    <b>Passo 1: Prepare o Ambiente</b><br>
                    Certifique-se de que sua topologia no GNS3 está rodando, com os containers Docker (hosts) iniciados.
                </li>
                <li>
                    <b>Passo 2: Conecte a Ferramenta</b><br>
                    Clique no botão <b>"Atualizar Hosts"</b> na aba principal. A ferramenta irá detectar
                    automaticamente todos os containers em execução.
                </li>
                <li>
                    <b>Passo 3: Edite as Regras de Firewall</b><br>
                    Selecione um host que funcionará como firewall na aba "Firewall". Utilize o editor
                    para carregar, modificar e aplicar conjuntos de regras <code>iptables</code>.
                </li>
                <li>
                    <b>Passo 4: Crie os Testes</b><br>
                    Vá para a aba "Testes de Firewall", defina os testes de conectividade desejados
                    (ex: de <code>hostA</code> para <code>hostB</code> na porta <code>80/tcp</code>) e adicione-os à lista.
                </li>
                <li>
                    <b>Passo 5: Execute e Analise</b><br>
                    Clique em <b>"Executar Testes Selecionados"</b>. Os resultados (Sucesso/Falha) serão exibidos
                    na tabela, ajudando a validar suas regras de firewall.
                </li>
            </ul>
        </body>
        </html>
        """
        help_text_browser.setHtml(help_content)
        main_layout.addWidget(help_text_browser)

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
        cont = containers.getContainersByImageName()

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

    def create_firewall_rules_tab(self):
        self.firewall_rules_frame = QWidget()
        layout = QVBoxLayout(self.firewall_rules_frame)
        self.notebook.addTab(self.firewall_rules_frame, "Firewall Rules")

        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("Edit firewall rules on host:"))
        self.combobox_firewall_rules_host = QComboBox()
        self.combobox_firewall_rules_host.addItems(self.hosts)
        self.combobox_firewall_rules_host.setCurrentIndex(-1)
        self.combobox_firewall_rules_host.currentIndexChanged.connect(self.selected_host_on_combobox_tab_firewall_rules)
        top_layout.addWidget(self.combobox_firewall_rules_host)
        top_layout.addStretch(1)
        layout.addLayout(top_layout)

        # Rules editor
        rules_box = QGroupBox("Rules to be applied to the firewall")
        rules_layout = QVBoxLayout(rules_box)
        self.text_firewall_rules = QTextEdit()
        self.text_firewall_rules.setFont(QFont("Monospace"))
        rules_layout.addWidget(self.text_firewall_rules)
        self.reset_firewall_check = QCheckBox("Automatically reset firewall rules")
        rules_layout.addWidget(self.reset_firewall_check)
        layout.addWidget(rules_box)

        # Output viewer
        self.output_firewall_rules_box = QGroupBox("Output")
        output_layout = QVBoxLayout(self.output_firewall_rules_box)
        self.text_active_firewall_rules = QTextEdit()
        self.text_active_firewall_rules.setReadOnly(True)
        self.text_active_firewall_rules.setFont(QFont("Monospace"))
        output_layout.addWidget(self.text_active_firewall_rules)
        self.button_list_firewall_rules = QPushButton("List firewall rules")
        self.button_list_firewall_rules.clicked.connect(self.list_firewall_rules_on_output)
        output_layout.addWidget(self.button_list_firewall_rules, alignment=Qt.AlignCenter)
        layout.addWidget(self.output_firewall_rules_box)

        # Main buttons
        buttons_layout = QHBoxLayout()
        self.button_retrieve_firewall_rules = QPushButton("Retrieve firewall rules")
        self.button_retrieve_firewall_rules.clicked.connect(self.load_firewall_rules)
        self.button_deploy_firewall_rules = QPushButton("Deploy firewall rules")
        self.button_deploy_firewall_rules.clicked.connect(self.apply_firewall_rules)
        button_show_output = QPushButton("Toggle Output")
        button_show_output.clicked.connect(lambda: self.output_firewall_rules_box.setVisible(not self.output_firewall_rules_box.isVisible()))
        
        buttons_layout.addWidget(self.button_retrieve_firewall_rules)
        buttons_layout.addWidget(self.button_deploy_firewall_rules)
        buttons_layout.addStretch(1)
        buttons_layout.addWidget(button_show_output)
        layout.addLayout(buttons_layout)
        
        self.selected_host_on_combobox_tab_firewall_rules() # To set initial button states

    def selected_host_on_combobox_tab_firewall_rules(self):
        selected_index = self.combobox_firewall_rules_host.currentIndex()
        is_host_selected = selected_index != -1
        
        self.button_retrieve_firewall_rules.setEnabled(is_host_selected)
        self.button_deploy_firewall_rules.setEnabled(is_host_selected)
        self.button_list_firewall_rules.setEnabled(is_host_selected)
        
        if is_host_selected:
            self.container_id_host_regras_firewall = self.container_hostname[selected_index]
        else:
            self.container_id_host_regras_firewall = None

    def list_firewall_rules_on_output(self):
        if not self.container_id_host_regras_firewall: return
        
        self.text_active_firewall_rules.clear()
        host_id, host_name = self.container_id_host_regras_firewall
        
        output_text = ""
        
        if self.config_include_mangle_check.isChecked():
            command = ["docker", "exec", host_id, "iptables", "-L", "-n", "-t", "mangle"]
            result = containers.run_command(command)
            output_text += f"<b>&bull; Mangle Rules on {host_name}:</b><br>{result.stdout.replace(os.linesep, '<br>')}<br><br>"
            
        if self.config_include_nat_check.isChecked():
            command = ["docker", "exec", host_id, "iptables", "-L", "-n", "-t", "nat"]
            result = containers.run_command(command)
            output_text += f"<b>&bull; NAT Rules on {host_name}:</b><br>{result.stdout.replace(os.linesep, '<br>')}<br><br>"

        if self.config_include_filter_check.isChecked():
            command = ["docker", "exec", host_id, "iptables", "-L", "-n"]
            result = containers.run_command(command)
            output_text += f"<b>&bull; Filter Rules on {host_name}:</b><br>{result.stdout.replace(os.linesep, '<br>')}<br><br>"
        
        if not output_text:
            output_text = "All firewall rule tables are disabled for listing in the settings tab."
            
        self.text_active_firewall_rules.setHtml(output_text)

    def load_firewall_rules(self):
        if not self.container_id_host_regras_firewall: return
        
        reply = QMessageBox.question(self, "Confirmation", "This will overwrite the existing rules in the interface. Continue?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            host_id, _ = self.container_id_host_regras_firewall
            file = self.config_firewall_dir_entry.text() + "/firewall.sh"
            command = ["docker", "exec", host_id, "cat", file]
            result = containers.run_command(command)
            self.text_firewall_rules.setPlainText(result.stdout)

    def apply_firewall_rules(self):
        if not self.container_id_host_regras_firewall: return

        print(f"Apply rules on the firewall of host {self.container_id_host_regras_firewall[1]}")
        rules = self.text_firewall_rules.toPlainText()
        file_rules_path = self.config_firewall_rules_entry.text()
        
        with open(file_rules_path, "w", encoding="utf-8") as file_name:
            file_name.write(rules)

        if self.reset_firewall_check.isChecked():
            self.send_to_host_file_to_execute_firewall_rules(self.config_firewall_reset_rules_entry.text(), True)
        
        self.send_to_host_file_to_execute_firewall_rules(file_rules_path, False)
        
        if self.reset_firewall_check.isChecked():
            self.text_active_firewall_rules.append("\n<b>&gt;&gt;Warning!&lt;&lt;</b> The firewall rules were reset via the interface. This SHOULD be in your script!")
    
    def send_to_host_file_to_execute_firewall_rules(self, file_rules_path, is_reset):
        if not self.container_id_host_regras_firewall: return
        host_id, host_name = self.container_id_host_regras_firewall

        if is_reset:
            container_path = self.config_firewall_dir_entry.text() + "/firewall_reset.sh"
            command_to_run = ["docker", "exec", host_id, "sh", container_path]
        else:
            container_path = self.config_firewall_dir_entry.text() + "/firewall.sh"
            command_to_run = ["docker", "exec", host_id, "sh", container_path]

        containers.copy_host2container(host_id, file_rules_path, container_path)
        result = containers.run_command(command_to_run)
        
        self.text_active_firewall_rules.clear()
        if result.stderr:
            self.text_active_firewall_rules.setHtml(f"<b>* Error applying firewall rules on host {host_name}:</b><br><pre>{result.stderr}</pre>")
            QMessageBox.warning(self, "Warning", "Something went wrong while executing the rules, check the output!")
        else:
            self.list_firewall_rules_on_output()
            self.text_active_firewall_rules.append(f"\n<b>* Firewall status on host {host_name} after rules have been applied.</b>")

    def create_firewall_tab(self):
        self.firewall_frame = QWidget()
        layout = QVBoxLayout(self.firewall_frame)
        self.notebook.addTab(self.firewall_frame, "Firewall Test")
        
        # --- Input Frame ---
        input_box = QGroupBox("New Test")
        input_layout = QGridLayout(input_box)
        layout.addWidget(input_box)

        self.hosts_display = [f"{c['hostname']} ({c['ip']})" for c in self.containers_data] if self.containers_data else ["No hosts found"]

        self.src_ip_combo = QComboBox()
        self.src_ip_combo.addItems(self.hosts_display)
        self.dst_ip_combo = QComboBox()
        self.dst_ip_combo.addItems(self.hosts_display)
        self.dst_ip_combo.setEditable(True)
        if len(self.hosts_display) > 1:
            self.dst_ip_combo.setCurrentIndex(1)
        
        self.protocol_combo = QComboBox()
        self.protocol_combo.addItems(["TCP", "UDP", "ICMP"])
        
        self.src_port_entry = QLineEdit("*")
        self.src_port_entry.setEnabled(False) # As per original code
        self.dst_port_entry = QLineEdit("80")

        self.expected_yes_radio = QRadioButton("Yes")
        self.expected_no_radio = QRadioButton("No")
        self.expected_yes_radio.setChecked(True)
        expected_layout = QHBoxLayout()
        expected_layout.addWidget(self.expected_yes_radio)
        expected_layout.addWidget(self.expected_no_radio)

        input_layout.addWidget(QLabel("Source IP:"), 0, 0)
        input_layout.addWidget(self.src_ip_combo, 1, 0)
        input_layout.addWidget(QLabel("Destination IP:"), 0, 1)
        input_layout.addWidget(self.dst_ip_combo, 1, 1)
        input_layout.addWidget(QLabel("Protocol:"), 0, 2)
        input_layout.addWidget(self.protocol_combo, 1, 2)
        input_layout.addWidget(QLabel("Src Port:"), 0, 3)
        input_layout.addWidget(self.src_port_entry, 1, 3)
        input_layout.addWidget(QLabel("Dst Port:"), 0, 4)
        input_layout.addWidget(self.dst_port_entry, 1, 4)
        input_layout.addWidget(QLabel("Expected Success?"), 0, 5)
        input_layout.addLayout(expected_layout, 1, 5)

        # --- Test Control Buttons ---
        buttons_layout = QHBoxLayout()
        layout.addLayout(buttons_layout)
        self.button_tree_add = QPushButton("Add")
        self.button_tree_edit = QPushButton("Edit")
        self.button_tree_del = QPushButton("Delete")
        self.button_tree_test = QPushButton("Test Line")
        self.button_tree_test_all = QPushButton("Test All")

        buttons_layout.addStretch(1)
        buttons_layout.addWidget(self.button_tree_add)
        buttons_layout.addWidget(self.button_tree_edit)
        buttons_layout.addWidget(self.button_tree_del)
        buttons_layout.addWidget(self.button_tree_test)
        buttons_layout.addWidget(self.button_tree_test_all)
        buttons_layout.addStretch(1)

        # --- Tree Widget for Tests ---
        self.tree = QTreeWidget()
        self.tree.setSelectionMode(QAbstractItemView.SingleSelection)
        header_labels = ["#", "Container ID", "Source", "Destination", "Protocol", "Src Port", "Dst Port", "Expected", "Result", "Network Flow", "Network Data"]
        self.tree.setHeaderLabels(header_labels)
        layout.addWidget(self.tree)
        
        # Column widths and settings
        self.tree.setColumnWidth(0, 40)
        self.tree.setColumnWidth(1, 130)
        self.tree.setColumnWidth(2, 250)
        self.tree.setColumnWidth(3, 250)
        self.tree.header().setSectionResizeMode(len(header_labels) - 1, QHeaderView.Stretch)

        # Connect signals
        self.button_tree_add.clicked.connect(self.firewall_test_tree_add_line_test)
        self.button_tree_edit.clicked.connect(self.firewall_test_tree_edit_line_test)
        self.button_tree_del.clicked.connect(self.firewall_test_tree_delete_line_test)
        self.button_tree_test.clicked.connect(self.firewall_tests_run_test_line)
        self.button_tree_test_all.clicked.connect(self.firewall_tests_popup_for_run_all_tests_using_threads)
        self.tree.itemSelectionChanged.connect(self.firewall_test_tree_select_line_test)
        self.tree.itemDoubleClicked.connect(self.firewall_test_tree_double_click_line_test)

        self.firewall_tests_buttons_set_normal_state()
        self.toggle_container_id_column() # Set initial visibility

        # --- Legend ---
        legend_box = QGroupBox("Legend")
        legend_layout = QHBoxLayout(legend_box)
        layout.addWidget(legend_box)
        
        def add_legend_item(color, text):
            label_color = QLabel()
            label_color.setFixedSize(16, 16)
            label_color.setStyleSheet(f"background-color: {color}; border: 1px solid black;")
            legend_layout.addWidget(label_color)
            legend_layout.addWidget(QLabel(text))
            legend_layout.addSpacing(15)

        add_legend_item("lightgreen", "Test passed (flow allowed/accepted)")
        add_legend_item("lightblue", "Test passed (flow blocked/dropped)")
        add_legend_item("salmon", "Test failed")
        add_legend_item("yellow", "Error (e.g., config error, host down)")
        legend_layout.addStretch(1)

        # --- Save/Load Buttons ---
        file_buttons_layout = QHBoxLayout()
        layout.addLayout(file_buttons_layout)
        self.button_save_tests = QPushButton("Save Tests")
        self.button_save_tests_as = QPushButton("Save Tests As")
        self.button_load_tests = QPushButton("Open Tests")
        
        self.button_save_tests.clicked.connect(self.firewall_tests_save_tests)
        self.button_save_tests_as.clicked.connect(self.firewall_tests_save_tests_as)
        self.button_load_tests.clicked.connect(self.firewall_tests_open_test_file)

        file_buttons_layout.addStretch(1)
        file_buttons_layout.addWidget(self.button_save_tests)
        file_buttons_layout.addWidget(self.button_save_tests_as)
        file_buttons_layout.addWidget(self.button_load_tests)
        file_buttons_layout.addStretch(1)
    
    def firewall_test_tree_select_line_test(self):
        selected_items = self.tree.selectedItems()
        if not selected_items:
            self.button_tree_edit.setEnabled(False)
            self.button_tree_del.setEnabled(False)
            self.button_tree_test.setEnabled(False)
            return

        item = selected_items[0]
        self.src_ip_combo.setCurrentText(item.text(2))
        self.dst_ip_combo.setCurrentText(item.text(3))
        self.protocol_combo.setCurrentText(item.text(4))
        self.src_port_entry.setText(item.text(5))
        self.dst_port_entry.setText(item.text(6))
        
        if item.text(7).lower() == "yes":
            self.expected_yes_radio.setChecked(True)
        else:
            self.expected_no_radio.setChecked(True)

        self.button_tree_edit.setEnabled(True)
        self.button_tree_del.setEnabled(True)
        self.button_tree_test.setEnabled(True)

    def firewall_test_tree_double_click_line_test(self, item, column):
        self.firewall_test_tree_select_line_test()
        self.firewall_tests_buttons_set_editing_state()
    
    def firewall_test_tree_add_line_test(self):
        if self.firewall_tests_validate_entrys() != 0: return

        src_ip = self.src_ip_combo.currentText()
        dst_ip = self.dst_ip_combo.currentText()
        protocol = self.protocol_combo.currentText()
        src_port = self.src_port_entry.text()
        dst_port = self.dst_port_entry.text()
        expected = "yes" if self.expected_yes_radio.isChecked() else "no"

        selected_index = self.src_ip_combo.currentIndex()
        container_id = self.containers_data[selected_index]["id"] if selected_index >= 0 else "N/A"
        
        row_index = self.tree.topLevelItemCount() + 1
        
        values = [str(row_index), container_id, src_ip, dst_ip, protocol, src_port, dst_port, expected, "-", "", ""]
        
        # Check for duplicates
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            existing_values = [item.text(j) for j in range(2, 8)] # Columns from Source to Expected
            if values[2:8] == existing_values:
                QMessageBox.warning(self, "Warning", "This test entry already exists.")
                return

        new_item = QTreeWidgetItem(values)
        self.tree.addTopLevelItem(new_item)
        self.firewall_tests_buttons_set_normal_state()
    
    def firewall_test_tree_edit_line_test(self):
        selected_items = self.tree.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Select an item to edit.")
            return

        if self.firewall_tests_validate_entrys() != 0: return
        
        item = selected_items[0]
        
        # Gather new values
        src_ip = self.src_ip_combo.currentText()
        dst_ip = self.dst_ip_combo.currentText()
        protocol = self.protocol_combo.currentText()
        src_port = self.src_port_entry.text()
        dst_port = self.dst_port_entry.text()
        expected = "yes" if self.expected_yes_radio.isChecked() else "no"
        
        selected_index = self.src_ip_combo.currentIndex()
        container_id = self.containers_data[selected_index]["id"] if selected_index >= 0 else "N/A"
        
        # Update item
        item.setText(1, container_id)
        item.setText(2, src_ip)
        item.setText(3, dst_ip)
        item.setText(4, protocol)
        item.setText(5, src_port)
        item.setText(6, dst_port)
        item.setText(7, expected)
        item.setText(8, "-") # Reset result
        item.setText(9, "")
        item.setText(10, "")
        
        # Reset color
        for i in range(item.columnCount()):
            item.setBackground(i, QBrush(QColor("transparent")))
            
        self.firewall_tests_buttons_set_normal_state()
    
    def firewall_test_tree_delete_line_test(self):
        selected_items = self.tree.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Select an item to delete.")
            return
        
        reply = QMessageBox.question(self, "Delete Test", "Are you sure you want to delete the selected test?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            item = selected_items[0]
            self.tree.takeTopLevelItem(self.tree.indexOfTopLevelItem(item))
            self.firewall_tests_buttons_set_normal_state()
    
    def firewall_tests_validate_entrys(self):
        if not self.dst_port_entry.text().isdigit():
            QMessageBox.warning(self, "Invalid Input", "The destination port must be a number between 1-65535.")
            return -1
        try:
            port = int(self.dst_port_entry.text())
            if not (1 <= port <= 65535):
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "The destination port must be a number between 1-65535.")
            return -1
        
        # Other validations from original code can be added here
        return 0

    def firewall_tests_buttons_set_normal_state(self):
        self.tree.clearSelection()
        self.button_tree_add.setEnabled(True)
        self.button_tree_edit.setEnabled(False)
        self.button_tree_del.setEnabled(False)
        self.button_tree_test.setEnabled(False)
        self.button_tree_edit.setText("Edit")
        is_empty = self.tree.topLevelItemCount() == 0
        self.button_tree_test_all.setEnabled(not is_empty)
    
    def firewall_tests_buttons_set_editing_state(self):
        self.button_tree_add.setEnabled(False)
        self.button_tree_edit.setEnabled(True)
        self.button_tree_del.setEnabled(True)
        self.button_tree_test.setEnabled(False)
        self.button_tree_test_all.setEnabled(False)
        self.button_tree_edit.setText("Save Edit")

    def extract_destination_host(self, destination):
        # This logic remains the same
        ip_match = re.search(r'\((\d+\.\d+\.\d+\.\d+)\)', destination)
        if ip_match:
            return ip_match.group(1)
        
        # Check for plain IP or domain
        if self.validate_ip_or_domain(destination):
            return destination

        print(f"\033[33mCould not extract the destination IP/domain: {destination}\033[0m")
        return None

    def validate_ip_or_domain(self, value):
        regex_ip = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
        regex_domain = r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(regex_ip, value) or re.match(regex_domain, value))

    def firewall_tests_run_test_line(self):
        selected_items = self.tree.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a test to run.")
            return

        item = selected_items[0]
        values = [item.text(i) for i in range(item.columnCount())]
        _, container_id, _, dst_ip, protocol, _, dst_port, expected, _, _, _ = values
        
        processed_dst_ip = self.extract_destination_host(dst_ip)
        if processed_dst_ip is None: return

        result_str = containers.run_client_test(container_id, processed_dst_ip, protocol.lower(), dst_port, "1", "2025", "0")
        
        try:
            result = json.loads(result_str)
            self.firewall_tests_analyse_and_update_tree(expected, result, values, item)
        except (json.JSONDecodeError, TypeError) as e:
            QMessageBox.critical(self, "Error", f"Could not process response from host: {e}")
            return
        
        self.tree.clearSelection()

    def firewall_tests_analyse_and_update_tree(self, expected, result, values, item):
        update_values, tag = self.firewall_tests_analyse_results(expected, result, values)
        
        # Update item text
        for i, value in enumerate(update_values):
            item.setText(i, str(value))
        
        # Update item color
        color_map = {
            "yes": "lightgreen",
            "yesFail": "lightblue",
            "no": "salmon",
            "error": "yellow"
        }
        color = QColor(color_map.get(tag, "transparent"))
        for i in range(item.columnCount()):
            item.setBackground(i, QBrush(color))

    def firewall_tests_analyse_results(self, expected, result, values):
        update_values = list(values)
        tag = None

        # Logic is copied and adapted from the original function
        if result.get("server_response"):
            update_values[9] = "Sent/Received"
            update_values[8] = "Pass"
        else:
            update_values[9] = "Sent"
            update_values[8] = "Fail"

        network_data = f"{result.get('client_ip', '')}:{result.get('client_port', '')} -> {result.get('server_ip', '')}:{result.get('server_port', '')} ({result.get('protocol', '')}) - Server Response? {result.get('server_response', '')} - Status: {result.get('status_msg', '')}"
        update_values[10] = network_data

        if result.get("status") != '0':
            update_values[8] = "ERROR"
            update_values[9] = "Not Sent"
            tag = "error"
        elif result.get("server_response") and expected == "yes":
            tag = "yes"
        elif not result.get("server_response") and expected == "no":
            tag = "yesFail"
        else:
            tag = "no"

        if "dnat" in result:
            dnat_data = result["dnat"]
            network_data = f"{result.get('client_ip', '')}:{result.get('client_port', '')} -> {dnat_data['ip']}:{dnat_data['port']} ({result.get('protocol', '')}) - Server Response? {result.get('server_response', '')} - Status: {result.get('status_msg', '')}"
            update_values[10] = network_data
            update_values[9] = "Sent/Received (DNAT)"
            
        return update_values, tag
    
    def firewall_tests_popup_for_run_all_tests_using_threads(self):
        self.progress_dialog = QProgressDialog("Running tests...", "Cancel", 0, 100, self)
        self.progress_dialog.setWindowTitle("Processing")
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.show()

        tests_to_run = [self.tree.topLevelItem(i) for i in range(self.tree.topLevelItemCount())]
        
        self.thread = QThread()
        self.worker = Worker(tests_to_run, self)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(lambda p, msg: (self.progress_dialog.setValue(p), self.progress_dialog.setLabelText(msg)))
        self.worker.update_item.connect(lambda item, values, tag: self.firewall_tests_analyse_and_update_tree(values[7], json.loads(containers.run_client_test(values[1], self.extract_destination_host(values[3]), values[4].lower(), values[6], "1", "2025", "0")), values, item))

        self.thread.finished.connect(lambda: (
            self.progress_dialog.setValue(100),
            QMessageBox.information(self, "Complete", "All tests have been executed."),
            self.progress_dialog.close()
        ))
        
        self.progress_dialog.canceled.connect(self.thread.quit)

        self.thread.start()

    def hosts_start_servers(self):
        for container in self.containers_data:
            containers.start_server(container["id"])
        self.update_server_status_icons()

    def update_server_status_icons(self):
        for item in self.list_button_servers_onOff:
            status = self.host_check_server_on_off(item['id'])
            item['label'].setText(f"Server Status: {status}")
            item['button'].setIcon(self.power_icon if status == 'on' else self.power_icon_off)

    def hosts_update(self):
        self.containers_data = containers.extract_containerid_hostname_ips()
        self.container_hostname = containers.get_containerid_hostname()
        self.hosts = list(map(lambda x: x[1], self.container_hostname))
        
        # Update hosts tab
        self.hosts_show_host_informations_in_host_tab()
        
        # Update firewall rules tab combobox
        self.combobox_firewall_rules_host.clear()
        self.combobox_firewall_rules_host.addItems(self.hosts)
        self.combobox_firewall_rules_host.setCurrentIndex(-1)
        
        # Update firewall test tab comboboxes
        self.hosts_display = [f"{c['hostname']} ({c['ip']})" for c in self.containers_data]
        self.src_ip_combo.clear()
        self.src_ip_combo.addItems(self.hosts_display)
        self.dst_ip_combo.clear()
        self.dst_ip_combo.addItems(self.hosts_display)
        
        QMessageBox.information(self, "Success", "Host information updated.")

    def host_check_server_on_off(self, container_id):
        cmd = f'docker exec {container_id} ps ax | grep "/usr/local/bin/python ./server.py" | grep -v grep'
        result = containers.run_command_shell(cmd)
        return "on" if result else "off"

    def host_toggle_server_and_button_between_onOff(self, container_id):
        status = self.host_check_server_on_off(container_id)
        if status == 'on':
            containers.stop_server(container_id)
        else:
            containers.start_server(container_id)
        self.update_server_status_icons()

    def firewall_tests_save_tests_as(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Test File", "", "JSON Files (*.json);;All Files (*)")
        if file_path:
            self.save_file_path = file_path
            self.firewall_tests_save_tests()
            
    def firewall_tests_save_tests(self):
        if not self.save_file_path:
            self.firewall_tests_save_tests_as()
            return

        tests_data = []
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            values = [item.text(j) for j in range(item.columnCount())]
            tests_data.append({
                "teste_id": values[0], "container_id": values[1], "src_ip": values[2],
                "dst_ip": values[3], "protocol": values[4], "src_port": values[5],
                "dst_port": values[6], "expected": values[7], "result": values[8],
                "flow": values[9], "data": values[10]
            })
            
        try:
            with open(self.save_file_path, "w") as f:
                json.dump(tests_data, f, indent=4)
            print(f"Tests successfully saved to {self.save_file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save file: {e}")

    def firewall_tests_open_test_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Test File", "", "JSON Files (*.json);;All Files (*)")
        if file_path:
            self.save_file_path = file_path
            self.firewall_tests_load_tests_from_file()

    def firewall_tests_load_tests_from_file(self):
        if not self.save_file_path or not os.path.exists(self.save_file_path):
            return
        
        try:
            with open(self.save_file_path, "r") as f:
                tests_data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            QMessageBox.critical(self, "Error", f"Could not load file: {e}")
            return

        reply = QMessageBox.question(self, "Load Tests", "This will clear current tests. Continue?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.No:
            return

        self.tree.clear()
        for test in tests_data:
            values = list(test.values())
            item = QTreeWidgetItem([str(v) for v in values])
            self.tree.addTopLevelItem(item)
            
        print("Tests loaded successfully.")
        self.firewall_tests_buttons_set_normal_state()


# Running the Firewall Tester application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FirewallGUI()
    window.show()
    sys.exit(app.exec_())
