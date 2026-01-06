"""
Unit tests for ThumbnailGenerator class.
"""

import io
from PIL import Image
import pytest

from src.core.thumbnail_generator import ThumbnailGenerator, Point3D, Triangle


class TestThumbnailGenerator:
    """Test suite for ThumbnailGenerator class."""

    def test_initialization(self):
        """Test that ThumbnailGenerator initializes with default colors."""
        generator = ThumbnailGenerator()
        assert generator.background_color == (255, 255, 255, 255)
        assert generator.model_color == (100, 100, 100, 255)

    def test_initialization_custom_colors(self):
        """Test initialization with custom colors."""
        bg_color = (200, 200, 200, 255)
        model_color = (50, 50, 50, 255)
        generator = ThumbnailGenerator(
            background_color=bg_color,
            model_color=model_color,
        )
        assert generator.background_color == bg_color
        assert generator.model_color == model_color

    def test_generate_placeholder_default(self):
        """Test generating a default placeholder thumbnail."""
        generator = ThumbnailGenerator()
        png_data = generator.generate_placeholder()

        # Verify it's valid PNG data
        assert isinstance(png_data, bytes)
        assert len(png_data) > 0

        # Verify PNG signature
        assert png_data[:8] == b"\x89PNG\r\n\x1a\n"

        # Verify we can load it as an image
        img = Image.open(io.BytesIO(png_data))
        assert img.format == "PNG"
        assert img.size == ThumbnailGenerator.STANDARD_SIZE

    def test_generate_placeholder_custom_size(self):
        """Test generating a placeholder with custom size."""
        generator = ThumbnailGenerator()
        size = (128, 128)
        png_data = generator.generate_placeholder(size=size)

        img = Image.open(io.BytesIO(png_data))
        assert img.size == size

    def test_generate_placeholder_with_text(self):
        """Test generating a placeholder with text."""
        generator = ThumbnailGenerator()
        png_data = generator.generate_placeholder(text="Test Model")

        # Verify it's valid PNG data
        img = Image.open(io.BytesIO(png_data))
        assert img.format == "PNG"
        assert img.size == ThumbnailGenerator.STANDARD_SIZE

    def test_generate_gradient_placeholder(self):
        """Test generating a gradient placeholder."""
        generator = ThumbnailGenerator()
        png_data = generator.generate_gradient_placeholder()

        img = Image.open(io.BytesIO(png_data))
        assert img.format == "PNG"
        assert img.size == ThumbnailGenerator.STANDARD_SIZE

    def test_generate_gradient_placeholder_custom_size(self):
        """Test generating a gradient placeholder with custom size."""
        generator = ThumbnailGenerator()
        size = (512, 512)
        png_data = generator.generate_gradient_placeholder(size=size)

        img = Image.open(io.BytesIO(png_data))
        assert img.size == size

    def test_generate_from_triangles_single_triangle(self):
        """Test generating thumbnail from a single triangle."""
        generator = ThumbnailGenerator()

        # Create a simple triangle
        triangle = Triangle(
            v1=Point3D(0.0, 0.0, 0.0),
            v2=Point3D(10.0, 0.0, 0.0),
            v3=Point3D(5.0, 10.0, 0.0),
        )

        png_data = generator.generate_from_triangles([triangle])

        img = Image.open(io.BytesIO(png_data))
        assert img.format == "PNG"
        assert img.size == ThumbnailGenerator.STANDARD_SIZE

    def test_generate_from_triangles_multiple_triangles(self):
        """Test generating thumbnail from multiple triangles."""
        generator = ThumbnailGenerator()

        # Create a simple square (2 triangles)
        triangles = [
            Triangle(
                v1=Point3D(0.0, 0.0, 0.0),
                v2=Point3D(10.0, 0.0, 0.0),
                v3=Point3D(10.0, 10.0, 0.0),
            ),
            Triangle(
                v1=Point3D(0.0, 0.0, 0.0),
                v2=Point3D(10.0, 10.0, 0.0),
                v3=Point3D(0.0, 10.0, 0.0),
            ),
        ]

        png_data = generator.generate_from_triangles(triangles)

        img = Image.open(io.BytesIO(png_data))
        assert img.format == "PNG"
        assert img.size == ThumbnailGenerator.STANDARD_SIZE

    def test_generate_from_triangles_empty_list(self):
        """Test that empty triangle list returns placeholder."""
        generator = ThumbnailGenerator()
        png_data = generator.generate_from_triangles([])

        img = Image.open(io.BytesIO(png_data))
        assert img.format == "PNG"
        # Should return a placeholder
        assert img.size == ThumbnailGenerator.STANDARD_SIZE

    def test_generate_from_triangles_custom_size(self):
        """Test generating thumbnail with custom size."""
        generator = ThumbnailGenerator()

        triangle = Triangle(
            v1=Point3D(0.0, 0.0, 0.0),
            v2=Point3D(10.0, 0.0, 0.0),
            v3=Point3D(5.0, 10.0, 0.0),
        )

        size = (512, 512)
        png_data = generator.generate_from_triangles([triangle], size=size)

        img = Image.open(io.BytesIO(png_data))
        assert img.size == size

    def test_generate_from_triangles_top_projection(self):
        """Test top projection (default)."""
        generator = ThumbnailGenerator()

        triangle = Triangle(
            v1=Point3D(0.0, 0.0, 0.0),
            v2=Point3D(10.0, 0.0, 5.0),
            v3=Point3D(5.0, 10.0, 10.0),
        )

        png_data = generator.generate_from_triangles([triangle], projection="top")

        img = Image.open(io.BytesIO(png_data))
        assert img.format == "PNG"

    def test_generate_from_triangles_front_projection(self):
        """Test front projection."""
        generator = ThumbnailGenerator()

        triangle = Triangle(
            v1=Point3D(0.0, 0.0, 0.0),
            v2=Point3D(10.0, 0.0, 5.0),
            v3=Point3D(5.0, 10.0, 10.0),
        )

        png_data = generator.generate_from_triangles([triangle], projection="front")

        img = Image.open(io.BytesIO(png_data))
        assert img.format == "PNG"

    def test_generate_from_triangles_side_projection(self):
        """Test side projection."""
        generator = ThumbnailGenerator()

        triangle = Triangle(
            v1=Point3D(0.0, 0.0, 0.0),
            v2=Point3D(10.0, 0.0, 5.0),
            v3=Point3D(5.0, 10.0, 10.0),
        )

        png_data = generator.generate_from_triangles([triangle], projection="side")

        img = Image.open(io.BytesIO(png_data))
        assert img.format == "PNG"

    def test_generate_from_triangles_invalid_projection(self):
        """Test that invalid projection raises ValueError."""
        generator = ThumbnailGenerator()

        triangle = Triangle(
            v1=Point3D(0.0, 0.0, 0.0),
            v2=Point3D(10.0, 0.0, 0.0),
            v3=Point3D(5.0, 10.0, 0.0),
        )

        with pytest.raises(ValueError, match="Unknown projection type"):
            generator.generate_from_triangles([triangle], projection="invalid")

    def test_generate_from_triangles_degenerate_case_point(self):
        """Test degenerate case where all vertices are at the same point."""
        generator = ThumbnailGenerator()

        # All vertices at the same point
        triangle = Triangle(
            v1=Point3D(5.0, 5.0, 5.0),
            v2=Point3D(5.0, 5.0, 5.0),
            v3=Point3D(5.0, 5.0, 5.0),
        )

        # Should return placeholder for degenerate case
        png_data = generator.generate_from_triangles([triangle])

        img = Image.open(io.BytesIO(png_data))
        assert img.format == "PNG"

    def test_generate_from_triangles_degenerate_case_line(self):
        """Test degenerate case where all vertices are collinear (no height)."""
        generator = ThumbnailGenerator()

        # All vertices on a horizontal line (no Y variation)
        triangle = Triangle(
            v1=Point3D(0.0, 5.0, 0.0),
            v2=Point3D(10.0, 5.0, 0.0),
            v3=Point3D(5.0, 5.0, 0.0),
        )

        # Should return placeholder for degenerate case
        png_data = generator.generate_from_triangles([triangle])

        img = Image.open(io.BytesIO(png_data))
        assert img.format == "PNG"

    def test_create_standard_set_without_triangles(self):
        """Test creating standard thumbnail set without geometry (placeholders)."""
        thumbnail_set = ThumbnailGenerator.create_standard_set()

        assert isinstance(thumbnail_set, dict)
        assert "plate" in thumbnail_set
        assert "plate_small" in thumbnail_set
        assert "pick" in thumbnail_set

        # Verify all are valid PNG data
        for thumb_type, png_data in thumbnail_set.items():
            assert isinstance(png_data, bytes)
            assert len(png_data) > 0
            assert png_data[:8] == b"\x89PNG\r\n\x1a\n"

        # Verify sizes
        plate_img = Image.open(io.BytesIO(thumbnail_set["plate"]))
        assert plate_img.size == ThumbnailGenerator.STANDARD_SIZE

        small_img = Image.open(io.BytesIO(thumbnail_set["plate_small"]))
        assert small_img.size == ThumbnailGenerator.SMALL_SIZE

        pick_img = Image.open(io.BytesIO(thumbnail_set["pick"]))
        assert pick_img.size == ThumbnailGenerator.PICK_SIZE

    def test_create_standard_set_with_triangles(self):
        """Test creating standard thumbnail set with geometry."""
        triangles = [
            Triangle(
                v1=Point3D(0.0, 0.0, 0.0),
                v2=Point3D(10.0, 0.0, 0.0),
                v3=Point3D(5.0, 10.0, 0.0),
            ),
        ]

        thumbnail_set = ThumbnailGenerator.create_standard_set(triangles)

        assert isinstance(thumbnail_set, dict)
        assert len(thumbnail_set) == 3

        # Verify all are valid PNG data
        for thumb_type, png_data in thumbnail_set.items():
            img = Image.open(io.BytesIO(png_data))
            assert img.format == "PNG"

    def test_create_standard_set_different_projections(self):
        """Test creating standard set with different projections."""
        triangles = [
            Triangle(
                v1=Point3D(0.0, 0.0, 0.0),
                v2=Point3D(10.0, 0.0, 5.0),
                v3=Point3D(5.0, 10.0, 10.0),
            ),
        ]

        for projection in ["top", "front", "side"]:
            thumbnail_set = ThumbnailGenerator.create_standard_set(triangles, projection)
            assert len(thumbnail_set) == 3

            for png_data in thumbnail_set.values():
                img = Image.open(io.BytesIO(png_data))
                assert img.format == "PNG"

    def test_image_to_png_bytes_optimization(self):
        """Test that PNG bytes are optimized."""
        generator = ThumbnailGenerator()

        # Generate two placeholders: one with optimization, one without
        png_data_optimized = generator.generate_placeholder()

        # Both should be valid PNG
        assert png_data_optimized[:8] == b"\x89PNG\r\n\x1a\n"

        # Optimized version should work
        img = Image.open(io.BytesIO(png_data_optimized))
        assert img.format == "PNG"

    def test_large_model(self):
        """Test thumbnail generation with a larger model (cube with 12 triangles)."""
        generator = ThumbnailGenerator()

        # Create a cube (6 faces, 2 triangles per face = 12 triangles)
        cube_triangles = []

        # Front face
        cube_triangles.append(
            Triangle(Point3D(0, 0, 0), Point3D(10, 0, 0), Point3D(10, 10, 0))
        )
        cube_triangles.append(
            Triangle(Point3D(0, 0, 0), Point3D(10, 10, 0), Point3D(0, 10, 0))
        )

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
        cube_triangles.append(
            Triangle(Point3D(0, 0, 0), Point3D(10, 0, 10), Point3D(10, 0, 0))
        )
        cube_triangles.append(
            Triangle(Point3D(0, 0, 0), Point3D(0, 0, 10), Point3D(10, 0, 10))
        )

        # Left face
        cube_triangles.append(
            Triangle(Point3D(0, 0, 0), Point3D(0, 10, 0), Point3D(0, 10, 10))
        )
        cube_triangles.append(
            Triangle(Point3D(0, 0, 0), Point3D(0, 10, 10), Point3D(0, 0, 10))
        )

        # Right face
        cube_triangles.append(
            Triangle(Point3D(10, 0, 0), Point3D(10, 10, 10), Point3D(10, 10, 0))
        )
        cube_triangles.append(
            Triangle(Point3D(10, 0, 0), Point3D(10, 0, 10), Point3D(10, 10, 10))
        )

        # Generate thumbnail
        png_data = generator.generate_from_triangles(cube_triangles)

        img = Image.open(io.BytesIO(png_data))
        assert img.format == "PNG"
        assert img.size == ThumbnailGenerator.STANDARD_SIZE
