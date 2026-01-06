"""
Tests for BambuConfigGenerator.

This test suite verifies the Bambu Lab configuration file generation
including model_settings.config, project_settings.config, and slice_info.config.
"""

import json
from xml.etree import ElementTree as ET

import pytest

from src.core.bambu_config import (
    BambuConfigGenerator,
    FilamentInfo,
    ObjectInfo,
    PlateInfo,
    SliceInfo,
)


class TestPlateInfo:
    """Tests for PlateInfo dataclass."""

    def test_plate_info_defaults(self):
        """Test PlateInfo with default values."""
        plate = PlateInfo()

        assert plate.plate_id == 1
        assert plate.plate_name == ""
        assert plate.locked is False
        assert plate.gcode_file == "Metadata/plate_1.gcode"
        assert plate.thumbnail_file == "Metadata/plate_1.png"

    def test_plate_info_custom_values(self):
        """Test PlateInfo with custom values."""
        plate = PlateInfo(
            plate_id=2,
            plate_name="Test Plate",
            locked=True,
            gcode_file="Metadata/plate_2.gcode",
        )

        assert plate.plate_id == 2
        assert plate.plate_name == "Test Plate"
        assert plate.locked is True
        assert plate.gcode_file == "Metadata/plate_2.gcode"


class TestObjectInfo:
    """Tests for ObjectInfo dataclass."""

    def test_object_info_creation(self):
        """Test ObjectInfo creation."""
        obj = ObjectInfo(identify_id="123", name="test.STL")

        assert obj.identify_id == "123"
        assert obj.name == "test.STL"
        assert obj.skipped is False

    def test_object_info_skipped(self):
        """Test ObjectInfo with skipped flag."""
        obj = ObjectInfo(identify_id="456", name="skipped.STL", skipped=True)

        assert obj.skipped is True


class TestFilamentInfo:
    """Tests for FilamentInfo dataclass."""

    def test_filament_info_defaults(self):
        """Test FilamentInfo with default values."""
        fil = FilamentInfo()

        assert fil.id == "1"
        assert fil.tray_info_idx == "GFA00"
        assert fil.type == "PLA"
        assert fil.color == "#FFFFFF"
        assert fil.used_m == 0.0
        assert fil.used_g == 0.0

    def test_filament_info_custom(self):
        """Test FilamentInfo with custom values."""
        fil = FilamentInfo(
            id="2",
            tray_info_idx="GFA01",
            type="PETG",
            color="#FF0000",
            used_m=10.5,
            used_g=25.3,
        )

        assert fil.id == "2"
        assert fil.type == "PETG"
        assert fil.color == "#FF0000"
        assert fil.used_m == 10.5
        assert fil.used_g == 25.3


class TestSliceInfo:
    """Tests for SliceInfo dataclass."""

    def test_slice_info_defaults(self):
        """Test SliceInfo with default values."""
        info = SliceInfo()

        assert info.printer_model_id == "BL-P001"
        assert info.nozzle_diameters == "0.4"
        assert info.timelapse_type == 0
        assert info.prediction == 0
        assert info.weight == 0.0
        assert info.outside is False
        assert info.support_used is False
        assert info.label_object_enabled is False
        assert len(info.objects) == 0
        assert len(info.filaments) == 0

    def test_slice_info_with_objects_and_filaments(self):
        """Test SliceInfo with objects and filaments."""
        obj1 = ObjectInfo("1", "part1.STL")
        obj2 = ObjectInfo("2", "part2.STL")
        fil = FilamentInfo(used_m=5.5, used_g=13.2)

        info = SliceInfo(
            prediction=1200,
            weight=13.2,
            objects=[obj1, obj2],
            filaments=[fil],
        )

        assert info.prediction == 1200
        assert info.weight == 13.2
        assert len(info.objects) == 2
        assert len(info.filaments) == 1
        assert info.objects[0].name == "part1.STL"
        assert info.filaments[0].used_g == 13.2


