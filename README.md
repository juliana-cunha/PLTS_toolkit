# Paraconsistent Logic Editor

A Python-based graphical toolkit for constructing, visualizing, and analyzing Paraconsistent Transition Systems (PLTS) based on Twist Structures.

## Overview

The **Paraconsistent Logic Editor** is an interactive GUI application designed for researchers and students working with non-classical logics. It allows users to define algebraic foundations (Lattices, Residuated Lattices), construct Paraconsistent Models where transitions and valuations are weighted by truth pairs, and evaluate modal formulas using the algebraic semantics of Twist Structures.

## Features

### 1. Algebraic Structure Creation

- **Lattices & Residuated Lattices** Define custom finite Lattices and Residuated Lattices.
- **Twist Structures** Automatically generate Twist Structures ($A^2$) from a base Residuated Lattice. Truth values are represented as pairs $(t, f)$ (evidence for, evidence against).
- **Hasse Diagrams** Visualize the partial order of any Lattice or Twist Structure using Hasse diagrams.

### 2. Paraconsistent Modeling

- **Batch World Creation** Efficiently create multiple worlds (states) with valuations assigned from the underlying Twist Structure.
- **Weighted Accessibility Relations** Build Kripke-style models where transitions are not just present/absent but carry a **weight** $(t, f)$ from the algebra.
- **Model Visualization** View models as directed graphs with support for bidirectional edges, self-loops, and clear labeling of actions and weights.

### 3. Logic Evaluation & Analysis

- **Formula Parser** Evaluate complex formulas using the specific semantics of Paraconsistent Modal Logic. Supported operators include:

  - **Modal:** Box (`[]`), Diamond (`<>` - weighted by relation)
  - **Lattice:** Weak Meet (`&`), Weak Join (`|`), Residuated Implication (`=>`)
  - **Material:** Material Implication (`->`), Material Equivalence (`<->`)
  - **Unary:** Paraconsistent Negation (`~`)
  - **Constants:** Top (`1`), Bottom (`0`)

- **Model Validity Checking** Automatically verify if a formula is **Valid** (evaluates to Absolute True `(1,0)` in all worlds). The system provides specific counter-examples for invalid formulas.

### 4. User Interface

- **Dark Mode** Toggle between Light and Dark themes for comfortable viewing in different lighting conditions.
- **JSON Persistence** Save and Load your Lattices, Structures, Worlds, and Models to JSON files to preserve your workspace.
- **Definitions & Legend** Built-in reference guides for mathematical definitions and logic symbols.

## Installation

### Requirements

- Python 3.8 or higher

### Install Dependencies

Run the following command to install the required libraries:

```bash
pip install PyQt6 networkx matplotlib
```

## How to Run

Navigate to the project directory and execute the main application script:

```bash
python app.py
```

## Contact

Created by [Rodrigo Alves](rodrigoalves@ua.pt), [Juliana Cunha](juliana.cunha@ua.pt), [Alexandre Madeira](madeira@ua.pt)
Feel free to reach out with questions or suggestions.
