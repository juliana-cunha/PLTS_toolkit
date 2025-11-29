"""
New Twist Structure Dialog.
"""

from typing import Dict, Any, Tuple
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QDialogButtonBox, 
    QComboBox, QMessageBox
)

class NewTwistStructureDialog(QDialog):
    def __init__(self, rl_dict: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Twist Structure")
        self.resize(400, 200)
        
        layout = QVBoxLayout(self)
        form = QFormLayout()
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Twist Structure Name")
        
        self.combo = QComboBox()
        if rl_dict:
            self.combo.addItems(sorted(list(rl_dict.keys())))
            
        form.addRow("Name:", self.name_input)
        form.addRow("Base Residuated Lattice:", self.combo)
        layout.addLayout(form)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.validate)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def validate(self):
        if not self.name_input.text().strip():
             QMessageBox.warning(self, "Error", "Name required.")
             return
        if self.combo.currentIndex() == -1:
             QMessageBox.warning(self, "Error", "Select a Residuated Lattice.")
             return
        self.accept()

    def get_data(self) -> Tuple[str, str]:
        """Returns (name, rl_name)."""
        return self.name_input.text().strip(), self.combo.currentText()