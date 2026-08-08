"""Select entities for the Growatt NOAH Optimizer."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import (
    AddConfigEntryEntitiesCallback,
)

from . import NoahOptimizerConfigEntry
from .const import (
    MODE_AUTOMATIC,
    MODE_CHARGE_PRIORITY,
    MODE_MANUAL,
    MODE_SELF_CONSUMPTION,
    OPT_MODE,
)
from .entity import NoahOptimizerEntity


MODES = [
    MODE_AUTOMATIC,
    MODE_SELF_CONSUMPTION,
    MODE_CHARGE_PRIORITY,
    MODE_MANUAL,
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: NoahOptimizerConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up optimizer mode selector."""

    async_add_entities(
        [
            NoahOptimizerModeSelect(
                entry.runtime_data,
                entry,
            )
        ]
    )


class NoahOptimizerModeSelect(
    NoahOptimizerEntity,
    SelectEntity,
):
    """Select the operating mode."""

    _attr_translation_key = "optimizer_mode"
    _attr_options = MODES

    def __init__(
        self,
        coordinator,
        entry,
    ) -> None:
        """Initialize the selector."""

        super().__init__(
            coordinator,
            entry,
        )

        self.entry = entry

        self._attr_unique_id = (
            f"{entry.entry_id}_optimizer_mode"
        )

    @property
    def current_option(self) -> str:
        """Return the selected mode."""

        return str(
            self.coordinator.get_option(
                OPT_MODE
            )
        )

    async def async_select_option(
        self,
        option: str,
    ) -> None:
        """Change operating mode."""

        if option not in MODES:
            raise ValueError(
                f"Unsupported optimizer mode: {option}"
            )

        await self.coordinator.async_set_option(
            OPT_MODE,
            option,
        )