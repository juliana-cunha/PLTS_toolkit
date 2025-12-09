"""
New Model Dialog Module.
"""

from collections import defaultdict
from typing import List, Set, Dict, Tuple, Optional, Any
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QDialogButtonBox, 
    QComboBox, QListWidget, QAbstractItemView, QTabWidget, QWidget, 
    QTableWidget, QLabel, QMessageBox, QHBoxLayout, QTextEdit
)
from ast import literal_eval

class NewModelDialog(QDialog):
    def __init__(
        self,
        twist_structures_dict: Dict[str, Any],
        worlds_dict: Dict[str, Any],
        props: Set[str],
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent)
        self.setWindowTitle("Create New PLTS")
        self.resize(850, 700)
        
        self.twist_structures = twist_structures_dict
        self.worlds_dict = worlds_dict
        self.ts_names = sorted(list(twist_structures_dict.keys()))
        self.props = props
        
        # Relations: { action: { source: {target: (t, f)} } }
        self.relations_data: Dict[str, Dict[str, Dict[str, Tuple[str, str]]]] = defaultdict(lambda: defaultdict(dict))
        
        self.current_action_context: Optional[str] = None
        
        # List of (Display String, User Data String)
        self.ts_elements_data: List[Tuple[str, Optional[str]]] = []
        
        self.no_connection_str = "(No Connection)"
        
        # UI Setup
        self.main_layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        self.tabs.currentChanged.connect(self.on_tab_changed)
        self.main_layout.addWidget(self.tabs)

        # Tab 1
        self.tab_general = QWidget()
        self.setup_general_tab()
        self.tabs.addTab(self.tab_general, "1. General & States")

        # Tab 2
        self.tab_relations = QWidget()
        self.setup_relations_tab()
        self.tabs.addTab(self.tab_relations, "2. Action Relations (Weights)")

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        self.main_layout.addWidget(buttons)

    def setup_general_tab(self) -> None:
        layout = QVBoxLayout(self.tab_general)
        form = QFormLayout()
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("PLTS Name")

        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("Optional description of the model...")
        self.desc_input.setMaximumHeight(1000)
        
        self.combo_ts = QComboBox()
        self.combo_ts.addItems(self.ts_names)
        self.combo_ts.currentIndexChanged.connect(self.on_ts_changed)
        
        self.actions_input = QLineEdit()
        self.actions_input.setPlaceholderText("e.g: knows, believes, a")
        self.actions_input.editingFinished.connect(self.parse_actions)

        form.addRow("Name:", self.name_input)
        form.addRow("Description:", self.desc_input)
        form.addRow("Twist Structure:", self.combo_ts)
        form.addRow("Actions:", self.actions_input)
        layout.addLayout(form)

        layout.addWidget(QLabel("Select States (Filtered by Twist Structure):"))
        self.list_worlds = QListWidget()
        
        self.list_worlds.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        layout.addWidget(self.list_worlds)
        
        if self.ts_names: self.on_ts_changed(0)

    def setup_relations_tab(self) -> None:
        layout = QVBoxLayout(self.tab_relations)
        
        action_layout = QHBoxLayout()
        action_layout.addWidget(QLabel("Edit Relations for Action:"))
        self.combo_current_action = QComboBox()
        self.combo_current_action.currentTextChanged.connect(self.switch_action_context)
        action_layout.addWidget(self.combo_current_action)
        layout.addLayout(action_layout)
        
        layout.addWidget(QLabel("Assign weights (Row → Col). Leave as '(No Connection)' for no edge."))
        self.table_relations = QTableWidget()
        layout.addWidget(self.table_relations)

    # Logic
    def on_ts_changed(self, index: int):
        name = self.combo_ts.currentText()
        
        # 1. Update available weights for relations
        if name in self.twist_structures:
            ts = self.twist_structures[name]
            sorted_elems = sorted(list(ts.elements), key=lambda x: str(x))
            self.ts_elements_data = []
            self.ts_elements_data.append((self.no_connection_str, None))
            for e in sorted_elems:
                real_str = str(e)
                display_str = real_str.replace("'", "")
                self.ts_elements_data.append((display_str, real_str))

        # 2. Filter Worlds List
        self.filter_worlds_by_ts(name)

    def filter_worlds_by_ts(self, ts_name: str) -> None:
        """Only show worlds that are associated with the selected Twist Structure."""
        self.list_worlds.clear()
        
        compatible_worlds = []
        for w_name, world_obj in self.worlds_dict.items():
            if world_obj.twist_structure.name == ts_name:
                compatible_worlds.append(w_name)
        
        self.list_worlds.addItems(sorted(compatible_worlds))
        
        if not compatible_worlds and self.worlds_dict:
            self.list_worlds.setToolTip("No states found for this Twist Structure.")
        else:
            self.list_worlds.setToolTip("")

    def parse_actions(self) -> List[str]:
        return [x.strip() for x in self.actions_input.text().split(',') if x.strip()]

    def on_tab_changed(self, index: int) -> None:
        if index == 1: self.prepare_relations_tab()

    def prepare_relations_tab(self) -> None:
        actions = self.parse_actions()
        if not actions:
            QMessageBox.warning(self, "Error", "Define at least one action first.")
            self.tabs.setCurrentIndex(0)
            return
        
        curr = self.combo_current_action.currentText()
        self.combo_current_action.blockSignals(True)
        self.combo_current_action.clear()
        self.combo_current_action.addItems(actions)
        if curr in actions: self.combo_current_action.setCurrentText(curr)
        self.combo_current_action.blockSignals(False)

        selected_worlds = [item.text() for item in self.list_worlds.selectedItems()]
        n = len(selected_worlds)
        self.table_relations.setRowCount(n)
        self.table_relations.setColumnCount(n)
        self.table_relations.setHorizontalHeaderLabels(selected_worlds)
        self.table_relations.setVerticalHeaderLabels(selected_worlds)
        
        if self.combo_current_action.count() > 0:
            self.switch_action_context(self.combo_current_action.currentText())

    def switch_action_context(self, new_action: str) -> None:
        if not new_action: return
        if self.current_action_context:
            self.save_current_table_to_data(self.current_action_context)
        self.current_action_context = new_action
        self.load_data_to_table(new_action)

    def save_current_table_to_data(self, action: str) -> None:
        rows = self.table_relations.rowCount()
        cols = self.table_relations.columnCount()
        
        if action not in self.relations_data:
            self.relations_data[action] = defaultdict(dict)
            
        for r in range(rows):
            src = self.table_relations.verticalHeaderItem(r).text()
            for c in range(cols):
                tgt = self.table_relations.horizontalHeaderItem(c).text()
                combo = self.table_relations.cellWidget(r, c)
                
                if isinstance(combo, QComboBox):
                    val_data = combo.currentData()
                    if val_data is None:
                        if tgt in self.relations_data[action][src]:
                            del self.relations_data[action][src][tgt]
                    else:
                        try:
                            val_tuple = literal_eval(val_data)
                            self.relations_data[action][src][tgt] = val_tuple
                        except: pass

    def load_data_to_table(self, action: str) -> None:
        rows = self.table_relations.rowCount()
        cols = self.table_relations.columnCount()
        data = self.relations_data.get(action, {})
        
        for r in range(rows):
            src = self.table_relations.verticalHeaderItem(r).text()
            row_data = data.get(src, {})
            
            for c in range(cols):
                tgt = self.table_relations.horizontalHeaderItem(c).text()
                
                combo = QComboBox()
                for display_text, user_data in self.ts_elements_data:
                    combo.addItem(display_text, user_data)
                
                saved_val = row_data.get(tgt, None)
                
                if saved_val is None:
                    idx = combo.findData(None)
                    combo.setCurrentIndex(idx if idx >= 0 else 0)
                    combo.setStyleSheet("color: gray;")
                else:
                    saved_str = str(saved_val)
                    idx = combo.findData(saved_str)
                    if idx >= 0:
                        combo.setCurrentIndex(idx)
                    else:
                        combo.setCurrentIndex(0)
                    combo.setStyleSheet("background-color: #d1f7c4; font-weight: bold;")
                
                self.table_relations.setCellWidget(r, c, combo)

    def validate_and_accept(self) -> None:
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Error", "PLTS Name required.")
            return
        if not self.combo_ts.currentText():
            QMessageBox.warning(self, "Error", "Twist Structure required.")
            return
        if not self.list_worlds.selectedItems():
            QMessageBox.warning(self, "Error", "Select at least one State.")
            return
        if not self.parse_actions():
            QMessageBox.warning(self, "Error", "Define actions.")
            return
        
        if self.current_action_context:
            self.save_current_table_to_data(self.current_action_context)
        self.accept()

    def get_data(self) -> Tuple[str, str, List[str], str, Set[str], Dict, str]:
        name = self.name_input.text().strip()
        description = self.desc_input.toPlainText().strip()
        ts_name = self.combo_ts.currentText()
        selected_items = self.list_worlds.selectedItems()
        world_names = [item.text() for item in selected_items]
        
        if self.current_action_context:
            self.save_current_table_to_data(self.current_action_context)

        return name, ts_name, world_names, self.props, self.relations_data, description