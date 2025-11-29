"""
New Lattice Dialog Module.

Creates a Lattice with elements, order relations, and an Implication Map.
"""

import itertools
from typing import Tuple, Set, Dict
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QDialogButtonBox, 
    QListWidget, QListWidgetItem, QPushButton, QLabel, QMessageBox,
    QTableWidget, QHeaderView, QComboBox, QTabWidget, QWidget
)
from PyQt6.QtCore import Qt


class NewLatticeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Lattice")
        self.resize(600, 700)
        
        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # TAB 1: Structure
        self.tab_struct = QWidget()
        self.setup_struct_tab()
        self.tabs.addTab(self.tab_struct, "1. Elements & Order")
        
        # TAB 2: Implication
        self.tab_imp = QWidget()
        self.setup_imp_tab()
        self.tabs.addTab(self.tab_imp, "2. Implication")
        
        self.tabs.currentChanged.connect(self.on_tab_changed)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def setup_struct_tab(self):
        layout = QVBoxLayout(self.tab_struct)
        form = QFormLayout()
        self.name_input = QLineEdit()
        self.elements_input = QLineEdit()
        self.elements_input.setPlaceholderText("e.g: 0, 1, a, b")
        self.elements_input.returnPressed.connect(self.populate_lists)
        form.addRow("Name:", self.name_input)
        form.addRow("Elements:", self.elements_input)
        layout.addLayout(form)

        self.gen_btn = QPushButton("Generate Pairs")
        self.gen_btn.clicked.connect(self.populate_lists)
        layout.addWidget(self.gen_btn)
        
        layout.addWidget(QLabel("Relations (a ≤ b):"))
        self.rel_list = QListWidget()
        layout.addWidget(self.rel_list)

    def setup_imp_tab(self):
        layout = QVBoxLayout(self.tab_imp)
        layout.addWidget(QLabel("Define Implication (Row → Col):"))
        self.table_imp = QTableWidget()
        layout.addWidget(self.table_imp)

    def populate_lists(self):
        elements = [e.strip() for e in self.elements_input.text().split(',') if e.strip()]
        if not elements: return
        self.rel_list.clear()
        for p in itertools.product(elements, repeat=2):
            item = QListWidgetItem(f"({p[0]}, {p[1]})")
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Checked if p[0] == p[1] else Qt.CheckState.Unchecked)
            self.rel_list.addItem(item)

    def on_tab_changed(self, index):
        if index == 1: self.populate_imp_table()

    def populate_imp_table(self):
        elements = sorted([e.strip() for e in self.elements_input.text().split(',') if e.strip()])
        n = len(elements)
        self.table_imp.setRowCount(n)
        self.table_imp.setColumnCount(n)
        self.table_imp.setHorizontalHeaderLabels(elements)
        self.table_imp.setVerticalHeaderLabels(elements)
        self.table_imp.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        for r in range(n):
            for c in range(n):
                combo = QComboBox()
                combo.addItems(elements)
                if elements[r] == elements[c]:
                     # Try to find a 1 or top element if exists, or just leave default
                     pass 
                self.table_imp.setCellWidget(r, c, combo)

    def validate_and_accept(self):
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Error", "Name required.")
            return
        self.accept()

    def get_data(self) -> Tuple[str, Set[str], Set[Tuple[str, str]], Dict[Tuple[str, str], str]]:
        name = self.name_input.text().strip()
        elements = {e.strip() for e in self.elements_input.text().split(',') if e.strip()}
        
        relations = set()
        for i in range(self.rel_list.count()):
            item = self.rel_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                clean = item.text().replace('(', '').replace(')', '').replace("'", "")
                p = [x.strip() for x in clean.split(',')]
                relations.add((p[0], p[1]))

        imp_map = {}
        rows = self.table_imp.rowCount()
        for r in range(rows):
            a = self.table_imp.verticalHeaderItem(r).text()
            for c in range(rows):
                b = self.table_imp.horizontalHeaderItem(c).text()
                res = self.table_imp.cellWidget(r, c).currentText()
                imp_map[(a, b)] = res
                
        return name, elements, relations, imp_map