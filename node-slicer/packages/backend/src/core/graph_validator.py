"""
Graph Validation and Execution Engine

This module provides comprehensive validation for node graphs including
connection validation, cycle detection, and reachability analysis.
"""

from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field

from .node_types import Node, Edge, NodeGraph, PortType
from .node_definitions import get_node_definition


@dataclass
class ValidationError:
    """Represents a validation error."""

    severity: str  # "error" or "warning"
    message: str
    node_id: Optional[str] = None
    edge_id: Optional[str] = None
    details: Optional[str] = None


@dataclass
class GraphValidationResult:
    """Result of graph validation."""

    is_valid: bool
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[ValidationError] = field(default_factory=list)

    def add_error(
        self,
        message: str,
        node_id: Optional[str] = None,
        edge_id: Optional[str] = None,
        details: Optional[str] = None,
    ):
        """Add an error to the result."""
        self.errors.append(
            ValidationError(
                severity="error",
                message=message,
                node_id=node_id,
                edge_id=edge_id,
                details=details,
            )
        )
        self.is_valid = False

    def add_warning(
        self,
        message: str,
        node_id: Optional[str] = None,
        edge_id: Optional[str] = None,
        details: Optional[str] = None,
    ):
        """Add a warning to the result."""
        self.warnings.append(
            ValidationError(
                severity="warning",
                message=message,
                node_id=node_id,
                edge_id=edge_id,
                details=details,
            )
        )


class GraphValidator:
    """
    Comprehensive graph validation engine.

    Validates node graphs for structural integrity, connection validity,
    and execution correctness.
    """

    def validate(self, graph: NodeGraph) -> GraphValidationResult:
        """
        Perform comprehensive graph validation.

        Args:
            graph: The graph to validate

        Returns:
            GraphValidationResult with all errors and warnings
        """
        result = GraphValidationResult(is_valid=True)

        # Run all validation checks
        self._validate_nodes(graph, result)
        self._validate_edges(graph, result)
        self._validate_start_node(graph, result)
        self._validate_end_node(graph, result)
        self._validate_cycles(graph, result)
        self._validate_reachability(graph, result)
        self._validate_connections(graph, result)
        self._validate_isolated_nodes(graph, result)

        return result

    def _validate_nodes(self, graph: NodeGraph, result: GraphValidationResult):
        """Validate all nodes in the graph."""
        if len(graph.nodes) == 0:
            result.add_error("Graph is empty")
            return

        # Check for duplicate node IDs
        node_ids = [node.id for node in graph.nodes]
        duplicates = set([nid for nid in node_ids if node_ids.count(nid) > 1])
        for dup_id in duplicates:
            result.add_error(f"Duplicate node ID: {dup_id}", node_id=dup_id)

        # Build map of connected inputs for each node
        connected_inputs = {node.id: set() for node in graph.nodes}
        for edge in graph.edges:
            if edge.target in connected_inputs:
                connected_inputs[edge.target].add(edge.target_port)

        # Validate each node
        for node in graph.nodes:
            # Check if node type exists
            node_def = get_node_definition(node.type)
            if not node_def:
                result.add_error(
                    f"Unknown node type: {node.type}",
                    node_id=node.id,
                    details=f"Node '{node.id}' has unrecognized type '{node.type}'",
                )
                continue

            # Validate node parameters with connected inputs
            params = node.parameters or {}
            inputs = {port_id: True for port_id in connected_inputs.get(node.id, set())}
            validation = node_def.validate(params, inputs)

            if not validation.is_valid:
                for error in validation.errors:
                    result.add_error(
                        error,
                        node_id=node.id,
                        details=f"Parameter validation failed for node '{node.id}'",
                    )

    def _validate_edges(self, graph: NodeGraph, result: GraphValidationResult):
        """Validate all edges in the graph."""
        if len(graph.edges) == 0 and len(graph.nodes) > 1:
            result.add_warning("Graph has nodes but no connections")

        # Check for duplicate edge IDs
        edge_ids = [edge.id for edge in graph.edges]
        duplicates = set([eid for eid in edge_ids if edge_ids.count(eid) > 1])
        for dup_id in duplicates:
            result.add_error(f"Duplicate edge ID: {dup_id}", edge_id=dup_id)

        # Validate each edge
        for edge in graph.edges:
            # Check if source node exists
            source_node = graph.get_node(edge.source)
            if not source_node:
                result.add_error(
                    f"Edge references non-existent source node: {edge.source}",
                    edge_id=edge.id,
                )
                continue

            # Check if target node exists
            target_node = graph.get_node(edge.target)
            if not target_node:
                result.add_error(
                    f"Edge references non-existent target node: {edge.target}",
                    edge_id=edge.id,
                )
                continue

    def _validate_start_node(self, graph: NodeGraph, result: GraphValidationResult):
        """Validate that graph has exactly one Start node."""
        start_nodes = [node for node in graph.nodes if node.type == "Start"]

        if len(start_nodes) == 0:
            result.add_error("Graph must have exactly one Start node")
        elif len(start_nodes) > 1:
            result.add_error(
                f"Graph has multiple Start nodes ({len(start_nodes)})",
                details="Found Start nodes: " + ", ".join([n.id for n in start_nodes]),
            )

    def _validate_end_node(self, graph: NodeGraph, result: GraphValidationResult):
        """Validate that graph has at least one End node."""
        end_nodes = [node for node in graph.nodes if node.type == "End"]

        if len(end_nodes) == 0:
            result.add_warning("Graph should have at least one End node")

    def _validate_cycles(self, graph: NodeGraph, result: GraphValidationResult):
        """Detect cycles in the graph using DFS."""
        visited = set()
        rec_stack = set()
        cycle_found = False

        def dfs(node_id: str, path: List[str]) -> Optional[List[str]]:
            """DFS to detect cycles. Returns cycle path if found."""
            visited.add(node_id)
            rec_stack.add(node_id)
            path.append(node_id)

            for successor_id in graph.get_successors(node_id):
                if successor_id not in visited:
                    cycle = dfs(successor_id, path.copy())
                    if cycle:
                        return cycle
                elif successor_id in rec_stack:
                    # Found cycle
                    cycle_start_idx = path.index(successor_id)
                    return path[cycle_start_idx:] + [successor_id]

            rec_stack.remove(node_id)
            return None

        for node in graph.nodes:
            if node.id not in visited:
                cycle = dfs(node.id, [])
                if cycle:
                    cycle_found = True
                    cycle_str = " -> ".join(cycle)
                    result.add_error(
                        "Graph contains a cycle",
                        details=f"Cycle detected: {cycle_str}",
                    )
                    break  # Report only first cycle

        return cycle_found

    def _validate_reachability(self, graph: NodeGraph, result: GraphValidationResult):
        """Check that all nodes are reachable from Start node."""
        start_nodes = [node for node in graph.nodes if node.type == "Start"]
        if len(start_nodes) != 1:
            # Already reported in _validate_start_node
            return

        start_node = start_nodes[0]

        # BFS to find all reachable nodes
        reachable = set()
        queue = [start_node.id]

        while queue:
            node_id = queue.pop(0)
            if node_id in reachable:
                continue

            reachable.add(node_id)
            queue.extend(graph.get_successors(node_id))

        # Find unreachable nodes
        all_node_ids = set(node.id for node in graph.nodes)
        unreachable = all_node_ids - reachable

        for node_id in unreachable:
            node = graph.get_node(node_id)
            result.add_warning(
                f"Node is unreachable from Start",
                node_id=node_id,
                details=f"Node '{node_id}' ({node.type if node else 'unknown'}) cannot be reached",
            )

    def _validate_connections(self, graph: NodeGraph, result: GraphValidationResult):
        """Validate port type compatibility for all connections."""
        for edge in graph.edges:
            source_node = graph.get_node(edge.source)
            target_node = graph.get_node(edge.target)

            if not source_node or not target_node:
                # Already reported in _validate_edges
                continue

            # Get node definitions
            source_def = get_node_definition(source_node.type)
            target_def = get_node_definition(target_node.type)

            if not source_def or not target_def:
                # Already reported in _validate_nodes
                continue

            # Find output port on source
            source_port = None
            for port in source_def.outputs:
                if port.id == edge.source_port:
                    source_port = port
                    break

            if not source_port:
                result.add_error(
                    f"Source node does not have output port '{edge.source_port}'",
                    edge_id=edge.id,
                    details=f"Node '{source_node.id}' ({source_node.type}) does not define output port '{edge.source_port}'",
                )
                continue

            # Find input port on target
            target_port = None
            for port in target_def.inputs:
                if port.id == edge.target_port:
                    target_port = port
                    break

            if not target_port:
                result.add_error(
                    f"Target node does not have input port '{edge.target_port}'",
                    edge_id=edge.id,
                    details=f"Node '{target_node.id}' ({target_node.type}) does not define input port '{edge.target_port}'",
                )
                continue

            # Check port type compatibility
            if not source_port.is_compatible(target_port):
                result.add_error(
                    "Incompatible port types",
                    edge_id=edge.id,
                    details=f"Cannot connect {source_port.port_type.value} output to {target_port.port_type.value} input",
                )

    def _validate_isolated_nodes(self, graph: NodeGraph, result: GraphValidationResult):
        """Check for nodes with no connections (except Start/End)."""
        for node in graph.nodes:
            # Skip Start and End nodes
            if node.type in ["Start", "End"]:
                continue

            incoming = graph.get_incoming_edges(node.id)
            outgoing = graph.get_outgoing_edges(node.id)

            if len(incoming) == 0 and len(outgoing) == 0:
                result.add_warning(
                    "Node is isolated",
                    node_id=node.id,
                    details=f"Node '{node.id}' ({node.type}) has no connections",
                )


