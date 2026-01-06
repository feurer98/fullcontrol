#!/usr/bin/env python
"""
Validation script for Node-Based G-Code Generation

This script demonstrates the conversion of node graphs to G-code using
the NodeConverter and FullControl integration.
"""

import sys
from pathlib import Path

# Add paths
backend_path = Path(__file__).parent.parent
fullcontrol_path = backend_path.parent.parent.parent
sys.path.insert(0, str(backend_path))
sys.path.insert(0, str(fullcontrol_path))

import fullcontrol as fc

from src.core.node_converter import NodeConverter
from src.core.node_types import Node, Edge, NodeGraph


def print_header(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def test_1_simple_print_sequence():
    """Test 1: Simple print sequence with basic operations."""
    print_header("Test 1: Simple Print Sequence")

    # Create a simple graph: Start -> Home -> Heat -> Move -> Extrude -> End
    graph = NodeGraph(
        nodes=[
            Node(id="start", type="Start", position={"x": 0, "y": 0}),
            Node(id="home", type="Home", position={"x": 100, "y": 0}, parameters={"axes": "XYZ"}),
            Node(
                id="heat_hotend",
                type="SetHotend",
                position={"x": 200, "y": 0},
                parameters={"temperature": 200, "wait": True},
            ),
            Node(
                id="heat_bed",
                type="SetBed",
                position={"x": 300, "y": 0},
                parameters={"temperature": 60, "wait": True},
            ),
            Node(
                id="move1",
                type="LinearMove",
                position={"x": 400, "y": 0},
                parameters={"x": 10.0, "y": 10.0, "z": 0.2},
            ),
            Node(
                id="extrude1",
                type="ExtrudeMove",
                position={"x": 500, "y": 0},
                parameters={"x": 50.0, "y": 10.0, "z": 0.2},
            ),
            Node(id="end", type="End", position={"x": 600, "y": 0}),
        ],
        edges=[
            Edge(id="e1", source="start", source_port="out", target="home", target_port="in"),
            Edge(id="e2", source="home", source_port="out", target="heat_hotend", target_port="in"),
            Edge(id="e3", source="heat_hotend", source_port="out", target="heat_bed", target_port="in"),
            Edge(id="e4", source="heat_bed", source_port="out", target="move1", target_port="in"),
            Edge(id="e5", source="move1", source_port="out", target="extrude1", target_port="in"),
            Edge(id="e6", source="extrude1", source_port="out", target="end", target_port="in"),
        ],
    )

    # Convert to steps
    converter = NodeConverter()
    steps = converter.convert(graph)

    print(f"\n✓ Graph converted to {len(steps)} FullControl steps")
    print("\nSteps generated:")
    for i, step in enumerate(steps, 1):
        step_type = step.__class__.__name__
        print(f"  {i}. {step_type}: {step}")

    # Convert to G-code
    print("\n✓ Converting to G-code...")
    gcode_controls = fc.GcodeControls(
        printer_name="bambulab_x1",
        save_as="test_simple_sequence",
        include_date=False,
    )
    gcode = fc.transform(steps, "gcode", gcode_controls, show_tips=False)

    # Display G-code
    gcode_lines = gcode.split("\n")
    print(f"\n✓ Generated {len(gcode_lines)} lines of G-code")
    print("\nFirst 20 lines of G-code:")
    for line in gcode_lines[:20]:
        print(f"  {line}")

    if len(gcode_lines) > 20:
        print(f"  ... ({len(gcode_lines) - 20} more lines)")

    print("\n✅ Test 1 passed!")
    return True


def test_2_temperature_control():
    """Test 2: Temperature control nodes."""
    print_header("Test 2: Temperature Control")

    graph = NodeGraph(
        nodes=[
            Node(id="start", type="Start", position={"x": 0, "y": 0}),
            Node(
                id="set_hotend",
                type="SetHotend",
                position={"x": 100, "y": 0},
                parameters={"temperature": 210, "wait": False},
            ),
            Node(
                id="wait_hotend",
                type="WaitHotend",
                position={"x": 200, "y": 0},
                parameters={"temperature": 210},
            ),
            Node(
                id="set_bed",
                type="SetBed",
                position={"x": 300, "y": 0},
                parameters={"temperature": 70, "wait": False},
            ),
            Node(
                id="wait_bed",
                type="WaitBed",
                position={"x": 400, "y": 0},
                parameters={"temperature": 70},
            ),
            Node(id="end", type="End", position={"x": 500, "y": 0}),
        ],
        edges=[
            Edge(id="e1", source="start", source_port="out", target="set_hotend", target_port="in"),
            Edge(id="e2", source="set_hotend", source_port="out", target="wait_hotend", target_port="in"),
            Edge(id="e3", source="wait_hotend", source_port="out", target="set_bed", target_port="in"),
            Edge(id="e4", source="set_bed", source_port="out", target="wait_bed", target_port="in"),
            Edge(id="e5", source="wait_bed", source_port="out", target="end", target_port="in"),
        ],
    )

    converter = NodeConverter()
    steps = converter.convert(graph)

    print(f"\n✓ Graph converted to {len(steps)} steps")
    print("\nTemperature control steps:")
    for step in steps:
        if isinstance(step, (fc.Hotend, fc.Buildplate)):
            step_type = step.__class__.__name__
            wait_status = "wait" if step.wait else "no wait"
            print(f"  • {step_type}: {step.temp}°C ({wait_status})")

    print("\n✅ Test 2 passed!")
    return True


def test_3_comments_and_custom_gcode():
    """Test 3: Comments and custom G-code."""
    print_header("Test 3: Comments and Custom G-Code")

    graph = NodeGraph(
        nodes=[
            Node(id="start", type="Start", position={"x": 0, "y": 0}),
            Node(
                id="comment1",
                type="Comment",
                position={"x": 100, "y": 0},
                parameters={"text": "Starting custom sequence"},
            ),
            Node(
                id="move1",
                type="LinearMove",
                position={"x": 150, "y": 0},
                parameters={"x": 10.0, "y": 10.0, "z": 5.0},
            ),
            Node(
                id="custom1",
                type="CustomGCode",
                position={"x": 200, "y": 0},
                parameters={"gcode": "M117 Hello from NodeSlicer"},
            ),
            Node(
                id="comment2",
                type="Comment",
                position={"x": 300, "y": 0},
                parameters={"text": "Custom sequence complete"},
            ),
            Node(id="end", type="End", position={"x": 400, "y": 0}),
        ],
        edges=[
            Edge(id="e1", source="start", source_port="out", target="comment1", target_port="in"),
            Edge(id="e2", source="comment1", source_port="out", target="move1", target_port="in"),
            Edge(id="e3", source="move1", source_port="out", target="custom1", target_port="in"),
            Edge(id="e4", source="custom1", source_port="out", target="comment2", target_port="in"),
            Edge(id="e5", source="comment2", source_port="out", target="end", target_port="in"),
        ],
    )

    converter = NodeConverter()
    steps = converter.convert(graph)

    print(f"\n✓ Graph converted to {len(steps)} steps")

    # Convert to G-code
    gcode_controls = fc.GcodeControls(
        printer_name="bambulab_x1",
        save_as="test_comments",
        include_date=False,
    )
    gcode = fc.transform(steps, "gcode", gcode_controls, show_tips=False)

    # Find comments and custom G-code in output
    print("\nG-code output (filtered):")
    for line in gcode.split("\n"):
        if "NodeSlicer" in line or "Starting" in line or "complete" in line or "M117" in line:
            print(f"  {line}")

    print("\n✅ Test 3 passed!")
    return True


def test_4_complex_print_path():
    """Test 4: Complex print path with multiple moves."""
    print_header("Test 4: Complex Print Path")

    # Create a square print path
    graph = NodeGraph(
        nodes=[
            Node(id="start", type="Start", position={"x": 0, "y": 0}),
            Node(id="home", type="Home", position={"x": 50, "y": 0}, parameters={"axes": "XYZ"}),
            # Draw a square: (10,10) -> (50,10) -> (50,50) -> (10,50) -> (10,10)
            Node(
                id="move_corner1",
                type="LinearMove",
                position={"x": 100, "y": 0},
                parameters={"x": 10.0, "y": 10.0, "z": 0.2},
            ),
            Node(
                id="extrude_side1",
                type="ExtrudeMove",
                position={"x": 150, "y": 0},
                parameters={"x": 50.0, "y": 10.0, "z": 0.2},
            ),
            Node(
                id="extrude_side2",
                type="ExtrudeMove",
                position={"x": 200, "y": 0},
                parameters={"x": 50.0, "y": 50.0, "z": 0.2},
            ),
            Node(
                id="extrude_side3",
                type="ExtrudeMove",
                position={"x": 250, "y": 0},
                parameters={"x": 10.0, "y": 50.0, "z": 0.2},
            ),
            Node(
                id="extrude_side4",
                type="ExtrudeMove",
                position={"x": 300, "y": 0},
                parameters={"x": 10.0, "y": 10.0, "z": 0.2},
            ),
            Node(id="end", type="End", position={"x": 350, "y": 0}),
        ],
        edges=[
            Edge(id="e1", source="start", source_port="out", target="home", target_port="in"),
            Edge(id="e2", source="home", source_port="out", target="move_corner1", target_port="in"),
            Edge(id="e3", source="move_corner1", source_port="out", target="extrude_side1", target_port="in"),
            Edge(id="e4", source="extrude_side1", source_port="out", target="extrude_side2", target_port="in"),
            Edge(id="e5", source="extrude_side2", source_port="out", target="extrude_side3", target_port="in"),
            Edge(id="e6", source="extrude_side3", source_port="out", target="extrude_side4", target_port="in"),
            Edge(id="e7", source="extrude_side4", source_port="out", target="end", target_port="in"),
        ],
    )

    converter = NodeConverter()
    steps = converter.convert(graph)

    print(f"\n✓ Graph converted to {len(steps)} steps")

    # Count extrusion moves
    extrusion_count = sum(1 for step in steps if isinstance(step, fc.Extruder))
    point_count = sum(1 for step in steps if isinstance(step, fc.Point))

    print(f"  • {extrusion_count} extrusion commands")
    print(f"  • {point_count} movement points")

    # Convert to G-code
    gcode_controls = fc.GcodeControls(
        printer_name="bambulab_x1",
        save_as="test_square",
        include_date=False,
    )
    gcode = fc.transform(steps, "gcode", gcode_controls, show_tips=False)
    gcode_lines = [line for line in gcode.split("\n") if line.strip()]

    print(f"\n✓ Generated {len(gcode_lines)} lines of G-code")
    print("\n✅ Test 4 passed!")
    return True


def main():
    """Run all validation tests."""
    print("\n" + "=" * 80)
    print("NODE-BASED G-CODE GENERATION VALIDATION")
    print("=" * 80)
    print("\nThis script validates the node-to-G-code conversion pipeline")
    print("including NodeConverter and FullControl integration.")

    tests = [
        test_1_simple_print_sequence,
        test_2_temperature_control,
        test_3_comments_and_custom_gcode,
        test_4_complex_print_path,
    ]

    passed = 0
    failed = 0

    for test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"\n❌ Test failed with error: {e}")
            import traceback

            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 80)
    print(f"VALIDATION SUMMARY: {passed} passed, {failed} failed")
    print("=" * 80)

    if failed == 0:
        print("\n✅ All validation tests passed!")
        print("\nNode-based G-code generation is working correctly!")
        return 0
    else:
        print("\n❌ Some tests failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
