"""Constants for the Growatt NOAH Optimizer."""

from __future__ import annotations

from datetime import timedelta
from typing import Final

from homeassistant.const import Platform


DOMAIN: Final = "noah_optimizer"

PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.SENSOR,
]

UPDATE_INTERVAL: Final = timedelta(minutes=1)


# Configuration keys
CONF_GRID_POWER: Final = "grid_power"
CONF_SOLAR_POWER: Final = "solar_power"
CONF_OUTPUT_POWER: Final = "output_power"
CONF_BATTERY_SOC: Final = "battery_soc"
CONF_CHARGING_POWER: Final = "charging_power"
CONF_DISCHARGE_POWER: Final = "discharge_power"
CONF_FORECAST_REMAINING: Final = "forecast_remaining"
CONF_SYSTEM_OUTPUT_POWER: Final = "system_output_power"
CONF_INVERT_GRID_SIGN: Final = "invert_grid_sign"


# Coordinator data keys
DATA_GRID_POWER: Final = "grid_power"
DATA_GRID_IMPORT: Final = "grid_import"
DATA_GRID_EXPORT: Final = "grid_export"

DATA_SOLAR_POWER: Final = "solar_power"
DATA_OUTPUT_POWER: Final = "output_power"

DATA_SOC: Final = "soc"

DATA_CHARGING_POWER: Final = "charging_power"
DATA_DISCHARGE_POWER: Final = "discharge_power"
DATA_BATTERY_POWER: Final = "battery_power"

DATA_HOME_LOAD: Final = "home_load"

DATA_FORECAST_REMAINING: Final = "forecast_remaining"

DATA_CRITICAL_DATA_OK: Final = "critical_data_ok"
DATA_FORECAST_AVAILABLE: Final = "forecast_available"
DATA_ACTUATOR_AVAILABLE: Final = "actuator_available"

DATA_STATUS: Final = "data_status"


STATUS_OK: Final = "ok"
STATUS_CRITICAL_DATA_MISSING: Final = "critical_data_missing"
STATUS_BATTERY_DATA_MISSING: Final = "battery_data_missing"
STATUS_FORECAST_UNAVAILABLE: Final = "forecast_unavailable"
STATUS_ACTUATOR_UNAVAILABLE: Final = "actuator_unavailable"