class TestBambuConfigGenerator:
    """Tests for BambuConfigGenerator."""

    def test_initialization(self):
        """Test BambuConfigGenerator initialization."""
        generator = BambuConfigGenerator()
        assert generator is not None

    def test_generate_model_settings_default(self):
        """Test model_settings.config generation with default PlateInfo."""
        generator = BambuConfigGenerator()
        plate = PlateInfo()

        config_xml = generator.generate_model_settings(plate)

        # Verify it's valid XML
        root = ET.fromstring(config_xml)
        assert root.tag == "config"

        # Find plate element
        plate_elem = root.find("plate")
        assert plate_elem is not None

        # Verify metadata elements
        metadata = {
            elem.get("key"): elem.get("value")
            for elem in plate_elem.findall("metadata")
        }

        assert metadata["plater_id"] == "1"
        assert metadata["locked"] == "false"
        assert metadata["gcode_file"] == "Metadata/plate_1.gcode"
        assert metadata["thumbnail_file"] == "Metadata/plate_1.png"

    def test_generate_model_settings_custom(self):
        """Test model_settings.config generation with custom PlateInfo."""
        generator = BambuConfigGenerator()
        plate = PlateInfo(
            plate_id=5,
            plate_name="CustomPlate",
            locked=True,
            gcode_file="Metadata/custom.gcode",
            thumbnail_file="Metadata/custom.png",
        )

        config_xml = generator.generate_model_settings(plate)

        # Parse and verify
        root = ET.fromstring(config_xml)
        plate_elem = root.find("plate")
        metadata = {
            elem.get("key"): elem.get("value")
            for elem in plate_elem.findall("metadata")
        }

        assert metadata["plater_id"] == "5"
        assert metadata["plater_name"] == "CustomPlate"
        assert metadata["locked"] == "true"
        assert metadata["gcode_file"] == "Metadata/custom.gcode"

    def test_generate_project_settings_defaults(self):
        """Test project_settings.config generation with defaults."""
        generator = BambuConfigGenerator()

        config_json = generator.generate_project_settings()

        # Verify it's valid JSON
        settings = json.loads(config_json)

        # Verify key settings
        assert settings["from"] == "project"
        assert settings["curr_bed_type"] == "Textured PEI Plate"
        assert settings["layer_height"] == "0.2"
        assert settings["filament_type"] == ["PLA"]
        assert settings["hot_plate_temp"] == ["55"]
        assert settings["inner_wall_speed"] == "300"

    def test_generate_project_settings_custom(self):
        """Test project_settings.config generation with custom values."""
        generator = BambuConfigGenerator()

        config_json = generator.generate_project_settings(
            printer="bambulab_p1s",
            filament="PETG",
            layer_height=0.15,
            nozzle_temp=250,
            bed_temp=70,
        )

        # Verify
        settings = json.loads(config_json)

        assert settings["layer_height"] == "0.15"
        assert settings["filament_type"] == ["PETG"]
        assert settings["hot_plate_temp"] == ["70"]
        assert settings["hot_plate_temp_initial_layer"] == ["70"]

    def test_generate_project_settings_additional_settings(self):
        """Test project_settings.config with additional settings."""
        generator = BambuConfigGenerator()

        additional = {
            "custom_setting_1": "value1",
            "custom_setting_2": 42,
            "custom_array": ["a", "b", "c"],
        }

        config_json = generator.generate_project_settings(
            additional_settings=additional
        )

        settings = json.loads(config_json)

        # Verify additional settings are present
        assert settings["custom_setting_1"] == "value1"
        assert settings["custom_setting_2"] == 42
        assert settings["custom_array"] == ["a", "b", "c"]

        # Verify defaults still present
        assert settings["filament_type"] == ["PLA"]

    def test_generate_slice_info_minimal(self):
        """Test slice_info.config generation with minimal data."""
        generator = BambuConfigGenerator()
        info = SliceInfo()

        config_xml = generator.generate_slice_info(info)

        # Verify it's valid XML
        root = ET.fromstring(config_xml)
        assert root.tag == "config"

        # Verify header
        header = root.find("header")
        assert header is not None
        header_items = {
            item.get("key"): item.get("value") for item in header.findall("header_item")
        }
        assert header_items["X-BBL-Client-Type"] == "slicer"
        assert "X-BBL-Client-Version" in header_items

        # Verify plate metadata
        plate = root.find("plate")
        assert plate is not None
        metadata = {
            elem.get("key"): elem.get("value") for elem in plate.findall("metadata")
        }

        assert metadata["printer_model_id"] == "BL-P001"
        assert metadata["nozzle_diameters"] == "0.4"
        assert metadata["prediction"] == "0"
        assert metadata["weight"] == "0.00"

    def test_generate_slice_info_with_objects(self):
        """Test slice_info.config generation with objects."""
        generator = BambuConfigGenerator()

        obj1 = ObjectInfo("100", "cube.STL")
        obj2 = ObjectInfo("101", "cylinder.STL", skipped=True)

        info = SliceInfo(
            prediction=3600,
            weight=50.5,
            objects=[obj1, obj2],
        )

        config_xml = generator.generate_slice_info(info)

        # Parse and verify
        root = ET.fromstring(config_xml)
        plate = root.find("plate")

        # Check metadata
        metadata = {
            elem.get("key"): elem.get("value") for elem in plate.findall("metadata")
        }
        assert metadata["prediction"] == "3600"
        assert metadata["weight"] == "50.50"

        # Check objects
        objects = plate.findall("object")
        assert len(objects) == 2
        assert objects[0].get("identify_id") == "100"
        assert objects[0].get("name") == "cube.STL"
        assert objects[0].get("skipped") == "false"
        assert objects[1].get("skipped") == "true"

    def test_generate_slice_info_with_filaments(self):
        """Test slice_info.config generation with filament info."""
        generator = BambuConfigGenerator()

        fil1 = FilamentInfo(id="1", type="PLA", color="#FF0000", used_m=10.5, used_g=25.2)
        fil2 = FilamentInfo(
            id="2", type="PETG", color="#00FF00", used_m=5.2, used_g=13.7
        )

        info = SliceInfo(
            prediction=1800,
            weight=38.9,
            filaments=[fil1, fil2],
        )

        config_xml = generator.generate_slice_info(info)

        # Parse and verify
        root = ET.fromstring(config_xml)
        plate = root.find("plate")

        # Check filaments
        filaments = plate.findall("filament")
        assert len(filaments) == 2
        assert filaments[0].get("id") == "1"
        assert filaments[0].get("type") == "PLA"
        assert filaments[0].get("color") == "#FF0000"
        assert filaments[0].get("used_m") == "10.50"
        assert filaments[0].get("used_g") == "25.20"
        assert filaments[1].get("type") == "PETG"

    def test_generate_slice_info_complete(self):
        """Test slice_info.config with all features."""
        generator = BambuConfigGenerator()

        obj = ObjectInfo("200", "complex_part.STL")
        fil = FilamentInfo(type="ABS", used_m=15.0, used_g=40.5)

        info = SliceInfo(
            printer_model_id="BL-P002",
            nozzle_diameters="0.6",
            timelapse_type=1,
            prediction=7200,
            weight=40.5,
            outside=True,
            support_used=True,
            label_object_enabled=True,
            objects=[obj],
            filaments=[fil],
        )

        config_xml = generator.generate_slice_info(info)

        # Parse and verify
        root = ET.fromstring(config_xml)
        plate = root.find("plate")
        metadata = {
            elem.get("key"): elem.get("value") for elem in plate.findall("metadata")
        }

        assert metadata["printer_model_id"] == "BL-P002"
        assert metadata["nozzle_diameters"] == "0.6"
        assert metadata["timelapse_type"] == "1"
        assert metadata["outside"] == "true"
        assert metadata["support_used"] == "true"
        assert metadata["label_object_enabled"] == "true"

    def test_prettify_xml(self):
        """Test XML prettification."""
        generator = BambuConfigGenerator()

        # Create a simple XML element
        root = ET.Element("test")
        child = ET.SubElement(root, "child")
        child.set("attr", "value")

        pretty_xml = generator._prettify_xml(root)

        # Verify it's properly formatted
        assert '<?xml version="1.0"' in pretty_xml
        assert "<test>" in pretty_xml
        assert '<child attr="value"/>' in pretty_xml or '<child attr="value" />' in pretty_xml

    def test_all_configs_are_valid_xml_json(self):
        """Test that all generated configs are valid XML/JSON."""
        generator = BambuConfigGenerator()

        # Test model_settings (XML)
        model_config = generator.generate_model_settings(PlateInfo())
        ET.fromstring(model_config)  # Should not raise

        # Test project_settings (JSON)
        project_config = generator.generate_project_settings()
        json.loads(project_config)  # Should not raise

        # Test slice_info (XML)
        slice_config = generator.generate_slice_info(SliceInfo())
        ET.fromstring(slice_config)  # Should not raise
