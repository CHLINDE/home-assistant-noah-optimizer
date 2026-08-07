"""Sensors for the Growatt NOAH Optimizer."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    UnitOfEnergy,
    UnitOfPower,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import (
    AddConfigEntryEntitiesCallback,
)

from . import NoahOptimizerConfigEntry
from .const import (
    DATA_BATTERY_POWER,
    DATA_CHARGING_POWER,
    DATA_DISCHARGE_POWER,
    DATA_FORECAST_REMAINING,
    DATA_GRID_EXPORT,
    DATA_GRID_IMPORT,
    DATA_GRID_POWER,
    DATA_HOME_LOAD,
    DATA_OUTPUT_POWER,
    DATA_SOC,
    DATA_SOLAR_POWER,
    DATA_STATUS,
    STATUS_ACTUATOR_UNAVAILABLE,
    STATUS_BATTERY_DATA_MISSING,
    STATUS_CRITICAL_DATA_MISSING,
    STATUS_FORECAST_UNAVAILABLE,
    STATUS_OK,
)
from .entity import NoahOptimizerEntity


@dataclass(
    frozen=True,
    kw_only=True,
)
class NoahSensorDescription(
    SensorEntityDescription
):
    """Describe a NOAH Optimizer sensor."""

    data_key: str


SENSORS: tuple[NoahSensorDescription, ...] = (
    NoahSensorDescription(
        key="grid_power",
        translation_key="grid_power",
        data_key=DATA_GRID_POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    NoahSensorDescription(
        key="grid_import",
        translation_key="grid_import",
        data_key=DATA_GRID_IMPORT,
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    NoahSensorDescription(
        key="grid_export",
        translation_key="grid_export",
        data_key=DATA_GRID_EXPORT,
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    NoahSensorDescription(
        key="solar_power",
        translation_key="solar_power",
        data_key=DATA_SOLAR_POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    NoahSensorDescription(
        key="output_power",
        translation_key="output_power",
        data_key=DATA_OUTPUT_POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    NoahSensorDescription(
        key="soc",
        translation_key="soc",
        data_key=DATA_SOC,
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    NoahSensorDescription(
        key="charging_power",
        translation_key="charging_power",
        data_key=DATA_CHARGING_POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    NoahSensorDescription(
        key="discharge_power",
        translation_key="discharge_power",
        data_key=DATA_DISCHARGE_POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    NoahSensorDescription(
        key="battery_power",
        translation_key="battery_power",
        data_key=DATA_BATTERY_POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    NoahSensorDescription(
        key="home_load",
        translation_key="home_load",
        data_key=DATA_HOME_LOAD,
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    NoahSensorDescription(
        key="forecast_remaining",
        translation_key="forecast_remaining",
        data_key=DATA_FORECAST_REMAINING,
        native_unit_of_measurement=(
            UnitOfEnergy.KILO_WATT_HOUR
        ),
        device_class=SensorDeviceClass.ENERGY,
    ),
    NoahSensorDescription(
        key="data_status",
        translation_key="data_status",
        data_key=DATA_STATUS,
        device_class=SensorDeviceClass.ENUM,
        options=[
            STATUS_OK,
            STATUS_CRITICAL_DATA_MISSING,
            STATUS_BATTERY_DATA_MISSING,
            STATUS_FORECAST_UNAVAILABLE,
            STATUS_ACTUATOR_UNAVAILABLE,
        ],
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: NoahOptimizerConfigEntry,
    async_add_entities:
        AddConfigEntryEntitiesCallback,
) -> None:
    """Set up NOAH Optimizer sensors."""

    async_add_entities(
        NoahOptimizerSensor(
            entry.runtime_data,
            entry,
            description,
        )
        for description in SENSORS
    )


class NoahOptimizerSensor(
    NoahOptimizerEntity,
    SensorEntity,
):
    """Represent a NOAH Optimizer sensor."""

    entity_description: NoahSensorDescription

    def __init__(
        self,
        coordinator,
        entry,
        description: NoahSensorDescription,
    ) -> None:
        """Initialize the sensor."""

        super().__init__(
            coordinator,
            entry,
        )

        self.entity_description = description

        self._attr_unique_id = (
            f"{entry.entry_id}_{description.key}"
        )

    @property
    def native_value(self) -> Any:
        """Return the current sensor value."""

        return self.coordinator.data.get(
            self.entity_description.data_key
        )

    @property
    def available(self) -> bool:
        """Return whether this sensor has valid data."""

        if self.entity_description.data_key == DATA_STATUS:
            return super().available

        return (
            super().available
            and self.coordinator.data.get(
                self.entity_description.data_key
            )
            is not None
        )