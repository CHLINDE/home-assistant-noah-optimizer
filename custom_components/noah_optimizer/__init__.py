"""Growatt NOAH Optimizer integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Event, EventStateChangedData, HomeAssistant
from homeassistant.helpers.event import async_track_state_change_event

from .const import (
    CONF_BATTERY_SOC,
    CONF_CHARGING_POWER,
    CONF_DISCHARGE_POWER,
    CONF_FORECAST_REMAINING,
    CONF_GRID_POWER,
    CONF_OUTPUT_POWER,
    CONF_SOLAR_POWER,
    CONF_SYSTEM_OUTPUT_POWER,
    PLATFORMS,
)
from .coordinator import NoahOptimizerCoordinator


type NoahOptimizerConfigEntry = ConfigEntry[
    NoahOptimizerCoordinator
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: NoahOptimizerConfigEntry,
) -> bool:
    """Set up the Growatt NOAH Optimizer."""

    coordinator = NoahOptimizerCoordinator(
        hass,
        entry,
    )

    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    source_entities = [
        entry.data[CONF_GRID_POWER],
        entry.data[CONF_SOLAR_POWER],
        entry.data[CONF_OUTPUT_POWER],
        entry.data[CONF_BATTERY_SOC],
        entry.data[CONF_CHARGING_POWER],
        entry.data[CONF_DISCHARGE_POWER],
        entry.data[CONF_FORECAST_REMAINING],
        entry.data[CONF_SYSTEM_OUTPUT_POWER],
    ]

    async def _async_source_state_changed(
        event: Event[EventStateChangedData],
    ) -> None:
        """Refresh when a configured source entity changes."""
        await coordinator.async_request_refresh()

    entry.async_on_unload(
        async_track_state_change_event(
            hass,
            source_entities,
            _async_source_state_changed,
        )
    )

    await hass.config_entries.async_forward_entry_setups(
        entry,
        PLATFORMS,
    )

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: NoahOptimizerConfigEntry,
) -> bool:
    """Unload the Growatt NOAH Optimizer."""

    return await hass.config_entries.async_unload_platforms(
        entry,
        PLATFORMS,
    )