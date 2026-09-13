"""Coordinator wrapper that blocks NOAH source updates while offline."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timedelta
from typing import Any

from homeassistant.util import dt as dt_util

from .const import (
    CONF_BATTERY_SOC,
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
    OPT_SOC_RELEASE_ENABLED,
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

        # Intraday plan rebasing is triggered only by a changed native
        # Forecast.Solar power curve. Normal coordinator refreshes must not
        # continuously move the plan anchor to the current SOC.
        self._forecast_plan_source_signature: (
            tuple[float | None, tuple[tuple[float, float], ...]] | None
        ) = None
        self._forecast_plan_anchor_at: datetime | None = None
        self._forecast_plan_anchor_soc: float | None = None

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

    @staticmethod
    def _forecast_source_signature(
        curve: ForecastCurveData,
    ) -> tuple[float | None, tuple[tuple[float, float], ...]]:
        """Return a signature for a genuine Forecast.Solar update.

        The source entity timestamp identifies a new Forecast.Solar refresh,
        while the power points also catch native runtime-curve changes. Normal
        NOAH coordinator refreshes leave both values unchanged and therefore do
        not continuously move the SOC-plan anchor.
        """
        updated_at = (
            curve.updated_at.timestamp()
            if curve.updated_at is not None
            else None
        )
        points = tuple(
            (
                timestamp.timestamp(),
                round(float(power), 3),
            )
            for timestamp, power in curve.raw_power
        )
        return updated_at, points

    @staticmethod
    def _forecast_power_at(
        points: tuple[tuple[datetime, float], ...],
        at: datetime,
    ) -> float:
        """Interpolate forecast power at the plan anchor timestamp."""
        if not points:
            return 0.0
        if at <= points[0][0]:
            return 0.0
        if at >= points[-1][0]:
            return 0.0

        previous_time, previous_power = points[0]
        for current_time, current_power in points[1:]:
            if at <= current_time:
                span = (current_time - previous_time).total_seconds()
                if span <= 0:
                    return max(float(current_power), 0.0)
                fraction = (at - previous_time).total_seconds() / span
                value = previous_power + fraction * (
                    current_power - previous_power
                )
                return max(float(value), 0.0)
            previous_time = current_time
            previous_power = current_power

        return 0.0

    def _rebase_forecast_curve(
        self,
        curve: ForecastCurveData,
        *,
        anchor_at: datetime,
        anchor_soc: float,
        forecast_safety_kwh: float,
        battery_capacity_kwh: float,
        efficiency: float,
        min_soc: float,
        target_soc: float,
    ) -> ForecastCurveData:
        """Build the remaining SOC plan from an observed intraday anchor.

        Forecast.Solar keeps forecast values for already elapsed periods in its
        complete daily runtime curve. A full-day SOC schedule therefore assumes
        that all forecast energy from the morning actually occurred. On every
        genuinely changed native forecast curve, start the actionable part of
        the schedule at the current measured SOC and integrate only forecast PV
        that still lies ahead of the anchor.
        """
        minimum = float(min_soc)
        target = max(float(target_soc), minimum)
        anchor_soc = min(max(float(anchor_soc), minimum), target)
        capacity = max(float(battery_capacity_kwh), 0.001)
        safe_efficiency = max(float(efficiency), 0.1)

        effective_points = tuple(curve.effective_power)
        anchor_power = self._forecast_power_at(effective_points, anchor_at)
        future_points: list[tuple[datetime, float]] = [
            (anchor_at, anchor_power)
        ]
        future_points.extend(
            (timestamp, max(float(power), 0.0))
            for timestamp, power in effective_points
            if timestamp > anchor_at
        )

        cumulative: list[tuple[datetime, float]] = [(anchor_at, 0.0)]
        cumulative_kwh = 0.0
        previous_time, previous_power = future_points[0]
        for current_time, current_power in future_points[1:]:
            delta_hours = (
                current_time - previous_time
            ).total_seconds() / 3600.0
            if 0 < delta_hours <= 2.0:
                cumulative_kwh += (
                    (previous_power + current_power)
                    / 2.0
                    * delta_hours
                    / 1000.0
                )
            cumulative.append((current_time, cumulative_kwh))
            previous_time = current_time
            previous_power = current_power

        total_input_kwh = cumulative[-1][1]
        total_storable_kwh = total_input_kwh * safe_efficiency
        safe_input_kwh = max(
            total_input_kwh - max(float(forecast_safety_kwh), 0.0),
            0.0,
        )
        usable_storable_kwh = safe_input_kwh * safe_efficiency

        usable_scale = (
            usable_storable_kwh / total_storable_kwh
            if total_storable_kwh > 0
            else 0.0
        )
        max_needed_kwh = capacity * max(target - anchor_soc, 0.0) / 100.0
        usable_for_plan_kwh = min(usable_storable_kwh, max_needed_kwh)
        target_scale = (
            usable_for_plan_kwh / usable_storable_kwh
            if usable_storable_kwh > 0
            else 0.0
        )

        future_soc_plan: list[tuple[datetime, float]] = []
        for timestamp, cumulative_input_kwh in cumulative:
            cumulative_storable_kwh = (
                cumulative_input_kwh
                * safe_efficiency
                * usable_scale
                * target_scale
            )
            soc_gain = cumulative_storable_kwh / capacity * 100.0
            planned_soc = min(
                max(anchor_soc + soc_gain, minimum),
                target,
            )
            future_soc_plan.append((timestamp, planned_soc))

        # Keep already established plan history visible in the newest snapshot.
        # Only the actionable future section is replaced by the new anchor and
        # remaining forecast. This makes intraday forecast corrections visible
        # in the historical plan instead of rewriting the past.
        prefix: list[tuple[datetime, float]] = []
        previous_curve = self._last_forecast_curve
        if previous_curve is not None and previous_curve.soc_plan:
            anchor_day = dt_util.as_local(anchor_at).date()
            previous_day = dt_util.as_local(
                previous_curve.soc_plan[0][0]
            ).date()
            if previous_day == anchor_day:
                prefix = [
                    (timestamp, value)
                    for timestamp, value in previous_curve.soc_plan
                    if timestamp < anchor_at
                ]

        soc_plan = tuple(prefix + future_soc_plan)
        planned_end_soc = (
            future_soc_plan[-1][1]
            if future_soc_plan
            else anchor_soc
        )

        return ForecastCurveData(
            updated_at=curve.updated_at,
            raw_power=curve.raw_power,
            effective_power=curve.effective_power,
            soc_plan=soc_plan,
            raw_day_energy_kwh=curve.raw_day_energy_kwh,
            effective_day_energy_kwh=curve.effective_day_energy_kwh,
            planned_end_soc=planned_end_soc,
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
        """Build a rebased plan and bridge short Forecast.Solar gaps."""
        signature = self._forecast_curve_signature(
            effective_factor=effective_factor,
            forecast_safety_kwh=forecast_safety_kwh,
            battery_capacity_kwh=battery_capacity_kwh,
            efficiency=efficiency,
            min_soc=min_soc,
            target_soc=target_soc,
        )

        native_curve = super()._build_forecast_curve(
            effective_factor=effective_factor,
            forecast_safety_kwh=forecast_safety_kwh,
            battery_capacity_kwh=battery_capacity_kwh,
            efficiency=efficiency,
            min_soc=min_soc,
            target_soc=target_soc,
        )

        now = dt_util.utcnow()
        if native_curve is not None:
            source_signature = self._forecast_source_signature(native_curve)
            anchor_day_changed = (
                self._forecast_plan_anchor_at is None
                or dt_util.as_local(self._forecast_plan_anchor_at).date()
                != dt_util.now().date()
            )
            source_changed = (
                self._forecast_plan_source_signature != source_signature
            )

            if source_changed or anchor_day_changed:
                current_soc = self._read_soc(
                    self.entry.data[CONF_BATTERY_SOC]
                )
                if current_soc is not None:
                    self._forecast_plan_anchor_at = now
                    self._forecast_plan_anchor_soc = current_soc
                    self._forecast_plan_source_signature = source_signature

            anchor_at = self._forecast_plan_anchor_at
            anchor_soc = self._forecast_plan_anchor_soc

            if anchor_at is not None and anchor_soc is not None:
                curve = self._rebase_forecast_curve(
                    native_curve,
                    anchor_at=anchor_at,
                    anchor_soc=anchor_soc,
                    forecast_safety_kwh=forecast_safety_kwh,
                    battery_capacity_kwh=battery_capacity_kwh,
                    efficiency=efficiency,
                    min_soc=min_soc,
                    target_soc=target_soc,
                )
            else:
                # SOC may be temporarily unavailable during startup. Keep the
                # native plan until a valid observed SOC can establish the
                # first intraday anchor; active control is blocked separately
                # by the normal critical-data checks.
                curve = native_curve

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
            bool(self.get_option(OPT_SOC_RELEASE_ENABLED))
            and previous_mode == CONTROLLER_SOC_RELEASE
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
