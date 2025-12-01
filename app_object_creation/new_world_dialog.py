"""
New World Dialog Module.
"""

from typing import Dict, Set, Tuple, Optional, Any, List
from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QDialogButtonBox, QComboBox, 
    QGroupBox, QVBoxLayout, QWidget, QMessageBox, QLabel, QScrollArea, QListWidget, QPushButton, QSplitter
)
from PyQt6.QtCore import Qt

class NewWorldDialog(QDialog):
    def __init__(
        self, 
        twist_structures: Dict[str, Any], 
        props: Set[str], 
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent)
        self.setWindowTitle("Create New States")
        self.resize(900, 600)
        
        self.twist_structures = twist_structures
        self.props = sorted(list(props))
        self.assignment_widgets: Dict[str, QComboBox] = {}
        
        # List of tuples: (long_name, short_name, ts_name, assignments_dict)
        self.queue_data: List[Tuple[str, str, str, Dict[str, str]]] = []
        
        # Main Layout (Splitter)
        main_layout = QVBoxLayout(self)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # ===========================
        #    LEFT: Input Form
        # ===========================
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # 1. Basic Info
        info_group = QGroupBox("State Definition")
        form_layout = QFormLayout()
        
        self.long_name_input = QLineEdit()
        self.long_name_input.setPlaceholderText("Unique ID (e.g. State_1)")
        
        self.short_name_input = QLineEdit()
        self.short_name_input.setPlaceholderText("Graph Label (e.g. s1)")
        
        self.combo_ts = QComboBox()
        self.combo_ts.setPlaceholderText("Select Twist Structure")
        if self.twist_structures:
            self.combo_ts.addItems(sorted(list(self.twist_structures.keys())))
        
        self.combo_ts.currentTextChanged.connect(self.update_assignment_options)
        
        form_layout.addRow("Long Name:", self.long_name_input)
        form_layout.addRow("Short Name:", self.short_name_input)
        form_layout.addRow("Twist Structure:", self.combo_ts)
        info_group.setLayout(form_layout)
        left_layout.addWidget(info_group)
        
        # 2. Assignments
        self.assignments_group = QGroupBox("Proposition Valuations")
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        self.assignments_layout = QFormLayout(scroll_content)
        
        if not self.props:
            self.assignments_layout.addRow(QWidget(), QLabel("No propositions defined."))
        else:
            for p in self.props:
                combo = QComboBox()
                self.assignment_widgets[p] = combo
                self.assignments_layout.addRow(f"Value for '{p}':", combo)
            
        scroll.setWidget(scroll_content)
        group_layout = QVBoxLayout(self.assignments_group)
        group_layout.addWidget(scroll)
        left_layout.addWidget(self.assignments_group)

        # 3. Add Button
        self.btn_add = QPushButton("Add to Queue >>")
        self.btn_add.setStyleSheet("font-weight: bold; padding: 8px;")
        self.btn_add.clicked.connect(self.add_to_queue)
        left_layout.addWidget(self.btn_add)
        
        # Initialize dropdowns
        if self.combo_ts.count() > 0:
            self.update_assignment_options(self.combo_ts.currentText())

        splitter.addWidget(left_widget)

        # ===========================
        #    RIGHT: Queue List
        # ===========================
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        right_layout.addWidget(QLabel("<b>States to Create:</b>"))
        self.list_queue = QListWidget()
        right_layout.addWidget(self.list_queue)
        
        btn_remove = QPushButton("Remove Selected")
        btn_remove.clicked.connect(self.remove_from_queue)
        right_layout.addWidget(btn_remove)
        
        splitter.addWidget(right_widget)
        splitter.setSizes([500, 400])

        # Bottom Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.validate_final)
        buttons.rejected.connect(self.reject)
        main_layout.addWidget(buttons)

    def update_assignment_options(self, ts_name: str) -> None:
        """Populates value dropdowns with elements from selected Twist Structure."""
        if ts_name not in self.twist_structures: return

        ts = self.twist_structures[ts_name]
        sorted_elems = sorted(list(ts.elements), key=lambda x: str(x))
        
        for combo in self.assignment_widgets.values():
            prev_text = combo.currentText()
            
            combo.blockSignals(True)
            combo.clear()
            
            for e in sorted_elems:
                real_str = str(e)
                display_str = real_str.replace("'", "") # Clean for user
                combo.addItem(display_str, real_str)   # Add (Text, Data)
            
            # Restore previous selection if possible (matching display text)
            idx = combo.findText(prev_text)
            if idx >= 0:
                combo.setCurrentIndex(idx)
                
            combo.blockSignals(False)

    def add_to_queue(self) -> None:
        """Validates current input and adds it to the right-hand list."""
        l_name = self.long_name_input.text().strip()
        s_name = self.short_name_input.text().strip()
        ts_name = self.combo_ts.currentText()
        
        if not l_name or not s_name:
            QMessageBox.warning(self, "Error", "Names are required.")
            return
        if not ts_name:
            QMessageBox.warning(self, "Error", "Twist Structure required.")
            return
        
        # Check duplicates in queue
        for item in self.queue_data:
            if item[0] == l_name:
                QMessageBox.warning(self, "Error", f"Long Name '{l_name}' already in queue.")
                return
            if item[1] == s_name:
                QMessageBox.warning(self, "Error", f"Short Name '{s_name}' already in queue.")
                return

        # Gather assignments using the stored DATA
        assignments = {}
        for p, combo in self.assignment_widgets.items():
            
            val = combo.currentData()
            if val is None:
                val = combo.currentText()
            assignments[p] = val
            
        # Store Data
        self.queue_data.append((l_name, s_name, ts_name, assignments))
        
        # Update UI
        display_str = f"{s_name} ({l_name}) - [{ts_name}]"
        self.list_queue.addItem(display_str)
        self.long_name_input.clear()
        self.short_name_input.clear()
        self.long_name_input.setFocus()

    def remove_from_queue(self) -> None:
        row = self.list_queue.currentRow()
        if row >= 0:
            self.list_queue.takeItem(row)
            self.queue_data.pop(row)

    def validate_final(self) -> None:
        """Called when pressing OK."""
        if not self.queue_data:
            if self.long_name_input.text().strip() and self.short_name_input.text().strip():
                reply = QMessageBox.question(
                    self, "Add current?", 
                    "The queue is empty, but you have data in the form.\nAdd this state and finish?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    self.add_to_queue()
                    if self.queue_data:
                        self.accept()
                    return
            
            QMessageBox.warning(self, "Error", "No states in the queue to create.")
            return
            
        self.accept()

    def get_data(self) -> List[Tuple[str, str, str, Dict[str, str]]]:
        """
        Returns a LIST of world data tuples.
        """
        return self.queue_data