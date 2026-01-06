#!/usr/bin/env python
"""
Validation script for Thumbnail Generation

This script demonstrates and validates the thumbnail generation functionality
for 3MF files, including:
1. Generating placeholders (gradient and solid)
2. Generating thumbnails from geometry (triangles)
3. Embedding thumbnails in 3MF files
4. Creating complete 3MF files with mesh, G-code, and thumbnails
"""

import io
import sys
import zipfile
from pathlib import Path

from PIL import Image

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.threemf_builder import ThreeMFBuilder
from src.core.thumbnail_generator import ThumbnailGenerator, Point3D, Triangle


def validate_png_data(png_data: bytes, expected_size: tuple) -> bool:
    """Validate that PNG data is valid and has expected size."""
    # Check PNG signature
    if png_data[:8] != b"\x89PNG\r\n\x1a\n":
        return False

    # Load and verify
    try:
        img = Image.open(io.BytesIO(png_data))
        return img.format == "PNG" and img.size == expected_size
    except Exception:
        return False


def test_1_placeholder_generation():
    """Test 1: Generate placeholder thumbnails."""
    print("\n" + "=" * 80)
    print("Test 1: Placeholder Thumbnail Generation")
    print("=" * 80)

    generator = ThumbnailGenerator()

    # Generate different placeholder types
    print("\n1.1 Generating solid placeholder...")
    solid_placeholder = generator.generate_placeholder()
    assert validate_png_data(solid_placeholder, ThumbnailGenerator.STANDARD_SIZE)
    print(f"✅ Solid placeholder: {len(solid_placeholder)} bytes, " f"256x256 pixels")

    print("\n1.2 Generating gradient placeholder...")
    gradient_placeholder = generator.generate_gradient_placeholder()
    assert validate_png_data(gradient_placeholder, ThumbnailGenerator.STANDARD_SIZE)
    print(f"✅ Gradient placeholder: {len(gradient_placeholder)} bytes, " f"256x256 pixels")

    print("\n1.3 Generating placeholder with text...")
    text_placeholder = generator.generate_placeholder(text="Test Model")
    assert validate_png_data(text_placeholder, ThumbnailGenerator.STANDARD_SIZE)
    print(f"✅ Text placeholder: {len(text_placeholder)} bytes, " f"256x256 pixels")

    print("\n1.4 Generating small placeholder...")
    small_placeholder = generator.generate_placeholder(size=(64, 64))
    assert validate_png_data(small_placeholder, (64, 64))
    print(f"✅ Small placeholder: {len(small_placeholder)} bytes, 64x64 pixels")

    print("\n✅ All placeholder generation tests passed!")


def test_2_geometry_thumbnails():
    """Test 2: Generate thumbnails from geometry."""
    print("\n" + "=" * 80)
    print("Test 2: Thumbnail Generation from Geometry")
    print("=" * 80)

    generator = ThumbnailGenerator()

    # Create a simple pyramid (4 faces, 4 triangles)
    print("\n2.1 Creating pyramid geometry...")
    pyramid_triangles = [
        # Base
        Triangle(Point3D(0, 0, 0), Point3D(10, 0, 0), Point3D(10, 10, 0)),
        Triangle(Point3D(0, 0, 0), Point3D(10, 10, 0), Point3D(0, 10, 0)),
        # Sides
        Triangle(Point3D(0, 0, 0), Point3D(10, 0, 0), Point3D(5, 5, 10)),
        Triangle(Point3D(10, 0, 0), Point3D(10, 10, 0), Point3D(5, 5, 10)),
        Triangle(Point3D(10, 10, 0), Point3D(0, 10, 0), Point3D(5, 5, 10)),
        Triangle(Point3D(0, 10, 0), Point3D(0, 0, 0), Point3D(5, 5, 10)),
    ]
    print(f"   Created pyramid with {len(pyramid_triangles)} triangles")

    print("\n2.2 Generating top-view thumbnail...")
    top_view = generator.generate_from_triangles(pyramid_triangles, projection="top")
    assert validate_png_data(top_view, ThumbnailGenerator.STANDARD_SIZE)
    print(f"✅ Top view: {len(top_view)} bytes")

    print("\n2.3 Generating front-view thumbnail...")
    front_view = generator.generate_from_triangles(pyramid_triangles, projection="front")
    assert validate_png_data(front_view, ThumbnailGenerator.STANDARD_SIZE)
    print(f"✅ Front view: {len(front_view)} bytes")

    print("\n2.4 Generating side-view thumbnail...")
    side_view = generator.generate_from_triangles(pyramid_triangles, projection="side")
    assert validate_png_data(side_view, ThumbnailGenerator.STANDARD_SIZE)
    print(f"✅ Side view: {len(side_view)} bytes")

    print("\n✅ All geometry thumbnail tests passed!")


