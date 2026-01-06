"""
Node Definitions and Registry

This module contains formal definitions for all MVP node types,
including their inputs, outputs, parameters, and validation logic.
"""

from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field

from .node_types import (
    NodeCategory,
    PortType,
    ParameterType,
    PortDefinition,
    ParameterDefinition,
)


@dataclass
class ValidationResult:
    """Result of node validation."""

    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class NodeDefinition:
    """
    Formal definition of a node type.

    This defines the schema for a node type including its ports,
    parameters, and validation logic.
    """

    id: str  # Unique identifier (e.g., "LinearMove")
    name: str  # Display name (e.g., "Linear Move")
    category: NodeCategory
    description: str
    inputs: List[PortDefinition] = field(default_factory=list)
    outputs: List[PortDefinition] = field(default_factory=list)
    parameters: List[ParameterDefinition] = field(default_factory=list)
    color: str = "#888888"  # UI color
    icon: Optional[str] = None  # Optional icon identifier

    def validate(self, params: Dict[str, Any], inputs: Dict[str, Any]) -> ValidationResult:
        """
        Validate a node instance with given parameters and inputs.

        Args:
            params: Parameter values
            inputs: Input port values

        Returns:
            ValidationResult with errors and warnings
        """
        result = ValidationResult(is_valid=True)

        # Validate parameters
        for param_def in self.parameters:
            value = params.get(param_def.id)
            is_valid, error = param_def.validate(value)
            if not is_valid:
                result.is_valid = False
                result.errors.append(error)

        # Validate required inputs
        for input_def in self.inputs:
            if input_def.required and input_def.id not in inputs:
                result.is_valid = False
                result.errors.append(f"Required input '{input_def.label}' is missing")

        return result


# ========== Control Nodes ==========

START_NODE = NodeDefinition(
    id="Start",
    name="Start",
    category=NodeCategory.CONTROL,
    description="Entry point for the node graph. Every graph must have exactly one Start node.",
    inputs=[],
    outputs=[
        PortDefinition(id="out", label="Out", port_type=PortType.EXEC, required=False)
    ],
    parameters=[],
    color="#4CAF50",
    icon="play_arrow",
)

END_NODE = NodeDefinition(
    id="End",
    name="End",
    category=NodeCategory.CONTROL,
    description="Exit point for the node graph. Generates finalization G-code.",
    inputs=[
        PortDefinition(id="in", label="In", port_type=PortType.EXEC, required=True)
    ],
    outputs=[],
    parameters=[],
    color="#F44336",
    icon="stop",
)

# ========== Movement Nodes ==========

HOME_NODE = NodeDefinition(
    id="Home",
    name="Home Axes",
    category=NodeCategory.MOVEMENT,
    description="Home (zero) the printer axes. Generates G28 command.",
    inputs=[
        PortDefinition(id="in", label="In", port_type=PortType.EXEC, required=True)
    ],
    outputs=[
        PortDefinition(id="out", label="Out", port_type=PortType.EXEC, required=False)
    ],
    parameters=[
        ParameterDefinition(
            id="axes",
            label="Axes",
            param_type=ParameterType.SELECT,
            default_value="XYZ",
            options=["X", "Y", "Z", "XY", "XZ", "YZ", "XYZ"],
            help_text="Which axes to home",
        )
    ],
    color="#2196F3",
    icon="home",
)

LINEAR_MOVE_NODE = NodeDefinition(
    id="LinearMove",
    name="Linear Move",
    category=NodeCategory.MOVEMENT,
    description="Move the print head to a specific position without extruding.",
    inputs=[
        PortDefinition(id="in", label="In", port_type=PortType.EXEC, required=True)
    ],
    outputs=[
        PortDefinition(id="out", label="Out", port_type=PortType.EXEC, required=False),
        PortDefinition(id="position", label="Position", port_type=PortType.POSITION, required=False),
    ],
    parameters=[
        ParameterDefinition(
            id="x",
            label="X",
            param_type=ParameterType.NUMBER,
            default_value=0.0,
            required=False,
            help_text="X coordinate (mm)",
        ),
        ParameterDefinition(
            id="y",
            label="Y",
            param_type=ParameterType.NUMBER,
            default_value=0.0,
            required=False,
            help_text="Y coordinate (mm)",
        ),
        ParameterDefinition(
            id="z",
            label="Z",
            param_type=ParameterType.NUMBER,
            default_value=0.0,
            required=False,
            help_text="Z coordinate (mm)",
        ),
    ],
    color="#03A9F4",
    icon="arrow_forward",
)

