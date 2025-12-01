"""
Lattice and Algebraic Structures Module.

This module defines classes for representing Lattices, Residuated Lattices, and Twist Structures. 
It provides methods for algebraic operations (meet, join, implication) and visualization.
"""

from typing import Set, Dict, Tuple, Optional, List
from collections import defaultdict

# Optional dependencies for visualization
try:
    import networkx as nx
    import matplotlib.pyplot as plt
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False

# HELPER: Custom Layout for Hasse Diagrams
def _compute_hasse_layout(G):
    """
    Computes a layout for a Hasse Diagram to minimize crossings.
    Uses the Barycenter Heuristic: nodes are placed horizontally based on 
    the average position of their predecessors (children in the lattice).
    """
    if not G.nodes: return {}

    # 1. Layer Assignment (Longest path from a root)
    layers = {}
    try:
        # Topological sort ensures we process parents after children
        sorted_nodes = list(nx.topological_sort(G))
    except:
        return nx.spring_layout(G)

    for n in sorted_nodes:
        preds = list(G.predecessors(n))
        if preds:
            layers[n] = max(layers[p] for p in preds) + 1
        else:
            layers[n] = 0

    # Group nodes by layer
    layer_nodes = defaultdict(list)
    for n, l in layers.items():
        layer_nodes[l].append(n)
        
    # 2. Minimize Crossings (Barycenter Heuristic)
    max_layer = max(layers.values())
    pos = {}
    
    # Initial placement for layer 0 (Bottom)
    # Sort by string representation to be deterministic
    layer_nodes[0].sort(key=lambda x: str(x))
    width = len(layer_nodes[0])
    for i, node in enumerate(layer_nodes[0]):
        pos[node] = (i - width / 2.0) * 1.5 # Spread out

    # Propagate up
    for l in range(1, max_layer + 1):
        # For each node, calculate average x of predecessors
        node_order = []
        for node in layer_nodes[l]:
            preds = list(G.predecessors(node))
            if preds:
                # Average X of children
                avg_x = sum(pos[p] for p in preds) / len(preds)
            else:
                avg_x = 0 
            node_order.append((node, avg_x))
        
        # Sort nodes in this layer by that average X
        node_order.sort(key=lambda x: x[1])
        
        # Assign integer/spaced x positions based on sort order
        current_nodes = [n for n, x in node_order]
        width = len(current_nodes)
        for i, node in enumerate(current_nodes):
            # x = i centered around 0, multiplied by spacing factor
            pos[node] = (i - width / 2.0) * 1.5

    # 3. Final formatting (x, layer)
    final_pos = {}
    for node, x in pos.items():
        final_pos[node] = (x, layers[node])
        
    return final_pos


