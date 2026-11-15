"""Pruebas de las series numéricas y fractales.
Ejecutar: python -m pytest tests/"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared import series, protocol  # noqa: E402

def test_geometric_partial_sums():
    assert series.geometric_partial_sums(1, 0.7, 3) == pytest.approx([1.0, 1.7, 2.19])

def test_sierpinski_stats():
    stats = series.sierpinski_stats(3)
    assert [s["piezas"] for s in stats] == [1, 3, 9, 27]
    assert stats[1]["area_pieza"] == pytest.approx(0.25)

def test_koch_perimeter_grows():
    assert series.koch_stats(0)["perimetro"] == pytest.approx(3.0)
    assert series.koch_stats(1)["perimetro"] == pytest.approx(4.0)
    assert series.koch_stats(1)["lados"] == 12

def test_dragon_length():
    for n in range(1, 6):
        assert len(series.dragon_turns(n)) == 2 ** n - 1

def test_mandelbrot_inside_and_outside():
    assert series.mandelbrot_escape(0j, 50) == 50          # dentro del conjunto
    assert series.mandelbrot_escape(2 + 2j, 50) < 50       # fuera del conjunto

def test_julia_bounded_point():
    assert series.julia_escape(0j, 0j, 30) == 30

def test_lorenz_step_moves():
    x, y, z = series.lorenz_step(1.0, 1.0, 1.0, 10.0, 28.0, 2.67, 0.005)
    assert (x, y, z) != (1.0, 1.0, 1.0)

def test_protocol_roundtrip():
    msg = {"type": "param", "key": "zoom", "value": 2.5}
    assert protocol.decode(protocol.encode(msg).strip()) == msg
