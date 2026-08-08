"""Config flow for the Growatt NOAH Optimizer."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers import selector

from .const import (
    CONF_BATTERY_SOC,
    CONF_CHARGING_POWER,
    CONF_DASHBOARD_SHOW_IN_SIDEBAR,
    CONF_DISCHARGE_POWER,
    CONF_FORECAST_REMAINING,
    CONF_GRID_POWER,
    CONF_INVERT_GRID_SIGN,
    CONF_OUTPUT_POWER,
    CONF_SOLAR_POWER,
    CONF_SYSTEM_OUTPUT_POWER,
    DOMAIN,
)


def _sensor_selector() -> selector.EntitySelector:
    """Return a selector for sensor entities."""

    return selector.EntitySelector(
        selector.EntitySelectorConfig(
            domain="sensor",
        )
    )


def _number_selector() -> selector.EntitySelector:
    """Return a selector for number entities."""

    return selector.EntitySelector(
        selector.EntitySelectorConfig(
            domain="number",
        )
    )


class NoahOptimizerConfigFlow(
    config_entries.ConfigFlow,
    domain=DOMAIN,
):
    """Handle the Growatt NOAH Optimizer config flow."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ):
        """Handle the initial configuration step."""

        errors: dict[str, str] = {}

        if user_input is not None:
            entity_keys = (
                CONF_GRID_POWER,
                CONF_SOLAR_POWER,
                CONF_OUTPUT_POWER,
                CONF_BATTERY_SOC,
                CONF_CHARGING_POWER,
                CONF_DISCHARGE_POWER,
                CONF_FORECAST_REMAINING,
                CONF_SYSTEM_OUTPUT_POWER,
            )

            for key in entity_keys:
                entity_id = user_input[key]

                if self.hass.states.get(entity_id) is None:
                    errors[key] = "entity_not_found"

            if not errors:
                return self.async_create_entry(
                    title="Growatt NOAH Optimizer",
                    data=user_input,
                )

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_GRID_POWER,
                ): _sensor_selector(),

                vol.Required(
                    CONF_SOLAR_POWER,
                ): _sensor_selector(),

                vol.Required(
                    CONF_OUTPUT_POWER,
                ): _sensor_selector(),

                vol.Required(
                    CONF_BATTERY_SOC,
                ): _sensor_selector(),

                vol.Required(
                    CONF_CHARGING_POWER,
                ): _sensor_selector(),

                vol.Required(
                    CONF_DISCHARGE_POWER,
                ): _sensor_selector(),

                vol.Required(
                    CONF_FORECAST_REMAINING,
                ): _sensor_selector(),

                vol.Required(
                    CONF_SYSTEM_OUTPUT_POWER,
                ): _number_selector(),

                vol.Optional(
                    CONF_INVERT_GRID_SIGN,
                    default=False,
                ): selector.BooleanSelector(),

                vol.Optional(
                    CONF_DASHBOARD_SHOW_IN_SIDEBAR,
                    default=True,
                ): selector.BooleanSelector(),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )