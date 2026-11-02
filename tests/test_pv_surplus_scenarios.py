"""Grid and charging scenarios for the revised automatic control math."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


SOURCE = (
    Path(__file__).resolve().parents[1]
    / "custom_components"
    / "noah_optimizer"
    / "pv_surplus.py"
)
spec = importlib.util.spec_from_file_location("pv_surplus_scenarios", SOURCE)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


@pytest.mark.parametrize(
    ("grid", "charge", "reserve", "expected"),
    [
        (-75, 130, 10, 0),  # PV export is never corrected by more output
        (0, 130, 10, 0),  # at balance there is no diversion
        (8, 130, 10, 0),  # small import is left as the safety reserve
        (39, 130, 10, 29),  # only the excess import is redirected
        (39, 130, 50, 0),  # large reserve can suppress diversion
        (90, 130, 10, 80),
        (300, 130, 10, 130),  # never redirect more than current charge
        (300, 0, 10, 0),  # no charging means no diversion
        (300, -10, 10, 0),  # bad telemetry cannot become discharge permission
    ],
)
def test_redirect_power(grid: float, charge: float, reserve: float, expected: float) -> None:
    assert module.pv_redirect_headroom(grid, charge, reserve) == expected


@pytest.mark.parametrize(
    ("out", "grid", "reserve", "expected"),
    [
        (520, -75, 10, 435),  # the reported surplus should go to the battery
        (482, 39, 50, 471),  # do not chase the stale 5-min average
        (520, 0, 10, 510),  # preserve a small grid reserve
        (100, -200, 10, 0),  # output can never be negative
        (800, 80, 20, 860),  # hardware maximum is applied by coordinator
    ],
)
def test_soc_hold_instantaneous_cap(
    out: float, grid: float, reserve: float, expected: float
) -> None:
    assert module.instantaneous_hold_cap(out, grid, reserve) == expected


@pytest.mark.parametrize("grid", [-400, -75, -0.1, 0, 0.1, 9, 10, 11, 75, 400])
@pytest.mark.parametrize("charging", [0, 25, 130])
def test_redirect_never_creates_discharge(
    grid: float, charging: float
) -> None:
    reserve = 10.0
    diversion = module.pv_redirect_headroom(grid, charging, reserve)
    assert 0 <= diversion <= charging
    assert diversion <= max(grid - reserve, 0)