def test_3_standard_thumbnail_set():
    """Test 3: Generate standard thumbnail set."""
    print("\n" + "=" * 80)
    print("Test 3: Standard Thumbnail Set Generation")
    print("=" * 80)

    # Create a cube geometry
    print("\n3.1 Creating cube geometry...")
    cube_triangles = []

    # Front face
    cube_triangles.append(Triangle(Point3D(0, 0, 0), Point3D(10, 0, 0), Point3D(10, 10, 0)))
    cube_triangles.append(Triangle(Point3D(0, 0, 0), Point3D(10, 10, 0), Point3D(0, 10, 0)))

    # Back face
    cube_triangles.append(
        Triangle(Point3D(0, 0, 10), Point3D(10, 10, 10), Point3D(10, 0, 10))
    )
    cube_triangles.append(
        Triangle(Point3D(0, 0, 10), Point3D(0, 10, 10), Point3D(10, 10, 10))
    )

    # Top face
    cube_triangles.append(
        Triangle(Point3D(0, 10, 0), Point3D(10, 10, 0), Point3D(10, 10, 10))
    )
    cube_triangles.append(
        Triangle(Point3D(0, 10, 0), Point3D(10, 10, 10), Point3D(0, 10, 10))
    )

    # Bottom face
    cube_triangles.append(Triangle(Point3D(0, 0, 0), Point3D(10, 0, 10), Point3D(10, 0, 0)))
    cube_triangles.append(Triangle(Point3D(0, 0, 0), Point3D(0, 0, 10), Point3D(10, 0, 10)))

    # Left face
    cube_triangles.append(Triangle(Point3D(0, 0, 0), Point3D(0, 10, 0), Point3D(0, 10, 10)))
    cube_triangles.append(Triangle(Point3D(0, 0, 0), Point3D(0, 10, 10), Point3D(0, 0, 10)))

    # Right face
    cube_triangles.append(
        Triangle(Point3D(10, 0, 0), Point3D(10, 10, 10), Point3D(10, 10, 0))
    )
    cube_triangles.append(
        Triangle(Point3D(10, 0, 0), Point3D(10, 0, 10), Point3D(10, 10, 10))
    )

    print(f"   Created cube with {len(cube_triangles)} triangles")

    print("\n3.2 Generating standard set (with geometry)...")
    thumbnail_set = ThumbnailGenerator.create_standard_set(cube_triangles)

    assert "plate" in thumbnail_set
    assert "plate_small" in thumbnail_set
    assert "pick" in thumbnail_set

    assert validate_png_data(thumbnail_set["plate"], ThumbnailGenerator.STANDARD_SIZE)
    assert validate_png_data(thumbnail_set["plate_small"], ThumbnailGenerator.SMALL_SIZE)
    assert validate_png_data(thumbnail_set["pick"], ThumbnailGenerator.PICK_SIZE)

    print(f"   ✓ plate: {len(thumbnail_set['plate'])} bytes (256x256)")
    print(f"   ✓ plate_small: {len(thumbnail_set['plate_small'])} bytes (64x64)")
    print(f"   ✓ pick: {len(thumbnail_set['pick'])} bytes (128x128)")

    print("\n3.3 Generating standard set (placeholders only)...")
    placeholder_set = ThumbnailGenerator.create_standard_set()

    assert len(placeholder_set) == 3
    assert all(validate_png_data(data, size) for data, size in [
        (placeholder_set["plate"], ThumbnailGenerator.STANDARD_SIZE),
        (placeholder_set["plate_small"], ThumbnailGenerator.SMALL_SIZE),
        (placeholder_set["pick"], ThumbnailGenerator.PICK_SIZE),
    ])
    print(f"   ✓ Generated 3 placeholder thumbnails")

    print("\n✅ All standard set tests passed!")


