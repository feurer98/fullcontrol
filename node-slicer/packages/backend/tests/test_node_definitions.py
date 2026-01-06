"""
Unit tests for Node Definitions and Registry
"""

import pytest

from src.core.node_definitions import (
    NODE_REGISTRY,
    ValidationResult,
    get_node_definition,
    get_all_node_definitions,
    get_nodes_by_category,
    validate_node_type,
    START_NODE,
    END_NODE,
    HOME_NODE,
    LINEAR_MOVE_NODE,
    EXTRUDE_MOVE_NODE,
    SET_HOTEND_NODE,
    WAIT_HOTEND_NODE,
    SET_BED_NODE,
    WAIT_BED_NODE,
    SET_FAN_NODE,
    COMMENT_NODE,
    CUSTOM_GCODE_NODE,
)
from src.core.node_types import NodeCategory, PortType, ParameterType


class TestNodeRegistry:
    """Test suite for Node Registry."""

    def test_registry_has_12_nodes(self):
        """Test that registry contains all 12 MVP nodes."""
        assert len(NODE_REGISTRY) == 12

    def test_all_mvp_nodes_registered(self):
        """Test that all MVP node types are registered."""
        expected_types = [
            "Start",
            "End",
            "Home",
            "LinearMove",
            "ExtrudeMove",
            "SetHotend",
            "WaitHotend",
            "SetBed",
            "WaitBed",
            "SetFan",
            "Comment",
            "CustomGCode",
        ]
        for node_type in expected_types:
            assert node_type in NODE_REGISTRY

    def test_get_node_definition(self):
        """Test getting a node definition by type."""
        node_def = get_node_definition("LinearMove")
        assert node_def is not None
        assert node_def.id == "LinearMove"
        assert node_def.name == "Linear Move"

    def test_get_node_definition_unknown(self):
        """Test getting an unknown node type returns None."""
        node_def = get_node_definition("UnknownNode")
        assert node_def is None

    def test_get_all_node_definitions(self):
        """Test getting all node definitions."""
        all_nodes = get_all_node_definitions()
        assert len(all_nodes) == 12
        assert all(hasattr(node, "id") for node in all_nodes)

    def test_get_nodes_by_category(self):
        """Test getting nodes by category."""
        control_nodes = get_nodes_by_category(NodeCategory.CONTROL)
        assert len(control_nodes) == 2  # Start, End

        movement_nodes = get_nodes_by_category(NodeCategory.MOVEMENT)
        assert len(movement_nodes) == 3  # Home, LinearMove, ExtrudeMove

        temp_nodes = get_nodes_by_category(NodeCategory.TEMPERATURE)
        assert len(temp_nodes) == 4  # SetHotend, WaitHotend, SetBed, WaitBed

        hardware_nodes = get_nodes_by_category(NodeCategory.HARDWARE)
        assert len(hardware_nodes) == 1  # SetFan

        utility_nodes = get_nodes_by_category(NodeCategory.UTILITY)
        assert len(utility_nodes) == 2  # Comment, CustomGCode

    def test_validate_node_type(self):
        """Test node type validation."""
        assert validate_node_type("Start") is True
        assert validate_node_type("LinearMove") is True
        assert validate_node_type("UnknownNode") is False


