"""
New Residuated Lattice Dialog.

Creates a RL by selecting a base Lattice (which already contains the Implication Map).
"""

from typing import Dict, Any, Tuple
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QDialogButtonBox, 
    QComboBox, QMessageBox
)

class NewResiduatedLatticeDialog(QDialog):
    def __init__(self, lattices: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Residuated Lattice")
        self.resize(400, 200)
        
        layout = QVBoxLayout(self)
        form = QFormLayout()
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("RL Name")
        
        self.combo = QComboBox()
        if lattices:
            self.combo.addItems(sorted(list(lattices.keys())))
            
        form.addRow("Name:", self.name_input)
        form.addRow("Base Lattice:", self.combo)
        layout.addLayout(form)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.validate)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def validate(self):
        if not self.name_input.text().strip() or self.combo.currentIndex() == -1:
            QMessageBox.warning(self, "Error", "Invalid Input")
            return
        self.accept()

    def get_data(self) -> Tuple[str, str]:
        return self.name_input.text().strip(), self.combo.currentText()