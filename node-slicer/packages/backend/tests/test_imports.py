"""
Smoke tests for critical imports.

These tests verify that all critical dependencies can be imported successfully.
"""

import pytest


def test_import_fastapi():
    """Test FastAPI import."""
    import fastapi

    assert fastapi.__version__


def test_import_uvicorn():
    """Test uvicorn import."""
    import uvicorn

    assert uvicorn


def test_import_websockets():
    """Test websockets import."""
    import websockets

    assert websockets


def test_import_pydantic():
    """Test pydantic import."""
    import pydantic

    assert pydantic.__version__


def test_import_lib3mf():
    """Test lib3mf import."""
    import lib3mf

    # Get wrapper and create a model to verify it works
    wrapper = lib3mf.get_wrapper()
    model = wrapper.CreateModel()
    assert wrapper is not None
    assert model is not None


def test_import_fullcontrol():
    """Test FullControl import."""
    import fullcontrol

    assert fullcontrol


def test_import_fullcontrol_point():
    """Test FullControl Point import."""
    from fullcontrol import Point

    # Create a simple point to verify it works
    point = Point(x=1, y=2, z=3)
    assert point.x == 1
    assert point.y == 2
    assert point.z == 3


def test_import_fullcontrol_gcode():
    """Test FullControl G-code module."""
    from fullcontrol.gcode import Point as GcodePoint

    point = GcodePoint(x=10, y=20, z=5)
    assert point.x == 10


def test_import_numpy():
    """Test numpy import (FullControl dependency)."""
    import numpy as np

    assert np.__version__


def test_import_plotly():
    """Test plotly import (FullControl dependency)."""
    import plotly

    assert plotly.__version__
