"""Coordinator for the Growatt NOAH Optimizer."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
)

from .const import (
    CONF_BATTERY_SOC,
    CONF_CHARGING_POWER,
    CONF_DISCHARGE_POWER,
    CONF_FORECAST_REMAINING,
    CONF_GRID_POWER,
    CONF_INVERT_GRID_SIGN,
    CONF_OUTPUT_POWER,
    CONF_SOLAR_POWER,
    CONF_SYSTEM_OUTPUT_POWER,
    DATA_ACTUATOR_AVAILABLE,
    DATA_BATTERY_POWER,
    DATA_CHARGING_POWER,
    DATA_CRITICAL_DATA_OK,
    DATA_DISCHARGE_POWER,
    DATA_FORECAST_AVAILABLE,
    DATA_FORECAST_REMAINING,
    DATA_GRID_EXPORT,
    DATA_GRID_IMPORT,
    DATA_GRID_POWER,
    DATA_HOME_LOAD,
    DATA_OUTPUT_POWER,
    DATA_SOC,
    DATA_SOLAR_POWER,
    DATA_STATUS,
    DOMAIN,
    STATUS_ACTUATOR_UNAVAILABLE,
    STATUS_BATTERY_DATA_MISSING,
    STATUS_CRITICAL_DATA_MISSING,
    STATUS_FORECAST_UNAVAILABLE,
    STATUS_OK,
    UPDATE_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)


class NoahOptimizerCoordinator(
    DataUpdateCoordinator[dict[str, Any]]
):
    """Read and normalize data used by the NOAH Optimizer."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the coordinator."""

        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
            always_update=False,
        )

        self.entry = entry

    def _read_numeric_state(
        self,
        entity_id: str,
    ) -> tuple[float | None, str | None]:
        """Read a numeric state and its unit."""

        state = self.hass.states.get(entity_id)

        if state is None:
            return None, None

        if state.state in {
            STATE_UNKNOWN,
            STATE_UNAVAILABLE,
            "",
        }:
            return None, state.attributes.get(
                "unit_of_measurement"
            )

        try:
            value = float(state.state)
        except (TypeError, ValueError):
            return None, state.attributes.get(
                "unit_of_measurement"
            )

        return (
            value,
            state.attributes.get("unit_of_measurement"),
        )

    def _read_power_w(
        self,
        entity_id: str,
    ) -> float | None:
        """Read a power entity and normalize it to watts."""

        value, unit = self._read_numeric_state(entity_id)

        if value is None:
            return None

        if unit == "W":
            return value

        if unit == "kW":
            return value * 1000

        return None

    def _read_energy_kwh(
        self,
        entity_id: str,
    ) -> float | None:
        """Read an energy entity and normalize it to kWh."""

        value, unit = self._read_numeric_state(entity_id)

        if value is None:
            return None

        if unit == "kWh":
            return value

        if unit == "Wh":
            return value / 1000

        return None

    def _read_soc(
        self,
        entity_id: str,
    ) -> float | None:
        """Read a battery SOC in percent."""

        value, unit = self._read_numeric_state(entity_id)

        if value is None:
            return None

        if unit not in {"%", None, ""}:
            return None

        if not 0 <= value <= 100:
            return None

        return value

    def _entity_available(
        self,
        entity_id: str,
    ) -> bool:
        """Return whether an entity currently has a usable state."""

        state = self.hass.states.get(entity_id)

        return (
            state is not None
            and state.state
            not in {
                STATE_UNKNOWN,
                STATE_UNAVAILABLE,
                "",
            }
        )

    async def _async_update_data(
        self,
    ) -> dict[str, Any]:
        """Read and calculate optimizer observation data."""

        grid_power = self._read_power_w(
            self.entry.data[CONF_GRID_POWER]
        )

        solar_power = self._read_power_w(
            self.entry.data[CONF_SOLAR_POWER]
        )

        output_power = self._read_power_w(
            self.entry.data[CONF_OUTPUT_POWER]
        )

        soc = self._read_soc(
            self.entry.data[CONF_BATTERY_SOC]
        )

        charging_power = self._read_power_w(
            self.entry.data[CONF_CHARGING_POWER]
        )

        discharging_power = self._read_power_w(
            self.entry.data[CONF_DISCHARGE_POWER]
        )

        forecast_remaining = self._read_energy_kwh(
            self.entry.data[CONF_FORECAST_REMAINING]
        )

        if (
            grid_power is not None
            and self.entry.data.get(
                CONF_INVERT_GRID_SIGN,
                False,
            )
        ):
            grid_power *= -1

        critical_data_ok = all(
            value is not None
            for value in (
                grid_power,
                solar_power,
                output_power,
                soc,
            )
        )

        battery_data_ok = (
            charging_power is not None
            and discharging_power is not None
        )

        forecast_available = (
            forecast_remaining is not None
        )

        actuator_available = self._entity_available(
            self.entry.data[CONF_SYSTEM_OUTPUT_POWER]
        )

        grid_import = (
            max(grid_power, 0.0)
            if grid_power is not None
            else None
        )

        grid_export = (
            max(-grid_power, 0.0)
            if grid_power is not None
            else None
        )

        home_load = (
            max(grid_power + output_power, 0.0)
            if grid_power is not None
            and output_power is not None
            else None
        )

        battery_power = (
            discharging_power - charging_power
            if charging_power is not None
            and discharging_power is not None
            else None
        )

        if not critical_data_ok:
            status = STATUS_CRITICAL_DATA_MISSING

        elif not actuator_available:
            status = STATUS_ACTUATOR_UNAVAILABLE

        elif not battery_data_ok:
            status = STATUS_BATTERY_DATA_MISSING

        elif not forecast_available:
            status = STATUS_FORECAST_UNAVAILABLE

        else:
            status = STATUS_OK

        return {
            DATA_GRID_POWER: (
                round(grid_power)
                if grid_power is not None
                else None
            ),
            DATA_GRID_IMPORT: (
                round(grid_import)
                if grid_import is not None
                else None
            ),
            DATA_GRID_EXPORT: (
                round(grid_export)
                if grid_export is not None
                else None
            ),
            DATA_SOLAR_POWER: (
                round(solar_power)
                if solar_power is not None
                else None
            ),
            DATA_OUTPUT_POWER: (
                round(output_power)
                if output_power is not None
                else None
            ),
            DATA_SOC: (
                round(soc, 1)
                if soc is not None
                else None
            ),
            DATA_CHARGING_POWER: (
                round(charging_power)
                if charging_power is not None
                else None
            ),
            DATA_DISCHARGE_POWER: (
                round(discharging_power)
                if discharging_power is not None
                else None
            ),
            DATA_BATTERY_POWER: (
                round(battery_power)
                if battery_power is not None
                else None
            ),
            DATA_HOME_LOAD: (
                round(home_load)
                if home_load is not None
                else None
            ),
            DATA_FORECAST_REMAINING: (
                round(forecast_remaining, 3)
                if forecast_remaining is not None
                else None
            ),
            DATA_CRITICAL_DATA_OK: critical_data_ok,
            DATA_FORECAST_AVAILABLE: forecast_available,
            DATA_ACTUATOR_AVAILABLE: actuator_available,
            DATA_STATUS: status,
        }