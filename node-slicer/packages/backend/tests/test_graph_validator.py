"""
Unit tests for Graph Validation and Execution Engine
"""

import pytest

from src.core.graph_validator import (
    GraphValidator,
    GraphExecutor,
    ValidationError,
    GraphValidationResult,
)
from src.core.node_types import Node, Edge, NodeGraph


class TestGraphValidator:
    """Test suite for GraphValidator class."""

    def test_empty_graph(self):
        """Test validation of empty graph."""
        validator = GraphValidator()
        graph = NodeGraph()

        result = validator.validate(graph)

        assert result.is_valid is False
        assert len(result.errors) > 0
        assert any("empty" in error.message.lower() for error in result.errors)

    def test_valid_simple_graph(self):
        """Test validation of a valid simple graph."""
        validator = GraphValidator()
        graph = NodeGraph(
            nodes=[
                Node(id="start", type="Start", position={"x": 0, "y": 0}),
                Node(id="end", type="End", position={"x": 100, "y": 0}),
            ],
            edges=[
                Edge(id="e1", source="start", source_port="out", target="end", target_port="in")
            ],
        )

        result = validator.validate(graph)

        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_missing_start_node(self):
        """Test that missing Start node is detected."""
        validator = GraphValidator()
        graph = NodeGraph(
            nodes=[
                Node(id="node1", type="Home", position={"x": 0, "y": 0}),
                Node(id="end", type="End", position={"x": 100, "y": 0}),
            ],
            edges=[],
        )

        result = validator.validate(graph)

        assert result.is_valid is False
        assert any("Start node" in error.message for error in result.errors)

    def test_multiple_start_nodes(self):
        """Test that multiple Start nodes are detected."""
        validator = GraphValidator()
        graph = NodeGraph(
            nodes=[
                Node(id="start1", type="Start", position={"x": 0, "y": 0}),
                Node(id="start2", type="Start", position={"x": 0, "y": 100}),
                Node(id="end", type="End", position={"x": 100, "y": 0}),
            ],
            edges=[],
        )

        result = validator.validate(graph)

        assert result.is_valid is False
        assert any("multiple" in error.message.lower() for error in result.errors)

    def test_missing_end_node(self):
        """Test that missing End node generates warning."""
        validator = GraphValidator()
        graph = NodeGraph(
            nodes=[
                Node(id="start", type="Start", position={"x": 0, "y": 0}),
                Node(id="node1", type="Home", position={"x": 100, "y": 0}),
            ],
            edges=[],
        )

        result = validator.validate(graph)

        # Missing End is a warning, not an error
        assert len(result.warnings) > 0
        assert any("End node" in warning.message for warning in result.warnings)

    def test_unknown_node_type(self):
        """Test that unknown node types are detected."""
        validator = GraphValidator()
        graph = NodeGraph(
            nodes=[
                Node(id="start", type="Start", position={"x": 0, "y": 0}),
                Node(id="unknown", type="UnknownType", position={"x": 100, "y": 0}),
            ],
            edges=[],
        )

        result = validator.validate(graph)

        assert result.is_valid is False
        assert any("Unknown node type" in error.message for error in result.errors)

    def test_cycle_detection(self):
        """Test that cycles are detected."""
        validator = GraphValidator()
        graph = NodeGraph(
            nodes=[
                Node(id="start", type="Start", position={"x": 0, "y": 0}),
                Node(id="node1", type="Home", position={"x": 100, "y": 0}),
                Node(id="node2", type="Comment", position={"x": 200, "y": 0}, parameters={"text": "test"}),
            ],
            edges=[
                Edge(id="e1", source="start", source_port="out", target="node1", target_port="in"),
                Edge(id="e2", source="node1", source_port="out", target="node2", target_port="in"),
                Edge(id="e3", source="node2", source_port="out", target="node1", target_port="in"),  # Cycle!
            ],
        )

        result = validator.validate(graph)

        assert result.is_valid is False
        assert any("cycle" in error.message.lower() for error in result.errors)

    def test_duplicate_node_ids(self):
        """Test that duplicate node IDs are detected."""
        validator = GraphValidator()
        graph = NodeGraph(
            nodes=[
                Node(id="node1", type="Start", position={"x": 0, "y": 0}),
                Node(id="node1", type="End", position={"x": 100, "y": 0}),  # Duplicate ID
            ],
            edges=[],
        )

        result = validator.validate(graph)

        assert result.is_valid is False
        assert any("Duplicate node ID" in error.message for error in result.errors)

    def test_duplicate_edge_ids(self):
        """Test that duplicate edge IDs are detected."""
        validator = GraphValidator()
        graph = NodeGraph(
            nodes=[
                Node(id="start", type="Start", position={"x": 0, "y": 0}),
                Node(id="node1", type="Home", position={"x": 100, "y": 0}),
                Node(id="end", type="End", position={"x": 200, "y": 0}),
            ],
            edges=[
                Edge(id="e1", source="start", source_port="out", target="node1", target_port="in"),
                Edge(id="e1", source="node1", source_port="out", target="end", target_port="in"),  # Duplicate ID
            ],
        )

        result = validator.validate(graph)

        assert result.is_valid is False
        assert any("Duplicate edge ID" in error.message for error in result.errors)

    def test_edge_to_nonexistent_node(self):
        """Test that edges to non-existent nodes are detected."""
        validator = GraphValidator()
        graph = NodeGraph(
            nodes=[
                Node(id="start", type="Start", position={"x": 0, "y": 0}),
            ],
            edges=[
                Edge(id="e1", source="start", source_port="out", target="nonexistent", target_port="in"),
            ],
        )

        result = validator.validate(graph)

        assert result.is_valid is False
        assert any("non-existent" in error.message.lower() for error in result.errors)

    def test_unreachable_nodes(self):
        """Test that unreachable nodes are detected."""
        validator = GraphValidator()
        graph = NodeGraph(
            nodes=[
                Node(id="start", type="Start", position={"x": 0, "y": 0}),
                Node(id="node1", type="Home", position={"x": 100, "y": 0}),
                Node(id="isolated", type="Comment", position={"x": 200, "y": 200}, parameters={"text": "isolated"}),
                Node(id="end", type="End", position={"x": 200, "y": 0}),
            ],
            edges=[
                Edge(id="e1", source="start", source_port="out", target="node1", target_port="in"),
                Edge(id="e2", source="node1", source_port="out", target="end", target_port="in"),
            ],
        )

        result = validator.validate(graph)

        # Unreachable nodes generate warnings
        assert len(result.warnings) > 0
        assert any("unreachable" in warning.message.lower() for warning in result.warnings)

    def test_isolated_nodes(self):
        """Test that isolated nodes (no connections) are detected."""
        validator = GraphValidator()
        graph = NodeGraph(
            nodes=[
                Node(id="start", type="Start", position={"x": 0, "y": 0}),
                Node(id="isolated", type="Home", position={"x": 200, "y": 200}),
                Node(id="end", type="End", position={"x": 100, "y": 0}),
            ],
            edges=[
                Edge(id="e1", source="start", source_port="out", target="end", target_port="in"),
            ],
        )

        result = validator.validate(graph)

        # Isolated nodes generate warnings
        assert len(result.warnings) > 0
        assert any("isolated" in warning.message.lower() for warning in result.warnings)

    def test_invalid_output_port(self):
        """Test that invalid output ports are detected."""
        validator = GraphValidator()
        graph = NodeGraph(
            nodes=[
                Node(id="start", type="Start", position={"x": 0, "y": 0}),
                Node(id="end", type="End", position={"x": 100, "y": 0}),
            ],
            edges=[
                Edge(id="e1", source="start", source_port="nonexistent_port", target="end", target_port="in"),
            ],
        )

        result = validator.validate(graph)

        assert result.is_valid is False
        assert any("output port" in error.message.lower() for error in result.errors)

    def test_invalid_input_port(self):
        """Test that invalid input ports are detected."""
        validator = GraphValidator()
        graph = NodeGraph(
            nodes=[
                Node(id="start", type="Start", position={"x": 0, "y": 0}),
                Node(id="end", type="End", position={"x": 100, "y": 0}),
            ],
            edges=[
                Edge(id="e1", source="start", source_port="out", target="end", target_port="nonexistent_port"),
            ],
        )

        result = validator.validate(graph)

        assert result.is_valid is False
        assert any("input port" in error.message.lower() for error in result.errors)

    def test_incompatible_port_types(self):
        """Test that incompatible port types are detected."""
        validator = GraphValidator()
        # Try to connect position output to exec input (incompatible)
        graph = NodeGraph(
            nodes=[
                Node(id="start", type="Start", position={"x": 0, "y": 0}),
                Node(id="move", type="LinearMove", position={"x": 100, "y": 0}, parameters={"x": 10, "y": 10, "z": 5}),
                Node(id="end", type="End", position={"x": 200, "y": 0}),
            ],
            edges=[
                Edge(id="e1", source="start", source_port="out", target="move", target_port="in"),
                # Try to connect position output to exec input (incompatible)
                Edge(id="e2", source="move", source_port="position", target="end", target_port="in"),
            ],
        )

        result = validator.validate(graph)

        assert result.is_valid is False
        assert any("incompatible" in error.message.lower() for error in result.errors)

    def test_invalid_parameters(self):
        """Test that invalid node parameters are detected."""
        validator = GraphValidator()
        graph = NodeGraph(
            nodes=[
                Node(id="start", type="Start", position={"x": 0, "y": 0}),
                Node(
                    id="hotend",
                    type="SetHotend",
                    position={"x": 100, "y": 0},
                    parameters={"temperature": 500, "wait": False},  # Out of range!
                ),
            ],
            edges=[],
        )

        result = validator.validate(graph)

        assert result.is_valid is False
        # Should have parameter validation error
        assert any(
            "hotend" in str(error.node_id).lower() and error.node_id == "hotend"
            for error in result.errors
        )


