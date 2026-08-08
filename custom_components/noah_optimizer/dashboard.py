"""Dashboard support for the Growatt NOAH Optimizer."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from homeassistant.components import frontend
from homeassistant.components.lovelace.const import (
    LOVELACE_DATA,
    MODE_STORAGE,
    ConfigNotFound,
)
from homeassistant.components.lovelace.dashboard import LovelaceConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.json import json_bytes, json_fragment
from homeassistant.helpers.storage import Store
from homeassistant.util.yaml import load_yaml_dict

from .const import (
    CONF_DASHBOARD_SHOW_IN_SIDEBAR,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

DASHBOARD_URL_PATH = "noah-optimizer"
DASHBOARD_TITLE = "NOAH Optimizer"
DASHBOARD_ICON = "mdi:home-battery"

DASHBOARD_STORAGE_VERSION = 1
DASHBOARD_STORAGE_KEY = f"{DOMAIN}.dashboard"

DASHBOARD_TEMPLATE_DE = Path(__file__).with_name("dashboard_de.yaml")
DASHBOARD_TEMPLATE_EN = Path(__file__).with_name("dashboard_en.yaml")

# token -> (entity domain, integration unique-id suffix)
ENTITY_TOKENS: dict[str, tuple[str, str]] = {
    "__GRID_POWER__": ("sensor", "grid_power"),
    "__GRID_IMPORT__": ("sensor", "grid_import"),
    "__GRID_EXPORT__": ("sensor", "grid_export"),
    "__SOLAR_POWER__": ("sensor", "solar_power"),
    "__OUTPUT_POWER__": ("sensor", "output_power"),
    "__SOC__": ("sensor", "soc"),
    "__CHARGING_POWER__": ("sensor", "charging_power"),
    "__DISCHARGING_POWER__": ("sensor", "discharge_power"),
    "__BATTERY_POWER__": ("sensor", "battery_power"),
    "__HOME_LOAD__": ("sensor", "home_load"),
    "__FORECAST_REMAINING__": ("sensor", "forecast_remaining"),
    "__GRID_POWER_AVERAGE__": ("sensor", "grid_power_average"),
    "__HOURS_TO_SUNSET__": ("sensor", "hours_to_sunset"),
    "__AVAILABLE_BATTERY_ENERGY__": (
        "sensor",
        "available_battery_energy",
    ),
    "__CHARGE_NEED__": ("sensor", "charge_need"),
    "__EFFECTIVE_FORECAST__": ("sensor", "effective_forecast"),
    "__EXPECTED_LOAD_ENERGY__": (
        "sensor",
        "expected_load_energy",
    ),
    "__FORECAST_MARGIN__": ("sensor", "forecast_margin"),
    "__FORECAST_COVERAGE__": ("sensor", "forecast_coverage"),
    "__REQUIRED_CHARGE_POWER__": (
        "sensor",
        "required_charge_power",
    ),
    "__MINUTES_TO_TARGET__": ("sensor", "minutes_to_target"),
    "__SELF_CONSUMPTION_TARGET__": (
        "sensor",
        "self_consumption_target",
    ),
    "__CHARGE_PRIORITY_TARGET__": (
        "sensor",
        "charge_priority_target",
    ),
    "__OUTPUT_TARGET__": ("sensor", "output_target"),
    "__CONTROLLER_MODE__": ("sensor", "controller_mode"),
    "__DATA_STATUS__": ("sensor", "data_status"),
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
    "__OPTIMIZER_ENABLED__": (
        "switch",
        "optimizer_enabled",
    ),
    "__CONTROL_ENABLED__": (
        "switch",
        "control_enabled",
    ),
    "__OPTIMIZER_MODE__": (
        "select",
        "optimizer_mode",
    ),
    "__BATTERY_CAPACITY__": (
        "number",
        "battery_capacity",
    ),
    "__TARGET_SOC__": ("number", "target_soc"),
    "__MIN_SOC__": ("number", "min_soc"),
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
    "__MAX_OUTPUT__": ("number", "max_output"),
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


class NoahDashboardStorage(LovelaceConfig):
    """Storage-backed Lovelace config owned by this integration.

    It intentionally does not register itself in Home Assistant's
    DashboardsCollection. This avoids maintaining a second,
    unsynchronised DashboardsCollection while still using the normal
    Lovelace config/save WebSocket API for this panel.
    """

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the dashboard storage."""

        # Keep config=None so this integration-managed panel is not exposed
        # as a normal user-created dashboard metadata entry.
        super().__init__(
            hass,
            DASHBOARD_URL_PATH,
            None,
        )

        self._store = Store[dict[str, Any]](
            hass,
            DASHBOARD_STORAGE_VERSION,
            DASHBOARD_STORAGE_KEY,
        )

        self._data: dict[str, Any] | None = None
        self._json_config: json_fragment | None = None

    @property
    def url_path(self) -> str:
        """Return the dashboard URL path."""

        return DASHBOARD_URL_PATH

    @property
    def mode(self) -> str:
        """Return the Lovelace mode."""

        return MODE_STORAGE

    async def _async_load_data(
        self,
    ) -> dict[str, Any]:
        """Load dashboard data from storage."""

        if self._data is None:
            stored = await self._store.async_load()

            self._data = (
                stored
                or {
                    "config": None,
                }
            )

        return self._data

    async def async_get_info(
        self,
    ) -> dict[str, Any]:
        """Return dashboard information."""

        try:
            config = await self.async_load(
                False
            )

        except ConfigNotFound:
            return {
                "mode": "auto-gen",
            }

        return {
            "mode": self.mode,
            "views": len(
                config.get(
                    "views",
                    [],
                )
            ),
        }

    async def async_load(
        self,
        force: bool,
    ) -> dict[str, Any]:
        """Load the dashboard configuration."""

        del force

        if self.hass.config.recovery_mode:
            raise ConfigNotFound

        data = await self._async_load_data()

        config = data.get(
            "config"
        )

        if not isinstance(
            config,
            dict,
        ):
            raise ConfigNotFound

        return config

    async def async_json(
        self,
        force: bool,
    ) -> json_fragment:
        """Return the dashboard configuration as JSON."""

        config = await self.async_load(
            force
        )

        if self._json_config is None:
            self._json_config = json_fragment(
                json_bytes(
                    config
                )
            )

        return self._json_config

    async def async_save(
        self,
        config: dict[str, Any],
    ) -> None:
        """Save the dashboard configuration."""

        if self.hass.config.recovery_mode:
            raise HomeAssistantError(
                "Saving the NOAH dashboard is not supported "
                "in recovery mode"
            )

        if not isinstance(
            config,
            dict,
        ):
            raise HomeAssistantError(
                "The NOAH dashboard configuration must be an object"
            )

        data = await self._async_load_data()

        data["config"] = config

        self._json_config = None
        self._config_updated()

        await self._store.async_save(
            data
        )

    async def async_delete(
        self,
    ) -> None:
        """Delete the stored dashboard configuration."""

        if self.hass.config.recovery_mode:
            raise HomeAssistantError(
                "Deleting the NOAH dashboard is not supported "
                "in recovery mode"
            )

        await self._store.async_remove()

        self._data = {
            "config": None,
        }

        self._json_config = None
        self._config_updated()


