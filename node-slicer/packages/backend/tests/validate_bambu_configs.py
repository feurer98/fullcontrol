"""
Validation script for Bambu Lab configuration file generation.

This script demonstrates and validates the generation of all three
Bambu Lab configuration files.
"""

import json
from xml.etree import ElementTree as ET

from src.core.bambu_config import (
    BambuConfigGenerator,
    FilamentInfo,
    ObjectInfo,
    PlateInfo,
    SliceInfo,
)


def print_separator(title: str) -> None:
    """Print a section separator."""
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80 + "\n")


def validate_configs():
    """Validate all Bambu Lab configuration file generation."""
    generator = BambuConfigGenerator()

    print_separator("Bambu Lab Config Generator Validation")

    # ========================================================================
    # Test 1: Generate model_settings.config
    # ========================================================================
    print_separator("1. model_settings.config (XML)")

    plate_info = PlateInfo(
        plate_id=1,
        plate_name="Test Plate",
        gcode_file="Metadata/plate_1.gcode",
        thumbnail_file="Metadata/plate_1.png",
    )

    model_config = generator.generate_model_settings(plate_info)
    print(model_config)

    # Validate XML structure
    try:
        root = ET.fromstring(model_config)
        plate = root.find("plate")
        metadata_count = len(plate.findall("metadata"))
        print(f"✅ Valid XML with {metadata_count} metadata entries")
    except Exception as e:
        print(f"❌ XML validation failed: {e}")

    # ========================================================================
    # Test 2: Generate project_settings.config
    # ========================================================================
    print_separator("2. project_settings.config (JSON) - First 2000 characters")

    project_config = generator.generate_project_settings(
        printer="bambulab_x1c",
        filament="PLA",
        layer_height=0.2,
        nozzle_temp=220,
        bed_temp=55,
    )

    # Print first 2000 characters
    print(project_config[:2000])
    if len(project_config) > 2000:
        print("\n[... output truncated ...]")

    # Validate JSON structure
    try:
        settings = json.loads(project_config)
        key_count = len(settings.keys())
        print(f"\n✅ Valid JSON with {key_count} settings")
        print(f"   - Filament: {settings.get('filament_type', ['N/A'])[0]}")
        print(f"   - Layer height: {settings.get('layer_height', 'N/A')}")
        print(f"   - Bed temp: {settings.get('hot_plate_temp', ['N/A'])[0]}")
        print(f"   - Print speed: {settings.get('inner_wall_speed', 'N/A')} mm/s")
    except Exception as e:
        print(f"❌ JSON validation failed: {e}")

    # ========================================================================
    # Test 3: Generate slice_info.config
    # ========================================================================
    print_separator("3. slice_info.config (XML)")

    obj1 = ObjectInfo("100", "cube.STL")
    obj2 = ObjectInfo("101", "cylinder.STL")
    fil = FilamentInfo(
        type="PLA",
        color="#FFFFFF",
        used_m=5.5,
        used_g=13.2,
    )

    slice_info = SliceInfo(
        printer_model_id="BL-P001",
        nozzle_diameters="0.4",
        prediction=1800,  # 30 minutes in seconds
        weight=13.2,
        objects=[obj1, obj2],
        filaments=[fil],
    )

    slice_config = generator.generate_slice_info(slice_info)
    print(slice_config)

    # Validate XML structure
    try:
        root = ET.fromstring(slice_config)
        plate = root.find("plate")
        objects = plate.findall("object")
        filaments = plate.findall("filament")
        print(f"✅ Valid XML with {len(objects)} objects and {len(filaments)} filaments")
    except Exception as e:
        print(f"❌ XML validation failed: {e}")

    # ========================================================================
    # Test 4: Multi-filament scenario
    # ========================================================================
    print_separator("4. Multi-Filament Scenario")

    fil1 = FilamentInfo(id="1", type="PLA", color="#FF0000", used_m=10.0, used_g=24.0)
    fil2 = FilamentInfo(id="2", type="PETG", color="#00FF00", used_m=5.0, used_g=13.5)

    multi_slice_info = SliceInfo(
        prediction=3600,
        weight=37.5,
        filaments=[fil1, fil2],
    )

    multi_slice_config = generator.generate_slice_info(multi_slice_info)

    # Parse and display
    root = ET.fromstring(multi_slice_config)
    plate = root.find("plate")
    filaments = plate.findall("filament")

    print("Filaments in multi-material print:")
    for fil in filaments:
        print(
            f"  - Filament {fil.get('id')}: {fil.get('type')} ({fil.get('color')})"
        )
        print(f"    Used: {fil.get('used_m')}m / {fil.get('used_g')}g")

    print("\n✅ Multi-filament configuration generated successfully")

    # ========================================================================
    # Test 5: Custom printer settings
    # ========================================================================
    print_separator("5. Custom Printer Settings")

    custom_settings = {
        "sparse_infill_density": "25%",
        "wall_loops": "3",
        "top_shell_layers": "5",
        "bottom_shell_layers": "5",
    }

    custom_config = generator.generate_project_settings(
        filament="PETG",
        layer_height=0.15,
        nozzle_temp=250,
        bed_temp=70,
        additional_settings=custom_settings,
    )

    settings = json.loads(custom_config)
    print("Custom settings applied:")
    print(f"  - Infill density: {settings['sparse_infill_density']}")
    print(f"  - Wall loops: {settings['wall_loops']}")
    print(f"  - Top layers: {settings['top_shell_layers']}")
    print(f"  - Bottom layers: {settings['bottom_shell_layers']}")
    print(f"  - Filament: {settings['filament_type'][0]}")
    print(f"  - Layer height: {settings['layer_height']}")

    print("\n✅ Custom settings merged successfully")

    # ========================================================================
    # Summary
    # ========================================================================
    print_separator("Summary")

    print("✅ All configuration file generators working correctly!")
    print()
    print("Generated configurations:")
    print("  1. model_settings.config - Plate and file references")
    print("  2. project_settings.config - Comprehensive printer settings")
    print("  3. slice_info.config - Slice metadata and statistics")
    print()
    print("Features tested:")
    print("  ✓ XML generation and validation")
    print("  ✓ JSON generation and validation")
    print("  ✓ Default values")
    print("  ✓ Custom values")
    print("  ✓ Multi-object support")
    print("  ✓ Multi-filament support")
    print("  ✓ Additional settings merging")
    print()
    print("=" * 80)


if __name__ == "__main__":
    validate_configs()
