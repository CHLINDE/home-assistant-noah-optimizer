"""Coordinator integration checks for offline SOC safety."""

from __future__ import annotations

from types import SimpleNamespace

from custom_components.noah_optimizer.const import (
    CONF_GRID_POWER,
    DATA_ACTUATOR_AVAILABLE,
    DATA_CRITICAL_DATA_OK,
    DATA_OUTPUT_TARGET,
    DATA_SOC,
    DATA_SOC_DEVIATION,
    DATA_STATUS,
    STATUS_EXPECTED_NIGHT_SHUTDOWN,
)
from custom_components.noah_optimizer.guarded_coordinator import (
    NoahOfflineAwareCoordinator,
)
from custom_components.noah_optimizer.soc_guard import SocZeroGuard


def test_offline_snapshot_has_no_live_soc_or_control_target():
    coordinator = object.__new__(NoahOfflineAwareCoordinator)
    coordinator._soc_guard = SocZeroGuard(last_trusted_soc=10.0)
    coordinator.data = {
        DATA_SOC: 10.0,
        DATA_SOC_DEVIATION: 0.0,
        DATA_OUTPUT_TARGET: 300,
        DATA_CRITICAL_DATA_OK: True,
    }
    coordinator.entry = SimpleNamespace(data={CONF_GRID_POWER: "sensor.grid"})
    coordinator._read_power_w = lambda _entity: 447
    coordinator.controller = SimpleNamespace(expected_night_shutdown=True)

    snapshot = coordinator._offline_snapshot()

    assert snapshot[DATA_SOC] is None
    assert snapshot[DATA_SOC_DEVIATION] is None
    assert snapshot[DATA_OUTPUT_TARGET] is None
    assert snapshot[DATA_CRITICAL_DATA_OK] is False
    assert snapshot[DATA_ACTUATOR_AVAILABLE] is False
    assert snapshot[DATA_STATUS] == STATUS_EXPECTED_NIGHT_SHUTDOWN
    assert coordinator.last_trusted_soc == 10.0
