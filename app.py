"""
Main Application Module.

This module defines the MainWindow class, which serves as the primary user interface
for the PLTS Editor.
"""

import sys
from typing import Dict, Set, Any

# GUI Imports
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
    QMenu, QMessageBox, QInputDialog, QLabel, QSplitter, QLineEdit, QComboBox, 
    QTreeWidget, QTreeWidgetItem, QFrame, QPushButton, QListWidget, 
    QAbstractItemView
)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QAction

# Internal Logic Imports
from math_objects.lattice import Lattice, ResiduatedLattice, TwistStructure
from math_objects.world import World
from math_objects.model import Model
from json_object_handler.json_handler import JSONHandler
from parser.formula_parser import FormulaParser 

# Dialog Imports
from app_object_creation.new_lattice_dialog import NewLatticeDialog
from app_object_creation.new_residuated_lattice_dialog import NewResiduatedLatticeDialog
from app_object_creation.new_twist_structure_dialog import NewTwistStructureDialog
from app_object_creation.new_world_dialog import NewWorldDialog
from app_object_creation.new_model_dialog import NewModelDialog
from app_object_loading.obj_loading import MultiSelectDialog


# LIGHT THEME DEFINITION
LIGHT_STYLESHEET = """
QWidget {
    font-family: "Segoe UI", "Arial", sans-serif;
}

QMenuBar::item {
    background: transparent;
    padding: 4px 10px;
}

QLineEdit, QTextEdit, QPlainTextEdit {
    padding: 4px;
    border-radius: 3px;
}

QPushButton {
    border: 1px solid #8f8f91;
    border-radius: 4px;
    background-color: #f0f0f0;
    padding: 5px 4px; 
    min-height: 20px;
}

QPushButton:hover {
    background-color: #e0e0e0;
}
QPushButton:pressed {
    background-color: #d0d0d0;
}

QComboBox {
    padding: 4px;
    padding-right: 20px;
    border: 1px solid #8f8f91;
    border-radius: 3px;
}
"""

