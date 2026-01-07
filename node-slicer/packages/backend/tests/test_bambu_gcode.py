"""
Unit tests for Bambu Lab G-Code Generator
"""

import pytest
from src.core.bambu_gcode import (
    BambuGCodeGenerator,
    BambuMetadata,
    BambuPrinterSettings,
    calculate_filament_stats,
)


class TestBambuMetadata:
    """Tests for BambuMetadata dataclass."""

    def test_metadata_creation(self):
        """Test creating metadata with required fields."""
        metadata = BambuMetadata(layer_count=100, print_time_seconds=3661)
        assert metadata.layer_count == 100
        assert metadata.print_time_seconds == 3661
        assert metadata.filament_diameter == 1.75  # Default value

    def test_format_time_hours(self):
        """Test time formatting with hours."""
        metadata = BambuMetadata(layer_count=1, print_time_seconds=3661)
        assert metadata.format_time() == "1h 1m 1s"

    def test_format_time_minutes(self):
        """Test time formatting with minutes only."""
        metadata = BambuMetadata(layer_count=1, print_time_seconds=125)
        assert metadata.format_time() == "2m 5s"

    def test_format_time_seconds(self):
        """Test time formatting with seconds only."""
        metadata = BambuMetadata(layer_count=1, print_time_seconds=45)
        assert metadata.format_time() == "45s"

    def test_metadata_custom_values(self):
        """Test metadata with custom values."""
        metadata = BambuMetadata(
            layer_count=50,
            print_time_seconds=600,
            filament_length_mm=1000.5,
            filament_volume_cm3=2.5,
            filament_weight_g=3.1,
            filament_type="PETG",
        )
        assert metadata.filament_type == "PETG"
        assert metadata.filament_length_mm == 1000.5


class TestBambuPrinterSettings:
    """Tests for BambuPrinterSettings dataclass."""

    def test_settings_defaults(self):
        """Test default printer settings."""
        settings = BambuPrinterSettings()
        assert settings.bed_temp == 60.0
        assert settings.hotend_temp == 210.0
        assert settings.print_speed == 100
        assert settings.relative_e is True

    def test_settings_custom(self):
        """Test custom printer settings."""
        settings = BambuPrinterSettings(
            bed_temp=80.0,
            hotend_temp=250.0,
            print_speed=150,
            relative_e=False,
        )
        assert settings.bed_temp == 80.0
        assert settings.hotend_temp == 250.0
        assert settings.print_speed == 150
        assert settings.relative_e is False