EXTRUDE_MOVE_NODE = NodeDefinition(
    id="ExtrudeMove",
    name="Extrude Move",
    category=NodeCategory.MOVEMENT,
    description="Move the print head while extruding material.",
    inputs=[
        PortDefinition(id="in", label="In", port_type=PortType.EXEC, required=True)
    ],
    outputs=[
        PortDefinition(id="out", label="Out", port_type=PortType.EXEC, required=False),
        PortDefinition(id="position", label="Position", port_type=PortType.POSITION, required=False),
    ],
    parameters=[
        ParameterDefinition(
            id="x",
            label="X",
            param_type=ParameterType.NUMBER,
            default_value=0.0,
            required=False,
            help_text="X coordinate (mm)",
        ),
        ParameterDefinition(
            id="y",
            label="Y",
            param_type=ParameterType.NUMBER,
            default_value=0.0,
            required=False,
            help_text="Y coordinate (mm)",
        ),
        ParameterDefinition(
            id="z",
            label="Z",
            param_type=ParameterType.NUMBER,
            default_value=0.0,
            required=False,
            help_text="Z coordinate (mm)",
        ),
    ],
    color="#00BCD4",
    icon="print",
)

# ========== Temperature Nodes ==========

SET_HOTEND_NODE = NodeDefinition(
    id="SetHotend",
    name="Set Hotend Temp",
    category=NodeCategory.TEMPERATURE,
    description="Set the hotend temperature. Can optionally wait for target temperature.",
    inputs=[
        PortDefinition(id="in", label="In", port_type=PortType.EXEC, required=True)
    ],
    outputs=[
        PortDefinition(id="out", label="Out", port_type=PortType.EXEC, required=False),
        PortDefinition(id="temp", label="Temperature", port_type=PortType.TEMPERATURE, required=False),
    ],
    parameters=[
        ParameterDefinition(
            id="temperature",
            label="Temperature",
            param_type=ParameterType.INTEGER,
            default_value=200,
            min_value=0,
            max_value=300,
            help_text="Target hotend temperature (°C)",
        ),
        ParameterDefinition(
            id="wait",
            label="Wait for Temperature",
            param_type=ParameterType.BOOLEAN,
            default_value=False,
            help_text="Wait until temperature is reached",
        ),
    ],
    color="#FF5722",
    icon="local_fire_department",
)

WAIT_HOTEND_NODE = NodeDefinition(
    id="WaitHotend",
    name="Wait for Hotend",
    category=NodeCategory.TEMPERATURE,
    description="Wait for the hotend to reach the specified temperature.",
    inputs=[
        PortDefinition(id="in", label="In", port_type=PortType.EXEC, required=True)
    ],
    outputs=[
        PortDefinition(id="out", label="Out", port_type=PortType.EXEC, required=False)
    ],
    parameters=[
        ParameterDefinition(
            id="temperature",
            label="Temperature",
            param_type=ParameterType.INTEGER,
            default_value=200,
            min_value=0,
            max_value=300,
            help_text="Target hotend temperature (°C)",
        ),
    ],
    color="#FF6F00",
    icon="hourglass_empty",
)

SET_BED_NODE = NodeDefinition(
    id="SetBed",
    name="Set Bed Temp",
    category=NodeCategory.TEMPERATURE,
    description="Set the heated bed temperature. Can optionally wait for target temperature.",
    inputs=[
        PortDefinition(id="in", label="In", port_type=PortType.EXEC, required=True)
    ],
    outputs=[
        PortDefinition(id="out", label="Out", port_type=PortType.EXEC, required=False),
        PortDefinition(id="temp", label="Temperature", port_type=PortType.TEMPERATURE, required=False),
    ],
    parameters=[
        ParameterDefinition(
            id="temperature",
            label="Temperature",
            param_type=ParameterType.INTEGER,
            default_value=60,
            min_value=0,
            max_value=120,
            help_text="Target bed temperature (°C)",
        ),
        ParameterDefinition(
            id="wait",
            label="Wait for Temperature",
            param_type=ParameterType.BOOLEAN,
            default_value=False,
            help_text="Wait until temperature is reached",
        ),
    ],
    color="#FF9800",
    icon="bed",
)