# DARK THEME DEFINITION
DARK_STYLESHEET = """
QWidget {
    background-color: #2b2b2b;
    color: #ffffff;
    font-family: "Segoe UI", "Arial", sans-serif;
}

QToolTip {
    color: #ffffff;
    background-color: #2a82da;
    border: 1px solid #ffffff;
}

QMenuBar {
    background-color: #2b2b2b;
    color: #ffffff;
}

QMenuBar::item {
    background: transparent;
    padding: 4px 10px;
}

QMenuBar::item:selected {
    background: #2a82da;
}

QMenu {
    background-color: #2b2b2b;
    color: #ffffff;
    border: 1px solid #555;
}

QMenu::item:selected {
    background-color: #2a82da;
}

QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #191919;
    color: #ffffff;
    border: 1px solid #555;
    border-radius: 3px;
    padding: 4px;
}

QComboBox {
    background-color: #191919;
    color: #ffffff;
    border: 1px solid #555;
    border-radius: 3px;
    padding: 4px;
    padding-right: 20px;
}

QComboBox QAbstractItemView {
    background-color: #191919;
    color: #ffffff;
    border: 1px solid #2a82da;
    selection-background-color: #2a82da;
    selection-color: #ffffff;
    outline: none;
}

QComboBox QAbstractItemView::item {
    min_height: 25px;
    padding: 5px;
}
QComboBox QAbstractItemView::item:hover {
    background-color: #353535;
}

QCheckBox {
    color: #ffffff;
    spacing: 5px;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid #888;
    border-radius: 3px;
    background: #191919;
}

QCheckBox::indicator:checked {
    background-color: #2a82da;
    border: 1px solid #2a82da;
    image: none; 
}

QCheckBox::indicator:hover {
    border: 1px solid #2a82da;
}

QTreeWidget, QListWidget, QTableWidget {
    background-color: #191919;
    color: #ffffff;
    border: 1px solid #555;
    alternate-background-color: #222;
}

QListWidget::item {
    color: #ffffff;
    padding: 2px;
}

QListWidget::item:selected {
    background-color: #2a82da;
    color: #ffffff;
}

QHeaderView::section {
    background-color: #353535;
    color: #ffffff;
    padding: 4px;
    border: 1px solid #555;
}

QTableCornerButton::section {
    background-color: #353535;
    border: 1px solid #555;
}

QPushButton {
    background-color: #353535;
    color: #ffffff;
    border: 1px solid #555;
    border-radius: 4px;
    padding: 5px 4px;
    min-height: 20px;
}

QPushButton:hover {
    background-color: #454545;
    border: 1px solid #888;
}

QPushButton:pressed {
    background-color: #2a82da;
    border: 1px solid #2a82da;
}

QPushButton:disabled {
    color: #888;
    background-color: #2b2b2b;
    border: 1px solid #444;
}

QScrollBar:vertical {
    border: none;
    background: #2b2b2b;
    width: 10px;
    margin: 0px 0px 0px 0px;
}

QScrollBar::handle:vertical {
    background: #555;
    min-height: 20px;
    border-radius: 5px;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""


class MainWindow(QMainWindow):
    """
    The main application window containing the workspace, sidebar, and tools.
    """

    def __init__(self):
        """Initializes the main window and internal storage structures."""
        super().__init__()
        self.setWindowTitle("PLTS Toolkit")
        self.resize(1100, 750)
        
        self.config_file = "json_files/config.json"
        self.is_dark_mode = False

        # Internal Storage
        self.lattices: Dict[str, Lattice] = {}
        self.residuated_lattices: Dict[str, ResiduatedLattice] = {}
        self.twist_structures: Dict[str, TwistStructure] = {}
        self.worlds: Dict[str, World] = {}
        self.models: Dict[str, Model] = {}
        
        # Default propositions
        self.props: Set[str] = {"p", "q", "r", "s"}

        # Tree categories mapping (Label -> TreeItem)
        self.tree_categories: Dict[str, QTreeWidgetItem] = {}

        # Initialize UI
        self.setup_ui()
        self.create_menu()
        
        # Load User Config and Apply Theme
        self.load_user_config()
        self.apply_theme()

    # ==========================================
    #           THEMING & CONFIG
    # ==========================================

    def load_user_config(self) -> None:
        """Loads user preference from JSON."""
        config = JSONHandler.load_config(self.config_file)
        self.is_dark_mode = config.get("dark_mode", False)

    def save_user_config(self) -> None:
        """Saves user preference to JSON."""
        config = {"dark_mode": self.is_dark_mode}
        JSONHandler.save_config(self.config_file, config)

    def toggle_dark_mode(self) -> None:
        self.is_dark_mode = not self.is_dark_mode
        self.apply_theme()
        self.save_user_config()
        
        # Re-render details text if something is selected to match theme
        item = self.tree.currentItem()
        if item: 
            self.on_tree_item_clicked(item)

    def apply_theme(self) -> None:
        """Applies the selected theme (Dark/Light) to the entire application."""
        app = QApplication.instance()
        
        # Force Fusion style to ensure palettes work consistently across OS
        app.setStyle("Fusion")
        
        if self.is_dark_mode:
            app.setStyleSheet(DARK_STYLESHEET)
            self.btn_legend.setStyleSheet("font-weight: bold; color: #5dade2;")
            if hasattr(self, 'action_dark_mode'):
                self.action_dark_mode.setText("Toggle Light Mode")
        else:
            app.setStyleSheet(LIGHT_STYLESHEET)
            self.btn_legend.setStyleSheet("font-weight: bold; color: #2980b9;")
            if hasattr(self, 'action_dark_mode'):
                self.action_dark_mode.setText("Toggle Dark Mode")

    def get_theme_color(self, role: str) -> str:
        """Returns hex color code based on current theme for HTML generation."""
        colors = {
            "header": ("#2c3e50", "#aaddff"), # Dark Blue / Light Blue
            "accent": ("#8e44ad", "#d1c4e9"), # Purple / Light Purple
            "warn":   ("#d35400", "#ffcc80"), # Orange / Light Orange
            "info":   ("#2980b9", "#81d4fa"), # Blue / Cyan
            "error":  ("#c0392b", "#ff8a80"), # Red / Light Red
            "text":   ("#000000", "#ffffff"), # Black / White
            "subtle": ("#7f8c8d", "#b0bec5")  # Gray / Light Gray
        }
        idx = 1 if self.is_dark_mode else 0
        return colors.get(role, ("black", "white"))[idx]

    # ==========================================
    #               UI SETUP
    # ==========================================

    def setup_ui(self) -> None:
        """Constructs the main user interface layout."""
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)

        # -----------------------------
        #      LEFT WIDGET: Sidebar
        # -----------------------------
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(5, 5, 5, 5)
        
        # 1. Project Explorer (Tree)
        label_list = QLabel("Project Explorer:")
        label_list.setStyleSheet("font-weight: bold;")
        left_layout.addWidget(label_list)

        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.open_tree_context_menu)
        left_layout.addWidget(self.tree)
        self.init_tree_categories()

        self.tree.itemClicked.connect(self.on_tree_item_clicked)

        # 2. Visual Separator
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        left_layout.addWidget(line)

        # 3. Propositions Section
        label_props = QLabel("Propositions:")
        label_props.setStyleSheet("font-weight: bold; margin-top: 10px;")
        left_layout.addWidget(label_props)

        self.prop_list_widget = QListWidget()
        self.prop_list_widget.setMaximumHeight(150)
        self.prop_list_widget.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.refresh_props_ui()
        left_layout.addWidget(self.prop_list_widget)

        # Buttons (Add / Remove)
        btn_layout = QHBoxLayout()
        self.btn_add_prop = QPushButton("Add")
        self.btn_add_prop.clicked.connect(self.add_proposition)
        
        self.btn_remove_prop = QPushButton("Remove")
        self.btn_remove_prop.clicked.connect(self.remove_proposition)
        
        btn_layout.addWidget(self.btn_add_prop)
        btn_layout.addWidget(self.btn_remove_prop)
        left_layout.addLayout(btn_layout)

        splitter.addWidget(left_widget)

        # -----------------------------
        #     RIGHT WIDGET: Workspace
        # -----------------------------
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(5, 5, 5, 5)

        # 1. Details Section
        label_details = QLabel("Object Details:")
        label_details.setStyleSheet("font-weight: bold;")
        right_layout.addWidget(label_details)

        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setPlaceholderText("Select an object in the tree to view details.")
        self.details_text.setMaximumHeight(350)
        right_layout.addWidget(self.details_text)

        # Visualization Buttons
        vis_btn_layout = QHBoxLayout()
        self.btn_hasse = QPushButton("Show Hasse Diagram")
        self.btn_hasse.clicked.connect(self.show_current_hasse)
        self.btn_hasse.setEnabled(False) 
        vis_btn_layout.addWidget(self.btn_hasse)
        
        self.btn_visualize_model = QPushButton("Show PLTS")
        self.btn_visualize_model.clicked.connect(self.visualize_current_model)
        self.btn_visualize_model.setEnabled(False)
        vis_btn_layout.addWidget(self.btn_visualize_model)
        
        right_layout.addLayout(vis_btn_layout)

        # Separator
        line_eval = QFrame()
        line_eval.setFrameShape(QFrame.Shape.HLine)
        line_eval.setFrameShadow(QFrame.Shadow.Sunken)
        right_layout.addWidget(line_eval)

        # 2. Formula Interpreter Section
        label_eval = QLabel("Formula Interpreter:")
        label_eval.setStyleSheet("font-weight: bold; margin-top: 10px;")
        right_layout.addWidget(label_eval)

        # A. Context Selection (Model + World)
        selection_layout = QHBoxLayout()
        selection_layout.setContentsMargins(0, 0, 0, 0)
        selection_layout.setSpacing(10)
        
        self.combo_models = QComboBox()
        self.combo_models.setPlaceholderText("Select PLTS")
        self.combo_models.setMinimumWidth(150)
        self.combo_models.currentIndexChanged.connect(self.update_world_combo)
        
        self.combo_worlds = QComboBox()
        self.combo_worlds.setPlaceholderText("Select State")
        self.combo_worlds.setMinimumWidth(150)
        
        selection_layout.addWidget(QLabel("PLTS:"))
        selection_layout.addWidget(self.combo_models)
        selection_layout.addSpacing(20)
        selection_layout.addWidget(QLabel("State:"))
        selection_layout.addWidget(self.combo_worlds)
        selection_layout.addStretch()
        
        right_layout.addLayout(selection_layout)

        # B. Symbol Buttons Toolbar
        symbols_layout = QHBoxLayout()
        symbols_layout.setSpacing(2)
        
        # (Label, InsertText)
        symbol_map = [
            ("□", "[a]"), 
            ("◇", "<a>"), 
            ("¬", "~"), 
            ("▷", "->"),
            ("◁▷", "<->"),  
            ("∧", "&"), 
            ("∨", "|"), 
            ("⊥", "0"),
            ("⊤", "1")
        ]

        for label, insert_text in symbol_map:
            btn = QPushButton(label)
            btn.setFixedWidth(30)
            btn.setToolTip(f"Insert {insert_text}")
            btn.clicked.connect(lambda checked, t=insert_text: self.insert_symbol(t))
            symbols_layout.addWidget(btn)

        # LEGEND BUTTON
        self.btn_legend = QPushButton("?")
        self.btn_legend.setFixedWidth(30)
        self.btn_legend.setToolTip("Show Symbol Legend")
        self.btn_legend.clicked.connect(self.show_symbol_legend)
        symbols_layout.addWidget(self.btn_legend)

        symbols_layout.addStretch()
        right_layout.addLayout(symbols_layout)

        # C. Input Field
        input_layout = QHBoxLayout()
        self.formula_input = QLineEdit()
        self.formula_input.setPlaceholderText("Type formula here (e.g., [a]p & q)...") 
        self.formula_input.returnPressed.connect(self.evaluate_formula) 
        
        self.btn_eval = QPushButton("Interpret")
        self.btn_eval.clicked.connect(self.evaluate_formula)
        
        self.btn_validity = QPushButton("Check Validity")
        self.btn_validity.setToolTip("Check if the formula holds in ALL states of the PLTS")
        self.btn_validity.clicked.connect(self.check_model_validity)
        
        input_layout.addWidget(self.formula_input)
        input_layout.addWidget(self.btn_eval)
        input_layout.addWidget(self.btn_validity)
        right_layout.addLayout(input_layout)

        # D. Result Area
        result_layout = QHBoxLayout()
        
        self.result_label = QLabel("Result: ")
        self.result_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        
        self.validity_label = QLabel("")
        self.validity_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-left: 20px;")
        
        result_layout.addWidget(self.result_label)
        result_layout.addWidget(self.validity_label)
        result_layout.addStretch()
        
        right_layout.addLayout(result_layout)
        
        right_layout.addStretch()

        splitter.addWidget(right_widget)
        splitter.setSizes([300, 700])

    def insert_symbol(self, text: str) -> None:
        """Helper to insert symbol from button click into input field."""
        self.formula_input.insert(text)
        self.formula_input.setFocus()

    def show_symbol_legend(self) -> None:
        """Displays a popup table explaining the math symbols."""
        text_col = "white" if self.is_dark_mode else "black"
        bg_col = "#333" if self.is_dark_mode else "#f0f0f0"
        
        msg = f"""
        <h3 style='color:{self.get_theme_color('info')};'>Symbol Legend</h3>
        <table border="1" cellpadding="4" cellspacing="0" style='border-collapse: collapse; color:{text_col};'>
            <tr style='background-color:{bg_col};'>
                <td><b>Button</b></td><td><b>Input</b></td><td><b>Description</b></td><td><b>Definition</b></td>
            </tr>
            <tr><td>□</td><td>[a]</td><td>Box (Necessity)</td><td>¬&lt;a&gt;¬A</td></tr>
            <tr><td>◇</td><td>&lt;a&gt;</td><td>Diamond (Possibility)</td><td>&lt;a&gt;A</td></tr>
            <tr><td>¬</td><td>~</td><td>Negation</td><td>¬A</td></tr>
            <tr><td>▷</td><td>-&gt;</td><td>Material Imp.</td><td>¬A ⊔ B</td></tr>
            <tr><td>◁▷</td><td>&lt;-&gt;</td><td>Material Iff.</td><td>(A ▷ B) ⊓ (B ▷ A)</td></tr>
            <tr><td>∧</td><td>&</td><td>Weak Meet</td><td>Conjunction (⊓)</td></tr>
            <tr><td>∨</td><td>|</td><td>Weak Join</td><td>Disjunction (⊔)</td></tr>
            <tr><td>⊥</td><td>0 / BOT</td><td>Bottom</td><td>Absolute False (0, 1)</td></tr>
            <tr><td>⊤</td><td>1 / TOP</td><td>Top</td><td>Absolute True (1, 0)</td></tr>
        </table>
        """
        QMessageBox.information(self, "Symbol Legend", msg)

    def show_definitions(self) -> None:
        """Displays mathematical definitions."""
        c_head = self.get_theme_color("header")
        c_text = self.get_theme_color("text")
        
        msg = f"""
        <div style='color:{c_text};'>
        <h3 style='color:{c_head};'>Paraconsistent Definitions</h3>
        <p><b>Twist Structure A²:</b> Given a lattice A, truth values are pairs (t, f) where t represents evidence for, and f evidence against.</p>
        
        <h4 style='color:{c_head};'>Logic Operations</h4>
        <ul>
            <li><b>Negation (¬):</b> //(t, f) = (f, t)</li>
            <li><b>Weak Meet (⊓):</b> (t1, f1) ⊓ (t2, f2) = (t1 ∧ t2, f1 ∨ f2)</li>
            <li><b>Weak Join (⊔):</b> (t1, f1) ⊔ (t2, f2) = (t1 ∨ t2, f1 ∧ f2)</li>
            <li><b>Residue Meet (⊙):</b> Used for Diamond.<br> (t1, f1) ⊙ (t2, f2) = (t1 ∧ t2, (t1→f2) ∧ (t2→f1))</li>
        </ul>

        <h4 style='color:{c_head};'>Modalities</h4>
        <ul>
            <li><b>Diamond (⟨a⟩φ):</b> ⊔<sub>v∈W</sub> ( R<sub>a</sub>(w,v) ⊙ V(v, φ) )</li>
            <li><b>Box ([a]φ):</b> ¬⟨a⟩¬φ</li>
        </ul>
        
        <h4 style='color:{c_head};'>PLTS Validity</h4>
        <p>A formula φ is <b>Valid</b> in PLTS M iff for all statess w, (M, w ⊨ φ) = (1, 0).</p>
        </div>
        """
        QMessageBox.information(self, "Definitions", msg)

    def init_tree_categories(self) -> None:
        """Creates the top-level category items in the Tree Widget."""
        categories = ["Lattices", "Residuated Lattices", "Twist Structures", "States", "PLTSs"]
        for cat in categories:
            item = QTreeWidgetItem(self.tree)
            item.setText(0, cat)
            item.setExpanded(True)
            self.tree_categories[cat] = item

    def create_menu(self) -> None:
        """Initializes the application menu bar actions."""
        menu_bar = self.menuBar()

        # --- NEW MENU ---
        new_menu = menu_bar.addMenu("New")
        new_menu.addAction("Lattice").triggered.connect(self.create_new_lattice)
        new_menu.addAction("Residuated Lattice").triggered.connect(self.create_new_residuated_lattice)
        new_menu.addAction("Twist Structure").triggered.connect(self.create_new_twist_structure)
        new_menu.addAction("State").triggered.connect(self.create_new_world)
        new_menu.addAction("PLTS").triggered.connect(self.create_new_model)

        # --- LOAD MENU ---
        load_menu = menu_bar.addMenu("Load")
        load_menu.addAction("Lattice").triggered.connect(lambda: self.load_specific_object("Lattice", "lattices", "name"))
        load_menu.addAction("Residuated Lattice").triggered.connect(lambda: self.load_specific_object("Residuated Lattice", "residuated_lattices", "name_residuated_lattice"))
        load_menu.addAction("Twist Structure").triggered.connect(lambda: self.load_specific_object("Twist Structure", "twist_structures", "name"))
        load_menu.addAction("State").triggered.connect(lambda: self.load_specific_object("World", "worlds", "world_name"))
        load_menu.addAction("PLTS").triggered.connect(lambda: self.load_specific_object("Model", "models", "model_name"))
        
        # --- DELETE MENU ---
        del_menu = menu_bar.addMenu("Delete")
        del_menu.addAction("Lattice").triggered.connect(lambda: self.delete_specific_object("Lattice", "lattices", "name"))
        del_menu.addAction("Residuated Lattice").triggered.connect(lambda: self.delete_specific_object("Residuated Lattice", "residuated_lattices", "name_residuated_lattice"))
        del_menu.addAction("Twist Structure").triggered.connect(lambda: self.delete_specific_object("Twist Structure", "twist_structures", "name"))
        del_menu.addAction("State").triggered.connect(lambda: self.delete_specific_object("World", "worlds", "world_name"))
        del_menu.addAction("PLTS").triggered.connect(lambda: self.delete_specific_object("Model", "models", "model_name"))
        
        # --- SEE MENU ---
        see_menu = menu_bar.addMenu("See")
        see_menu.addAction("Lattices in File").triggered.connect(lambda: self.see_objects_in_file("lattices", "name"))
        see_menu.addAction("Residuated Lattices in File").triggered.connect(lambda: self.see_objects_in_file("residuated_lattices", "name_residuated_lattice"))
        see_menu.addAction("Twist Structures in File").triggered.connect(lambda: self.see_objects_in_file("twist_structures", "name"))
        see_menu.addAction("States in File").triggered.connect(lambda: self.see_objects_in_file("worlds", "world_name"))
        see_menu.addAction("PLTSs in File").triggered.connect(lambda: self.see_objects_in_file("models", "model_name"))
        
        # --- VIEW MENU (Dark Mode) ---
        view_menu = menu_bar.addMenu("View")
        self.action_dark_mode = QAction("Toggle Dark Mode", self)
        self.action_dark_mode.triggered.connect(self.toggle_dark_mode)
        view_menu.addAction(self.action_dark_mode)
        
        # --- HELP MENU (Definitions) ---
        help_menu = menu_bar.addMenu("Help")
        help_menu.addAction("Mathematical Definitions").triggered.connect(self.show_definitions)
        help_menu.addAction("Symbol Legend").triggered.connect(self.show_symbol_legend)

    # ==========================================
    #             UI HELPER METHODS
    # ==========================================

    def refresh_model_combo(self) -> None:
        self.combo_models.blockSignals(True)
        self.combo_models.clear()
        self.combo_models.addItems(list(self.models.keys()))
        self.combo_models.blockSignals(False)
        self.update_world_combo()

    def update_world_combo(self) -> None:
        self.combo_worlds.clear()
        model_name = self.combo_models.currentText()
        if model_name in self.models:
            model = self.models[model_name]
            world_names = sorted([w.name_long for w in model.worlds])
            self.combo_worlds.addItems(world_names)

    def refresh_props_ui(self) -> None:
        self.prop_list_widget.clear()
        for p in sorted(list(self.props)):
            self.prop_list_widget.addItem(p)

    def add_proposition(self) -> None:
        text, ok = QInputDialog.getText(self, "Add Propositions", "Enter propositions, e.g: p, q, r:")
        if ok and text:
            for item in text.split(','):
                p = item.strip()
                if p: self.props.add(p)
            self.refresh_props_ui()

    def remove_proposition(self) -> None:
        for item in self.prop_list_widget.selectedItems():
            if item.text() in self.props: self.props.remove(item.text())
        self.refresh_props_ui()

    # ==========================================
    #            OBJECT MANAGEMENT
    # ==========================================

    def is_object_loaded(self, category: str, name: str) -> bool:
        if category == "Lattice": return name in self.lattices
        if category == "Residuated Lattice": return name in self.residuated_lattices
        if category == "Twist Structure": return name in self.twist_structures
        if category == "World": return name in self.worlds
        if category == "Model": return name in self.models
        return False

    def register_object(self, name: str, obj: Any, type_str: str) -> None:
        if type_str == "Lattice": self.lattices[name] = obj
        elif type_str == "Residuated Lattice": self.residuated_lattices[name] = obj
        elif type_str == "Twist Structure": self.twist_structures[name] = obj
        elif type_str == "World": self.worlds[name] = obj
        elif type_str == "Model": self.models[name] = obj
        
        cat_map = {"Lattice": "Lattices", "Residuated Lattice": "Residuated Lattices", "Twist Structure": "Twist Structures", "World": "States", "Model": "PLTSs"}
        cat = cat_map.get(type_str)
        if cat and cat in self.tree_categories:
            parent = self.tree_categories[cat]
            if not any(parent.child(i).text(0) == name for i in range(parent.childCount())):
                item = QTreeWidgetItem(parent)
                item.setText(0, name)
        if type_str == "Model": self.refresh_model_combo()

    def remove_from_tree(self, category_label: str, object_name: str) -> None:
        root_item = self.tree_categories.get(category_label)
        if not root_item: return
        for i in range(root_item.childCount()):
            child = root_item.child(i)
            if child.text(0) == object_name:
                root_item.removeChild(child)
                break

    def remove_object_from_memory(self, ui_category: str, tree_category_label: str, object_name: str) -> None:
        memory_map = {
            "Lattice": self.lattices,
            "Residuated Lattice": self.residuated_lattices,
            "Twist Structure": self.twist_structures,
            "World": self.worlds,
            "Model": self.models,
        }
        memory_dict = memory_map.get(ui_category)
        if memory_dict and object_name in memory_dict:
            del memory_dict[object_name]
            self.remove_from_tree(tree_category_label, object_name)
            self.details_text.clear()
            self.statusBar().showMessage(f"Removed '{object_name}' from workspace.", 2000)
            
            if ui_category == "Model": self.refresh_model_combo()

    # ==========================================
    #             FILE OPERATIONS
    # ==========================================

    def see_objects_in_file(self, json_key: str, name_key: str) -> None:
        filename_map = {
            "lattices": "json_files/lattices.json",
            "residuated_lattices": "json_files/residuated_lattices.json",
            "twist_structures": "json_files/twist_structures.json",
            "worlds": "json_files/worlds.json",
            "models": "json_files/models.json"
        }
        fname = filename_map.get(json_key)
        if not fname: return

        names = JSONHandler.get_names_from_json(fname, json_key, name_key)
        display_text = "\n".join(names) if names else "No items found."
        QMessageBox.information(self, f"File Content: {fname}", display_text)

    def _recursive_register(self, obj: Any) -> None:
        """
        Recursively registers dependencies of an object to ensure they appear in the UI.
        Traverses Model -> TwistStructure -> ResiduatedLattice -> Lattice.
        """
        if isinstance(obj, Model):
            self._recursive_register(obj.twist_structure)
            for w in obj.worlds:
                # Ensure world's twist structure is loaded
                self._recursive_register(w.twist_structure)
                
                if not self.is_object_loaded("World", w.name_long):
                    self.register_object(w.name_long, w, "World")
        
        elif isinstance(obj, TwistStructure):
            if not self.is_object_loaded("Twist Structure", obj.name):
                self.register_object(obj.name, obj, "Twist Structure")
            self._recursive_register(obj.residuated_lattice)
            
        elif isinstance(obj, ResiduatedLattice):
            if not self.is_object_loaded("Residuated Lattice", obj.name_residuated_lattice):
                self.register_object(obj.name_residuated_lattice, obj, "Residuated Lattice")
            
            # Load and register the base Lattice if not present
            base_name = obj.name
            if not self.is_object_loaded("Lattice", base_name):
                base_lat = JSONHandler.load_lattice_from_json("json_files/lattices.json", base_name)
                if base_lat:
                    self.register_object(base_name, base_lat, "Lattice")
        
        elif isinstance(obj, World):
             self._recursive_register(obj.twist_structure)

    def load_specific_object(self, ui_category: str, json_key: str, name_key: str) -> None:
        filename_map = {
            "Lattice": "json_files/lattices.json",
            "Residuated Lattice": "json_files/residuated_lattices.json",
            "Twist Structure": "json_files/twist_structures.json",
            "World": "json_files/worlds.json",
            "Model": "json_files/models.json"
        }
        
        fname = filename_map.get(ui_category)
        
        if not fname: 
            print(f"Error: Unknown category {ui_category}")
            return
        
        name_map = {"Model": "PLTS", "World": "State"}
        display_name = name_map.get(ui_category, ui_category)

        names = JSONHandler.get_names_from_json(fname, json_key, name_key)
        if not names:
            QMessageBox.information(self, f"Load {display_name}", f"No objects found in {fname}.")
            return

        dialog = MultiSelectDialog(f"Load {display_name}", names, self)
        if dialog.exec():
            for selected_name in dialog.get_selected_items():
                if self.is_object_loaded(ui_category, selected_name): continue
                
                try:
                    obj = None
                    if ui_category == "Lattice":
                        obj = JSONHandler.load_lattice_from_json(fname, selected_name)
                    elif ui_category == "Residuated Lattice":
                        obj = JSONHandler.load_residuated_lattice_from_json(fname, selected_name)
                    elif ui_category == "Twist Structure":
                        obj = JSONHandler.load_twist_structure_from_json(fname, selected_name)
                    elif ui_category == "World":
                        obj = JSONHandler.load_world_from_json(fname, selected_name)
                    elif ui_category == "Model":
                        obj = JSONHandler.load_model_from_json(fname, selected_name)

                    if obj:
                        self.register_object(selected_name, obj, ui_category)
                        # TRIGGER RECURSIVE LOADING
                        self._recursive_register(obj)
                        
                        self.statusBar().showMessage(f"Loaded {selected_name} and dependencies.", 3000)
                except Exception as e:
                    print(f"Failed to load {selected_name}: {e}")

    def delete_specific_object(self, ui_category: str, json_key: str, name_key: str) -> None:
        filename_map = {
            "Lattice": "json_files/lattices.json",
            "Residuated Lattice": "json_files/residuated_lattices.json",
            "Twist Structure": "json_files/twist_structures.json",
            "World": "json_files/worlds.json",
            "Model": "json_files/models.json"
        }
        fname = filename_map.get(ui_category)
        if not fname: return

        names = JSONHandler.get_names_from_json(fname, json_key, name_key)
        name_map = {"Model": "PLTS", "World": "State"}
        display_name = name_map.get(ui_category, ui_category)
        dialog = MultiSelectDialog(f"Delete {display_name}", names, self)
        if dialog.exec():
            to_delete = dialog.get_selected_items()
            if not to_delete: return
            
            if QMessageBox.question(self, "Confirm", f"Delete {len(to_delete)} items?", 
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
                
                config = {
                    "Lattice": (JSONHandler.delete_lattice_from_json, "Lattices"),
                    "Residuated Lattice": (JSONHandler.delete_residuated_lattice_from_json, "Residuated Lattices"),
                    "Twist Structure": (JSONHandler.delete_twist_structure_from_json, "Twist Structures"),
                    "World": (JSONHandler.delete_world_from_json, "States"),
                    "Model": (JSONHandler.delete_model_from_json, "PLTSs")
                }
                
                handler, tree_cat = config[ui_category]
                for name in to_delete:
                    handler(fname, name)
                    self.remove_object_from_memory(ui_category, tree_cat, name)

    # ==========================================
    #            OBJECT CREATION
    # ==========================================

    def create_new_lattice(self) -> None:
        dialog = NewLatticeDialog(self)
        if dialog.exec():
            name, elements, relations, imp_map = dialog.get_data()
            try:
                lat = Lattice(name, elements, relations, imp_map)
                if JSONHandler.save_lattice_to_json("json_files/lattices.json", lat):
                    self.register_object(name, lat, "Lattice")
                    self.statusBar().showMessage(f"Success: Lattice '{name}' created.", 5000)
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def create_new_residuated_lattice(self) -> None:
        if not self.lattices:
            QMessageBox.warning(self, "Error", "Load a Lattice first.")
            return
        dialog = NewResiduatedLatticeDialog(self.lattices, self)
        if dialog.exec():
            name, base_name = dialog.get_data()
            try:
                base = self.lattices[base_name]
                rl = ResiduatedLattice(name, base.name, base.elements, base.relations, base.implication_map)
                if JSONHandler.save_residuated_lattice_to_json("json_files/residuated_lattices.json", rl):
                    self.register_object(name, rl, "Residuated Lattice")
                    self.statusBar().showMessage(f"Success: RL '{name}' created.", 5000)
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def create_new_twist_structure(self) -> None:
        if not self.residuated_lattices:
            QMessageBox.warning(self, "Error", "Load a Residuated Lattice first.")
            return
        
        dialog = NewTwistStructureDialog(self.residuated_lattices, self)
        if dialog.exec():
            name, rl_name = dialog.get_data()
            try:
                if name in self.twist_structures:
                    raise ValueError(f"Twist Structure '{name}' already exists.")

                rl = self.residuated_lattices[rl_name]
                ts = TwistStructure(rl)
                ts.name = name
                if JSONHandler.save_twist_structure_to_json("json_files/twist_structures.json", ts, name):
                    self.register_object(name, ts, "Twist Structure")
                    self.statusBar().showMessage(f"Success: TS '{name}' created.", 5000)
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def create_new_world(self) -> None:
        if not self.twist_structures:
            QMessageBox.warning(self, "Error", "Load a Twist Structure first.")
            return
            
        dialog = NewWorldDialog(self.twist_structures, self.props, self)
        if dialog.exec():
            worlds_data = dialog.get_data()
            
            created_count = 0
            errors = []
            
            for (long_name, short_name, ts_name, assignments) in worlds_data:
                try:
                    if long_name in self.worlds:
                        errors.append(f"'{long_name}' already exists.")
                        continue
                        
                    ts = self.twist_structures[ts_name]
                    w = World(long_name, short_name, ts, assignments)
                    
                    if JSONHandler.save_world_to_json("json_files/worlds.json", w):
                        self.register_object(long_name, w, "World")
                        created_count += 1
                    else:
                        errors.append(f"Failed to save '{long_name}' to file.")
                        
                except Exception as e:
                    errors.append(f"Error creating '{long_name}': {str(e)}")
            
            if created_count > 0:
                msg = f"Successfully created {created_count} worlds."
                if errors:
                    msg += f"\n\nErrors ({len(errors)}):\n" + "\n".join(errors)
                    QMessageBox.warning(self, "Partial Success", msg)
                else:
                    self.statusBar().showMessage(msg, 5000)
            elif errors:
                QMessageBox.critical(self, "Error", "\n".join(errors))

    def create_new_model(self) -> None:
        if not self.worlds:
            QMessageBox.warning(self, "Error", "Create Worlds first.")
            return
        if not self.twist_structures:
            QMessageBox.warning(self, "Error", "Load Twist Structures first.")
            return
        
        dialog = NewModelDialog(self.twist_structures, self.worlds, self.props, self)
        
        if dialog.exec():
            name, ts_name, w_names, props, rel_data_dict, description = dialog.get_data()
            try:
                ts = self.twist_structures[ts_name]
                selected_worlds_objs = {self.worlds[wn] for wn in w_names}
                
                final_rels = {}
                for action, matrix in rel_data_dict.items():
                    final_rels[action] = {}
                    for src_str, targets_map in matrix.items():
                        if src_str in self.worlds:
                            src_obj = self.worlds[src_str]
                            final_rels[action][src_obj] = {}
                            
                            for tgt_str, weight in targets_map.items():
                                if tgt_str in self.worlds:
                                    tgt_obj = self.worlds[tgt_str]
                                    final_rels[action][src_obj][tgt_obj] = weight

                m = Model(name, ts, selected_worlds_objs, final_rels, props, description=description)
                
                if JSONHandler.save_model_to_json("json_files/models.json", m):
                    self.register_object(name, m, "Model")
                    self._recursive_register(m)
                    self.statusBar().showMessage(f"Success: Model '{name}' created.", 5000)
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    # ==========================================
    #           VISUALIZATION & LOGIC
    # ==========================================

    def on_tree_item_clicked(self, item: QTreeWidgetItem) -> None:
        parent = item.parent()
        if not parent: return
        cat, name = parent.text(0), item.text(0)
        
        self.btn_hasse.setEnabled(False)
        self.btn_visualize_model.setEnabled(False)
        
        html = ""

        def clean_str(obj):
            return str(obj).replace("'", "")
        
        # --- DYNAMIC COLOR HELPER ---
        c_head = self.get_theme_color("header")
        c_acc = self.get_theme_color("accent")
        c_warn = self.get_theme_color("warn")
        c_info = self.get_theme_color("info")
        c_err = self.get_theme_color("error")
        c_text = self.get_theme_color("text")
        c_sub = self.get_theme_color("subtle")

        if cat == "Lattices" and name in self.lattices:
            l = self.lattices[name]
            self.btn_hasse.setEnabled(True)
            
            html += f"<h3 style='color:{c_head};'>LATTICE: {l.name}</h3>"
            html += f"<b>Elements ({len(l.elements)}):</b><br>"
            clean_elems = [clean_str(e) for e in sorted(list(l.elements))]
            html += f"<span style='font-family:monospace; color:{c_acc};'>{{{', '.join(clean_elems)}}}</span><br><br>"
            
            html += "<b>Relations (≤):</b><br>"
            rels_fmt = [f"({clean_str(a)},{clean_str(b)})" for a, b in sorted(list(l.relations))]
            html += f"<span style='font-family:monospace; color:{c_sub};'>{', '.join(rels_fmt)}</span><br><br>"
            
            html += "<b>Implication (→):</b><br>"
            if hasattr(l, 'implication_map') and l.implication_map:
                html += "<table border='0' cellspacing='2' cellpadding='2' style='font-family:monospace;'>"
                for (a, b), res in sorted(l.implication_map.items(), key=lambda x: str(x[0])):
                    html += f"<tr><td>{clean_str(a)} → {clean_str(b)}</td><td>= <b>{clean_str(res)}</b></td></tr>"
                html += "</table>"
            else:
                html += f"<i style='color:{c_sub};'>(Not defined)</i>"
        
        elif cat == "Residuated Lattices" and name in self.residuated_lattices:
            rl = self.residuated_lattices[name]
            self.btn_hasse.setEnabled(True)
            
            html += f"<h3 style='color:{c_acc};'>RESIDUATED LATTICE: {rl.name_residuated_lattice}</h3>"
            html += f"<b>Base Lattice:</b> {rl.name}<br>"
            clean_elems = [clean_str(e) for e in sorted(list(rl.elements))]
            html += f"<b>Elements:</b> <span style='font-family:monospace;'>{{{', '.join(clean_elems)}}}</span><br><br>"
            
            html += "<b>Implication (Inherited):</b><br>"
            if hasattr(rl, 'implication_map') and rl.implication_map:
                html += "<table border='0' cellspacing='2' cellpadding='2' style='font-family:monospace;'>"
                for (a, b), res in sorted(rl.implication_map.items(), key=lambda x: str(x[0])):
                    html += f"<tr><td>{clean_str(a)} → {clean_str(b)}</td><td>= <b>{clean_str(res)}</b></td></tr>"
                html += "</table>"
            else:
                html += f"<i style='color:{c_sub};'>(Not defined)</i>"
        
        elif cat == "Twist Structures" and name in self.twist_structures:
            ts = self.twist_structures[name]
            self.btn_hasse.setEnabled(True)
            
            html += f"<h3 style='color:{c_warn};'>TWIST STRUCTURE: {name}</h3>"
            html += f"<b>Base RL:</b> {ts.residuated_lattice.name_residuated_lattice}<br><br>"
            
            html += f"<b>Elements (L x L) [{len(ts.elements)}]:</b><br>"
            sorted_elems = sorted(list(ts.elements), key=lambda x: (str(x[0]), str(x[1])))
            clean_elems_str = [clean_str(e) for e in sorted_elems]
            html += f"<span style='font-family:monospace; color:{c_acc};'>{', '.join(clean_elems_str)}</span><br><br>"
            
            html += "<b>Truth Ordering (≤<sub>t</sub>):</b><br>"
            sorted_truth = sorted(list(ts.truth_relation), key=lambda x: (str(x[0]), str(x[1])))
            count = 0
            html += "<div style='font-family:monospace; font-size:11px;'>"
            for a, b in sorted_truth:
                if a != b: 
                    html += f"{clean_str(a)} ≤<sub>t</sub> {clean_str(b)}<br>"
                    count += 1
            if count == 0: html += f"<i style='color:{c_sub};'>(Reflexive only)</i>"
            html += "</div><br>"
            
        elif cat == "States" and name in self.worlds:
            w = self.worlds[name]
            html += f"<h3 style='color:{c_info};'>STATE: {w.name_long}</h3>"
            html += f"<b>Short Name:</b> {w.name_short}<br>"
            if hasattr(w, 'twist_structure') and w.twist_structure:
                html += f"<b>Twist Structure:</b> {w.twist_structure.name}<br><br>"
            
            html += "<b>Valuations (V):</b><br>"
            if w.assignments:
                border_c = "#555" if self.is_dark_mode else "#ddd"
                bg_c = "#333" if self.is_dark_mode else "#f2f2f2"
                
                html += f"<table border='1' cellspacing='0' cellpadding='4' style='border-collapse:collapse; border-color:{border_c}; font-family:monospace;'>"
                html += f"<tr style='background-color:{bg_c};'><th>Prop</th><th>Value</th></tr>"
                for p, v in sorted(w.assignments.items()):
                    html += f"<tr><td>{p}</td><td style='color:{c_info};'>{clean_str(v)}</td></tr>"
                html += "</table>"
            else:
                html += f"<i style='color:{c_sub};'>(No assignments)</i>"
            
        elif cat == "PLTSs" and name in self.models:
            m = self.models[name]
            self.btn_visualize_model.setEnabled(True)
            
            html += f"<h3 style='color:{c_err};'>PLTS: {m.name_model}</h3>"

            if hasattr(m, 'description') and m.description:
                html += f"<b>Description:</b><br><i style='color:{c_text};'>{m.description}</i><br><br>"
            
            if hasattr(m, 'twist_structure') and m.twist_structure:
                html += f"<b>Twist Structure:</b> {m.twist_structure.name}<br>"
            
            world_list = [w.name_short for w in m.worlds]
            html += f"<b>States ({len(world_list)}):</b> {', '.join(sorted(world_list))}<br>"
            
            action_list = list(m.actions)
            html += f"<b>Actions:</b> {', '.join(sorted(action_list))}<br><br>"
            
            html += "<b>Accessibility Relations (R):</b><br>"
            if not m.actions:
                html += f"<i style='color:{c_sub};'>(No actions defined)</i>"
            else:
                for action in sorted(list(m.actions)):
                    html += f"<div style='margin-top:5px; font-weight:bold; color:{c_text};'>[{action}] Transitions:</div>"
                    rel_map = m.accessibility_relations.get(action, {})
                    
                    has_edges = False
                    edge_list = []
                    
                    sorted_src = sorted(rel_map.keys(), key=lambda w: w.name_short)
                    for src in sorted_src:
                        targets = rel_map[src]
                        if targets:
                            valid_targets = {tgt: w for tgt, w in targets.items() if w is not None}
                            if valid_targets:
                                has_edges = True
                                tgt_strs = [f"{t.name_short} <span style='color:{c_sub}; font-size:10px;'>{clean_str(w)}</span>" 
                                            for t, w in valid_targets.items()]
                                edge_list.append(f"{src.name_short} &#8594; {{ {', '.join(sorted(tgt_strs))} }}")
                    
                    if has_edges:
                        html += f"<div style='margin-left:15px; font-family:monospace; color:{c_text};'>"
                        html += "<br>".join(edge_list)
                        html += "</div>"
                    else:
                        html += f"<div style='margin-left:15px; color:{c_sub}; font-style:italic;'>No transitions</div>"

        self.details_text.setHtml(html)

    def visualize_current_model(self) -> None:
        item = self.tree.currentItem()
        if item and item.parent() and item.parent().text(0) == "PLTSs":
            model_name = item.text(0)
            if model_name in self.models:
                try:
                    self.models[model_name].draw_graph()
                except Exception as e:
                    QMessageBox.critical(self, "Error", str(e))
        else:
            QMessageBox.warning(self, "Selection Error", "Please select a PLTS in the Project Explorer tree to visualize.")

    def show_current_hasse(self) -> None:
        item = self.tree.currentItem()
        if item and item.parent():
            cat, name = item.parent().text(0), item.text(0)
            obj = None
            if cat == "Lattices": obj = self.lattices.get(name)
            elif cat == "Residuated Lattices": obj = self.residuated_lattices.get(name)
            elif cat == "Twist Structures": obj = self.twist_structures.get(name)
            if obj: obj.draw_hasse()

    def open_tree_context_menu(self, pos: QPoint) -> None:
        item = self.tree.itemAt(pos)
        if item and item.parent():
            name = item.text(0)
            cat = item.parent().text(0)
            menu = QMenu()
            action = menu.addAction(f"Remove {name}")
            if menu.exec(self.tree.viewport().mapToGlobal(pos)) == action:
                cat_map = {"Lattices": "Lattice", "Residuated Lattices": "Residuated Lattice", 
                           "Twist Structures": "Twist Structure", "States": "World", "PLTSs": "Model"}
                if cat in cat_map:
                    self.remove_object_from_memory(cat_map[cat], cat, name)

    def evaluate_formula(self) -> None:
        try:
            f_str = self.formula_input.text().strip()
            if not f_str: 
                self.result_label.setText("Result: Empty")
                self.validity_label.setText("")
                return

            m_name = self.combo_models.currentText()
            w_name = self.combo_worlds.currentText()

            if not m_name or not w_name:
                QMessageBox.warning(self, "Error", "Select PLTS and State.")
                return

            model = self.models[m_name]
            world = next((w for w in model.worlds if w.name_long == w_name), None)
            twist = model.twist_structure

            if not world: return

            parser = FormulaParser(f_str)
            root = parser.parse()

            unknown = [a for a in root.get_atoms() if a not in world.assignments and a != '0' and a.lower() != 'bot']
            if unknown:
                QMessageBox.warning(self, "Error", f"Missing assignments for: {', '.join(unknown)}")
                return

            res = root.evaluate(model, world, twist)
            
            res_str = str(res).replace("'", "")
            self.result_label.setText(f"Result: <b>{res_str}</b>")
            self.validity_label.setText("")
            self.statusBar().showMessage(f"Evaluated in {w_name}: {res_str}", 5000)

        except ValueError as ve:
            self.result_label.setText("Syntax Error")
            self.validity_label.setText("")
            QMessageBox.warning(self, "Syntax Error", str(ve))
        except Exception as e:
            self.result_label.setText("Error")
            self.validity_label.setText("")
            QMessageBox.critical(self, "Error", str(e))

    def check_model_validity(self) -> None:
        try:
            f_str = self.formula_input.text().strip()
            m_name = self.combo_models.currentText()
            
            if not f_str or not m_name:
                self.validity_label.setText("Validity: Error")
                QMessageBox.warning(self, "Error", "Select PLTS and enter formula.")
                return

            model = self.models[m_name]
            twist = model.twist_structure
            parser = FormulaParser(f_str)
            root = parser.parse()

            lat_top = twist.residuated_lattice.top
            lat_bot = twist.residuated_lattice.bottom
            
            results = []
            failed_worlds = []

            sorted_worlds = sorted(model.worlds, key=lambda w: w.name_long)

            for world in sorted_worlds:
                unknown = [a for a in root.get_atoms() if a not in world.assignments and a != '0' and a.lower() != 'bot']
                if unknown:
                    self.validity_label.setText("Validity: Error")
                    QMessageBox.warning(self, "Error", f"State {world.name_short} missing assignments for: {unknown}")
                    return

                res = root.evaluate(model, world, twist)
                results.append(res)
                
                if res != (lat_top, lat_bot):
                    failed_worlds.append(world.name_long)

            validity_val = twist.weak_meet_set(results)
            is_valid = (validity_val == (lat_top, lat_bot)) and (not failed_worlds)
            
            val_str = str(validity_val).replace("'", "")
            
            if is_valid:
                self.validity_label.setText(f"<span style='color:green'>VALID {val_str}</span>")
                self.statusBar().showMessage(f"Valid in {m_name}", 5000)
            else:
                fail_msg = f"{failed_worlds[:3]}..." if len(failed_worlds)>3 else str(failed_worlds)
                self.validity_label.setText(f"<span style='color:red'>INVALID {val_str}</span> Failed: {fail_msg}")
                self.statusBar().showMessage(f"Invalid. Failed in {len(failed_worlds)} states.", 5000)

        except Exception as e:
            self.validity_label.setText("Validity: Error")
            QMessageBox.critical(self, "Error", str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())