"""Forecast.Solar curve helpers for the Growatt NOAH Optimizer."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Iterable, Mapping

from homeassistant.util import dt as dt_util


@dataclass(frozen=True)
class ForecastCurveData:
    """Normalized Forecast.Solar curve and derived charging schedule."""

    updated_at: datetime | None
    raw_power: tuple[tuple[datetime, float], ...]
    effective_power: tuple[tuple[datetime, float], ...]
    soc_plan: tuple[tuple[datetime, float], ...]
    raw_day_energy_kwh: float
    effective_day_energy_kwh: float
    planned_end_soc: float

    def soc_target_at(self, at: datetime) -> float | None:
        """Interpolate the charging schedule at a timestamp."""
        if not self.soc_plan:
            return None

        if at.tzinfo is None:
            at = at.replace(tzinfo=UTC)

        points = self.soc_plan
        if at <= points[0][0]:
            return points[0][1]
        if at >= points[-1][0]:
            return points[-1][1]

        previous_time, previous_value = points[0]
        for current_time, current_value in points[1:]:
            if at <= current_time:
                span = (current_time - previous_time).total_seconds()
                if span <= 0:
                    return current_value
                fraction = (at - previous_time).total_seconds() / span
                return previous_value + fraction * (current_value - previous_value)
            previous_time = current_time
            previous_value = current_value

        return points[-1][1]

    def as_attributes(self) -> dict[str, object]:
        """Return compact state attributes for dashboard charts."""
        return {
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "raw_power": [
                [timestamp.isoformat(), round(value, 1)]
                for timestamp, value in self.raw_power
            ],
            "effective_power": [
                [timestamp.isoformat(), round(value, 1)]
                for timestamp, value in self.effective_power
            ],
            "soc_plan": [
                [timestamp.isoformat(), round(value, 2)]
                for timestamp, value in self.soc_plan
            ],
            "raw_day_energy_kwh": round(self.raw_day_energy_kwh, 3),
            "effective_day_energy_kwh": round(
                self.effective_day_energy_kwh,
                3,
            ),
            "planned_end_soc": round(self.planned_end_soc, 1),
        }


def _today_points(
    values: Mapping[datetime, int | float],
    today,
) -> list[tuple[datetime, float]]:
    """Return sorted points that belong to the local Home Assistant day."""
    result: list[tuple[datetime, float]] = []
    for timestamp, value in values.items():
        local_timestamp = dt_util.as_local(timestamp)
        if local_timestamp.date() != today:
            continue
        result.append((timestamp, max(float(value), 0.0)))
    result.sort(key=lambda item: item[0])
    return result


def _integrate_trapezoids(
    points: Iterable[tuple[datetime, float]],
) -> list[tuple[datetime, float]]:
    """Return cumulative kWh for a power curve using trapezoidal integration."""
    values = list(points)
    if not values:
        return []

    cumulative = 0.0
    result: list[tuple[datetime, float]] = [(values[0][0], 0.0)]

    previous_time, previous_power = values[0]
    for current_time, current_power in values[1:]:
        delta_hours = (current_time - previous_time).total_seconds() / 3600.0

        # Forecast.Solar normally provides 15- or 60-minute points. Ignore
        # unexpectedly large gaps instead of integrating across an overnight
        # or malformed interval.
        if 0 < delta_hours <= 2.0:
            average_power = (previous_power + current_power) / 2.0
            cumulative += average_power * delta_hours / 1000.0

        result.append((current_time, cumulative))
        previous_time = current_time
        previous_power = current_power

    return result


def build_forecast_curve(
    *,
    watts: Mapping[datetime, int | float],
    wh_period: Mapping[datetime, int | float],
    updated_at: datetime | None,
    effective_factor: float,
    expected_load_w: float,
    forecast_safety_kwh: float,
    battery_capacity_kwh: float,
    efficiency: float,
    min_soc: float,
    target_soc: float,
) -> ForecastCurveData | None:
    """Build a forecast-shaped charging schedule for the current day.

    The schedule is derived solely from the Forecast.Solar power curve and
    configured planning parameters. Actual PV production and actual SOC are
    deliberately not used to reshape the day's plan.
    """
    today = dt_util.now().date()
    raw_power = _today_points(watts, today)
    if len(raw_power) < 2:
        return None

    factor = max(float(effective_factor), 0.0)
    effective_power = [
        (timestamp, power * factor)
        for timestamp, power in raw_power
    ]

    # Battery-usable power is the forecast PV power left after the configured
    # expected household load. This gives the charging schedule its real
    # time-of-day shape instead of using astronomical daylight progress.
    net_battery_power = [
        (
            timestamp,
            max(power - max(expected_load_w, 0.0), 0.0),
        )
        for timestamp, power in effective_power
    ]
    cumulative = _integrate_trapezoids(net_battery_power)
    if not cumulative:
        return None

    efficiency = max(float(efficiency), 0.1)
    capacity = max(float(battery_capacity_kwh), 0.001)
    total_input_kwh = cumulative[-1][1]
    total_storable_kwh = total_input_kwh * efficiency

    # Keep the configured forecast safety reserve protected. It is subtracted
    # before charging efficiency, consistent with the existing optimizer
    # energy calculation.
    safe_input_kwh = max(
        total_input_kwh - max(float(forecast_safety_kwh), 0.0),
        0.0,
    )
    usable_storable_kwh = safe_input_kwh * efficiency

    if total_storable_kwh > 0:
        usable_scale = usable_storable_kwh / total_storable_kwh
    else:
        usable_scale = 0.0

    soc_span = max(float(target_soc) - float(min_soc), 0.0)
    max_needed_kwh = capacity * soc_span / 100.0
    usable_for_plan_kwh = min(usable_storable_kwh, max_needed_kwh)

    if usable_storable_kwh > 0:
        target_scale = usable_for_plan_kwh / usable_storable_kwh
    else:
        target_scale = 0.0

    soc_plan: list[tuple[datetime, float]] = []
    for timestamp, cumulative_input_kwh in cumulative:
        cumulative_storable = (
            cumulative_input_kwh
            * efficiency
            * usable_scale
            * target_scale
        )
        soc_gain = cumulative_storable / capacity * 100.0
        planned_soc = min(
            max(float(min_soc) + soc_gain, float(min_soc)),
            float(target_soc),
        )
        soc_plan.append((timestamp, planned_soc))

    raw_day_energy_kwh = sum(
        value
        for timestamp, value in _today_points(wh_period, today)
    ) / 1000.0

    return ForecastCurveData(
        updated_at=updated_at,
        raw_power=tuple(raw_power),
        effective_power=tuple(effective_power),
        soc_plan=tuple(soc_plan),
        raw_day_energy_kwh=raw_day_energy_kwh,
        effective_day_energy_kwh=raw_day_energy_kwh * factor,
        planned_end_soc=soc_plan[-1][1],
    )


def target_after_hours(
    curve: ForecastCurveData,
    now: datetime,
    hours: float,
) -> float | None:
    """Return the forecast schedule target after the given number of hours."""
    return curve.soc_target_at(now + timedelta(hours=max(hours, 0.0)))
