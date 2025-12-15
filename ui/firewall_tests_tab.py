"""
Defines the 'Firewall Tests' tab for the Firewall Tester application.

This tab allows users to create, manage, and run a series of network tests
against the containers to verify firewall rules. It supports saving and
loading test suites.
"""

import json
import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QGroupBox, QGridLayout, QLineEdit,
    QRadioButton, QTreeWidget, QTreeWidgetItem,
    QAbstractItemView, QProgressDialog, QMessageBox, QFileDialog, QDialog)
from PyQt5.QtGui import QColor, QBrush
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QObject, QEvent

class TestWorker(QObject):
    """A worker that runs firewall tests in a separate thread."""
    progress = pyqtSignal(int, str)
    item_tested = pyqtSignal(QTreeWidgetItem, dict, str)
    finished = pyqtSignal()

    def __init__(self, test_items, test_runner, hosts_map, parent=None):
        super().__init__(parent)
        self.test_items = test_items
        self.test_runner = test_runner
        self.hosts_map = hosts_map 
        self.is_cancelled = False
    def run(self):
        """Executes the test items and emits signals for progress and results."""
        total = len(self.test_items)
        for i, item in enumerate(self.test_items):
            if self.is_cancelled:
                break
            
            progress_msg = f"Testing {i+1}/{total}: {item.text(2)} -> {item.text(3)}"
            self.progress.emit(int(((i + 1) / total) * 100), progress_msg)

            _, container_id, _, dst_hostname, proto, _, dst_port, expected, _, _, _ = [
                item.text(c) for c in range(item.columnCount())
            ]
            
            destination_ip = dst_hostname
            clean_name = dst_hostname.split(' (')[0].strip()
            
            found = False
            for data in self.hosts_map.values():
                if data['hostname'] == clean_name:
                    destination_ip = data['ip']
                    found = True
                    break
            if not found and dst_hostname in self.hosts_map:
                destination_ip = self.hosts_map[dst_hostname]['ip']

            effective_port = "1" if proto.upper() == "ICMP" else dst_port

            _, result_dict = self.test_runner.run_single_test(container_id, destination_ip, proto, effective_port)
            
            if self.is_cancelled:
                break
            
            analysis, tag = self.test_runner.analyze_test_result(expected, result_dict)
            self.item_tested.emit(item, analysis, tag)
            
            
        self.finished.emit()

    def cancel(self):
        """Flags the worker to stop processing tests."""
        self.is_cancelled = True

