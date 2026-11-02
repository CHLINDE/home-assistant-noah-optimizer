"""Unit tests for PV surplus charging, independent of Home Assistant."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


_MODULE_FILE = (
    Path(__file__).resolve().parents[1]
    / "custom_components"
    / "noah_optimizer"
    / "pv_surplus.py"
)
_spec = importlib.util.spec_from_file_location("noah_optimizer_pv_surplus", _MODULE_FILE)
assert _spec is not None and _spec.loader is not None
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)


class PvSurplusTests(unittest.TestCase):
    def test_zero_or_export_never_redirects_charge_to_house(self) -> None:
        for grid_power in (-75.0, 0.0):
            with self.subTest(grid_power=grid_power):
                self.assertEqual(_module.pv_redirect_headroom(grid_power, 130, 10), 0)

    def test_import_below_reserve_does_not_cause_diversion(self) -> None:
        self.assertEqual(_module.pv_redirect_headroom(39, 130, 50), 0)

    def test_import_above_reserve_only_redirects_excess(self) -> None:
        self.assertEqual(_module.pv_redirect_headroom(90, 130, 50), 40)

    def test_redirect_never_exceeds_current_charging(self) -> None:
        self.assertEqual(_module.pv_redirect_headroom(300, 130, 50), 130)

    def test_export_forces_immediate_hold_reduction(self) -> None:
        self.assertEqual(_module.instantaneous_hold_cap(520, -75, 10), 435)

    def test_import_below_reserve_must_not_increase_output(self) -> None:
        self.assertEqual(_module.instantaneous_hold_cap(482, 39, 50), 471)

    def test_positive_average_cannot_override_instantaneous_cap(self) -> None:
        # Even if the old average suggests an output increase to 560 W,
        # SOC-hold can only request 471 W given the current meter reading.
        old_average_target = 560
        cap = _module.instantaneous_hold_cap(482, 39, 50)
        self.assertEqual(min(old_average_target, cap), 471)

    def test_negative_reserve_is_treated_as_zero(self) -> None:
        self.assertEqual(_module.pv_redirect_headroom(39, 130, -10), 39)
        self.assertEqual(_module.instantaneous_hold_cap(482, -75, -10), 407)


if __name__ == "__main__":
    unittest.main()
