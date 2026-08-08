"""Growatt NOAH Optimizer integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import (
    Event,
    EventStateChangedData,
    HomeAssistant,
)
from homeassistant.helpers.event import (
    async_track_state_change_event,
    async_track_time_interval,
)

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
from .control import (
    CONTROL_CHECK_INTERVAL,
    NoahOptimizerController,
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

    controller = NoahOptimizerController(
        hass,
        coordinator,
    )

    # Keep the existing runtime_data interface for all entities.
    coordinator.controller = controller
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
        "sun.sun",
    ]

    async def _async_source_state_changed(
        event: Event[EventStateChangedData],
    ) -> None:
        """Refresh when a configured source entity changes."""

        await coordinator.async_update_from_states()

    entry.async_on_unload(
        async_track_state_change_event(
            hass,
            source_entities,
            _async_source_state_changed,
        )
    )

    # Check active control once per minute.
    # Actual normal output commands are rate-limited to
    # at least two minutes in control.py.
    entry.async_on_unload(
        async_track_time_interval(
            hass,
            controller.async_control_tick,
            CONTROL_CHECK_INTERVAL,
        )
    )

    await hass.config_entries.async_forward_entry_setups(
        entry,
        PLATFORMS,
    )

    # On a normal beta.4 -> beta.5 update this does not write
    # anything because OPT_CONTROL_ENABLED defaults to False.
    #
    # If active control was explicitly enabled in beta.5 and
    # Home Assistant is restarted, control resumes here.
    await controller.async_control_tick()

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