class Lattice:
    """
    Represents a lattice with elements, a partial order, meet, join, 
    and an explicit implication mapping.
    """

    def __init__(
        self,
        name: str,
        elements: Set[str],
        relations: Set[Tuple[str, str]],
        implication_map: Optional[Dict[Tuple[str, str], str]] = None
    ):
        self.name = name
        self.elements = set(elements)
        self.relations = set(relations)
        self.implication_map = implication_map if implication_map is not None else {}

        if not self._check_is_lattice():
            raise ValueError(f"The object '{name}' is not a valid lattice.")

        self.bottom = self.meet_set(self.elements)
        self.top = self.join_set(self.elements)

    def is_less_than_or_equal(self, a: str, b: str) -> bool:
        return (a, b) in self.relations

    def join(self, a: str, b: str) -> str:
        if a not in self.elements or b not in self.elements:
            raise ValueError(f"Elements '{a}' or '{b}' not in the lattice.")
        upper_bounds = {
            x for x in self.elements 
            if self.is_less_than_or_equal(a, x) and self.is_less_than_or_equal(b, x)
        }
        if not upper_bounds:
            raise ValueError(f"No common upper bounds found for '{a}' and '{b}'.")
        for x in upper_bounds:
            if all(self.is_less_than_or_equal(x, y) for y in upper_bounds):
                return x
        raise ValueError(f"No unique Join found for '{a}' and '{b}'.")

    def meet(self, a: str, b: str) -> str:
        if a not in self.elements or b not in self.elements:
            raise ValueError(f"Elements '{a}' or '{b}' not in the lattice.")
        lower_bounds = {
            x for x in self.elements 
            if self.is_less_than_or_equal(x, a) and self.is_less_than_or_equal(x, b)
        }
        if not lower_bounds:
            raise ValueError(f"No common lower bounds found for '{a}' and '{b}'.")
        for x in lower_bounds:
            if all(self.is_less_than_or_equal(y, x) for y in lower_bounds):
                return x
        raise ValueError(f"No unique Meet found for '{a}' and '{b}'.")

    def implication(self, a: str, b: str) -> Optional[str]:
        return self.implication_map.get((a, b))

    def meet_set(self, subset: Optional[Set[str]] = None) -> str:
        if subset is None: subset = set()
        subset_list = list(subset)
        if not subset_list: return self.top
        lower = subset_list[0]
        for element in subset_list:
            lower = self.meet(lower, element)
        return lower

    def join_set(self, subset: Optional[Set[str]] = None) -> str:
        if subset is None: subset = set()
        subset_list = list(subset)
        if not subset_list: return self.bottom
        greatest = subset_list[0]
        for element in subset_list:
            greatest = self.join(greatest, element)
        return greatest

    def _check_is_lattice(self) -> bool:
        try:
            for x in self.elements:
                for y in self.elements:
                    self.meet(x, y)
                    self.join(x, y)
            return True
        except ValueError as e:
            print(f"Lattice check failed: {e}")
            return False

    def draw_hasse(self) -> None:
        """
        Draws the Hasse Diagram of the lattice using NetworkX.
        Uses custom Barycenter Layout for clean, untangled layers.
        """
        if not VISUALIZATION_AVAILABLE:
            print("Visualization libraries (networkx, matplotlib) not installed.")
            return

        if not self.elements:
            print("Lattice is empty.")
            return

        G = nx.DiGraph()
        G.add_nodes_from(self.elements)
        
        edges = [(a, b) for a, b in self.relations if a != b]
        G.add_edges_from(edges)

        # Transitive Reduction
        try:
            TR = nx.transitive_reduction(G)
        except Exception as e:
            print(f"Warning: Transitive reduction failed ({e}). Using full graph.")
            TR = G

        # Use Custom Layout
        pos = _compute_hasse_layout(TR)

        plt.figure(figsize=(8, 10))
        plt.title(f"Hasse Diagram: {self.name}")

        # Dynamic Node Size
        labels = {node: str(node).replace("'", "") for node in TR.nodes()}
        max_len = max((len(l) for l in labels.values()), default=1)
        node_size = 1000 + (max_len * 300)

        nx.draw_networkx_nodes(TR, pos, node_size=node_size, node_color="#A0CBE2", edgecolors="black")
        nx.draw_networkx_labels(TR, pos, labels=labels, font_size=10, font_weight="bold")
        nx.draw_networkx_edges(TR, pos, arrows=False, width=1.5, edge_color="gray")
        
        plt.axis("off")
        plt.tight_layout()
        plt.show()

    def __repr__(self) -> str:
        return f"{self.name}"


class ResiduatedLattice(Lattice):
    def __init__(
        self,
        name_residuated_lattice: str,
        name_lattice: str,
        elements: Set[str],
        relations: Set[Tuple[str, str]],
        implication_map: Dict[Tuple[str, str], str]
    ):
        super().__init__(name_lattice, elements, relations, implication_map)
        self.name_residuated_lattice = name_residuated_lattice


