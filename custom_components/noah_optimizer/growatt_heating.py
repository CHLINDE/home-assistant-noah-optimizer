"""Read the optional NOAH heater status from Growatt OpenAPI v4."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any

from aiohttp import ClientError
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

_LOGGER = logging.getLogger(__name__)
_URL = "https://openapi.growatt.com/v4/new-api/queryLastData"


def parse_heating_status(payload: Any, serial: str) -> bool:
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
    timestamp = device.get("time")
    if timestamp is not None:
        try:
            age = datetime.now(timezone.utc) - datetime.fromtimestamp(
                float(timestamp) / 1000, tz=timezone.utc
            )
        except (TypeError, ValueError, OverflowError) as err:
            raise ValueError("Invalid NOAH data timestamp") from err
        if age > timedelta(minutes=30) or age < -timedelta(minutes=5):
            raise ValueError("NOAH data is stale")
    status = device.get("heatingStatus")
    if status in (0, "0", False):
        return False
    if status in (1, "1", True):
        return True
    raise ValueError("Unknown NOAH heating status")


class GrowattHeatingCoordinator(DataUpdateCoordinator[bool]):
    """Poll Growatt independently of the optimizer's control loop."""

    def __init__(self, hass: HomeAssistant, token: str, serial: str) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="NOAH battery heating",
            update_interval=timedelta(minutes=5),
        )
        self._token = token
        self._serial = serial

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
            return parse_heating_status(payload, self._serial)
        except (ClientError, TimeoutError, ValueError) as err:
            raise UpdateFailed(f"NOAH heating status unavailable: {err}") from err
