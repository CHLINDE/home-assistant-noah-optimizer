"""Switch entities for the Growatt NOAH Optimizer."""

from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import (
    AddConfigEntryEntitiesCallback,
)

from . import NoahOptimizerConfigEntry
from .const import OPT_ENABLED
from .entity import NoahOptimizerEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: NoahOptimizerConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up optimizer switch."""

    async_add_entities(
        [
            NoahOptimizerEnabledSwitch(
                entry.runtime_data,
                entry,
            )
        ]
    )


class NoahOptimizerEnabledSwitch(
    NoahOptimizerEntity,
    SwitchEntity,
):
    """Enable optimizer calculations."""

    _attr_translation_key = "optimizer_enabled"

    def __init__(
        self,
        coordinator,
        entry,
    ) -> None:
        """Initialize the switch."""

        super().__init__(coordinator, entry)

        self.entry = entry
        self._attr_unique_id = (
            f"{entry.entry_id}_optimizer_enabled"
        )

    @property
    def is_on(self) -> bool:
        """Return enabled state."""

        return bool(
            self.coordinator.get_option(OPT_ENABLED)
        )

    async def async_turn_on(self, **kwargs) -> None:
        """Enable optimizer calculation."""

        await self.coordinator.async_set_option(
            OPT_ENABLED,
            True,
        )

    async def async_turn_off(self, **kwargs) -> None:
        """Disable optimizer calculation."""

        await self.coordinator.async_set_option(
            OPT_ENABLED,
            False,
        )