"""Frontend registration for bundled NOAH Optimizer dashboard cards."""

from __future__ import annotations

from pathlib import Path

from homeassistant.components import frontend
from homeassistant.components.http import StaticPathConfig
from homeassistant.components.lovelace.const import LOVELACE_DATA
from homeassistant.components.lovelace.resources import ResourceStorageCollection
from homeassistant.core import HomeAssistant

from .const import DOMAIN

HISTORY_CARD_STATIC_URL = f"/{DOMAIN}/noah-soc-history-card.js"
HISTORY_CARD_VERSION = "9"
HISTORY_CARD_URL = f"{HISTORY_CARD_STATIC_URL}?v={HISTORY_CARD_VERSION}"
HISTORY_CARD_FILE = Path(__file__).with_name("frontend") / "noah-soc-history-card.js"

ENERGY_FLOW_CARD_STATIC_URL = f"/{DOMAIN}/noah-energy-flow-card.js"
ENERGY_FLOW_CARD_VERSION = "3"
ENERGY_FLOW_CARD_URL = f"{ENERGY_FLOW_CARD_STATIC_URL}?v={ENERGY_FLOW_CARD_VERSION}"
ENERGY_FLOW_CARD_FILE = Path(__file__).with_name("frontend") / "noah-energy-flow-card.js"

_FRONTEND_CARDS = (
    (HISTORY_CARD_STATIC_URL, HISTORY_CARD_URL, HISTORY_CARD_FILE),
    (ENERGY_FLOW_CARD_STATIC_URL, ENERGY_FLOW_CARD_URL, ENERGY_FLOW_CARD_FILE),
)

_DATA_HISTORY_STATIC_REGISTERED = f"{DOMAIN}_history_card_static_registered"
_DATA_ENERGY_FLOW_STATIC_REGISTERED = f"{DOMAIN}_energy_flow_card_static_registered"


async def async_register_history_card(hass: HomeAssistant) -> None:
    """Serve and register all bundled NOAH Optimizer frontend cards.

    The function name is kept for compatibility with the existing integration
    setup path; Beta 16 added the dedicated energy-flow card.
    """

    # Keep the Beta 4 history-card registration key so an in-process update
    # from an older beta does not try to register the same static route twice.
    if not hass.data.get(_DATA_HISTORY_STATIC_REGISTERED):
        await hass.http.async_register_static_paths(
            [
                StaticPathConfig(
                    HISTORY_CARD_STATIC_URL,
                    str(HISTORY_CARD_FILE),
                    False,
                )
            ]
        )
        hass.data[_DATA_HISTORY_STATIC_REGISTERED] = True

    if not hass.data.get(_DATA_ENERGY_FLOW_STATIC_REGISTERED):
        await hass.http.async_register_static_paths(
            [
                StaticPathConfig(
                    ENERGY_FLOW_CARD_STATIC_URL,
                    str(ENERGY_FLOW_CARD_FILE),
                    False,
                )
            ]
        )
        hass.data[_DATA_ENERGY_FLOW_STATIC_REGISTERED] = True

    # In storage resource mode, register the cards as real Lovelace module
    # resources. Home Assistant awaits Lovelace resources before constructing
    # custom cards, avoiding a load-order race on a cold frontend load.
    lovelace_data = hass.data.get(LOVELACE_DATA)
    resources = getattr(lovelace_data, "resources", None)

    if isinstance(resources, ResourceStorageCollection):
        await resources.async_get_info()

        for static_url, versioned_url, _file_path in _FRONTEND_CARDS:
            existing = next(
                (
                    item
                    for item in resources.async_items()
                    if item.get("url", "").startswith(static_url)
                ),
                None,
            )

            if existing is not None:
                if (
                    existing.get("url") != versioned_url
                    or existing.get("type") != "module"
                ):
                    await resources.async_update_item(
                        existing["id"],
                        {
                            "res_type": "module",
                            "url": versioned_url,
                        },
                    )
                continue

            await resources.async_create_item(
                {
                    "res_type": "module",
                    "url": versioned_url,
                }
            )
        return

    # YAML resource mode cannot be changed persistently from the integration.
    # Keep the frontend injection as a compatibility fallback there.
    for _static_url, versioned_url, _file_path in _FRONTEND_CARDS:
        frontend.add_extra_js_url(hass, versioned_url)


def remove_history_card(hass: HomeAssistant) -> None:
    """Remove runtime fallback injection while leaving Lovelace resources intact."""

    for _static_url, versioned_url, _file_path in _FRONTEND_CARDS:
        frontend.remove_extra_js_url(hass, versioned_url)
