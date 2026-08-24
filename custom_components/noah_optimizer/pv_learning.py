"""Persistent PV forecast learning for the Growatt NOAH Optimizer."""

from __future__ import annotations

import asyncio
from collections import deque
from statistics import median
import time
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from .const import DOMAIN

STORAGE_VERSION = 1
LEARNING_WINDOW_DAYS = 7
MIN_LEARNING_DAYS = 3
MIN_FORECAST_KWH = 0.25
MIN_OBSERVATION_SECONDS = 2 * 60 * 60
MIN_LEARNING_FACTOR = 0.50
MAX_LEARNING_FACTOR = 1.50
MAX_SAMPLE_GAP_SECONDS = 10 * 60
SAVE_INTERVAL_SECONDS = 15 * 60


class PvLearning:
    """Learn the systematic difference between PV forecast and production."""

    def __init__(self, hass: HomeAssistant, entry_id: str) -> None:
        """Initialize PV learning."""
        self.hass = hass
        self._store: Store[dict[str, Any]] = Store(
            hass,
            STORAGE_VERSION,
            f"{DOMAIN}.pv_learning.{entry_id}",
        )
        self._lock = asyncio.Lock()

        self._date: str | None = None
        self._actual_pv_kwh = 0.0
        self._forecast_reference_kwh: float | None = None
        self._observed_seconds = 0.0
        self._day_eligible = False

        self._last_sample_ts: float | None = None
        self._last_solar_power_w: float | None = None
        self._last_save_ts = 0.0

        self._ratios: deque[float] = deque(maxlen=LEARNING_WINDOW_DAYS)
        self._last_ratio: float | None = None

    async def async_load(self) -> None:
        """Load persisted PV-learning data."""
        data = await self._store.async_load()
        if not isinstance(data, dict):
            return

        self._date = data.get("date")
        self._actual_pv_kwh = float(data.get("actual_pv_kwh", 0.0))

        forecast_reference = data.get("forecast_reference_kwh")
        self._forecast_reference_kwh = (
            float(forecast_reference)
            if isinstance(forecast_reference, (int, float))
            else None
        )

        self._observed_seconds = float(data.get("observed_seconds", 0.0))
        self._day_eligible = bool(data.get("day_eligible", False))

        last_sample_ts = data.get("last_sample_ts")
        self._last_sample_ts = (
            float(last_sample_ts)
            if isinstance(last_sample_ts, (int, float))
            else None
        )

        last_solar_power = data.get("last_solar_power_w")
        self._last_solar_power_w = (
            float(last_solar_power)
            if isinstance(last_solar_power, (int, float))
            else None
        )

        ratios = data.get("ratios", [])
        if isinstance(ratios, list):
            self._ratios = deque(
                (
                    float(value)
                    for value in ratios
                    if isinstance(value, (int, float))
                ),
                maxlen=LEARNING_WINDOW_DAYS,
            )

        last_ratio = data.get("last_ratio")
        self._last_ratio = (
            float(last_ratio)
            if isinstance(last_ratio, (int, float))
            else None
        )

    async def async_update(
        self,
        *,
        solar_power_w: float,
        forecast_remaining_kwh: float | None,
        daylight_progress: float,
        night: bool,
    ) -> None:
        """Update today's measured PV energy and learning state."""
        async with self._lock:
            now_ts = time.time()
            today = dt_util.now().date().isoformat()

            if self._date != today:
                if self._date is not None:
                    self._finalize_day()

                self._start_new_day(
                    today=today,
                    daylight_progress=daylight_progress,
                    night=night,
                )

            solar_power_w = max(solar_power_w, 0.0)

            if (
                self._day_eligible
                and self._forecast_reference_kwh is None
                and forecast_remaining_kwh is not None
                and forecast_remaining_kwh >= MIN_FORECAST_KWH
                and (night or daylight_progress <= 0.20)
            ):
                # Forecast.Solar provides the remaining forecast. When the
                # first usable value arrives shortly after sunrise, add the
                # already measured PV energy to approximate a complete-day
                # forecast reference.
                self._forecast_reference_kwh = (
                    forecast_remaining_kwh + self._actual_pv_kwh
                )

            if (
                self._last_sample_ts is not None
                and self._last_solar_power_w is not None
            ):
                delta_seconds = now_ts - self._last_sample_ts

                if 0 < delta_seconds <= MAX_SAMPLE_GAP_SECONDS:
                    average_power_w = (
                        self._last_solar_power_w + solar_power_w
                    ) / 2.0
                    self._actual_pv_kwh += (
                        average_power_w * delta_seconds / 3_600_000
                    )

                    if not night:
                        self._observed_seconds += delta_seconds

            self._last_sample_ts = now_ts
            self._last_solar_power_w = solar_power_w

            if now_ts - self._last_save_ts >= SAVE_INTERVAL_SECONDS:
                await self._async_save()
                self._last_save_ts = now_ts

    def _start_new_day(
        self,
        *,
        today: str,
        daylight_progress: float,
        night: bool,
    ) -> None:
        """Initialize a new learning day."""
        self._date = today
        self._actual_pv_kwh = 0.0
        self._forecast_reference_kwh = None
        self._observed_seconds = 0.0

        # Do not learn from a partial day if the integration is first started
        # well after sunrise. A stored day that survived a restart keeps its
        # original eligibility flag because _start_new_day is then not called.
        self._day_eligible = night or daylight_progress <= 0.15

        self._last_sample_ts = None
        self._last_solar_power_w = None
        # Force persistence on the first update of a new day so a freshly
        # finalized learning sample cannot be lost before the next interval.
        self._last_save_ts = 0.0

    def _finalize_day(self) -> None:
        """Convert the completed day into one learning sample."""
        if not self._day_eligible:
            return
        if (
            self._forecast_reference_kwh is None
            or self._forecast_reference_kwh < MIN_FORECAST_KWH
        ):
            return
        if self._observed_seconds < MIN_OBSERVATION_SECONDS:
            return

        raw_ratio = self._actual_pv_kwh / self._forecast_reference_kwh
        self._last_ratio = raw_ratio

        bounded_ratio = min(
            max(raw_ratio, MIN_LEARNING_FACTOR),
            MAX_LEARNING_FACTOR,
        )
        self._ratios.append(bounded_ratio)

    async def _async_save(self) -> None:
        """Persist current PV-learning state."""
        await self._store.async_save(
            {
                "date": self._date,
                "actual_pv_kwh": self._actual_pv_kwh,
                "forecast_reference_kwh": self._forecast_reference_kwh,
                "observed_seconds": self._observed_seconds,
                "day_eligible": self._day_eligible,
                "last_sample_ts": self._last_sample_ts,
                "last_solar_power_w": self._last_solar_power_w,
                "ratios": list(self._ratios),
                "last_ratio": self._last_ratio,
            }
        )

    async def async_reset(self) -> None:
        """Delete all learned PV data."""
        async with self._lock:
            self._date = None
            self._actual_pv_kwh = 0.0
            self._forecast_reference_kwh = None
            self._observed_seconds = 0.0
            self._day_eligible = False
            self._last_sample_ts = None
            self._last_solar_power_w = None
            self._last_save_ts = 0.0
            self._ratios.clear()
            self._last_ratio = None
            await self._store.async_remove()

    @property
    def factor(self) -> float:
        """Return learned PV correction factor."""
        if not self._ratios:
            return 1.0
        return float(median(self._ratios))

    @property
    def ready(self) -> bool:
        """Return whether enough valid learning days exist."""
        return len(self._ratios) >= MIN_LEARNING_DAYS

    @property
    def sample_count(self) -> int:
        """Return number of valid learning days."""
        return len(self._ratios)

    @property
    def last_ratio(self) -> float | None:
        """Return last unbounded daily ratio."""
        return self._last_ratio

    @property
    def actual_pv_today_kwh(self) -> float:
        """Return integrated PV production for the current day."""
        return self._actual_pv_kwh

    @property
    def forecast_reference_kwh(self) -> float | None:
        """Return today's PV forecast reference."""
        return self._forecast_reference_kwh
