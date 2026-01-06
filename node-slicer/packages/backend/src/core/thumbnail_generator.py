"""
Thumbnail Generator for 3MF Files

Generates PNG thumbnails in various sizes for 3MF preview in Bambu Studio.
"""

from io import BytesIO
from typing import List, Optional, Tuple
from dataclasses import dataclass

from PIL import Image, ImageDraw, ImageFont


@dataclass
class Point3D:
    """3D Point representation."""

    x: float
    y: float
    z: float


@dataclass
class Triangle:
    """3D Triangle with three vertices."""

    v1: Point3D
    v2: Point3D
    v3: Point3D


class ThumbnailGenerator:
    """
    Generator for PNG thumbnails in various sizes.

    This class creates preview thumbnails for 3MF files that are displayed
    in Bambu Studio's file browser and print queue.
    """

    # Bambu Lab standard thumbnail sizes
    STANDARD_SIZE = (256, 256)
    SMALL_SIZE = (64, 64)
    PICK_SIZE = (128, 128)

    def __init__(
        self,
        background_color: Tuple[int, int, int, int] = (255, 255, 255, 255),
        model_color: Tuple[int, int, int, int] = (100, 100, 100, 255),
    ):
        """
        Initialize the thumbnail generator.

        Args:
            background_color: RGBA background color (default: white)
            model_color: RGBA model/line color (default: gray)
        """
        self.background_color = background_color
        self.model_color = model_color

    def generate_from_triangles(
        self,
        triangles: List[Triangle],
        size: Tuple[int, int] = STANDARD_SIZE,
        projection: str = "top",
    ) -> bytes:
        """
        Generate a thumbnail from a list of triangles.

        Args:
            triangles: List of 3D triangles representing the model
            size: Output image size (width, height)
            projection: Projection type ("top", "front", "side")

        Returns:
            PNG image data as bytes
        """
        if not triangles:
            return self.generate_placeholder(size)

        # Create image
        img = Image.new("RGBA", size, self.background_color)
        draw = ImageDraw.Draw(img)

        # Calculate bounding box
        min_x = min_y = float("inf")
        max_x = max_y = float("-inf")

        points_2d = []
        for triangle in triangles:
            for vertex in [triangle.v1, triangle.v2, triangle.v3]:
                # Project to 2D based on projection type
                if projection == "top":
                    x, y = vertex.x, vertex.y
                elif projection == "front":
                    x, y = vertex.x, vertex.z
                elif projection == "side":
                    x, y = vertex.y, vertex.z
                else:
                    raise ValueError(f"Unknown projection type: {projection}")

                points_2d.append((x, y))
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)

        # Handle degenerate cases
        if min_x == max_x or min_y == max_y:
            return self.generate_placeholder(size)

        # Calculate scale and offset to fit in image
        model_width = max_x - min_x
        model_height = max_y - min_y

        # Add 10% margin
        margin = 0.1
        scale_x = size[0] * (1 - 2 * margin) / model_width
        scale_y = size[1] * (1 - 2 * margin) / model_height
        scale = min(scale_x, scale_y)

        offset_x = (size[0] - model_width * scale) / 2 - min_x * scale
        offset_y = (size[1] - model_height * scale) / 2 - min_y * scale

        # Draw triangles
        for triangle in triangles:
            vertices = [triangle.v1, triangle.v2, triangle.v3]
            polygon_points = []

            for vertex in vertices:
                if projection == "top":
                    x, y = vertex.x, vertex.y
                elif projection == "front":
                    x, y = vertex.x, vertex.z
                else:  # side
                    x, y = vertex.y, vertex.z

                # Transform to image coordinates
                img_x = x * scale + offset_x
                img_y = size[1] - (y * scale + offset_y)  # Flip Y-axis
                polygon_points.append((img_x, img_y))

            # Draw filled triangle
            draw.polygon(polygon_points, fill=self.model_color, outline=self.model_color)

        return self._image_to_png_bytes(img)

    def generate_placeholder(
        self,
        size: Tuple[int, int] = STANDARD_SIZE,
        text: Optional[str] = None,
    ) -> bytes:
        """
        Generate a placeholder thumbnail with optional text.

        Args:
            size: Output image size (width, height)
            text: Optional text to display (e.g., "No Preview")

        Returns:
            PNG image data as bytes
        """
        img = Image.new("RGBA", size, self.background_color)
        draw = ImageDraw.Draw(img)

        # Draw a simple border
        border_color = (200, 200, 200, 255)
        border_width = max(1, size[0] // 64)
        draw.rectangle(
            [border_width, border_width, size[0] - border_width, size[1] - border_width],
            outline=border_color,
            width=border_width,
        )

        # Add text if provided
        if text:
            # Try to use a default font, fall back to PIL default if not available
            try:
                font_size = size[1] // 10
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
            except (OSError, IOError):
                font = ImageFont.load_default()

            # Calculate text position (center)
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            position = ((size[0] - text_width) // 2, (size[1] - text_height) // 2)

            draw.text(position, text, fill=(128, 128, 128, 255), font=font)

        return self._image_to_png_bytes(img)

    def generate_gradient_placeholder(
        self,
        size: Tuple[int, int] = STANDARD_SIZE,
    ) -> bytes:
        """
        Generate a gradient placeholder thumbnail.

        This creates a more visually appealing placeholder than a solid color.

        Args:
            size: Output image size (width, height)

        Returns:
            PNG image data as bytes
        """
        img = Image.new("RGBA", size, self.background_color)
        draw = ImageDraw.Draw(img)

        # Create a simple vertical gradient
        for y in range(size[1]):
            # Interpolate color from light to slightly darker
            factor = y / size[1]
            r = int(240 - 20 * factor)
            g = int(240 - 20 * factor)
            b = int(240 - 20 * factor)

            draw.line([(0, y), (size[0], y)], fill=(r, g, b, 255))

        # Draw a decorative frame
        frame_color = (180, 180, 180, 255)
        frame_width = max(2, size[0] // 32)
        for i in range(frame_width):
            draw.rectangle(
                [i, i, size[0] - i - 1, size[1] - i - 1],
                outline=frame_color,
            )

        return self._image_to_png_bytes(img)

    def _image_to_png_bytes(self, img: Image.Image) -> bytes:
        """
        Convert PIL Image to PNG bytes.

        Args:
            img: PIL Image object

        Returns:
            PNG image data as bytes
        """
        buffer = BytesIO()
        img.save(buffer, format="PNG", optimize=True)
        return buffer.getvalue()

    @staticmethod
    def create_standard_set(
        triangles: Optional[List[Triangle]] = None,
        projection: str = "top",
    ) -> dict[str, bytes]:
        """
        Create a standard set of thumbnails for Bambu Lab 3MF files.

        Returns:
            Dictionary with keys: "plate", "plate_small", "pick"
            Each value is PNG image data as bytes
        """
        generator = ThumbnailGenerator()

        if triangles:
            plate = generator.generate_from_triangles(
                triangles, ThumbnailGenerator.STANDARD_SIZE, projection
            )
            plate_small = generator.generate_from_triangles(
                triangles, ThumbnailGenerator.SMALL_SIZE, projection
            )
            pick = generator.generate_from_triangles(
                triangles, ThumbnailGenerator.PICK_SIZE, projection
            )
        else:
            plate = generator.generate_gradient_placeholder(ThumbnailGenerator.STANDARD_SIZE)
            plate_small = generator.generate_gradient_placeholder(ThumbnailGenerator.SMALL_SIZE)
            pick = generator.generate_gradient_placeholder(ThumbnailGenerator.PICK_SIZE)

        return {
            "plate": plate,
            "plate_small": plate_small,
            "pick": pick,
        }
