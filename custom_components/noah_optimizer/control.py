"""Active control for the Growatt NOAH Optimizer."""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
import logging

from homeassistant.const import (
    STATE_ON,
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.util import dt as dt_util

from .const import (
    CONF_SYSTEM_OUTPUT_POWER,
    DATA_ACTUATOR_AVAILABLE,
    DATA_CRITICAL_DATA_OK,
    DATA_OUTPUT_TARGET,
    OPT_COMMAND_DEADBAND,
    OPT_CONTROL_ENABLED,
    OPT_ENABLED,
)

_LOGGER = logging.getLogger(__name__)


# How often the control logic is evaluated.
CONTROL_CHECK_INTERVAL = timedelta(minutes=1)

# Normal output commands must be at least this far apart.
MIN_COMMAND_INTERVAL = timedelta(minutes=2)

# Retry if the NOAH has not taken over the requested value.
RETRY_INTERVAL = timedelta(minutes=20)

# Set the output to 0 W after critical data has been missing
# for this amount of time.
FAILSAFE_DELAY = timedelta(minutes=10)

# Entity used by the legacy YAML optimizer.
# If it exists and is ON, active control is blocked.
LEGACY_OPTIMIZER_ENABLE_ENTITY = (
    "input_boolean.noah_optimizer_enabled"
)

FAILSAFE_NOTIFICATION_ID = "noah_optimizer_failsafe"


class NoahOptimizerController:
    """Control the NOAH output power."""

    def __init__(
        self,
        hass: HomeAssistant,
        coordinator,
    ) -> None:
        """Initialize the controller."""

        self.hass = hass
        self.coordinator = coordinator

        self._lock = asyncio.Lock()

        self._last_command_target: float | None = None
        self._last_command_at: datetime | None = None

        self._critical_missing_since: datetime | None = None
        self._failsafe_sent = False

        self._status = "disabled"

    @property
    def status(self) -> str:
        """Return the current controller status."""

        return self._status

    @property
    def last_command_target(self) -> float | None:
        """Return the last commanded output power."""

        return self._last_command_target

    @property
    def last_command_at(self) -> datetime | None:
        """Return the time of the last command."""

        return self._last_command_at

    def _publish_state(self) -> None:
        """Notify coordinator entities about controller changes."""

        if self.coordinator.data is not None:
            self.coordinator.async_set_updated_data(
                dict(self.coordinator.data)
            )

    def _set_status(
        self,
        status: str,
    ) -> None:
        """Set controller status."""

        if self._status == status:
            return

        self._status = status

        _LOGGER.debug(
            "NOAH controller status changed to %s",
            status,
        )

        self._publish_state()

    def _legacy_optimizer_active(self) -> bool:
        """Return whether the legacy YAML optimizer is active."""

        state = self.hass.states.get(
            LEGACY_OPTIMIZER_ENABLE_ENTITY
        )

        return (
            state is not None
            and state.state == STATE_ON
        )

    def _read_actuator_value(self) -> float | None:
        """Read the current NOAH output setpoint in watts."""

        entity_id = self.coordinator.entry.data[
            CONF_SYSTEM_OUTPUT_POWER
        ]

        state = self.hass.states.get(entity_id)

        if state is None:
            return None

        if state.state in {
            STATE_UNKNOWN,
            STATE_UNAVAILABLE,
            "",
        }:
            return None

        try:
            value = float(state.state)
        except (TypeError, ValueError):
            return None

        unit = state.attributes.get(
            "unit_of_measurement"
        )

        if unit == "kW":
            return value * 1000

        if unit in {
            "W",
            None,
            "",
        }:
            return value

        return None

    async def _async_write_output(
        self,
        target: float,
        now: datetime,
    ) -> bool:
        """Write output power to the NOAH."""

        entity_id = self.coordinator.entry.data[
            CONF_SYSTEM_OUTPUT_POWER
        ]

        target = float(round(target))

        try:
            await self.hass.services.async_call(
                "number",
                "set_value",
                {
                    "entity_id": entity_id,
                    "value": target,
                },
                blocking=True,
            )

        except HomeAssistantError as err:
            _LOGGER.error(
                "Failed to set NOAH output power to %.0f W: %s",
                target,
                err,
            )

            self._set_status(
                "command_failed"
            )

            return False

        self._last_command_target = target
        self._last_command_at = now

        _LOGGER.info(
            "NOAH output power set to %.0f W",
            target,
        )

        self._publish_state()

        return True

    async def _async_create_failsafe_notification(
        self,
    ) -> None:
        """Create Home Assistant failsafe notification."""

        try:
            await self.hass.services.async_call(
                "persistent_notification",
                "create",
                {
                    "notification_id":
                        FAILSAFE_NOTIFICATION_ID,
                    "title":
                        "NOAH-Optimierer gestoppt",
                    "message":
                        "Kritische Messwerte fehlen seit "
                        "mindestens zehn Minuten. "
                        "Die NOAH-Ausgangsleistung wurde "
                        "soweit möglich auf 0 W gesetzt.",
                },
                blocking=False,
            )

        except HomeAssistantError:
            _LOGGER.exception(
                "Could not create NOAH failsafe notification"
            )

    async def _async_dismiss_failsafe_notification(
        self,
    ) -> None:
        """Dismiss Home Assistant failsafe notification."""

        try:
            await self.hass.services.async_call(
                "persistent_notification",
                "dismiss",
                {
                    "notification_id":
                        FAILSAFE_NOTIFICATION_ID,
                },
                blocking=False,
            )

        except HomeAssistantError:
            _LOGGER.exception(
                "Could not dismiss NOAH failsafe notification"
            )

    async def _async_handle_missing_data(
        self,
        now: datetime,
    ) -> None:
        """Handle missing critical measurement data."""

        if self._critical_missing_since is None:
            self._critical_missing_since = now

        missing_duration = (
            now - self._critical_missing_since
        )

        if missing_duration < FAILSAFE_DELAY:
            self._set_status(
                "critical_data_missing"
            )
            return

        if self._failsafe_sent:
            self._set_status(
                "failsafe"
            )
            return

        if not self.coordinator.data.get(
            DATA_ACTUATOR_AVAILABLE,
            False,
        ):
            self._set_status(
                "actuator_unavailable"
            )
            return

        success = await self._async_write_output(
            0,
            now,
        )

        if not success:
            return

        self._failsafe_sent = True

        self._set_status(
            "failsafe"
        )

        await self._async_create_failsafe_notification()

    async def _async_handle_data_recovered(
        self,
    ) -> None:
        """Reset failsafe state after data recovery."""

        if self._critical_missing_since is None:
            return

        had_failsafe = self._failsafe_sent

        self._critical_missing_since = None
        self._failsafe_sent = False

        if had_failsafe:
            await self._async_dismiss_failsafe_notification()

    async def async_control_tick(
        self,
        _now: datetime | None = None,
    ) -> None:
        """Evaluate and, if required, send an output command."""

        async with self._lock:

            now = dt_util.utcnow()

            # Always use the newest available states.
            await self.coordinator.async_update_from_states()

            # Active output control has its own explicit opt-in.
            if not self.coordinator.get_option(
                OPT_CONTROL_ENABLED
            ):
                self._set_status(
                    "disabled"
                )
                return

            # Optimizer calculation must also be enabled.
            if not self.coordinator.get_option(
                OPT_ENABLED
            ):
                self._set_status(
                    "optimizer_disabled"
                )
                return

            # Never allow the legacy YAML controller and this
            # controller to write to the same NOAH simultaneously.
            if self._legacy_optimizer_active():
                self._set_status(
                    "legacy_controller_active"
                )

                _LOGGER.warning(
                    "NOAH active control blocked because the "
                    "legacy YAML optimizer is still enabled"
                )

                return

            critical_data_ok = bool(
                self.coordinator.data.get(
                    DATA_CRITICAL_DATA_OK,
                    False,
                )
            )

            if not critical_data_ok:
                await self._async_handle_missing_data(
                    now
                )
                return

            await self._async_handle_data_recovered()

            if not self.coordinator.data.get(
                DATA_ACTUATOR_AVAILABLE,
                False,
            ):
                self._set_status(
                    "actuator_unavailable"
                )
                return

            target = self.coordinator.data.get(
                DATA_OUTPUT_TARGET
            )

            if target is None:
                self._set_status(
                    "target_unavailable"
                )
                return

            target = float(target)

            actual_setpoint = (
                self._read_actuator_value()
            )

            if actual_setpoint is None:
                self._set_status(
                    "actuator_unavailable"
                )
                return

            deadband = float(
                self.coordinator.get_option(
                    OPT_COMMAND_DEADBAND
                )
            )

            if self._last_command_at is None:
                elapsed = None
            else:
                elapsed = (
                    now - self._last_command_at
                )

            # Rate limiting:
            # never send normal commands faster than every two minutes.
            if (
                elapsed is not None
                and elapsed < MIN_COMMAND_INTERVAL
            ):
                self._set_status(
                    "rate_limited"
                )
                return

            if self._last_command_target is None:
                reference = actual_setpoint
            else:
                reference = (
                    self._last_command_target
                )

            change_required = (
                abs(target - reference)
                >= deadband
            )

            first_sync_required = (
                self._last_command_at is None
                and abs(
                    target - actual_setpoint
                ) >= deadband
            )

            retry_required = (
                elapsed is not None
                and elapsed >= RETRY_INTERVAL
                and abs(
                    target - actual_setpoint
                ) >= deadband
            )

            if not (
                change_required
                or first_sync_required
                or retry_required
            ):
                if (
                    abs(
                        target - actual_setpoint
                    ) < deadband
                ):
                    self._set_status(
                        "in_sync"
                    )
                else:
                    self._set_status(
                        "waiting_for_retry"
                    )

                return

            success = await self._async_write_output(
                target,
                now,
            )

            if success:
                self._set_status(
                    "command_sent"
                )