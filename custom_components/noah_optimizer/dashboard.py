"""Dashboard support for the Growatt NOAH Optimizer."""

from __future__ import annotations

from copy import deepcopy
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

from .const import CONF_DASHBOARD_SHOW_IN_SIDEBAR, DOMAIN

_LOGGER = logging.getLogger(__name__)

DASHBOARD_URL_PATH = "noah-optimizer"
DASHBOARD_TITLE = "NOAH Optimizer"
DASHBOARD_ICON = "mdi:home-battery"

DASHBOARD_STORAGE_VERSION = 1
DASHBOARD_STORAGE_KEY = f"{DOMAIN}.dashboard"
DASHBOARD_TEMPLATE_VERSION = 8

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
    "__EXPECTED_LOAD_ENERGY__": ("sensor", "expected_load_energy"),
    "__FORECAST_MARGIN__": ("sensor", "forecast_margin"),
    "__FORECAST_COVERAGE__": ("sensor", "forecast_coverage"),
    "__REQUIRED_CHARGE_POWER__": ("sensor", "required_charge_power"),
    "__MINUTES_TO_TARGET__": ("sensor", "minutes_to_target"),
    "__DYNAMIC_SOC_TARGET__": ("sensor", "dynamic_soc_target"),
    "__SOC_DEVIATION__": ("sensor", "soc_deviation"),
    "__DYNAMIC_REQUIRED_CHARGE_POWER__": (
        "sensor",
        "dynamic_required_charge_power",
    ),
    "__DYNAMIC_SOC_STATUS__": ("sensor", "dynamic_soc_status"),
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
    "__CRITICAL_DATA_OK__": ("binary_sensor", "critical_data_ok"),
    "__FORECAST_AVAILABLE__": ("binary_sensor", "forecast_available"),
    "__ACTUATOR_AVAILABLE__": ("binary_sensor", "actuator_available"),
    "__OPTIMIZER_ENABLED__": ("switch", "optimizer_enabled"),
    "__CONTROL_ENABLED__": ("switch", "control_enabled"),
    "__DYNAMIC_SOC_ENABLED__": ("switch", "dynamic_soc_enabled"),
    "__OPTIMIZER_MODE__": ("select", "optimizer_mode"),
    "__BATTERY_CAPACITY__": ("number", "battery_capacity"),
    "__TARGET_SOC__": ("number", "target_soc"),
    "__MIN_SOC__": ("number", "min_soc"),
    "__CHARGE_EFFICIENCY__": ("number", "charge_efficiency"),
    "__FORECAST_FACTOR__": ("number", "forecast_factor"),
    "__FORECAST_SAFETY__": ("number", "forecast_safety"),
    "__RELEASE_MARGIN__": ("number", "release_margin"),
    "__EXPECTED_DAY_LOAD__": ("number", "expected_day_load"),
    "__GRID_RESERVE__": ("number", "grid_reserve"),
    "__MAX_OUTPUT__": ("number", "max_output"),
    "__NIGHT_MAX_OUTPUT__": ("number", "night_max_output"),
    "__MANUAL_OUTPUT__": ("number", "manual_output"),
    "__COMMAND_STEP__": ("number", "command_step"),
    "__COMMAND_DEADBAND__": ("number", "command_deadband"),
    "__DYNAMIC_SOC_CATCHUP_HOURS__": (
        "number",
        "dynamic_soc_catchup_hours",
    ),
}