def test_4_embed_in_3mf():
    """Test 4: Embed thumbnails in 3MF file."""
    print("\n" + "=" * 80)
    print("Test 4: Embedding Thumbnails in 3MF Files")
    print("=" * 80)

    builder = ThreeMFBuilder()

    # Create simple geometry
    print("\n4.1 Creating mesh object...")
    vertices = [(0, 0, 0), (10, 0, 0), (5, 10, 0)]
    triangles = [(0, 1, 2)]
    obj_id = builder.create_mesh_object(vertices, triangles)
    builder.add_to_build(obj_id)
    print("   ✓ Mesh created")

    # Generate thumbnail
    print("\n4.2 Generating and embedding thumbnail...")
    generator = ThumbnailGenerator()
    png_data = generator.generate_gradient_placeholder()

    path = builder.embed_thumbnail(png_data, plate=1, thumbnail_type="plate")
    print(f"   ✓ Embedded at: {path}")

    # Save and verify
    print("\n4.3 Saving 3MF and verifying structure...")
    output_path = Path("test_output_thumbnails.3mf")
    builder.save(output_path)

    # Inspect ZIP
    with zipfile.ZipFile(output_path, "r") as z:
        namelist = z.namelist()
        print(f"   ✓ 3MF file created: {output_path.stat().st_size} bytes")
        print(f"   ✓ Files in archive: {len(namelist)}")

        if "Metadata/plate_1.png" in namelist:
            thumb_data = z.read("Metadata/plate_1.png")
            print(f"   ✓ Thumbnail found: {len(thumb_data)} bytes")
            assert thumb_data[:8] == b"\x89PNG\r\n\x1a\n"
            print("   ✓ Valid PNG signature")
        else:
            raise AssertionError("Thumbnail not found in 3MF archive!")

    # Cleanup
    output_path.unlink()
    print("   ✓ Cleanup complete")

    print("\n✅ Embedding test passed!")


