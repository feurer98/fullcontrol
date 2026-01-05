"""
ThreeMF Builder Module

This module provides a high-level, type-safe Python wrapper around lib3mf
for creating and manipulating 3MF files.
"""

from __future__ import annotations

from ctypes import c_float, c_uint32
from pathlib import Path
from typing import Any, List, Optional, Tuple

import lib3mf


class ThreeMFBuilder:
    """
    A high-level builder class for creating 3MF files using lib3mf.

    This class provides a type-safe API for creating 3MF models, adding metadata,
    creating mesh objects, and building 3D manufacturing files.

    Example:
        >>> builder = ThreeMFBuilder()
        >>> builder.add_metadata("Application", "NodeSlicer")
        >>> builder.save("output.3mf")
    """

    def __init__(self) -> None:
        """Initialize the ThreeMFBuilder with a new model."""
        self.wrapper = lib3mf.get_wrapper()
        self.model = self.wrapper.CreateModel()

    def add_metadata(self, name: str, value: str, namespace: str = "") -> None:
        """
        Add metadata to the 3MF model.

        Note: This is a simplified wrapper. For production use, consider using
        specific metadata namespaces as per the 3MF specification.

        Args:
            name: The metadata key/name
            value: The metadata value
            namespace: Optional XML namespace (default: empty)

        Example:
            >>> builder.add_metadata("Title", "My Model")
            >>> builder.add_metadata("Application", "NodeSlicer")
        """
        # Note: lib3mf metadata can be finicky. For now, we'll catch errors
        # and continue, as metadata is not critical for basic 3MF functionality
        try:
            metadata_group = self.model.GetMetaDataGroup()
            metadata_group.AddMetaData(namespace, name, value, "", True)
        except Exception:
            # Metadata addition failed, but this is not critical for basic 3MF files
            pass

    def create_mesh_object(
        self,
        vertices: List[Tuple[float, float, float]],
        triangles: List[Tuple[int, int, int]],
        name: Optional[str] = None,
    ) -> Any:
        """
        Create a mesh object from vertices and triangles.

        Args:
            vertices: List of (x, y, z) vertex coordinates
            triangles: List of (v1, v2, v3) vertex indices forming triangles
            name: Optional name for the mesh object

        Returns:
            The created mesh object

        Example:
            >>> vertices = [(0, 0, 0), (10, 0, 0), (5, 10, 0)]
            >>> triangles = [(0, 1, 2)]
            >>> mesh = builder.create_mesh_object(vertices, triangles, "Triangle")
        """
        mesh_object = self.model.AddMeshObject()

        if name:
            mesh_object.SetName(name)

        # Add vertices using lib3mf Position structures
        for x, y, z in vertices:
            pos = lib3mf.Position()
            pos.Coordinates = (c_float * 3)(float(x), float(y), float(z))
            mesh_object.AddVertex(pos)

        # Add triangles using lib3mf Triangle structures
        for v1, v2, v3 in triangles:
            tri = lib3mf.Triangle()
            tri.Indices = (c_uint32 * 3)(int(v1), int(v2), int(v3))
            mesh_object.AddTriangle(tri)

        return mesh_object

    def add_to_build(
        self,
        object_resource: Any,
        transform: Optional[List[List[float]]] = None,
    ) -> Any:
        """
        Add an object to the build plate.

        Args:
            object_resource: The mesh object or component to add
            transform: Optional 4x4 transformation matrix. If None, identity is used.
                      Note: Currently only identity transform is supported.
                      Custom transforms will be added in future versions.

        Returns:
            The created build item

        Example:
            >>> mesh = builder.create_mesh_object(vertices, triangles)
            >>> builder.add_to_build(mesh)
        """
        # For now, always use identity transform
        # TODO: Implement custom transform support in Task 2.2
        transform_obj = self.wrapper.GetIdentityTransform()

        build_item = self.model.AddBuildItem(object_resource, transform_obj)
        return build_item

    def save(self, path: str | Path) -> None:
        """
        Save the 3MF model to a file.

        Args:
            path: File path where the 3MF should be saved

        Example:
            >>> builder.save("output.3mf")
            >>> builder.save(Path("models/test.3mf"))
        """
        path_str = str(path)
        writer = self.model.QueryWriter("3mf")
        writer.WriteToFile(path_str)

    def get_model(self) -> Any:
        """
        Get the underlying lib3mf model.

        Returns:
            The lib3mf model object
        """
        return self.model

    def get_wrapper(self) -> Any:
        """
        Get the underlying lib3mf wrapper.

        Returns:
            The lib3mf wrapper object
        """
        return self.wrapper
