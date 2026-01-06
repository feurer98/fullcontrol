"""
Unit tests for NodeConverter

Tests the conversion of node graphs to FullControl steps.
"""

import pytest
import sys
from pathlib import Path

# Add fullcontrol to path
fullcontrol_path = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(fullcontrol_path))

import fullcontrol as fc

from src.core.node_converter import NodeConverter, GraphValidationError
from src.core.node_types import Node, Edge, NodeGraph


class TestNodeConverter:
    """Test suite for NodeConverter class."""

    def test_initialization(self):
        """Test that converter initializes correctly."""
        converter = NodeConverter()
        assert converter is not None
        assert len(converter.node_handlers) > 0

    def test_empty_graph_raises_error(self):
        """Test that empty graph raises validation error."""
        converter = NodeConverter()
        graph = NodeGraph()

        with pytest.raises(GraphValidationError, match="No Start node"):
            converter.convert(graph)

    def test_graph_without_start_node(self):
        """Test that graph without Start node raises error."""
        converter = NodeConverter()
        graph = NodeGraph(
            nodes=[Node(id="1", type="End", position={"x": 0, "y": 0})], edges=[]
        )

        with pytest.raises(GraphValidationError, match="No Start node"):
            converter.convert(graph)

    def test_simple_start_end_graph(self):
        """Test conversion of simple Start -> End graph."""
        converter = NodeConverter()
        graph = NodeGraph(
            nodes=[
                Node(id="start", type="Start", position={"x": 0, "y": 0}),
                Node(id="end", type="End", position={"x": 100, "y": 0}),
            ],
            edges=[Edge(id="e1", source="start", source_port="out", target="end", target_port="in")],
        )

        steps = converter.convert(graph)

        # Start generates no steps, End generates a comment
        assert len(steps) == 1
        assert isinstance(steps[0], fc.GcodeComment)

    def test_home_node(self):
        """Test conversion of Home node."""
        converter = NodeConverter()
        graph = NodeGraph(
            nodes=[
                Node(id="start", type="Start", position={"x": 0, "y": 0}),
                Node(
                    id="home",
                    type="Home",
                    position={"x": 100, "y": 0},
                    parameters={"axes": "XYZ"},
                ),
            ],
            edges=[Edge(id="e1", source="start", source_port="out", target="home", target_port="in")],
        )

        steps = converter.convert(graph)

        assert len(steps) == 1
        assert isinstance(steps[0], fc.ManualGcode)
        assert steps[0].text == "G28 XYZ"

    def test_linear_move_node(self):
        """Test conversion of LinearMove node."""
        converter = NodeConverter()
        graph = NodeGraph(
            nodes=[
                Node(id="start", type="Start", position={"x": 0, "y": 0}),
                Node(
                    id="move",
                    type="LinearMove",
                    position={"x": 100, "y": 0},
                    parameters={"x": 10.0, "y": 20.0, "z": 5.0},
                ),
            ],
            edges=[Edge(id="e1", source="start", source_port="out", target="move", target_port="in")],
        )

        steps = converter.convert(graph)

        assert len(steps) == 1
        assert isinstance(steps[0], fc.Point)
        assert steps[0].x == 10.0
        assert steps[0].y == 20.0
        assert steps[0].z == 5.0

    def test_extrude_move_node(self):
        """Test conversion of ExtrudeMove node."""
        converter = NodeConverter()
        graph = NodeGraph(
            nodes=[
                Node(id="start", type="Start", position={"x": 0, "y": 0}),
                Node(
                    id="extrude",
                    type="ExtrudeMove",
                    position={"x": 100, "y": 0},
                    parameters={"x": 15.0, "y": 25.0, "z": 3.0},
                ),
            ],
            edges=[Edge(id="e1", source="start", source_port="out", target="extrude", target_port="in")],
        )

        steps = converter.convert(graph)

        assert len(steps) == 2
        assert isinstance(steps[0], fc.Extruder)
        assert steps[0].on is True
        assert isinstance(steps[1], fc.Point)
        assert steps[1].x == 15.0

    def test_set_hotend_node(self):
        """Test conversion of SetHotend node."""
        converter = NodeConverter()
        graph = NodeGraph(
            nodes=[
                Node(id="start", type="Start", position={"x": 0, "y": 0}),
                Node(
                    id="hotend",
                    type="SetHotend",
                    position={"x": 100, "y": 0},
                    parameters={"temperature": 210, "wait": False},
                ),
            ],
            edges=[Edge(id="e1", source="start", source_port="out", target="hotend", target_port="in")],
        )

        steps = converter.convert(graph)

        assert len(steps) == 1
        assert isinstance(steps[0], fc.Hotend)
        assert steps[0].temp == 210
        assert steps[0].wait is False

    def test_wait_hotend_node(self):
        """Test conversion of WaitHotend node."""
        converter = NodeConverter()
        graph = NodeGraph(
            nodes=[
                Node(id="start", type="Start", position={"x": 0, "y": 0}),
                Node(
                    id="wait_hotend",
                    type="WaitHotend",
                    position={"x": 100, "y": 0},
                    parameters={"temperature": 200},
                ),
            ],
            edges=[Edge(id="e1", source="start", source_port="out", target="wait_hotend", target_port="in")],
        )

        steps = converter.convert(graph)

        assert len(steps) == 1
        assert isinstance(steps[0], fc.Hotend)
        assert steps[0].temp == 200
        assert steps[0].wait is True

    def test_set_bed_node(self):
        """Test conversion of SetBed node."""
        converter = NodeConverter()
        graph = NodeGraph(
            nodes=[
                Node(id="start", type="Start", position={"x": 0, "y": 0}),
                Node(
                    id="bed",
                    type="SetBed",
                    position={"x": 100, "y": 0},
                    parameters={"temperature": 70, "wait": True},
                ),
            ],
            edges=[Edge(id="e1", source="start", source_port="out", target="bed", target_port="in")],
        )

        steps = converter.convert(graph)

        assert len(steps) == 1
        assert isinstance(steps[0], fc.Buildplate)
        assert steps[0].temp == 70
        assert steps[0].wait is True

    def test_wait_bed_node(self):
        """Test conversion of WaitBed node."""
        converter = NodeConverter()
        graph = NodeGraph(
            nodes=[
                Node(id="start", type="Start", position={"x": 0, "y": 0}),
                Node(
                    id="wait_bed",
                    type="WaitBed",
                    position={"x": 100, "y": 0},
                    parameters={"temperature": 60},
                ),
            ],
            edges=[Edge(id="e1", source="start", source_port="out", target="wait_bed", target_port="in")],
        )

        steps = converter.convert(graph)

        assert len(steps) == 1
        assert isinstance(steps[0], fc.Buildplate)
        assert steps[0].temp == 60
        assert steps[0].wait is True

    def test_set_fan_node(self):
        """Test conversion of SetFan node."""
        converter = NodeConverter()
        graph = NodeGraph(
            nodes=[
                Node(id="start", type="Start", position={"x": 0, "y": 0}),
                Node(
                    id="fan",
                    type="SetFan",
                    position={"x": 100, "y": 0},
                    parameters={"speed": 75},
                ),
            ],
            edges=[Edge(id="e1", source="start", source_port="out", target="fan", target_port="in")],
        )

        steps = converter.convert(graph)

        assert len(steps) == 1
        assert isinstance(steps[0], fc.Fan)
        assert steps[0].speed_percent == 75

    def test_comment_node(self):
        """Test conversion of Comment node."""
        converter = NodeConverter()
        graph = NodeGraph(
            nodes=[
                Node(id="start", type="Start", position={"x": 0, "y": 0}),
                Node(
                    id="comment",
                    type="Comment",
                    position={"x": 100, "y": 0},
                    parameters={"text": "This is a test comment"},
                ),
            ],
            edges=[Edge(id="e1", source="start", source_port="out", target="comment", target_port="in")],
        )

        steps = converter.convert(graph)

        assert len(steps) == 1
        assert isinstance(steps[0], fc.GcodeComment)
        assert steps[0].text == "This is a test comment"

    def test_custom_gcode_node(self):
        """Test conversion of CustomGCode node."""
        converter = NodeConverter()
        graph = NodeGraph(
            nodes=[
                Node(id="start", type="Start", position={"x": 0, "y": 0}),
                Node(
                    id="custom",
                    type="CustomGCode",
                    position={"x": 100, "y": 0},
                    parameters={"gcode": "M117 Hello World"},
                ),
            ],
            edges=[Edge(id="e1", source="start", source_port="out", target="custom", target_port="in")],
        )

        steps = converter.convert(graph)

        assert len(steps) == 1
        assert isinstance(steps[0], fc.ManualGcode)
        assert steps[0].text == "M117 Hello World"

    def test_sequence_of_nodes(self):
        """Test conversion of a sequence: Start -> Home -> SetHotend -> LinearMove -> End."""
        converter = NodeConverter()
        graph = NodeGraph(
            nodes=[
                Node(id="start", type="Start", position={"x": 0, "y": 0}),
                Node(id="home", type="Home", position={"x": 100, "y": 0}, parameters={"axes": "XYZ"}),
                Node(
                    id="hotend",
                    type="SetHotend",
                    position={"x": 200, "y": 0},
                    parameters={"temperature": 200, "wait": True},
                ),
                Node(
                    id="move",
                    type="LinearMove",
                    position={"x": 300, "y": 0},
                    parameters={"x": 50, "y": 50, "z": 10},
                ),
                Node(id="end", type="End", position={"x": 400, "y": 0}),
            ],
            edges=[
                Edge(id="e1", source="start", source_port="out", target="home", target_port="in"),
                Edge(id="e2", source="home", source_port="out", target="hotend", target_port="in"),
                Edge(id="e3", source="hotend", source_port="out", target="move", target_port="in"),
                Edge(id="e4", source="move", source_port="out", target="end", target_port="in"),
            ],
        )

        steps = converter.convert(graph)

        # Start (0) + Home (1) + Hotend (1) + Move (1) + End (1) = 4 steps
        assert len(steps) == 4

        assert isinstance(steps[0], fc.ManualGcode)  # Home
        assert steps[0].text == "G28 XYZ"

        assert isinstance(steps[1], fc.Hotend)  # SetHotend
        assert steps[1].temp == 200

        assert isinstance(steps[2], fc.Point)  # LinearMove
        assert steps[2].x == 50

        assert isinstance(steps[3], fc.GcodeComment)  # End

    def test_unknown_node_type(self):
        """Test that unknown node type raises validation error."""
        converter = NodeConverter()
        graph = NodeGraph(
            nodes=[
                Node(id="start", type="Start", position={"x": 0, "y": 0}),
                Node(id="unknown", type="UnknownType", position={"x": 100, "y": 0}),
            ],
            edges=[Edge(id="e1", source="start", source_port="out", target="unknown", target_port="in")],
        )

        with pytest.raises(GraphValidationError, match="Unknown node type"):
            converter.convert(graph)

    def test_cyclic_graph_detection(self):
        """Test that cycles in graph are detected."""
        converter = NodeConverter()
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

        with pytest.raises(GraphValidationError, match="contains cycles"):
            converter.convert(graph)

    def test_multiple_paths_converge(self):
        """Test that multiple paths can converge to same node (not a cycle)."""
        converter = NodeConverter()
        # Start -> Node1 -> Node3
        #       -> Node2 -> Node3
        graph = NodeGraph(
            nodes=[
                Node(id="start", type="Start", position={"x": 0, "y": 0}),
                Node(id="node1", type="Comment", position={"x": 100, "y": 0}, parameters={"text": "path1"}),
                Node(id="node2", type="Comment", position={"x": 100, "y": 100}, parameters={"text": "path2"}),
                Node(id="node3", type="End", position={"x": 200, "y": 50}),
            ],
            edges=[
                Edge(id="e1", source="start", source_port="out", target="node1", target_port="in"),
                Edge(id="e2", source="start", source_port="out", target="node2", target_port="in"),
                Edge(id="e3", source="node1", source_port="out", target="node3", target_port="in"),
                Edge(id="e4", source="node2", source_port="out", target="node3", target_port="in"),
            ],
        )

        # This should not raise an error (convergence is not a cycle)
        steps = converter.convert(graph)
        assert len(steps) >= 1  # Should have at least the End comment
