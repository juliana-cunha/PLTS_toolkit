"""
World Module.

This module defines the World class, representing a single state in the model.
Each world is strictly associated with a specific Twist Structure.
"""

from typing import Dict, Optional, Any

class World:
    """
    Represents a single world in a Paraconsistent Modal Model.

    Attributes:
        name_long (str): Unique identifier.
        name_short (str): Display label.
        twist_structure (TwistStructure): The algebraic structure defining truth values.
        assignments (Dict[str, str]): Mapping of propositions to truth values (as strings).
    """

    def __init__(
        self, 
        name_long: str, 
        name_short: str, 
        twist_structure: Any, 
        assignments: Optional[Dict[str, str]] = None
    ):
        """
        Initializes the World.

        Args:
            name_long (str): Unique identifier.
            name_short (str): Display label.
            twist_structure (TwistStructure): The associated algebra.
            assignments (Optional[Dict]): Initial valuation map.
        """
        self.name_long = name_long
        self.name_short = name_short
        self.twist_structure = twist_structure
        self.assignments = assignments if assignments is not None else {}

    def get_assignment(self, variable: str) -> Optional[str]:
        return self.assignments.get(variable)

    def assign_value(self, variable: str, value: str) -> None:
        """
        Assigns a value to a proposition.
        """
        self.assignments[variable] = value

    def __repr__(self) -> str:
        return f"{self.name_short}"