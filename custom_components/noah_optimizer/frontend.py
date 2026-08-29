"""Frontend registration for the NOAH Optimizer history card."""

from __future__ import annotations

from pathlib import Path

from homeassistant.components import frontend
from homeassistant.components.http import StaticPathConfig
from homeassistant.components.lovelace.const import LOVELACE_DATA
from homeassistant.components.lovelace.resources import ResourceStorageCollection
from homeassistant.core import HomeAssistant

from .const import DOMAIN

HISTORY_CARD_STATIC_URL = f"/{DOMAIN}/noah-soc-history-card.js"
HISTORY_CARD_VERSION = "7"
HISTORY_CARD_URL = f"{HISTORY_CARD_STATIC_URL}?v={HISTORY_CARD_VERSION}"
HISTORY_CARD_FILE = Path(__file__).with_name("frontend") / "noah-soc-history-card.js"

_DATA_STATIC_REGISTERED = f"{DOMAIN}_history_card_static_registered"


async def async_register_history_card(hass: HomeAssistant) -> None:
    """Serve and register the bundled SOC history card."""
    if not hass.data.get(_DATA_STATIC_REGISTERED):
        await hass.http.async_register_static_paths(
            [
                StaticPathConfig(
                    HISTORY_CARD_STATIC_URL,
                    str(HISTORY_CARD_FILE),
                    False,
                )
            ]
        )
        hass.data[_DATA_STATIC_REGISTERED] = True

    # In storage resource mode, register the card as a real Lovelace module
    # resource. Home Assistant awaits Lovelace resources before constructing
    # custom cards, avoiding the load-order race that can otherwise leave a
    # permanent "Configuration error" card on a cold frontend load.
    lovelace_data = hass.data.get(LOVELACE_DATA)
    resources = getattr(lovelace_data, "resources", None)

    if isinstance(resources, ResourceStorageCollection):
        await resources.async_get_info()

        for item in resources.async_items():
            url = item.get("url", "")
            if not url.startswith(HISTORY_CARD_STATIC_URL):
                continue

            if url != HISTORY_CARD_URL or item.get("type") != "module":
                await resources.async_update_item(
                    item["id"],
                    {
                        "res_type": "module",
                        "url": HISTORY_CARD_URL,
                    },
                )
            return

        await resources.async_create_item(
            {
                "res_type": "module",
                "url": HISTORY_CARD_URL,
            }
        )
        return

    # YAML resource mode cannot be changed persistently from the integration.
    # Keep the frontend injection as a compatibility fallback there.
    frontend.add_extra_js_url(hass, HISTORY_CARD_URL)


def remove_history_card(hass: HomeAssistant) -> None:
    """Remove runtime fallback injection while leaving Lovelace resources intact."""
    frontend.remove_extra_js_url(hass, HISTORY_CARD_URL)
