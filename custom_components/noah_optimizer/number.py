"""Number entities for the Growatt NOAH Optimizer."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.number import (
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.const import PERCENTAGE, UnitOfEnergy, UnitOfPower, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import NoahOptimizerConfigEntry
from .const import (
    OPT_BATTERY_CAPACITY,
    OPT_CHARGE_EFFICIENCY,
    OPT_COMMAND_DEADBAND,
    OPT_COMMAND_STEP,
    OPT_DYNAMIC_SOC_CATCHUP_HOURS,
    OPT_EXPECTED_DAY_LOAD,
    OPT_FORECAST_FACTOR,
    OPT_FORECAST_SAFETY,
    OPT_GRID_RESERVE,
    OPT_MANUAL_OUTPUT,
    OPT_MAX_OUTPUT,
    OPT_MIN_SOC,
    OPT_NIGHT_MAX_OUTPUT,
    OPT_RELEASE_MARGIN,
    OPT_TARGET_SOC,
)
from .entity import NoahOptimizerEntity


@dataclass(frozen=True, kw_only=True)
class NoahNumberDescription(NumberEntityDescription):
    """Describe a NOAH Optimizer number."""

    option_key: str
    default: float


NUMBERS: tuple[NoahNumberDescription, ...] = (
    NoahNumberDescription(
        key="battery_capacity",
        translation_key="battery_capacity",
        option_key=OPT_BATTERY_CAPACITY,
        default=2.048,
        native_min_value=0.5,
        native_max_value=16.0,
        native_step=0.001,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        mode=NumberMode.BOX,
    ),
    NoahNumberDescription(
        key="target_soc",
        translation_key="target_soc",
        option_key=OPT_TARGET_SOC,
        default=95.0,
        native_min_value=50,
        native_max_value=100,
        native_step=1,
        native_unit_of_measurement=PERCENTAGE,
        mode=NumberMode.SLIDER,
    ),
    NoahNumberDescription(
        key="min_soc",
        translation_key="min_soc",
        option_key=OPT_MIN_SOC,
        default=10.0,
        native_min_value=0,
        native_max_value=30,
        native_step=1,
        native_unit_of_measurement=PERCENTAGE,
        mode=NumberMode.SLIDER,
    ),
    NoahNumberDescription(
        key="charge_efficiency",
        translation_key="charge_efficiency",
        option_key=OPT_CHARGE_EFFICIENCY,
        default=0.90,
        native_min_value=0.70,
        native_max_value=1.00,
        native_step=0.01,
        mode=NumberMode.BOX,
    ),
    NoahNumberDescription(
        key="forecast_factor",
        translation_key="forecast_factor",
        option_key=OPT_FORECAST_FACTOR,
        default=0.80,
        native_min_value=0.30,
        native_max_value=1.20,
        native_step=0.01,
        mode=NumberMode.SLIDER,
    ),
    NoahNumberDescription(
        key="forecast_safety",
        translation_key="forecast_safety",
        option_key=OPT_FORECAST_SAFETY,
        default=0.25,
        native_min_value=0,
        native_max_value=3,
        native_step=0.05,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        mode=NumberMode.BOX,
    ),
    NoahNumberDescription(
        key="release_margin",
        translation_key="release_margin",
        option_key=OPT_RELEASE_MARGIN,
        default=0.50,
        native_min_value=0.05,
        native_max_value=3,
        native_step=0.05,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        mode=NumberMode.BOX,
    ),
    NoahNumberDescription(
        key="expected_day_load",
        translation_key="expected_day_load",
        option_key=OPT_EXPECTED_DAY_LOAD,
        default=250,
        native_min_value=0,
        native_max_value=1500,
        native_step=10,
        native_unit_of_measurement=UnitOfPower.WATT,
        mode=NumberMode.BOX,
    ),
    NoahNumberDescription(
        key="grid_reserve",
        translation_key="grid_reserve",
        option_key=OPT_GRID_RESERVE,
        default=50,
        native_min_value=0,
        native_max_value=250,
        native_step=10,
        native_unit_of_measurement=UnitOfPower.WATT,
        mode=NumberMode.BOX,
    ),
    NoahNumberDescription(
        key="max_output",
        translation_key="max_output",
        option_key=OPT_MAX_OUTPUT,
        default=800,
        native_min_value=0,
        native_max_value=800,
        native_step=10,
        native_unit_of_measurement=UnitOfPower.WATT,
        mode=NumberMode.BOX,
    ),
    NoahNumberDescription(
        key="night_max_output",
        translation_key="night_max_output",
        option_key=OPT_NIGHT_MAX_OUTPUT,
        default=400,
        native_min_value=0,
        native_max_value=800,
        native_step=10,
        native_unit_of_measurement=UnitOfPower.WATT,
        mode=NumberMode.BOX,
    ),
    NoahNumberDescription(
        key="manual_output",
        translation_key="manual_output",
        option_key=OPT_MANUAL_OUTPUT,
        default=200,
        native_min_value=0,
        native_max_value=800,
        native_step=10,
        native_unit_of_measurement=UnitOfPower.WATT,
        mode=NumberMode.SLIDER,
    ),
    NoahNumberDescription(
        key="command_step",
        translation_key="command_step",
        option_key=OPT_COMMAND_STEP,
        default=50,
        native_min_value=10,
        native_max_value=200,
        native_step=10,
        native_unit_of_measurement=UnitOfPower.WATT,
        mode=NumberMode.BOX,
    ),
    NoahNumberDescription(
        key="command_deadband",
        translation_key="command_deadband",
        option_key=OPT_COMMAND_DEADBAND,
        default=50,
        native_min_value=10,
        native_max_value=250,
        native_step=10,
        native_unit_of_measurement=UnitOfPower.WATT,
        mode=NumberMode.BOX,
    ),
    NoahNumberDescription(
        key="dynamic_soc_catchup_hours",
        translation_key="dynamic_soc_catchup_hours",
        option_key=OPT_DYNAMIC_SOC_CATCHUP_HOURS,
        default=2.0,
        native_min_value=0.5,
        native_max_value=6.0,
        native_step=0.5,
        native_unit_of_measurement=UnitOfTime.HOURS,
        mode=NumberMode.BOX,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: NoahOptimizerConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up number entities."""
    async_add_entities(
        NoahOptimizerNumber(
            entry.runtime_data,
            entry,
            description,
        )
        for description in NUMBERS
    )


class NoahOptimizerNumber(NoahOptimizerEntity, NumberEntity):
    """Represent an optimizer setting."""

    entity_description: NoahNumberDescription

    def __init__(self, coordinator, entry, description: NoahNumberDescription) -> None:
        """Initialize the entity."""
        super().__init__(coordinator, entry)
        self.entry = entry
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"

    @property
    def native_value(self) -> float:
        """Return the configured value."""
        return float(
            self.coordinator.get_option(self.entity_description.option_key)
        )

    async def async_set_native_value(self, value: float) -> None:
        """Update the optimizer option."""
        await self.coordinator.async_set_option(
            self.entity_description.option_key,
            value,
        )