class NoahDashboardStorage(LovelaceConfig):
    """Storage-backed Lovelace config owned by this integration."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize dashboard storage."""
        super().__init__(hass, DASHBOARD_URL_PATH, None)
        self._store = Store[dict[str, Any]](
            hass,
            DASHBOARD_STORAGE_VERSION,
            DASHBOARD_STORAGE_KEY,
        )
        self._data: dict[str, Any] | None = None
        self._json_config: json_fragment | None = None

    @property
    def url_path(self) -> str:
        """Return dashboard URL path."""
        return DASHBOARD_URL_PATH

    @property
    def mode(self) -> str:
        """Return Lovelace mode."""
        return MODE_STORAGE

    async def _async_load_data(self) -> dict[str, Any]:
        """Load dashboard data from storage."""
        if self._data is None:
            stored = await self._store.async_load()
            self._data = stored or {
                "config": None,
                "template_version": 0,
            }

        return self._data

    async def async_get_template_version(self) -> int:
        """Return the version of the default template already migrated."""
        data = await self._async_load_data()
        try:
            return int(data.get("template_version", 0))
        except (TypeError, ValueError):
            return 0

    async def async_get_info(self) -> dict[str, Any]:
        """Return dashboard information."""
        try:
            config = await self.async_load(False)
        except ConfigNotFound:
            return {"mode": "auto-gen"}

        return {
            "mode": self.mode,
            "views": len(config.get("views", [])),
        }

    async def async_load(self, force: bool) -> dict[str, Any]:
        """Load dashboard configuration."""
        del force

        if self.hass.config.recovery_mode:
            raise ConfigNotFound

        data = await self._async_load_data()
        config = data.get("config")

        if not isinstance(config, dict):
            raise ConfigNotFound

        return config

    async def async_json(self, force: bool) -> json_fragment:
        """Return dashboard configuration as JSON."""
        config = await self.async_load(force)

        if self._json_config is None:
            self._json_config = json_fragment(json_bytes(config))

        return self._json_config

    async def async_save(self, config: dict[str, Any]) -> None:
        """Save dashboard configuration."""
        if self.hass.config.recovery_mode:
            raise HomeAssistantError(
                "Saving the NOAH dashboard is not supported in recovery mode"
            )

        if not isinstance(config, dict):
            raise HomeAssistantError(
                "The NOAH dashboard configuration must be an object"
            )

        data = await self._async_load_data()
        data["config"] = config
        data["template_version"] = DASHBOARD_TEMPLATE_VERSION

        self._json_config = None
        self._config_updated()
        await self._store.async_save(data)

    async def async_delete(self) -> None:
        """Delete stored dashboard configuration."""
        if self.hass.config.recovery_mode:
            raise HomeAssistantError(
                "Deleting the NOAH dashboard is not supported in recovery mode"
            )

        await self._store.async_remove()
        self._data = {
            "config": None,
            "template_version": 0,
        }
        self._json_config = None
        self._config_updated()


def _resolve_entities(hass: HomeAssistant, entry: ConfigEntry) -> dict[str, str]:
    """Resolve optimizer entity IDs from stable unique IDs."""
    registry = er.async_get(hass)
    resolved: dict[str, str] = {}

    for token, (entity_domain, unique_id_suffix) in ENTITY_TOKENS.items():
        unique_id = f"{entry.entry_id}_{unique_id_suffix}"
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


def _replace_tokens(value: Any, replacements: dict[str, str]) -> Any:
    """Replace entity tokens recursively."""
    if isinstance(value, str):
        result = value
        for token, entity_id in replacements.items():
            result = result.replace(token, entity_id)
        return result

    if isinstance(value, list):
        return [_replace_tokens(item, replacements) for item in value]

    if isinstance(value, dict):
        return {
            key: _replace_tokens(item, replacements)
            for key, item in value.items()
        }

    return value


def _dashboard_template_for_language(hass: HomeAssistant) -> Path:
    """Return dashboard template matching Home Assistant language."""
    language = (hass.config.language or "en").lower()
    if language.startswith("de"):
        return DASHBOARD_TEMPLATE_DE
    return DASHBOARD_TEMPLATE_EN


