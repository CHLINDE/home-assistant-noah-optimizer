"""Coordinator for the Growatt NOAH Optimizer."""

from __future__ import annotations

from collections import deque
import logging
import time
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
)
from homeassistant.util import dt as dt_util

from .const import (
    CONF_BATTERY_SOC,
    CONF_CHARGING_POWER,
    CONF_DISCHARGE_POWER,
    CONF_FORECAST_REMAINING,
    CONF_GRID_POWER,
    CONF_INVERT_GRID_SIGN,
    CONF_OUTPUT_POWER,
    CONF_SOLAR_POWER,
    CONF_SYSTEM_OUTPUT_POWER,
    CONTROLLER_BLEND,
    CONTROLLER_CHARGE_PRIORITY,
    CONTROLLER_MANUAL,
    CONTROLLER_MINIMUM_SOC,
    CONTROLLER_NIGHT,
    CONTROLLER_NO_FORECAST,
    CONTROLLER_OFF,
    CONTROLLER_SELF_CONSUMPTION,
    CONTROLLER_TARGET_SOC_REACHED,
    DATA_ACTUATOR_AVAILABLE,
    DATA_AVAILABLE_BATTERY_ENERGY,
    DATA_BATTERY_POWER,
    DATA_CHARGE_NEED,
    DATA_CHARGE_PRIORITY_TARGET,
    DATA_CHARGING_POWER,
    DATA_CONTROLLER_MODE,
    DATA_CRITICAL_DATA_OK,
    DATA_DISCHARGE_POWER,
    DATA_EFFECTIVE_FORECAST,
    DATA_EXPECTED_LOAD_ENERGY,
    DATA_FORECAST_AVAILABLE,
    DATA_FORECAST_COVERAGE,
    DATA_FORECAST_MARGIN,
    DATA_FORECAST_REMAINING,
    DATA_GRID_EXPORT,
    DATA_GRID_IMPORT,
    DATA_GRID_POWER,
    DATA_GRID_POWER_AVERAGE,
    DATA_HOME_LOAD,
    DATA_HOURS_TO_SUNSET,
    DATA_MINUTES_TO_TARGET,
    DATA_OUTPUT_POWER,
    DATA_OUTPUT_TARGET,
    DATA_REQUIRED_CHARGE_POWER,
    DATA_SELF_CONSUMPTION_TARGET,
    DATA_SOC,
    DATA_SOLAR_POWER,
    DATA_STATUS,
    DEFAULT_OPTIONS,
    DOMAIN,
    MODE_AUTOMATIC,
    MODE_CHARGE_PRIORITY,
    MODE_MANUAL,
    MODE_SELF_CONSUMPTION,
    OPT_BATTERY_CAPACITY,
    OPT_CHARGE_EFFICIENCY,
    OPT_COMMAND_STEP,
    OPT_ENABLED,
    OPT_EXPECTED_DAY_LOAD,
    OPT_FORECAST_FACTOR,
    OPT_FORECAST_SAFETY,
    OPT_GRID_RESERVE,
    OPT_MANUAL_OUTPUT,
    OPT_MAX_OUTPUT,
    OPT_MIN_SOC,
    OPT_MODE,
    OPT_NIGHT_MAX_OUTPUT,
    OPT_RELEASE_MARGIN,
    OPT_TARGET_SOC,
    STATUS_ACTUATOR_UNAVAILABLE,
    STATUS_BATTERY_DATA_MISSING,
    STATUS_CRITICAL_DATA_MISSING,
    STATUS_FORECAST_UNAVAILABLE,
    STATUS_OK,
    UPDATE_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)

GRID_AVERAGE_SECONDS = 300


