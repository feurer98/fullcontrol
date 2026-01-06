"""
Node Type Definitions for the Node-Based G-Code Generator

This module defines the type system for nodes in the visual programming
interface, including node categories, port types, and parameter types.
"""

from enum import Enum
from typing import Any, List, Optional, Union
from dataclasses import dataclass, field


class NodeCategory(str, Enum):
    """Categories for organizing nodes in the UI."""

    CONTROL = "control"  # Start, End, Sequence, Loop
    MOVEMENT = "movement"  # LinearMove, ExtrudeMove, Home
    TEMPERATURE = "temperature"  # SetHotend, SetBed, WaitHotend, WaitBed
    HARDWARE = "hardware"  # SetFan, SetTool
    UTILITY = "utility"  # Comment, Custom G-Code


class PortType(str, Enum):
    """Data types that can flow through connections."""

    EXEC = "exec"  # Execution flow (no data, just sequence)
    POSITION = "position"  # 3D position (x, y, z)
    NUMBER = "number"  # Numeric value (float/int)
    BOOLEAN = "boolean"  # True/False
    STRING = "string"  # Text
    TEMPERATURE = "temperature"  # Temperature value
    ANY = "any"  # Any type (for flexible inputs)


class ParameterType(str, Enum):
    """Types of parameters that nodes can have."""

    NUMBER = "number"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    STRING = "string"
    SELECT = "select"  # Dropdown selection
    POSITION = "position"  # X, Y, Z coordinates


@dataclass
class PortDefinition:
    """Definition of an input or output port on a node."""

    id: str
    label: str
    port_type: PortType
    required: bool = True
    default_value: Any = None

    def is_compatible(self, other: "PortDefinition") -> bool:
        """Check if this port can connect to another port."""
        if self.port_type == PortType.ANY or other.port_type == PortType.ANY:
            return True
        return self.port_type == other.port_type


@dataclass
class ParameterDefinition:
    """Definition of a configurable parameter on a node."""

    id: str
    label: str
    param_type: ParameterType
    default_value: Any
    required: bool = True
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    options: Optional[List[str]] = None  # For SELECT type
    help_text: Optional[str] = None

    def validate(self, value: Any) -> tuple[bool, Optional[str]]:
        """
        Validate a parameter value.

        Returns:
            Tuple of (is_valid, error_message)
        """
        if value is None:
            if self.required:
                return False, f"{self.label} is required"
            return True, None

        # Type validation
        if self.param_type == ParameterType.NUMBER:
            if not isinstance(value, (int, float)):
                return False, f"{self.label} must be a number"
            if self.min_value is not None and value < self.min_value:
                return False, f"{self.label} must be >= {self.min_value}"
            if self.max_value is not None and value > self.max_value:
                return False, f"{self.label} must be <= {self.max_value}"

        elif self.param_type == ParameterType.INTEGER:
            if not isinstance(value, int):
                return False, f"{self.label} must be an integer"
            if self.min_value is not None and value < self.min_value:
                return False, f"{self.label} must be >= {self.min_value}"
            if self.max_value is not None and value > self.max_value:
                return False, f"{self.label} must be <= {self.max_value}"

        elif self.param_type == ParameterType.BOOLEAN:
            if not isinstance(value, bool):
                return False, f"{self.label} must be a boolean"

        elif self.param_type == ParameterType.STRING:
            if not isinstance(value, str):
                return False, f"{self.label} must be a string"

        elif self.param_type == ParameterType.SELECT:
            if self.options and value not in self.options:
                return False, f"{self.label} must be one of: {', '.join(self.options)}"

        return True, None


@dataclass
class Node:
    """Instance of a node in the graph."""

    id: str  # Unique identifier for this node instance
    type: str  # Node type (e.g., "LinearMove", "SetHotend")
    position: dict[str, float]  # UI position {x, y}
    parameters: dict[str, Any] = field(default_factory=dict)  # Parameter values
    metadata: dict[str, Any] = field(default_factory=dict)  # Additional data

    def get_parameter(self, param_id: str, default: Any = None) -> Any:
        """Get a parameter value with optional default."""
        return self.parameters.get(param_id, default)


@dataclass
class Edge:
    """Connection between two nodes."""

    id: str  # Unique identifier for this edge
    source: str  # Source node ID
    source_port: str  # Source port ID
    target: str  # Target node ID
    target_port: str  # Target port ID
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class NodeGraph:
    """A complete node graph."""

    nodes: List[Node] = field(default_factory=list)
    edges: List[Edge] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def get_node(self, node_id: str) -> Optional[Node]:
        """Get a node by its ID."""
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None

    def get_outgoing_edges(self, node_id: str, port_id: Optional[str] = None) -> List[Edge]:
        """Get all edges originating from a node (optionally from a specific port)."""
        edges = [edge for edge in self.edges if edge.source == node_id]
        if port_id:
            edges = [edge for edge in edges if edge.source_port == port_id]
        return edges

    def get_incoming_edges(self, node_id: str, port_id: Optional[str] = None) -> List[Edge]:
        """Get all edges targeting a node (optionally to a specific port)."""
        edges = [edge for edge in self.edges if edge.target == node_id]
        if port_id:
            edges = [edge for edge in edges if edge.target_port == port_id]
        return edges

    def get_predecessors(self, node_id: str) -> List[str]:
        """Get all node IDs that directly connect to this node."""
        return [edge.source for edge in self.get_incoming_edges(node_id)]

    def get_successors(self, node_id: str) -> List[str]:
        """Get all node IDs that this node directly connects to."""
        return [edge.target for edge in self.get_outgoing_edges(node_id)]