class TestBambuGCodeGenerator:
    """Tests for BambuGCodeGenerator class."""

    def test_initialization(self):
        """Test generator initialization."""
        gen = BambuGCodeGenerator()
        assert gen.metadata is not None
        assert gen.settings is not None

    def test_initialization_with_metadata(self):
        """Test generator initialization with metadata."""
        metadata = BambuMetadata(layer_count=50, print_time_seconds=300)
        gen = BambuGCodeGenerator(metadata=metadata)
        assert gen.metadata.layer_count == 50
        assert gen.metadata.print_time_seconds == 300

    def test_generate_header_basic(self):
        """Test basic header generation."""
        metadata = BambuMetadata(layer_count=100, print_time_seconds=3600)
        gen = BambuGCodeGenerator(metadata=metadata)

        header = gen.generate_header()

        assert "; HEADER_BLOCK_START" in header
        assert "; HEADER_BLOCK_END" in header
        assert "; NodeSlicer" in header
        assert "; total layer number: 100" in header
        assert "1h 0m 0s" in header

    def test_generate_header_with_filament_info(self):
        """Test header generation with filament information."""
        metadata = BambuMetadata(
            layer_count=50,
            print_time_seconds=600,
            filament_length_mm=1500.25,
            filament_volume_cm3=3.5,
            filament_weight_g=4.34,
        )
        gen = BambuGCodeGenerator(metadata=metadata)

        header = gen.generate_header()

        assert "; total filament length [mm]: 1500.25" in header
        assert "; total filament volume [cm^3]: 3.50" in header
        assert "; total filament weight [g]: 4.34" in header

    def test_generate_config_block_default(self):
        """Test config block generation with defaults."""
        gen = BambuGCodeGenerator()
        config = gen.generate_config_block()

        assert "; CONFIG_BLOCK_START" in config
        assert "; CONFIG_BLOCK_END" in config
        assert "; curr_bed_type = Textured PEI Plate" in config
        assert "; use_relative_e_distances = 1" in config

    def test_generate_config_block_custom(self):
        """Test config block generation with custom config."""
        gen = BambuGCodeGenerator()
        custom_config = {
            "custom_setting": "test_value",
            "numeric_setting": 42,
        }
        config = gen.generate_config_block(custom_config)

        assert "; custom_setting = test_value" in config
        assert "; numeric_setting = 42" in config

    def test_generate_starting_procedure(self):
        """Test starting procedure generation."""
        settings = BambuPrinterSettings(
            bed_temp=65.0,
            hotend_temp=220.0,
            aux_fan_enabled=True,
        )
        gen = BambuGCodeGenerator(settings=settings)

        start = gen.generate_starting_procedure()

        assert "; STARTING_PROCEDURE_START" in start
        assert "; STARTING_PROCEDURE_END" in start
        assert "M140 S65" in start  # Bed temp
        assert "M109 S220" in start  # Hotend temp
        assert "G28" in start  # Home
        assert "M106 P2 S255" in start  # Aux fan
        assert "M83" in start  # Relative extrusion

    def test_generate_starting_procedure_absolute_e(self):
        """Test starting procedure with absolute extrusion."""
        settings = BambuPrinterSettings(relative_e=False)
        gen = BambuGCodeGenerator(settings=settings)

        start = gen.generate_starting_procedure()

        assert "M82" in start  # Absolute extrusion
        assert "M83" not in start

    def test_generate_starting_procedure_no_aux_fan(self):
        """Test starting procedure without aux fan."""
        settings = BambuPrinterSettings(aux_fan_enabled=False)
        gen = BambuGCodeGenerator(settings=settings)

        start = gen.generate_starting_procedure()

        assert "M106 P2 S255" not in start

    def test_generate_ending_procedure(self):
        """Test ending procedure generation."""
        settings = BambuPrinterSettings(
            retraction_length=1.0,
            retraction_speed=3500.0,
        )
        gen = BambuGCodeGenerator(settings=settings)

        end = gen.generate_ending_procedure()

        assert "; ENDING_PROCEDURE_START" in end
        assert "; ENDING_PROCEDURE_END" in end
        assert "G1 E-1.0 F3500" in end  # Retraction
        assert "M140 S0" in end  # Turn off bed
        assert "M104 S0" in end  # Turn off hotend
        assert "M84" in end  # Disable motors
        assert "M221 S100" in end  # Reset flow

    def test_generate_progress_update_basic(self):
        """Test basic progress update generation."""
        gen = BambuGCodeGenerator()

        progress = gen.generate_progress_update(50)

        assert progress == "M73 P50 ; update progress"

    def test_generate_progress_update_with_layer(self):
        """Test progress update with layer number."""
        gen = BambuGCodeGenerator()

        progress = gen.generate_progress_update(75, layer=150)

        assert progress == "M73 P75 L150 ; update progress"

    def test_generate_progress_update_invalid_percent(self):
        """Test progress update with invalid percentage."""
        gen = BambuGCodeGenerator()

        with pytest.raises(ValueError, match="Progress percent must be 0-100"):
            gen.generate_progress_update(150)

        with pytest.raises(ValueError, match="Progress percent must be 0-100"):
            gen.generate_progress_update(-10)

    def test_generate_layer_change(self):
        """Test layer change generation."""
        gen = BambuGCodeGenerator()

        layer_change = gen.generate_layer_change(layer=10, z_height=2.5)

        assert "; LAYER_CHANGE" in layer_change
        assert "; Z:2.50" in layer_change
        assert "; LAYER:10" in layer_change

    def test_generate_tool_change_basic(self):
        """Test basic tool change."""
        gen = BambuGCodeGenerator()

        tool_change = gen.generate_tool_change(tool=1)

        assert tool_change == "T1"

    def test_generate_tool_change_with_comment(self):
        """Test tool change with comment."""
        gen = BambuGCodeGenerator()

        tool_change = gen.generate_tool_change(tool=2, comment="Red PLA")

        assert tool_change == "T2 ; Red PLA"

    def test_generate_tool_change_invalid_tool(self):
        """Test tool change with invalid tool number."""
        gen = BambuGCodeGenerator()

        with pytest.raises(ValueError, match="Tool number must be 0-3"):
            gen.generate_tool_change(tool=5)

        with pytest.raises(ValueError, match="Tool number must be 0-3"):
            gen.generate_tool_change(tool=-1)

    def test_generate_filament_change(self):
        """Test complete filament change sequence."""
        gen = BambuGCodeGenerator()

        change = gen.generate_filament_change(tool=1, purge_length=75.0)

        assert "; AMS Filament Change to T1" in change
        assert "T1" in change
        assert "G92 E0" in change
        assert "G1 E75.0 F300" in change  # Purge
        assert "G4 P500" in change  # Dwell

    def test_generate_wait_for_temperature_hotend(self):
        """Test temperature wait for hotend only."""
        gen = BambuGCodeGenerator()

        wait = gen.generate_wait_for_temperature(hotend=230.0)

        assert wait == "M109 S230 ; wait for hotend temperature"

    def test_generate_wait_for_temperature_bed(self):
        """Test temperature wait for bed only."""
        gen = BambuGCodeGenerator()

        wait = gen.generate_wait_for_temperature(bed=70.0)

        assert wait == "M190 S70 ; wait for bed temperature"

    def test_generate_wait_for_temperature_both(self):
        """Test temperature wait for both."""
        gen = BambuGCodeGenerator()

        wait = gen.generate_wait_for_temperature(hotend=250.0, bed=80.0)

        assert "M190 S80" in wait
        assert "M109 S250" in wait

    def test_generate_complete_gcode(self):
        """Test complete G-Code generation."""
        metadata = BambuMetadata(layer_count=10, print_time_seconds=600)
        gen = BambuGCodeGenerator(metadata=metadata)

        body = "G1 X10 Y10 Z0.2 E1.0\nG1 X20 Y20 E2.0"
        complete = gen.generate_complete_gcode(body)

        # Check all major sections are present
        assert "; HEADER_BLOCK_START" in complete
        assert "; CONFIG_BLOCK_START" in complete
        assert "; STARTING_PROCEDURE_START" in complete
        assert "; EXECUTABLE_BLOCK_START" in complete
        assert body in complete
        assert "; EXECUTABLE_BLOCK_END" in complete
        assert "; ENDING_PROCEDURE_START" in complete
        assert "M73 P100" in complete  # Final progress

    def test_generate_complete_gcode_no_progress(self):
        """Test complete G-Code without progress updates."""
        gen = BambuGCodeGenerator()

        body = "G1 X10 Y10"
        complete = gen.generate_complete_gcode(body, include_progress=False)

        assert "M73 P100" not in complete


