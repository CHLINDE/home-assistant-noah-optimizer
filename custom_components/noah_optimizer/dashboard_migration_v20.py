"""Dashboard template-v20 migration for the bundled NOAH energy-flow card.

Template v20 replaces the generated Power Flow Card Plus card with the bundled
NOAH-specific energy-flow card. The new card models the actual NOAH topology:
PV enters the NOAH on the DC side and the NOAH-to-home line is driven only by
the measured AC ``output_power`` entity.

All older dashboard migrations remain active through dashboard_migration_v18.
"""

from __future__ import annotations

from typing import Any

# Importing the v19 migration module installs the stricter standard chart color
# migration before we extend dashboard.py with template v20 behavior.
from . import dashboard_migration_v18 as _previous_migration  # noqa: F401
from . import dashboard as _dashboard

DASHBOARD_TEMPLATE_VERSION = 20
_PATCH_MARKER = "_noah_template_v20_energy_flow_patch_installed"


def _energy_flow_labels(german: bool) -> dict[str, str]:
    """Return localized labels for the bundled energy-flow card."""
    if german:
        return {
            "grid": "Netz",
            "pv": "PV",
            "noah": "NOAH",
            "home": "Haus",
            "output": "Ausgang",
            "charging": "Laden",
            "discharging": "Entladen",
        }
    return {
        "grid": "Grid",
        "pv": "PV",
        "noah": "NOAH",
        "home": "Home",
        "output": "Output",
        "charging": "Charging",
        "discharging": "Discharging",
    }


def _energy_flow_card(
    replacements: dict[str, str],
    *,
    german: bool,
) -> dict[str, Any]:
    """Return the bundled NOAH-specific energy-flow card configuration."""
    return {
        "type": "custom:noah-energy-flow-card",
        "title": "Aktueller Energiefluss" if german else "Current energy flow",
        "entities": {
            "grid_import": replacements["__GRID_IMPORT__"],
            "grid_export": replacements["__GRID_EXPORT__"],
            "solar_power": replacements["__SOLAR_POWER__"],
            "output_power": replacements["__OUTPUT_POWER__"],
            "charging_power": replacements["__CHARGING_POWER__"],
            "discharging_power": replacements["__DISCHARGING_POWER__"],
            "soc": replacements["__SOC__"],
            "home_load": replacements["__HOME_LOAD__"],
        },
        "labels": _energy_flow_labels(german),
    }


def _is_generated_legacy_energy_flow(
    card: dict[str, Any],
    replacements: dict[str, str],
) -> bool:
    """Recognize the generated Power Flow Card Plus card conservatively."""
    if card.get("type") != "custom:power-flow-card-plus":
        return False
    if card.get("title") not in {"Aktueller Energiefluss", "Current energy flow"}:
        return False

    entities = card.get("entities")
    if not isinstance(entities, dict):
        return False

    grid = entities.get("grid")
    solar = entities.get("solar")
    battery = entities.get("battery")
    home = entities.get("home")
    if not all(isinstance(value, dict) for value in (grid, solar, battery, home)):
        return False

    grid_entity = grid.get("entity")
    battery_entity = battery.get("entity")
    if not isinstance(grid_entity, dict) or not isinstance(battery_entity, dict):
        return False

    return (
        grid_entity.get("consumption") == replacements["__GRID_IMPORT__"]
        and grid_entity.get("production") == replacements["__GRID_EXPORT__"]
        and solar.get("entity") == replacements["__SOLAR_POWER__"]
        and battery.get("state_of_charge") == replacements["__SOC__"]
        and home.get("entity") == replacements["__HOME_LOAD__"]
    )


def _is_generated_v20_energy_flow(
    card: dict[str, Any],
    replacements: dict[str, str],
) -> bool:
    """Return whether a card already is the generated template-v20 card."""
    if card.get("type") != "custom:noah-energy-flow-card":
        return False
    if card.get("title") not in {"Aktueller Energiefluss", "Current energy flow"}:
        return False

    entities = card.get("entities")
    if not isinstance(entities, dict):
        return False

    expected = {
        "grid_import": replacements["__GRID_IMPORT__"],
        "grid_export": replacements["__GRID_EXPORT__"],
        "solar_power": replacements["__SOLAR_POWER__"],
        "output_power": replacements["__OUTPUT_POWER__"],
        "charging_power": replacements["__CHARGING_POWER__"],
        "discharging_power": replacements["__DISCHARGING_POWER__"],
        "soc": replacements["__SOC__"],
        "home_load": replacements["__HOME_LOAD__"],
    }
    return all(entities.get(key) == value for key, value in expected.items())


def _apply_energy_flow_v20(
    config: dict[str, Any],
    replacements: dict[str, str],
    *,
    german: bool,
) -> bool:
    """Replace only the recognized generated legacy energy-flow card.

    User-created Power Flow Card Plus cards are intentionally left untouched.
    Returning True for an already migrated generated card also allows the
    template version to advance without repeating the migration on restart.
    """
    recognized = False
    changed = False

    for card in _dashboard._iter_dicts(config):
        if _is_generated_v20_energy_flow(card, replacements):
            recognized = True
            continue

        if not _is_generated_legacy_energy_flow(card, replacements):
            continue

        recognized = True
        card.clear()
        card.update(_energy_flow_card(replacements, german=german))
        changed = True

    return changed or recognized


def _install_template_v20_migration() -> None:
    """Extend dashboard.py with template-v20 energy-flow migration once."""
    _dashboard.DASHBOARD_TEMPLATE_VERSION = DASHBOARD_TEMPLATE_VERSION

    if getattr(_dashboard, _PATCH_MARKER, False):
        return

    previous_migrate = _dashboard._migrate_dashboard_to_beta11
    previous_build = _dashboard._async_build_dashboard_config

    def _migrate_dashboard_to_v20(
        hass,
        config: dict[str, Any],
        replacements: dict[str, str],
    ) -> tuple[dict[str, Any], bool]:
        migrated, changed = previous_migrate(hass, config, replacements)
        german = (hass.config.language or "en").lower().startswith("de")
        energy_flow_result = _apply_energy_flow_v20(
            migrated,
            replacements,
            german=german,
        )
        return migrated, changed or energy_flow_result

    async def _build_dashboard_v20(hass, entry) -> dict[str, Any]:
        config = await previous_build(hass, entry)
        replacements = _dashboard._resolve_entities(hass, entry)
        german = (hass.config.language or "en").lower().startswith("de")
        _apply_energy_flow_v20(config, replacements, german=german)
        return config

    _dashboard._migrate_dashboard_to_beta11 = _migrate_dashboard_to_v20
    _dashboard._async_build_dashboard_config = _build_dashboard_v20
    setattr(_dashboard, _PATCH_MARKER, True)


_install_template_v20_migration()

async_ensure_dashboard = _dashboard.async_ensure_dashboard
remove_dashboard_panel = _dashboard.remove_dashboard_panel
