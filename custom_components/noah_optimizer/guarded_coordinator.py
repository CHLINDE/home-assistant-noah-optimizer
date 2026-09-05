"""Coordinator wrapper that blocks stale NOAH source updates."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .const import (
    CONTROLLER_OFF,
    DATA_ACTUATOR_AVAILABLE,
    DATA_CONTROLLER_MODE,
    DATA_CRITICAL_DATA_OK,
    DATA_OUTPUT_TARGET,
    DATA_STATUS,
    STATUS_ACTUATOR_UNAVAILABLE,
)
from .coordinator import NoahOptimizerCoordinator


class NoahOfflineAwareCoordinator(NoahOptimizerCoordinator):
    """Prevent cached Noah-MQTT data from being consumed while offline."""

    def __init__(self, hass, entry) -> None:
        """Initialize the guarded coordinator."""
        super().__init__(hass, entry)
        self._source_updates_allowed: Callable[[], bool] | None = None

    def set_source_update_guard(
        self,
        callback: Callable[[], bool],
    ) -> None:
        """Register the synchronous source-data validity check."""
        self._source_updates_allowed = callback

    def _offline_snapshot(self) -> dict[str, Any]:
        """Return the last known data marked as unsafe for active control."""
        data = dict(self.data or {})
        data[DATA_CRITICAL_DATA_OK] = False
        data[DATA_ACTUATOR_AVAILABLE] = False
        data[DATA_OUTPUT_TARGET] = None
        data[DATA_CONTROLLER_MODE] = CONTROLLER_OFF
        data[DATA_STATUS] = STATUS_ACTUATOR_UNAVAILABLE
        return data

    async def _async_update_data(self) -> dict[str, Any]:
        """Update only if the NOAH connectivity state is valid."""
        if (
            self._source_updates_allowed is not None
            and not self._source_updates_allowed()
        ):
            return self._offline_snapshot()

        return await super()._async_update_data()