class TestCalculateFilamentStats:
    """Tests for filament statistics calculation."""

    def test_calculate_filament_stats_basic(self):
        """Test basic filament statistics calculation."""
        gcode = """
        G1 X10 Y10 E5.0
        G1 X20 Y20 E10.0
        G1 X30 Y30 E15.0
        """

        stats = calculate_filament_stats(gcode)

        assert stats["length_mm"] == 30.0
        assert stats["volume_cm3"] > 0
        assert stats["weight_g"] > 0

    def test_calculate_filament_stats_no_extrusion(self):
        """Test stats with no extrusion moves."""
        gcode = """
        G1 X10 Y10 Z5
        G0 X20 Y20
        """

        stats = calculate_filament_stats(gcode)

        assert stats["length_mm"] == 0.0
        assert stats["volume_cm3"] == 0.0
        assert stats["weight_g"] == 0.0

    def test_calculate_filament_stats_custom_diameter(self):
        """Test stats with custom filament diameter."""
        gcode = "G1 E100.0"

        stats_175 = calculate_filament_stats(gcode, filament_diameter=1.75)
        stats_285 = calculate_filament_stats(gcode, filament_diameter=2.85)

        # Larger diameter should give larger volume
        assert stats_285["volume_cm3"] > stats_175["volume_cm3"]

    def test_calculate_filament_stats_custom_density(self):
        """Test stats with custom filament density."""
        gcode = "G1 E100.0"

        stats_pla = calculate_filament_stats(gcode, filament_density=1.24)
        stats_abs = calculate_filament_stats(gcode, filament_density=1.04)

        # Higher density should give heavier weight for same volume
        assert stats_pla["weight_g"] > stats_abs["weight_g"]

    def test_calculate_filament_stats_negative_e(self):
        """Test stats with retraction (negative E) moves."""
        gcode = """
        G1 E50.0
        G1 E-2.0
        G1 E30.0
        """

        stats = calculate_filament_stats(gcode)

        # Should only count positive extrusion
        assert stats["length_mm"] == 80.0

    def test_calculate_filament_stats_realistic_print(self):
        """Test stats with realistic print G-Code."""
        gcode = """
        G92 E0
        G1 X10 Y10 E1.5
        G1 X20 Y10 E3.0
        G1 X20 Y20 E4.5
        G1 E-0.8 ; retract
        G0 X30 Y30
        G1 E0.8 ; unretract
        G1 X40 Y40 E2.3
        """

        stats = calculate_filament_stats(gcode)

        # Total positive extrusion: 1.5 + 3.0 + 4.5 + 0.8 + 2.3 = 12.1
        assert 12.0 <= stats["length_mm"] <= 12.2
        assert stats["volume_cm3"] > 0
        assert stats["weight_g"] > 0


