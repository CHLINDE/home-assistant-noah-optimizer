"""Coordinator regression scenarios using synthetic HA states, never real hardware."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from custom_components.noah_optimizer.const import (
    CONF_BATTERY_SOC,
    CONF_CHARGING_POWER,
    CONF_DISCHARGE_POWER,
    CONF_FORECAST_REMAINING,
    CONF_GRID_POWER,
    CONF_OUTPUT_POWER,
    CONF_SOLAR_POWER,
    CONF_SYSTEM_OUTPUT_POWER,
    CONTROLLER_PV_REDIRECT,
    CONTROLLER_SOC_HOLD,
    DATA_CONTROLLER_MODE,
    DATA_GRID_EXPORT,
    DATA_GRID_IMPORT,
    DATA_OUTPUT_TARGET,
    OPT_COMMAND_STEP,
    OPT_DYNAMIC_SOC_ENABLED,
    OPT_ENABLED,
    OPT_GRID_RESERVE,
    OPT_MAX_OUTPUT,
    OPT_MODE,
    OPT_SOC_RELEASE_ENABLED,
    MODE_AUTOMATIC,
)
from custom_components.noah_optimizer.coordinator import NoahOptimizerCoordinator


def _state(value: float, unit: str) -> SimpleNamespace:
    return SimpleNamespace(state=str(value), attributes={"unit_of_measurement": unit})


def _fake_coordinator(
    monkeypatch: pytest.MonkeyPatch,
    *,
    grid: float,
    pv: float = 616,
    output: float = 520,
    charging: float = 130,
    reserve: float = 10,
    grid_average: float = 120,
) -> NoahOptimizerCoordinator:
    """Exercise the real coordinator formula and mode selection with mock inputs."""
    entities = {
        "sensor.grid": _state(grid, "W"),
        "sensor.pv": _state(pv, "W"),
        "sensor.output": _state(output, "W"),
        "sensor.soc": _state(76, "%"),
        "sensor.charging": _state(charging, "W"),
        "sensor.discharging": _state(0, "W"),
        "sensor.forecast": _state(0.832, "kWh"),
        "number.target": _state(output, "W"),
    }
    keys = {
        CONF_GRID_POWER: "sensor.grid",
        CONF_SOLAR_POWER: "sensor.pv",
        CONF_OUTPUT_POWER: "sensor.output",
        CONF_BATTERY_SOC: "sensor.soc",
        CONF_CHARGING_POWER: "sensor.charging",
        CONF_DISCHARGE_POWER: "sensor.discharging",
        CONF_FORECAST_REMAINING: "sensor.forecast",
        CONF_SYSTEM_OUTPUT_POWER: "number.target",
    }
    options = {
        OPT_ENABLED: True,
        OPT_MODE: MODE_AUTOMATIC,
        OPT_DYNAMIC_SOC_ENABLED: True,
        OPT_SOC_RELEASE_ENABLED: False,
        OPT_COMMAND_STEP: 10,
        OPT_MAX_OUTPUT: 800,
        OPT_GRID_RESERVE: reserve,
    }
    coordinator = object.__new__(NoahOptimizerCoordinator)
    coordinator.hass = SimpleNamespace(states=SimpleNamespace(get=entities.get))
    coordinator.entry = SimpleNamespace(data=keys, options=options)
    coordinator.pv_learning = SimpleNamespace(
        factor=1.0,
        ready=False,
        last_ratio=None,
        sample_count=0,
        actual_pv_today_kwh=0.0,
        forecast_reference_kwh=None,
        async_update=AsyncMock(),
    )
    coordinator.history = SimpleNamespace(async_record_forecast_snapshot=AsyncMock())
    monkeypatch.setattr(coordinator, "_daylight_progress", lambda: 0.6)
    monkeypatch.setattr(coordinator, "_is_night", lambda _: False)
    monkeypatch.setattr(coordinator, "_hours_to_sunset", lambda: 3.5)
    monkeypatch.setattr(coordinator, "_build_forecast_curve", lambda **_: None)
    monkeypatch.setattr(coordinator, "_update_grid_average", lambda _: grid_average)
    # An already-satisfied dynamic target, but well short of final target SOC.
    monkeypatch.setattr(
        coordinator,
        "_dynamic_soc_values",
        lambda **_: (60.5, 15.5, "ahead", 0.0, 55.0, 70.0, 0.12),
    )
    return coordinator


@pytest.mark.asyncio
async def test_export_while_ahead_of_schedule_reduces_output(monkeypatch) -> None:
    coordinator = _fake_coordinator(monkeypatch, grid=-75, reserve=10)
    data = await coordinator._async_update_data()
    assert data[DATA_CONTROLLER_MODE] == CONTROLLER_SOC_HOLD
    assert data[DATA_GRID_EXPORT] == 75
    assert data[DATA_GRID_IMPORT] == 0
    assert data[DATA_OUTPUT_TARGET] == 430  # 520 - 75 - 10, floored to 10 W


@pytest.mark.asyncio
async def test_old_grid_average_cannot_increase_output(monkeypatch) -> None:
    coordinator = _fake_coordinator(
        monkeypatch, grid=39, output=482, reserve=50, grid_average=200
    )
    data = await coordinator._async_update_data()
    assert data[DATA_CONTROLLER_MODE] == CONTROLLER_SOC_HOLD
    assert data[DATA_OUTPUT_TARGET] == 470


@pytest.mark.asyncio
async def test_charging_redirect_respects_grid_reserve(monkeypatch) -> None:
    coordinator = _fake_coordinator(
        monkeypatch, grid=90, output=450, charging=130, reserve=50
    )
    data = await coordinator._async_update_data()
    assert data[DATA_CONTROLLER_MODE] == CONTROLLER_PV_REDIRECT
    assert data[DATA_OUTPUT_TARGET] == 490  # 450 + (90 - 50)


@pytest.mark.asyncio
async def test_when_no_battery_charge_does_not_redirect(monkeypatch) -> None:
    coordinator = _fake_coordinator(
        monkeypatch, grid=90, output=450, charging=0, reserve=50
    )
    data = await coordinator._async_update_data()
    assert data[DATA_CONTROLLER_MODE] == CONTROLLER_SOC_HOLD
    assert data[DATA_OUTPUT_TARGET] <= 450
