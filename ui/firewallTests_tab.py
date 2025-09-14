import json
import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QComboBox, QGroupBox, QGridLayout, QLineEdit, 
    QRadioButton, QTreeWidget, QTreeWidgetItem, 
    QAbstractItemView, QHeaderView, QMessageBox, 
    QFileDialog, QProgressDialog, QApplication)
from PyQt5.QtGui import QFont, QColor, QBrush
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QObject

class TestWorker(QObject):
    progress = pyqtSignal(int, str)
    item_tested = pyqtSignal(QTreeWidgetItem, dict, str)
    finished = pyqtSignal()

    def __init__(self, test_items, test_runner, parent=None):
        super().__init__(parent)
        self.test_items = test_items
        self.test_runner = test_runner
        self.is_cancelled = False

    def run(self):
        total = len(self.test_items)
        for i, item in enumerate(self.test_items):
            if self.is_cancelled:
                break
            
            self.progress.emit(int(((i + 1) / total) * 100), f"Testando {i+1}/{total}: {item.text(2)} -> {item.text(3)}")
            
            _, container_id, _, dst_ip, proto, _, dst_port, expected, _, _, _ = [item.text(c) for c in range(item.columnCount())]
            
            success, result_dict = self.test_runner.run_single_test(container_id, dst_ip, proto, dst_port)
            analysis, tag = self.test_runner.analyze_test_result(expected, result_dict)
            
            self.item_tested.emit(item, analysis, tag)
            
        self.finished.emit()

    def cancel(self):
        self.is_cancelled = True

class FirewallTestsTab(QWidget):
    def __init__(self, test_runner, hosts_data, parent=None):
        super().__init__(parent)
        self.test_runner = test_runner
        self.hosts_data = hosts_data
        self.save_file_path = None
        
        self._setup_ui()
        self._update_comboboxes()
        self._set_buttons_normal_state()

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
        header_labels = ["#", "ID Container", "Origem", "Destino", "Protocolo", "P. Origem", "P. Destino", "Esperado", "Resultado", "Fluxo", "Dados"]
        self.tree.setHeaderLabels(header_labels)
        main_layout.addWidget(self.tree)
        self.tree.setColumnWidth(0, 40)
        self.tree.setColumnWidth(1, 130)
        
        legend_box = QGroupBox("Legenda")
        legend_layout = QHBoxLayout(legend_box)
        main_layout.addWidget(legend_box)
        
        def add_legend_item(color, text):
            # ... (código da legenda) ...
            pass
        add_legend_item("lightgreen", "Teste passou (Permitido como esperado)")
        add_legend_item("lightblue", "Teste passou (Bloqueado como esperado)")
        add_legend_item("salmon", "Teste Falhou")
        add_legend_item("yellow", "Erro no Teste")
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

    def _update_comboboxes(self):
        """Atualiza os comboboxes com os hosts disponíveis."""
        # ... (código para preencher os QComboBoxes com base em self.hosts_data) ...
        pass

    def _set_buttons_normal_state(self):
        # ... (lógica para habilitar/desabilitar botões) ...
        pass

    # --- Slots de Ação ---
    def _add_test(self):
        # ... (lógica para validar entradas e adicionar um item na árvore) ...
        pass

    def _edit_test(self):
        # ... (lógica para editar o item selecionado na árvore) ...
        pass

    def _delete_test(self):
        # ... (lógica para remover o item selecionado da árvore) ...
        pass

    def _on_item_selected(self):
        # ... (lógica para preencher o formulário quando um item é selecionado) ...
        pass
    
    def _run_selected_test(self):
        selected_items = self.tree.selectedItems()
        if not selected_items: return
        item = selected_items[0]

        _, container_id, _, dst_ip, proto, _, dst_port, expected, _, _, _ = [item.text(c) for c in range(item.columnCount())]
        
        success, result_dict = self.test_runner.run_single_test(container_id, dst_ip, proto, dst_port)
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
        if not tests_to_run: return

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
        self.worker.progress.connect(lambda p, msg: (self.progress_dialog.setValue(p), self.progress_dialog.setLabelText(msg)))
        self.progress_dialog.canceled.connect(self.worker.cancel)
        self.thread.finished.connect(lambda: self.progress_dialog.close())

        self.thread.start()
        self.progress_dialog.exec_()
        
    def _save_tests(self):
        # ... (lógica para salvar os dados da árvore em um JSON) ...
        pass
        
    def _save_tests_as(self):
        # ... (lógica para abrir o QFileDialog e chamar _save_tests) ...
        pass

    def _open_tests(self):
        # ... (lógica para abrir o QFileDialog e chamar _load_from_file) ...
        pass

    def _load_from_file(self):
        # ... (lógica para carregar um JSON e popular a árvore) ...
        pass

    def update_hosts_list(self, hosts_data_tuples):

        self.hosts_data = hosts_data_tuples
        
        host_names = [name for name, _ in self.hosts_data]
        
        self.src_ip_combo.clear()
        self.src_ip_combo.addItems(host_names)
        self.src_ip_combo.setCurrentIndex(-1)
        
        self.dst_ip_combo.clear()
        self.dst_ip_combo.addItems(host_names)
        self.dst_ip_combo.setCurrentIndex(-1)
