"""Dashboard template-v18 migration for the NOAH Optimizer.

This module keeps the existing dashboard implementation intact and adds the
one-time v18 migration that realigns stale colors on recognized generated
NOAH standard charts. It can be folded back into dashboard.py in a later
cleanup without changing stored dashboard data.
"""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components import frontend
from homeassistant.components.lovelace.const import (
    LOVELACE_DATA,
    MODE_STORAGE,
    ConfigNotFound,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from . import dashboard as _dashboard
from .const import CONF_DASHBOARD_SHOW_IN_SIDEBAR

_LOGGER = logging.getLogger(__name__)

DASHBOARD_TEMPLATE_VERSION = 18

# NoahDashboardStorage.async_save() reads this global from dashboard.py.
# Set it before any dashboard is loaded/saved so both new and existing
# installations persist template version 18 consistently.
_dashboard.DASHBOARD_TEMPLATE_VERSION = DASHBOARD_TEMPLATE_VERSION

def _apply_standard_series_colors_v18(
    config: dict[str, Any],
    replacements: dict[str, str],
) -> bool:
    """Align the stable NOAH palette on recognized standard ApexCharts cards.

    Template v18 intentionally replaces stale explicit colors only when a
    generated NOAH standard chart can be identified by its known title and
    entity set. Additional or user-created ApexCharts cards are left untouched.
    """
    changed = False

    for card in _dashboard._iter_dicts(config):
        if card.get("type") != "custom:apexcharts-card":
            continue
        series = card.get("series")
        if not isinstance(series, list):
            continue

        header = card.get("header")
        title = header.get("title") if isinstance(header, dict) else None
        entity_ids = {
            item.get("entity")
            for item in series
            if isinstance(item, dict) and isinstance(item.get("entity"), str)
        }

        colors: dict[str, str] | None = None
        mode: str | None = None

        forecast_generators = [
            item.get("data_generator")
            for item in series
            if isinstance(item, dict)
            and item.get("entity") == replacements["__FORECAST_CURVE__"]
            and isinstance(item.get("data_generator"), str)
        ]
        if (
            title in {"PV-Prognose", "PV forecast"}
            and {
                replacements["__FORECAST_CURVE__"],
                replacements["__SOLAR_POWER__"],
            }.issubset(entity_ids)
            and any("raw_power" in generator for generator in forecast_generators)
            and any("effective_power" in generator for generator in forecast_generators)
        ):
            mode = "forecast_curve"
        elif (
            title in {
                "Dynamischer SOC-Ladeplan",
                "Dynamic SOC charging schedule",
            }
            and {
                replacements["__SOC__"],
                replacements["__DYNAMIC_SOC_TARGET__"],
                replacements["__TARGET_SOC__"],
            }.issubset(entity_ids)
        ):
            colors = {
                replacements["__SOC__"]: "#2196F3",
                replacements["__DYNAMIC_SOC_TARGET__"]: "#009B21",
                replacements["__TARGET_SOC__"]: "#FF6A00",
            }
        elif (
            title in {
                "Energieplanung bis Sonnenuntergang",
                "Energy planning until sunset",
            }
            and {
                replacements["__EFFECTIVE_FORECAST__"],
                replacements["__CHARGE_NEED__"],
                replacements["__EXPECTED_LOAD_ENERGY__"],
                replacements["__FORECAST_MARGIN__"],
            }.issubset(entity_ids)
        ):
            colors = {
                replacements["__EFFECTIVE_FORECAST__"]: "#2196F3",
                replacements["__CHARGE_NEED__"]: "#009B21",
                replacements["__EXPECTED_LOAD_ENERGY__"]: "#FF6A00",
                replacements["__FORECAST_MARGIN__"]: "#FFD800",
            }
        elif (
            title in {"Leistung heute", "Power today"}
            and {
                replacements["__SOLAR_POWER__"],
                replacements["__OUTPUT_POWER__"],
                replacements["__GRID_IMPORT__"],
                replacements["__GRID_EXPORT__"],
                replacements["__BATTERY_POWER__"],
                replacements["__SOC__"],
            }.issubset(entity_ids)
        ):
            colors = {
                replacements["__SOLAR_POWER__"]: "#2196F3",
                replacements["__OUTPUT_POWER__"]: "#009B21",
                replacements["__GRID_IMPORT__"]: "#FF6A00",
                replacements["__GRID_EXPORT__"]: "#FFD800",
                replacements["__BATTERY_POWER__"]: "#00FFFF",
                replacements["__SOC__"]: "#B200FF",
            }
        elif (
            title in {"Reglerverhalten", "Controller behavior"}
            and {
                replacements["__OUTPUT_TARGET__"],
                replacements["__OUTPUT_POWER__"],
                replacements["__SELF_CONSUMPTION_TARGET__"],
                replacements["__CHARGE_PRIORITY_TARGET__"],
                replacements["__REQUIRED_CHARGE_POWER__"],
                replacements["__DYNAMIC_REQUIRED_CHARGE_POWER__"],
            }.issubset(entity_ids)
        ):
            colors = {
                replacements["__OUTPUT_TARGET__"]: "#2196F3",
                replacements["__OUTPUT_POWER__"]: "#009B21",
                replacements["__SELF_CONSUMPTION_TARGET__"]: "#FF6A00",
                replacements["__CHARGE_PRIORITY_TARGET__"]: "#FFD800",
                replacements["__REQUIRED_CHARGE_POWER__"]: "#00FFFF",
                replacements["__DYNAMIC_REQUIRED_CHARGE_POWER__"]: "#B200FF",
            }

        # Do not touch unrecognized/custom ApexCharts cards.
        if mode is None and colors is None:
            continue

        for item in series:
            if not isinstance(item, dict):
                continue

            entity_id = item.get("entity")
            color = None
            if mode == "forecast_curve":
                if entity_id == replacements["__FORECAST_CURVE__"]:
                    generator = item.get("data_generator")
                    if isinstance(generator, str) and "raw_power" in generator:
                        color = "#2196F3"
                    elif isinstance(generator, str) and "effective_power" in generator:
                        color = "#009B21"
                elif entity_id == replacements["__SOLAR_POWER__"]:
                    color = "#FF6A00"
            elif colors is not None and isinstance(entity_id, str):
                color = colors.get(entity_id)

            if color is not None and item.get("color") != color:
                item["color"] = color
                changed = True

    return changed


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

    existing = lovelace_data.dashboards.get(_dashboard.DASHBOARD_URL_PATH)
    if existing is not None:
        if isinstance(existing, _dashboard.NoahDashboardStorage):
            return
        raise HomeAssistantError(
            "Cannot register the NOAH Optimizer dashboard because "
            f"/{_dashboard.DASHBOARD_URL_PATH} is already used by another dashboard"
        )

    if frontend.async_panel_exists(hass, _dashboard.DASHBOARD_URL_PATH):
        raise HomeAssistantError(
            "Cannot register the NOAH Optimizer dashboard because "
            f"/{_dashboard.DASHBOARD_URL_PATH} is already used by another panel"
        )

    dashboard = _dashboard.NoahDashboardStorage(hass)
    replacements = _dashboard._resolve_entities(hass, entry)

    try:
        dashboard_config = await dashboard.async_load(False)
        template_version = await dashboard.async_get_template_version()

        if template_version < DASHBOARD_TEMPLATE_VERSION:
            dashboard_config, changed = _dashboard._migrate_dashboard_to_beta11(
                hass,
                dashboard_config,
                replacements,
            )
            changed |= _apply_standard_series_colors_v18(
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
        dashboard_config = await _dashboard._async_build_dashboard_config(
            hass,
            entry,
        )
        await dashboard.async_save(dashboard_config)

    lovelace_data.dashboards[_dashboard.DASHBOARD_URL_PATH] = dashboard

    try:
        frontend.async_register_built_in_panel(
            hass,
            "lovelace",
            sidebar_title=_dashboard.DASHBOARD_TITLE,
            sidebar_icon=_dashboard.DASHBOARD_ICON,
            frontend_url_path=_dashboard.DASHBOARD_URL_PATH,
            require_admin=False,
            config={"mode": MODE_STORAGE},
            show_in_sidebar=bool(
                entry.data.get(CONF_DASHBOARD_SHOW_IN_SIDEBAR, True)
            ),
        )
    except ValueError:
        lovelace_data.dashboards.pop(_dashboard.DASHBOARD_URL_PATH, None)
        raise

    _LOGGER.info(
        "NOAH Optimizer dashboard available at /%s",
        _dashboard.DASHBOARD_URL_PATH,
    )


def remove_dashboard_panel(hass: HomeAssistant) -> None:
    """Remove runtime panel registration while preserving stored config."""
    _dashboard.remove_dashboard_panel(hass)
