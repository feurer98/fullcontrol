#!/usr/bin/env python3
"""
Validation script for Bambu Lab G-Code Generator

This script validates the BambuGCodeGenerator by creating various
test scenarios and verifying the output.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.bambu_gcode import (
    BambuGCodeGenerator,
    BambuMetadata,
    BambuPrinterSettings,
    calculate_filament_stats,
)


def print_section(title: str):
    """Print a section header."""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}\n")


def validate_scenario_1():
    """Scenario 1: Basic single-material print."""
    print_section("Scenario 1: Basic Single-Material Print")

    metadata = BambuMetadata(
        layer_count=50,
        print_time_seconds=1800,  # 30 minutes
        filament_type="PLA",
        generator_version="0.1.0",
    )

    settings = BambuPrinterSettings(
        bed_temp=60.0,
        hotend_temp=210.0,
    )

    gen = BambuGCodeGenerator(metadata=metadata, settings=settings)

    # Generate simple print body
    body_lines = []
    for layer in range(5):
        z_height = layer * 0.2
        body_lines.append(gen.generate_layer_change(layer, z_height))
        body_lines.append(f"G1 X10 Y10 Z{z_height:.2f} E1.0")
        body_lines.append(f"G1 X20 Y10 Z{z_height:.2f} E2.0")
        body_lines.append(gen.generate_progress_update(layer * 20, layer))

    body = "\n".join(body_lines)
    complete_gcode = gen.generate_complete_gcode(body)

    # Validate structure
    checks = [
        ("; HEADER_BLOCK_START" in complete_gcode, "Header block present"),
        ("; NodeSlicer 0.1.0" in complete_gcode, "Generator version in header"),
        ("; total layer number: 50" in complete_gcode, "Layer count in header"),
        ("; filament_type: PLA" in complete_gcode, "Filament type in header"),
        ("; CONFIG_BLOCK_START" in complete_gcode, "Config block present"),
        ("; STARTING_PROCEDURE_START" in complete_gcode, "Starting procedure present"),
        ("M140 S60" in complete_gcode, "Bed temperature set"),
        ("M109 S210" in complete_gcode, "Hotend temperature wait"),
        ("G28" in complete_gcode, "Homing command"),
        ("; EXECUTABLE_BLOCK_START" in complete_gcode, "Executable block start"),
        ("; LAYER_CHANGE" in complete_gcode, "Layer changes present"),
        ("M73" in complete_gcode, "Progress updates present"),
        ("; EXECUTABLE_BLOCK_END" in complete_gcode, "Executable block end"),
        ("; ENDING_PROCEDURE_START" in complete_gcode, "Ending procedure present"),
        ("M84" in complete_gcode, "Motors disabled at end"),
    ]

    all_passed = True
    for check, description in checks:
        status = "✓" if check else "✗"
        print(f"{status} {description}")
        if not check:
            all_passed = False

    print(f"\nGenerated G-Code length: {len(complete_gcode)} bytes")
    print(f"Generated G-Code lines: {len(complete_gcode.splitlines())} lines")

    return all_passed


def validate_scenario_2():
    """Scenario 2: Multi-material print with AMS."""
    print_section("Scenario 2: Multi-Material Print (AMS)")

    metadata = BambuMetadata(
        layer_count=30,
        print_time_seconds=3600,  # 1 hour
        filament_type="PLA",
    )

    gen = BambuGCodeGenerator(metadata=metadata)

    # Generate multi-material body
    body_lines = [
        "; Base layer - Tool 0 (White PLA)",
        gen.generate_tool_change(0, "White PLA"),
        "G1 X10 Y10 Z0.2 E5.0",
        "G1 X50 Y10 Z0.2 E15.0",
        "",
        "; Detail layer - Tool 1 (Red PLA)",
        gen.generate_filament_change(1, purge_length=60.0),
        "G1 X15 Y15 Z0.4 E3.0",
        "G1 X45 Y15 Z0.4 E8.0",
        "",
        "; Support layer - Tool 2 (Support material)",
        gen.generate_filament_change(2, purge_length=70.0),
        "G1 X20 Y20 Z0.6 E4.0",
        "",
        "; Back to base - Tool 0",
        gen.generate_filament_change(0, purge_length=60.0),
        "G1 X30 Y30 Z0.8 E10.0",
    ]

    body = "\n".join(body_lines)
    complete_gcode = gen.generate_complete_gcode(body)

    # Validate AMS features
    checks = [
        ("T0 ; White PLA" in complete_gcode, "Tool 0 change with comment"),
        ("T1" in complete_gcode, "Tool 1 change"),
        ("T2" in complete_gcode, "Tool 2 change"),
        ("; AMS Filament Change" in complete_gcode, "AMS filament change sequence"),
        ("G1 E60.0 F300" in complete_gcode, "Purge command"),
        ("G4 P500" in complete_gcode, "Dwell after purge"),
        (complete_gcode.count("G92 E0") >= 6, "Multiple extruder resets"),
    ]

    all_passed = True
    for check, description in checks:
        status = "✓" if check else "✗"
        print(f"{status} {description}")
        if not check:
            all_passed = False

    # Count tool changes
    tool_changes = sum(1 for line in complete_gcode.split('\n') if line.strip().startswith('T'))
    print(f"\nTotal tool changes: {tool_changes}")

    return all_passed


def validate_scenario_3():
    """Scenario 3: Progress reporting throughout print."""
    print_section("Scenario 3: Progress Reporting")

    metadata = BambuMetadata(
        layer_count=100,
        print_time_seconds=7200,  # 2 hours
    )

    gen = BambuGCodeGenerator(metadata=metadata)

    # Generate body with progress updates
    body_lines = []
    for layer in range(0, 101, 10):  # Every 10 layers
        z_height = layer * 0.2
        progress = layer  # 0-100%
        body_lines.append(gen.generate_layer_change(layer, z_height))
        body_lines.append(f"G1 X{layer} Y{layer} Z{z_height:.2f} E1.0")
        body_lines.append(gen.generate_progress_update(progress, layer))

    body = "\n".join(body_lines)
    complete_gcode = gen.generate_complete_gcode(body, include_progress=True)

    # Count progress updates
    progress_updates = [line for line in complete_gcode.split('\n') if 'M73 P' in line]

    checks = [
        (len(progress_updates) >= 11, "Multiple progress updates (11+)"),
        ("M73 P0" in complete_gcode, "0% progress update"),
        ("M73 P50" in complete_gcode, "50% progress update"),
        ("M73 P100" in complete_gcode, "100% progress update"),
        (any("L" in update for update in progress_updates), "Layer number in progress"),
    ]

    all_passed = True
    for check, description in checks:
        status = "✓" if check else "✗"
        print(f"{status} {description}")
        if not check:
            all_passed = False

    print(f"\nTotal progress updates: {len(progress_updates)}")
    print(f"First update: {progress_updates[0].strip()}")
    print(f"Last update: {progress_updates[-1].strip()}")

    return all_passed


def validate_scenario_4():
    """Scenario 4: Custom temperature profiles."""
    print_section("Scenario 4: Custom Temperature Profiles")

    # High-temp materials (PETG)
    settings_petg = BambuPrinterSettings(
        bed_temp=80.0,
        hotend_temp=240.0,
        print_speed=80,
    )

    gen = BambuGCodeGenerator(settings=settings_petg)

    # Test temperature wait commands
    temp_wait = gen.generate_wait_for_temperature(hotend=260.0, bed=85.0)

    checks = [
        ("M190 S85" in temp_wait, "Bed temperature wait (85°C)"),
        ("M109 S260" in temp_wait, "Hotend temperature wait (260°C)"),
    ]

    # Generate starting procedure
    start = gen.generate_starting_procedure()

    checks.extend([
        ("M140 S80" in start, "PETG bed temp in start procedure (80°C)"),
        ("M109 S240" in start, "PETG hotend temp in start procedure (240°C)"),
        ("M220 S80" in start, "Custom speed factor (80%)"),
    ])

    all_passed = True
    for check, description in checks:
        status = "✓" if check else "✗"
        print(f"{status} {description}")
        if not check:
            all_passed = False

    return all_passed


def validate_scenario_5():
    """Scenario 5: Filament statistics calculation."""
    print_section("Scenario 5: Filament Statistics")

    # Create realistic G-Code with extrusion
    test_gcode = """
    G92 E0
    G1 X0 Y0 Z0.2 E0
    G1 X100 Y0 Z0.2 E10.5
    G1 X100 Y100 Z0.2 E21.0
    G1 X0 Y100 Z0.2 E31.5
    G1 X0 Y0 Z0.2 E42.0
    G1 E-0.8 F3000 ; retract
    G0 Z10
    G1 E0.8 ; unretract
    G1 X50 Y50 Z0.4 E45.0
    """

    # Calculate stats with PLA
    stats_pla = calculate_filament_stats(test_gcode, filament_diameter=1.75, filament_density=1.24)

    # Calculate stats with ABS
    stats_abs = calculate_filament_stats(test_gcode, filament_diameter=1.75, filament_density=1.04)

    checks = [
        (stats_pla["length_mm"] > 0, "Filament length calculated"),
        (stats_pla["volume_cm3"] > 0, "Filament volume calculated"),
        (stats_pla["weight_g"] > 0, "Filament weight calculated"),
        (stats_pla["weight_g"] > stats_abs["weight_g"], "PLA heavier than ABS (same volume)"),
    ]

    all_passed = True
    for check, description in checks:
        status = "✓" if check else "✗"
        print(f"{status} {description}")
        if not check:
            all_passed = False

    print(f"\nPLA Statistics:")
    print(f"  Length: {stats_pla['length_mm']:.2f} mm")
    print(f"  Volume: {stats_pla['volume_cm3']:.2f} cm³")
    print(f"  Weight: {stats_pla['weight_g']:.2f} g")

    print(f"\nABS Statistics:")
    print(f"  Length: {stats_abs['length_mm']:.2f} mm")
    print(f"  Volume: {stats_abs['volume_cm3']:.2f} cm³")
    print(f"  Weight: {stats_abs['weight_g']:.2f} g")

    return all_passed


def main():
    """Run all validation scenarios."""
    print("\n" + "=" * 60)
    print("  Bambu Lab G-Code Generator Validation")
    print("=" * 60)

    scenarios = [
        ("Scenario 1: Basic Print", validate_scenario_1),
        ("Scenario 2: AMS Multi-Material", validate_scenario_2),
        ("Scenario 3: Progress Reporting", validate_scenario_3),
        ("Scenario 4: Temperature Profiles", validate_scenario_4),
        ("Scenario 5: Filament Statistics", validate_scenario_5),
    ]

    results = []
    for name, scenario_func in scenarios:
        try:
            passed = scenario_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\n✗ {name} FAILED with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))

    # Summary
    print_section("Validation Summary")

    total = len(results)
    passed = sum(1 for _, result in results if result)
    failed = total - passed

    for name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{status}: {name}")

    print(f"\nTotal: {total} scenarios")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    if failed == 0:
        print("\n🎉 All validation scenarios passed!")
        return 0
    else:
        print(f"\n❌ {failed} scenario(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