class NoahOptimizerCoordinator(
    DataUpdateCoordinator[dict[str, Any]]
):
    """Read and calculate NOAH Optimizer data."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
    ) -> None:
        """Initialize coordinator."""

        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
            always_update=False,
        )

        self.entry = entry

        self._grid_samples: deque[
            tuple[float, float]
        ] = deque()

        self._last_grid_timestamp: float | None = None

    def get_option(
        self,
        key: str,
    ) -> Any:
        """Return an option or its default value."""

        return self.entry.options.get(
            key,
            DEFAULT_OPTIONS[key],
        )

    async def async_set_option(
        self,
        key: str,
        value: Any,
    ) -> None:
        """Store an optimizer option."""

        options = dict(self.entry.options)
        options[key] = value

        self.hass.config_entries.async_update_entry(
            self.entry,
            options=options,
        )

        await self.async_update_from_states()

    async def async_update_from_states(self) -> None:
        """Immediately update data from HA states."""

        data = await self._async_update_data()
        self.async_set_updated_data(data)

    def _read_numeric_state(
        self,
        entity_id: str,
    ) -> tuple[float | None, str | None]:
        """Read numeric state and unit."""

        state = self.hass.states.get(entity_id)

        if state is None:
            return None, None

        if state.state in {
            STATE_UNKNOWN,
            STATE_UNAVAILABLE,
            "",
        }:
            return (
                None,
                state.attributes.get(
                    "unit_of_measurement"
                ),
            )

        try:
            value = float(state.state)
        except (TypeError, ValueError):
            return (
                None,
                state.attributes.get(
                    "unit_of_measurement"
                ),
            )

        return (
            value,
            state.attributes.get(
                "unit_of_measurement"
            ),
        )

    def _read_power_w(
        self,
        entity_id: str,
    ) -> float | None:
        """Read power and normalize to watts."""

        value, unit = self._read_numeric_state(
            entity_id
        )

        if value is None:
            return None

        if unit == "W":
            return value

        if unit == "kW":
            return value * 1000

        return None

    def _read_energy_kwh(
        self,
        entity_id: str,
    ) -> float | None:
        """Read energy and normalize to kWh."""

        value, unit = self._read_numeric_state(
            entity_id
        )

        if value is None:
            return None

        if unit == "kWh":
            return value

        if unit == "Wh":
            return value / 1000

        return None

    def _read_soc(
        self,
        entity_id: str,
    ) -> float | None:
        """Read SOC in percent."""

        value, unit = self._read_numeric_state(
            entity_id
        )

        if value is None:
            return None

        if unit not in {"%", None, ""}:
            return None

        if not 0 <= value <= 100:
            return None

        return value

    def _entity_available(
        self,
        entity_id: str,
    ) -> bool:
        """Return whether entity is available."""

        state = self.hass.states.get(entity_id)

        return (
            state is not None
            and state.state
            not in {
                STATE_UNKNOWN,
                STATE_UNAVAILABLE,
                "",
            }
        )

    def _update_grid_average(
        self,
        grid_power: float,
    ) -> float:
        """Calculate five-minute time-weighted grid average."""

        state = self.hass.states.get(
            self.entry.data[CONF_GRID_POWER]
        )

        now_ts = time.time()

        state_ts = (
            state.last_updated.timestamp()
            if state is not None
            else now_ts
        )

        if state_ts != self._last_grid_timestamp:
            self._grid_samples.append(
                (state_ts, grid_power)
            )
            self._last_grid_timestamp = state_ts

        cutoff = now_ts - GRID_AVERAGE_SECONDS

        while (
            len(self._grid_samples) >= 2
            and self._grid_samples[1][0] <= cutoff
        ):
            self._grid_samples.popleft()

        if not self._grid_samples:
            return grid_power

        previous_value = self._grid_samples[0][1]
        previous_time = cutoff
        weighted_sum = 0.0

        for sample_time, sample_value in self._grid_samples:
            if sample_time <= cutoff:
                previous_value = sample_value
                continue

            duration = sample_time - previous_time

            if duration > 0:
                weighted_sum += (
                    previous_value * duration
                )

            previous_time = sample_time
            previous_value = sample_value

        remaining = now_ts - previous_time

        if remaining > 0:
            weighted_sum += (
                previous_value * remaining
            )

        return (
            weighted_sum / GRID_AVERAGE_SECONDS
        )

    def _hours_to_sunset(self) -> float:
        """Return hours until next sunset."""

        sun = self.hass.states.get("sun.sun")

        if (
            sun is None
            or sun.state != "above_horizon"
        ):
            return 0.0

        next_setting = sun.attributes.get(
            "next_setting"
        )

        if not next_setting:
            return 0.0

        sunset = dt_util.parse_datetime(
            str(next_setting)
        )

        if sunset is None:
            return 0.0

        seconds = (
            sunset - dt_util.utcnow()
        ).total_seconds()

        return max(
            seconds / 3600,
            0.0,
        )

    def _is_night(
        self,
        solar_power: float,
    ) -> bool:
        """Return whether night mode applies."""

        sun = self.hass.states.get("sun.sun")

        if sun is None:
            return solar_power < 20

        if sun.state == "below_horizon":
            return True

        elevation = float(
            sun.attributes.get(
                "elevation",
                90,
            )
        )

        return (
            elevation < 3
            and solar_power < 20
        )

    @staticmethod
    def _round_to_step(
        value: float,
        step: float,
        maximum: float,
    ) -> float:
        """Limit and round target to configured step."""

        limited = min(
            max(value, 0.0),
            maximum,
        )

        if step <= 0:
            return round(limited)

        return round(
            limited / step
        ) * step

    async def _async_update_data(
        self,
    ) -> dict[str, Any]:
        """Read states and calculate optimizer values."""

        grid_power = self._read_power_w(
            self.entry.data[CONF_GRID_POWER]
        )

        solar_power = self._read_power_w(
            self.entry.data[CONF_SOLAR_POWER]
        )

        output_power = self._read_power_w(
            self.entry.data[CONF_OUTPUT_POWER]
        )

        soc = self._read_soc(
            self.entry.data[CONF_BATTERY_SOC]
        )

        charging_power = self._read_power_w(
            self.entry.data[
                CONF_CHARGING_POWER
            ]
        )

        discharging_power = self._read_power_w(
            self.entry.data[
                CONF_DISCHARGE_POWER
            ]
        )

        forecast_remaining = (
            self._read_energy_kwh(
                self.entry.data[
                    CONF_FORECAST_REMAINING
                ]
            )
        )

        if (
            grid_power is not None
            and self.entry.data.get(
                CONF_INVERT_GRID_SIGN,
                False,
            )
        ):
            grid_power *= -1

        critical_data_ok = all(
            value is not None
            for value in (
                grid_power,
                solar_power,
                output_power,
                soc,
            )
        )

        battery_data_ok = (
            charging_power is not None
            and discharging_power is not None
        )

        forecast_available = (
            forecast_remaining is not None
        )

        actuator_available = (
            self._entity_available(
                self.entry.data[
                    CONF_SYSTEM_OUTPUT_POWER
                ]
            )
        )

        if not critical_data_ok:
            status = STATUS_CRITICAL_DATA_MISSING
        elif not actuator_available:
            status = STATUS_ACTUATOR_UNAVAILABLE
        elif not battery_data_ok:
            status = STATUS_BATTERY_DATA_MISSING
        elif not forecast_available:
            status = STATUS_FORECAST_UNAVAILABLE
        else:
            status = STATUS_OK

        if not critical_data_ok:
            return {
                DATA_GRID_POWER: grid_power,
                DATA_GRID_POWER_AVERAGE: None,
                DATA_GRID_IMPORT: None,
                DATA_GRID_EXPORT: None,
                DATA_SOLAR_POWER: solar_power,
                DATA_OUTPUT_POWER: output_power,
                DATA_SOC: soc,
                DATA_CHARGING_POWER: charging_power,
                DATA_DISCHARGE_POWER: discharging_power,
                DATA_BATTERY_POWER: None,
                DATA_HOME_LOAD: None,
                DATA_FORECAST_REMAINING:
                    forecast_remaining,
                DATA_HOURS_TO_SUNSET: None,
                DATA_AVAILABLE_BATTERY_ENERGY: None,
                DATA_CHARGE_NEED: None,
                DATA_EFFECTIVE_FORECAST: None,
                DATA_EXPECTED_LOAD_ENERGY: None,
                DATA_FORECAST_MARGIN: None,
                DATA_FORECAST_COVERAGE: None,
                DATA_REQUIRED_CHARGE_POWER: None,
                DATA_MINUTES_TO_TARGET: None,
                DATA_SELF_CONSUMPTION_TARGET: None,
                DATA_CHARGE_PRIORITY_TARGET: None,
                DATA_OUTPUT_TARGET: None,
                DATA_CONTROLLER_MODE:
                    CONTROLLER_OFF,
                DATA_CRITICAL_DATA_OK: False,
                DATA_FORECAST_AVAILABLE:
                    forecast_available,
                DATA_ACTUATOR_AVAILABLE:
                    actuator_available,
                DATA_STATUS: status,
            }

        assert grid_power is not None
        assert solar_power is not None
        assert output_power is not None
        assert soc is not None

        grid_average = (
            self._update_grid_average(
                grid_power
            )
        )

        grid_import = max(
            grid_power,
            0.0,
        )

        grid_export = max(
            -grid_power,
            0.0,
        )

        home_load = max(
            grid_power + output_power,
            0.0,
        )

        battery_power = (
            discharging_power - charging_power
            if battery_data_ok
            else None
        )

        capacity = float(
            self.get_option(
                OPT_BATTERY_CAPACITY
            )
        )

        target_soc = float(
            self.get_option(
                OPT_TARGET_SOC
            )
        )

        min_soc = float(
            self.get_option(
                OPT_MIN_SOC
            )
        )

        efficiency = float(
            self.get_option(
                OPT_CHARGE_EFFICIENCY
            )
        )

        forecast_factor = float(
            self.get_option(
                OPT_FORECAST_FACTOR
            )
        )

        forecast_safety = float(
            self.get_option(
                OPT_FORECAST_SAFETY
            )
        )

        release_margin = float(
            self.get_option(
                OPT_RELEASE_MARGIN
            )
        )

        expected_day_load = float(
            self.get_option(
                OPT_EXPECTED_DAY_LOAD
            )
        )

        grid_reserve = float(
            self.get_option(
                OPT_GRID_RESERVE
            )
        )

        max_output = float(
            self.get_option(
                OPT_MAX_OUTPUT
            )
        )

        night_max_output = float(
            self.get_option(
                OPT_NIGHT_MAX_OUTPUT
            )
        )

        manual_output = float(
            self.get_option(
                OPT_MANUAL_OUTPUT
            )
        )

        command_step = float(
            self.get_option(
                OPT_COMMAND_STEP
            )
        )

        selected_mode = str(
            self.get_option(
                OPT_MODE
            )
        )

        enabled = bool(
            self.get_option(
                OPT_ENABLED
            )
        )

        hours_to_sunset = (
            self._hours_to_sunset()
        )

        available_battery_energy = (
            capacity
            * max(
                soc - min_soc,
                0.0,
            )
            / 100
        )

        charge_deficit = max(
            target_soc - soc,
            0.0,
        )

        charge_need = (
            capacity
            * charge_deficit
            / 100
            / max(
                efficiency,
                0.1,
            )
        )

        effective_forecast = (
            (forecast_remaining or 0.0)
            * forecast_factor
        )

        expected_load_energy = (
            hours_to_sunset
            * expected_day_load
            / 1000
        )

        forecast_margin = (
            effective_forecast
            - charge_need
            - expected_load_energy
            - forecast_safety
        )

        required_energy = (
            charge_need
            + expected_load_energy
            + forecast_safety
        )

        forecast_coverage = (
            100.0
            if required_energy <= 0
            else (
                effective_forecast
                / required_energy
                * 100
            )
        )

        required_charge_power = (
            0.0
            if hours_to_sunset <= 0
            else (
                charge_need
                * 1000
                / hours_to_sunset
            )
        )

        if charge_need <= 0:
            minutes_to_target = 0.0
        elif (
            charging_power is None
            or charging_power < 10
        ):
            minutes_to_target = 9999.0
        else:
            minutes_to_target = (
                charge_need
                * 1000
                / charging_power
                * 60
            )

        # Same behaviour as the YAML optimizer:
        # react immediately to export while the target SOC
        # has not yet been reached.
        if (
            soc < target_soc
            and grid_power < 0
        ):
            control_grid = grid_power
        else:
            control_grid = grid_average

        self_consumption_target = min(
            max(
                output_power
                + control_grid
                - grid_reserve,
                0.0,
            ),
            max_output,
        )

        charge_priority_raw = max(
            solar_power
            - required_charge_power,
            0.0,
        )

        charge_priority_target = min(
            charge_priority_raw,
            self_consumption_target,
        )

        night = self._is_night(
            solar_power
        )

        if not enabled:
            controller_mode = (
                CONTROLLER_OFF
            )

        elif selected_mode == MODE_MANUAL:
            controller_mode = (
                CONTROLLER_MANUAL
            )

        elif (
            selected_mode
            == MODE_SELF_CONSUMPTION
        ):
            controller_mode = (
                CONTROLLER_SELF_CONSUMPTION
            )

        elif (
            selected_mode
            == MODE_CHARGE_PRIORITY
        ):
            controller_mode = (
                CONTROLLER_CHARGE_PRIORITY
            )

        elif soc <= min_soc:
            controller_mode = (
                CONTROLLER_MINIMUM_SOC
            )

        elif night:
            controller_mode = (
                CONTROLLER_NIGHT
            )

        elif soc >= target_soc:
            controller_mode = (
                CONTROLLER_TARGET_SOC_REACHED
            )

        elif not forecast_available:
            controller_mode = (
                CONTROLLER_NO_FORECAST
            )

        elif forecast_margin <= 0:
            controller_mode = (
                CONTROLLER_CHARGE_PRIORITY
            )

        elif forecast_margin >= release_margin:
            controller_mode = (
                CONTROLLER_SELF_CONSUMPTION
            )

        else:
            controller_mode = (
                CONTROLLER_BLEND
            )

        if selected_mode == MODE_MANUAL:
            raw_target = manual_output

        elif (
            selected_mode
            == MODE_SELF_CONSUMPTION
        ):
            raw_target = (
                self_consumption_target
            )

        elif (
            selected_mode
            == MODE_CHARGE_PRIORITY
        ):
            raw_target = (
                charge_priority_target
            )

        elif soc <= min_soc:
            raw_target = 0.0

        elif night:
            raw_target = min(
                self_consumption_target,
                night_max_output,
            )

        elif soc >= target_soc:
            raw_target = (
                self_consumption_target
            )

        elif not forecast_available:
            raw_target = (
                charge_priority_target
            )

        elif forecast_margin <= 0:
            raw_target = (
                charge_priority_target
            )

        elif forecast_margin >= release_margin:
            raw_target = (
                self_consumption_target
            )

        else:
            blend = min(
                max(
                    forecast_margin
                    / max(
                        release_margin,
                        0.05,
                    ),
                    0.0,
                ),
                1.0,
            )

            raw_target = (
                charge_priority_target
                + blend
                * (
                    self_consumption_target
                    - charge_priority_target
                )
            )

        output_target = self._round_to_step(
            raw_target,
            command_step,
            max_output,
        )

        return {
            DATA_GRID_POWER:
                round(grid_power),
            DATA_GRID_POWER_AVERAGE:
                round(grid_average),
            DATA_GRID_IMPORT:
                round(grid_import),
            DATA_GRID_EXPORT:
                round(grid_export),

            DATA_SOLAR_POWER:
                round(solar_power),
            DATA_OUTPUT_POWER:
                round(output_power),

            DATA_SOC:
                round(soc, 1),

            DATA_CHARGING_POWER:
                round(charging_power)
                if charging_power is not None
                else None,

            DATA_DISCHARGE_POWER:
                round(discharging_power)
                if discharging_power is not None
                else None,

            DATA_BATTERY_POWER:
                round(battery_power)
                if battery_power is not None
                else None,

            DATA_HOME_LOAD:
                round(home_load),

            DATA_FORECAST_REMAINING:
                round(forecast_remaining, 3)
                if forecast_remaining is not None
                else None,

            DATA_HOURS_TO_SUNSET:
                round(hours_to_sunset, 2),

            DATA_AVAILABLE_BATTERY_ENERGY:
                round(
                    available_battery_energy,
                    3,
                ),

            DATA_CHARGE_NEED:
                round(charge_need, 3),

            DATA_EFFECTIVE_FORECAST:
                round(
                    effective_forecast,
                    3,
                ),

            DATA_EXPECTED_LOAD_ENERGY:
                round(
                    expected_load_energy,
                    3,
                ),

            DATA_FORECAST_MARGIN:
                round(
                    forecast_margin,
                    3,
                ),

            DATA_FORECAST_COVERAGE:
                round(forecast_coverage),

            DATA_REQUIRED_CHARGE_POWER:
                round(
                    required_charge_power
                ),

            DATA_MINUTES_TO_TARGET:
                round(minutes_to_target),

            DATA_SELF_CONSUMPTION_TARGET:
                round(
                    self_consumption_target
                ),

            DATA_CHARGE_PRIORITY_TARGET:
                round(
                    charge_priority_target
                ),

            DATA_OUTPUT_TARGET:
                round(output_target),

            DATA_CONTROLLER_MODE:
                controller_mode,

            DATA_CRITICAL_DATA_OK:
                critical_data_ok,

            DATA_FORECAST_AVAILABLE:
                forecast_available,

            DATA_ACTUATOR_AVAILABLE:
                actuator_available,

            DATA_STATUS:
                status,
        }