"""Read the optional NOAH heater status from Growatt OpenAPI v4."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone, tzinfo
from typing import Any
from zoneinfo import ZoneInfo

from aiohttp import ClientError
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.storage import Store
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
_URL = "https://openapi.growatt.com/v4/new-api/queryLastData"


def parse_heating_status(
    payload: Any,
    serial: str,
    local_timezone: tzinfo,
    now: datetime | None = None,
) -> bool:
    """Reject missing, stale, or mismatched data instead of reporting OFF."""
    if not isinstance(payload, dict) or str(payload.get("code")) != "0":
        raise ValueError("Growatt did not return a successful response")
    data = payload.get("data")
    devices = data.get("noah") if isinstance(data, dict) else None
    if not isinstance(devices, list):
        raise ValueError("Growatt response has no NOAH data")
    device = next(
        (item for item in devices if isinstance(item, dict) and item.get("deviceSn") == serial),
        None,
    )
    if device is None:
        raise ValueError("NOAH serial number not found in Growatt response")
    # Growatt's timeStr is the plant's local display time. Its numeric `time`
    # can differ from that display time by several hours, so prefer timeStr
    # for freshness checks. The epoch remains a fallback for older responses.
    try:
        if isinstance(device.get("timeStr"), str) and device["timeStr"].strip():
            timestamp = datetime.fromisoformat(device["timeStr"].strip())
            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=local_timezone)
        elif device.get("time") is not None:
            timestamp = datetime.fromtimestamp(
                float(device["time"]) / 1000, tz=timezone.utc
            )
        else:
            raise ValueError("NOAH response has no timestamp")
    except (TypeError, ValueError, OverflowError) as err:
        raise ValueError("Invalid NOAH data timestamp") from err
    age = (now or datetime.now(timezone.utc)) - timestamp
    if age > timedelta(minutes=30) or age < -timedelta(minutes=5):
        raise ValueError(
            f"NOAH data is stale (last update {timestamp.isoformat()}, "
            f"age {age})"
        )
    status = device.get("heatingStatus")
    if status in (0, "0", False):
        return False
    if status in (1, "1", True):
        return True
    raise ValueError("Unknown NOAH heating status")


class GrowattHeatingCoordinator(DataUpdateCoordinator[bool]):
    """Poll Growatt independently of the optimizer's control loop."""

    def __init__(
        self, hass: HomeAssistant, token: str, serial: str, entry_id: str
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="NOAH battery heating",
            update_interval=timedelta(minutes=5),
        )
        self._token = token
        self._serial = serial
        self._local_timezone = ZoneInfo(hass.config.time_zone)
        self._store: Store[dict[str, Any]] = Store(
            hass, 1, f"{DOMAIN}.heating.{entry_id}"
        )
        self._periods: dict[str, str] = {}
        self._counts = {"today": 0, "week": 0, "month": 0}
        self._last_state: bool | None = None

    async def async_initialize(self) -> None:
        """Restore counters and the previous state across HA restarts."""
        saved = await self._store.async_load()
        if not isinstance(saved, dict) or saved.get("serial") != self._serial:
            return
        periods = saved.get("periods")
        counts = saved.get("counts")
        if isinstance(periods, dict) and isinstance(counts, dict):
            for period in self._counts:
                value = counts.get(period)
                key = periods.get(period)
                if isinstance(key, str) and type(value) is int and value >= 0:
                    self._periods[period] = key
                    self._counts[period] = value
        if type(saved.get("last_state")) is bool:
            self._last_state = saved["last_state"]

    @staticmethod
    def _period_keys(now: datetime) -> dict[str, str]:
        """Use HA's local date, ISO calendar weeks and calendar months."""
        iso = now.isocalendar()
        return {
            "today": now.date().isoformat(),
            "week": f"{iso.year}-W{iso.week:02d}",
            "month": f"{now.year}-{now.month:02d}",
        }

    def activation_count(self, period: str) -> int:
        """Return zero immediately after a period boundary."""
        return (
            self._counts[period]
            if self._periods.get(period) == self._period_keys(dt_util.now())[period]
            else 0
        )

    @property
    def history_available(self) -> bool:
        """Counters start once a first valid status has been observed."""
        return self._last_state is not None

    async def _async_record_state(self, state: bool) -> None:
        """Count observed OFF-to-ON transitions and persist them."""
        keys = self._period_keys(dt_util.now())
        changed = False
        for period, key in keys.items():
            if self._periods.get(period) != key:
                self._periods[period] = key
                self._counts[period] = 0
                changed = True
        if self._last_state is False and state is True:
            for period in self._counts:
                self._counts[period] += 1
            changed = True
        if self._last_state is not state:
            self._last_state = state
            changed = True
        if changed:
            await self._store.async_save(
                {
                    "serial": self._serial,
                    "periods": self._periods,
                    "counts": self._counts,
                    "last_state": self._last_state,
                }
            )

    async def _async_update_data(self) -> bool:
        try:
            async with async_get_clientsession(self.hass).post(
                _URL,
                headers={"token": self._token},
                data={"deviceSn": self._serial, "deviceType": "noah"},
                timeout=15,
            ) as response:
                response.raise_for_status()
                payload = await response.json()
            state = parse_heating_status(
                payload, self._serial, self._local_timezone
            )
            await self._async_record_state(state)
            return state
        except (ClientError, TimeoutError, ValueError) as err:
            raise UpdateFailed(f"NOAH heating status unavailable: {err}") from err
