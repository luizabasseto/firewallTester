#!/usr/bin/python

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
    Version: 1.0
"""


import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import font
from tkinter import filedialog
import os
import containers
import json
import re
import threading
import webbrowser
import textwrap

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
# TODO - The scroll of the firewall tests is not working properly and is cutting off the last column of the tree.
# TODO - Check if scroll is needed in other areas of the program (vertical and horizontal).
# TODO - Is it interesting to have a button to save firewall rules on the host? the user can do ctrl+c and ctrl+v - remembering that the rules are already saved in the container.
# TODO - if only the host or all hosts in the scenario are turned off, there is no problem for the interface, but if GNS3 is turned off and the same scenario is turned on again, the interface becomes inconsistent, even the host update button does not work properly! Also, the rules deployed in the firewall are lost.
# TODO - when saving and opening tests - do not reference the container ID, only the names and perhaps IPs (I think IPs are unavoidable for now), and when the rules are opened, the interface must relate or re-relate the hostname with the container_id, and perhaps the IPs (it would be nice not to relate with the IPs, because in the scenario the user could create or change the hostname to another IP and the test would continue to work).
# TODO - the combobox of "Edit firewall rules on host" should not show multiple lines for the same host (it shows one per host IP), but rather only one name.
# TODO - You need a scroll on the tabs and it also limits their size, because when you put too many hosts (about 7) the buttons to update hosts and exit the program disappeared, because the tabs pushed them off the screen.
# TODO - The information regarding docker containers is being performed three times in a row at the beginning, see if this is really necessary or if it can be done just once.
# TODO - relate the name of the docker image with the name used in the configuration tab.
# TODO - 

class FirewallGUI:
    """
        Class to work with firewall tester interface.
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

    def __init__(self, root):
        """
            Start firewall tester interface with some variables, methods and create default frames.
        """
        self.root = root
        self.root.title("Firewall Tester")
        self.root.geometry("800x600")

        # Creating Notebook tab
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill="both")

        # Criando as abas
        self.firewall_frame = ttk.Frame(self.notebook)
        self.hosts_frame = ttk.Frame(self.notebook)
        self.config_frame = ttk.Frame(self.notebook)
        self.firewall_rules = ttk.Frame(self.notebook)
        self.about_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.firewall_frame, text="Firewall Test")
        self.notebook.add(self.firewall_rules, text="Firewall Rules")
        self.notebook.add(self.hosts_frame, text="Hosts")
        self.notebook.add(self.config_frame, text="Settings")
        self.notebook.add(self.about_frame, text="About")

        # Frame under tabs
        frame_botton = ttk.Frame(self.root)
        frame_botton.pack(side=tk.BOTTOM, pady=6)
        
        # TODO - when updating host data, it may be necessary to change test data, especially container IDs and perhaps host IPs - just as it has to be done when loading tests from a file - think of a single solution for both problems - perhaps user intervention is needed.
        self.button_uptate_host = ttk.Button(frame_botton, text="Update Hosts", command=self.hosts_update)
        self.button_uptate_host.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.button_quit = ttk.Button(frame_botton, text="Exit", command=self.confirm_software_exit)
        self.button_quit.grid(row=0, column=6, padx=10, pady=10, sticky="nsew")
        
        frame_botton.grid_columnconfigure(0, weight=1)
        frame_botton.grid_columnconfigure(1, weight=1)
        frame_botton.grid_columnconfigure(2, weight=1)

        # file name path
        self.save_file_path = None

        # List to store tests
        self.tests = []

        # buttons list from hosts
        self.list_button_servers_onOff = []
        
        # get data from containers and hosts
        self.containers_data = containers.extract_containerid_hostname_ips( )  # get hosts informations
        
        # get container_id and hostname - used for example to combobox in firewall rules.
        self.container_hostname = containers.get_containerid_hostname() # container_id and hostname for operations
        self.hosts = list(map(lambda x: x[1], self.container_hostname)) # hostnames to display

        # creating tabs
        self.create_hosts_tab()
        self.create_settings_tab()
        self.create_firewall_tab()
        self.create_firewall_rules_tab()
        # restart servers on containers/hosts
        self.hosts_start_servers()
        self.create_about_tab()
        

    def load_settings(self):
        try:
            with open(self.SETTINGS_FILE, "r") as f:
                #print(json.load(f))
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return self.DEFAULT_SETTINGS.copy()
    
    def save_settings(self):
        settings = {
            "firewall_directory": self.config_firewall_dir_var.get(),
            "reset_rules_file": self.config_firewall_reset_rules_var.get(),
            "firewall_rules_file": self.config_firewall_rules_var.get(),
            "server_ports_file": self.config_server_ports_var.get(),
            "show_container_id": self.config_show_container_id_var.get(),
            "docker_image": self.config_docker_image_var.get(),
            "include_filter_table": self.config_include_filter_var.get(),
            "include_nat_table": self.config_include_nat_var.get(),
            "include_mangle_table": self.config_include_mangle_var.get()
        }
        with open(self.SETTINGS_FILE, "w") as f:
            json.dump(settings, f, indent=4)
        
        if self.config_show_container_id_var.get():
            self.tree.column("Container ID", width=130, minwidth=100)
        else:
            self.tree.column("Container ID", width=0, minwidth=0)
    
    def restore_default_settings(self):
        self.config_firewall_dir_var.set(self.DEFAULT_SETTINGS["firewall_directory"])
        self.config_firewall_reset_rules_var.set(self.DEFAULT_SETTINGS["reset_rules_file"])
        self.config_firewall_rules_var.set(self.DEFAULT_SETTINGS["firewall_rules_file"])
        self.config_server_ports_var.set(self.DEFAULT_SETTINGS["server_ports_file"])
        self.config_show_container_id_var.set(self.DEFAULT_SETTINGS["show_container_id"])
        self.config_docker_image_var.set(self.DEFAULT_SETTINGS["docker_image"])
        self.config_include_filter_var.set(self.DEFAULT_SETTINGS["include_filter_table"])
        self.config_include_nat_var.set(self.DEFAULT_SETTINGS["include_nat_table"])
        self.config_include_mangle_var.set(self.DEFAULT_SETTINGS["include_mangle_table"])
        self.save_settings()

    def create_settings_tab(self):
        """
            Create and configura settings for this software.
        """
        tittle_frame = tk.Frame(self.config_frame)
        tittle_frame.pack(pady=10)
        
        settings = self.load_settings()
        print("settings loaded:")
        print("firewall_directory:", settings.get("firewall_directory", ""))
        print("reset_rules_file:", settings.get("reset_rules_file", ""))
        print("firewall_rules_file:", settings.get("firewall_rules_file", ""))
        print("server_ports_file:", settings.get("server_ports_file", ""))
        print("show_container_id:", settings.get("show_container_id", False))
        print("docker_image:", settings.get("docker_image", ""))
        print("include_filter_table:", settings.get("include_filter_table", False))
        print("include_nat_table:", settings.get("include_nat_table", False))
        print("include_mangle_table:", settings.get("include_mangle_table", False))

       # Variables as class attributes
        self.config_firewall_dir_var = tk.StringVar(value=settings.get("firewall_directory", ""))
        self.config_firewall_reset_rules_var = tk.StringVar(value=settings.get("reset_rules_file", ""))
        self.config_firewall_rules_var = tk.StringVar(value=settings.get("firewall_rules_file", ""))
        self.config_server_ports_var = tk.StringVar(value=settings.get("server_ports_file", ""))
        self.config_show_container_id_var = tk.BooleanVar(value=settings.get("show_container_id", False))
        self.config_docker_image_var = tk.StringVar(value=settings.get("docker_image", ""))
        self.config_include_filter_var = tk.BooleanVar(value=settings.get("include_filter_table", False))
        self.config_include_nat_var = tk.BooleanVar(value=settings.get("include_nat_table", False))
        self.config_include_mangle_var = tk.BooleanVar(value=settings.get("include_mangle_table", False))

        # Developer Information
        ttk.Label(tittle_frame, text="Software Settings", font=("Arial", 14, "bold")).pack()
        
        buttons_frame = tk.Frame(self.config_frame)
        buttons_frame.pack(pady=10)
        
        ttk.Label(buttons_frame, text="Firewall Directory in the containers:").grid(row=0, column=0, sticky="w")
        ttk.Entry(buttons_frame, textvariable=self.config_firewall_dir_var, width=40).grid(row=0, column=1)

        ttk.Label(buttons_frame, text="Reset Rules File:").grid(row=1, column=0, sticky="w")
        ttk.Entry(buttons_frame, textvariable=self.config_firewall_reset_rules_var, width=40).grid(row=1, column=1)

        ttk.Label(buttons_frame, text="Firewall Rules File:").grid(row=2, column=0, sticky="w")
        ttk.Entry(buttons_frame, textvariable=self.config_firewall_rules_var, width=40).grid(row=2, column=1)

        ttk.Label(buttons_frame, text="Server Ports File:").grid(row=3, column=0, sticky="w")
        ttk.Entry(buttons_frame, textvariable=self.config_server_ports_var, width=40).grid(row=3, column=1)

        ttk.Label(buttons_frame, text="Docker Image Name:").grid(row=4, column=0, sticky="w")
        ttk.Entry(buttons_frame, textvariable=self.config_docker_image_var, width=40).grid(row=4, column=1)

        ttk.Checkbutton(buttons_frame, text="Show Container ID Column", variable=self.config_show_container_id_var).grid(row=5, column=0, columnspan=2, sticky="w")

        ttk.Checkbutton(buttons_frame, text="Include Filter Table in Firewall Listing", variable=self.config_include_filter_var).grid(row=6, column=0, columnspan=2, sticky="w")

        ttk.Checkbutton(buttons_frame, text="Include Filter NAT in Firewall Listing", variable=self.config_include_nat_var).grid(row=7, column=0, columnspan=2, sticky="w")

        ttk.Checkbutton(buttons_frame, text="Include Mangle Table in Firewall Listing", variable=self.config_include_mangle_var).grid(row=8, column=0, columnspan=2, sticky="w")

        ttk.Button(buttons_frame, text="Save Settings", command=self.save_settings).grid(row=9, column=0, columnspan=3, pady=5)
        ttk.Button(buttons_frame, text="Restore Defaults", command=self.restore_default_settings).grid(row=10, column=0, columnspan=3, pady=5)


    def create_about_tab(self):
        """
            Create tab about to present some informations about the software interface like: author, description, licence, etc.
        """
        top_frame = tk.Frame(self.about_frame)
        top_frame.pack(pady=10)

        # Developer Information
        lbl_title = ttk.Label(top_frame, text="About the Software", font=("Arial", 14, "bold"))
        lbl_title.pack(pady=10)

        # Software Description
        description = "This software was developed with the goal of strengthening network security through practical and efficient firewall testing. More than just a testing tool, it stands out as a valuable educational resource, designed to simplify and enhance the learning process about firewalls. Through an intuitive and interactive interface, students can visualize and experiment with the creation and application of firewall rules, making it easier to understand complex concepts and promoting deeper and more effective learning."

        # Create a frame for the description
        description_frame = ttk.Frame(top_frame)
        description_frame.pack(pady=10, padx=20, fill="x") #fill x to ocuupy the entire width.

        # Simulate full justification using textwrap
        wrapped_text = textwrap.fill(description, width=70) #Was increased the width to spread out more

        # Get background color from parent frame
        bg_color = top_frame.cget("background")

        # Use tk.Text for display
        text_widget = tk.Text(description_frame, wrap="word", width=70, height=8, borderwidth=0, highlightthickness=0, background=bg_color) #was increased the height and width
        text_widget.insert("1.0", wrapped_text)
        text_widget.config(state="disabled")  # Make it read-only
        text_widget.pack(pady=10, padx=10, fill="x")

        # Developer
        lbl_developer_name_head = ttk.Label(top_frame, text="Developer:")
        lbl_developer_name_head.pack()
        lbl_developer_name = ttk.Label(top_frame, text=f"Prof. Luiz Arthur Feitosa dos Santos", font=("Arial", 12, "bold"))
        lbl_developer_name.pack()

        # Clickable Email
        #lbl_email_text = ttk.Label(top_frame, text="Email: ")
        #lbl_email_text.pack()

        lbl_email = ttk.Label(top_frame, text=f"luiz.arthur.feitosa.santos@gmail.com\n", foreground="blue", cursor="hand2")
        lbl_email.pack()
        lbl_email.bind("<Button-1>", lambda e: webbrowser.open_new_tab("mailto:luiz.arthur.feitosa.santos@gmail.com"))

        lbl_institution_head = ttk.Label(top_frame, text="Institution:")
        lbl_institution_head.pack()
        lbl_institution = ttk.Label(top_frame, text=f"UTFPR-CM\n", font=("Arial", 12, "bold"))
        lbl_institution.pack()

        # Clickable Project Link
        lbl_project_link_text = ttk.Label(top_frame, text="Project Link: ")
        lbl_project_link_text.pack()

        lbl_project_link = ttk.Label(top_frame, text=f"https://github.com/luizsantos/firewallTester\n", foreground="blue", cursor="hand2")
        lbl_project_link.pack()
        lbl_project_link.bind("<Button-1>", lambda e: webbrowser.open_new_tab("https://github.com/luizsantos/firewallTester"))

        # Clickable License Link
        lbl_license_text = ttk.Label(top_frame, text="License: ")
        lbl_license_text.pack()

        lbl_license = ttk.Label(top_frame, text=f"GNU GPL v3\n", foreground="blue", cursor="hand2")
        lbl_license.pack()
        lbl_license.bind("<Button-1>", lambda e: webbrowser.open_new_tab("https://www.gnu.org/licenses/gpl-3.0.html"))

        # Help Button
        btn_help = ttk.Button(top_frame, text="Help", command=self.open_help)
        btn_help.pack(pady=20)

    def open_help(self):
        """
            Open a link in the web browser, to show help content.
        """
        webbrowser.open_new_tab("https://github.com/luizsantos/firewallTester")

    def create_hosts_tab(self):
            """
                Create Hosts tab, show informations about hosts and permit change some configurations like port and start/stop servers.
            """

            self.top_frame = tk.Frame(self.hosts_frame)
            self.top_frame.pack(pady=10)

            ttk.Label(self.top_frame, text="Network Containers Hosts:", font=("Arial", 12)).pack(padx=10)

            # Button to turn on all containers/servers
            ttk.Button(self.top_frame, text="Turn on servers", command=self.hosts_start_servers).pack(side=tk.LEFT, padx=10)

            self.frame_all_hosts = tk.Frame(self.hosts_frame)
            self.frame_all_hosts.pack(fill=tk.BOTH, expand=True) # Adicionado para expandir o frame

            # Criando um frame intermediário para centralizar tudo
            self.central_frame = tk.Frame(self.frame_all_hosts) 
            self.central_frame.place(relx=0.5, rely=0.5, anchor="center")

            self.canva_hosts = tk.Canvas(self.central_frame, width=500, height=800, takefocus=0, highlightthickness=0)
            self.canva_hosts.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            self.barra_vertical = ttk.Scrollbar(self.frame_all_hosts, orient="vertical", command=self.canva_hosts.yview)
            self.barra_vertical.pack(side=tk.RIGHT, fill=tk.Y)

            self.canva_hosts.configure(yscrollcommand=self.barra_vertical.set)

            self.frame_hosts_informations = tk.Frame(self.canva_hosts) # Frame para o conteúdo dentro do canvas
            self.canva_hosts.create_window((0, 0), window=self.frame_hosts_informations, anchor="n")

            #self.frame_hosts_informations.bind("<Configure>", lambda event: self.canva_hosts.configure(scrollregion=self.canva_hosts.bbox("all")))
            self.frame_hosts_informations.bind("<Configure>", self.scroll_ajust)

            self.hosts_show_host_informations_in_host_tab()

    def hosts_show_host_informations_in_host_tab(self):
        """
            Displays host information in the hosts tab.
        """
        #print(f"self.containers_data: {self.containers_data}")
        cont = containers.getContainersByImageName()
        #print(f"cont :  {json.dumps(cont, indent=4)}")
        self.list_button_servers_onOff = []
        row_index = 0  # Starting line on the grid

        # Load the icons
        self.power_icon = tk.PhotoImage(file="img/system-shutdown-symbolic.png")  
        self.power_icon_off = tk.PhotoImage(file="img/system-shutdown-symbolic-off.png") 
        status_on_icon = tk.PhotoImage(file="img/system-shutdown-symbolic.png")  
        status_off_icon = tk.PhotoImage(file="img/system-shutdown-symbolic.png") 

        for host in cont:
            print(f"ID: {host['id']}")
            print(f"Nome: {host['nome']}")
            print(f"Hostname: {host['hostname']}")
            print("Interfaces:")

            status = self.host_check_server_on_off(host['id'])

            container_id = host["id"]
            container_name = host["nome"]
            hostname = host["hostname"]

            #
            if not self.frame_hosts_informations.winfo_exists() or not self.canva_hosts.winfo_exists():
                print("Error: frame_content_hosts or canvas does not exist anymore!")
                #recriate 
                self.frame_hosts_informations = ttk.Frame(self.canva_hosts)
                self.canva_hosts.create_window((0, 0), window=self.frame_hosts_informations, anchor="n")

            
            # Creating a frame for each host
            frame_item = ttk.Frame(self.frame_hosts_informations)
            frame_item.grid(row=row_index, column=1, columnspan=1, sticky="ew", padx=10, pady=5)

            # Button to edit host ports
            btn = ttk.Button(frame_item, text=f"{hostname}", command=lambda cid=container_id: self.edit_host_ports(cid, hostname))
            btn.grid(row=0, column=0, padx=5, pady=2, sticky="w")

            # Label with container information
            lbl_container = ttk.Label(frame_item, text=f"Container: {container_id} - {container_name}", font=("Arial", 10))
            lbl_container.grid(row=0, column=1, padx=5, pady=2, sticky="w")

            row_index += 1  # Move to the next line

            if not host['interfaces']:
                # Creating a subframe to align interfaces and IPs together
                interface_frame = ttk.Frame(frame_item)
                interface_frame.grid(row=row_index, column=1, columnspan=2, sticky="w", padx=20)
                ip_index = 1
                lbl_interface = ttk.Label(interface_frame, text=f"Interface: None or Down", font=("Arial", 10, "bold"))
                lbl_interface.grid(row=0, column=0, sticky="w")

            else:
                for interface in host['interfaces']:
                    print(f"  - Interface: {interface['nome']}")
                    if_name = interface['nome']

                    # Creating a subframe to align interfaces and IPs together
                    interface_frame = ttk.Frame(frame_item)
                    interface_frame.grid(row=row_index, column=1, columnspan=2, sticky="w", padx=20)

                    # TODO - I noticed that the ip command shows the interface IPs even if this interface is turned off.
                    # Label with the interface name
                    lbl_interface = ttk.Label(interface_frame, text=f"Interface: {if_name}", font=("Arial", 10, "bold"))
                    lbl_interface.grid(row=0, column=0, sticky="w")

                    ip_index = 1
                    for ip in interface['ips']:
                        lbl_ip = ttk.Label(interface_frame, text=f"IP: {ip}", font=("Arial", 10))
                        lbl_ip.grid(row=ip_index, column=0, padx=20, sticky="w")
                        ip_index += 1

                    row_index += 2  # Move to the next line in the layout

            self.frame_hosts_informations.columnconfigure(0, weight=1)
            self.frame_hosts_informations.columnconfigure(2, weight=1)

            # Server status
            lbl_status = ttk.Label(interface_frame, text=f"Status from server: {status}", font=("Arial", 10))
            lbl_status.grid(row=ip_index, column=0, padx=5, sticky="w")

            # Power button with icon
            btn_toggle = ttk.Button(interface_frame, image=self.power_icon, command=lambda cid=container_id: self.host_toggle_server_and_button_between_onOff(cid, btn_toggle))
            btn_toggle.image = self.power_icon  # Keep the reference to avoid garbage collection
            btn_toggle.grid(row=ip_index, column=1, padx=10, pady=5, sticky="w")
            self.list_button_servers_onOff.append((container_id, btn_toggle, lbl_status))
            row_index += 1  # Extra line to separate hosts

    def scroll_ajust(self, event=None):
        """
            Updates the Canvas scroll area, adding a little extra space at the end.
        """
        self.canva_hosts.update_idletasks()  # Ensures the layout has been updated

        # Gets the actual region of content within the Canvas
        bbox = self.canva_hosts.bbox("all")

        if bbox:
            x0, y0, x1, y1 = bbox
            self.canva_hosts.configure(scrollregion=(x0, y0, x1, y1 + 50))  # Add extra 50px


    def create_firewall_rules_tab(self):
        """
            Create firewal rules tab, this permit create, list and edit firewall rules on the hosts.
        """
        # Top frame for title. 
        frame_tittle = tk.Frame(self.firewall_rules)
        frame_tittle.pack(fill=tk.X)

        ttk.Label(frame_tittle, text="Edit firewall rules on host:", font=("Arial", 12, "bold")).pack(padx=10)
        #self.combobox_firewall_rules_host = ttk.Combobox(frame_tittle, values=self.hosts_display, width=25, state="readonly", style="TCombobox")
        self.combobox_firewall_rules_host = ttk.Combobox(frame_tittle, values=self.hosts, width=25, state="readonly", style="TCombobox")
        self.combobox_firewall_rules_host.pack(pady=10)
        #self.combobox_host_regra_firewall.current(0)
        self.combobox_firewall_rules_host.set("")

        self.combobox_firewall_rules_host.bind("<<ComboboxSelected>>", self.selected_host_on_combobox_tab_firewall_rules)

        #label_titulo = tk.Label(frame_titulo, text="Editar regras de firewall", font=("Arial", 12, "bold"))
        #label_titulo.pack(pady=5)

        # Creating frame for the labels
        frame_firewall_rules = ttk.LabelFrame(self.firewall_rules, text="Rules to be applied to the firewall")
        frame_firewall_rules.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.text_firewall_rules = tk.Text(frame_firewall_rules, wrap=tk.NONE, height=10, undo=True)
        self.text_firewall_rules.grid(row=0, column=0, sticky="nsew")

        scroll_y_firewall_rules = tk.Scrollbar(frame_firewall_rules, orient=tk.VERTICAL, command=self.text_firewall_rules.yview)
        scroll_y_firewall_rules.grid(row=0, column=1, sticky="ns")
        self.text_firewall_rules.config(yscrollcommand=scroll_y_firewall_rules.set)

        scroll_x_firewall_rules = tk.Scrollbar(frame_firewall_rules, orient=tk.HORIZONTAL, command=self.text_firewall_rules.xview)
        scroll_x_firewall_rules.grid(row=1, column=0, sticky="ew")
        self.text_firewall_rules.config(xscrollcommand=scroll_x_firewall_rules.set)

        self.reset_firewall = tk.IntVar()
        checkbtn_reset_firewall_rules = tk.Checkbutton(frame_firewall_rules, text="Automatically reset firewall rules – this should be in your script, but you can do it here.", variable=self.reset_firewall)
        checkbtn_reset_firewall_rules.grid(row=2, column=0, sticky="w")

        frame_firewall_rules.grid_columnconfigure(0, weight=1)
        frame_firewall_rules.grid_rowconfigure(0, weight=1)

        # Creating frame for the active rules
        frame_output_firewall_rules = ttk.LabelFrame(self.firewall_rules, text="Output ")
        frame_output_firewall_rules.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        #frame_ativas.pack_forget()  # Hide on the start

        def toggle_frame_output_on_rule_tab():
            """
                Change frame output to hide or show output text in firewall rule tab.
            """
            if frame_output_firewall_rules.winfo_ismapped():
                frame_output_firewall_rules.pack_forget()
                button_show_active_firewall_rules.config(text="Show output")
            else:
                frame_output_firewall_rules.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
                button_show_active_firewall_rules.config(text="Hide output")

        def select_all_text_on_rules_text(event):
            """
                Selecte every texto inside texto firewall rule - for use with Ctrl+A
            """
            event.widget.tag_add("sel", "1.0", "end")
            return "break"

        self.text_active_firewall_rules = tk.Text(frame_output_firewall_rules, wrap=tk.NONE, height=10)
        self.text_active_firewall_rules.grid(row=0, column=0, sticky="nsew")
        self.text_active_firewall_rules.bind("<Control-a>", select_all_text_on_rules_text)

        self.text_firewall_rules.bind("<Control-a>", select_all_text_on_rules_text)

        scroll_y_active_firewall_rules = tk.Scrollbar(frame_output_firewall_rules, orient=tk.VERTICAL, command=self.text_active_firewall_rules.yview)
        scroll_y_active_firewall_rules.grid(row=0, column=1, sticky="ns")
        self.text_active_firewall_rules.config(yscrollcommand=scroll_y_active_firewall_rules.set)
        self.text_active_firewall_rules.config(state=tk.NORMAL) # I don't know why, but if you don't activate and deactivate text_actives, select all doesn't work in text_rules
        #self.text_ativas.config(state=tk.DISABLED)

        scroll_x_active_firewall_rules = tk.Scrollbar(frame_output_firewall_rules, orient=tk.HORIZONTAL, command=self.text_active_firewall_rules.xview)
        scroll_x_active_firewall_rules.grid(row=1, column=0, sticky="ew")
        self.text_active_firewall_rules.config(xscrollcommand=scroll_x_active_firewall_rules.set)

        frame_output_firewall_rules.grid_columnconfigure(0, weight=1)
        frame_output_firewall_rules.grid_rowconfigure(0, weight=1)
        self.button_list_firewall_rules = tk.Button(frame_output_firewall_rules, text="List firewall rules", command=self.list_firewall_rules_on_output)
        self.button_list_firewall_rules.grid(row=2, column=0)
        self.button_list_firewall_rules.config(state="disabled")

        # Creating buttons
        frame_buttons = tk.Frame(self.firewall_rules)
        frame_buttons.pack(pady=10)

        self.button_retrieve_firewall_rules = tk.Button(frame_buttons, text="Retrieve firewall rules", command=self.load_firewall_rules)
        self.button_retrieve_firewall_rules.pack(side=tk.LEFT, padx=10)
        self.button_retrieve_firewall_rules.config(state="disabled")

        self.button_deploy_firewall_rules = tk.Button(frame_buttons, text="Deploy firewall rules", command=self.apply_firewall_rules)
        self.button_deploy_firewall_rules.pack(side=tk.LEFT, padx=10)
        self.button_deploy_firewall_rules.config(state="disable")

        #self.btn_zerar = tk.Button(frame_botoes, text="Zerar Regras no firewall", command=self.zerar_regras_firewall)
        #self.btn_zerar.pack(side=tk.LEFT, padx=10)
        #self.btn_zerar.config(state="disable")

        button_show_active_firewall_rules = tk.Button(frame_buttons, text="Hide output", command=toggle_frame_output_on_rule_tab)
        button_show_active_firewall_rules.pack(side=tk.RIGHT, padx=10)

    def selected_host_on_combobox_tab_firewall_rules(self, src_ip):
        """
            Treats the selected host in the combobox
        """
        #print("selected_host_on_combobox_tab_firewall_rules")
        selected_index = self.combobox_firewall_rules_host.current()
        if selected_index >= 0 and selected_index < len(self.container_hostname):
            container_id = [self.container_hostname[selected_index][0], self.container_hostname[selected_index][1]]
            #print(f"container_data selected_index{selected_index} -  {self.containers_data[selected_index]}")
        else:
            container_id = "N/A"  # Caso nenhum container seja selecionado
        #print(container_id)
        self.button_retrieve_firewall_rules.config(state="normal")
        self.button_deploy_firewall_rules.config(state="normal")
        self.button_list_firewall_rules.config(state="normal")
        #self.btn_zerar.config(state="normal")
        self.container_id_host_regras_firewall=container_id

    def list_firewall_rules_on_output(self):
        """
            List active firewall rules on the host and display in the output text on firewall rules tab. The container/host is selected in the combobox on the firewall rules tab.
        """
        print(f"List firewall rules for host {self.container_id_host_regras_firewall[1]}")
        
        self.text_active_firewall_rules.delete(1.0, tk.END)

        self.text_active_firewall_rules.tag_configure("bold", font=("TkDefaultFont", "10", "bold"))
        #self.text_active_firewall_rules.tag_configure("normal", font=("TkDefaultFont", "10"))

        if self.config_include_mangle_var.get() or self.config_include_nat_var.get() or self.config_include_filter_var.get():
            if self.config_include_mangle_var.get():
                command = ["docker", "exec", self.container_id_host_regras_firewall[0], "iptables", "-L", "-n", "-t", "mangle"]
                result = containers.run_command(command)
                self.text_active_firewall_rules.insert(tk.END, f"\n\u2022 Mangle Rules:", "bold")
                self.text_active_firewall_rules.insert(tk.END, f"\n - Result of the command iptables -t mangle -L on host {self.container_id_host_regras_firewall[1]}:\n\n")
                self.text_active_firewall_rules.insert(tk.END, result.stdout)    

            if self.config_include_nat_var.get():
                command = ["docker", "exec", self.container_id_host_regras_firewall[0], "iptables", "-L", "-n", "-t", "nat"]
                result = containers.run_command(command)
                self.text_active_firewall_rules.insert(tk.END, f"\n\u2022 NAT Rules:", "bold")
                self.text_active_firewall_rules.insert(tk.END, f"\n - Result of the command iptables -t nat -L on host {self.container_id_host_regras_firewall[1]}:\n\n")
                self.text_active_firewall_rules.insert(tk.END, result.stdout)
            
            if self.config_include_filter_var.get():
                command = ["docker", "exec", self.container_id_host_regras_firewall[0], "iptables", "-L", "-n"]
                result = containers.run_command(command)
                self.text_active_firewall_rules.insert(tk.END, f"\n\u2022 Filter Rules:", "bold")
                self.text_active_firewall_rules.insert(tk.END, f"\n - Result of the command iptables -L on host {self.container_id_host_regras_firewall[1]}:\n\n")
                self.text_active_firewall_rules.insert(tk.END, result.stdout)
        else:
            self.text_active_firewall_rules.insert(tk.END, f"\n* All firewall rule tables are disabled for listing in the settings tab - so if you want to list the rules enable them in the settings tab.\n\n")

        self.text_active_firewall_rules.see(tk.END) # rola o scroll para o final, para ver o texto mais recente!
        

    def load_firewall_rules(self):
        """
            Load firewall rules into container/host, this rules are present in the firewall rules texto component in the firewall rules tab. The container/host is selected in the combobox on the firewall rules tab.
        """
        print(f"Load firewall rules from hos {self.container_id_host_regras_firewall[1]}")

        resposta = messagebox.askyesno("Confirmation","This will overwrite the existing rules in the interface. Are you sure you want to continue?")
        # TODO - in UTPFR there was a problem when copying the file from the firewall to the container, it said it copied but didn't copy anything, it only copied when the file was touched - see this.
        if resposta:
            file = self.config_firewall_dir_var.get()+"/firewall.sh"
            command = ["docker", "exec", self.container_id_host_regras_firewall[0], "cat", file]
            result = containers.run_command(command)
            self.text_firewall_rules.delete(1.0, tk.END)
            self.text_firewall_rules.insert(tk.END, result.stdout)

    # TODO - would it be good to have a button to reset the firewall rules?

    def sento_to_host_file_to_execute_firewall_rules(self, file_rules, reset): # se for reset indica que o caminho é o arquivo de reset, caso contrário são regras
        """
            Send to save in the container/host the firewall rules in the firewall interface (tab firewall rules). The container/host is selected in the combobox on the firewall rules tab.

            Args:
                file_rules (string) - source file.
                reset - indicate if the firewall rules will be reseted or not by the interface.  If it is reset it indicates that the path is the reset file, otherwise it is rules.

        """
        print(f"Send and execute firewall rules on host {self.container_id_host_regras_firewall[1]}")
        
        file_reset = self.config_firewall_dir_var.get()+"/firewall_reset.sh"
        file = self.config_firewall_dir_var.get()+"/firewall.sh"

        if reset!=None:
            containers.copy_host2container(self.container_id_host_regras_firewall[0], file_rules, file_reset)
            command = ["docker", "exec", self.container_id_host_regras_firewall[0], "sh", file_reset]
        else:
            containers.copy_host2container(self.container_id_host_regras_firewall[0], file_rules, file)
            command = ["docker", "exec", self.container_id_host_regras_firewall[0], "sh", file]

        result = containers.run_command(command)

        self.text_active_firewall_rules.delete(1.0, tk.END)
        if result.stderr:
            self.text_active_firewall_rules.delete(1.0, tk.END)
            self.text_active_firewall_rules.insert(tk.END, f"\n* Error applying firewall rules - check if there is something wrong with the rules on host {self.container_id_host_regras_firewall[1]}:\n\n")
            self.text_active_firewall_rules.insert(tk.END, result.stderr)
            self.text_active_firewall_rules.see(tk.END) # scroll to the end to see the most recent text!
            messagebox.showinfo("Warning", "Something went wrong while executing the rules, check the output!")
        else:
            self.list_firewall_rules_on_output()
            self.text_active_firewall_rules.insert(tk.END, f"\n* Firewall status on host {self.container_id_host_regras_firewall[1]} after rules have been applied\n\n")
            self.text_active_firewall_rules.see(tk.END) # scroll to the end to see the most recent text!


    def apply_firewall_rules(self):
        """
            Apply/execute rules firewall rules on host/container selected in the combobox on the firewall rules tab.
        """
        print(f"Apply rules on the firewall of host {self.container_id_host_regras_firewall[1]}")
        rules = self.text_firewall_rules.get("1.0", tk.END)
        file_rules=self.config_firewall_rules_var.get()
        with open(file_rules, "w", encoding="utf-8") as file_name:
            file_name.write(rules)
        print(f"Rules saved in the file {file_rules}")
        if self.reset_firewall.get() == 1: # If the checkbox is checked, first reset the firewall, then apply the rules.
            self.sento_to_host_file_to_execute_firewall_rules(self.config_firewall_reset_rules_var.get(), 1)
        
        self.sento_to_host_file_to_execute_firewall_rules(file_rules, None)
        
        if self.reset_firewall.get() == 1:
            self.text_active_firewall_rules.insert(tk.END, f"\n>>Warning!<< The firewall rules of host {self.container_id_host_regras_firewall[1]} were reset via the interface, but this SHOULD be in your firewall commands because firewalls do not reset automatically in real life!\n\n")
            self.text_active_firewall_rules.see(tk.END) # scroll to the end to see the most recent text!

    def reset_firewall_rules(self):
        """
            Resets the firewall rules for the host/container selected in the combobox on the firewall rules tab.
        """
        print(f"Reset firewall rules on host {self.container_id_host_regras_firewall[1]}")
        response = messagebox.askyesno("Warning","This action of resetting firewall rules does not exist by default, meaning this should be handled in your firewall rules. Are you sure you want to continue?")
        if response:
            self.sento_to_host_file_to_execute_firewall_rules(self.reset_firewall.get(), 1)

    # def selecionar_tudo(self, event=None):
    #     """Seleciona todo o texto."""
    #     self.text.tag_add("sel", "1.0", "end")
    #     return "break"  # Impede o comportamento padrão do atalho

    def edit_host_ports(self, container_id, hostname):
        """
            Opens a new window to edit host ports in the hosts tab.

            Args:
                container_id: Container ID.
                hostname: Hostname or container.
        """
        popup = tk.Toplevel(self.root)
        popup.title(f"Edit Ports for Container {container_id} - {hostname}:")
        popup.geometry("400x300")  

        ports = containers.get_port_from_container(container_id)
    
        ttk.Label(popup, text=f"Opened Ports from {hostname}", font=("Arial", 10)).pack(pady=5)

        # Create a Treeview to show network ports.
        colunas = ("Protocolo", "Porta")
        list_host_ports = ttk.Treeview(popup, columns=colunas, show="headings", selectmode="browse")
        list_host_ports.heading("Protocolo", text="Protocol")
        list_host_ports.heading("Porta", text="Port")
        list_host_ports.column("Protocolo", width=150, anchor=tk.CENTER)
        list_host_ports.column("Porta", width=100, anchor=tk.CENTER)
        list_host_ports.pack(pady=10)

        # Populate the Treeview with existing ports
        for protocol, port in ports:
            list_host_ports.insert("", tk.END, values=(protocol, port))

        # Create a frame to buttons
        frame_buttons = ttk.Frame(popup)
        frame_buttons.pack(pady=10)

        # Button to add line/port
        button_add = ttk.Button(frame_buttons, text="Add Port", command=lambda: self.add_line_treeview_host(list_host_ports))
        button_add.pack(side=tk.LEFT, padx=5)

        # Button to remove a line/port
        button_delete = ttk.Button(frame_buttons, text="Delete Port ", command=lambda: self.delete_line_treeview_host(list_host_ports))
        button_delete.pack(side=tk.LEFT, padx=5)

        ttk.Button(popup, text="Reload Ports", command=lambda: self.hosts_save_ports_in_file(container_id, list_host_ports)).pack(pady=10)

        
    def add_line_treeview_host(self, ports_list):
        """
            Open a new window to add a port in a Treeview

            Args:
                ports_list: List of network ports.

        """
        popup = tk.Toplevel()
        popup.title("Add Port")
        popup.geometry("300x150")

        
        def add_port_on_host():
            """
                Validate and add the port.
            """
            protocol = combobox_protocol.get().strip().upper()
            port = entry_port.get().strip()

            # Validate protocol
            if protocol not in ["TCP", "UDP"]:
                messagebox.showerror("Error", "Invalid protocol! Choose TCP or UDP.")
                return

            # Validate port
            try:
                port = int(port)
                if port < 1 or port > 65535:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Invalid port! Must be a number between 0 and 65535.")
                return

            # Checks if the protocol/port combination already exists in the table
            for line in ports_list.get_children():
                values = ports_list.item(line, "values")
                if values[0].upper() == protocol and values[1] == str(port):
                    messagebox.showerror("Error", f"Port {port}/{protocol} already exists in the table!")
                    return

            # Add new port in the Treeview
            ports_list.insert("", tk.END, values=(protocol, port))
            popup.destroy()  # Close popup

        # Fields to select the protocol
        ttk.Label(popup, text="Protocol:").pack(pady=5)
        combobox_protocol = ttk.Combobox(popup, values=["TCP", "UDP"], state="readonly")
        combobox_protocol.set("TCP")  # Default value
        combobox_protocol.pack(pady=5)

        # Field to add port
        ttk.Label(popup, text="Port:").pack(pady=5)
        entry_port = ttk.Entry(popup)
        entry_port.pack(pady=5)

        # Button to add port
        ttk.Button(popup, text="Add", command=add_port_on_host).pack(pady=10)

    # Função para remover a linha selecionada
    def delete_line_treeview_host(self, ports_list):
        """
            Remove line/port from a host.
            
            Args:
                ports_list: List of network ports.
        """
        #print("Delete")
        selected = ports_list.selection()
        if selected:  # Verifica se há algo selecionado
            ports_list.delete(selected)

    def hosts_save_ports_in_file(self, container_id, ports_list):
        """
            Saves the ports and protocols of the Treeview in a file, in the format "port/protocol".

            Args:
                ports_table: The Treeview containing the columns "Protocol" and "Port".
                file_name: Name of the file where the data will be saved.
        """
        file_name = self.config_server_ports_var.get()
        try:
            with open(file_name, "w") as file:
                # Iterate through all rows of the Treeview
                for line in ports_list.get_children():
                    # Get the line values (protocol and port)
                    valores = ports_list.item(line, "values")
                    if len(valores) == 2:  # Check if there are two values ​​(protocol and port)
                        protocolo, porta = valores
                        # write in the file in the format "prot/protocol"
                        file.write(f"{porta}/{protocolo}\n")
            print(f"Ports successfully saved in file {file_name}!")
        except Exception as e:
            print(f"Error saving ports: {e}")
        
        # reload the ports in the container, starting all services on each port.
        self.reload_ports(container_id, file_name)
        # restart server
        containers.start_server(container_id)

    def reload_ports(self, container_id, file_name):
        """
            Reload service ports in the container/host. It's made copying the file in the interface to the container.
            
            Args:
                container_id: container ID.
                file_name: File name.
        """
        print(f"Reload ports from {container_id}")

        containers.copy_ports2server(container_id, file_name)

    def create_firewall_tab(self):
        """
            Create the firewall tests tab.
        """
        ttk.Label(self.firewall_frame, text="Firewall Test", font=("Arial", 12)).pack(pady=10)

        # Frame for input fields
        frame_botton = ttk.Frame(self.firewall_frame)
        #frame_entrada.pack(fill="x", padx=10, pady=5)
        frame_botton.pack(pady=10)

        # List values in the Combobox (hostname + IP)
        if self.containers_data:
            self.hosts_display = [f"{c['hostname']} ({c['ip']})" for c in self.containers_data]
        else: # If there are no elements it displays a message.
            self.hosts_display = ["HOSTS (0.0.0.0)", "HOSTS (0.0.0.0)"]
            messagebox.showerror("Warning", "Something seems to be wrong! \n Is GNS3 or the hosts turned on?")
        # Sort the list of hosts in ascending order.

        protocols = ["TCP", "UDP", "ICMP"]

        # setting style - so readonly doesn't turn gray
        style = ttk.Style()
        style.map("TCombobox", fieldbackground=[("readonly", "white")])
        # background color of the selected line - so as not to cover the test color


        # Inputs components
        ttk.Label(frame_botton, text="Source IP:").grid(row=0, column=0)
        self.src_ip = ttk.Combobox(frame_botton, values=self.hosts_display, width=25, state="readonly", style="TCombobox")
        self.src_ip.current(0)
        self.src_ip.grid(row=1, column=0)


        ttk.Label(frame_botton, text="Destination IP:").grid(row=0, column=1)
        self.dst_ip = ttk.Combobox(frame_botton, values=self.hosts_display, width=25)
        if len(self.containers_data) > 1: # checks if there is more than one element in the host list, if there isn't, you can't set the second one as default.
            self.dst_ip.current(1)
        else:
            self.dst_ip.current(0)

        self.dst_ip.grid(row=1, column=1)
        # Binds the selection event
        self.dst_ip["state"] = "normal"

        ttk.Label(frame_botton, text="Protocol:").grid(row=0, column=2)
        self.protocol = ttk.Combobox(frame_botton, values=protocols, width=6, state="readonly", style="TCombobox")
        self.protocol.current(0)
        self.protocol.grid(row=1, column=2)

        ttk.Label(frame_botton, text="Src Port:").grid(row=0, column=3)
        self.src_port = ttk.Entry(frame_botton, width=11)
        self.src_port.insert(0, "*")
        self.src_port.config(state="disabled")
        self.src_port.grid(row=1, column=3)

        ttk.Label(frame_botton, text="Dst Port:").grid(row=0, column=4)
        self.dst_port = ttk.Entry(frame_botton, width=11)
        self.dst_port.insert(0, "80")
        self.dst_port.grid(row=1, column=4)

        ttk.Label(frame_botton, text="Expected success?").grid(row=0, column=5)
        self.expected = tk.StringVar(value="yes")
        ttk.Radiobutton(frame_botton, text="Yes", variable=self.expected, value="yes").grid(row=1, column=5)
        ttk.Radiobutton(frame_botton, text="No", variable=self.expected, value="no").grid(row=1, column=6)

        # Frame to display added tests
        self.tests_frame = ttk.Frame(self.firewall_frame)
        self.tests_frame.pack(fill="x", padx=10, pady=10)

        # Intermediate frame to center the buttons
        self.button_frame = tk.Frame(self.tests_frame)
        self.button_frame.pack(pady=10)  # Centraliza verticalmente

        button_size=15
        # Creating and adding buttons inside the intermediate frame
        self.button_tree_add = tk.Button(self.button_frame, text="Add", command=self.firewall_test_tree_add_line_test, width=button_size, underline=0)
        self.button_tree_add.pack(side="left", padx=5)
        self.root.bind("<Alt-a>", lambda event: self.firewall_test_tree_add_line_test())

        self.button_tree_edit = tk.Button(self.button_frame, text="Edit", command=self.firewall_test_tree_edit_line_test, width=button_size, underline=0)
        self.button_tree_edit.pack(side="left", padx=5)
        # # TODO - you have to think about when to enable and disable binds, because the way it is it works everywhere!
        #self.root.bind("<Alt-e>", lambda event: self.edit_entry())

        self.button_tree_del = tk.Button(self.button_frame, text="Delete", command=self.firewall_test_tree_delete_line_test, width=button_size, underline=0)
        self.button_tree_del.pack(side="left", padx=5)
        #self.root.bind("<Alt-d>", lambda event: self.delete_entry())

        self.button_tree_test = tk.Button(self.button_frame, text="Test Line", command=self.firewall_tests_run_test_line, width=button_size, underline=8)
        self.button_tree_test.pack(side="left", padx=5)
        #self.root.bind("<Alt-l>", lambda event: self.testar_linha_tree())

        self.button_tree_test_all = tk.Button(self.button_frame, text="Test All", command=self.firewall_tests_popup_for_run_all_tests_using_threads, width=button_size, underline=0)
        self.button_tree_test_all.pack(side="left", padx=5)
        #self.root.bind("<Alt-l>", lambda event: self.executar_todos_testes())


        # Frame to display the tests added in the treeview
        self.tests_frame_Tree = ttk.Frame(self.firewall_frame)
        self.tests_frame_Tree.pack(fill="both", expand=True, padx=10, pady=10)

        self.hidden_data = {}  # Dictionary to store Container ID associated with Test ID
        self.entries = []
        visible_fields = ["#", "Container ID", "Source", "Destination", "Protocol", "Source Port", "Destination Port", "Expected", "Result", "flow", "data"]
        self.tree = ttk.Treeview(self.tests_frame_Tree, columns=visible_fields, show="headings")

        font = ("TkDefaultFont", 10)
        tk_font = tk.font.Font(font=font)

        self.tree.heading("#", text="#")
        self.tree.column("#", width=30, anchor="e", stretch=False)

        if  self.config_show_container_id_var.get(): # Show or hide container ID in tree table.
            self.colunaContainerID=130 # show
        else:
            self.colunaContainerID=0 # hide.
            
        self.tree.heading("Container ID", text="Container ID")
        self.tree.column("Container ID", width=self.colunaContainerID, stretch=False)

        self.tree.heading("Source", text="Source")
        self.tree.column("Source", width=250, stretch=False)

        self.tree.heading("Destination", text="Destination")
        self.tree.column("Destination", width=250, stretch=False)

        self.tree.heading("Protocol", text="Protocol")
        self.tree.column("Protocol", width=80, anchor="center", stretch=False)

        self.tree.heading("Source Port", text="Src Port")
        self.tree.column("Source Port", width=80, anchor="center", stretch=False)

        self.tree.heading("Destination Port", text="Dst Port")
        self.tree.column("Destination Port", width=80, anchor="center", stretch=False)

        self.tree.heading("Expected", text="Expected")
        self.tree.column("Expected", width=80, anchor="center", stretch=False)

        self.tree.heading("Result", text="Result")
        self.tree.column("Result", width=80, anchor="w", stretch=False)

        self.tree.heading("flow", text="Network Flow")
        self.tree.column("flow", width=200, anchor="w", stretch=False)

        self.tree.heading("data", text="Network Data")
        self.tree.column("data", minwidth=100, width=200, anchor="w", stretch=True)

        #self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scroll_vertical_tree = tk.Scrollbar(self.tests_frame_Tree, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll_vertical_tree)
        scroll_vertical_tree.pack(side=tk.RIGHT, fill=tk.Y)

        frame_horizontal = ttk.Frame(self.firewall_frame) # Frame para a barra de rolagem horizontal
        frame_horizontal.pack(fill=tk.X)

        # TODO - scroll is not adjusting when data exceeds the window size!
        scroll_horizontal_tree = tk.Scrollbar(frame_horizontal, orient=tk.HORIZONTAL, command=self.tree.xview)
        #self.tree.configure(xscrollcommand=scroll_horizontal_tree.set)
        scroll_horizontal_tree.pack(side=tk.BOTTOM, fill=tk.X, expand=True)

        self.tree.configure(yscrollcommand=scroll_vertical_tree.set, xscrollcommand=scroll_horizontal_tree.set)

        # Color definition
        style = ttk.Style()
        style.configure("Treeview", rowheight=25)
        style.map("Treeview", background=[("selected", "#4a90e2")])
        self.tree.tag_configure("yes", background="lightgreen")
        self.tree.tag_configure("yesFail", background="lightblue")
        self.tree.tag_configure("no", background="salmon")
        self.tree.tag_configure("error", background="yellow")
        #self.tree.tag_configure("nat", background="lightblue")

        self.tree.bind("<<TreeviewSelect>>", self.firewall_test_tree_select_line_test)
        self.tree.bind("<Double-1>", self.firewall_test_tree_double_click_line_test)
        self.tree.bind('<Escape>', self.firewall_test_tree_select_line_test)

        btn_frame = tk.Frame(root)
        btn_frame.pack(side="bottom", fill="x", padx=10, pady=10)

        self.button_tree_edit.config(state="disabled")
        self.button_tree_del.config(state="disabled")
        self.button_tree_test.config(state="disabled")
        if not self.tree.get_children():
            self.button_tree_test_all.config(state="disabled")

        # Frame Legend
        self.frame_test_legend = ttk.LabelFrame(self.firewall_frame, text="Legenda")
        self.frame_test_legend.pack(side="bottom", fill="x", padx=20, pady=15)
        self.frame_test_legend.pack_propagate(False)
        self.frame_test_legend.config(width=700, height=50)

        tk.Label(self.frame_test_legend, bg="lightgreen", width=2, height=1, font=("Arial", 6)).pack(side="left", padx=5)
        tk.Label(self.frame_test_legend, text="Test successfully completed - net flow allowed/accepted).", font=("Arial", 10)).pack(side="left")

        tk.Label(self.frame_test_legend, bg="lightblue", width=2, height=1, font=("Arial", 6)).pack(side="left", padx=5)
        tk.Label(self.frame_test_legend, text="Test successfully completed - net flow blocked/dropped).", font=("Arial", 10)).pack(side="left")

        tk.Label(self.frame_test_legend, bg="red", width=2, height=1, font=("Arial", 6)).pack(side="left", padx=5)
        tk.Label(self.frame_test_legend, text="Test failed.", font=("Arial", 10)).pack(side="left")

        tk.Label(self.frame_test_legend, bg="yellow", width=2, height=1, font=("Arial", 6)).pack(side="left", padx=5)
        tk.Label(self.frame_test_legend, text="Error (e.g., error in IP, GW, DNS, Server)", font=("Arial", 10)).pack(side="left")

        self.frame_button_save_tests = ttk.Frame(self.firewall_frame)
        self.frame_button_save_tests.pack(pady=10)

        self.button_save_tests = ttk.Button(self.frame_button_save_tests, text="Save Tests", command=self.firewall_tests_save_tests)
        self.button_save_tests.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        self.button_save_tests_as = ttk.Button(self.frame_button_save_tests, text="Save Tests As", command=self.firewall_tests_save_tests_as)
        self.button_save_tests_as.grid(row=0, column=3, padx=10, pady=10, sticky="nsew")

        self.button_load_tests = ttk.Button(self.frame_button_save_tests, text="Open Tests", command=self.firewall_tests_open_test_file)
        self.button_load_tests.grid(row=0, column=5, padx=10, pady=10, sticky="nsew")

    def firewall_test_tree_select_line_test(self, event):
        """
            Method executed when a row of the firewall test table is executed (on tab firewall test ).
        """
        #print("firewall_test_tree_select_line")
        selected_item = self.tree.selection()
        if selected_item:
            item_values = self.tree.item(selected_item, "values")
            if item_values:
                #print(f"{item_values}")
                
                self.src_ip.set(item_values[2])

                self.dst_ip.delete(0, tk.END)
                self.dst_ip.insert(0, item_values[3])

                self.protocol.set(item_values[4])

                self.src_port.delete(0, tk.END)
                self.src_port.insert(0, item_values[5])

                self.dst_port.delete(0, tk.END)
                self.dst_port.insert(0, item_values[6])

                self.expected.set(item_values[7])

        if not self.tree.selection():
            self.button_tree_test.config(state="disabled")
        else:
            self.button_tree_test.config(state="normal")
            self.button_tree_test_all.config(state="normal")

        self.button_tree_add.config(state="normal")
        self.button_tree_edit.config(state="disable")
        self.button_tree_del.config(state="disable")
    
    def firewall_test_tree_double_click_line_test(self, event):
        """
            Treat double click in firewall teste tree
        """
        self.firewall_test_tree_select_line_test(event)
        self.firewall_tests_buttons_set_editing_state()


    def firewall_test_tree_add_line_test(self):
        """
            Add a line/test on treeview firewall tests.
        """
        #print("add_line_on_tree_test_firewall")
        
        src_ip = self.src_ip.get()
        dst_ip = self.dst_ip.get()
        protocol = self.protocol.get()
        src_port = self.src_port.get()
        dst_port = self.dst_port.get()
        expected = self.expected.get()

        if self.firewall_tests_validate_entrys() != 0: return # test values

        # Gets the ID of the container selected in the Combobox
        selected_index = self.src_ip.current()
        if selected_index >= 0 and selected_index < len(self.containers_data):
            container_id = self.containers_data[selected_index]["id"]
            print(f"container_data selected_index{selected_index} -  {self.containers_data[selected_index]}")
        else:
            container_id = "N/A"  # If no container is selected
        
        row_index = len(self.tree.get_children()) + 1 # tree line index

        values = [src_ip, dst_ip, protocol, src_port, dst_port, expected, "-", " ", " "]

        for item in self.tree.get_children(): # avoid duplicate testing
            existing_values = self.tree.item(item, "values")
            #print(f"Values\n{values}\n{existing_values[2:]}")
            if tuple(values) == existing_values[2:]:
                #print(f"egual values - \n{values}\n{existing_values}")
                messagebox.showwarning("Warning", "This entry already exists in the table!")
                return

        values=[]
        self.tree.insert("", "end", values=[row_index, container_id, src_ip, dst_ip, protocol, src_port, dst_port, expected, "-", " ", " "])
        #self.tree.column("Container ID", width=self.colunaContainerID, stretch=False)
        
        self.firewall_tests_buttons_set_normal_state()

    def firewall_test_tree_edit_line_test(self):
        """
            Edit a row/test of an existing item/test in the firewall test Treeview. The test to be edited is the one currently selected in the treeview.
        """
        selected_item = self.tree.selection()
        print(f"Selected item {selected_item}")
        if not selected_item:
            messagebox.showwarning("Warning", "Select an item to edit!")
            return
        
        src_ip = self.src_ip.get()
        dst_ip = self.dst_ip.get()
        protocol = self.protocol.get()
        src_port = self.src_port.get()
        dst_port = self.dst_port.get()
        expected = self.expected.get()

        if self.firewall_tests_validate_entrys() != 0: return # Test values

        values = [src_ip, dst_ip, protocol, src_port, dst_port, expected, "-", " ", " "]

        for item in self.tree.get_children(): # avoid duplicate TODO testing - put this in a method as it is duplicated in the code!
            existing_values = self.tree.item(item, "values")
            if tuple(values) == existing_values[2:]:
                messagebox.showwarning("Warning", "This entry already exists in the table!")
                return

        # Gets the ID of the container selected in the Combobox
        selected_index = self.src_ip.current()
        if selected_index >= 0 and selected_index < len(self.containers_data):
            container_id = self.containers_data[selected_index]["id"]
        else:
            container_id = "N/A"  # If no container is selected
        
        values=[self.tree.item(selected_item, "values")[0], container_id, src_ip, dst_ip, protocol, src_port, dst_port, expected, "-", " ", " "]

        self.tree.item(selected_item, values=values)
        self.tree.item(selected_item, tags="")  # return the color to default
        

        self.firewall_tests_buttons_set_normal_state()

    def firewall_tests_buttons_set_normal_state(self):
        """
            Defines the state of the firewall test buttons when adding a line/test. This is the normal state when using the Estes interface (startup state).
        """
        self.tree.selection_set(())
        self.button_tree_add.config(state="normal")
        self.button_tree_edit.config(state="disable")
        self.button_tree_del.config(state="disable")
        self.button_tree_test.config(state="disabled")
        self.button_tree_edit.config(text="Editar")
        if not self.tree.get_children():
            self.button_tree_test_all.config(state="disabled")
        else:
            self.button_tree_test_all.config(state="normal")
        
    def firewall_tests_buttons_set_editing_state(self):
        """
            Defines the state of the firewall test buttons when editing a line/test. 
            State used to prevent the user from running a test while the rule is malformed (under editing or deletion)
        """
        self.button_tree_edit.config(state="normal")
        self.button_tree_del.config(state="normal")
        self.button_tree_add.config(state="disabled")
        self.button_tree_test.config(state="disabled")
        self.button_tree_test_all.config(state="disabled")
        self.button_tree_edit.config(text="Save Edit")

    def firewall_test_tree_delete_line_test(self): # TODO - renumber lines when removing a test
        """
            Delete a row/test of an existing item/test in the firewall test Treeview. The test to be deleted is the one currently selected in the treeview.
        """
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Select an item to delete!")
            return
        self.tree.delete(selected_item)

        self.firewall_tests_buttons_set_normal_state() 

    def validate_ip_or_domain(self, ip_or_domain):
        """
            Validate IP or domain. Method used, for example, to validate whether an IP or domain chosen or entered by the user is valid for test processing. Validate only IPv4 address not IPv6.

            Arg:
                ip_or_domain: IP or Domain to be validate.
        """
        # Regex to IP (IPv4)
        regex_ip = r'^\d+\.\d+\.\d+\.\d+$'
        
        # Regex do domain (ex: google.com, www.example.com)
        regex_domain = r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if re.match(regex_ip, ip_or_domain):
            return True
        elif re.match(regex_domain, ip_or_domain):
            return True
        else:
            return False
    
    def firewall_tests_validate_entrys(self):
        """
            Checks if the IPs, domains and ports have the expected values. If all fields have been filled in, etc.
        """
        # Check if the required fields are filled in

        if not self.src_ip.get() or not self.dst_ip.get() or not self.protocol.get() or not self.dst_port.get():
            messagebox.showwarning("Mandatory fields", "Please fill in all mandatory fields.")
            return -1
        if not self.dst_port.get().isdigit():
            messagebox.showwarning("Mandatory fields", "The port must be a number between 1-65535.")
            return -1
        try:
            porta = int(self.dst_port.get())
            if porta < 1 or porta > 65535:
                messagebox.showwarning("Mandatory fields", "The port must be a number between 1-65535.")
                return -1
        except ValueError:
            messagebox.showwarning("Invalid port: conversion error.")
            return -1
        
        if self.dst_ip.get() not in self.hosts_display:
            if self.validate_ip_or_domain(self.dst_ip.get()) == False:
                messagebox.showwarning(f"Invalid address", "The address must either: \n1. Be on the list, \n2. Be an IP (8.8.8.8), \n3. Be a domain (www.google.com.br).")
                return -1
            else: # If it is outside the list of hosts in the scenario, for now it is only possible to perform ping tests.
                if self.protocol.get() != "ICMP":
                    messagebox.showwarning(f"Invalid protocol", "Unfortunately, in this version, only ICMP (ping) can be used to test external hosts.")
                    return -1
                
        return 0
        # TODO - if the destination is changed, in this version of the system, you can only use the ICMP protocol, you cannot use TCP or UDP, because the server (if it exists) will not recognize the message sent.
        # If all fields are filled in, call the firewall_test_tree_edit_line_test (old add_edit_test method)
        

    # def validar_e_adicionar_teste(self):
    #     """Valida os campos antes de chamar o método adicionar_editar_teste"""
    #     # Verifica se os campos obrigatórios estão preenchidos

    #     if not self.src_ip.get() or not self.dst_ip.get() or not self.protocol.get() or not self.dst_port.get():
    #         messagebox.showwarning("Mandatory fields", "Please fill in all mandatory fields.")
    #         return
    #     if not self.dst_port.get().isdigit():
    #         messagebox.showwarning("Mandatory fields", "The port must be a number between 1-65535.")
    #         return
    #     try:
    #         porta = int(self.dst_port.get())
    #         if porta < 1 or porta > 65535:
    #             messagebox.showwarning("Mandatory fields", "The port must be a number between 1-65535.")
    #             return
    #     except ValueError:
    #         messagebox.showwarning("Invalid port: conversion error.")
    #         return
        
    #     if self.dst_ip.get() not in self.hosts_display:
    #         if self.validate_ip_or_domain(self.dst_ip.get()) == False:
    #             messagebox.showwarning(f"Invalid address", "The address must either: \n1. Be on the list, \n2. Be an IP (8.8.8.8), \n3. Be a domain (www.google.com.br).")
    #             return
    #         else: # se for fora da lista de hosts do cenário, por enquanto só é possível realizar testes de ping.
    #             if self.protocol.get() != "ICMP":
    #                 messagebox.showwarning(f"Invalid protocol", "Unfortunately, in this version, only ICMP (ping) can be used to test external hosts.")
    #                 return
    #     # TODO - se for alterado o destino, nesta versão do sistema só pode utilizar o protocolo icmp, não dá para utilizar tcp ou udp, pq o servidor (se existir) não vai reconhecer a mensagem enviada.
    #     # Se todos os campos estiverem preenchidos, chama o método adicionar_editar_teste
    #     self.adicionar_editar_teste()
    
    def firewall_tests_update_tree(self):
        """
            Updates the treeview of tests in the firewall, in firewall tests tab.
        """
        itens = self.tree.get_children()

        for item in itens:
            self.tree.item(item, tags="")  # Sets tags to an empty list
        # TODO - I don't know if it's interesting to do the results that demonstrate the test results - I don't think so!

    def extract_ip_parenthesized_from_string(self,string):
        """
            Extract IPs from a string, this method expects the IP to be in parentheses, which is the host format presented in the comboboxes of the firewall testing tab. 
            So the string will be something like: Host1 (10.0.0.1), the method will return only 10.0.0.1. Only IPv4.

            Args:
                string: String to be parsed for IP
        """
        match = re.search(r'\((\d+\.\d+\.\d+\.\d+)\)', string)
        return match.group(1) if match else None
    
    def extract_ip_from_string(self, string):
        """
            Extract IPs from a string. Only IPv4.
            Args:
                string: String to be parsed for IP
        """
        match = re.search(r'\(?(\d+\.\d+\.\d+\.\d+)\)?', string)  
        return match.group(1) if match else None
    
    def extract_domain(self, string):
        """
            Extract domain from a string. This method expects two or more words separated by a dot - this method is not perfect.
            Args:
                string: String to be parsed for domain
        """
        match = re.search(r'\(?([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\)?', string)
        return match.group(1) if match else None
    
    def extract_destination_host(self, destination):
        """
            Extract the target host.

            Args:
                dst_ip: destination, can be a IP, host (IP) or a domain.
        """
        temp_destination =  self.extract_ip_parenthesized_from_string(destination)
        #print(f"temp_dst_ip {temp_destination}")

        if temp_destination != None:
            destination = temp_destination
        else:
            # without parentheses
            temp_destination = self.extract_ip_from_string(destination)
            if temp_destination != None:
                destination = temp_destination
            else:
                # dpmain
                temp_destination = self.extract_domain(destination)
                if temp_destination != None:
                    destination = temp_destination
                else:
                    # invalid
                    print(f"\033[33mCould not extract the destination IP in the interface:\n\tThe destination address must be an IP or domain, such as: 8.8.8.8 or www.google.com.\033[0m")
                    return None
        return destination    
    
    def firewall_tests_run_test_line(self):
        """
            Test only one row of the firewall test table. This row will be the currently selected row in the firewall test tree.
        """
        selected_item = self.tree.selection()
        if selected_item:
            values = self.tree.item(selected_item, "values")
            print(f"Items to testing:: {values}")
            teste_id, container_id, src_ip, dst_ip, protocol, src_port, dst_port, expected, result, dnat, observation = values
            
            # if you were unable to extract the destination IP entered by the user to
            dst_ip = self.extract_destination_host(dst_ip)
            if dst_ip == None: return
            
            print(f"Test executed - Container ID: {container_id}, Dados: {src_ip} -> {dst_ip} [{protocol}] {src_port}:{dst_port} (Expected: {expected})")

            result_str = containers.run_client_test(container_id, dst_ip, protocol.lower(), dst_port, "1", "2025", "0")

            try:
                result = json.loads(result_str)
                print(f"The return of the command on the host is {result_str}")
            except (json.JSONDecodeError, TypeError) as e:
                print("Error processing JSON received from host:", e)
                messagebox.showerror("Error", "Could not get a response from the hosts! \n Is GNS3 or the hosts turned on?")
                result = None
                return

            self.firewall_tests_analyse_results_update_tree(expected, result, values, selected_item)
            self.tree.selection_set(())
        

    def firewall_tests_analyse_results_update_tree(self, expected, result, values, selected_item):
        """
            Analyze the test result and update the table with the fields and colors that represent these results in the firewall test tree.

            Args:
                expected: result that was expected from the test.
                result: result obtained in the test.
                values: values ​​used and obtained in the test, such as source, destination, etc. are the columns of the firewall test treeview.
                selected_item: Test line used and which will have its values ​​and color updated in the firewall test table.
        """
        # TODO - check whether all cases have been covered
        # TODO - improve logic for checking user errors - such as testing a port that is not connected!
        #print(values)
        update_values = list(values)
        tag = None

        if result["server_response"] == True: # if the server responded then put sent/receved, otherwise just Sent - TODO - there may be a case where it didn't even send, which would be the case of the error!
                    update_values[9] = "Sent/Receved" # The package was just sent and there was a response!
                    update_values[8] = "Pass"
        else:
                    update_values[9] = "Sent" # The package was just sent but there was no response!
                    update_values[8] = "Fail"

        network_data = result['client_ip']+':'+str(result['client_port'])+'->'+result['server_ip']+':'+str(result['server_port'])+'('+result['protocol']+')'+' - Server response? '+ str(result['server_response'])+ ' - Status: '+result['status_msg']
        update_values[-1] = network_data

        if (result["status"] != '0'):
            # an error occurred, such as the host network was not configured.
            print(f"\033[33mThere was an error with the host when sending the packet, such as a misconfigured network - IP, GW, etc.\033[0m")
            update_values[8] = "ERROR"
            update_values[9] = "Not Sent"
            tag = "error"
        elif (result["server_response"] == True and expected == "yes"):
            # test performed successfully and there was a response from the server.
            print(f"\033[32mThe SUCCESS test occurred as expected.\033[0m")
            tag = "yes"
        elif (result["server_response"] == False and expected == "no"):
            # # The packet sending test failed, but this was expected in the test, so this is a success!
            print(f"\033[32mThe FAIL test occurred as expected.\033[0m")
            tag = "yesFail"
        else: # TODO - I think the logic is wrong here (check the possible cases) - is that in client.py you had to remove status=1 because it said there was an error in a packet blocked by the firewall!
            print(f"\033[31mThe test did NOT occur as expected.\033[0m")
            tag = "no"


        if "dnat" in result: # dnat only happens if there is a response from the server so there is no need for result["server_response"] == True - this comes from server.py
                #print("dnat")
                # there was DNAT
                dnat_data = result["dnat"]
                network_data = result['client_ip']+':'+str(result['client_port'])+'->'+dnat_data['ip']+':'+str(dnat_data['port'])+'('+result['protocol']+')'+' - Server response? '+ str(result['server_response'])+ ' - Status: '+result['status_msg']
                update_values[-1] = network_data
                update_values[9] = "Sent/Receved (DNAT)"
        
        # update the test line in the firewall test tree.
        self.tree.item(selected_item, values=update_values, tags=(tag,))
        
        
    
    def firewall_tests_popup_for_run_all_tests_using_threads(self):
        """
            Starts a window with a progress bar that executes all the tests in the firewall test tree. Threads are used for the progress bar to work.
        """
        print("Thread to execute all tests.")
        popup_window = tk.Toplevel(self.root)
        popup_window.title("Processing...")
        popup_window.geometry("300x120")
        popup_window.resizable(False, False)
        
        status_label = tk.Label(popup_window, text="Starting...", font=("Arial", 10))
        status_label.pack(pady=10)

        progress_bar = tk.IntVar()
        barra_progresso = ttk.Progressbar(popup_window, length=250, mode="determinate", variable=progress_bar)
        barra_progresso.pack(pady=5)

        self.tree.selection_set(())
        self.firewall_tests_update_tree()

        threading.Thread(target=self.firewall_tests_run_all_tests, args=(popup_window, progress_bar, status_label), daemon=True).start()
    
    def firewall_tests_run_all_tests(self, popup_window, progress_bar, status_label):
        """
            Run a all tests in the firewall test treeview.

            Args:
                popup_window: Pop up window used to show tests progress.
                progress_bar: Progress bar used in the popup to show tests progresses.
                status_label: Label used in the popup to show the tests progress.
        """
        index=0
        
        itens = self.tree.get_children()

        total_list = len(itens)
        for test in itens:
            values = self.tree.item(test, "values")
            teste_id, container_id, src_ip, dst_ip, protocol, src_port, dst_port, expected, result, dnat, observation = values
            print(f"Executing test - Container ID:  {container_id}, Data: {src_ip} -> {dst_ip} [{protocol}] {src_port}:{dst_port} (Expected: {expected})")
            
            # if you were unable to extract the destination IP entered by the user to
            dst_ip = self.extract_destination_host(dst_ip)
            if dst_ip == None: return

            print(f"Executing test - Container ID:  {container_id}, Data: {src_ip} -> {dst_ip} [{protocol}] {src_port}:{dst_port} (Expected: {expected})")

            result_str = containers.run_client_test(container_id, dst_ip, protocol.lower(), dst_port, "1", "2025", "0")

            try:
                result = json.loads(result_str)
            except (json.JSONDecodeError, TypeError) as e:
                print("Error processing the JSON received from the host:", e)
                messagebox.showerror("Error", "Unable to get a response from the hosts! \n Is GNS3 or the hosts running?")
                result = None
                return

            self.firewall_tests_analyse_results_update_tree(expected,result, values, test)

            index+=1
            percentage_compete = (index / total_list) * 100
            progress_bar.set(percentage_compete)  # Update progress bar
            status_label.config(text=f"Processing... {index}/{total_list}")
            

        status_label.config(text="Task completed!")
        progress_bar.set(100)  # Ensures the bar goes all the way to the end
        popup_window.destroy()


    def hosts_start_servers(self):
        """
            Start all the servers in the containers, use server.py for this.
        """
        #print("start_servers")
        # TODO - check if there was an error when starting the server and in which container.
        for container in self.containers_data:
            container_id = container["id"]
            containers.start_server(container_id)

        for cid, btn, label_status in self.list_button_servers_onOff:
            #print(f"cid/btn {cid} - {btn}")
                btn.config(image=self.power_icon, text="liga")
                status = self.host_check_server_on_off(container_id)
                label_status.config(text=f"Server Status: {status}", font=("Arial", 10))
        
    def hosts_update(self):
        """
            Updates all host/container data - checks for example if any container was created or deleted, if any network configuration changed, etc.
        """
        #print("update_hosts")

        for widget in self.canva_hosts.winfo_children():
            widget.destroy()

        self.containers_data = containers.extract_containerid_hostname_ips( )  # get hosts information (hostname, interfaces, ips)

        # get container_id and hostname - used for example to combobox in firewall rules.
        self.container_hostname = containers.get_containerid_hostname() # container_id and hostname for operations
        self.hosts = list(map(lambda x: x[1], self.container_hostname)) # hostnames to display
        self.combobox_firewall_rules_host['values']=self.hosts # update combobox values

        #print(self.hosts)

        self.hosts_show_host_informations_in_host_tab( )

        # List of values ​​displayed in Combobox (hostname + IP)
        if self.containers_data:
            self.hosts_display = [f"{c['hostname']} ({c['ip']})" for c in self.containers_data]
        else: # if there are no elements it displays a message
            self.hosts_display = ["HOSTS (0.0.0.0)", "HOSTS (0.0.0.0)"]
            messagebox.showerror("Error", "Unable to get a response from the hosts! \n Is GNS3 or the hosts running?")
        self.src_ip["values"] = self.hosts_display
        self.dst_ip["values"] = self.hosts_display
        self.src_ip.current(0)
        if len(self.containers_data) > 1: # checks if there is more than one element in the host list, if there isn't, you can't set the second one as default.
            self.dst_ip.current(1)
        else:
            self.dst_ip.current(0)

        #self.root.update_idletasks() # was commented, as there was a problem with the hosts tab.

    def host_check_server_on_off(self, container_id):
        """
            Checks if the server is on or off (server is serve.py in each container/host).

            Args:
                container_id: Container ID.
        """
        #print(f"Check if server is on or off at container {container_id}")
        cmd = 'docker exec '+ container_id+' ps ax | grep "/usr/local/bin/python ./server.py" | grep -v grep'
        result = containers.run_command_shell(cmd)
        if result !="":
            return "on"
        else:
            return "off"


    def host_toggle_server_and_button_between_onOff(self, container_id, button_on_off):
        """
            Toggles between on and off in the hosts tab (toggles the button)

            Args:
                container_id: Conteriner ID to start or stop server.
                button_on_off: Button on/off to be changed between on and off. 
        """
        print(f"Toggling server for container ID: {container_id}")  
        # Find the corresponding button in the list and change the image
        for cid, button_on_off, label_status in self.list_button_servers_onOff:
            #print(f"container_id/button {cid} - {button_on_off}")
            if cid == container_id:
                current_image = button_on_off["image"][0]
                if current_image == str(self.power_icon):
                    #print("off")
                    label_status.config()
                    containers.stop_server(container_id)
                    button_on_off.config(image=self.power_icon_off)
                else:
                    #print("on")
                    containers.start_server(container_id)
                    button_on_off.config(image=self.power_icon, text="liga")
                status = self.host_check_server_on_off(container_id)
                label_status.config(text=f"Server Status: {status}", font=("Arial", 10))
                break

                
    # TODO - the host tab should have a scroll, as there may be more hosts than fit on the tab!


    def firewall_tests_save_tests_as(self):
        """
            Opens a window to save the tests as to a JSON file.
        """
        file_path = filedialog.asksaveasfilename(
            title="Save test file",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if not file_path:  # If the user cancels, do nothing
            return

        self.save_file_path = file_path

        #print(f"Saving in the file: {self.save_file_path}")
        self.firewall_tests_save_tests()

    def firewall_tests_save_tests(self):
        """
            Saves the Treeview data to a JSON file.
        """
        print("Saving tests...")
        if not self.save_file_path:
            self.firewall_tests_save_tests_as()
        else:
            items = self.tree.get_children()
            tests_data = []

            for item in items:
                values = self.tree.item(item, "values")
                if values:
                    # Recover the hidden Container ID
                    #teste_id = values[0]
                    #container_id = self.hidden_data.get(teste_id, "")  
                    teste_id, container_id, src_ip, dst_ip, protocol, src_port, dst_port, expected, result, dnat, observation = values

                    # Create the dictionary and add it to the list
                    tests_data.append({
                        "teste_id": teste_id,
                        "container_id": container_id,
                        "src_ip": src_ip,
                        "dst_ip": dst_ip,
                        "protocol": protocol,
                        "src_port": src_port,
                        "dst_port": dst_port,
                        "expected": expected,
                        "result": result,
                        "flow": dnat,
                        "data": observation
                    })

            # Write to JSON file
            with open(self.save_file_path, "w") as f:
                json.dump(tests_data, f, indent=4)

            print(f"Tests successfully saved in file: {self.save_file_path}")

    # TODO - When loading, you have to check if the source still has the same container ID - because if it is on different machines or in different GNS3 projects - the container ID will change!
    # TODO - I would also have to see if the IPs still match, because in class, the teacher usually gives the name of the machine and not the IP, so I would have to check if the IPs are the same, if they are not, I would have to update the IP, probably with user interaction if the host has more than one IP (choose which IP is for the test, especially if it is the destination - at the source this will not make much difference)
    
    def firewall_tests_load_tests_from_file(self):
        """
            Loads data from the JSON file into the Treeview.
        """
        print("Loading tests...")

        if os.path.exists(self.save_file_path):
            with open(self.save_file_path, "r") as f:
                try:
                    tests_data = json.load(f)
                except json.JSONDecodeError:
                    print("Error loading the JSON file.")
                    return

            # Add items to the Treeview

            for test in tests_data:

                source = self.extract_hostname(test["src_ip"])
                print(f"test source: {source}")
                container_id = self.find_container_id(source)
                if container_id:
                    item_id = self.tree.insert("", "end", values=[
                        test["teste_id"], container_id, test["src_ip"], test["dst_ip"], test["protocol"],
                        test["src_port"], test["dst_port"], test["expected"], test["result"], test["flow"], test["data"]
                    ])
                else:
                    # If the source host loaded from the file does not exist in the network scenario, prompt the user to find a new matching host, or ignore and do not include this test line.
                    # TODO - Perhaps it would be necessary to check if the hosts' IPs are the same as the loaded test, if not the user could be asked to change the IP by choosing from a list.
                    container_id, selected_host = self.ask_user_for_source_host(test["src_ip"], self.hosts_display, test)
                    
                    if selected_host is not None:
                        item_id = self.tree.insert("", "end", values=[
                            test["teste_id"], container_id, selected_host, test["dst_ip"], test["protocol"],
                            test["src_port"], test["dst_port"], test["expected"], test["result"], test["flow"], test["data"]
                        ])
                    else:
                        print(f"Test {test} ignored by user.")

            print("Tests successfully loaded!")
            self.firewall_tests_buttons_set_normal_state()
        else:
            print("No test files found.")
    
    def ask_user_for_source_host(self, source, available_hosts, test):
        """
        Opens a dialog to ask the user to select a host if no container_id is found during load file test process,
        displaying the test details.

        Args:
            source: the old source hostname, which was not found when the test was loaded from the file.
            available_hosts: list of host names available in the current network scenario.
            test: test data.

        Returns: Container id and hostname of the new source host that was chosen in the interface by the user.
        """
        dialog = tk.Toplevel(self.root)
        dialog.title("Select Host")
        dialog.geometry("400x400")
        dialog.transient(self.root)  
        dialog.grab_set()  # block main window

        warning_text = ("Attention: When trying to load the test from the file, "
                    "no host was found matching the source hostname. "
                    "Please select a host from the list that corresponds "
                    "to the source host of the test, or ignore it to discard this test entry.")
        ttk.Label(dialog, text=warning_text, wraplength=380, justify="left", font=("Arial", 10, "bold")).pack(pady=5)
        
        test_info = (f"Test data:\n"
                    f"\tTest ID: {test['teste_id']}\n"
                    f"\tSource: {test['src_ip']}\n"
                    f"\tDestination: {test['dst_ip']}\n"
                    f"\tProtocol: {test['protocol']}\n"
                    f"\tSource Port: {test['src_port']}\n"
                    f"\tDestination Port: {test['dst_port']}\n"
                    f"\tExpected success for the test: {test['expected']}")
        ttk.Label(dialog, text=test_info, justify="left").pack(pady=5)

        ttk.Label(dialog, text=f"Then the source host ({source})\n" 
                                f"was not found in the test scenario.\n"
                                f"Please select a corresponding host or ignore.").pack(pady=5)
        
        host_var = tk.StringVar()
        combobox = ttk.Combobox(dialog, textvariable=host_var, values=available_hosts, state="readonly", width=30)
        combobox.pack(pady=5)
        combobox.set(available_hosts[0] if available_hosts else "")

        selected_host = None
        container_id = None

        def on_select():
            nonlocal selected_host
            nonlocal container_id
            selected_host = host_var.get()
            hostname = self.extract_hostname(selected_host)
            container_id = self.find_container_id(hostname)
            print(f"container_id on select {container_id}")
            #selected_host = self.replace_hostname(source, selected_host)
            dialog.destroy()

        def on_ignore():
            nonlocal selected_host
            selected_host = None
            dialog.destroy()

        ttk.Button(dialog, text="Select", command=on_select).pack(side="left", padx=10, pady=10)
        ttk.Button(dialog, text="Ignore", command=on_ignore).pack(side="right", padx=10, pady=10)

        dialog.wait_window()  # wait closing window
        
        return container_id,selected_host

    def replace_hostname(self, old_hostname, new_hostname):
        """
        Changes the old source hostname to the new one, preserving the old IP.

        Args:
            old_hostname: Old hostname - hostname (IP)
            new_hostname: New hostname - newhostname
        
        Returns: the old string with IP, but with the new name.
        """
        match = re.match(r"^(.*?) \((.*?)\)$", old_hostname)
        if match:
            return f"{new_hostname} ({match.group(2)})"
        return old_hostname  

    def extract_hostname(self, host_string):
        """
        Extracts the hostname from a string in the format "Host (address)".

        Args:
            host_string (str): The string containing the hostname and IP address.

        Returns:
            str: The hostname, or None if the string is not in the expected format.
        """
        try:
            hostname = host_string.split(" (")[0]
            return hostname
        except IndexError:
            return None  # Return None if the string is not in the expected format

    def find_container_id(self, search_hostname):
        """
        Finds the container_id associated with a hostname in the self.container_hostname list.

        Args:
            search_hostname (str): The hostname to search for.

        Returns:
            str or None: The container_id if the hostname is found, or None if not found.
        """
        for container_id, hostname in self.container_hostname:
            if hostname == search_hostname:
                return container_id
        return None  # Return None if hostname is not found

    def firewall_tests_open_test_file(self):
        """
            Opens a window to select a JSON file and load the tests.
        """
        file_path = filedialog.askopenfilename(
            title="Open test file",
            filetypes=[("JSON file", "*.json"), ("All files", "*.*")]
        )

        if not file_path:  # If the user cancels, it does nothing.
            return

        self.save_file_path = file_path

        print(f"Loading tests from file: {file_path}")

        self.firewall_tests_load_tests_from_file()
    

    def confirm_software_exit(self):
        """
            A window opens asking if you really want to exit the firewall tester program.
        """
        if messagebox.askyesno("Confirmation", "Do you really want to exit the program?"):
            self.root.destroy()

# Running the Firewall Tester application
if __name__ == "__main__":
    root = tk.Tk()
    app = FirewallGUI(root)
    root.mainloop()
