"""Dashboard support for the Growatt NOAH Optimizer."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from homeassistant.components import frontend
from homeassistant.components.lovelace.const import (
    CONF_REQUIRE_ADMIN,
    CONF_SHOW_IN_SIDEBAR,
    CONF_TITLE,
    CONF_URL_PATH,
    LOVELACE_DATA,
    MODE_STORAGE,
    ConfigNotFound,
)
from homeassistant.components.lovelace.dashboard import (
    DashboardsCollection,
    LovelaceStorage,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ICON
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import entity_registry as er
from homeassistant.util.yaml import load_yaml_dict

from .const import (
    CONF_DASHBOARD_SHOW_IN_SIDEBAR,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

DASHBOARD_URL_PATH = "noah-optimizer"
DASHBOARD_TITLE = "NOAH Optimizer"
DASHBOARD_ICON = "mdi:home-battery"

DASHBOARD_TEMPLATE = Path(__file__).with_name(
    "dashboard.yaml"
)


# token -> (entity domain, integration unique-id suffix)
ENTITY_TOKENS: dict[str, tuple[str, str]] = {
    # Base sensors
    "__GRID_POWER__": ("sensor", "grid_power"),
    "__GRID_IMPORT__": ("sensor", "grid_import"),
    "__GRID_EXPORT__": ("sensor", "grid_export"),
    "__SOLAR_POWER__": ("sensor", "solar_power"),
    "__OUTPUT_POWER__": ("sensor", "output_power"),
    "__SOC__": ("sensor", "soc"),
    "__CHARGING_POWER__": (
        "sensor",
        "charging_power",
    ),
    "__DISCHARGING_POWER__": (
        "sensor",
        "discharging_power",
    ),
    "__BATTERY_POWER__": (
        "sensor",
        "battery_power",
    ),
    "__HOME_LOAD__": ("sensor", "home_load"),
    "__FORECAST_REMAINING__": (
        "sensor",
        "forecast_remaining",
    ),

    # Calculation sensors
    "__GRID_POWER_AVERAGE__": (
        "sensor",
        "grid_power_average",
    ),
    "__HOURS_TO_SUNSET__": (
        "sensor",
        "hours_to_sunset",
    ),
    "__AVAILABLE_BATTERY_ENERGY__": (
        "sensor",
        "available_battery_energy",
    ),
    "__CHARGE_NEED__": (
        "sensor",
        "charge_need",
    ),
    "__EFFECTIVE_FORECAST__": (
        "sensor",
        "effective_forecast",
    ),
    "__EXPECTED_LOAD_ENERGY__": (
        "sensor",
        "expected_load_energy",
    ),
    "__FORECAST_MARGIN__": (
        "sensor",
        "forecast_margin",
    ),
    "__FORECAST_COVERAGE__": (
        "sensor",
        "forecast_coverage",
    ),
    "__REQUIRED_CHARGE_POWER__": (
        "sensor",
        "required_charge_power",
    ),
    "__MINUTES_TO_TARGET__": (
        "sensor",
        "minutes_to_target",
    ),
    "__SELF_CONSUMPTION_TARGET__": (
        "sensor",
        "self_consumption_target",
    ),
    "__CHARGE_PRIORITY_TARGET__": (
        "sensor",
        "charge_priority_target",
    ),
    "__OUTPUT_TARGET__": (
        "sensor",
        "output_target",
    ),
    "__CONTROLLER_MODE__": (
        "sensor",
        "controller_mode",
    ),
    "__DATA_STATUS__": (
        "sensor",
        "data_status",
    ),

    # Binary sensors
    "__CRITICAL_DATA_OK__": (
        "binary_sensor",
        "critical_data_ok",
    ),
    "__FORECAST_AVAILABLE__": (
        "binary_sensor",
        "forecast_available",
    ),
    "__ACTUATOR_AVAILABLE__": (
        "binary_sensor",
        "actuator_available",
    ),

    # Switches
    "__OPTIMIZER_ENABLED__": (
        "switch",
        "optimizer_enabled",
    ),
    "__CONTROL_ENABLED__": (
        "switch",
        "control_enabled",
    ),

    # Select
    "__OPTIMIZER_MODE__": (
        "select",
        "optimizer_mode",
    ),

    # Numbers
    "__BATTERY_CAPACITY__": (
        "number",
        "battery_capacity",
    ),
    "__TARGET_SOC__": (
        "number",
        "target_soc",
    ),
    "__MIN_SOC__": (
        "number",
        "min_soc",
    ),
    "__CHARGE_EFFICIENCY__": (
        "number",
        "charge_efficiency",
    ),
    "__FORECAST_FACTOR__": (
        "number",
        "forecast_factor",
    ),
    "__FORECAST_SAFETY__": (
        "number",
        "forecast_safety",
    ),
    "__RELEASE_MARGIN__": (
        "number",
        "release_margin",
    ),
    "__EXPECTED_DAY_LOAD__": (
        "number",
        "expected_day_load",
    ),
    "__GRID_RESERVE__": (
        "number",
        "grid_reserve",
    ),
    "__MAX_OUTPUT__": (
        "number",
        "max_output",
    ),
    "__NIGHT_MAX_OUTPUT__": (
        "number",
        "night_max_output",
    ),
    "__MANUAL_OUTPUT__": (
        "number",
        "manual_output",
    ),
    "__COMMAND_STEP__": (
        "number",
        "command_step",
    ),
    "__COMMAND_DEADBAND__": (
        "number",
        "command_deadband",
    ),
}


def _resolve_entities(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> dict[str, str]:
    """Resolve optimizer entity IDs from unique IDs."""

    registry = er.async_get(hass)

    resolved: dict[str, str] = {}

    for token, (
        entity_domain,
        unique_id_suffix,
    ) in ENTITY_TOKENS.items():
        unique_id = (
            f"{entry.entry_id}_{unique_id_suffix}"
        )

        entity_id = registry.async_get_entity_id(
            entity_domain,
            DOMAIN,
            unique_id,
        )

        if entity_id is None:
            raise HomeAssistantError(
                "Could not resolve dashboard entity "
                f"{entity_domain}:{unique_id}"
            )

        resolved[token] = entity_id

    return resolved


def _replace_tokens(
    value: Any,
    replacements: dict[str, str],
) -> Any:
    """Replace entity tokens recursively."""

    if isinstance(value, str):
        result = value

        for token, entity_id in replacements.items():
            result = result.replace(
                token,
                entity_id,
            )

        return result

    if isinstance(value, list):
        return [
            _replace_tokens(
                item,
                replacements,
            )
            for item in value
        ]

    if isinstance(value, dict):
        return {
            key: _replace_tokens(
                item,
                replacements,
            )
            for key, item in value.items()
        }

    return value


async def _async_build_dashboard_config(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> dict[str, Any]:
    """Build dashboard configuration."""

    replacements = _resolve_entities(
        hass,
        entry,
    )

    template = await hass.async_add_executor_job(
        load_yaml_dict,
        DASHBOARD_TEMPLATE,
    )

    return _replace_tokens(
        template,
        replacements,
    )


async def async_ensure_dashboard(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> None:
    """Create the NOAH dashboard if it does not exist."""

    lovelace_data = hass.data.get(
        LOVELACE_DATA
    )

    if lovelace_data is None:
        raise HomeAssistantError(
            "Lovelace is not available"
        )

    # Dashboard is already registered.
    # Never overwrite it, because the user may have edited it.
    if (
        DASHBOARD_URL_PATH
        in lovelace_data.dashboards
    ):
        _LOGGER.debug(
            "NOAH Optimizer dashboard already exists"
        )
        return

    dashboards = DashboardsCollection(hass)

    await dashboards.async_load()

    dashboard_item = next(
        (
            item
            for item
            in dashboards.async_items()
            if item.get(CONF_URL_PATH)
            == DASHBOARD_URL_PATH
        ),
        None,
    )

    if dashboard_item is None:
        if frontend.async_panel_exists(
            hass,
            DASHBOARD_URL_PATH,
        ):
            raise HomeAssistantError(
                "Cannot create NOAH Optimizer "
                "dashboard because the URL path "
                f"{DASHBOARD_URL_PATH} is already used"
            )

        dashboard_item = (
            await dashboards.async_create_item(
                {
                    CONF_TITLE:
                        DASHBOARD_TITLE,
                    CONF_ICON:
                        DASHBOARD_ICON,
                    CONF_URL_PATH:
                        DASHBOARD_URL_PATH,
                    CONF_REQUIRE_ADMIN:
                        False,
                    CONF_SHOW_IN_SIDEBAR:
                        bool(
                            entry.data.get(
                                CONF_DASHBOARD_SHOW_IN_SIDEBAR,
                                True,
                            )
                        ),
                }
            )
        )

    dashboard = LovelaceStorage(
        hass,
        dashboard_item,
    )

    lovelace_data.dashboards[
        DASHBOARD_URL_PATH
    ] = dashboard

    try:
        await dashboard.async_load(False)

    except ConfigNotFound:
        dashboard_config = (
            await _async_build_dashboard_config(
                hass,
                entry,
            )
        )

        await dashboard.async_save(
            dashboard_config
        )

    # The Lovelace integration has already finished loading its
    # dashboard collection before this custom integration starts.
    # Therefore register the panel in the current runtime as well.
    if not frontend.async_panel_exists(
        hass,
        DASHBOARD_URL_PATH,
    ):
        frontend.async_register_built_in_panel(
            hass,
            "lovelace",
            sidebar_title=dashboard_item[
                CONF_TITLE
            ],
            sidebar_icon=dashboard_item.get(
                CONF_ICON,
                DASHBOARD_ICON,
            ),
            frontend_url_path=DASHBOARD_URL_PATH,
            require_admin=dashboard_item.get(
                CONF_REQUIRE_ADMIN,
                False,
            ),
            config={
                "mode": MODE_STORAGE,
            },
            show_in_sidebar=dashboard_item.get(
                CONF_SHOW_IN_SIDEBAR,
                True,
            ),
        )

    _LOGGER.info(
        "NOAH Optimizer dashboard available at /%s",
        DASHBOARD_URL_PATH,
    )