class TestGraphExecutor:
    """Test suite for GraphExecutor class."""

    def test_simple_execution_order(self):
        """Test execution order for simple linear graph."""
        executor = GraphExecutor()
        graph = NodeGraph(
            nodes=[
                Node(id="start", type="Start", position={"x": 0, "y": 0}),
                Node(id="node1", type="Home", position={"x": 100, "y": 0}),
                Node(id="node2", type="Comment", position={"x": 200, "y": 0}, parameters={"text": "test"}),
                Node(id="end", type="End", position={"x": 300, "y": 0}),
            ],
            edges=[
                Edge(id="e1", source="start", source_port="out", target="node1", target_port="in"),
                Edge(id="e2", source="node1", source_port="out", target="node2", target_port="in"),
                Edge(id="e3", source="node2", source_port="out", target="end", target_port="in"),
            ],
        )

        order = executor.get_execution_order(graph)

        assert len(order) == 4
        assert order[0].id == "start"
        assert order[1].id == "node1"
        assert order[2].id == "node2"
        assert order[3].id == "end"

    def test_execution_order_with_branches(self):
        """Test execution order with parallel branches."""
        executor = GraphExecutor()
        # Start -> Node1 -> Node3
        #       -> Node2 -> Node3
        graph = NodeGraph(
            nodes=[
                Node(id="start", type="Start", position={"x": 0, "y": 0}),
                Node(id="node1", type="Home", position={"x": 100, "y": 0}),
                Node(id="node2", type="Comment", position={"x": 100, "y": 100}, parameters={"text": "branch"}),
                Node(id="node3", type="End", position={"x": 200, "y": 50}),
            ],
            edges=[
                Edge(id="e1", source="start", source_port="out", target="node1", target_port="in"),
                Edge(id="e2", source="start", source_port="out", target="node2", target_port="in"),
                Edge(id="e3", source="node1", source_port="out", target="node3", target_port="in"),
                Edge(id="e4", source="node2", source_port="out", target="node3", target_port="in"),
            ],
        )

        order = executor.get_execution_order(graph)

        assert len(order) == 4
        assert order[0].id == "start"
        # Node1 and Node2 can be in any order (they're parallel)
        assert set([order[1].id, order[2].id]) == {"node1", "node2"}
        # Node3 must be last (depends on both)
        assert order[3].id == "node3"

    def test_execution_order_no_start_node(self):
        """Test that execution order fails without Start node."""
        executor = GraphExecutor()
        graph = NodeGraph(
            nodes=[
                Node(id="node1", type="Home", position={"x": 0, "y": 0}),
                Node(id="end", type="End", position={"x": 100, "y": 0}),
            ],
            edges=[
                Edge(id="e1", source="node1", source_port="out", target="end", target_port="in"),
            ],
        )

        with pytest.raises(ValueError, match="Start node"):
            executor.get_execution_order(graph)

    def test_execution_order_with_cycle(self):
        """Test that execution order fails with cycles."""
        executor = GraphExecutor()
        graph = NodeGraph(
            nodes=[
                Node(id="start", type="Start", position={"x": 0, "y": 0}),
                Node(id="node1", type="Home", position={"x": 100, "y": 0}),
                Node(id="node2", type="Comment", position={"x": 200, "y": 0}, parameters={"text": "test"}),
            ],
            edges=[
                Edge(id="e1", source="start", source_port="out", target="node1", target_port="in"),
                Edge(id="e2", source="node1", source_port="out", target="node2", target_port="in"),
                Edge(id="e3", source="node2", source_port="out", target="node1", target_port="in"),  # Cycle!
            ],
        )

        with pytest.raises(ValueError, match="cycle"):
            executor.get_execution_order(graph)


class TestValidationResult:
    """Test suite for ValidationResult class."""

    def test_add_error(self):
        """Test adding an error to result."""
        result = GraphValidationResult(is_valid=True)
        result.add_error("Test error", node_id="node1")

        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].message == "Test error"
        assert result.errors[0].node_id == "node1"

    def test_add_warning(self):
        """Test adding a warning to result."""
        result = GraphValidationResult(is_valid=True)
        result.add_warning("Test warning", edge_id="edge1")

        assert result.is_valid is True  # Warnings don't invalidate
        assert len(result.warnings) == 1
        assert result.warnings[0].message == "Test warning"
        assert result.warnings[0].edge_id == "edge1"

    def test_multiple_errors(self):
        """Test adding multiple errors."""
        result = GraphValidationResult(is_valid=True)
        result.add_error("Error 1")
        result.add_error("Error 2", details="More info")

        assert result.is_valid is False
        assert len(result.errors) == 2
        assert result.errors[1].details == "More info"