class TwistStructure:
    def __init__(self, residuated_lattice: ResiduatedLattice):
        if not isinstance(residuated_lattice, ResiduatedLattice):
            raise TypeError("Argument must be a ResiduatedLattice.")
        
        self.residuated_lattice = residuated_lattice
        self.elements = self._build_elements()
        self.truth_relation = self._build_truth_order()
        self.qntt_info_relation = self._build_quantity_info_order()

    def _build_elements(self) -> Set[Tuple[str, str]]:
        return {
            (e1, e2) 
            for e1 in self.residuated_lattice.elements 
            for e2 in self.residuated_lattice.elements
        }

    def _build_truth_order(self) -> Set[Tuple[Tuple[str, str], Tuple[str, str]]]:
        relation = set()
        rl = self.residuated_lattice
        for p1 in self.elements:
            for p2 in self.elements:
                if rl.is_less_than_or_equal(p1[0], p2[0]) and rl.is_less_than_or_equal(p2[1], p1[1]):
                    relation.add((p1, p2))
        return relation

    def _build_quantity_info_order(self) -> Set[Tuple[Tuple[str, str], Tuple[str, str]]]:
        relation = set()
        rl = self.residuated_lattice
        for p1 in self.elements:
            for p2 in self.elements:
                if rl.is_less_than_or_equal(p1[0], p2[0]) and rl.is_less_than_or_equal(p1[1], p2[1]):
                    relation.add((p1, p2))
        return relation

    def implication(self, pair1: Tuple[str, str], pair2: Tuple[str, str]) -> Tuple[str, str]:
        rl = self.residuated_lattice
        t1, f1 = pair1
        t2, f2 = pair2
        imp_t1_t2 = rl.implication(t1, t2)
        imp_f2_f1 = rl.implication(f2, f1)
        if imp_t1_t2 is None or imp_f2_f1 is None:
            raise ValueError("Implication definition missing in base lattice.")
        meet_imp = rl.meet(imp_t1_t2, imp_f2_f1)
        meet_t1_f2 = rl.meet(t1, f2)
        return (meet_imp, meet_t1_f2)

    def consensus(self, pair1: Tuple[str, str], pair2: Tuple[str, str]) -> Tuple[str, str]:
        rl = self.residuated_lattice
        meet_t = rl.meet(pair1[0], pair2[0])
        meet_f = rl.meet(pair1[1], pair2[1]) 
        return (meet_t, meet_f)

    def residue_meet(self, pair1: Tuple[str, str], pair2: Tuple[str, str]) -> Tuple[str, str]:
        rl = self.residuated_lattice
        t1, f1 = pair1
        t2, f2 = pair2
        meet_t = rl.meet(t1, t2)
        imp1 = rl.implication(t1, f2)
        imp2 = rl.implication(t2, f1)
        if imp1 is None or imp2 is None:
            raise ValueError("Implication definition missing in base lattice for residue_meet.")
        meet_imp = rl.meet(imp1, imp2)
        return (meet_t, meet_imp)

    def negation(self, pair): 
        return (pair[1], pair[0])
        
    def weak_meet(self, pair1, pair2): 
        rl = self.residuated_lattice
        return (rl.meet(pair1[0], pair2[0]), rl.join(pair1[1], pair2[1]))
        
    def weak_join(self, pair1, pair2):
        rl = self.residuated_lattice
        return (rl.join(pair1[0], pair2[0]), rl.meet(pair1[1], pair2[1]))
        
    def accept_all(self, pair1, pair2):
        rl = self.residuated_lattice
        return (rl.join(pair1[0], pair2[0]), rl.join(pair1[1], pair2[1]))

    def weak_meet_set(self, pairs: List[Tuple[str, str]]) -> Tuple[str, str]:
        if not pairs:
            return (self.residuated_lattice.top, self.residuated_lattice.bottom)
        t_list = [p[0] for p in pairs]
        f_list = [p[1] for p in pairs]
        final_t = self.residuated_lattice.meet_set(set(t_list))
        final_f = self.residuated_lattice.join_set(set(f_list))
        return (final_t, final_f)

    def weak_join_set(self, pairs: List[Tuple[str, str]]) -> Tuple[str, str]:
        if not pairs:
            return (self.residuated_lattice.bottom, self.residuated_lattice.top)
        t_list = [p[0] for p in pairs]
        f_list = [p[1] for p in pairs]
        final_t = self.residuated_lattice.join_set(set(t_list))
        final_f = self.residuated_lattice.meet_set(set(f_list))
        return (final_t, final_f)
    
    def draw_hasse(self) -> None:
        """
        Draws the Hasse Diagram of the Twist Structure using NetworkX.
        Uses custom Barycenter Layout.
        """
        if not VISUALIZATION_AVAILABLE:
            print("Visualization libraries (networkx, matplotlib) not installed.")
            return

        if not self.elements:
            print("Lattice is empty.")
            return

        G = nx.DiGraph()
        G.add_nodes_from(self.elements)
        edges = [(a, b) for a, b in self.truth_relation if a != b]
        G.add_edges_from(edges)

        try:
            TR = nx.transitive_reduction(G)
        except Exception as e:
            print(f"Warning: Transitive reduction failed ({e}). Using full graph.")
            TR = G

        pos = _compute_hasse_layout(TR)

        plt.figure(figsize=(8, 10))
        plt.title(f"Hasse Diagram: {self.name}")

        labels = {node: str(node).replace("'", "") for node in TR.nodes()}
        max_len = max((len(l) for l in labels.values()), default=1)
        node_size = 1000 + (max_len * 300)

        nx.draw_networkx_nodes(TR, pos, node_size=node_size, node_color="#A0CBE2", edgecolors="black")
        nx.draw_networkx_labels(TR, pos, labels=labels, font_size=10, font_weight="bold")
        nx.draw_networkx_edges(TR, pos, arrows=False, width=1.5, edge_color="gray")
        
        plt.axis("off")
        plt.tight_layout()
        plt.show()