class TestNodeDefinitions:
    """Test suite for individual node definitions."""

    def test_start_node_definition(self):
        """Test Start node definition."""
        assert START_NODE.id == "Start"
        assert START_NODE.category == NodeCategory.CONTROL
        assert len(START_NODE.inputs) == 0
        assert len(START_NODE.outputs) == 1
        assert START_NODE.outputs[0].port_type == PortType.EXEC
        assert len(START_NODE.parameters) == 0

    def test_end_node_definition(self):
        """Test End node definition."""
        assert END_NODE.id == "End"
        assert END_NODE.category == NodeCategory.CONTROL
        assert len(END_NODE.inputs) == 1
        assert len(END_NODE.outputs) == 0
        assert END_NODE.inputs[0].port_type == PortType.EXEC

    def test_home_node_definition(self):
        """Test Home node definition."""
        assert HOME_NODE.id == "Home"
        assert HOME_NODE.category == NodeCategory.MOVEMENT
        assert len(HOME_NODE.parameters) == 1
        assert HOME_NODE.parameters[0].id == "axes"
        assert HOME_NODE.parameters[0].param_type == ParameterType.SELECT
        assert "XYZ" in HOME_NODE.parameters[0].options

    def test_linear_move_node_definition(self):
        """Test LinearMove node definition."""
        assert LINEAR_MOVE_NODE.id == "LinearMove"
        assert LINEAR_MOVE_NODE.category == NodeCategory.MOVEMENT
        assert len(LINEAR_MOVE_NODE.parameters) == 3
        # Check X, Y, Z parameters
        param_ids = [p.id for p in LINEAR_MOVE_NODE.parameters]
        assert "x" in param_ids
        assert "y" in param_ids
        assert "z" in param_ids

    def test_extrude_move_node_definition(self):
        """Test ExtrudeMove node definition."""
        assert EXTRUDE_MOVE_NODE.id == "ExtrudeMove"
        assert EXTRUDE_MOVE_NODE.category == NodeCategory.MOVEMENT
        assert len(EXTRUDE_MOVE_NODE.parameters) == 3

    def test_set_hotend_node_definition(self):
        """Test SetHotend node definition."""
        assert SET_HOTEND_NODE.id == "SetHotend"
        assert SET_HOTEND_NODE.category == NodeCategory.TEMPERATURE
        assert len(SET_HOTEND_NODE.parameters) == 2
        # Check temperature parameter
        temp_param = next(p for p in SET_HOTEND_NODE.parameters if p.id == "temperature")
        assert temp_param.min_value == 0
        assert temp_param.max_value == 300
        # Check wait parameter
        wait_param = next(p for p in SET_HOTEND_NODE.parameters if p.id == "wait")
        assert wait_param.param_type == ParameterType.BOOLEAN

    def test_wait_hotend_node_definition(self):
        """Test WaitHotend node definition."""
        assert WAIT_HOTEND_NODE.id == "WaitHotend"
        assert WAIT_HOTEND_NODE.category == NodeCategory.TEMPERATURE
        assert len(WAIT_HOTEND_NODE.parameters) == 1

    def test_set_bed_node_definition(self):
        """Test SetBed node definition."""
        assert SET_BED_NODE.id == "SetBed"
        assert SET_BED_NODE.category == NodeCategory.TEMPERATURE
        temp_param = next(p for p in SET_BED_NODE.parameters if p.id == "temperature")
        assert temp_param.min_value == 0
        assert temp_param.max_value == 120

    def test_wait_bed_node_definition(self):
        """Test WaitBed node definition."""
        assert WAIT_BED_NODE.id == "WaitBed"
        assert WAIT_BED_NODE.category == NodeCategory.TEMPERATURE

    def test_set_fan_node_definition(self):
        """Test SetFan node definition."""
        assert SET_FAN_NODE.id == "SetFan"
        assert SET_FAN_NODE.category == NodeCategory.HARDWARE
        speed_param = SET_FAN_NODE.parameters[0]
        assert speed_param.id == "speed"
        assert speed_param.min_value == 0
        assert speed_param.max_value == 100

    def test_comment_node_definition(self):
        """Test Comment node definition."""
        assert COMMENT_NODE.id == "Comment"
        assert COMMENT_NODE.category == NodeCategory.UTILITY
        text_param = COMMENT_NODE.parameters[0]
        assert text_param.id == "text"
        assert text_param.param_type == ParameterType.STRING

    def test_custom_gcode_node_definition(self):
        """Test CustomGCode node definition."""
        assert CUSTOM_GCODE_NODE.id == "CustomGCode"
        assert CUSTOM_GCODE_NODE.category == NodeCategory.UTILITY
        gcode_param = CUSTOM_GCODE_NODE.parameters[0]
        assert gcode_param.id == "gcode"


class TestNodeValidation:
    """Test suite for node validation."""

    def test_validate_linear_move_valid_params(self):
        """Test validation with valid parameters."""
        params = {"x": 10.0, "y": 20.0, "z": 5.0}
        inputs = {"in": True}

        result = LINEAR_MOVE_NODE.validate(params, inputs)
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_linear_move_missing_input(self):
        """Test validation with missing required input."""
        params = {"x": 10.0}
        inputs = {}

        result = LINEAR_MOVE_NODE.validate(params, inputs)
        assert result.is_valid is False
        assert any("Required input" in error for error in result.errors)

    def test_validate_set_hotend_temp_out_of_range(self):
        """Test validation with temperature out of range."""
        params = {"temperature": 400, "wait": False}  # Max is 300
        inputs = {"in": True}

        result = SET_HOTEND_NODE.validate(params, inputs)
        assert result.is_valid is False
        assert any("must be <=" in error for error in result.errors)

    def test_validate_set_hotend_temp_valid(self):
        """Test validation with valid temperature."""
        params = {"temperature": 200, "wait": True}
        inputs = {"in": True}

        result = SET_HOTEND_NODE.validate(params, inputs)
        assert result.is_valid is True

    def test_validate_set_fan_speed_valid(self):
        """Test validation with valid fan speed."""
        params = {"speed": 75}
        inputs = {"in": True}

        result = SET_FAN_NODE.validate(params, inputs)
        assert result.is_valid is True

    def test_validate_set_fan_speed_out_of_range(self):
        """Test validation with fan speed out of range."""
        params = {"speed": 150}  # Max is 100
        inputs = {"in": True}

        result = SET_FAN_NODE.validate(params, inputs)
        assert result.is_valid is False

    def test_validate_home_axes_valid_option(self):
        """Test validation with valid axes selection."""
        params = {"axes": "XY"}
        inputs = {"in": True}

        result = HOME_NODE.validate(params, inputs)
        assert result.is_valid is True

    def test_validate_home_axes_invalid_option(self):
        """Test validation with invalid axes selection."""
        params = {"axes": "ABC"}  # Not in options
        inputs = {"in": True}

        result = HOME_NODE.validate(params, inputs)
        assert result.is_valid is False
        assert any("must be one of" in error for error in result.errors)

    def test_validate_comment_with_text(self):
        """Test validation of comment node with text."""
        params = {"text": "This is a test comment"}
        inputs = {"in": True}

        result = COMMENT_NODE.validate(params, inputs)
        assert result.is_valid is True

    def test_validate_custom_gcode(self):
        """Test validation of custom G-code node."""
        params = {"gcode": "M117 Hello World"}
        inputs = {"in": True}

        result = CUSTOM_GCODE_NODE.validate(params, inputs)
        assert result.is_valid is True


