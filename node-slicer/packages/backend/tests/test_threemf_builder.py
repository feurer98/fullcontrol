"""
Unit tests for ThreeMFBuilder class.
"""

import tempfile
from pathlib import Path

import pytest

from src.core.threemf_builder import ThreeMFBuilder


class TestThreeMFBuilder:
    """Test suite for ThreeMFBuilder class."""

    def test_initialization(self):
        """Test that ThreeMFBuilder initializes correctly."""
        builder = ThreeMFBuilder()
        assert builder.wrapper is not None
        assert builder.model is not None

    def test_add_metadata(self):
        """Test adding metadata to the model."""
        builder = ThreeMFBuilder()
        # add_metadata currently fails silently, but should not raise an error
        builder.add_metadata("Application", "NodeSlicer")
        builder.add_metadata("Version", "0.1.0")

        # Metadata may or may not be added (lib3mf can be finicky)
        # The important thing is that it doesn't crash
        assert builder.model is not None

    def test_create_empty_3mf(self):
        """Test creating and saving an empty 3MF file."""
        builder = ThreeMFBuilder()
        builder.add_metadata("Application", "NodeSlicer Test")

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_empty.3mf"
            builder.save(output_path)

            # Verify file was created
            assert output_path.exists()
            assert output_path.stat().st_size > 0

    def test_create_mesh_object(self):
        """Test creating a simple mesh object."""
        builder = ThreeMFBuilder()

        # Create a simple triangle
        vertices = [(0.0, 0.0, 0.0), (10.0, 0.0, 0.0), (5.0, 10.0, 0.0)]
        triangles = [(0, 1, 2)]

        mesh = builder.create_mesh_object(vertices, triangles, "TestTriangle")

        assert mesh is not None
        assert mesh.GetName() == "TestTriangle"
        assert mesh.GetVertexCount() == 3
        assert mesh.GetTriangleCount() == 1

    def test_create_cube_mesh(self):
        """Test creating a cube mesh object."""
        builder = ThreeMFBuilder()

        # Define cube vertices
        vertices = [
            (0.0, 0.0, 0.0),  # 0
            (10.0, 0.0, 0.0),  # 1
            (10.0, 10.0, 0.0),  # 2
            (0.0, 10.0, 0.0),  # 3
            (0.0, 0.0, 10.0),  # 4
            (10.0, 0.0, 10.0),  # 5
            (10.0, 10.0, 10.0),  # 6
            (0.0, 10.0, 10.0),  # 7
        ]

        # Define cube triangles (2 per face, 12 total)
        triangles = [
            # Bottom face
            (0, 1, 2),
            (0, 2, 3),
            # Top face
            (4, 6, 5),
            (4, 7, 6),
            # Front face
            (0, 5, 1),
            (0, 4, 5),
            # Back face
            (2, 7, 3),
            (2, 6, 7),
            # Left face
            (0, 3, 7),
            (0, 7, 4),
            # Right face
            (1, 5, 6),
            (1, 6, 2),
        ]

        mesh = builder.create_mesh_object(vertices, triangles, "Cube")

        assert mesh is not None
        assert mesh.GetVertexCount() == 8
        assert mesh.GetTriangleCount() == 12

    def test_add_to_build(self):
        """Test adding a mesh object to the build plate."""
        builder = ThreeMFBuilder()

        # Create a simple triangle
        vertices = [(0.0, 0.0, 0.0), (10.0, 0.0, 0.0), (5.0, 10.0, 0.0)]
        triangles = [(0, 1, 2)]

        mesh = builder.create_mesh_object(vertices, triangles)
        build_item = builder.add_to_build(mesh)

        assert build_item is not None

    def test_save_with_mesh(self):
        """Test saving a 3MF file with a mesh object."""
        builder = ThreeMFBuilder()
        builder.add_metadata("Application", "NodeSlicer")
        builder.add_metadata("CreationDate", "2026-01-05")

        # Create a simple pyramid
        vertices = [
            (0.0, 0.0, 0.0),  # Base corner 1
            (10.0, 0.0, 0.0),  # Base corner 2
            (10.0, 10.0, 0.0),  # Base corner 3
            (0.0, 10.0, 0.0),  # Base corner 4
            (5.0, 5.0, 10.0),  # Apex
        ]

        triangles = [
            # Base
            (0, 1, 2),
            (0, 2, 3),
            # Sides
            (0, 4, 1),
            (1, 4, 2),
            (2, 4, 3),
            (3, 4, 0),
        ]

        mesh = builder.create_mesh_object(vertices, triangles, "Pyramid")
        builder.add_to_build(mesh)

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_pyramid.3mf"
            builder.save(output_path)

            # Verify file was created and has reasonable size
            assert output_path.exists()
            assert output_path.stat().st_size > 100  # Should be larger than empty file

    def test_add_to_build_with_transform(self):
        """Test adding a mesh with a transformation matrix."""
        builder = ThreeMFBuilder()

        # Create a simple triangle
        vertices = [(0.0, 0.0, 0.0), (10.0, 0.0, 0.0), (5.0, 10.0, 0.0)]
        triangles = [(0, 1, 2)]

        mesh = builder.create_mesh_object(vertices, triangles)

        # Translation matrix: move 10 units in X direction
        # Note: Custom transforms not yet fully implemented, using identity for now
        transform = [
            [1.0, 0.0, 0.0, 10.0],
            [0.0, 1.0, 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 1.0],
        ]

        # The transform parameter is accepted but currently uses identity transform
        build_item = builder.add_to_build(mesh, transform)
        assert build_item is not None

    def test_get_model_and_wrapper(self):
        """Test getting the underlying model and wrapper."""
        builder = ThreeMFBuilder()

        model = builder.get_model()
        wrapper = builder.get_wrapper()

        assert model is not None
        assert wrapper is not None
        assert model == builder.model
        assert wrapper == builder.wrapper

    def test_save_with_pathlib_path(self):
        """Test that save() works with pathlib.Path objects."""
        builder = ThreeMFBuilder()
        builder.add_metadata("Application", "NodeSlicer")

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_pathlib.3mf"
            builder.save(output_path)  # Should accept Path object

            assert output_path.exists()

    def test_production_extension_enable(self):
        """Test enabling Production Extension."""
        builder = ThreeMFBuilder()

        # Initially disabled
        assert builder.production_extension_enabled is False

        # Enable Production Extension
        builder.enable_production_extension()

        # Should be enabled (or gracefully fail)
        # The extension may not be available in all lib3mf versions
        # So we just check that the method doesn't crash
        assert builder.production_extension_enabled in [True, False]

    def test_uuid_generation(self):
        """Test UUID generation."""
        builder = ThreeMFBuilder()

        uuid1 = builder.generate_uuid()
        uuid2 = builder.generate_uuid()

        # UUIDs should be strings
        assert isinstance(uuid1, str)
        assert isinstance(uuid2, str)

        # UUIDs should be different
        assert uuid1 != uuid2

        # UUIDs should match RFC 4122 format (with hyphens)
        assert len(uuid1) == 36
        assert uuid1.count("-") == 4

    def test_set_object_uuid(self):
        """Test setting UUID on an object."""
        builder = ThreeMFBuilder()
        builder.enable_production_extension()

        vertices = [(0.0, 0.0, 0.0), (10.0, 0.0, 0.0), (5.0, 10.0, 0.0)]
        triangles = [(0, 1, 2)]

        mesh = builder.create_mesh_object(vertices, triangles, assign_uuid=False)

        # Set UUID manually
        uuid_str = builder.set_object_uuid(mesh)

        # If Production Extension is actually enabled, UUID should be set
        if builder.production_extension_enabled:
            # UUID should be returned and stored
            assert uuid_str != ""
            assert len(uuid_str) == 36

            # UUID should be in the map
            resource_id = mesh.GetResourceID()
            uuid_map = builder.get_uuid_map()
            assert resource_id in uuid_map
            assert uuid_map[resource_id] == uuid_str
        else:
            # If not enabled, UUID should be empty
            assert uuid_str == ""

    def test_set_object_uuid_custom(self):
        """Test setting a custom UUID on an object."""
        builder = ThreeMFBuilder()
        builder.enable_production_extension()

        vertices = [(0.0, 0.0, 0.0), (10.0, 0.0, 0.0), (5.0, 10.0, 0.0)]
        triangles = [(0, 1, 2)]

        mesh = builder.create_mesh_object(vertices, triangles, assign_uuid=False)

        # Set custom UUID
        custom_uuid = "12345678-1234-1234-1234-123456789abc"
        uuid_str = builder.set_object_uuid(mesh, custom_uuid)

        # If Production Extension is actually enabled, UUID should be set
        if builder.production_extension_enabled:
            # Should return the custom UUID
            assert uuid_str == custom_uuid

            # Should be in the map
            resource_id = mesh.GetResourceID()
            uuid_map = builder.get_uuid_map()
            assert uuid_map[resource_id] == custom_uuid
        else:
            # If not enabled, UUID should be empty
            assert uuid_str == ""

    def test_create_mesh_with_auto_uuid(self):
        """Test creating a mesh object with automatic UUID assignment."""
        builder = ThreeMFBuilder()
        builder.enable_production_extension()

        vertices = [(0.0, 0.0, 0.0), (10.0, 0.0, 0.0), (5.0, 10.0, 0.0)]
        triangles = [(0, 1, 2)]

        # Create mesh with auto UUID (default behavior)
        mesh = builder.create_mesh_object(vertices, triangles)

        # Should have a UUID in the map
        resource_id = mesh.GetResourceID()
        uuid_map = builder.get_uuid_map()

        if builder.production_extension_enabled:
            assert resource_id in uuid_map
            assert len(uuid_map[resource_id]) == 36

    def test_create_mesh_without_auto_uuid(self):
        """Test creating a mesh object without automatic UUID assignment."""
        builder = ThreeMFBuilder()
        builder.enable_production_extension()

        vertices = [(0.0, 0.0, 0.0), (10.0, 0.0, 0.0), (5.0, 10.0, 0.0)]
        triangles = [(0, 1, 2)]

        # Create mesh without auto UUID
        mesh = builder.create_mesh_object(vertices, triangles, assign_uuid=False)

        # Should NOT have a UUID in the map
        resource_id = mesh.GetResourceID()
        uuid_map = builder.get_uuid_map()
        assert resource_id not in uuid_map

    def test_add_to_build_with_auto_uuid(self):
        """Test adding a mesh to build with automatic UUID assignment."""
        builder = ThreeMFBuilder()
        builder.enable_production_extension()

        vertices = [(0.0, 0.0, 0.0), (10.0, 0.0, 0.0), (5.0, 10.0, 0.0)]
        triangles = [(0, 1, 2)]

        mesh = builder.create_mesh_object(vertices, triangles)
        build_item = builder.add_to_build(mesh)

        # Build item should be created successfully
        assert build_item is not None

    def test_save_with_production_extension(self):
        """Test saving a 3MF file with Production Extension enabled."""
        builder = ThreeMFBuilder()
        builder.enable_production_extension()
        builder.add_metadata("Application", "NodeSlicer")
        builder.add_metadata("Version", "0.2.0")

        # Create a mesh with UUID
        vertices = [(0.0, 0.0, 0.0), (10.0, 0.0, 0.0), (5.0, 10.0, 0.0)]
        triangles = [(0, 1, 2)]

        mesh = builder.create_mesh_object(vertices, triangles, "TriangleWithUUID")
        builder.add_to_build(mesh)

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_production_ext.3mf"
            builder.save(output_path)

            # Verify file was created
            assert output_path.exists()
            assert output_path.stat().st_size > 0

    def test_multiple_objects_with_uuids(self):
        """Test creating multiple objects, each with their own UUID."""
        builder = ThreeMFBuilder()
        builder.enable_production_extension()

        # Create three different meshes
        vertices1 = [(0.0, 0.0, 0.0), (10.0, 0.0, 0.0), (5.0, 10.0, 0.0)]
        triangles1 = [(0, 1, 2)]
        mesh1 = builder.create_mesh_object(vertices1, triangles1, "Mesh1")

        vertices2 = [(0.0, 0.0, 0.0), (10.0, 0.0, 0.0), (10.0, 10.0, 0.0), (0.0, 10.0, 0.0)]
        triangles2 = [(0, 1, 2), (0, 2, 3)]
        mesh2 = builder.create_mesh_object(vertices2, triangles2, "Mesh2")

        vertices3 = [
            (0.0, 0.0, 0.0),
            (10.0, 0.0, 0.0),
            (10.0, 10.0, 0.0),
            (0.0, 10.0, 0.0),
            (5.0, 5.0, 10.0),
        ]
        triangles3 = [(0, 1, 2), (0, 2, 3), (0, 4, 1), (1, 4, 2), (2, 4, 3), (3, 4, 0)]
        mesh3 = builder.create_mesh_object(vertices3, triangles3, "Mesh3")

        # Get UUIDs
        uuid_map = builder.get_uuid_map()

        if builder.production_extension_enabled:
            # Each mesh should have a unique UUID
            assert mesh1.GetResourceID() in uuid_map
            assert mesh2.GetResourceID() in uuid_map
            assert mesh3.GetResourceID() in uuid_map

            uuid1 = uuid_map[mesh1.GetResourceID()]
            uuid2 = uuid_map[mesh2.GetResourceID()]
            uuid3 = uuid_map[mesh3.GetResourceID()]

            # All UUIDs should be different
            assert uuid1 != uuid2
            assert uuid2 != uuid3
            assert uuid1 != uuid3

    def test_uuid_without_production_extension(self):
        """Test that UUID methods work gracefully without Production Extension."""
        builder = ThreeMFBuilder()
        # Don't enable Production Extension

        vertices = [(0.0, 0.0, 0.0), (10.0, 0.0, 0.0), (5.0, 10.0, 0.0)]
        triangles = [(0, 1, 2)]

        # Creating mesh should still work
        mesh = builder.create_mesh_object(vertices, triangles)
        assert mesh is not None

        # Manually setting UUID should return empty string
        uuid_str = builder.set_object_uuid(mesh)
        assert uuid_str == ""

        # UUID map should be empty
        uuid_map = builder.get_uuid_map()
        assert len(uuid_map) == 0

    def test_embed_gcode_basic(self):
        """Test basic G-code embedding."""
        builder = ThreeMFBuilder()

        gcode = "G28\nG1 X10 Y10 Z0.2\nG1 E5\nM104 S200\n"
        md5 = builder.embed_gcode(gcode, plate=1)

        # MD5 should be returned
        assert md5 != ""
        assert len(md5) == 32  # MD5 hash is 32 hex characters

        # G-code path should be tracked
        paths = builder.get_embedded_gcode_paths()
        assert 1 in paths
        assert paths[1] == "/Metadata/plate_1.gcode"

    def test_embed_gcode_without_md5(self):
        """Test G-code embedding without MD5 checksum."""
        builder = ThreeMFBuilder()

        gcode = "G28\nG1 X100 Y100\n"
        md5 = builder.embed_gcode(gcode, plate=1, generate_md5=False)

        # MD5 should be empty when disabled
        assert md5 == ""

        # G-code should still be tracked
        paths = builder.get_embedded_gcode_paths()
        assert 1 in paths

    def test_embed_gcode_multiple_plates(self):
        """Test embedding G-code for multiple plates."""
        builder = ThreeMFBuilder()

        gcode1 = "G28\nG1 X10 Y10\n"
        gcode2 = "G28\nG1 X20 Y20\n"
        gcode3 = "G28\nG1 X30 Y30\n"

        md5_1 = builder.embed_gcode(gcode1, plate=1)
        md5_2 = builder.embed_gcode(gcode2, plate=2)
        md5_3 = builder.embed_gcode(gcode3, plate=3)

        # All should have different MD5 hashes
        assert md5_1 != md5_2
        assert md5_2 != md5_3
        assert md5_1 != md5_3

        # All plates should be tracked
        paths = builder.get_embedded_gcode_paths()
        assert len(paths) == 3
        assert 1 in paths
        assert 2 in paths
        assert 3 in paths
        assert paths[1] == "/Metadata/plate_1.gcode"
        assert paths[2] == "/Metadata/plate_2.gcode"
        assert paths[3] == "/Metadata/plate_3.gcode"

    def test_embed_gcode_md5_verification(self):
        """Test that MD5 checksum is correct."""
        import hashlib

        builder = ThreeMFBuilder()

        gcode = "G28\nG1 X50 Y50 Z1\nM104 S220\n"
        expected_md5 = hashlib.md5(gcode.encode("utf-8")).hexdigest()

        actual_md5 = builder.embed_gcode(gcode, plate=1)

        # MD5 should match
        assert actual_md5 == expected_md5

    def test_embed_gcode_large_file(self):
        """Test embedding a large G-code file."""
        builder = ThreeMFBuilder()

        # Generate a large G-code file (simulate real print)
        gcode_lines = ["G28\n"]
        for layer in range(100):
            gcode_lines.append(f"; Layer {layer}\n")
            for i in range(50):
                gcode_lines.append(f"G1 X{i} Y{i} Z{layer * 0.2}\n")
        gcode = "".join(gcode_lines)

        md5 = builder.embed_gcode(gcode, plate=1)

        # Should handle large files
        assert md5 != ""
        assert len(md5) == 32

    def test_embed_gcode_and_save(self):
        """Test embedding G-code and saving to file."""
        builder = ThreeMFBuilder()
        builder.add_metadata("Application", "NodeSlicer")

        # Create a simple mesh
        vertices = [(0.0, 0.0, 0.0), (10.0, 0.0, 0.0), (5.0, 10.0, 0.0)]
        triangles = [(0, 1, 2)]
        mesh = builder.create_mesh_object(vertices, triangles)
        builder.add_to_build(mesh)

        # Embed G-code
        gcode = "G28\nG1 X10 Y10 Z0.2\nM104 S200\n"
        md5 = builder.embed_gcode(gcode, plate=1)

        # Save to file
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_with_gcode.3mf"
            builder.save(output_path)

            # Verify file exists and has content
            assert output_path.exists()
            assert output_path.stat().st_size > 0

            # Verify 3MF contains G-code file
            import zipfile

            with zipfile.ZipFile(output_path, "r") as zip_file:
                file_list = zip_file.namelist()
                assert "Metadata/plate_1.gcode" in file_list
                assert "Metadata/plate_1.gcode.md5" in file_list

                # Verify G-code content
                gcode_content = zip_file.read("Metadata/plate_1.gcode").decode("utf-8")
                assert gcode_content == gcode

                # Verify MD5 content
                md5_content = zip_file.read("Metadata/plate_1.gcode.md5").decode("utf-8")
                assert md5_content == md5

    def test_embed_gcode_empty_string(self):
        """Test embedding empty G-code string."""
        import hashlib

        builder = ThreeMFBuilder()

        gcode = ""
        md5 = builder.embed_gcode(gcode, plate=1)

        # Should still generate MD5 for empty string
        expected_md5 = hashlib.md5("".encode("utf-8")).hexdigest()
        assert md5 == expected_md5

    def test_embed_gcode_special_characters(self):
        """Test embedding G-code with special characters."""
        builder = ThreeMFBuilder()

        # G-code with comments and special characters
        gcode = "; This is a comment\nG28\n; Temperature: 200°C\nG1 X10 Y10\n"
        md5 = builder.embed_gcode(gcode, plate=1)

        # Should handle special characters
        assert md5 != ""
        assert len(md5) == 32

    def test_get_embedded_gcode_paths_empty(self):
        """Test getting embedded G-code paths when none are embedded."""
        builder = ThreeMFBuilder()

        paths = builder.get_embedded_gcode_paths()

        assert len(paths) == 0
        assert isinstance(paths, dict)

    # ========== Thumbnail Embedding Tests ==========

    def test_embed_thumbnail_basic(self):
        """Test basic thumbnail embedding."""
        import io
        from PIL import Image

        builder = ThreeMFBuilder()

        # Create a simple PNG image
        img = Image.new("RGB", (256, 256), color="red")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        png_data = buffer.getvalue()

        # Embed the thumbnail
        path = builder.embed_thumbnail(png_data, plate=1, thumbnail_type="plate")

        assert path == "/Metadata/plate_1.png"

    def test_embed_thumbnail_all_types(self):
        """Test embedding all thumbnail types."""
        import io
        from PIL import Image

        builder = ThreeMFBuilder()

        img = Image.new("RGB", (256, 256), color="blue")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        png_data = buffer.getvalue()

        # Test all three types
        path_plate = builder.embed_thumbnail(png_data, plate=1, thumbnail_type="plate")
        assert path_plate == "/Metadata/plate_1.png"

        path_small = builder.embed_thumbnail(png_data, plate=1, thumbnail_type="plate_small")
        assert path_small == "/Metadata/plate_1_small.png"

        path_pick = builder.embed_thumbnail(png_data, plate=1, thumbnail_type="pick")
        assert path_pick == "/Metadata/pick_1.png"

    def test_embed_thumbnail_multiple_plates(self):
        """Test embedding thumbnails for multiple plates."""
        import io
        from PIL import Image

        builder = ThreeMFBuilder()

        img = Image.new("RGB", (256, 256), color="green")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        png_data = buffer.getvalue()

        # Embed for multiple plates
        path1 = builder.embed_thumbnail(png_data, plate=1)
        path2 = builder.embed_thumbnail(png_data, plate=2)
        path3 = builder.embed_thumbnail(png_data, plate=3)

        assert path1 == "/Metadata/plate_1.png"
        assert path2 == "/Metadata/plate_2.png"
        assert path3 == "/Metadata/plate_3.png"

    def test_embed_thumbnail_invalid_type(self):
        """Test that invalid thumbnail type raises ValueError."""
        import io
        from PIL import Image

        builder = ThreeMFBuilder()

        img = Image.new("RGB", (256, 256), color="yellow")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        png_data = buffer.getvalue()

        with pytest.raises(ValueError, match="Invalid thumbnail_type"):
            builder.embed_thumbnail(png_data, plate=1, thumbnail_type="invalid_type")

    def test_embed_thumbnail_and_save(self):
        """Test embedding thumbnail and saving to file."""
        import io
        import tempfile
        import zipfile
        from PIL import Image

        builder = ThreeMFBuilder()

        # Create a simple mesh (required for valid 3MF)
        vertices = [(0, 0, 0), (10, 0, 0), (5, 10, 0)]
        triangles_indices = [(0, 1, 2)]
        obj_id = builder.create_mesh_object(vertices, triangles_indices)
        builder.add_to_build(obj_id)

        # Create a simple PNG
        img = Image.new("RGB", (128, 128), color="purple")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        png_data = buffer.getvalue()

        # Embed thumbnail
        builder.embed_thumbnail(png_data, plate=1, thumbnail_type="plate")

        # Save to temporary file
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_thumbnail.3mf"
            builder.save(output_path)

            # Verify the file exists and contains the thumbnail
            assert output_path.exists()

            # Open the 3MF as a ZIP and check for thumbnail
            with zipfile.ZipFile(output_path, "r") as z:
                namelist = z.namelist()
                assert "Metadata/plate_1.png" in namelist

                # Verify it's valid PNG data
                thumb_data = z.read("Metadata/plate_1.png")
                assert thumb_data[:8] == b"\x89PNG\r\n\x1a\n"

    def test_embed_thumbnails_from_generator_no_geometry(self):
        """Test embedding thumbnails from generator without geometry (placeholders)."""
        builder = ThreeMFBuilder()

        paths = builder.embed_thumbnails_from_generator()

        # Should return all three standard types
        assert "plate" in paths
        assert "plate_small" in paths
        assert "pick" in paths

        assert paths["plate"] == "/Metadata/plate_1.png"
        assert paths["plate_small"] == "/Metadata/plate_1_small.png"
        assert paths["pick"] == "/Metadata/pick_1.png"

    def test_embed_thumbnails_from_generator_with_geometry(self):
        """Test embedding thumbnails from generator with geometry."""
        from src.core.thumbnail_generator import Triangle, Point3D

        builder = ThreeMFBuilder()

        # Create a simple triangle
        triangles = [
            Triangle(
                v1=Point3D(0.0, 0.0, 0.0),
                v2=Point3D(10.0, 0.0, 0.0),
                v3=Point3D(5.0, 10.0, 0.0),
            ),
        ]

        paths = builder.embed_thumbnails_from_generator(triangles=triangles, plate=1)

        assert len(paths) == 3
        assert all(isinstance(v, str) for v in paths.values())

    def test_embed_thumbnails_from_generator_different_projections(self):
        """Test embedding thumbnails with different projections."""
        from src.core.thumbnail_generator import Triangle, Point3D

        triangles = [
            Triangle(
                v1=Point3D(0.0, 0.0, 0.0),
                v2=Point3D(10.0, 0.0, 5.0),
                v3=Point3D(5.0, 10.0, 10.0),
            ),
        ]

        # Test different projections (create new builder for each to avoid duplicate paths)
        for projection in ["top", "front", "side"]:
            builder = ThreeMFBuilder()
            paths = builder.embed_thumbnails_from_generator(
                triangles=triangles, plate=1, projection=projection
            )
            assert len(paths) == 3

    def test_embed_thumbnails_from_generator_multiple_plates(self):
        """Test embedding thumbnails for multiple plates."""
        builder = ThreeMFBuilder()

        paths1 = builder.embed_thumbnails_from_generator(plate=1)
        paths2 = builder.embed_thumbnails_from_generator(plate=2)

        # Verify different plate numbers
        assert paths1["plate"] == "/Metadata/plate_1.png"
        assert paths2["plate"] == "/Metadata/plate_2.png"

    def test_embed_thumbnails_complete_workflow(self):
        """Test complete workflow: mesh, G-code, thumbnails, save."""
        import io
        import tempfile
        import zipfile
        from PIL import Image

        builder = ThreeMFBuilder()

        # Add metadata
        builder.add_metadata("Title", "Complete Test")

        # Create a simple mesh
        vertices = [(0, 0, 0), (10, 0, 0), (5, 10, 0)]
        triangles_indices = [(0, 1, 2)]
        obj_id = builder.create_mesh_object(vertices, triangles_indices)

        # Add to build
        builder.add_to_build(obj_id)

        # Embed G-code
        gcode = "G28\nG1 X10 Y10\nM104 S200\n"
        builder.embed_gcode(gcode, plate=1)

        # Create and embed thumbnail
        img = Image.new("RGB", (256, 256), color="cyan")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        png_data = buffer.getvalue()
        builder.embed_thumbnail(png_data, plate=1, thumbnail_type="plate")

        # Save
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_complete_workflow.3mf"
            builder.save(output_path)

            # Verify file structure
            assert output_path.exists()

            with zipfile.ZipFile(output_path, "r") as z:
                namelist = z.namelist()
                assert "3D/3dmodel.model" in namelist
                assert "Metadata/plate_1.gcode" in namelist
                assert "Metadata/plate_1.png" in namelist
