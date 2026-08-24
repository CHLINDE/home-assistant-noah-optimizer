"""Button entities for the Growatt NOAH Optimizer."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import NoahOptimizerConfigEntry
from .entity import NoahOptimizerEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: NoahOptimizerConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up optimizer buttons."""
    async_add_entities(
        [
            NoahOptimizerPvLearningResetButton(
                entry.runtime_data,
                entry,
            )
        ]
    )


class NoahOptimizerPvLearningResetButton(NoahOptimizerEntity, ButtonEntity):
    """Reset persistent PV-learning data."""

    _attr_translation_key = "pv_learning_reset"

    def __init__(self, coordinator, entry) -> None:
        """Initialize the button."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_pv_learning_reset"

    async def async_press(self) -> None:
        """Reset learned PV data."""
        await self.coordinator.async_reset_pv_learning()