def _resolve_entities(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> dict[str, str]:
    """Resolve optimizer entity IDs from stable unique IDs."""

    registry = er.async_get(
        hass
    )

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

    if isinstance(
        value,
        str,
    ):
        result = value

        for token, entity_id in replacements.items():
            result = result.replace(
                token,
                entity_id,
            )

        return result

    if isinstance(
        value,
        list,
    ):
        return [
            _replace_tokens(
                item,
                replacements,
            )
            for item in value
        ]

    if isinstance(
        value,
        dict,
    ):
        return {
            key: _replace_tokens(
                item,
                replacements,
            )
            for key, item in value.items()
        }

    return value


def _dashboard_template_for_language(
    hass: HomeAssistant,
) -> Path:
    """Return the dashboard template matching the HA language."""

    language = (
        hass.config.language
        or "en"
    ).lower()

    if language.startswith(
        "de"
    ):
        return DASHBOARD_TEMPLATE_DE

    return DASHBOARD_TEMPLATE_EN


async def _async_build_dashboard_config(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> dict[str, Any]:
    """Build the initial dashboard configuration."""

    replacements = _resolve_entities(
        hass,
        entry,
    )

    template_path = (
        _dashboard_template_for_language(
            hass
        )
    )

    template = await hass.async_add_executor_job(
        load_yaml_dict,
        template_path,
    )

    return _replace_tokens(
        template,
        replacements,
    )


async def async_ensure_dashboard(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> None:
    """Create and register the NOAH dashboard panel."""

    if hass.config.recovery_mode:
        return

    lovelace_data = hass.data.get(
        LOVELACE_DATA
    )

    if lovelace_data is None:
        raise HomeAssistantError(
            "Lovelace is not available"
        )

    existing = (
        lovelace_data.dashboards.get(
            DASHBOARD_URL_PATH
        )
    )

    if existing is not None:

        if isinstance(
            existing,
            NoahDashboardStorage,
        ):
            return

        raise HomeAssistantError(
            "Cannot register the NOAH Optimizer dashboard because "
            f"/{DASHBOARD_URL_PATH} is already used by another dashboard"
        )

    if frontend.async_panel_exists(
        hass,
        DASHBOARD_URL_PATH,
    ):
        raise HomeAssistantError(
            "Cannot register the NOAH Optimizer dashboard because "
            f"/{DASHBOARD_URL_PATH} is already used by another panel"
        )

    dashboard = NoahDashboardStorage(
        hass
    )

    try:
        await dashboard.async_load(
            False
        )

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

    lovelace_data.dashboards[
        DASHBOARD_URL_PATH
    ] = dashboard

    try:
        frontend.async_register_built_in_panel(
            hass,
            "lovelace",
            sidebar_title=DASHBOARD_TITLE,
            sidebar_icon=DASHBOARD_ICON,
            frontend_url_path=DASHBOARD_URL_PATH,
            require_admin=False,
            config={
                "mode": MODE_STORAGE,
            },
            show_in_sidebar=bool(
                entry.data.get(
                    CONF_DASHBOARD_SHOW_IN_SIDEBAR,
                    True,
                )
            ),
        )

    except ValueError:
        lovelace_data.dashboards.pop(
            DASHBOARD_URL_PATH,
            None,
        )
        raise

    _LOGGER.info(
        "NOAH Optimizer dashboard available at /%s",
        DASHBOARD_URL_PATH,
    )


def remove_dashboard_panel(
    hass: HomeAssistant,
) -> None:
    """Remove the runtime registration of the dashboard panel.

    The stored dashboard configuration is intentionally kept so user
    customisations survive integration reloads and Home Assistant restarts.
    """

    lovelace_data = hass.data.get(
        LOVELACE_DATA
    )

    if lovelace_data is None:
        return

    dashboard = (
        lovelace_data.dashboards.get(
            DASHBOARD_URL_PATH
        )
    )

    if not isinstance(
        dashboard,
        NoahDashboardStorage,
    ):
        return

    lovelace_data.dashboards.pop(
        DASHBOARD_URL_PATH,
        None,
    )

    if frontend.async_panel_exists(
        hass,
        DASHBOARD_URL_PATH,
    ):
        frontend.async_remove_panel(
            hass,
            DASHBOARD_URL_PATH,
        )