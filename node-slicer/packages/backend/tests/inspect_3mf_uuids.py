"""
Detailed inspection of 3MF file to verify UUID implementation.
"""

import tempfile
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

from src.core.threemf_builder import ThreeMFBuilder


def inspect_3mf_file():
    """Create a 3MF and inspect its UUID implementation."""
    # Create builder
    builder = ThreeMFBuilder()
    builder.enable_production_extension()
    builder.add_metadata("Application", "NodeSlicer UUID Test")

    # Create test objects
    vertices = [(0.0, 0.0, 0.0), (10.0, 0.0, 0.0), (5.0, 10.0, 0.0)]
    triangles = [(0, 1, 2)]

    mesh1 = builder.create_mesh_object(vertices, triangles, "TestMesh1")
    mesh2 = builder.create_mesh_object(vertices, triangles, "TestMesh2")

    builder.add_to_build(mesh1)
    builder.add_to_build(mesh2)

    # Save and inspect
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "test_uuids.3mf"
        builder.save(output_path)

        print("=" * 80)
        print("3MF UUID Inspection")
        print("=" * 80)

        with zipfile.ZipFile(output_path, "r") as zip_file:
            model_xml = zip_file.read("3D/3dmodel.model").decode("utf-8")

            # Parse XML
            root = ET.fromstring(model_xml)

            # Define namespaces
            namespaces = {
                "": "http://schemas.microsoft.com/3dmanufacturing/core/2015/02",
                "p": "http://schemas.microsoft.com/3dmanufacturing/production/2015/06",
            }

            print("\n📦 Model Namespaces:")
            for prefix, uri in root.attrib.items():
                if "xmlns" in prefix:
                    print(f"  {prefix}: {uri}")

            # Find all objects with UUIDs
            print("\n🔷 Objects with UUIDs:")
            objects = root.findall(".//object", namespaces)
            for obj in objects:
                obj_id = obj.get("id")
                obj_name = obj.get("name", "Unnamed")
                uuid_attr = obj.get(
                    "{http://schemas.microsoft.com/3dmanufacturing/production/2015/06}UUID"
                )
                print(f"  Object ID={obj_id}, Name='{obj_name}', UUID={uuid_attr}")

            # Find all build items with UUIDs
            print("\n🏗️  Build Items with UUIDs:")
            build = root.find(".//build", namespaces)
            if build is not None:
                items = build.findall("./item", namespaces)
                for item in items:
                    obj_id = item.get("objectid")
                    uuid_attr = item.get(
                        "{http://schemas.microsoft.com/3dmanufacturing/production/2015/06}UUID"
                    )
                    print(f"  Item objectid={obj_id}, UUID={uuid_attr}")
            else:
                print("  No build section found")

            # Print full XML for inspection
            print("\n📄 Full 3dmodel.model XML:")
            print("=" * 80)
            print(model_xml)
            print("=" * 80)


if __name__ == "__main__":
    inspect_3mf_file()