def test_5_complete_workflow():
    """Test 5: Complete workflow with mesh, G-code, and thumbnails."""
    print("\n" + "=" * 80)
    print("Test 5: Complete 3MF Workflow (Mesh + G-Code + Thumbnails)")
    print("=" * 80)

    builder = ThreeMFBuilder()

    # Add metadata
    print("\n5.1 Adding metadata...")
    builder.add_metadata("Title", "Validation Test Model")
    builder.add_metadata("Designer", "ThumbnailGenerator")
    print("   ✓ Metadata added")

    # Create pyramid geometry
    print("\n5.2 Creating pyramid mesh...")
    vertices = [
        (0, 0, 0),  # Base corners
        (10, 0, 0),
        (10, 10, 0),
        (0, 10, 0),
        (5, 5, 10),  # Apex
    ]
    triangles = [
        (0, 1, 2),  # Base (split into 2 triangles)
        (0, 2, 3),
        (0, 1, 4),  # Sides
        (1, 2, 4),
        (2, 3, 4),
        (3, 0, 4),
    ]
    obj_id = builder.create_mesh_object(vertices, triangles)
    builder.add_to_build(obj_id)
    print(f"   ✓ Mesh created with {len(vertices)} vertices, {len(triangles)} faces")

    # Embed G-code
    print("\n5.3 Embedding G-code...")
    gcode = """; Test G-code
G28 ; Home all axes
M104 S200 ; Set hotend temperature
M140 S60 ; Set bed temperature
G1 Z10 F3000 ; Lift nozzle
G1 X50 Y50 F3000 ; Move to center
; Print sequence would follow here
"""
    builder.embed_gcode(gcode, plate=1)
    print(f"   ✓ G-code embedded ({len(gcode)} bytes)")

    # Generate and embed thumbnails using the generator
    print("\n5.4 Generating and embedding all standard thumbnails...")

    # Create triangle representation of our pyramid
    pyramid_tris = [
        Triangle(Point3D(0, 0, 0), Point3D(10, 0, 0), Point3D(10, 10, 0)),
        Triangle(Point3D(0, 0, 0), Point3D(10, 10, 0), Point3D(0, 10, 0)),
        Triangle(Point3D(0, 0, 0), Point3D(10, 0, 0), Point3D(5, 5, 10)),
        Triangle(Point3D(10, 0, 0), Point3D(10, 10, 0), Point3D(5, 5, 10)),
        Triangle(Point3D(10, 10, 0), Point3D(0, 10, 0), Point3D(5, 5, 10)),
        Triangle(Point3D(0, 10, 0), Point3D(0, 0, 0), Point3D(5, 5, 10)),
    ]

    paths = builder.embed_thumbnails_from_generator(triangles=pyramid_tris, plate=1)
    for thumb_type, path in paths.items():
        print(f"   ✓ {thumb_type}: {path}")

    # Save
    print("\n5.5 Saving complete 3MF file...")
    output_path = Path("test_complete_workflow.3mf")
    builder.save(output_path)

    # Verify structure
    print("\n5.6 Verifying 3MF structure...")
    with zipfile.ZipFile(output_path, "r") as z:
        namelist = z.namelist()

        # Check for required files
        required_files = [
            "3D/3dmodel.model",
            "Metadata/plate_1.gcode",
            "Metadata/plate_1.png",
            "Metadata/plate_1_small.png",
            "Metadata/pick_1.png",
        ]

        for required_file in required_files:
            if required_file in namelist:
                file_data = z.read(required_file)
                print(f"   ✓ {required_file}: {len(file_data)} bytes")
            else:
                raise AssertionError(f"Missing required file: {required_file}")

        # Verify PNG files
        for png_file in ["Metadata/plate_1.png", "Metadata/plate_1_small.png", "Metadata/pick_1.png"]:
            png_data = z.read(png_file)
            assert png_data[:8] == b"\x89PNG\r\n\x1a\n", f"Invalid PNG: {png_file}"

    file_size_kb = output_path.stat().st_size / 1024
    print(f"\n   ✓ Complete 3MF file: {file_size_kb:.2f} KB")
    print(f"   ✓ Contains {len(namelist)} files")

    # Cleanup
    output_path.unlink()
    print("   ✓ Cleanup complete")

    print("\n✅ Complete workflow test passed!")


def main():
    """Run all validation tests."""
    print("\n" + "=" * 80)
    print("THUMBNAIL GENERATION VALIDATION")
    print("=" * 80)
    print("\nThis script validates the thumbnail generation and embedding functionality")
    print("for 3MF files compatible with Bambu Studio and other slicers.")

    try:
        test_1_placeholder_generation()
        test_2_geometry_thumbnails()
        test_3_standard_thumbnail_set()
        test_4_embed_in_3mf()
        test_5_complete_workflow()

        print("\n" + "=" * 80)
        print("✅ ALL VALIDATION TESTS PASSED!")
        print("=" * 80)
        print("\nSummary:")
        print("  • Placeholder generation: ✅")
        print("  • Geometry-based thumbnails: ✅")
        print("  • Standard thumbnail sets: ✅")
        print("  • 3MF embedding: ✅")
        print("  • Complete workflow: ✅")
        print("\nThumbnail generation is working correctly!")
        print("=" * 80 + "\n")

        return 0

    except AssertionError as e:
        print(f"\n❌ Validation failed: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