async def _async_build_dashboard_config(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> dict[str, Any]:
    """Build initial dashboard configuration."""
    replacements = _resolve_entities(hass, entry)
    template_path = _dashboard_template_for_language(hass)
    template = await hass.async_add_executor_job(load_yaml_dict, template_path)
    return _replace_tokens(template, replacements)


def _iter_dicts(value: Any):
    """Yield all nested dictionaries."""
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _iter_dicts(child)
    elif isinstance(value, list):
        for child in value:
            yield from _iter_dicts(child)


def _entity_from_row(row: Any) -> str | None:
    """Return an entity ID from an entities-card row."""
    if isinstance(row, str):
        return row
    if isinstance(row, dict):
        entity = row.get("entity")
        return entity if isinstance(entity, str) else None
    return None


def _card_contains_entity(card: dict[str, Any], entity_id: str) -> bool:
    """Return whether a card references an entity."""
    for item in _iter_dicts(card):
        if item.get("entity") == entity_id:
            return True

    entities = card.get("entities")
    if isinstance(entities, list):
        return any(_entity_from_row(row) == entity_id for row in entities)

    return False


def _append_entity_row(
    card: dict[str, Any],
    entity_id: str,
    name: str,
) -> bool:
    """Append an entities-card row if it does not already exist."""
    entities = card.get("entities")
    if not isinstance(entities, list):
        return False

    if any(_entity_from_row(row) == entity_id for row in entities):
        return False

    entities.append({"entity": entity_id, "name": name})
    return True


def _localized_dynamic_labels(hass: HomeAssistant) -> dict[str, str]:
    """Return labels used by dashboard migration."""
    if (hass.config.language or "en").lower().startswith("de"):
        return {
            "dynamic_switch": "Dynamische SOC-Steuerung aktiv",
            "dynamic_target": "Dynamisches SOC-Soll",
            "soc_deviation": "SOC-Abweichung",
            "dynamic_status": "SOC-Ladeplan",
            "dynamic_power": "Dynamisch erforderliche Ladeleistung",
            "catchup_hours": "SOC-Nachholzeit",
            "chart_title": "Dynamischer SOC-Ladeplan",
            "actual_soc": "Ist-SOC",
            "target_soc": "Dynamisches Soll",
            "final_target_soc": "Ziel-SOC",
        }

    return {
        "dynamic_switch": "Dynamic SOC control enabled",
        "dynamic_target": "Dynamic SOC target",
        "soc_deviation": "SOC deviation",
        "dynamic_status": "SOC schedule status",
        "dynamic_power": "Dynamic required charging power",
        "catchup_hours": "SOC catch-up time",
        "chart_title": "Dynamic SOC charging schedule",
        "actual_soc": "Actual SOC",
        "target_soc": "Dynamic target",
        "final_target_soc": "Target SOC",
    }


def _dynamic_soc_chart(
    replacements: dict[str, str],
    labels: dict[str, str],
) -> dict[str, Any]:
    """Return the Beta 8 dynamic-SOC chart card."""
    return {
        "type": "custom:apexcharts-card",
        "section_mode": True,
        "header": {
            "show": True,
            "title": labels["chart_title"],
            "show_states": True,
            "colorize_states": True,
        },
        "graph_span": "24h",
        "span": {"start": "day"},
        "now": {"show": True},
        "yaxis": [
            {
                "id": "soc",
                "min": 0,
                "max": 100,
                "decimals": 0,
            }
        ],
        "series": [
            {
                "entity": replacements["__SOC__"],
                "name": labels["actual_soc"],
                "yaxis_id": "soc",
                "type": "line",
                "stroke_width": 2,
                "group_by": {"duration": "5min", "func": "avg"},
            },
            {
                "entity": replacements["__DYNAMIC_SOC_TARGET__"],
                "name": labels["target_soc"],
                "yaxis_id": "soc",
                "type": "line",
                "curve": "stepline",
                "stroke_width": 3,
                "group_by": {"duration": "5min", "func": "avg"},
            },
            {
                "entity": replacements["__TARGET_SOC__"],
                "name": labels["final_target_soc"],
                "yaxis_id": "soc",
                "type": "line",
                "curve": "stepline",
                "stroke_width": 1,
                "group_by": {"duration": "5min", "func": "avg"},
            },
        ],
    }


def _patch_status_markdown(
    content: str,
    replacements: dict[str, str],
    german: bool,
) -> tuple[str, bool]:
    """Add Beta 8 mode and SOC values to an existing status markdown card."""
    changed = False

    if "'soc_catchup'" not in content:
        if german and "'blended_reserve': 'Gleitende Reserve'" in content:
            content = content.replace(
                "'blended_reserve': 'Gleitende Reserve'",
                "'blended_reserve': 'Gleitende Reserve',\n"
                "                'soc_catchup': 'SOC-Nachladung'",
            )
            changed = True
        elif not german and "'blended_reserve': 'Blended reserve'" in content:
            content = content.replace(
                "'blended_reserve': 'Blended reserve'",
                "'blended_reserve': 'Blended reserve',\n"
                "                'soc_catchup': 'SOC catch-up'",
            )
            changed = True

    dynamic_entity = replacements["__DYNAMIC_SOC_TARGET__"]
    if dynamic_entity not in content:
        soc_deviation_entity = replacements["__SOC_DEVIATION__"]
        soc_status_entity = replacements["__DYNAMIC_SOC_STATUS__"]
        dynamic_power_entity = replacements["__DYNAMIC_REQUIRED_CHARGE_POWER__"]

        if german:
            anchor = "**Prognosemarge:**"
            status_expression = (
                "{{ {'ahead': 'Vor Ladeplan', 'on_track': 'Im Ladeplan', "
                "'behind': 'Hinter Ladeplan'}.get("
                f"states('{soc_status_entity}'), states('{soc_status_entity}')) }}"
            )
            addition = (
                f"**Dynamisches SOC-Soll:** "
                f"{{{{ states('{dynamic_entity}') }}}} %\n"
                f"**SOC-Abweichung:** "
                f"{{{{ states('{soc_deviation_entity}') }}}} %\n"
                f"**SOC-Ladeplan:** {status_expression}\n"
                "**Dynamisch erforderliche Ladeleistung:** "
                f"{{{{ states('{dynamic_power_entity}') }}}} W\n\n"
            )
        else:
            anchor = "**Forecast margin:**"
            status_expression = (
                "{{ {'ahead': 'Ahead of schedule', 'on_track': 'On schedule', "
                "'behind': 'Behind schedule'}.get("
                f"states('{soc_status_entity}'), states('{soc_status_entity}')) }}"
            )
            addition = (
                f"**Dynamic SOC target:** "
                f"{{{{ states('{dynamic_entity}') }}}} %\n"
                f"**SOC deviation:** "
                f"{{{{ states('{soc_deviation_entity}') }}}} %\n"
                f"**SOC schedule:** {status_expression}\n"
                "**Dynamic required charging power:** "
                f"{{{{ states('{dynamic_power_entity}') }}}} W\n\n"
            )

        anchor_index = content.find(anchor)
        if anchor_index >= 0:
            line_end = content.find("\n", anchor_index)
            if line_end >= 0:
                content = content[: line_end + 1] + addition + content[line_end + 1 :]
            else:
                content += "\n" + addition
            changed = True

    return content, changed


def _migrate_dashboard_to_beta8(
    hass: HomeAssistant,
    config: dict[str, Any],
    replacements: dict[str, str],
) -> tuple[dict[str, Any], bool]:
    """Apply targeted Beta 8 additions without replacing user customizations."""
    migrated = deepcopy(config)
    changed = False
    labels = _localized_dynamic_labels(hass)
    german = (hass.config.language or "en").lower().startswith("de")

    # Beta 7 compatibility: repair the reversed Beta 6 battery mapping only
    # when the exact old mapping is still present.
    for item in _iter_dicts(migrated):
        if item.get("type") != "custom:power-flow-card-plus":
            continue

        entities = item.get("entities")
        if not isinstance(entities, dict):
            continue

        battery = entities.get("battery")
        if not isinstance(battery, dict):
            continue

        battery_entity = battery.get("entity")
        if not isinstance(battery_entity, dict):
            continue

        if (
            battery_entity.get("consumption")
            == replacements["__CHARGING_POWER__"]
            and battery_entity.get("production")
            == replacements["__DISCHARGING_POWER__"]
        ):
            battery_entity["consumption"] = replacements["__DISCHARGING_POWER__"]
            battery_entity["production"] = replacements["__CHARGING_POWER__"]
            changed = True

    # Add the new Beta 8 entities to the existing cards where possible.
    for item in _iter_dicts(migrated):
        if item.get("type") == "entities":
            if (
                _card_contains_entity(item, replacements["__OPTIMIZER_ENABLED__"])
                and _card_contains_entity(item, replacements["__CONTROL_ENABLED__"])
            ):
                changed |= _append_entity_row(
                    item,
                    replacements["__DYNAMIC_SOC_ENABLED__"],
                    labels["dynamic_switch"],
                )

            if (
                _card_contains_entity(item, replacements["__FORECAST_REMAINING__"])
                and _card_contains_entity(item, replacements["__FORECAST_MARGIN__"])
            ):
                changed |= _append_entity_row(
                    item,
                    replacements["__DYNAMIC_SOC_TARGET__"],
                    labels["dynamic_target"],
                )
                changed |= _append_entity_row(
                    item,
                    replacements["__SOC_DEVIATION__"],
                    labels["soc_deviation"],
                )
                changed |= _append_entity_row(
                    item,
                    replacements["__DYNAMIC_SOC_STATUS__"],
                    labels["dynamic_status"],
                )
                changed |= _append_entity_row(
                    item,
                    replacements["__DYNAMIC_REQUIRED_CHARGE_POWER__"],
                    labels["dynamic_power"],
                )

            if (
                _card_contains_entity(item, replacements["__BATTERY_CAPACITY__"])
                and _card_contains_entity(item, replacements["__COMMAND_DEADBAND__"])
            ):
                changed |= _append_entity_row(
                    item,
                    replacements["__DYNAMIC_SOC_CATCHUP_HOURS__"],
                    labels["catchup_hours"],
                )

        if item.get("type") == "markdown":
            content = item.get("content")
            if (
                isinstance(content, str)
                and replacements["__OUTPUT_TARGET__"] in content
                and replacements["__CONTROL_ENABLED__"] in content
            ):
                new_content, markdown_changed = _patch_status_markdown(
                    content,
                    replacements,
                    german,
                )
                if markdown_changed:
                    item["content"] = new_content
                    changed = True

    # Add one SOC history chart to the section that already contains the
    # existing SOC/forecast key figures. Do not add a duplicate if the user
    # already created a chart with the dynamic target entity.
    views = migrated.get("views")
    if isinstance(views, list):
        for view in views:
            if not isinstance(view, dict):
                continue

            sections = view.get("sections")
            if not isinstance(sections, list):
                continue

            for section in sections:
                if not isinstance(section, dict):
                    continue

                dynamic_chart_exists = any(
                    isinstance(card, dict)
                    and card.get("type") == "custom:apexcharts-card"
                    and _card_contains_entity(
                        card,
                        replacements["__DYNAMIC_SOC_TARGET__"],
                    )
                    for card in section.get("cards", [])
                )
                if dynamic_chart_exists:
                    continue

                if not (
                    _card_contains_entity(section, replacements["__SOC__"])
                    and _card_contains_entity(
                        section,
                        replacements["__FORECAST_COVERAGE__"],
                    )
                ):
                    continue

                cards = section.get("cards")
                if not isinstance(cards, list):
                    continue

                insert_index = min(2, len(cards))
                cards.insert(
                    insert_index,
                    _dynamic_soc_chart(replacements, labels),
                )
                changed = True
                break

    return migrated, changed


async def async_ensure_dashboard(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> None:
    """Create, migrate, and register the NOAH dashboard panel."""
    if hass.config.recovery_mode:
        return

    lovelace_data = hass.data.get(LOVELACE_DATA)
    if lovelace_data is None:
        raise HomeAssistantError("Lovelace is not available")

    existing = lovelace_data.dashboards.get(DASHBOARD_URL_PATH)
    if existing is not None:
        if isinstance(existing, NoahDashboardStorage):
            return
        raise HomeAssistantError(
            "Cannot register the NOAH Optimizer dashboard because "
            f"/{DASHBOARD_URL_PATH} is already used by another dashboard"
        )

    if frontend.async_panel_exists(hass, DASHBOARD_URL_PATH):
        raise HomeAssistantError(
            "Cannot register the NOAH Optimizer dashboard because "
            f"/{DASHBOARD_URL_PATH} is already used by another panel"
        )

    dashboard = NoahDashboardStorage(hass)
    replacements = _resolve_entities(hass, entry)

    try:
        dashboard_config = await dashboard.async_load(False)
        template_version = await dashboard.async_get_template_version()

        if template_version < DASHBOARD_TEMPLATE_VERSION:
            dashboard_config, changed = _migrate_dashboard_to_beta8(
                hass,
                dashboard_config,
                replacements,
            )

            # Save even when no visible card needed changing so this migration
            # is not repeated on every Home Assistant restart.
            await dashboard.async_save(dashboard_config)

            if changed:
                _LOGGER.info(
                    "Migrated NOAH Optimizer dashboard to template version %s",
                    DASHBOARD_TEMPLATE_VERSION,
                )

    except ConfigNotFound:
        dashboard_config = await _async_build_dashboard_config(hass, entry)
        await dashboard.async_save(dashboard_config)

    lovelace_data.dashboards[DASHBOARD_URL_PATH] = dashboard

    try:
        frontend.async_register_built_in_panel(
            hass,
            "lovelace",
            sidebar_title=DASHBOARD_TITLE,
            sidebar_icon=DASHBOARD_ICON,
            frontend_url_path=DASHBOARD_URL_PATH,
            require_admin=False,
            config={"mode": MODE_STORAGE},
            show_in_sidebar=bool(
                entry.data.get(CONF_DASHBOARD_SHOW_IN_SIDEBAR, True)
            ),
        )
    except ValueError:
        lovelace_data.dashboards.pop(DASHBOARD_URL_PATH, None)
        raise

    _LOGGER.info(
        "NOAH Optimizer dashboard available at /%s",
        DASHBOARD_URL_PATH,
    )


def remove_dashboard_panel(hass: HomeAssistant) -> None:
    """Remove runtime panel registration while preserving stored config."""
    lovelace_data = hass.data.get(LOVELACE_DATA)
    if lovelace_data is None:
        return

    dashboard = lovelace_data.dashboards.get(DASHBOARD_URL_PATH)
    if not isinstance(dashboard, NoahDashboardStorage):
        return

    lovelace_data.dashboards.pop(DASHBOARD_URL_PATH, None)

    if frontend.async_panel_exists(hass, DASHBOARD_URL_PATH):
        frontend.async_remove_panel(hass, DASHBOARD_URL_PATH)
