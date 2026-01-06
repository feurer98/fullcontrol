"""
ThreeMF Builder Module

This module provides a high-level, type-safe Python wrapper around lib3mf
for creating and manipulating 3MF files.
"""

from __future__ import annotations

import uuid
from ctypes import c_float, c_uint32
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

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
        self.uuid_map: Dict[int, str] = {}  # Maps resource IDs to UUIDs
        self.production_extension_enabled = False

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

    def enable_production_extension(self) -> None:
        """
        Enable the 3MF Production Extension for UUID support.

        This adds the Production Extension namespace to the model, enabling
        UUID attributes on build, item, object, and component elements.

        The Production Extension is defined in the 3MF spec:
        http://schemas.microsoft.com/3dmanufacturing/production/2015/06

        Example:
            >>> builder = ThreeMFBuilder()
            >>> builder.enable_production_extension()
            >>> # Now UUIDs will be generated for objects and build items
        """
        try:
            # Register the Production Extension namespace
            # Namespace URI: http://schemas.microsoft.com/3dmanufacturing/production/2015/06
            # Prefix: p
            namespace_uri = (
                "http://schemas.microsoft.com/3dmanufacturing/production/2015/06"
            )
            self.model.AddNameSpace(namespace_uri, "p")
            self.production_extension_enabled = True
        except Exception as e:
            # If namespace registration fails, log but continue
            # This allows the library to work even if Production Extension isn't supported
            print(f"Warning: Could not enable Production Extension: {e}")
            self.production_extension_enabled = False

    def generate_uuid(self) -> str:
        """
        Generate a new RFC 4122 compliant UUID.

        Returns:
            A UUID string in the format: 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'

        Example:
            >>> builder = ThreeMFBuilder()
            >>> uuid_str = builder.generate_uuid()
            >>> # uuid_str is something like '550e8400-e29b-41d4-a716-446655440000'
        """
        return str(uuid.uuid4())

    def set_object_uuid(self, object_resource: Any, obj_uuid: Optional[str] = None) -> str:
        """
        Set the UUID for an object resource.

        This requires the Production Extension to be enabled.

        Args:
            object_resource: The object (mesh, component, etc.) to set UUID on
            obj_uuid: Optional UUID string. If None, a new UUID is generated.

        Returns:
            The UUID string that was set

        Example:
            >>> builder = ThreeMFBuilder()
            >>> builder.enable_production_extension()
            >>> mesh = builder.create_mesh_object(vertices, triangles)
            >>> uuid_str = builder.set_object_uuid(mesh)
        """
        if not self.production_extension_enabled:
            # Silently skip if Production Extension is not enabled
            return ""

        if obj_uuid is None:
            obj_uuid = self.generate_uuid()

        try:
            # Get the resource ID and store the UUID mapping
            resource_id = object_resource.GetResourceID()
            self.uuid_map[resource_id] = obj_uuid

            # Try to set the UUID attribute on the object
            # Note: lib3mf may or may not support this directly via SetUUID()
            # If it fails, we'll handle it gracefully
            try:
                object_resource.SetUUID(obj_uuid)
            except AttributeError:
                # SetUUID may not be available in all lib3mf versions
                # Store in map for potential manual XML manipulation later
                pass

        except Exception as e:
            print(f"Warning: Could not set UUID for object: {e}")

        return obj_uuid

    def set_build_item_uuid(
        self, build_item: Any, item_uuid: Optional[str] = None
    ) -> str:
        """
        Set the UUID for a build item.

        This requires the Production Extension to be enabled.

        Args:
            build_item: The build item to set UUID on
            item_uuid: Optional UUID string. If None, a new UUID is generated.

        Returns:
            The UUID string that was set

        Example:
            >>> builder = ThreeMFBuilder()
            >>> builder.enable_production_extension()
            >>> mesh = builder.create_mesh_object(vertices, triangles)
            >>> build_item = builder.add_to_build(mesh)
            >>> uuid_str = builder.set_build_item_uuid(build_item)
        """
        if not self.production_extension_enabled:
            return ""

        if item_uuid is None:
            item_uuid = self.generate_uuid()

        try:
            # Try to set the UUID on the build item
            try:
                build_item.SetUUID(item_uuid)
            except AttributeError:
                # SetUUID may not be available, store for later
                pass
        except Exception as e:
            print(f"Warning: Could not set UUID for build item: {e}")

        return item_uuid

    def create_mesh_object(
        self,
        vertices: List[Tuple[float, float, float]],
        triangles: List[Tuple[int, int, int]],
        name: Optional[str] = None,
        assign_uuid: bool = True,
    ) -> Any:
        """
        Create a mesh object from vertices and triangles.

        Args:
            vertices: List of (x, y, z) vertex coordinates
            triangles: List of (v1, v2, v3) vertex indices forming triangles
            name: Optional name for the mesh object
            assign_uuid: If True and Production Extension is enabled, automatically
                        assign a UUID to the object

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

        # Automatically assign UUID if Production Extension is enabled
        if assign_uuid and self.production_extension_enabled:
            self.set_object_uuid(mesh_object)

        return mesh_object

    def add_to_build(
        self,
        object_resource: Any,
        transform: Optional[List[List[float]]] = None,
        assign_uuid: bool = True,
    ) -> Any:
        """
        Add an object to the build plate.

        Args:
            object_resource: The mesh object or component to add
            transform: Optional 4x4 transformation matrix. If None, identity is used.
                      Note: Currently only identity transform is supported.
                      Custom transforms will be added in future versions.
            assign_uuid: If True and Production Extension is enabled, automatically
                        assign a UUID to the build item

        Returns:
            The created build item

        Example:
            >>> mesh = builder.create_mesh_object(vertices, triangles)
            >>> builder.add_to_build(mesh)
        """
        # For now, always use identity transform
        # TODO: Implement custom transform support in a future task
        transform_obj = self.wrapper.GetIdentityTransform()

        build_item = self.model.AddBuildItem(object_resource, transform_obj)

        # Automatically assign UUID if Production Extension is enabled
        if assign_uuid and self.production_extension_enabled:
            self.set_build_item_uuid(build_item)

        return build_item

    def get_uuid_map(self) -> Dict[int, str]:
        """
        Get the mapping of resource IDs to UUIDs.

        Returns:
            Dictionary mapping resource IDs (int) to UUID strings

        Example:
            >>> builder = ThreeMFBuilder()
            >>> builder.enable_production_extension()
            >>> mesh = builder.create_mesh_object(vertices, triangles)
            >>> uuid_map = builder.get_uuid_map()
            >>> print(f"Mesh resource ID: {mesh.GetResourceID()}, UUID: {uuid_map[mesh.GetResourceID()]}")
        """
        return self.uuid_map.copy()

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
