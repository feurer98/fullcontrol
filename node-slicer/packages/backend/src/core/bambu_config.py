"""
Bambu Lab 3MF Config Generator.

This module provides functionality to generate Bambu Lab specific configuration
files for 3MF packages:
- model_settings.config (XML): Plate and file references
- project_settings.config (JSON): Printer and print settings
- slice_info.config (XML): Slice metadata and statistics
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
from xml.dom import minidom
from xml.etree import ElementTree as ET


@dataclass
class ObjectInfo:
    """Information about an object in the 3MF file."""

    identify_id: str
    name: str
    skipped: bool = False


@dataclass
class FilamentInfo:
    """Filament information for a plate."""

    id: str = "1"
    tray_info_idx: str = "GFA00"
    type: str = "PLA"
    color: str = "#FFFFFF"
    used_m: float = 0.0
    used_g: float = 0.0


@dataclass
class PlateInfo:
    """Information about a build plate."""

    plate_id: int = 1
    plate_name: str = ""
    locked: bool = False
    gcode_file: str = "Metadata/plate_1.gcode"
    thumbnail_file: str = "Metadata/plate_1.png"
    thumbnail_no_light_file: str = "Metadata/plate_1.png"
    top_file: str = "Metadata/pick_1.png"
    pick_file: str = "Metadata/pick_1.png"
    pattern_bbox_file: str = "Metadata/plate_1.json"


@dataclass
class SliceInfo:
    """Slice information for metadata."""

    printer_model_id: str = "BL-P001"  # Bambu Lab X1 Carbon
    nozzle_diameters: str = "0.4"
    timelapse_type: int = 0
    prediction: int = 0  # Estimated print time in seconds
    weight: float = 0.0  # Filament weight in grams
    outside: bool = False
    support_used: bool = False
    label_object_enabled: bool = False
    objects: List[ObjectInfo] = field(default_factory=list)
    filaments: List[FilamentInfo] = field(default_factory=list)


class BambuConfigGenerator:
    """
    Generator for Bambu Lab specific 3MF configuration files.

    This class creates the necessary configuration files that Bambu Studio
    expects in a 3MF package:
    - model_settings.config: References to G-code and thumbnail files
    - project_settings.config: Printer and print settings
    - slice_info.config: Slice metadata and statistics

    Example:
        >>> generator = BambuConfigGenerator()
        >>> plate_info = PlateInfo(plate_id=1, gcode_file="Metadata/plate_1.gcode")
        >>> model_config = generator.generate_model_settings(plate_info)
        >>> print(model_config)
    """

    def __init__(self) -> None:
        """Initialize the Bambu Lab config generator."""
        pass

    def generate_model_settings(self, plate_info: PlateInfo) -> str:
        """
        Generate model_settings.config XML content.

        This file contains references to G-code files, thumbnails, and other
        plate-related metadata.

        Args:
            plate_info: Information about the build plate

        Returns:
            XML string for model_settings.config

        Example:
            >>> generator = BambuConfigGenerator()
            >>> plate = PlateInfo(plate_id=1)
            >>> config = generator.generate_model_settings(plate)
            >>> assert '<?xml version="1.0"' in config
        """
        root = ET.Element("config")

        # Create plate element
        plate = ET.SubElement(root, "plate")

        # Add metadata elements
        metadata_items = [
            ("plater_id", str(plate_info.plate_id)),
            ("plater_name", plate_info.plate_name),
            ("locked", "true" if plate_info.locked else "false"),
            ("gcode_file", plate_info.gcode_file),
            ("thumbnail_file", plate_info.thumbnail_file),
            ("thumbnail_no_light_file", plate_info.thumbnail_no_light_file),
            ("top_file", plate_info.top_file),
            ("pick_file", plate_info.pick_file),
            ("pattern_bbox_file", plate_info.pattern_bbox_file),
        ]

        for key, value in metadata_items:
            metadata = ET.SubElement(plate, "metadata")
            metadata.set("key", key)
            metadata.set("value", value)

        # Convert to pretty-printed XML string
        return self._prettify_xml(root)

    def generate_project_settings(
        self,
        printer: str = "bambulab_x1c",
        filament: str = "PLA",
        layer_height: float = 0.2,
        nozzle_temp: int = 220,
        bed_temp: int = 55,
        additional_settings: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Generate project_settings.config JSON content.

        This file contains extensive printer and print settings. We generate
        a minimal viable configuration with sensible defaults.

        Args:
            printer: Printer model identifier
            filament: Filament type (PLA, PETG, ABS, etc.)
            layer_height: Layer height in mm
            nozzle_temp: Nozzle temperature in Celsius
            bed_temp: Bed temperature in Celsius
            additional_settings: Optional additional settings to merge

        Returns:
            JSON string for project_settings.config

        Example:
            >>> generator = BambuConfigGenerator()
            >>> config = generator.generate_project_settings(
            ...     printer="bambulab_x1c",
            ...     filament="PLA",
            ...     nozzle_temp=220,
            ...     bed_temp=55
            ... )
            >>> settings = json.loads(config)
            >>> assert settings["filament_type"] == ["PLA"]
        """
        # Minimal viable configuration
        config: Dict[str, Any] = {
            # Basic settings
            "from": "project",
            "curr_bed_type": "Textured PEI Plate",
            "default_print_profile": f"{layer_height:.2f}mm Standard @BBL X1C",
            "default_filament_profile": [f"Bambu {filament} Basic @BBL X1C"],
            # Layer height
            "layer_height": f"{layer_height}",
            "initial_layer_print_height": f"{layer_height}",
            # Temperatures
            "hot_plate_temp": [str(bed_temp)],
            "hot_plate_temp_initial_layer": [str(bed_temp)],
            "cool_plate_temp": [str(bed_temp)],
            "cool_plate_temp_initial_layer": [str(bed_temp)],
            "eng_plate_temp": ["0"],
            "eng_plate_temp_initial_layer": ["0"],
            "chamber_temperatures": ["0"],
            # Filament
            "filament_type": [filament],
            "filament_colour": ["#FFFFFF"],
            "filament_vendor": ["Bambu Lab"],
            "filament_diameter": ["1.75"],
            "filament_density": ["1.24" if filament == "PLA" else "1.27"],
            "filament_cost": ["24.99"],
            "filament_settings_id": [f"Bambu {filament} Basic @BBL X1C"],
            "filament_ids": ["GFA00"],
            "filament_is_support": ["0"],
            "filament_soluble": ["0"],
            # Print speeds
            "inner_wall_speed": "300",
            "outer_wall_speed": "200",
            "internal_solid_infill_speed": "250",
            "initial_layer_speed": "50",
            "gap_infill_speed": "250",
            "bridge_speed": "50",
            # Accelerations
            "default_acceleration": "10000",
            "initial_layer_acceleration": "500",
            "inner_wall_acceleration": "0",
            "outer_wall_acceleration": "0",
            # Jerk
            "default_jerk": "0",
            "initial_layer_jerk": "9",
            "inner_wall_jerk": "9",
            "infill_jerk": "9",
            # Line widths
            "line_width": "0.42",
            "inner_wall_line_width": "0.45",
            "initial_layer_line_width": "0.5",
            "internal_solid_infill_line_width": "0.42",
            # Walls and shells
            "wall_loops": "2",
            "top_shell_layers": "3",
            "bottom_shell_layers": "3",
            "top_shell_thickness": "0",
            "bottom_shell_thickness": "0",
            "ensure_vertical_shell_thickness": "1",
            # Infill
            "sparse_infill_density": "15%",
            "sparse_infill_pattern": "grid",
            "infill_direction": "45",
            "infill_wall_overlap": "15%",
            # Fan speeds
            "fan_min_speed": ["100"],
            "fan_max_speed": ["100"],
            "close_fan_the_first_x_layers": ["1"],
            "full_fan_speed_layer": ["0"],
            "fan_cooling_layer_time": ["100"],
            "auxiliary_fan": "1",
            "during_print_exhaust_fan_speed": ["70"],
            "complete_print_exhaust_fan_speed": ["70"],
            "additional_cooling_fan_speed": ["70"],
            # Support
            "enable_support": "0",
            "enforce_support_layers": "0",
            "enable_prime_tower": "0",
            # Retraction
            "filament_retraction_length": ["nil"],
            "filament_retraction_speed": ["nil"],
            "filament_deretraction_speed": ["nil"],
            "deretraction_speed": ["30"],
            # Advanced
            "enable_arc_fitting": "1",
            "gcode_flavor": "marlin",
            "gcode_add_line_number": "0",
            "exclude_object": "1",
            "enable_overhang_speed": "1",
            "detect_overhang_wall": "1",
            "detect_thin_wall": "0",
            "detect_narrow_internal_solid_infill": "1",
            "elefant_foot_compensation": "0.15",
            "filename_format": "{input_filename_base}_{filament_type[0]}_{print_time}.gcode",
            # Machine limits
            "machine_max_acceleration_e": ["5000", "5000"],
            "machine_max_acceleration_extruding": ["20000", "20000"],
            "machine_max_acceleration_retracting": ["5000", "5000"],
            "machine_max_acceleration_travel": ["9000", "9000"],
            "machine_max_acceleration_x": ["20000", "20000"],
            "machine_max_acceleration_y": ["20000", "20000"],
            "machine_max_acceleration_z": ["500", "200"],
            "machine_max_jerk_e": ["2.5", "2.5"],
            "machine_max_jerk_x": ["9", "9"],
            "machine_max_jerk_y": ["9", "9"],
            "machine_max_jerk_z": ["3", "3"],
            "machine_max_speed_e": ["30", "30"],
            "machine_max_speed_x": ["500", "200"],
            "machine_max_speed_y": ["500", "200"],
            "machine_max_speed_z": ["20", "20"],
            # Extruder
            "extruder_colour": ["#018001"],
            "extruder_offset": ["0x2"],
            "extruder_type": ["DirectDrive"],
            "default_filament_colour": [""],
            # Build volume
            "extruder_clearance_height_to_lid": "90",
            "extruder_clearance_height_to_rod": "34",
            "extruder_clearance_max_radius": "68",
            "extruder_clearance_radius": "57",
        }

        # Merge additional settings if provided
        if additional_settings:
            config.update(additional_settings)

        # Convert to pretty-printed JSON
        return json.dumps(config, indent=4)

    def generate_slice_info(self, slice_info: SliceInfo) -> str:
        """
        Generate slice_info.config XML content.

        This file contains metadata about the slicing process, including
        printer model, prediction time, filament usage, and object information.

        Args:
            slice_info: Slice information and metadata

        Returns:
            XML string for slice_info.config

        Example:
            >>> generator = BambuConfigGenerator()
            >>> info = SliceInfo(
            ...     prediction=582,
            ...     weight=1.35,
            ...     objects=[ObjectInfo("78", "test.STL")]
            ... )
            >>> config = generator.generate_slice_info(info)
            >>> assert "prediction" in config
        """
        root = ET.Element("config")

        # Header section
        header = ET.SubElement(root, "header")
        ET.SubElement(header, "header_item").set("key", "X-BBL-Client-Type")
        header[0].set("value", "slicer")
        ET.SubElement(header, "header_item").set("key", "X-BBL-Client-Version")
        header[1].set("value", "01.09.07.52")

        # Plate section
        plate = ET.SubElement(root, "plate")

        # Plate metadata
        plate_metadata = [
            ("index", "1"),
            ("printer_model_id", slice_info.printer_model_id),
            ("nozzle_diameters", slice_info.nozzle_diameters),
            ("timelapse_type", str(slice_info.timelapse_type)),
            ("prediction", str(slice_info.prediction)),
            ("weight", f"{slice_info.weight:.2f}"),
            ("outside", "true" if slice_info.outside else "false"),
            ("support_used", "true" if slice_info.support_used else "false"),
            (
                "label_object_enabled",
                "true" if slice_info.label_object_enabled else "false",
            ),
        ]

        for key, value in plate_metadata:
            metadata = ET.SubElement(plate, "metadata")
            metadata.set("key", key)
            metadata.set("value", value)

        # Object information
        for obj in slice_info.objects:
            object_elem = ET.SubElement(plate, "object")
            object_elem.set("identify_id", obj.identify_id)
            object_elem.set("name", obj.name)
            object_elem.set("skipped", "true" if obj.skipped else "false")

        # Filament information
        for fil in slice_info.filaments:
            filament_elem = ET.SubElement(plate, "filament")
            filament_elem.set("id", fil.id)
            filament_elem.set("tray_info_idx", fil.tray_info_idx)
            filament_elem.set("type", fil.type)
            filament_elem.set("color", fil.color)
            filament_elem.set("used_m", f"{fil.used_m:.2f}")
            filament_elem.set("used_g", f"{fil.used_g:.2f}")

        # Convert to pretty-printed XML string
        return self._prettify_xml(root)

    def _prettify_xml(self, elem: ET.Element) -> str:
        """
        Return a pretty-printed XML string for the Element.

        Args:
            elem: XML Element to prettify

        Returns:
            Pretty-printed XML string
        """
        rough_string = ET.tostring(elem, encoding="UTF-8")
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ", encoding="UTF-8").decode("UTF-8")
