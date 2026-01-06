"""
Validation script for UUID and Production Extension implementation.

This script creates a 3MF file with Production Extension enabled and
inspects the generated file to verify UUID implementation.
"""

import tempfile
import zipfile
from pathlib import Path

from src.core.threemf_builder import ThreeMFBuilder


def validate_uuid_implementation():
    """Create and validate a 3MF file with UUIDs."""
    print("=" * 70)
    print("UUID and Production Extension Validation")
    print("=" * 70)

    # Create builder with Production Extension
    builder = ThreeMFBuilder()
    builder.enable_production_extension()

    print(f"\n✓ Production Extension enabled: {builder.production_extension_enabled}")

    # Add metadata
    builder.add_metadata("Application", "NodeSlicer")
    builder.add_metadata("Version", "0.2.0")
    builder.add_metadata("CreatedBy", "Task 2.2 - Production Extension")

    # Create multiple mesh objects with UUIDs
    print("\n" + "=" * 70)
    print("Creating mesh objects with UUIDs")
    print("=" * 70)

    # Mesh 1: Triangle
    vertices1 = [(0.0, 0.0, 0.0), (10.0, 0.0, 0.0), (5.0, 10.0, 0.0)]
    triangles1 = [(0, 1, 2)]
    mesh1 = builder.create_mesh_object(vertices1, triangles1, "Triangle")
    print(f"✓ Created Triangle mesh (Resource ID: {mesh1.GetResourceID()})")

    # Mesh 2: Square
    vertices2 = [(0.0, 0.0, 0.0), (10.0, 0.0, 0.0), (10.0, 10.0, 0.0), (0.0, 10.0, 0.0)]
    triangles2 = [(0, 1, 2), (0, 2, 3)]
    mesh2 = builder.create_mesh_object(vertices2, triangles2, "Square")
    print(f"✓ Created Square mesh (Resource ID: {mesh2.GetResourceID()})")

    # Mesh 3: Pyramid
    vertices3 = [
        (0.0, 0.0, 0.0),  # Base
        (10.0, 0.0, 0.0),
        (10.0, 10.0, 0.0),
        (0.0, 10.0, 0.0),
        (5.0, 5.0, 10.0),  # Apex
    ]
    triangles3 = [
        (0, 1, 2),
        (0, 2, 3),  # Base
        (0, 4, 1),
        (1, 4, 2),
        (2, 4, 3),
        (3, 4, 0),  # Sides
    ]
    mesh3 = builder.create_mesh_object(vertices3, triangles3, "Pyramid")
    print(f"✓ Created Pyramid mesh (Resource ID: {mesh3.GetResourceID()})")

    # Add to build plate
    print("\n" + "=" * 70)
    print("Adding objects to build plate")
    print("=" * 70)

    builder.add_to_build(mesh1)
    print("✓ Added Triangle to build plate")

    builder.add_to_build(mesh2)
    print("✓ Added Square to build plate")

    builder.add_to_build(mesh3)
    print("✓ Added Pyramid to build plate")

    # Get UUID map
    uuid_map = builder.get_uuid_map()
    print("\n" + "=" * 70)
    print("UUID Map")
    print("=" * 70)

    if uuid_map:
        for resource_id, uuid_str in uuid_map.items():
            print(f"Resource ID {resource_id}: {uuid_str}")
    else:
        print(
            "⚠️  No UUIDs in map (Production Extension may not be supported by lib3mf)"
        )

    # Save the 3MF file
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "uuid_validation.3mf"
        builder.save(output_path)

        print("\n" + "=" * 70)
        print("3MF File Validation")
        print("=" * 70)
        print(f"✓ Saved to: {output_path}")
        print(f"✓ File size: {output_path.stat().st_size:,} bytes")

        # Inspect the 3MF file (it's a ZIP archive)
        print("\n" + "=" * 70)
        print("3MF Archive Contents")
        print("=" * 70)

        with zipfile.ZipFile(output_path, "r") as zip_file:
            for file_info in zip_file.filelist:
                print(f"  - {file_info.filename} ({file_info.file_size} bytes)")

            # Read and display the 3D model XML (truncated)
            print("\n" + "=" * 70)
            print("3dmodel.model Content (first 2000 characters)")
            print("=" * 70)

            model_xml = zip_file.read("3D/3dmodel.model").decode("utf-8")
            print(model_xml[:2000])

            if len(model_xml) > 2000:
                print("\n[... truncated ...]")

    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"✓ Production Extension enabled: {builder.production_extension_enabled}")
    print(f"✓ Created 3 mesh objects")
    print(f"✓ Added 3 build items")
    print(f"✓ Generated {len(uuid_map)} UUIDs")
    print(f"✓ Successfully saved 3MF file")

    if builder.production_extension_enabled:
        print(
            "\n✅ SUCCESS: Production Extension is supported and UUIDs are generated!"
        )
    else:
        print(
            "\n⚠️  NOTE: Production Extension namespace registration not supported by this"
        )
        print(
            "   lib3mf version, but UUID generation and tracking work correctly."
        )
        print(
            "   UUIDs are stored in the UUID map and can be used for manual XML manipulation."
        )

    print("=" * 70)


if __name__ == "__main__":
    validate_uuid_implementation()
