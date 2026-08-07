"""Binary sensors for the Growatt NOAH Optimizer."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import (
    AddConfigEntryEntitiesCallback,
)

from . import NoahOptimizerConfigEntry
from .const import (
    DATA_ACTUATOR_AVAILABLE,
    DATA_CRITICAL_DATA_OK,
    DATA_FORECAST_AVAILABLE,
)
from .entity import NoahOptimizerEntity


@dataclass(
    frozen=True,
    kw_only=True,
)
class NoahBinarySensorDescription(
    BinarySensorEntityDescription
):
    """Describe a NOAH Optimizer binary sensor."""

    data_key: str


BINARY_SENSORS: tuple[
    NoahBinarySensorDescription,
    ...
] = (
    NoahBinarySensorDescription(
        key="critical_data_ok",
        translation_key="critical_data_ok",
        data_key=DATA_CRITICAL_DATA_OK,
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
    ),
    NoahBinarySensorDescription(
        key="forecast_available",
        translation_key="forecast_available",
        data_key=DATA_FORECAST_AVAILABLE,
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
    ),
    NoahBinarySensorDescription(
        key="actuator_available",
        translation_key="actuator_available",
        data_key=DATA_ACTUATOR_AVAILABLE,
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: NoahOptimizerConfigEntry,
    async_add_entities:
        AddConfigEntryEntitiesCallback,
) -> None:
    """Set up NOAH Optimizer binary sensors."""

    async_add_entities(
        NoahOptimizerBinarySensor(
            entry.runtime_data,
            entry,
            description,
        )
        for description in BINARY_SENSORS
    )


class NoahOptimizerBinarySensor(
    NoahOptimizerEntity,
    BinarySensorEntity,
):
    """Represent a NOAH Optimizer binary sensor."""

    entity_description: NoahBinarySensorDescription

    def __init__(
        self,
        coordinator,
        entry,
        description: NoahBinarySensorDescription,
    ) -> None:
        """Initialize the binary sensor."""

        super().__init__(
            coordinator,
            entry,
        )

        self.entity_description = description

        self._attr_unique_id = (
            f"{entry.entry_id}_{description.key}"
        )

    @property
    def is_on(self) -> bool:
        """Return the binary sensor state."""

        return bool(
            self.coordinator.data.get(
                self.entity_description.data_key
            )
        )