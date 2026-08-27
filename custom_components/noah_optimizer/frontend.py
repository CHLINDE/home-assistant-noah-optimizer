"""Frontend registration for the NOAH Optimizer history card."""

from __future__ import annotations

from pathlib import Path

from homeassistant.components import frontend
from homeassistant.components.http import StaticPathConfig
from homeassistant.core import HomeAssistant

from .const import DOMAIN

HISTORY_CARD_STATIC_URL = f"/{DOMAIN}/noah-soc-history-card.js"
HISTORY_CARD_VERSION = "4"
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

    frontend.add_extra_js_url(hass, HISTORY_CARD_URL)


def remove_history_card(hass: HomeAssistant) -> None:
    """Remove runtime frontend injection while leaving the static route."""
    frontend.remove_extra_js_url(hass, HISTORY_CARD_URL)
