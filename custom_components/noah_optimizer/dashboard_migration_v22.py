"""Show a compact offline view instead of unavailable NOAH gauges.

Only recognized standard cards are changed. Existing daytime cards remain
intact inside conditional wrappers, including user-selected flow styling.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from . import dashboard_migration_v21 as _previous_migration  # noqa: F401
from . import dashboard as _dashboard

_dashboard.DASHBOARD_TEMPLATE_VERSION = 22
_PATCH_MARKER = "_noah_template_v22_night_view_patch_installed"


def _flow_content(replacements: dict[str, str], german: bool) -> str:
    """Build flow text that distinguishes last-known and grid values."""
    status = replacements["__DATA_STATUS__"]
    soc = replacements["__SOC__"]
    minimum = replacements["__MIN_SOC__"]
    grid = replacements["__GRID_IMPORT__"]
    export = replacements["__GRID_EXPORT__"]
    if german:
        return (
            f"{{% if is_state('{status}', 'expected_night_shutdown') %}}\n"
            "## NOAH in Nachtruhe\n"
            "Der Speicher hat den Mindest-SOC erreicht und ist erwartungsgemäß aus.\n"
            "{% else %}\n"
            "## NOAH nicht erreichbar\n"
            "Die Stellwerte sind derzeit nicht verfügbar. Bitte die Verbindung prüfen.\n"
            "{% endif %}\n\n"
            f"**Mindest-SOC:** {{{{ states('{minimum}') }}}} %  \n"
            f"{{% set last_soc = states('{soc}') %}}\n"
            "**Zuletzt gemeldeter SOC:** {{ last_soc ~ ' %' if last_soc not in "
            "['unknown', 'unavailable'] else 'nicht bekannt' }} (kein Live-Wert)  \n"
            f"{{% set grid_import = states('{grid}') %}}\n"
            "**Netzbezug:** {{ grid_import ~ ' W' if grid_import not in "
            "['unknown', 'unavailable'] else 'nicht verfügbar' }}  \n"
            f"{{% set grid_export = states('{export}') %}}\n"
            "**Netzeinspeisung:** {{ grid_export ~ ' W' if grid_export not in "
            "['unknown', 'unavailable'] else 'nicht verfügbar' }} (Netzsensor)"
        )
    return (
        f"{{% if is_state('{status}', 'expected_night_shutdown') %}}\n"
        "## NOAH resting overnight\n"
        "The battery reached minimum SOC and shut down as expected.\n"
        "{% else %}\n"
        "## NOAH unavailable\n"
        "Output control is unavailable. Check the connection.\n"
        "{% endif %}\n\n"
        f"**Minimum SOC:** {{{{ states('{minimum}') }}}} %  \n"
        f"{{% set last_soc = states('{soc}') %}}\n"
        "**Last reported SOC:** {{ last_soc ~ ' %' if last_soc not in "
        "['unknown', 'unavailable'] else 'unknown' }} (not live)  \n"
        f"{{% set grid_import = states('{grid}') %}}\n"
        "**Grid import:** {{ grid_import ~ ' W' if grid_import not in "
        "['unknown', 'unavailable'] else 'unavailable' }}  \n"
        f"{{% set grid_export = states('{export}') %}}\n"
        "**Grid export:** {{ grid_export ~ ' W' if grid_export not in "
        "['unknown', 'unavailable'] else 'unavailable' }} (grid meter)"
    )


def _status_content(replacements: dict[str, str], german: bool) -> str:
    """Keep offline controller diagnostics short and honest."""
    status = replacements["__DATA_STATUS__"]
    if german:
        return (
            f"{{% if is_state('{status}', 'expected_night_shutdown') %}}\n"
            "## Nachtruhe am Mindest-SOC\n"
            "Der NOAH ist erwartungsgemäß abgeschaltet. Stellbefehle sind gesperrt.\n"
            "{% else %}\n"
            "## Stellgröße nicht verfügbar\n"
            "Der NOAH oder seine Stellgröße ist nicht erreichbar. Stellbefehle sind gesperrt.\n"
            "{% endif %}"
        )
    return (
        f"{{% if is_state('{status}', 'expected_night_shutdown') %}}\n"
        "## Resting at minimum SOC\n"
        "NOAH shut down as expected. Output commands are blocked.\n"
        "{% else %}\n"
        "## Output control unavailable\n"
        "NOAH or its output control cannot be reached. Output commands are blocked.\n"
        "{% endif %}"
    )


def _offline_gauges(replacements: dict[str, str], german: bool) -> dict[str, Any]:
    """Show available grid measurements and configured SOC limits as tiles."""
    names = (
        ("Netzbezug", "Netzeinspeisung", "Mindest-SOC", "Ziel-SOC")
        if german else
        ("Grid import", "Grid export", "Minimum SOC", "Target SOC")
    )
    tokens = ("__GRID_IMPORT__", "__GRID_EXPORT__", "__MIN_SOC__", "__TARGET_SOC__")
    return {
        "type": "grid",
        "columns": 2,
        "square": False,
        "cards": [
            {"type": "tile", "entity": replacements[token], "name": name}
            for token, name in zip(tokens, names, strict=True)
        ],
    }


def _is_standard_gauges(card: dict[str, Any], replacements: dict[str, str]) -> bool:
    if card.get("type") != "grid":
        return False
    cards = card.get("cards")
    expected = (
        "__SOC__",
        "__FORECAST_COVERAGE__",
        "__OUTPUT_TARGET__",
        "__GRID_IMPORT__",
    )
    return (
        isinstance(cards, list)
        and len(cards) == len(expected)
        and all(
            isinstance(item, dict)
            and item.get("type") == "gauge"
            and item.get("entity") == replacements[token]
            for item, token in zip(cards, expected, strict=True)
        )
    )


def _is_standard_flow(card: dict[str, Any], replacements: dict[str, str]) -> bool:
    if card.get("title") not in {"Aktueller Energiefluss", "Current energy flow"}:
        return False
    entities = card.get("entities")
    if not isinstance(entities, dict):
        return False
    if card.get("type") == "custom:noah-energy-flow-card":
        return (
            entities.get("grid_import") == replacements["__GRID_IMPORT__"]
            and entities.get("soc") == replacements["__SOC__"]
        )
    if card.get("type") == "custom:power-flow-card-plus":
        battery = entities.get("battery")
        return (
            isinstance(battery, dict)
            and battery.get("state_of_charge") == replacements["__SOC__"]
            and isinstance(entities.get("grid"), dict)
        )
    return False


def _apply_night_view(
    config: dict[str, Any], replacements: dict[str, str], german: bool,
) -> bool:
    """Wrap generated cards without altering their online configuration."""
    changed = False
    actuator = replacements["__ACTUATOR_AVAILABLE__"]
    flow_content = _flow_content(replacements, german)

    for view in config.get("views", []):
        if not isinstance(view, dict):
            continue
        for section in view.get("sections", []):
            if not isinstance(section, dict):
                continue
            cards = section.get("cards")
            if not isinstance(cards, list):
                continue
            for index, card in enumerate(cards):
                if not isinstance(card, dict):
                    continue
                is_flow = _is_standard_flow(card, replacements)
                if _is_standard_gauges(card, replacements) or is_flow:
                    original = deepcopy(card)
                    cards[index] = {
                        "type": "vertical-stack",
                        "cards": [
                            {
                                "type": "conditional",
                                "conditions": [{"condition": "state", "entity": actuator, "state": "on"}],
                                "card": original,
                            },
                            {
                                "type": "conditional",
                                "conditions": [{"condition": "state", "entity": actuator, "state": "off"}],
                                "card": {
                                    "type": "markdown",
                                    "title": original.get("title", ""),
                                    "content": flow_content,
                                } if is_flow else _offline_gauges(replacements, german),
                            },
                        ],
                    }
                    changed = True
                elif (
                    card.get("type") == "markdown"
                    and card.get("title") in {"Reglerstatus", "Controller status"}
                    and isinstance(card.get("content"), str)
                    and "**Controller:**" in card["content"]
                    and "noah_night_view_v22" not in card["content"]
                ):
                    previous = card["content"]
                    card["content"] = (
                        "{# noah_night_view_v22 #}\n"
                        f"{{% if is_state('{actuator}', 'off') %}}\n"
                        + _status_content(replacements, german)
                        + "\n{% else %}\n"
                        + previous
                        + "\n{% endif %}"
                    )
                    changed = True
    return changed


def _preserve_legacy_flow(
    config: dict[str, Any], replacements: dict[str, str],
) -> list[dict[str, Any]]:
    """Remember an existing four-node flow card and its visual settings."""
    return [
        deepcopy(card)
        for view in config.get("views", []) if isinstance(view, dict)
        for section in view.get("sections", []) if isinstance(section, dict)
        for card in section.get("cards", []) if isinstance(card, dict)
        if card.get("type") == "custom:power-flow-card-plus"
        and _is_standard_flow(card, replacements)
    ]


def _restore_legacy_flow(
    config: dict[str, Any], preserved: list[dict[str, Any]],
) -> bool:
    """Keep the user's current daytime card if an older migration replaced it."""
    changed = False
    for view in config.get("views", []):
        if not isinstance(view, dict):
            continue
        for section in view.get("sections", []):
            if not isinstance(section, dict):
                continue
            cards = section.get("cards", [])
            if not isinstance(cards, list):
                continue
            for index, card in enumerate(cards):
                if not isinstance(card, dict) or card.get("type") != "custom:noah-energy-flow-card":
                    continue
                original = next(
                    (item for item in preserved if item.get("title") == card.get("title")),
                    None,
                )
                if original is not None:
                    cards[index] = original
                    preserved.remove(original)
                    changed = True
    return changed


def _install() -> None:
    if getattr(_dashboard, _PATCH_MARKER, False):
        return
    previous_migrate = _dashboard._migrate_dashboard_to_beta11
    previous_build = _dashboard._async_build_dashboard_config

    def migrate(hass, config, replacements):
        preserved_flow = _preserve_legacy_flow(config, replacements)
        config, changed = previous_migrate(hass, config, replacements)
        changed = _restore_legacy_flow(config, preserved_flow) or changed
        german = (hass.config.language or "en").lower().startswith("de")
        return config, _apply_night_view(config, replacements, german) or changed

    async def build(hass, entry):
        config = await previous_build(hass, entry)
        replacements = _dashboard._resolve_entities(hass, entry)
        german = (hass.config.language or "en").lower().startswith("de")
        _apply_night_view(config, replacements, german)
        return config

    _dashboard._migrate_dashboard_to_beta11 = migrate
    _dashboard._async_build_dashboard_config = build
    setattr(_dashboard, _PATCH_MARKER, True)


_install()
async_ensure_dashboard = _dashboard.async_ensure_dashboard
remove_dashboard_panel = _dashboard.remove_dashboard_panel
