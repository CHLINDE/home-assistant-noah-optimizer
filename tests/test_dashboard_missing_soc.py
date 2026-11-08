"""Dashboard regression checks for NOAH wake-up with unavailable SOC.

These check the generated Lovelace configuration; no physical battery is used.
"""

from __future__ import annotations

from copy import deepcopy

from custom_components.noah_optimizer.dashboard_migration_v23 import (
    _apply_valid_data_view,
    _offline_content,
)


def _entities() -> dict[str, str]:
    return {
        "__CRITICAL_DATA_OK__": "binary_sensor.noah_critical_data",
        "__ACTUATOR_AVAILABLE__": "binary_sensor.noah_actuator_available",
        "__SOC__": "sensor.noah_soc",
        "__FORECAST_COVERAGE__": "sensor.noah_coverage",
        "__OUTPUT_TARGET__": "sensor.noah_output_target",
        "__GRID_IMPORT__": "sensor.noah_grid_import",
        "__GRID_POWER__": "sensor.noah_grid_power",
        "__DATA_STATUS__": "sensor.noah_data_status",
        "__MIN_SOC__": "number.noah_minimum_soc",
        "__TARGET_SOC__": "number.noah_target_soc",
    }


def _gauges() -> dict:
    return {
        "type": "grid",
        "columns": 2,
        "cards": [
            {"type": "gauge", "entity": "sensor.noah_soc", "name": "Akkustand"},
            {"type": "gauge", "entity": "sensor.noah_coverage", "name": "Prognosedeckung"},
            {"type": "gauge", "entity": "sensor.noah_output_target", "name": "Ausgang"},
            {"type": "gauge", "entity": "sensor.noah_grid_import", "name": "Netzbezug"},
        ],
    }


def _flow() -> dict:
    return {
        "type": "custom:noah-energy-flow-card",
        "title": "Aktueller Energiefluss",
        "entities": {"grid_import": "sensor.noah_grid_import", "soc": "sensor.noah_soc"},
        "colors": {"grid": "#998877"},
    }


def _config(*cards: dict) -> dict:
    return {"views": [{"sections": [{"cards": list(cards)}]}]}


def _children(config: dict, index: int = 0):
    wrapper = config["views"][0]["sections"][0]["cards"][index]
    assert wrapper["type"] == "vertical-stack"
    return wrapper["cards"]


def test_invalid_soc_hides_live_gauges_even_when_actuator_is_online():
    original = _gauges()
    config = _config(deepcopy(original))
    assert _apply_valid_data_view(config, _entities(), german=True)
    live, fallback = _children(config)

    # Do not gate on actuator availability: it may be online while
    # the SOC source still contains a placeholder 0 %.
    assert live["conditions"] == [
        {"condition": "state", "entity": "binary_sensor.noah_critical_data", "state": "on"}
    ]
    assert fallback["conditions"] == [
        {"condition": "state_not", "entity": "binary_sensor.noah_critical_data", "state": "on"}
    ]
    assert live["card"] == original
    assert fallback["card"]["type"] == "markdown"
    assert "Warten auf gültige Messwerte" in fallback["card"]["content"]
    assert "Akkustand:** derzeit nicht messbar" in fallback["card"]["content"]


def test_beta2_actuator_conditional_wrapper_is_upgraded_without_nesting():
    original = _gauges()
    previous = {
        "type": "vertical-stack",
        "cards": [
            {
                "type": "conditional",
                "conditions": [
                    {
                        "condition": "state",
                        "entity": "binary_sensor.noah_actuator_available",
                        "state": "on",
                    }
                ],
                "card": original,
            },
            {
                "type": "conditional",
                "conditions": [
                    {
                        "condition": "state",
                        "entity": "binary_sensor.noah_actuator_available",
                        "state": "off",
                    }
                ],
                "card": {"type": "grid", "cards": []},
            },
        ],
    }
    config = _config(previous)
    assert _apply_valid_data_view(config, _entities(), german=True)
    live, fallback = _children(config)
    assert live["card"] == original
    assert fallback["card"]["type"] == "markdown"
    assert live["conditions"][0]["entity"] == "binary_sensor.noah_critical_data"
    assert fallback["conditions"][0]["condition"] == "state_not"
    assert _apply_valid_data_view(config, _entities(), german=True) is False


def test_energy_flow_styling_is_preserved_for_daytime():
    original = _flow()
    config = _config(deepcopy(original))
    assert _apply_valid_data_view(config, _entities(), german=True)
    live, fallback = _children(config)
    assert live["card"] == original
    assert fallback["card"]["type"] == "markdown"
    assert fallback["card"]["title"] == "Aktueller Energiefluss"


def test_reordered_default_gauges_migrate_and_user_cards_are_preserved():
    customized = _gauges()
    customized["cards"].reverse()
    customized["cards"][0]["needle"] = False
    user_card = {"type": "gauge", "entity": "sensor.other", "name": "Other"}
    config = _config(deepcopy(customized), deepcopy(user_card))
    assert _apply_valid_data_view(config, _entities(), german=True)
    assert _children(config)[0]["card"] == customized
    assert config["views"][0]["sections"][0]["cards"][1] == user_card


def test_status_markdown_is_hidden_until_critical_data_recovers():
    original = {
        "type": "markdown",
        "title": "Reglerstatus",
        "content": "{# noah_night_view_v22 #}\n**Controller:** In sync",
    }
    config = _config(deepcopy(original))
    assert _apply_valid_data_view(config, _entities(), german=True)
    live, fallback = _children(config)
    assert live["card"] == original
    assert fallback["card"]["type"] == "markdown"


def test_offline_message_describes_missing_data_in_both_languages():
    de = _offline_content(_entities(), german=True)
    en = _offline_content(_entities(), german=False)
    assert "expected_night_shutdown" in de
    assert "critical_data_missing" in de
    assert "kein live-wert" in de.lower()
    assert "no live measurement" in en
    assert "blocked" in en
    assert "0 %" not in de
