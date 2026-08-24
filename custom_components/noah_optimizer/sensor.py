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
from homeassistant.const import PERCENTAGE, UnitOfEnergy, UnitOfPower, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import NoahOptimizerConfigEntry
from .const import (
    CONTROLLER_BLEND,
    CONTROLLER_CHARGE_PRIORITY,
    CONTROLLER_MANUAL,
    CONTROLLER_MINIMUM_SOC,
    CONTROLLER_NIGHT,
    CONTROLLER_NO_FORECAST,
    CONTROLLER_OFF,
    CONTROLLER_PV_REDIRECT,
    CONTROLLER_SELF_CONSUMPTION,
    CONTROLLER_SOC_CATCHUP,
    CONTROLLER_SOC_RELEASE,
    CONTROLLER_TARGET_SOC_REACHED,
    CONTROL_STATUS_ACTUATOR_UNAVAILABLE,
    CONTROL_STATUS_COMMAND_FAILED,
    CONTROL_STATUS_COMMAND_SENT,
    CONTROL_STATUS_CRITICAL_DATA_MISSING,
    CONTROL_STATUS_DISABLED,
    CONTROL_STATUS_FAILSAFE,
    CONTROL_STATUS_IN_SYNC,
    CONTROL_STATUS_LEGACY_CONTROLLER_ACTIVE,
    CONTROL_STATUS_OPTIMIZER_DISABLED,
    CONTROL_STATUS_RATE_LIMITED,
    CONTROL_STATUS_TARGET_UNAVAILABLE,
    CONTROL_STATUS_WAITING_FOR_RETRY,
    DATA_AVAILABLE_BATTERY_ENERGY,
    DATA_BATTERY_POWER,
    DATA_CHARGE_NEED,
    DATA_CHARGE_PRIORITY_TARGET,
    DATA_CHARGING_POWER,
    DATA_CONTROLLER_MODE,
    DATA_DISCHARGE_POWER,
    DATA_DYNAMIC_REQUIRED_CHARGE_POWER,
    DATA_DYNAMIC_SOC_STATUS,
    DATA_DYNAMIC_SOC_TARGET,
    DATA_EFFECTIVE_FORECAST,
    DATA_EFFECTIVE_FORECAST_FACTOR,
    DATA_EXPECTED_LOAD_ENERGY,
    DATA_FORECAST_COVERAGE,
    DATA_FORECAST_MARGIN,
    DATA_FORECAST_REMAINING,
    DATA_FORECAST_REQUIRED_SOC,
    DATA_GRID_EXPORT,
    DATA_GRID_IMPORT,
    DATA_GRID_POWER,
    DATA_GRID_POWER_AVERAGE,
    DATA_HOME_LOAD,
    DATA_HOURS_TO_SUNSET,
    DATA_MINUTES_TO_TARGET,
    DATA_OUTPUT_POWER,
    DATA_OUTPUT_TARGET,
    DATA_PV_ENERGY_TODAY,
    DATA_PV_FORECAST_REFERENCE,
    DATA_PV_LEARNING_FACTOR,
    DATA_PV_LEARNING_LAST_RATIO,
    DATA_PV_LEARNING_SAMPLE_COUNT,
    DATA_REQUIRED_CHARGE_POWER,
    DATA_RELEASABLE_BATTERY_ENERGY,
    DATA_SELF_CONSUMPTION_TARGET,
    DATA_SOC,
    DATA_SOC_DEVIATION,
    DATA_SOC_RELEASE_FLOOR,
    DATA_SOC_RELEASE_TARGET,
    DATA_SOLAR_POWER,
    DATA_STATUS,
    DYNAMIC_SOC_AHEAD,
    DYNAMIC_SOC_BEHIND,
    DYNAMIC_SOC_NIGHT,
    DYNAMIC_SOC_ON_TRACK,
    STATUS_ACTUATOR_UNAVAILABLE,
    STATUS_BATTERY_DATA_MISSING,
    STATUS_CRITICAL_DATA_MISSING,
    STATUS_FORECAST_UNAVAILABLE,
    STATUS_OK,
)
from .entity import NoahOptimizerEntity


