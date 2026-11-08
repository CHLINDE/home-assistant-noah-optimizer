"""Dashboard template 23: show a calm placeholder until NOAH data is valid.

Template 22 used actuator availability alone to decide when to show live
gauges. After a night shutdown, the actuator can be online while SOC is still
invalid; this left four large "entity unavailable" warnings in the dashboard.

Use the existing critical-data flag, not a fabricated SOC, to decide whether
real-time cards may be displayed. Preserve the original live cards unchanged.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from . import dashboard_migration_v22 as _previous_migration  # noqa: F401
from . import dashboard as _dashboard

# Bump the stored dashboard template version so early beta-3 test installs
# with the broken condition are repaired automatically on the next restart.
_dashboard.DASHBOARD_TEMPLATE_VERSION = 24
_PATCH_MARKER = "_noah_template_v23_safe_dashboard_installed"


def _offline_content(replacements: dict[str, str], german: bool) -> str:
    """Describe missing measurements without claiming a current battery SOC."""
    status = replacements["__DATA_STATUS__"]
    minimum = replacements["__MIN_SOC__"]
    target = replacements["__TARGET_SOC__"]
    grid_power = replacements["__GRID_POWER__"]

    if german:
        return (
            f"{{% set status = states('{status}') %}}\n"
            "{% if status == 'expected_night_shutdown' %}\n"
            "## NOAH in Nachtruhe\n"
            "Der Speicher hat sich am Mindest-SOC abgeschaltet.\n"
            "{% elif status == 'critical_data_missing' %}\n"
            "## NOAH: Warten auf gültige Messwerte\n"
            "Der NOAH liefert noch nicht alle für die Regelung benötigten Messwerte.\n"
            "{% else %}\n"
            "## NOAH derzeit nicht verfügbar\n"
            "Bitte die NOAH-Verbindung und die Messwerte prüfen.\n"
            "{% endif %}\n\n"
            "**Akkustand:** derzeit nicht messbar (kein Live-Wert)  \n"
            f"**Mindest-SOC:** {{{{ states('{minimum}') }}}} %  \n"
            f"**Ziel-SOC:** {{{{ states('{target}') }}}} %  \n"
            f"{{% set grid = states('{grid_power}') %}}\n"
            "{% if is_number(grid) %}\n"
            "**Netzleistung:** {{ grid }} W  \n"
            "{% endif %}\n"
            "\nDie aktive NOAH-Ausgangsregelung bleibt bis zu gültigen Daten gesperrt."
        )

    return (
        f"{{% set status = states('{status}') %}}\n"
        "{% if status == 'expected_night_shutdown' %}\n"
        "## NOAH resting overnight\n"
        "The battery shut down at its minimum SOC.\n"
        "{% elif status == 'critical_data_missing' %}\n"
        "## NOAH: Waiting for valid measurements\n"
        "NOAH has not yet provided all measurements required for control.\n"
        "{% else %}\n"
        "## NOAH currently unavailable\n"
        "Check NOAH connectivity and measurements.\n"
        "{% endif %}\n\n"
        "**Battery SOC:** no live measurement available  \n"
        f"**Minimum SOC:** {{{{ states('{minimum}') }}}} %  \n"
        f"**Target SOC:** {{{{ states('{target}') }}}} %  \n"
        f"{{% set grid = states('{grid_power}') %}}\n"
        "{% if is_number(grid) %}\n"
        "**Grid power:** {{ grid }} W  \n"
        "{% endif %}\n"
        "\nActive NOAH output control remains blocked until data is valid."
    )


def _is_gauge_group(card: dict[str, Any], replacements: dict[str, str]) -> bool:
    """Recognize the four standard gauges, including harmless reordering."""
    if card.get("type") != "grid":
        return False
    cards = card.get("cards")
    expected = {
        replacements[token]
        for token in (
            "__SOC__",
            "__FORECAST_COVERAGE__",
            "__OUTPUT_TARGET__",
            "__GRID_IMPORT__",
        )
    }
    return (
        isinstance(cards, list)
        and len(cards) == 4
        and all(isinstance(item, dict) and item.get("type") == "gauge" for item in cards)
        and {item.get("entity") for item in cards} == expected
    )


def _card_kind(card: dict[str, Any], replacements: dict[str, str]) -> str | None:
    """Only touch identifiable generated cards, not unrelated user cards."""
    if _is_gauge_group(card, replacements):
        return "gauges"
    if _previous_migration._is_standard_flow(card, replacements):
        return "flow"
    if (
        card.get("type") == "markdown"
        and card.get("title") in {"Reglerstatus", "Controller status"}
        and isinstance(card.get("content"), str)
        and (
            "noah_night_view_v22" in card["content"]
            or "**Controller:**" in card["content"]
        )
    ):
        return "status"
    return None


def _wrapped_card(
    original: dict[str, Any],
    kind: str,
    replacements: dict[str, str],
    german: bool,
) -> dict[str, Any]:
    """Show live data only when all critical measurements are valid."""
    critical = replacements["__CRITICAL_DATA_OK__"]
    note = {"type": "markdown", "content": _offline_content(replacements, german)}
    if kind == "flow":
        note["title"] = original.get("title", "")
    return {
        "type": "vertical-stack",
        "cards": [
            {
                "type": "conditional",
                "conditions": [
                    {"condition": "state", "entity": critical, "state": "on"}
                ],
                "card": deepcopy(original),
            },
            {
                "type": "conditional",
                "conditions": [
                    {
                        "condition": "not",
                        "conditions": [
                            {"condition": "state", "entity": critical, "state": "on"}
                        ],
                    }
                ],
                "card": note,
            },
        ],
    }


def _original_from_previous_wrapper(
    card: dict[str, Any], replacements: dict[str, str],
) -> tuple[dict[str, Any], str] | None:
    """Find beta-2 wrappers so they can be migrated without nesting stacks."""
    if card.get("type") != "vertical-stack":
        return None
    children = card.get("cards")
    if not isinstance(children, list) or len(children) != 2:
        return None
    live, offline = children
    if not all(isinstance(item, dict) and item.get("type") == "conditional" for item in children):
        return None
    original = live.get("card")
    if not isinstance(original, dict):
        return None
    kind = _card_kind(original, replacements)
    if kind is None:
        return None
    # Do not replace a user-defined conditional pair with a matching live card.
    offline_card = offline.get("card")
    if not isinstance(offline_card, dict):
        return None
    if offline_card.get("type") not in {"markdown", "grid"}:
        return None
    live_conditions = live.get("conditions")
    if not isinstance(live_conditions, list) or len(live_conditions) != 1:
        return None
    if live_conditions[0].get("condition") != "state":
        return None
    return original, kind


def _apply_valid_data_view(
    config: dict[str, Any], replacements: dict[str, str], german: bool,
) -> bool:
    """Upgrade stored beta-2 wrappers, and wrap any missed standard cards."""
    changed = False
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
                existing = _original_from_previous_wrapper(card, replacements)
                if existing is not None:
                    original, kind = existing
                else:
                    kind = _card_kind(card, replacements)
                    if kind is None:
                        continue
                    original = card
                wrapped = _wrapped_card(original, kind, replacements, german)
                if wrapped != card:
                    cards[index] = wrapped
                    changed = True
    return changed


def _install() -> None:
    if getattr(_dashboard, _PATCH_MARKER, False):
        return

    previous_migrate = _dashboard._migrate_dashboard_to_beta11
    previous_build = _dashboard._async_build_dashboard_config

    def migrate(hass, config, replacements):
        migrated, changed = previous_migrate(hass, config, replacements)
        german = (hass.config.language or "en").lower().startswith("de")
        upgraded = _apply_valid_data_view(migrated, replacements, german)
        return migrated, changed or upgraded

    async def build(hass, entry):
        config = await previous_build(hass, entry)
        replacements = _dashboard._resolve_entities(hass, entry)
        german = (hass.config.language or "en").lower().startswith("de")
        _apply_valid_data_view(config, replacements, german)
        return config

    _dashboard._migrate_dashboard_to_beta11 = migrate
    _dashboard._async_build_dashboard_config = build
    setattr(_dashboard, _PATCH_MARKER, True)


_install()
async_ensure_dashboard = _dashboard.async_ensure_dashboard
remove_dashboard_panel = _dashboard.remove_dashboard_panel