class TestIntegration:
    """Integration tests for complete workflows."""

    def test_complete_workflow(self):
        """Test complete workflow from metadata to G-Code."""
        # Create metadata
        metadata = BambuMetadata(
            layer_count=50,
            print_time_seconds=1800,
            filament_type="PETG",
        )

        # Create settings
        settings = BambuPrinterSettings(
            bed_temp=80.0,
            hotend_temp=240.0,
        )

        # Create generator
        gen = BambuGCodeGenerator(metadata=metadata, settings=settings)

        # Generate G-Code body
        body_lines = []
        for layer in range(5):
            z = layer * 0.2
            body_lines.append(gen.generate_layer_change(layer, z))
            body_lines.append(f"G1 X10 Y10 Z{z:.2f} E1.0")
            body_lines.append(gen.generate_progress_update(layer * 20, layer))

        body = "\n".join(body_lines)

        # Generate complete G-Code
        complete = gen.generate_complete_gcode(body)

        # Verify structure
        assert "; HEADER_BLOCK_START" in complete
        assert "; filament_type: PETG" in complete
        assert "M140 S80" in complete
        assert "M109 S240" in complete
        assert all(f"; LAYER:{i}" in complete for i in range(5))
        assert "; ENDING_PROCEDURE_START" in complete

    def test_ams_multi_material_workflow(self):
        """Test AMS multi-material printing workflow."""
        gen = BambuGCodeGenerator()

        body_lines = [
            "; Layer 1 - Tool 0 (Base layer)",
            gen.generate_tool_change(0, "White PLA"),
            "G1 X10 Y10 Z0.2 E5.0",
            "",
            "; Layer 2 - Tool 1 (Detail layer)",
            gen.generate_filament_change(1, purge_length=60.0),
            "G1 X15 Y15 Z0.4 E3.0",
            "",
            "; Layer 3 - Back to Tool 0",
            gen.generate_filament_change(0, purge_length=60.0),
            "G1 X20 Y20 Z0.6 E5.0",
        ]

        body = "\n".join(body_lines)
        complete = gen.generate_complete_gcode(body)

        # Verify tool changes are present
        assert "T0 ; White PLA" in complete
        assert "AMS Filament Change to T1" in complete
        assert "AMS Filament Change to T0" in complete
        assert complete.count("G92 E0") >= 4  # Purge sequences
