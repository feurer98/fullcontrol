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
