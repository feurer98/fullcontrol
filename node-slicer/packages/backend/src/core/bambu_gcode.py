"""
Bambu Lab G-Code Generator

This module provides Bambu Lab specific G-Code generation features including
headers, footers, AMS tool changes, and progress reporting.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime


@dataclass
class BambuMetadata:
    """Metadata for Bambu Lab G-Code header."""

    # Required fields
    layer_count: int
    print_time_seconds: int

    # Filament info
    filament_length_mm: float = 0.0
    filament_volume_cm3: float = 0.0
    filament_weight_g: float = 0.0
    filament_density: float = 1.24  # Default PLA density
    filament_diameter: float = 1.75

    # Printer info
    max_z_height: float = 250.0
    nozzle_diameter: float = 0.4

    # Additional metadata
    generator_name: str = "NodeSlicer"
    generator_version: str = "0.1.0"
    filament_type: str = "PLA"
    filament_vendor: str = "Generic"

    def format_time(self) -> str:
        """Format print time as human-readable string."""
        hours = self.print_time_seconds // 3600
        minutes = (self.print_time_seconds % 3600) // 60
        seconds = self.print_time_seconds % 60

        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"


@dataclass
class BambuPrinterSettings:
    """Bambu Lab printer settings."""

    # Temperature settings
    bed_temp: float = 60.0
    hotend_temp: float = 210.0

    # Speed settings
    print_speed: int = 100  # Percentage
    travel_speed: float = 500.0
    material_flow: int = 100  # Percentage

    # Fan settings
    fan_speed: int = 100  # Percentage
    aux_fan_enabled: bool = True

    # Retraction settings
    retraction_length: float = 0.8
    retraction_speed: float = 3000.0

    # Other settings
    relative_e: bool = True
    z_hop: float = 0.4


class BambuGCodeGenerator:
    """
    Bambu Lab G-Code Generator.

    Provides methods to generate Bambu Lab specific G-Code including headers,
    footers, progress reporting, and AMS tool changes.
    """

    def __init__(self, metadata: Optional[BambuMetadata] = None,
                 settings: Optional[BambuPrinterSettings] = None):
        """
        Initialize the Bambu Lab G-Code generator.

        Args:
            metadata: Print metadata for header generation
            settings: Printer settings for start/end procedures
        """
        self.metadata = metadata or BambuMetadata(layer_count=0, print_time_seconds=0)
        self.settings = settings or BambuPrinterSettings()

    def generate_header(self) -> str:
        """
        Generate Bambu Lab G-Code header block.

        Returns:
            Header block as string with metadata
        """
        header_lines = [
            "; HEADER_BLOCK_START",
            f"; {self.metadata.generator_name} {self.metadata.generator_version}",
            f"; Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"; model printing time: {self.metadata.format_time()}",
            f"; total layer number: {self.metadata.layer_count}",
        ]

        # Add filament info if available
        if self.metadata.filament_length_mm > 0:
            header_lines.extend([
                f"; total filament length [mm]: {self.metadata.filament_length_mm:.2f}",
                f"; total filament volume [cm^3]: {self.metadata.filament_volume_cm3:.2f}",
                f"; total filament weight [g]: {self.metadata.filament_weight_g:.2f}",
            ])

        header_lines.extend([
            f"; filament_density: {self.metadata.filament_density}",
            f"; filament_diameter: {self.metadata.filament_diameter}",
            f"; filament_type: {self.metadata.filament_type}",
            f"; nozzle_diameter: {self.metadata.nozzle_diameter}",
            f"; max_z_height: {self.metadata.max_z_height}",
            "; HEADER_BLOCK_END",
            "",
        ])

        return "\n".join(header_lines)

    def generate_config_block(self, config: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate Bambu Lab config block with slicer settings.

        Args:
            config: Optional configuration dictionary

        Returns:
            Config block as string
        """
        if not config:
            config = {
                "curr_bed_type": "Textured PEI Plate",
                "default_filament_profile": f"Generic {self.metadata.filament_type}",
                "filament_type": self.metadata.filament_type,
                "filament_vendor": self.metadata.filament_vendor,
                "nozzle_diameter": self.metadata.nozzle_diameter,
                "enable_arc_fitting": 1,
                "use_relative_e_distances": 1 if self.settings.relative_e else 0,
            }

        config_lines = ["; CONFIG_BLOCK_START"]

        for key, value in sorted(config.items()):
            config_lines.append(f"; {key} = {value}")

        config_lines.extend([
            "; CONFIG_BLOCK_END",
            "",
        ])

        return "\n".join(config_lines)

    def generate_starting_procedure(self) -> str:
        """
        Generate Bambu Lab starting procedure (based on bambulab_x1.py).

        Returns:
            Starting G-Code procedure as string
        """
        lines = [
            "; STARTING_PROCEDURE_START",
            "",
            "; Heat bed and nozzle",
            f"M140 S{self.settings.bed_temp:.0f} ; set bed temp",
            f"M104 S150 ; preheat nozzle to 150C",
            f"M190 S{self.settings.bed_temp:.0f} ; wait for bed temp",
            "M109 S150 ; wait for nozzle preheat",
            "",
            "; Home and level",
            "G28 ; home all axes (includes mesh bed leveling)",
            "",
            "; Set coordinate systems",
            "G90 ; absolute positioning",
            "G21 ; set units to millimeters",
        ]

        if self.settings.relative_e:
            lines.append("M83 ; extruder relative mode")
        else:
            lines.append("M82 ; extruder absolute mode")

        lines.extend([
            "",
            "; Set fans",
            f"M106 S{int(self.settings.fan_speed * 2.55)} ; set part cooling fan",
        ])

        if self.settings.aux_fan_enabled:
            lines.append("M106 P2 S255 ; enable auxiliary fan")

        lines.extend([
            "",
            "; Offset print to avoid filament cutting area",
            "G1 X20 Y20 Z10 F3000",
            "G92 X0 Y0 ; set offset",
            "G1 X5 Y5 Z10 F3000",
            "",
            "; Heat to printing temperature",
            f"M109 S{self.settings.hotend_temp:.0f} ; wait for hotend temp",
            "",
            "; Prime nozzle",
            "G92 E0 ; reset extruder",
            "G1 E50 F250 ; prime 50mm",
            "G92 E0 ; reset extruder",
            "",
            "; Move to start position",
            "G1 Z50 F8000 ; lift nozzle",
            f"G1 X10 Y10 F{self.settings.travel_speed:.0f} ; move to start",
            "G1 Z0.3 F1000 ; lower to first layer",
            "",
            "; Set speed overrides",
            f"M220 S{self.settings.print_speed} ; set speed factor",
            f"M221 S{self.settings.material_flow} ; set flow factor",
            "",
            "; STARTING_PROCEDURE_END",
            "",
        ])

        return "\n".join(lines)

    def generate_ending_procedure(self) -> str:
        """
        Generate Bambu Lab ending procedure (based on bambulab_x1.py).

        Returns:
            Ending G-Code procedure as string
        """
        lines = [
            "",
            "; ENDING_PROCEDURE_START",
            "",
            "; Retract and lift",
            "M83 ; relative extrusion",
            f"G1 E-{self.settings.retraction_length:.1f} F{self.settings.retraction_speed:.0f} ; retract",
            "G91 ; relative positioning",
            "G1 Z20 F8000 ; drop bed 20mm",
            "G90 ; absolute positioning",
            "",
            "; Turn off heaters and fans",
            "M140 S0 ; turn off bed",
            "M104 S0 ; turn off hotend",
            "M106 S0 ; turn off part cooling fan",
        ]

        if self.settings.aux_fan_enabled:
            lines.append("M106 P2 S0 ; turn off auxiliary fan")

        lines.extend([
            "",
            "; Reset overrides",
            "M220 S100 ; reset speed factor",
            "M221 S100 ; reset flow factor",
            "M900 K0 ; reset linear advance",
            "",
            "; Disable motors",
            "M84 ; disable all steppers",
            "",
            "; ENDING_PROCEDURE_END",
        ])

        return "\n".join(lines)

    def generate_progress_update(self, percent: int, layer: Optional[int] = None) -> str:
        """
        Generate progress update G-Code (M73).

        Args:
            percent: Progress percentage (0-100)
            layer: Optional current layer number

        Returns:
            Progress update G-Code command
        """
        if not 0 <= percent <= 100:
            raise ValueError(f"Progress percent must be 0-100, got {percent}")

        if layer is not None:
            return f"M73 P{percent} L{layer} ; update progress"
        return f"M73 P{percent} ; update progress"

    def generate_layer_change(self, layer: int, z_height: float) -> str:
        """
        Generate layer change notification.

        Args:
            layer: Layer number
            z_height: Z height for this layer

        Returns:
            Layer change comment
        """
        return f"; LAYER_CHANGE\n; Z:{z_height:.2f}\n; LAYER:{layer}"

    def generate_tool_change(self, tool: int, comment: Optional[str] = None) -> str:
        """
        Generate AMS tool change command (T-code).

        Args:
            tool: Tool number (0-3 for AMS)
            comment: Optional comment describing the tool

        Returns:
            Tool change G-Code
        """
        if not 0 <= tool <= 3:
            raise ValueError(f"Tool number must be 0-3 for AMS, got {tool}")

        if comment:
            return f"T{tool} ; {comment}"
        return f"T{tool}"

    def generate_filament_change(self, tool: int, purge_length: float = 50.0) -> str:
        """
        Generate complete filament change sequence for AMS.

        Args:
            tool: Target tool number (0-3)
            purge_length: Amount of filament to purge (mm)

        Returns:
            Complete filament change G-Code sequence
        """
        lines = [
            f"; AMS Filament Change to T{tool}",
            f"T{tool} ; switch to tool {tool}",
            "G92 E0 ; reset extruder",
            f"G1 E{purge_length:.1f} F300 ; purge filament",
            "G92 E0 ; reset extruder",
            "G4 P500 ; dwell 500ms",
        ]

        return "\n".join(lines)

    def generate_wait_for_temperature(self, hotend: Optional[float] = None,
                                     bed: Optional[float] = None) -> str:
        """
        Generate temperature wait commands.

        Args:
            hotend: Hotend temperature to wait for
            bed: Bed temperature to wait for

        Returns:
            Temperature wait G-Code commands
        """
        lines = []

        if bed is not None:
            lines.append(f"M190 S{bed:.0f} ; wait for bed temperature")

        if hotend is not None:
            lines.append(f"M109 S{hotend:.0f} ; wait for hotend temperature")

        return "\n".join(lines)

    def generate_complete_gcode(self, body_gcode: str,
                               include_progress: bool = True) -> str:
        """
        Generate complete Bambu Lab G-Code with header, body, and footer.

        Args:
            body_gcode: The main G-Code body (toolpath commands)
            include_progress: Whether to include progress updates

        Returns:
            Complete G-Code file content
        """
        parts = [
            self.generate_header(),
            self.generate_config_block(),
            self.generate_starting_procedure(),
            "; EXECUTABLE_BLOCK_START",
            "",
            body_gcode.strip(),
            "",
            "; EXECUTABLE_BLOCK_END",
            self.generate_ending_procedure(),
        ]

        if include_progress:
            # Add final progress update
            parts.insert(-1, self.generate_progress_update(100))

        return "\n".join(parts)