@dataclass(frozen=True, kw_only=True)
class NoahSensorDescription(SensorEntityDescription):
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
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
    ),
    NoahSensorDescription(
        key="grid_power_average",
        translation_key="grid_power_average",
        data_key=DATA_GRID_POWER_AVERAGE,
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    NoahSensorDescription(
        key="hours_to_sunset",
        translation_key="hours_to_sunset",
        data_key=DATA_HOURS_TO_SUNSET,
        native_unit_of_measurement=UnitOfTime.HOURS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    NoahSensorDescription(
        key="available_battery_energy",
        translation_key="available_battery_energy",
        data_key=DATA_AVAILABLE_BATTERY_ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY_STORAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    NoahSensorDescription(
        key="charge_need",
        translation_key="charge_need",
        data_key=DATA_CHARGE_NEED,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    NoahSensorDescription(
        key="effective_forecast",
        translation_key="effective_forecast",
        data_key=DATA_EFFECTIVE_FORECAST,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
    ),
    NoahSensorDescription(
        key="pv_learning_factor",
        translation_key="pv_learning_factor",
        data_key=DATA_PV_LEARNING_FACTOR,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    NoahSensorDescription(
        key="effective_forecast_factor",
        translation_key="effective_forecast_factor",
        data_key=DATA_EFFECTIVE_FORECAST_FACTOR,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    NoahSensorDescription(
        key="pv_learning_sample_count",
        translation_key="pv_learning_sample_count",
        data_key=DATA_PV_LEARNING_SAMPLE_COUNT,
    ),
    NoahSensorDescription(
        key="pv_learning_last_ratio",
        translation_key="pv_learning_last_ratio",
        data_key=DATA_PV_LEARNING_LAST_RATIO,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    NoahSensorDescription(
        key="pv_energy_today",
        translation_key="pv_energy_today",
        data_key=DATA_PV_ENERGY_TODAY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
    ),
    NoahSensorDescription(
        key="pv_forecast_reference",
        translation_key="pv_forecast_reference",
        data_key=DATA_PV_FORECAST_REFERENCE,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
    ),
    NoahSensorDescription(
        key="expected_load_energy",
        translation_key="expected_load_energy",
        data_key=DATA_EXPECTED_LOAD_ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
    ),
    NoahSensorDescription(
        key="forecast_margin",
        translation_key="forecast_margin",
        data_key=DATA_FORECAST_MARGIN,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    NoahSensorDescription(
        key="forecast_coverage",
        translation_key="forecast_coverage",
        data_key=DATA_FORECAST_COVERAGE,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    NoahSensorDescription(
        key="required_charge_power",
        translation_key="required_charge_power",
        data_key=DATA_REQUIRED_CHARGE_POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    NoahSensorDescription(
        key="minutes_to_target",
        translation_key="minutes_to_target",
        data_key=DATA_MINUTES_TO_TARGET,
        native_unit_of_measurement=UnitOfTime.MINUTES,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    NoahSensorDescription(
        key="dynamic_soc_target",
        translation_key="dynamic_soc_target",
        data_key=DATA_DYNAMIC_SOC_TARGET,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    NoahSensorDescription(
        key="soc_deviation",
        translation_key="soc_deviation",
        data_key=DATA_SOC_DEVIATION,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    NoahSensorDescription(
        key="dynamic_required_charge_power",
        translation_key="dynamic_required_charge_power",
        data_key=DATA_DYNAMIC_REQUIRED_CHARGE_POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    NoahSensorDescription(
        key="dynamic_soc_status",
        translation_key="dynamic_soc_status",
        data_key=DATA_DYNAMIC_SOC_STATUS,
        device_class=SensorDeviceClass.ENUM,
        options=[
            DYNAMIC_SOC_AHEAD,
            DYNAMIC_SOC_ON_TRACK,
            DYNAMIC_SOC_BEHIND,
            DYNAMIC_SOC_NIGHT,
        ],
    ),
    NoahSensorDescription(
        key="forecast_required_soc",
        translation_key="forecast_required_soc",
        data_key=DATA_FORECAST_REQUIRED_SOC,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    NoahSensorDescription(
        key="soc_release_floor",
        translation_key="soc_release_floor",
        data_key=DATA_SOC_RELEASE_FLOOR,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    NoahSensorDescription(
        key="releasable_battery_energy",
        translation_key="releasable_battery_energy",
        data_key=DATA_RELEASABLE_BATTERY_ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY_STORAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    NoahSensorDescription(
        key="soc_release_target",
        translation_key="soc_release_target",
        data_key=DATA_SOC_RELEASE_TARGET,
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    NoahSensorDescription(
        key="self_consumption_target",
        translation_key="self_consumption_target",
        data_key=DATA_SELF_CONSUMPTION_TARGET,
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    NoahSensorDescription(
        key="charge_priority_target",
        translation_key="charge_priority_target",
        data_key=DATA_CHARGE_PRIORITY_TARGET,
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    NoahSensorDescription(
        key="output_target",
        translation_key="output_target",
        data_key=DATA_OUTPUT_TARGET,
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    NoahSensorDescription(
        key="controller_mode",
        translation_key="controller_mode",
        data_key=DATA_CONTROLLER_MODE,
        device_class=SensorDeviceClass.ENUM,
        options=[
            CONTROLLER_OFF,
            CONTROLLER_MANUAL,
            CONTROLLER_SELF_CONSUMPTION,
            CONTROLLER_CHARGE_PRIORITY,
            CONTROLLER_MINIMUM_SOC,
            CONTROLLER_NIGHT,
            CONTROLLER_TARGET_SOC_REACHED,
            CONTROLLER_NO_FORECAST,
            CONTROLLER_BLEND,
            CONTROLLER_SOC_CATCHUP,
            CONTROLLER_SOC_RELEASE,
            CONTROLLER_PV_REDIRECT,
        ],
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


CONTROL_STATUS_OPTIONS = [
    CONTROL_STATUS_DISABLED,
    CONTROL_STATUS_OPTIMIZER_DISABLED,
    CONTROL_STATUS_LEGACY_CONTROLLER_ACTIVE,
    CONTROL_STATUS_CRITICAL_DATA_MISSING,
    CONTROL_STATUS_ACTUATOR_UNAVAILABLE,
    CONTROL_STATUS_TARGET_UNAVAILABLE,
    CONTROL_STATUS_RATE_LIMITED,
    CONTROL_STATUS_WAITING_FOR_RETRY,
    CONTROL_STATUS_IN_SYNC,
    CONTROL_STATUS_COMMAND_SENT,
    CONTROL_STATUS_COMMAND_FAILED,
    CONTROL_STATUS_FAILSAFE,
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: NoahOptimizerConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up NOAH Optimizer sensors."""
    sensors: list[SensorEntity] = [
        NoahOptimizerSensor(
            entry.runtime_data,
            entry,
            description,
        )
        for description in SENSORS
    ]
    sensors.append(
        NoahOptimizerControllerStatusSensor(
            entry.runtime_data,
            entry,
        )
    )
    async_add_entities(sensors)


class NoahOptimizerSensor(NoahOptimizerEntity, SensorEntity):
    """Represent a NOAH Optimizer sensor."""

    entity_description: NoahSensorDescription

    def __init__(self, coordinator, entry, description: NoahSensorDescription) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"

    @property
    def native_value(self) -> Any:
        """Return the current sensor value."""
        return self.coordinator.data.get(self.entity_description.data_key)

    @property
    def available(self) -> bool:
        """Return whether this sensor has valid data."""
        if self.entity_description.data_key == DATA_STATUS:
            return super().available

        return (
            super().available
            and self.coordinator.data.get(self.entity_description.data_key)
            is not None
        )


class NoahOptimizerControllerStatusSensor(NoahOptimizerEntity, SensorEntity):
    """Represent the low-level NOAH controller status."""

    _attr_device_class = SensorDeviceClass.ENUM
    _attr_translation_key = "controller_status"
    _attr_options = CONTROL_STATUS_OPTIONS

    def __init__(self, coordinator, entry) -> None:
        """Initialize the controller status sensor."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_controller_status"

    @property
    def native_value(self) -> str:
        """Return the current low-level controller status."""
        controller = getattr(self.coordinator, "controller", None)
        if controller is None:
            return CONTROL_STATUS_DISABLED
        return controller.status