class GraphExecutor:
    """
    Graph execution engine with topological sorting.

    Provides ordered execution of nodes with proper dependency handling.
    """

    def get_execution_order(self, graph: NodeGraph) -> List[Node]:
        """
        Get the execution order for nodes using topological sort.

        Uses Kahn's algorithm for topological sorting.

        Args:
            graph: The graph to sort

        Returns:
            List of nodes in execution order

        Raises:
            ValueError: If graph contains cycles
        """
        # Calculate in-degrees
        in_degree = {node.id: 0 for node in graph.nodes}
        for edge in graph.edges:
            if edge.target in in_degree:
                in_degree[edge.target] += 1

        # Find Start node
        start_nodes = [node for node in graph.nodes if node.type == "Start"]
        if len(start_nodes) != 1:
            raise ValueError("Graph must have exactly one Start node")

        # Queue with nodes that have no dependencies
        queue = [node for node in graph.nodes if in_degree[node.id] == 0]
        result = []

        while queue:
            # Sort by Start node first
            queue.sort(key=lambda n: 0 if n.type == "Start" else 1)
            node = queue.pop(0)
            result.append(node)

            # Reduce in-degree for successors
            for successor_id in graph.get_successors(node.id):
                in_degree[successor_id] -= 1
                if in_degree[successor_id] == 0:
                    successor = graph.get_node(successor_id)
                    if successor:
                        queue.append(successor)

        # Check if all nodes were processed
        if len(result) != len(graph.nodes):
            raise ValueError("Graph contains cycles - cannot determine execution order")

        return result
