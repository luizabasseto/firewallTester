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
    QAbstractItemView, QProgressDialog, QMessageBox, QFileDialog)
from PyQt5.QtGui import QColor, QBrush
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QObject

class TestWorker(QObject):
    """A worker that runs firewall tests in a separate thread."""
    progress = pyqtSignal(int, str)
    item_tested = pyqtSignal(QTreeWidgetItem, dict, str)
    finished = pyqtSignal()

    def __init__(self, test_items, test_runner, parent=None):
        super().__init__(parent)
        self.test_items = test_items
        self.test_runner = test_runner
        self.is_cancelled = False

    def run(self):
        """Executes the test items and emits signals for progress and results."""
        total = len(self.test_items)
        for i, item in enumerate(self.test_items):
            if self.is_cancelled:
                break

            progress_msg = f"Testando {i+1}/{total}: {item.text(2)} -> {item.text(3)}"
            self.progress.emit(int(((i + 1) / total) * 100), progress_msg)

            _, container_id, _, dst_ip, proto, _, dst_port, expected, _, _, _ = [
                item.text(c) for c in range(item.columnCount())
            ]

            _, result_dict = self.test_runner.run_single_test(container_id, dst_ip, proto, dst_port)
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
        self.config = config
        self.save_file_path = None

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

        input_box = QGroupBox("Novo Teste")
        input_layout = QGridLayout(input_box)
        main_layout.addWidget(input_box)

        self.src_ip_combo = QComboBox()
        self.dst_ip_combo = QComboBox()
        self.dst_ip_combo.setEditable(True)
        self.protocol_combo = QComboBox()
        self.protocol_combo.addItems(["TCP", "UDP", "ICMP"])
        self.src_port_entry = QLineEdit("*")
        self.src_port_entry.setEnabled(False)
        self.dst_port_entry = QLineEdit("80")
        self.expected_yes_radio = QRadioButton("Permitido")
        self.expected_no_radio = QRadioButton("Bloqueado")
        self.expected_yes_radio.setChecked(True)
        expected_layout = QHBoxLayout()
        expected_layout.addWidget(self.expected_yes_radio)
        expected_layout.addWidget(self.expected_no_radio)

        input_layout.addWidget(QLabel("Origem:"), 0, 0)
        input_layout.addWidget(self.src_ip_combo, 1, 0)
        input_layout.addWidget(QLabel("Destino:"), 0, 1)
        input_layout.addWidget(self.dst_ip_combo, 1, 1)
        input_layout.addWidget(QLabel("Protocolo:"), 0, 2)
        input_layout.addWidget(self.protocol_combo, 1, 2)
        input_layout.addWidget(QLabel("Porta Dst:"), 0, 3)
        input_layout.addWidget(self.dst_port_entry, 1, 3)
        input_layout.addWidget(QLabel("Resultado Esperado:"), 0, 4)
        input_layout.addLayout(expected_layout, 1, 4)

        buttons_layout = QHBoxLayout()
        main_layout.addLayout(buttons_layout)
        self.btn_add = QPushButton("Adicionar")
        self.btn_edit = QPushButton("Editar")
        self.btn_del = QPushButton("Deletar")
        self.btn_test = QPushButton("Testar Linha")
        self.btn_test_all = QPushButton("Testar Todos")

        buttons_layout.addStretch(1)
        buttons_layout.addWidget(self.btn_add)
        buttons_layout.addWidget(self.btn_edit)
        buttons_layout.addWidget(self.btn_del)
        buttons_layout.addWidget(self.btn_test)
        buttons_layout.addWidget(self.btn_test_all)
        buttons_layout.addStretch(1)

        self.tree = QTreeWidget()
        self.tree.setSelectionMode(QAbstractItemView.SingleSelection)
        self.header_labels = [
            "#", "ID Container", "Origem", "Destino", "Protocolo", "P. Origem",
            "P. Destino", "Esperado", "Resultado", "Fluxo", "Dados"
        ]
        self.tree.setHeaderLabels(self.header_labels)
        main_layout.addWidget(self.tree)
        self.tree.setColumnWidth(0, 40)
        self.tree.setColumnHidden(1, not self.config.get("show_container_id", False))

        legend_box = QGroupBox("Legenda")
        legend_layout = QHBoxLayout(legend_box)
        main_layout.addWidget(legend_box)
        def add_legend_item(color, text):
            label_color = QLabel()
            label_color.setFixedSize(16, 16)
            label_color.setStyleSheet(f"background-color: {color}; border: 1px solid black;")
            legend_layout.addWidget(label_color)
            legend_layout.addWidget(QLabel(text))
            legend_layout.addSpacing(15)

        add_legend_item("lightgreen", "Passou (Permitido)")
        add_legend_item("lightblue", "Passou (Bloqueado)")
        add_legend_item("salmon", "Falhou")
        add_legend_item("yellow", "Erro")
        legend_layout.addStretch(1)

        file_buttons_layout = QHBoxLayout()
        main_layout.addLayout(file_buttons_layout)
        self.btn_save = QPushButton("Salvar Testes")
        self.btn_save_as = QPushButton("Salvar Como...")
        self.btn_load = QPushButton("Abrir Testes")

        file_buttons_layout.addStretch(1)
        file_buttons_layout.addWidget(self.btn_save)
        file_buttons_layout.addWidget(self.btn_save_as)
        file_buttons_layout.addWidget(self.btn_load)
        file_buttons_layout.addStretch(1)

        self.btn_add.clicked.connect(self._add_test)
        self.btn_edit.clicked.connect(self._edit_test)
        self.btn_del.clicked.connect(self._delete_test)
        self.btn_test.clicked.connect(self._run_selected_test)
        self.btn_test_all.clicked.connect(self._run_all_tests)
        self.tree.itemSelectionChanged.connect(self._on_item_selected)
        self.btn_save.clicked.connect(self._save_tests)
        self.btn_save_as.clicked.connect(self._save_tests_as)
        self.btn_load.clicked.connect(self._open_tests)
        

    def _run_selected_test(self):
        selected_items = self.tree.selectedItems()
        if not selected_items:
            return
        item = selected_items[0]

        _, container_id, _, dst_ip, proto, _, dst_port, expected, _, _, _ = [
            item.text(c) for c in range(item.columnCount())
        ]

        _, result_dict = self.test_runner.run_single_test(
            container_id, dst_ip, proto, dst_port
        )
        analysis, tag = self.test_runner.analyze_test_result(expected, result_dict)

        self._update_tree_item(item, analysis, tag)

    def _update_tree_item(self, item, analysis_dict, tag):
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

    def _run_all_tests(self):
        tests_to_run = [self.tree.topLevelItem(i) for i in range(self.tree.topLevelItemCount())]
        if not tests_to_run:
            return

        self.progress_dialog = QProgressDialog("Executando testes...", "Cancelar", 0, 100, self)
        self.progress_dialog.setWindowTitle("Processando Testes")
        self.progress_dialog.setWindowModality(Qt.WindowModal)

        self.thread = QThread()
        self.worker = TestWorker(tests_to_run, self.test_runner)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.item_tested.connect(self._update_tree_item)
        self.worker.progress.connect(self._update_progress_dialog)
        self.progress_dialog.canceled.connect(self.worker.cancel)
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
        selected_index = self.src_ip_combo.currentIndex()
        container_id = self.hosts_data[selected_index][1] if selected_index >= 0 else "N/A"

        values = [
            str(self.tree.topLevelItemCount() + 1),
            container_id,
            src_text,
            self.dst_ip_combo.currentText(),
            self.protocol_combo.currentText(),
            self.src_port_entry.text(),
            self.dst_port_entry.text(),
            "yes" if self.expected_yes_radio.isChecked() else "no",
            "-", "", ""
        ]

        new_item = QTreeWidgetItem(values)
        self.tree.addTopLevelItem(new_item)
        self._set_buttons_normal_state()

    def _edit_test(self):
        selected_items = self.tree.selectedItems()
        if not selected_items:
            return

        if not self._validate_inputs():
            return

        item = selected_items[0]
        src_text = self.src_ip_combo.currentText()
        selected_index = self.src_ip_combo.currentIndex()
        container_id = self.hosts_data[selected_index][1] if selected_index >= 0 else "N/A"

        item.setText(1, container_id)
        item.setText(2, src_text)
        item.setText(3, self.dst_ip_combo.currentText())
        item.setText(4, self.protocol_combo.currentText())
        item.setText(6, self.dst_port_entry.text())
        item.setText(7, "yes" if self.expected_yes_radio.isChecked() else "no")
        for i in range(8, 11):
            item.setText(i, "" if i > 8 else "-")
            item.setBackground(i, QBrush(QColor("transparent")))

    def _delete_test(self):
        selected_items = self.tree.selectedItems()
        if not selected_items:
            return

        reply = QMessageBox.question(self, "Deletar Teste", 
            "Tem certeza que deseja deletar o teste selecionado?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            item = selected_items[0]
            self.tree.takeTopLevelItem(self.tree.indexOfTopLevelItem(item))
            self._renumber_tests()
            self._set_buttons_normal_state()

    def _renumber_tests(self):
        for i in range(self.tree.topLevelItemCount()):
            self.tree.topLevelItem(i).setText(0, str(i + 1))

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

        self.btn_edit.setEnabled(True)
        self.btn_del.setEnabled(True)
        self.btn_test.setEnabled(True)

    def _validate_inputs(self):
        try:
            port = int(self.dst_port_entry.text())
            if not (1 <= port <= 65535):
                QMessageBox.warning(self, "Entrada Inválida", "A porta de destino deve ser "
                                    "um número entre 1 e 65535.")
                return False
        except ValueError:
            if self.protocol_combo.currentText() != "ICMP":
                QMessageBox.warning(self, "Entrada Inválida", "A porta de destino deve ser um número.")
                return False

        destination = self.dst_ip_combo.currentText()
        known_hosts = [self.src_ip_combo.itemText(i) for i in range(self.src_ip_combo.count())]

        if destination not in known_hosts:
            # pylint: disable=protected-access
            if not self.test_runner._extract_destination_host(destination):
                QMessageBox.warning(self, "Destino Inválido",
                                    "O destino deve ser um host da lista, um IP válido "
                                    "ou um domínio.")
                return False

            if self.protocol_combo.currentText() != "ICMP":
                QMessageBox.warning(self, "Protocolo Inválido para Destino Externo", "Apenas "
                                    "o protocolo ICMP (ping) pode ser usado para destinos "
                                    "externos.")
                return False

        return True

    def _set_buttons_normal_state(self):
        """Resets input fields and button states to their default."""
        self.tree.clearSelection()
        self.btn_add.setEnabled(True)
        self.btn_edit.setEnabled(False)
        self.btn_del.setEnabled(False)
        self.btn_test.setEnabled(False)
        self.btn_test_all.setEnabled(self.tree.topLevelItemCount() > 0)

    def update_hosts_list(self, hosts_data_tuples):
        """Updates the host dropdowns with the latest list of available hosts."""
        self.hosts_data = hosts_data_tuples        

        host_names = [name for name, _ in self.hosts_data]

        self.src_ip_combo.clear()
        self.src_ip_combo.addItems(host_names)
        self.src_ip_combo.setCurrentIndex(-1)
        

        self.dst_ip_combo.clear()
        self.dst_ip_combo.addItems(host_names)
        self.dst_ip_combo.setCurrentIndex(-1)

    def _save_tests_as(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Salvar Arquivo de Testes", 
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
            test_dict = {self.header_labels[j]: item.text(j) for j in range(len(self.header_labels))}
            tests_data.append(test_dict)
            

        try:
            with open(self.save_file_path, "w", encoding="utf-8") as f:
                json.dump(tests_data, f, indent=4, ensure_ascii=False)
            QMessageBox.information(self, "Sucesso", f"Testes salvos em:\n{self.save_file_path}")
        except (IOError, TypeError) as e:
            QMessageBox.critical(self, "Erro", f"Não foi possível salvar o arquivo:\n{e}")

    def _open_tests(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Abrir Arquivo de Testes", 
            "", 
            "JSON Files (*.json);;All Files (*)"
        )
        if file_path:
            self.save_file_path = file_path
            self._load_from_file()

    def _load_from_file(self):
        if not self.save_file_path or not os.path.exists(self.save_file_path):
            QMessageBox.warning(self, "Erro", "Arquivo de testes não encontrado.")
            return

        reply = QMessageBox.question(self, "Carregar Testes", 
            "Isso irá limpar todos os testes atuais na tabela. Deseja continuar?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.No:
            return

        try:
            with open(self.save_file_path, "r", encoding="utf-8") as f:
                tests_data = json.load(f)

            self.tree.clear()
            for test in tests_data:
                # A lógica de remapear hosts ('ask_user_for_source_host')
                # ainda precisa ser implementada aqui com um QDialog.

                # Monta a lista de valores na ordem correta dos cabeçalhos
                values = [test.get(key, "") for key in self.header_labels]
                self.tree.addTopLevelItem(QTreeWidgetItem(values))

            self._renumber_tests()
            self._set_buttons_normal_state()
            QMessageBox.information(self, "Sucesso", "Testes carregados com sucesso.")

        except (IOError, json.JSONDecodeError) as e:
            QMessageBox.critical(self, "Erro", f"Não foi possível carregar o arquivo:\n{e}")