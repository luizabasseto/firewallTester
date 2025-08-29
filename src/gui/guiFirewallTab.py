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
