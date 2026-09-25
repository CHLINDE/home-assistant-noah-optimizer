"""Binary sensors for the Growatt NOAH Optimizer."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity_platform import (
    AddConfigEntryEntitiesCallback,
)

from . import NoahOptimizerConfigEntry
from .const import (
    DATA_ACTUATOR_AVAILABLE,
    DATA_CRITICAL_DATA_OK,
    DATA_FORECAST_AVAILABLE,
    DATA_PV_LEARNING_READY,
    CONF_NOAH_API_TOKEN,
    CONF_NOAH_DEVICE_SN,
    DOMAIN,
)
from .entity import NoahOptimizerEntity
from .growatt_heating import GrowattHeatingCoordinator


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
    NoahBinarySensorDescription(
        key="pv_learning_ready",
        translation_key="pv_learning_ready",
        data_key=DATA_PV_LEARNING_READY,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: NoahOptimizerConfigEntry,
    async_add_entities:
        AddConfigEntryEntitiesCallback,
) -> None:
    """Set up NOAH Optimizer binary sensors."""

    entities = [
        NoahOptimizerBinarySensor(
            entry.runtime_data,
            entry,
            description,
        )
        for description in BINARY_SENSORS
    ]
    token = entry.options.get(CONF_NOAH_API_TOKEN)
    serial = entry.options.get(CONF_NOAH_DEVICE_SN)
    if token and serial:
        heating = GrowattHeatingCoordinator(hass, token, serial)
        await heating.async_refresh()
        entities.append(NoahHeatingBinarySensor(heating, entry, serial))
    async_add_entities(entities)


class NoahHeatingBinarySensor(
    CoordinatorEntity[GrowattHeatingCoordinator], BinarySensorEntity
):
    """Show the NOAH battery heater state; unavailable on API failures."""

    _attr_has_entity_name = True
    _attr_translation_key = "battery_heating"
    _attr_device_class = BinarySensorDeviceClass.HEAT

    def __init__(self, coordinator, entry, serial: str) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_battery_heating"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Growatt NOAH Optimizer",
            manufacturer="Community",
            model="NOAH Optimizer",
        )

    @property
    def is_on(self) -> bool:
        return self.coordinator.data is True


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
