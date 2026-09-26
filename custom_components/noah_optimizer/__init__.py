"""Growatt NOAH Optimizer integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import (
    Event,
    EventStateChangedData,
    HomeAssistant,
)
from homeassistant.helpers.event import (
    async_track_state_change_event,
    async_track_time_change,
    async_track_time_interval,
)

from .const import (
    CONF_BATTERY_SOC,
    CONF_CHARGING_POWER,
    CONF_DISCHARGE_POWER,
    CONF_FORECAST_REMAINING,
    CONF_GRID_POWER,
    CONF_NOAH_API_TOKEN,
    CONF_NOAH_DEVICE_SN,
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
from .guarded_coordinator import NoahOfflineAwareCoordinator
from .dashboard_migration_v21 import (
    async_ensure_dashboard,
    remove_dashboard_panel,
)
from .frontend import async_register_history_card, remove_history_card
from .growatt_heating import GrowattHeatingCoordinator
from .history import (
    async_register_history_store,
    async_unregister_history_store,
)
from .offline_guard import NoahOfflineGuard

_LOGGER = logging.getLogger(__name__)


type NoahOptimizerConfigEntry = ConfigEntry[
    NoahOptimizerCoordinator
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: NoahOptimizerConfigEntry,
) -> bool:
    """Set up the Growatt NOAH Optimizer."""

    coordinator = NoahOfflineAwareCoordinator(
        hass,
        entry,
    )
    await coordinator.async_initialize()

    base_controller = NoahOptimizerController(
        hass,
        coordinator,
    )
    controller = NoahOfflineGuard(
        hass,
        coordinator,
        base_controller,
    )
    await controller.async_prepare()

    # Install the connectivity gate before the very first coordinator refresh.
    # This protects startup, scheduled DataUpdateCoordinator refreshes, option
    # changes and reset actions from consuming retained Noah-MQTT values.
    coordinator.set_source_update_guard(
        controller.source_updates_allowed
    )

    coordinator.controller = controller
    entry.runtime_data = coordinator

    api_config = (
        entry.options.get(CONF_NOAH_API_TOKEN),
        entry.options.get(CONF_NOAH_DEVICE_SN),
    )

    async def _async_options_changed(hass, updated_entry) -> None:
        if api_config != (
            updated_entry.options.get(CONF_NOAH_API_TOKEN),
            updated_entry.options.get(CONF_NOAH_DEVICE_SN),
        ):
            await hass.config_entries.async_reload(updated_entry.entry_id)

    entry.async_on_unload(entry.add_update_listener(_async_options_changed))

    await coordinator.async_config_entry_first_refresh()

    coordinator.heating = None
    if all(api_config):
        try:
            heating = GrowattHeatingCoordinator(
                hass, api_config[0], api_config[1], entry.entry_id
            )
            await heating.async_initialize()
            await heating.async_refresh()
            coordinator.heating = heating
            entry.async_on_unload(
                async_track_time_change(
                    hass,
                    lambda _now: heating.async_update_listeners(),
                    hour=0,
                    minute=0,
                    second=0,
                )
            )
        except Exception:  # noqa: BLE001
            _LOGGER.exception("Could not initialize optional NOAH heating diagnostics")

    async_register_history_store(hass, entry.entry_id, coordinator.history)

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

    connectivity_entity_id = controller.connectivity_entity_id
    if (
        connectivity_entity_id is not None
        and connectivity_entity_id not in source_entities
    ):
        source_entities.append(connectivity_entity_id)

    async def _async_source_state_changed(
        event: Event[EventStateChangedData],
    ) -> None:
        """Refresh when a configured source entity changes."""

        # Check NOAH connectivity before consuming source values. This keeps
        # retained Noah-MQTT measurements out of PV learning while the device
        # is offline.
        await controller.async_source_state_changed()

    entry.async_on_unload(
        async_track_state_change_event(
            hass,
            source_entities,
            _async_source_state_changed,
        )
    )
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

    # Resume active control only when the user had explicitly enabled it.
    # The offline guard runs before the original controller can write.
    await controller.async_control_tick()

    # The bundled frontend cards are optional and must never prevent the
    # optimizer itself from loading.
    try:
        await async_register_history_card(hass)
    except Exception:  # noqa: BLE001
        _LOGGER.exception(
            "Could not register the NOAH Optimizer frontend cards"
        )

    # The dashboard is optional and must never prevent the optimizer itself
    # from loading.
    try:
        await async_ensure_dashboard(
            hass,
            entry,
        )
    except Exception:  # noqa: BLE001
        _LOGGER.exception(
            "Could not create the NOAH Optimizer dashboard"
        )

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: NoahOptimizerConfigEntry,
) -> bool:
    """Unload the Growatt NOAH Optimizer."""

    controller = getattr(entry.runtime_data, "controller", None)
    if controller is not None:
        try:
            await controller.async_shutdown()
        except Exception:  # noqa: BLE001
            _LOGGER.exception(
                "Could not shut down the NOAH offline guard"
            )

    # Persist the latest PV-learning and plan-history state before a controlled
    # reload or Home Assistant shutdown.
    try:
        await entry.runtime_data.async_shutdown()
    except Exception:  # noqa: BLE001
        _LOGGER.exception(
            "Could not persist optimizer state while unloading"
        )

    unload_ok = (
        await hass.config_entries.async_unload_platforms(
            entry,
            PLATFORMS,
        )
    )

    if unload_ok:
        heating = getattr(entry.runtime_data, "heating", None)
        if heating is not None:
            await heating.async_shutdown()
        remove_dashboard_panel(hass)
        remove_history_card(hass)
        async_unregister_history_store(hass, entry.entry_id)

    return unload_ok