class TestPortDefinitions:
    """Test suite for port definitions."""

    def test_linear_move_has_exec_ports(self):
        """Test that LinearMove has execution ports."""
        input_port = LINEAR_MOVE_NODE.inputs[0]
        assert input_port.port_type == PortType.EXEC
        assert input_port.required is True

        output_port = LINEAR_MOVE_NODE.outputs[0]
        assert output_port.port_type == PortType.EXEC

    def test_linear_move_has_position_output(self):
        """Test that LinearMove has a position output port."""
        position_port = next(p for p in LINEAR_MOVE_NODE.outputs if p.id == "position")
        assert position_port.port_type == PortType.POSITION

    def test_set_hotend_has_temp_output(self):
        """Test that SetHotend has a temperature output port."""
        temp_port = next(p for p in SET_HOTEND_NODE.outputs if p.id == "temp")
        assert temp_port.port_type == PortType.TEMPERATURE

    def test_start_node_has_no_inputs(self):
        """Test that Start node has no inputs."""
        assert len(START_NODE.inputs) == 0
        assert len(START_NODE.outputs) == 1

    def test_end_node_has_no_outputs(self):
        """Test that End node has no outputs."""
        assert len(END_NODE.inputs) == 1
        assert len(END_NODE.outputs) == 0


class TestNodeColors:
    """Test suite for node UI colors."""

    def test_all_nodes_have_colors(self):
        """Test that all nodes have color definitions."""
        for node in get_all_node_definitions():
            assert node.color is not None
            assert node.color.startswith("#")
            assert len(node.color) == 7  # #RRGGBB format

    def test_category_color_consistency(self):
        """Test that nodes in same category have similar colors."""
        # This is just a basic check that colors are defined
        control_nodes = get_nodes_by_category(NodeCategory.CONTROL)
        for node in control_nodes:
            assert node.color is not None


class TestParameterDefinitions:
    """Test suite for parameter definitions."""

    def test_temperature_parameters_have_ranges(self):
        """Test that temperature parameters have appropriate ranges."""
        hotend_temp = next(p for p in SET_HOTEND_NODE.parameters if p.id == "temperature")
        assert hotend_temp.min_value is not None
        assert hotend_temp.max_value is not None
        assert hotend_temp.min_value < hotend_temp.max_value

        bed_temp = next(p for p in SET_BED_NODE.parameters if p.id == "temperature")
        assert bed_temp.min_value is not None
        assert bed_temp.max_value is not None

    def test_select_parameters_have_options(self):
        """Test that SELECT type parameters have options."""
        axes_param = next(p for p in HOME_NODE.parameters if p.id == "axes")
        assert axes_param.param_type == ParameterType.SELECT
        assert axes_param.options is not None
        assert len(axes_param.options) > 0

    def test_boolean_parameters_have_defaults(self):
        """Test that boolean parameters have default values."""
        wait_param = next(p for p in SET_HOTEND_NODE.parameters if p.id == "wait")
        assert wait_param.param_type == ParameterType.BOOLEAN
        assert wait_param.default_value is not None
        assert isinstance(wait_param.default_value, bool)

    def test_all_parameters_have_help_text(self):
        """Test that all parameters have help text."""
        for node in get_all_node_definitions():
            for param in node.parameters:
                assert param.help_text is not None
                assert len(param.help_text) > 0
