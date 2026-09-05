"""NOAH connectivity guard for active optimizer control."""

from __future__ import annotations

import asyncio
from datetime import datetime
import logging

from homeassistant.const import (
    STATE_OFF,
    STATE_ON,
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util

from .const import (
    CONF_SYSTEM_OUTPUT_POWER,
    CONTROL_STATUS_ACTUATOR_UNAVAILABLE,
    DATA_ACTUATOR_AVAILABLE,
    DATA_STATUS,
    STATUS_ACTUATOR_UNAVAILABLE,
)
from .control import NoahOptimizerController

_LOGGER = logging.getLogger(__name__)

NOAH_OFFLINE_NOTIFICATION_ID = "noah_optimizer_noah_offline"


class NoahOfflineGuard:
    """Block active output control while the physical NOAH is offline."""

    def __init__(
        self,
        hass: HomeAssistant,
        coordinator,
        controller: NoahOptimizerController,
    ) -> None:
        """Initialize the guard."""

        self.hass = hass
        self.coordinator = coordinator
        self._controller = controller
        self._lock = asyncio.Lock()

        self._connectivity_entity_id: str | None = None
        self._connectivity_ever_found = False
        self._missing_sensor_warned = False

        self._offline = False
        self._offline_reason: str | None = None
        self._offline_notified = False
        self._first_online_cleanup_done = False


    @property
    def status(self) -> str:
        """Return the delegated controller status."""

        return self._controller.status

    @property
    def last_command_target(self) -> float | None:
        """Return the last commanded output power."""

        return self._controller.last_command_target

    @property
    def last_command_at(self) -> datetime | None:
        """Return the last command timestamp."""

        return self._controller.last_command_at

    @property
    def connectivity_entity_id(self) -> str | None:
        """Return the discovered Noah-MQTT connectivity entity."""

        return self._connectivity_entity_id

    def source_updates_allowed(self) -> bool:
        """Return whether Noah-MQTT source values may be consumed.

        The coordinator calls this synchronously before every update path,
        including its own scheduled refreshes and option-triggered refreshes.
        Missing connectivity support keeps the existing compatibility mode.

        Only the actual Connectivity entity state is evaluated here. MQTT
        entities do not necessarily write a new Home Assistant state when the
        same payload/value is received again, so ``last_reported`` must not be
        used as an MQTT message freshness indicator.
        """
        online, _reason = self._read_connectivity()
        return online is not False

    async def async_prepare(self) -> None:
        """Resolve the connectivity entity during setup."""

        self._connectivity_entity_id = self._find_connectivity_entity_id()

        if self._connectivity_entity_id is not None:
            _LOGGER.info(
                "Using Noah-MQTT connectivity entity %s",
                self._connectivity_entity_id,
            )

    def _find_connectivity_entity_id(self) -> str | None:
        """Find Connectivity on the same HA device as System Output Power."""

        actuator_entity_id = self.coordinator.entry.data.get(
            CONF_SYSTEM_OUTPUT_POWER
        )
        if not actuator_entity_id:
            return None

        registry = er.async_get(self.hass)
        actuator_entry = registry.async_get(actuator_entity_id)
        if actuator_entry is None or actuator_entry.device_id is None:
            return None

        candidates: list[tuple[int, str]] = []

        for entry in er.async_entries_for_device(
            registry,
            actuator_entry.device_id,
            include_disabled_entities=False,
        ):
            if not entry.entity_id.startswith("binary_sensor."):
                continue

            state = self.hass.states.get(entry.entity_id)
            device_class = (
                state.attributes.get("device_class")
                if state is not None
                else None
            )
            unique_id = str(entry.unique_id or "").lower()
            entity_id = entry.entity_id.lower()

            if not (
                device_class == "connectivity"
                or unique_id.endswith("_connectivity")
                or entity_id.endswith("_connectivity")
            ):
                continue

            # Noah-MQTT currently uses <serial>_connectivity as unique ID.
            score = 2
            if unique_id.endswith("_connectivity"):
                score = 0
            elif device_class == "connectivity":
                score = 1

            candidates.append((score, entry.entity_id))

        if not candidates:
            return None

        candidates.sort()
        self._connectivity_ever_found = True
        return candidates[0][1]

    def _read_connectivity(self) -> tuple[bool | None, str]:
        """Read the Noah-MQTT Connectivity entity state.

        True  = online
        False = offline, unavailable, unknown or disappeared
        None  = no connectivity entity has ever been discovered
        """

        if self._connectivity_entity_id is None:
            self._connectivity_entity_id = self._find_connectivity_entity_id()

        entity_id = self._connectivity_entity_id

        if entity_id is None:
            if self._connectivity_ever_found:
                return False, "connectivity_entity_missing"

            if not self._missing_sensor_warned:
                _LOGGER.warning(
                    "No Noah-MQTT Connectivity binary sensor found for the "
                    "configured NOAH. Offline protection is in compatibility "
                    "mode. Update Noah-MQTT if this entity is missing."
                )
                self._missing_sensor_warned = True

            return None, "connectivity_sensor_not_found"

        state = self.hass.states.get(entity_id)
        if state is None:
            self._connectivity_entity_id = None
            return False, "connectivity_state_missing"

        if state.state == STATE_OFF:
            return False, "reported_offline"

        if state.state in {
            STATE_UNKNOWN,
            STATE_UNAVAILABLE,
            "",
        }:
            return False, f"connectivity_{state.state or 'empty'}"

        if state.state != STATE_ON:
            return False, f"connectivity_unexpected_{state.state}"

        return True, "online"

    def _notification_text(self) -> tuple[str, str]:
        """Return localized persistent-notification content."""

        language = str(self.hass.config.language or "en").lower()

        if language.startswith("de"):
            return (
                "NOAH Optimizer: NOAH offline",
                "Der Growatt NOAH wird von Noah-MQTT als offline oder "
                "nicht verfügbar gemeldet. Es werden keine Stellbefehle "
                "an den NOAH gesendet. Bitte die IoT-/WLAN-Verbindung "
                "des NOAH (IoT-Taste/LED) und Noah-MQTT prüfen.",
            )

        return (
            "NOAH Optimizer: NOAH offline",
            "Noah-MQTT reports the Growatt NOAH as offline or unavailable. "
            "No output commands are sent to the NOAH. Check the NOAH "
            "IoT/Wi-Fi connection and Noah-MQTT.",
        )

    async def _async_create_offline_notification(self) -> None:
        """Create the persistent offline notification once per episode."""

        title, message = self._notification_text()

        try:
            await self.hass.services.async_call(
                "persistent_notification",
                "create",
                {
                    "notification_id": NOAH_OFFLINE_NOTIFICATION_ID,
                    "title": title,
                    "message": message,
                },
                blocking=False,
            )
        except HomeAssistantError:
            _LOGGER.exception(
                "Could not create NOAH offline notification"
            )

    async def _async_dismiss_offline_notification(self) -> None:
        """Dismiss the offline notification."""

        try:
            await self.hass.services.async_call(
                "persistent_notification",
                "dismiss",
                {"notification_id": NOAH_OFFLINE_NOTIFICATION_ID},
                blocking=False,
            )
        except HomeAssistantError:
            _LOGGER.exception(
                "Could not dismiss NOAH offline notification"
            )

    async def _async_reset_failsafe_for_offline(self) -> None:
        """Prevent a delayed failsafe write after an offline interval."""

        if getattr(self._controller, "_failsafe_notified", False):
            try:
                await self._controller._async_dismiss_failsafe_notification()
            except HomeAssistantError:
                _LOGGER.exception(
                    "Could not dismiss existing failsafe notification"
                )

        self._controller._critical_missing_since = None
        self._controller._failsafe_sent = False
        self._controller._failsafe_notified = False

    async def _async_enter_offline(self, reason: str) -> None:
        """Enter protected offline state."""

        was_offline = self._offline
        old_reason = self._offline_reason

        self._offline = True
        self._offline_reason = reason

        # Noah-MQTT can leave numeric values cached/available while the
        # physical device itself is offline. Override the optimizer-facing
        # status after each normal coordinator refresh.
        self.coordinator.data[DATA_ACTUATOR_AVAILABLE] = False
        self.coordinator.data[DATA_STATUS] = STATUS_ACTUATOR_UNAVAILABLE

        await self._async_reset_failsafe_for_offline()

        self._controller._set_status(
            CONTROL_STATUS_ACTUATOR_UNAVAILABLE
        )
        self.coordinator.async_update_listeners()

        if not was_offline or old_reason != reason:
            _LOGGER.warning(
                "NOAH offline guard active (%s); output commands are blocked",
                reason,
            )

        if not self._offline_notified:
            await self._async_create_offline_notification()
            self._offline_notified = True

    async def _async_leave_offline(self) -> None:
        """Leave protected offline state."""

        if self._offline:
            _LOGGER.info(
                "NOAH connectivity restored; active control may resume"
            )

        self._offline = False
        self._offline_reason = None

        if self._offline_notified or not self._first_online_cleanup_done:
            await self._async_dismiss_offline_notification()

        self._offline_notified = False
        self._first_online_cleanup_done = True

    async def async_source_state_changed(self) -> None:
        """Refresh source data only while the NOAH connection is valid.

        Noah-MQTT can keep numeric entities at their last value while the
        physical NOAH is offline. Connectivity must therefore be checked
        before the coordinator consumes source values; otherwise cached PV
        power would be integrated by PV learning as if it were live data.
        """

        async with self._lock:
            online, reason = self._read_connectivity()

            if online is False:
                await self._async_enter_offline(reason)
                return

            if online is True:
                await self._async_leave_offline()

            # Online or compatibility mode: source data may be consumed.
            await self.coordinator.async_update_from_states()

    async def async_refresh_status(self) -> None:
        """Backward-compatible alias for source-state refresh handling."""

        await self.async_source_state_changed()

    async def async_control_tick(
        self,
        _now: datetime | None = None,
    ) -> None:
        """Block or delegate a normal controller tick."""

        async with self._lock:
            online, reason = self._read_connectivity()

            if online is False:
                # Do not refresh the coordinator here. Cached Noah-MQTT values
                # must not be consumed while the physical NOAH is offline; in
                # particular, PV learning integrates power over elapsed time.
                # The skipped interval becomes a normal learning gap after
                # connectivity returns instead of fake PV production.
                await self._async_enter_offline(reason)
                return

            if online is True:
                await self._async_leave_offline()

            # Compatibility mode (None) preserves the existing behavior for an
            # installation where a connectivity entity has never existed.
            await self._controller.async_control_tick(_now)

    async def async_shutdown(self) -> None:
        """Dismiss the integration-owned offline notification on unload."""

        if self._offline_notified:
            await self._async_dismiss_offline_notification()

        self._offline = False
        self._offline_reason = None
        self._offline_notified = False
