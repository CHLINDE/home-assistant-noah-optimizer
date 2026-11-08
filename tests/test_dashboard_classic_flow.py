"""Regressions for preserving the original NOAH Power Flow Card Plus layout."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import yaml

from custom_components.noah_optimizer.dashboard_migration_v20 import (
    _energy_flow_card,
)
from custom_components.noah_optimizer.dashboard_migration_v25 import (
    _classic_power_flow,
    _restore_classic_flow,
)

ROOT = Path(__file__).resolve().parents[1]


def entities() -> dict[str, str]:
    names = (
        "__GRID_IMPORT__", "__GRID_EXPORT__", "__SOLAR_POWER__",
        "__DISCHARGING_POWER__", "__CHARGING_POWER__", "__SOC__",
        "__HOME_LOAD__",
    )
    return {name: "sensor." + name.strip("_").lower() for name in names}


def make_config(card) -> dict:
    return {"views": [{"sections": [{"cards": [card]}]}]}


def test_reconstructed_classic_flow_matches_original_yaml_in_both_languages():
    ids = entities()
    for lang in ("de", "en"):
        config = yaml.safe_load(
            (ROOT / "custom_components" / "noah_optimizer" / f"dashboard_{lang}.yaml")
            .read_text(encoding="utf-8")
        )
        from_yaml = config["views"][0]["sections"][0]["cards"][0]
        classic = _classic_power_flow(ids, german=lang == "de")
        for token, value in ids.items():
            # The YAML is the pre-existing canonical classic power-flow layout.
            def replace_tokens(value_to_replace):
                if isinstance(value_to_replace, dict):
                    return {k: replace_tokens(v) for k, v in value_to_replace.items()}
                if isinstance(value_to_replace, list):
                    return [replace_tokens(v) for v in value_to_replace]
                if isinstance(value_to_replace, str):
                    for key, entity in ids.items():
                        value_to_replace = value_to_replace.replace(key, entity)
                return value_to_replace

            from_yaml = replace_tokens(from_yaml)
        assert classic == from_yaml


def test_generated_v20_flow_replaced_by_original_classic_style():
    ids = entities()
    current = _energy_flow_card(ids, german=True)
    config = make_config(current)
    assert _restore_classic_flow(config, ids, german=True)
    classic = config["views"][0]["sections"][0]["cards"][0]
    assert classic["type"] == "custom:power-flow-card-plus"
    assert classic["display_zero_lines"]["mode"] == "grey_out"
    assert classic["entities"]["battery"]["state_of_charge"] == ids["__SOC__"]
    assert not _restore_classic_flow(config, ids, german=True)


def test_existing_beta3_offline_wrappers_keep_their_conditions_and_note():
    ids = entities()
    current = _energy_flow_card(ids, german=True)
    live = {
        "type": "conditional",
        "conditions": [
            {"condition": "state", "entity": "binary_sensor.noah_critical_data", "state": "on"}
        ],
        "card": current,
    }
    offline = {
        "type": "conditional",
        "conditions": [
            {"condition": "not", "conditions": [
                {"condition": "state", "entity": "binary_sensor.noah_critical_data", "state": "on"}
            ]}
        ],
        "card": {"type": "markdown", "title": "Aktueller Energiefluss", "content": "NOAH offline"},
    }
    config = make_config({
        "type": "vertical-stack",
        "cards": [deepcopy(live), deepcopy(offline)],
    })
    assert _restore_classic_flow(config, ids, german=True)
    wrapper = config["views"][0]["sections"][0]["cards"][0]
    assert wrapper["cards"][0]["conditions"] == live["conditions"]
    assert wrapper["cards"][0]["card"]["type"] == "custom:power-flow-card-plus"
    assert wrapper["cards"][1] == offline
    assert not _restore_classic_flow(config, ids, german=True)


def test_existing_classic_style_and_custom_user_flows_remain_untouched():
    ids = entities()
    classic = _classic_power_flow(ids, german=True)
    classic["color"] = "#123456"
    custom_noah = _energy_flow_card(ids, german=True)
    custom_noah["colors"] = {"battery": "pink"}
    other_noah = {"type": "custom:noah-energy-flow-card", "title": "My custom flow"}
    config = {"views": [{"sections": [{"cards": [
        deepcopy(classic), deepcopy(custom_noah), deepcopy(other_noah),
    ]}]}]}
    original = deepcopy(config)
    assert not _restore_classic_flow(config, ids, german=True)
    assert config == original


def test_new_english_dashboard_recovers_classic_flow():
    ids = entities()
    config = make_config(_energy_flow_card(ids, german=False))
    assert _restore_classic_flow(config, ids, german=False)
    classic = config["views"][0]["sections"][0]["cards"][0]
    assert classic["title"] == "Current energy flow"
    assert classic["entities"]["home"]["name"] == "Home"