WAIT_BED_NODE = NodeDefinition(
    id="WaitBed",
    name="Wait for Bed",
    category=NodeCategory.TEMPERATURE,
    description="Wait for the heated bed to reach the specified temperature.",
    inputs=[
        PortDefinition(id="in", label="In", port_type=PortType.EXEC, required=True)
    ],
    outputs=[
        PortDefinition(id="out", label="Out", port_type=PortType.EXEC, required=False)
    ],
    parameters=[
        ParameterDefinition(
            id="temperature",
            label="Temperature",
            param_type=ParameterType.INTEGER,
            default_value=60,
            min_value=0,
            max_value=120,
            help_text="Target bed temperature (°C)",
        ),
    ],
    color="#FFA726",
    icon="hourglass_empty",
)

# ========== Hardware Nodes ==========

SET_FAN_NODE = NodeDefinition(
    id="SetFan",
    name="Set Fan Speed",
    category=NodeCategory.HARDWARE,
    description="Set the cooling fan speed as a percentage (0-100%).",
    inputs=[
        PortDefinition(id="in", label="In", port_type=PortType.EXEC, required=True)
    ],
    outputs=[
        PortDefinition(id="out", label="Out", port_type=PortType.EXEC, required=False)
    ],
    parameters=[
        ParameterDefinition(
            id="speed",
            label="Fan Speed",
            param_type=ParameterType.INTEGER,
            default_value=100,
            min_value=0,
            max_value=100,
            help_text="Fan speed percentage (0-100%)",
        ),
    ],
    color="#00BCD4",
    icon="air",
)

# ========== Utility Nodes ==========

COMMENT_NODE = NodeDefinition(
    id="Comment",
    name="Comment",
    category=NodeCategory.UTILITY,
    description="Add a comment to the G-code output for documentation.",
    inputs=[
        PortDefinition(id="in", label="In", port_type=PortType.EXEC, required=True)
    ],
    outputs=[
        PortDefinition(id="out", label="Out", port_type=PortType.EXEC, required=False)
    ],
    parameters=[
        ParameterDefinition(
            id="text",
            label="Comment Text",
            param_type=ParameterType.STRING,
            default_value="",
            help_text="Comment text to add to G-code",
        ),
    ],
    color="#9E9E9E",
    icon="comment",
)

CUSTOM_GCODE_NODE = NodeDefinition(
    id="CustomGCode",
    name="Custom G-Code",
    category=NodeCategory.UTILITY,
    description="Insert custom G-code commands directly into the output.",
    inputs=[
        PortDefinition(id="in", label="In", port_type=PortType.EXEC, required=True)
    ],
    outputs=[
        PortDefinition(id="out", label="Out", port_type=PortType.EXEC, required=False)
    ],
    parameters=[
        ParameterDefinition(
            id="gcode",
            label="G-Code",
            param_type=ParameterType.STRING,
            default_value="",
            help_text="Custom G-code command(s)",
        ),
    ],
    color="#607D8B",
    icon="code",
)


# ========== Node Registry ==========

NODE_REGISTRY: Dict[str, NodeDefinition] = {
    "Start": START_NODE,
    "End": END_NODE,
    "Home": HOME_NODE,
    "LinearMove": LINEAR_MOVE_NODE,
    "ExtrudeMove": EXTRUDE_MOVE_NODE,
    "SetHotend": SET_HOTEND_NODE,
    "WaitHotend": WAIT_HOTEND_NODE,
    "SetBed": SET_BED_NODE,
    "WaitBed": WAIT_BED_NODE,
    "SetFan": SET_FAN_NODE,
    "Comment": COMMENT_NODE,
    "CustomGCode": CUSTOM_GCODE_NODE,
}


def get_node_definition(node_type: str) -> Optional[NodeDefinition]:
    """
    Get a node definition by type.

    Args:
        node_type: The node type identifier

    Returns:
        NodeDefinition or None if not found
    """
    return NODE_REGISTRY.get(node_type)


def get_all_node_definitions() -> List[NodeDefinition]:
    """
    Get all registered node definitions.

    Returns:
        List of all node definitions
    """
    return list(NODE_REGISTRY.values())


def get_nodes_by_category(category: NodeCategory) -> List[NodeDefinition]:
    """
    Get all node definitions in a specific category.

    Args:
        category: The node category

    Returns:
        List of node definitions in the category
    """
    return [node for node in NODE_REGISTRY.values() if node.category == category]


def validate_node_type(node_type: str) -> bool:
    """
    Check if a node type is registered.

    Args:
        node_type: The node type identifier

    Returns:
        True if the node type exists, False otherwise
    """
    return node_type in NODE_REGISTRY