def calculate_filament_stats(gcode: str, filament_diameter: float = 1.75,
                            filament_density: float = 1.24) -> Dict[str, float]:
    """
    Calculate filament usage statistics from G-Code.

    Args:
        gcode: G-Code content to analyze
        filament_diameter: Filament diameter in mm
        filament_density: Filament density in g/cm³

    Returns:
        Dictionary with filament statistics (length, volume, weight)
    """
    import re

    total_extrusion = 0.0

    # Find all extrusion commands (E parameter)
    for line in gcode.split('\n'):
        # Look for G1 commands with E parameter
        if line.strip().startswith('G1 ') or line.strip().startswith('G0 '):
            # Extract E value
            e_match = re.search(r'E([-+]?\d*\.?\d+)', line)
            if e_match:
                e_value = float(e_match.group(1))
                if e_value > 0:  # Positive E is extrusion
                    total_extrusion += e_value

    # Calculate volume (cylinder volume = π * r² * length)
    radius_mm = filament_diameter / 2
    volume_mm3 = total_extrusion * 3.14159 * (radius_mm ** 2)
    volume_cm3 = volume_mm3 / 1000

    # Calculate weight
    weight_g = volume_cm3 * filament_density

    return {
        "length_mm": total_extrusion,
        "volume_cm3": volume_cm3,
        "weight_g": weight_g,
    }
