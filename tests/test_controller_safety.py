"""Safety regression tests for the active NOAH output controller.

No MQTT connection or physical NOAH is used. The coordinator and HA states
are deterministic doubles; the real controller decisions execute unchanged.
"""

from __future__ import annotations

from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
from homeassistant.util import dt as dt_util

from custom_components.noah_optimizer.const import (
    CONTROLLER_PV_REDIRECT,
    CONTROLLER_SOC_HOLD,
    CONTROLLER_SOC_RELEASE,
    CONTROL_STATUS_DISABLED,
    CONTROL_STATUS_RATE_LIMITED,
    DATA_ACTUATOR_AVAILABLE,
    DATA_CONTROLLER_MODE,
    DATA_CRITICAL_DATA_OK,
    DATA_OUTPUT_TARGET,
    OPT_COMMAND_DEADBAND,
    OPT_CONTROL_ENABLED,
    OPT_ENABLED,
)
from custom_components.noah_optimizer.control import NoahOptimizerController


def _controller(
    *,
    actual: float,
    target: float,
    mode: str,
    control_enabled: bool = True,
    critical: bool = True,
) -> NoahOptimizerController:
    state = SimpleNamespace(
        state=str(actual), attributes={"unit_of_measurement": "W"}
    )
    states = {"number.noah_output": state}
    hass = SimpleNamespace(states=SimpleNamespace(get=states.get))
    options = {
        OPT_ENABLED: True,
        OPT_CONTROL_ENABLED: control_enabled,
        OPT_COMMAND_DEADBAND: 50,
    }
    coordinator = SimpleNamespace(
        entry=SimpleNamespace(data={"system_output_power": "number.noah_output"}),
        data={
            DATA_CRITICAL_DATA_OK: critical,
            DATA_ACTUATOR_AVAILABLE: True,
            DATA_OUTPUT_TARGET: target,
            DATA_CONTROLLER_MODE: mode,
        },
        get_option=lambda key: options[key],
        async_update_from_states=AsyncMock(),
        async_update_listeners=Mock(),
    )
    controller = NoahOptimizerController(hass, coordinator)
    controller._async_handle_data_recovered = AsyncMock()
    controller._async_handle_missing_data = AsyncMock()
    controller._async_write_output = AsyncMock(return_value=True)
    return controller


@pytest.mark.asyncio
async def test_reduction_after_pv_redirect_ignores_command_rate_limit() -> None:
    controller = _controller(
        actual=520, target=430, mode=CONTROLLER_SOC_HOLD
    )
    controller._last_command_mode = CONTROLLER_PV_REDIRECT
    controller._last_command_target = 520
    controller._last_command_at = dt_util.utcnow() - timedelta(seconds=5)
    await controller.async_control_tick()
    controller._async_write_output.assert_awaited_once()
    assert controller._async_write_output.await_args.args[0] == 430


@pytest.mark.asyncio
async def test_soc_hold_increase_is_rate_limited() -> None:
    controller = _controller(
        actual=400, target=500, mode=CONTROLLER_SOC_HOLD
    )
    controller._last_command_mode = CONTROLLER_SOC_HOLD
    controller._last_command_target = 400
    controller._last_command_at = dt_util.utcnow() - timedelta(seconds=5)
    await controller.async_control_tick()
    controller._async_write_output.assert_not_awaited()
    assert controller.status == CONTROL_STATUS_RATE_LIMITED


@pytest.mark.asyncio
async def test_pv_redirect_increase_waits_30_seconds() -> None:
    controller = _controller(
        actual=400, target=480, mode=CONTROLLER_PV_REDIRECT
    )
    controller._last_command_mode = CONTROLLER_PV_REDIRECT
    controller._last_command_target = 400
    controller._last_command_at = dt_util.utcnow() - timedelta(seconds=20)
    await controller.async_control_tick()
    controller._async_write_output.assert_not_awaited()
    assert controller.status == CONTROL_STATUS_RATE_LIMITED


@pytest.mark.asyncio
async def test_pv_redirect_increase_allowed_after_30_seconds() -> None:
    controller = _controller(
        actual=400, target=480, mode=CONTROLLER_PV_REDIRECT
    )
    controller._last_command_mode = CONTROLLER_PV_REDIRECT
    controller._last_command_target = 400
    controller._last_command_at = dt_util.utcnow() - timedelta(seconds=35)
    await controller.async_control_tick()
    controller._async_write_output.assert_awaited_once()


@pytest.mark.asyncio
async def test_soc_release_reduction_is_immediate() -> None:
    controller = _controller(
        actual=600, target=500, mode=CONTROLLER_SOC_HOLD
    )
    controller._last_command_mode = CONTROLLER_SOC_RELEASE
    controller._last_command_target = 600
    controller._last_command_at = dt_util.utcnow() - timedelta(seconds=5)
    await controller.async_control_tick()
    controller._async_write_output.assert_awaited_once()


@pytest.mark.asyncio
async def test_disabled_controller_sends_no_commands() -> None:
    controller = _controller(
        actual=520, target=430, mode=CONTROLLER_SOC_HOLD,
        control_enabled=False,
    )
    await controller.async_control_tick()
    controller._async_write_output.assert_not_awaited()
    assert controller.status == CONTROL_STATUS_DISABLED


@pytest.mark.asyncio
async def test_missing_critical_data_never_sends_normal_command() -> None:
    controller = _controller(
        actual=520, target=430, mode=CONTROLLER_SOC_HOLD, critical=False
    )
    await controller.async_control_tick()
    controller._async_handle_missing_data.assert_awaited_once()
    controller._async_write_output.assert_not_awaited()
