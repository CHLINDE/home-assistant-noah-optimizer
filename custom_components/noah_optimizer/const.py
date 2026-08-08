"""Constants for the Growatt NOAH Optimizer."""

from __future__ import annotations

from datetime import timedelta
from typing import Final

from homeassistant.const import Platform


DOMAIN: Final = "noah_optimizer"

PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SENSOR,
    Platform.SWITCH,
]

UPDATE_INTERVAL: Final = timedelta(minutes=1)


# ---------------------------------------------------------------------------
# Configuration entities
# ---------------------------------------------------------------------------

CONF_GRID_POWER: Final = "grid_power"
CONF_SOLAR_POWER: Final = "solar_power"
CONF_OUTPUT_POWER: Final = "output_power"
CONF_BATTERY_SOC: Final = "battery_soc"
CONF_CHARGING_POWER: Final = "charging_power"
CONF_DISCHARGE_POWER: Final = "discharge_power"
CONF_FORECAST_REMAINING: Final = "forecast_remaining"
CONF_SYSTEM_OUTPUT_POWER: Final = "system_output_power"
CONF_INVERT_GRID_SIGN: Final = "invert_grid_sign"
CONF_DASHBOARD_SHOW_IN_SIDEBAR: Final = (
    "dashboard_show_in_sidebar"
)

# ---------------------------------------------------------------------------
# Optimizer options
# ---------------------------------------------------------------------------

OPT_ENABLED: Final = "enabled"
OPT_MODE: Final = "mode"
OPT_CONTROL_ENABLED: Final = "control_enabled"

OPT_BATTERY_CAPACITY: Final = "battery_capacity"
OPT_TARGET_SOC: Final = "target_soc"
OPT_MIN_SOC: Final = "min_soc"
OPT_CHARGE_EFFICIENCY: Final = "charge_efficiency"

OPT_FORECAST_FACTOR: Final = "forecast_factor"
OPT_FORECAST_SAFETY: Final = "forecast_safety"
OPT_RELEASE_MARGIN: Final = "release_margin"

OPT_EXPECTED_DAY_LOAD: Final = "expected_day_load"
OPT_GRID_RESERVE: Final = "grid_reserve"

OPT_MAX_OUTPUT: Final = "max_output"
OPT_NIGHT_MAX_OUTPUT: Final = "night_max_output"
OPT_MANUAL_OUTPUT: Final = "manual_output"

OPT_COMMAND_STEP: Final = "command_step"
OPT_COMMAND_DEADBAND: Final = "command_deadband"


MODE_AUTOMATIC: Final = "automatic"
MODE_SELF_CONSUMPTION: Final = "self_consumption"
MODE_CHARGE_PRIORITY: Final = "charge_priority"
MODE_MANUAL: Final = "manual"


DEFAULT_OPTIONS: Final = {
    OPT_ENABLED: False,
    OPT_CONTROL_ENABLED: False,
    OPT_MODE: MODE_AUTOMATIC,

    OPT_BATTERY_CAPACITY: 2.048,
    OPT_TARGET_SOC: 95.0,
    OPT_MIN_SOC: 10.0,
    OPT_CHARGE_EFFICIENCY: 0.90,

    OPT_FORECAST_FACTOR: 0.80,
    OPT_FORECAST_SAFETY: 0.25,
    OPT_RELEASE_MARGIN: 0.50,

    OPT_EXPECTED_DAY_LOAD: 250.0,
    OPT_GRID_RESERVE: 50.0,

    OPT_MAX_OUTPUT: 800.0,
    OPT_NIGHT_MAX_OUTPUT: 400.0,
    OPT_MANUAL_OUTPUT: 200.0,

    OPT_COMMAND_STEP: 50.0,
    OPT_COMMAND_DEADBAND: 50.0,
}


# ---------------------------------------------------------------------------
# Coordinator data
# ---------------------------------------------------------------------------

DATA_GRID_POWER: Final = "grid_power"
DATA_GRID_POWER_AVERAGE: Final = "grid_power_average"
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

DATA_HOURS_TO_SUNSET: Final = "hours_to_sunset"
DATA_AVAILABLE_BATTERY_ENERGY: Final = "available_battery_energy"
DATA_CHARGE_NEED: Final = "charge_need"
DATA_EFFECTIVE_FORECAST: Final = "effective_forecast"
DATA_EXPECTED_LOAD_ENERGY: Final = "expected_load_energy"
DATA_FORECAST_MARGIN: Final = "forecast_margin"
DATA_FORECAST_COVERAGE: Final = "forecast_coverage"
DATA_REQUIRED_CHARGE_POWER: Final = "required_charge_power"
DATA_MINUTES_TO_TARGET: Final = "minutes_to_target"

DATA_SELF_CONSUMPTION_TARGET: Final = "self_consumption_target"
DATA_CHARGE_PRIORITY_TARGET: Final = "charge_priority_target"
DATA_OUTPUT_TARGET: Final = "output_target"
DATA_CONTROLLER_MODE: Final = "controller_mode"

DATA_CRITICAL_DATA_OK: Final = "critical_data_ok"
DATA_FORECAST_AVAILABLE: Final = "forecast_available"
DATA_ACTUATOR_AVAILABLE: Final = "actuator_available"
DATA_STATUS: Final = "data_status"


# ---------------------------------------------------------------------------
# Status values
# ---------------------------------------------------------------------------

STATUS_OK: Final = "ok"
STATUS_CRITICAL_DATA_MISSING: Final = "critical_data_missing"
STATUS_BATTERY_DATA_MISSING: Final = "battery_data_missing"
STATUS_FORECAST_UNAVAILABLE: Final = "forecast_unavailable"
STATUS_ACTUATOR_UNAVAILABLE: Final = "actuator_unavailable"


# ---------------------------------------------------------------------------
# Controller modes
# ---------------------------------------------------------------------------

CONTROLLER_OFF: Final = "off"
CONTROLLER_MANUAL: Final = "manual"
CONTROLLER_SELF_CONSUMPTION: Final = "self_consumption"
CONTROLLER_CHARGE_PRIORITY: Final = "charge_priority"
CONTROLLER_MINIMUM_SOC: Final = "minimum_soc"
CONTROLLER_NIGHT: Final = "night"
CONTROLLER_TARGET_SOC_REACHED: Final = "target_soc_reached"
CONTROLLER_NO_FORECAST: Final = "no_forecast"
CONTROLLER_BLEND: Final = "blended_reserve"