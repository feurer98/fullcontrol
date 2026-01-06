"""
Node to FullControl Steps Converter

This module converts a node graph to FullControl steps that can be transformed
into G-code. It handles topological sorting, validation, and step generation.
"""

from typing import Any, List, Optional, Dict
from collections import deque

import sys
from pathlib import Path

# Add fullcontrol to path
fullcontrol_path = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(fullcontrol_path))

import fullcontrol as fc

from .node_types import Node, Edge, NodeGraph, PortType


class GraphValidationError(Exception):
    """Raised when graph validation fails."""

    pass


class NodeConverter:
    """
    Converts a node graph to FullControl steps.

    This class handles:
    - Topological sorting of nodes
    - Cycle detection
    - Conversion of nodes to FullControl steps
    """

    def __init__(self):
        """Initialize the converter."""
        self.node_handlers: Dict[str, callable] = {
            "Start": self._convert_start,
            "End": self._convert_end,
            "Home": self._convert_home,
            "LinearMove": self._convert_linear_move,
            "ExtrudeMove": self._convert_extrude_move,
            "SetHotend": self._convert_set_hotend,
            "WaitHotend": self._convert_wait_hotend,
            "SetBed": self._convert_set_bed,
            "WaitBed": self._convert_wait_bed,
            "SetFan": self._convert_set_fan,
            "Comment": self._convert_comment,
            "CustomGCode": self._convert_custom_gcode,
        }

    def convert(self, graph: NodeGraph) -> List[Any]:
        """
        Convert a node graph to FullControl steps.

        Args:
            graph: The node graph to convert

        Returns:
            List of FullControl step objects

        Raises:
            GraphValidationError: If the graph is invalid
        """
        # Validate graph
        self._validate_graph(graph)

        # Find start node
        start_node = self._find_start_node(graph)
        if not start_node:
            raise GraphValidationError("No Start node found in graph")

        # Topological sort
        sorted_nodes = self._topological_sort(graph, start_node)

        # Convert nodes to steps
        steps = []
        for node in sorted_nodes:
            node_steps = self._convert_node(node, graph)
            steps.extend(node_steps)

        return steps

    def _validate_graph(self, graph: NodeGraph) -> None:
        """
        Validate the graph structure.

        Args:
            graph: The graph to validate

        Raises:
            GraphValidationError: If validation fails
        """
        # Check for cycles
        if self._has_cycles(graph):
            raise GraphValidationError("Graph contains cycles")

        # Validate node types
        for node in graph.nodes:
            if node.type not in self.node_handlers:
                raise GraphValidationError(f"Unknown node type: {node.type}")

    def _has_cycles(self, graph: NodeGraph) -> bool:
        """
        Check if the graph has cycles using DFS.

        Args:
            graph: The graph to check

        Returns:
            True if cycles exist, False otherwise
        """
        visited = set()
        rec_stack = set()

        def dfs(node_id: str) -> bool:
            visited.add(node_id)
            rec_stack.add(node_id)

            for successor in graph.get_successors(node_id):
                if successor not in visited:
                    if dfs(successor):
                        return True
                elif successor in rec_stack:
                    return True

            rec_stack.remove(node_id)
            return False

        for node in graph.nodes:
            if node.id not in visited:
                if dfs(node.id):
                    return True

        return False

    def _find_start_node(self, graph: NodeGraph) -> Optional[Node]:
        """Find the Start node in the graph."""
        for node in graph.nodes:
            if node.type == "Start":
                return node
        return None

    def _topological_sort(self, graph: NodeGraph, start_node: Node) -> List[Node]:
        """
        Perform topological sort starting from the start node.

        Uses BFS to traverse the graph in execution order.

        Args:
            graph: The graph to sort
            start_node: The starting node

        Returns:
            List of nodes in execution order
        """
        visited = set()
        result = []
        queue = deque([start_node.id])

        while queue:
            node_id = queue.popleft()

            if node_id in visited:
                continue

            visited.add(node_id)
            node = graph.get_node(node_id)
            if node:
                result.append(node)

                # Add successors to queue
                for successor_id in graph.get_successors(node_id):
                    if successor_id not in visited:
                        queue.append(successor_id)

        return result

    def _convert_node(self, node: Node, graph: NodeGraph) -> List[Any]:
        """
        Convert a single node to FullControl steps.

        Args:
            node: The node to convert
            graph: The complete graph (for context)

        Returns:
            List of FullControl steps
        """
        handler = self.node_handlers.get(node.type)
        if not handler:
            return []

        return handler(node, graph)

    # ========== Node-specific converters ==========

    def _convert_start(self, node: Node, graph: NodeGraph) -> List[Any]:
        """Convert Start node (generates initialization steps)."""
        # Start node doesn't generate steps, it's just a marker
        return []

    def _convert_end(self, node: Node, graph: NodeGraph) -> List[Any]:
        """Convert End node (generates finalization steps)."""
        # End node can add finalization comments
        return [fc.GcodeComment(text="End of print")]

    def _convert_home(self, node: Node, graph: NodeGraph) -> List[Any]:
        """Convert Home node to G28 command."""
        axes = node.get_parameter("axes", "XYZ")
        return [fc.ManualGcode(text=f"G28 {axes}")]

    def _convert_linear_move(self, node: Node, graph: NodeGraph) -> List[Any]:
        """Convert LinearMove node to Point."""
        x = node.get_parameter("x")
        y = node.get_parameter("y")
        z = node.get_parameter("z")

        return [fc.Point(x=x, y=y, z=z)]

    def _convert_extrude_move(self, node: Node, graph: NodeGraph) -> List[Any]:
        """Convert ExtrudeMove node to Extruder + Point."""
        x = node.get_parameter("x")
        y = node.get_parameter("y")
        z = node.get_parameter("z")

        return [
            fc.Extruder(on=True),
            fc.Point(x=x, y=y, z=z),
        ]

    def _convert_set_hotend(self, node: Node, graph: NodeGraph) -> List[Any]:
        """Convert SetHotend node to Hotend."""
        temp = node.get_parameter("temperature", 200)
        wait = node.get_parameter("wait", False)

        return [fc.Hotend(temp=temp, wait=wait)]

    def _convert_wait_hotend(self, node: Node, graph: NodeGraph) -> List[Any]:
        """Convert WaitHotend node to Hotend with wait=True."""
        temp = node.get_parameter("temperature", 200)

        return [fc.Hotend(temp=temp, wait=True)]

    def _convert_set_bed(self, node: Node, graph: NodeGraph) -> List[Any]:
        """Convert SetBed node to Buildplate."""
        temp = node.get_parameter("temperature", 60)
        wait = node.get_parameter("wait", False)

        return [fc.Buildplate(temp=temp, wait=wait)]

    def _convert_wait_bed(self, node: Node, graph: NodeGraph) -> List[Any]:
        """Convert WaitBed node to Buildplate with wait=True."""
        temp = node.get_parameter("temperature", 60)

        return [fc.Buildplate(temp=temp, wait=True)]

    def _convert_set_fan(self, node: Node, graph: NodeGraph) -> List[Any]:
        """Convert SetFan node to Fan."""
        speed = node.get_parameter("speed", 100)

        return [fc.Fan(speed_percent=speed)]

    def _convert_comment(self, node: Node, graph: NodeGraph) -> List[Any]:
        """Convert Comment node to GcodeComment."""
        text = node.get_parameter("text", "")

        return [fc.GcodeComment(text=text)]

    def _convert_custom_gcode(self, node: Node, graph: NodeGraph) -> List[Any]:
        """Convert CustomGCode node to ManualGcode."""
        gcode = node.get_parameter("gcode", "")

        return [fc.ManualGcode(text=gcode)]