class FirewallTestsTab(QWidget):
    """
    A QWidget that provides the UI for creating, running, and managing firewall tests.
    """
    # R0902: Pylint flags too many attributes. This is common for UI classes
    # where widgets are stored as instance attributes for later access.
    # R0903: This class has few public methods as it's primarily a display
    # widget updated by the main window, which is an acceptable design.
    def __init__(self, test_runner, hosts_data, config, parent=None):
        super().__init__(parent)
        self.test_runner = test_runner
        self.hosts_data = hosts_data
        self.hosts_map = {host['hostname']: host for host in hosts_data}
        self.config = config
        self.save_file_path = None
        self.is_editing = False

        # W0201: Initialize thread-related attributes to None
        self.progress_dialog = None
        self.thread = None
        self.worker = None

        self._setup_ui()
        self.update_hosts_list(hosts_data)
        self._set_buttons_normal_state()

    # R0915: This method is long, but it's a standard pattern for UI setup.
    # It could be broken down further, but is kept this way for clarity.
    def _setup_ui(self):
        main_layout = QVBoxLayout(self)

        input_box = QGroupBox("New test")
        input_layout = QGridLayout(input_box)
        main_layout.addWidget(input_box)

        self.src_ip_combo = QComboBox()
        self.src_ip_combo.setMinimumWidth(100)
        self.dst_ip_combo = QComboBox()
        self.dst_ip_combo.setMinimumWidth(100)
        self.dst_ip_combo.setEditable(True)
        self.protocol_combo = QComboBox()
        self.protocol_combo.addItems(["TCP", "UDP", "ICMP"])
        self.src_port_entry = QLineEdit("*")
        self.src_port_entry.setEnabled(False)
        self.dst_port_entry = QLineEdit("80")
        self.dst_port_entry.setMaximumWidth(50)
        self.expected_yes_radio = QRadioButton("Allowed")
        self.expected_no_radio = QRadioButton("Blocked")
        self.expected_yes_radio.setChecked(True)
        expected_layout = QHBoxLayout()
        expected_layout.addWidget(self.expected_yes_radio)
        expected_layout.addWidget(self.expected_no_radio)

        input_layout.addWidget(QLabel("Source:"), 0, 0)
        input_layout.addWidget(self.src_ip_combo, 1, 0)
        input_layout.addWidget(QLabel("Destination:"), 0, 1)
        input_layout.addWidget(self.dst_ip_combo, 1, 1)
        input_layout.addWidget(QLabel("Protocol:"), 0, 2)
        input_layout.addWidget(self.protocol_combo, 1, 2)
        input_layout.addWidget(QLabel("Dst Port:"), 0, 3)
        input_layout.addWidget(self.dst_port_entry, 1, 3)
        input_layout.addWidget(QLabel("Expected result:"), 0, 4)
        input_layout.addLayout(expected_layout, 1, 4)

        buttons_layout = QHBoxLayout()
        main_layout.addLayout(buttons_layout)
        self.btn_add = QPushButton("Add")
        self.btn_edit = QPushButton("Edit")
        self.btn_del = QPushButton("Delete")
        self.btn_del_all = QPushButton("Delete all")
        self.btn_test = QPushButton("Test selected")
        self.btn_test_all = QPushButton("Test all")

        buttons_layout.addStretch(1)
        buttons_layout.addWidget(self.btn_add)
        buttons_layout.addWidget(self.btn_edit)
        buttons_layout.addWidget(self.btn_del_all)
        buttons_layout.addWidget(self.btn_del)
        buttons_layout.addWidget(self.btn_test)
        buttons_layout.addWidget(self.btn_test_all)
        buttons_layout.addStretch(1)

        self.tree = QTreeWidget()
        self.tree.setSelectionMode(QAbstractItemView.SingleSelection)
        self.header_labels = ["#","Container ID","Source","Destination","Protocol","Src Port","Dst Port",
            "Expected","Result","Flow","Data"
        ]

        self.tree.setHeaderLabels(self.header_labels)
        main_layout.addWidget(self.tree)
        self.tree.setColumnWidth(0, 40)
        self.tree.setColumnHidden(1, not self.config.get("show_container_id", False))
        self.tree.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tree.viewport().installEventFilter(self)

        legend_box = QGroupBox("Legend")
        legend_layout = QHBoxLayout(legend_box)
        main_layout.addWidget(legend_box)
        def add_legend_item(color, text):
            label_color = QLabel()
            label_color.setFixedSize(16, 16)
            label_color.setStyleSheet(f"background-color: {color}; border: 1px solid black;")
            legend_layout.addWidget(label_color)
            legend_layout.addWidget(QLabel(text))
            legend_layout.addSpacing(15)

        add_legend_item("lightgreen", "Passed (Allowed)")
        add_legend_item("lightblue", "Passed (Blocked)")
        add_legend_item("salmon", "Failed")
        add_legend_item("yellow", "Error")
        legend_layout.addStretch(1)

        file_buttons_layout = QHBoxLayout()
        main_layout.addLayout(file_buttons_layout)
        self.btn_save = QPushButton("Save tests")
        self.btn_save_as = QPushButton("Save as...")
        self.btn_load = QPushButton("Open tests")

        file_buttons_layout.addStretch(1)
        file_buttons_layout.addWidget(self.btn_save)
        file_buttons_layout.addWidget(self.btn_save_as)
        file_buttons_layout.addWidget(self.btn_load)
        file_buttons_layout.addStretch(1)

        self.btn_add.clicked.connect(self._add_test)
        self.btn_edit.clicked.connect(self._edit_test)
        self.btn_del_all.clicked.connect(self._delete_all_test)
        self.btn_del.clicked.connect(self._delete_test)
        self.btn_test.clicked.connect(self._run_selected_test)
        self.btn_test_all.clicked.connect(self._run_all_tests)
        self.tree.itemSelectionChanged.connect(self._on_item_selected)
        self.tree.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.btn_save.clicked.connect(self._save_tests)
        self.btn_save_as.clicked.connect(self._save_tests_as)
        self.btn_load.clicked.connect(self._open_tests)
        

    def _run_selected_test(self):
        selected_items = self.tree.selectedItems()
        if not selected_items:
            return
        item = selected_items[0]

        _, container_id, _, dst_hostname, proto, _, dst_port, expected, _, _, _ = [
            item.text(c) for c in range(item.columnCount())
        ]
        
        destination_ip = self._find_ip_by_hostname(dst_hostname)
        
        effective_port = "1" if proto.upper() == "ICMP" else dst_port
        
        _, result_dict = self.test_runner.run_single_test(container_id, destination_ip, proto, effective_port)
        analysis, tag = self.test_runner.analyze_test_result(expected, result_dict)

        self._update_tree_item(item, analysis, tag)
        

    def _update_tree_item(self, item, analysis_dict, tag):
        if self.progress_dialog and not self.progress_dialog.isVisible():
            return
        
        print("\n Test execution results:")
        print(f"Container ID: {item.text(1)}")
        print(f"Source: {item.text(2)} -> Destination: {item.text(3)}")
        print(f"Transmission details: {analysis_dict['data']}")


        item.setText(8, analysis_dict['result'])
        item.setText(9, analysis_dict['flow'])
        item.setText(10, analysis_dict['data'])

        color_map = {
            "yes": "lightgreen", "yesFail": "lightblue",
            "no": "salmon", "error": "yellow"
        }
        color = QColor(color_map.get(tag, "transparent"))
        for i in range(item.columnCount()):
            item.setBackground(i, QBrush(color))
        self._clear_selection_and_reset_buttons()

    def _run_all_tests(self):
        tests_to_run = [self.tree.topLevelItem(i) for i in range(self.tree.topLevelItemCount())]
        if not tests_to_run:
            print("No tests to run.")
            return
        
        self.tree.clearSelection()
        self.progress_dialog = QProgressDialog("Running tests", "Cancel", 0, 100, self)
        self.progress_dialog.setWindowTitle("Processing tests")
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.setMinimumDuration(0)
        self.progress_dialog.setAutoClose(False) 
        
        self.thread = QThread()
        self.worker = TestWorker(tests_to_run, self.test_runner, self.hosts_map)
        self.worker.moveToThread(self.thread)
        
        def on_cancel():
            self.worker.cancel()
            self.progress_dialog.close()
        
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.item_tested.connect(self._update_tree_item)
        self.worker.progress.connect(self._update_progress_dialog)
        self.progress_dialog.canceled.connect(on_cancel)
        self.thread.finished.connect(self.progress_dialog.close)
        

        self.thread.start()
        self.progress_dialog.exec_()
        
    def _update_progress_dialog(self, value, text):
        """Updates the progress dialog's value and label text."""
        self.progress_dialog.setValue(value)
        self.progress_dialog.setLabelText(text)

    def _add_test(self):
        if not self._validate_inputs():
            return

        src_text = self.src_ip_combo.currentText()
        container_id = self.hosts_map.get(src_text, {}).get('id', 'N/A')

        values = [
            str(self.tree.topLevelItemCount() + 1),
            container_id,
            src_text,
            self.dst_ip_combo.currentText(),
            self.protocol_combo.currentText(),
            self.src_port_entry.text(),
            self.dst_port_entry.text(),
            "Allowed" if self.expected_yes_radio.isChecked() else "Blocked",
            "-", "", ""
        ]

        new_item = QTreeWidgetItem(values)
        self.tree.addTopLevelItem(new_item)
        self._clear_selection_and_reset_buttons()
    
    def _edit_test(self):
        if not self.is_editing:
            selected_items = self.tree.selectedItems()
            if not selected_items:
                return
            self.is_editing = True
            self.btn_edit.setText("Save edit")
            self.btn_add.setEnabled(False)
            self.btn_del.setEnabled(False)
            self.btn_del_all.setEnabled(False)
            self.btn_test.setEnabled(False)
            self.btn_test_all.setEnabled(False)
            self.tree.setEnabled(False)            
            self.src_ip_combo.setFocus()
            
        else:
            if not self._validate_inputs():
                return

            item = self.tree.selectedItems()[0]
            
            src_text = self.src_ip_combo.currentText()
            container_id = self.hosts_map.get(src_text, {}).get('id', 'N/A')

            item.setText(1, container_id)
            item.setText(2, src_text)
            item.setText(3, self.dst_ip_combo.currentText())
            item.setText(4, self.protocol_combo.currentText())
            item.setText(6, self.dst_port_entry.text())
            item.setText(7, "Allowed" if self.expected_yes_radio.isChecked() else "Blocked")
            
            for i in range(8, 11):
                item.setText(i, "" if i > 8 else "-")
                item.setBackground(i, QBrush(QColor("transparent")))
            
            self.is_editing = False
            self.btn_edit.setText("Edit")
            self.tree.setEnabled(True)           
            self._clear_selection_and_reset_buttons()
            
    def _delete_all_test(self):
        if self.tree.topLevelItemCount() == 0:
            return

        reply = QMessageBox.question(self, "Delete all tests", 
            "Are you sure you want to delete ALL tests from the list?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.tree.clear() 
            self._set_buttons_normal_state()

    def _delete_test(self):
        selected_items = self.tree.selectedItems()
        if not selected_items:
            return

        reply = QMessageBox.question(self, "Delete test", 
            "Are you sure you want to delete the selected test?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            item = selected_items[0]
            self.tree.takeTopLevelItem(self.tree.indexOfTopLevelItem(item))
            self._renumber_tests()
            self._set_buttons_normal_state()

    def _renumber_tests(self):
        for i in range(self.tree.topLevelItemCount()):
            self.tree.topLevelItem(i).setText(0, str(i + 1))
    def _on_item_double_clicked(self):
        self.src_ip_combo.setFocus()
        self._edit_test()
        
    def _on_item_selected(self):
        selected_items = self.tree.selectedItems()
        if not selected_items:
            self._set_buttons_normal_state()
            return

        item = selected_items[0]
        self.src_ip_combo.setCurrentText(item.text(2))
        self.dst_ip_combo.setCurrentText(item.text(3))
        self.protocol_combo.setCurrentText(item.text(4))
        self.dst_port_entry.setText(item.text(6))
        
        if item.text(7).lower() == "yes":
            self.expected_yes_radio.setChecked(True)
        else:
            self.expected_no_radio.setChecked(True)

        self.btn_edit.setText("Edit")
        self.btn_edit.setEnabled(True)
        self.btn_del_all.setEnabled(True)
        self.btn_del.setEnabled(True)
        self.btn_test.setEnabled(True)

    def _validate_inputs(self):
        try:
            port = int(self.dst_port_entry.text())
            if not (1 <= port <= 65535):
                QMessageBox.warning(self, "Invalid input", "The destination port must be a number between 1 and 65535.")
                return False
        except ValueError:
            if self.protocol_combo.currentText() != "ICMP":
                QMessageBox.warning(self, "Invalid input", "The destination port must be a number.")
                return False

        destination = self.dst_ip_combo.currentText()
        known_hosts = [self.src_ip_combo.itemText(i) for i in range(self.src_ip_combo.count())]

        if destination not in known_hosts:
            # pylint: disable=protected-access
            if not self.test_runner._extract_destination_host(destination):
                QMessageBox.warning(self, "Invalid destination",
                                    "The destination must be a host from the list, a valid IP address, or a domain.")
                return False

            if self.protocol_combo.currentText() != "ICMP":
                QMessageBox.warning(self, "Invalid Protocol for external destination", "Only the ICMP protocol (ping) can be used for external destinations.")
                return False

        return True

    def _set_buttons_normal_state(self):
        """Resets input fields and button states to their default."""
        
        self.btn_add.setEnabled(True)
        self.btn_edit.setEnabled(False)
        self.btn_del_all.setEnabled(True)
        self.btn_del.setEnabled(False)
        self.btn_test.setEnabled(False)
        self.btn_test_all.setEnabled(self.tree.topLevelItemCount() > 0)
        
        self.is_editing = False
        self.btn_edit.setText("Edit")
        self.tree.setEnabled(True)

    def update_hosts_list(self, hosts_data_tuples):
        """Updates the host dropdowns with the latest list of available hosts."""
        self.hosts_data_list = hosts_data_tuples
        self.hosts_map = {}
        display_names = []

        for host in self.hosts_data_list:
            hostname = host.get('hostname', 'N/A')
            host_id = host.get('id', 'N/A')
            raw_ips = host.get('ip', 'N/A')

            if raw_ips and raw_ips != 'N/A':
                ip_list = [ip.strip() for ip in raw_ips.split(',')]
            else:
                ip_list = ['N/A']

            for ip in ip_list:
                if ip == 'N/A':
                    display_text = hostname
                    ip_to_store = hostname
                else:
                    display_text = f"{hostname} ({ip})"
                    ip_to_store = ip

                display_names.append(display_text)

                self.hosts_map[display_text] = {
                    'id': host_id,
                    'hostname': hostname,
                    'ip': ip_to_store 
                }

        current_src = self.src_ip_combo.currentText()
        current_dst = self.dst_ip_combo.currentText()

        self.src_ip_combo.clear()
        self.src_ip_combo.addItems(display_names)
        
        self.dst_ip_combo.clear()
        self.dst_ip_combo.addItems(display_names)
        
        if current_src in display_names:
            self.src_ip_combo.setCurrentText(current_src)
        else:
            self.src_ip_combo.setCurrentIndex(-1)
            
        if current_dst in display_names:
            self.dst_ip_combo.setCurrentText(current_dst)
        else:
            self.dst_ip_combo.setCurrentIndex(-1)

    def _save_tests_as(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Save test file", 
            "",  
            "JSON Files (*.json);;All Files (*)"
        )
        

        if file_path:
            self.save_file_path = file_path
            self._save_tests()

    def _save_tests(self):
        if not self.save_file_path:
            self._save_tests_as()
            return

        tests_data = []
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            # Salvamos o header e o valor para cada coluna
            # Importante: salvar o hostname puro extraído da UI
            test_dict = {}
            for j, key in enumerate(self.header_labels):
                test_dict[key] = item.text(j)
            
            # Adicionalmente, vamos salvar explicitamente o hostname (sem IP) se possível
            # para facilitar a busca ao recarregar
            src_text = item.text(2) # Coluna Origem
            test_dict['src_hostname_only'] = self._extract_hostname_from_combo_text(src_text)
            
            tests_data.append(test_dict)

        try:
            with open(self.save_file_path, "w", encoding="utf-8") as f:
                json.dump(tests_data, f, indent=4, ensure_ascii=False)
            QMessageBox.information(self, "Sucess", f"Tests saved at:\n{self.save_file_path}")
        except (IOError, TypeError) as e:
            QMessageBox.critical(self, "Error", f"Could not save the file:\n{e}")

    def _open_tests(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Open test files", 
            "", 
            "JSON Files (*.json);;All Files (*)"
        )
        if file_path:
            self.save_file_path = file_path
            self._load_from_file()

    def _load_from_file(self):
        if not self.save_file_path or not os.path.exists(self.save_file_path):
            QMessageBox.warning(self, "Error", "Could not find load file.")
            return

        reply = QMessageBox.question(self, "Load testd", 
            "This action will clear all current tests in the table. Do you want to continue?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.No:
            return

        try:
            with open(self.save_file_path, "r", encoding="utf-8") as f:
                tests_data = json.load(f)

            self.tree.clear()
            replacements = {}
            total_tests = len(tests_data)
            was_aborted = False

            def resolve_host(hostname, current_idx):
                if not hostname: return "", ""

                new_id, new_display_text = self._find_container_data_by_hostname(hostname)
                if new_id:
                    return new_id, new_display_text

                if hostname in replacements:
                    return replacements[hostname]

                user_id, user_text, action = self._ask_user_for_source_host(
                        src_hostname, current_idx=i+1, total_count=total_tests
                    )

                if action == 'abort':
                    raise StopIteration("Aborted")
                elif action == 'update':
                    replacements[hostname] = (user_id, user_text)
                    return user_id, user_text
                
                else:
                    replacements[hostname] = (None, None)
                    return None, None

            for i, test in enumerate(tests_data):
                try:
                    src_hostname = test.get("src_hostname_only")
                    if not src_hostname:
                        src_hostname = self._extract_hostname_from_combo_text(test.get("Origem", ""))
                    
                    dst_orig_text = test.get("Dst", "")
                    dst_hostname = self._extract_hostname_from_combo_text(dst_orig_text)

                    final_src_id, final_src_text = resolve_host(src_hostname, i+1)
                    if final_src_id is None and src_hostname in replacements:
                        continue
                    final_dst_id, final_dst_text = resolve_host(dst_hostname, i+1)
                    
                    if not final_dst_text: 
                        final_dst_text = dst_orig_text

                    values = [
                        test.get("#", ""),
                        final_src_id,
                        final_src_text,
                        final_dst_text,
                        test.get("Protocol", ""),
                        test.get("Origin Port", ""),
                        test.get("Dst Port", ""),
                        test.get("Esperado", ""),
                        "-", "", ""
                    ]
                    self.tree.addTopLevelItem(QTreeWidgetItem(values))

                except StopIteration:
                    was_aborted = True
                    break

            if was_aborted:
                QMessageBox.information(self, "Canceled", "Import canceled by the user.")
            else:
                self._renumber_tests()
                self._set_buttons_normal_state()
                QMessageBox.information(self, "Success", "Tests loaded and synchronized.")

        except (IOError, json.JSONDecodeError) as e:
            QMessageBox.critical(self, "Error", f"Could not load the file:\n{e}")
            
    def _clear_selection_and_reset_buttons(self):
        self.tree.clearSelection()
        self._set_buttons_normal_state()
         
    def eventFilter(self, source, event):
        if event.type() == QEvent.MouseButtonPress and source is self.tree.viewport():
            item = self.tree.itemAt(event.pos())
            if item is None:
                self._clear_selection_and_reset_buttons()
        return super().eventFilter(source, event)
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape and self.is_editing:
            self._clear_selection_and_reset_buttons()
        else:
            super().keyPressEvent(event)
            
    def _extract_hostname_from_combo_text(self, text):
        return text.split(' (')[0] if ' (' in text else text

    def _find_container_data_by_hostname(self, search_hostname):
        for display_text, data in self.hosts_map.items():
            if data['hostname'] == search_hostname:
                return data['id'], display_text
        return None, None

    def _ask_user_for_source_host(self, source_hostname, current_idx=1, total_count=1):
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Resolving Host Conflicts ({current_idx} of {total_count})")
        dialog.setMinimumWidth(400)
        layout = QVBoxLayout(dialog)

        msg = (f"Warning: The source host '{source_hostname}' saved in the file"
                f"was not found in the current environment."
                f"Please select a corresponding host from the list below"
                f"to update the test,"
                f"or click 'Ignore' to skip this test.")
        layout.addWidget(QLabel(msg))

        combo = QComboBox()
        available_hosts = list(self.hosts_map.keys())
        combo.addItems(available_hosts)
        layout.addWidget(combo)
        
        result_state = {"id": None, "name": None, "action": "abort"}

        btn_layout = QHBoxLayout()
        btn_select = QPushButton("Select and update")
        btn_ignore = QPushButton("Ignore test")
        btn_canceled = QPushButton("Cancel all tests")
        btn_layout.addWidget(btn_select)
        btn_layout.addWidget(btn_ignore)
        btn_layout.addWidget(btn_canceled)
        layout.addLayout(btn_layout)

        def on_select():
            selected_text = combo.currentText()
            new_id = self.hosts_map.get(selected_text, {}).get('id')
            result_state["id"] = new_id
            result_state["name"] = selected_text
            result_state["action"] = "update"
            dialog.accept()

        def on_ignore():
            result_state["action"] = "skip"
            dialog.accept()
        
        def on_cancel():
            result_state["action"] = "abort"
            dialog.reject()

        btn_select.clicked.connect(on_select)
        btn_ignore.clicked.connect(on_ignore)
        btn_canceled.clicked.connect(on_cancel)
        
        dialog.exec_()
        return result_state["id"], result_state["name"], result_state["action"]
    
    def _find_ip_by_hostname(self, hostname):
        if hostname in self.hosts_map:
            return self.hosts_map[hostname]['ip']
            
        clean_hostname = hostname.split(' (')[0].strip()
        
        for data in self.hosts_map.values():
            if data['hostname'] == clean_hostname:
                return data['ip']

        return clean_hostname