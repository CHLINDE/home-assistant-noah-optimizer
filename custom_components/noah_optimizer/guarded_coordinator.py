"""Coordinator wrapper that blocks NOAH source updates while offline."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timedelta
from typing import Any

from homeassistant.util import dt as dt_util

from .const import (
    CONTROLLER_OFF,
    CONTROLLER_SOC_HOLD,
    CONTROLLER_SOC_RELEASE,
    DATA_ACTUATOR_AVAILABLE,
    DATA_CONTROLLER_MODE,
    DATA_CRITICAL_DATA_OK,
    DATA_FORECAST_AVAILABLE,
    DATA_GRID_POWER,
    DATA_OUTPUT_POWER,
    DATA_OUTPUT_TARGET,
    DATA_RELEASABLE_BATTERY_ENERGY,
    DATA_SOC,
    DATA_SOC_RELEASE_FLOOR,
    DATA_SOC_RELEASE_TARGET,
    DATA_STATUS,
    OPT_COMMAND_STEP,
    OPT_GRID_RESERVE,
    OPT_MAX_OUTPUT,
    STATUS_ACTUATOR_UNAVAILABLE,
)
from .coordinator import NoahOptimizerCoordinator
from .forecast_curve import ForecastCurveData

# A short Forecast.Solar runtime outage must not replace a valid intraday SOC
# plan with the old daylight fallback. The cache is deliberately bounded and
# never crosses the local calendar day.
FORECAST_CURVE_CACHE_MAX_AGE = timedelta(hours=3)

# Predictive SOC release follows the grid closely. Keep a minimum export band
# so a single small overshoot does not immediately switch back to SOC hold.
SOC_RELEASE_MIN_EXPORT_HYSTERESIS_W = 50.0


class NoahOfflineAwareCoordinator(NoahOptimizerCoordinator):
    """Prevent cached Noah-MQTT data from being consumed while offline."""

    def __init__(self, hass, entry) -> None:
        """Initialize the guarded coordinator."""
        super().__init__(hass, entry)
        self._source_updates_allowed: Callable[[], bool] | None = None

        self._last_forecast_curve: ForecastCurveData | None = None
        self._last_forecast_curve_cached_at: datetime | None = None
        self._last_forecast_curve_signature: tuple[float, ...] | None = None

    def set_source_update_guard(
        self,
        callback: Callable[[], bool],
    ) -> None:
        """Register the synchronous source-data validity check."""
        self._source_updates_allowed = callback

    @staticmethod
    def _forecast_curve_signature(
        *,
        effective_factor: float,
        forecast_safety_kwh: float,
        battery_capacity_kwh: float,
        efficiency: float,
        min_soc: float,
        target_soc: float,
    ) -> tuple[float, ...]:
        """Return the planning parameters that define a forecast SOC curve."""
        return (
            float(effective_factor),
            float(forecast_safety_kwh),
            float(battery_capacity_kwh),
            float(efficiency),
            float(min_soc),
            float(target_soc),
        )

    def _build_forecast_curve(
        self,
        *,
        effective_factor: float,
        forecast_safety_kwh: float,
        battery_capacity_kwh: float,
        efficiency: float,
        min_soc: float,
        target_soc: float,
    ) -> ForecastCurveData | None:
        """Use the last valid same-day Forecast.Solar curve for short gaps."""
        signature = self._forecast_curve_signature(
            effective_factor=effective_factor,
            forecast_safety_kwh=forecast_safety_kwh,
            battery_capacity_kwh=battery_capacity_kwh,
            efficiency=efficiency,
            min_soc=min_soc,
            target_soc=target_soc,
        )

        curve = super()._build_forecast_curve(
            effective_factor=effective_factor,
            forecast_safety_kwh=forecast_safety_kwh,
            battery_capacity_kwh=battery_capacity_kwh,
            efficiency=efficiency,
            min_soc=min_soc,
            target_soc=target_soc,
        )

        now = dt_util.utcnow()
        if curve is not None:
            self._last_forecast_curve = curve
            self._last_forecast_curve_cached_at = now
            self._last_forecast_curve_signature = signature
            return curve

        cached = self._last_forecast_curve
        cached_at = self._last_forecast_curve_cached_at
        if cached is None or cached_at is None:
            return None
        if self._last_forecast_curve_signature != signature:
            return None
        if now - cached_at > FORECAST_CURVE_CACHE_MAX_AGE:
            return None
        if not cached.raw_power:
            return None

        curve_day = dt_util.as_local(cached.raw_power[0][0]).date()
        if curve_day != dt_util.now().date():
            return None

        return cached

    def _offline_snapshot(self) -> dict[str, Any]:
        """Return the last known data marked as unsafe for active control."""
        data = dict(self.data or {})
        data[DATA_CRITICAL_DATA_OK] = False
        data[DATA_ACTUATOR_AVAILABLE] = False
        data[DATA_OUTPUT_TARGET] = None
        data[DATA_CONTROLLER_MODE] = CONTROLLER_OFF
        data[DATA_STATUS] = STATUS_ACTUATOR_UNAVAILABLE
        return data

    def _apply_soc_release_hysteresis(
        self,
        data: dict[str, Any],
        previous_mode: str | None,
    ) -> dict[str, Any]:
        """Prevent SOC release / SOC hold oscillation around zero grid power."""
        if not data.get(DATA_CRITICAL_DATA_OK, False):
            return data
        if not data.get(DATA_FORECAST_AVAILABLE, False):
            return data

        mode = str(data.get(DATA_CONTROLLER_MODE, ""))
        if mode not in {CONTROLLER_SOC_RELEASE, CONTROLLER_SOC_HOLD}:
            return data

        try:
            grid_power = float(data[DATA_GRID_POWER])
            output_power = float(data[DATA_OUTPUT_POWER])
            soc = float(data[DATA_SOC])
            release_floor = float(data[DATA_SOC_RELEASE_FLOOR])
            releasable_energy = float(data[DATA_RELEASABLE_BATTERY_ENERGY])
            command_step = float(self.get_option(OPT_COMMAND_STEP))
            grid_reserve = max(float(self.get_option(OPT_GRID_RESERVE)), 0.0)
            max_output = float(self.get_option(OPT_MAX_OUTPUT))
        except (KeyError, TypeError, ValueError):
            return data

        # Always expose the zero-grid target while release is eligible. Unlike
        # the old target, signed grid power also corrects a small overshoot.
        release_target = round(
            self._round_to_step(
                output_power + grid_power,
                command_step,
                max_output,
            )
        )
        data[DATA_SOC_RELEASE_TARGET] = release_target

        release_headroom = (
            soc > release_floor
            and releasable_energy > 0.0
        )

        # Entry behavior stays backward-compatible: the base coordinator enters
        # predictive release on positive grid import. The hysteresis is applied
        # on exit so a tiny export overshoot does not immediately switch modes.
        # Once release is active, keep it latched across a small export
        # overshoot. The target continues to follow signed grid power back
        # toward zero instead of immediately jumping to the SOC-hold target.
        export_hysteresis = max(
            SOC_RELEASE_MIN_EXPORT_HYSTERESIS_W,
            grid_reserve,
            max(command_step, 0.0) * 2.0,
        )
        retain_release = (
            previous_mode == CONTROLLER_SOC_RELEASE
            and mode == CONTROLLER_SOC_HOLD
            and release_headroom
            and grid_power >= -export_hysteresis
        )

        if mode == CONTROLLER_SOC_RELEASE or retain_release:
            data[DATA_CONTROLLER_MODE] = CONTROLLER_SOC_RELEASE
            data[DATA_OUTPUT_TARGET] = release_target

        return data

    async def _async_update_data(self) -> dict[str, Any]:
        """Update only if the NOAH connectivity state is valid."""
        if (
            self._source_updates_allowed is not None
            and not self._source_updates_allowed()
        ):
            return self._offline_snapshot()

        previous_mode = None
        if self.data:
            previous_mode = str(self.data.get(DATA_CONTROLLER_MODE, "")) or None

        data = await super()._async_update_data()
        return self._apply_soc_release_hysteresis(data, previous_mode)
