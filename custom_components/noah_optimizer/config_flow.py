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
    CONF_NOAH_API_TOKEN,
    CONF_NOAH_DEVICE_SN,
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

    @staticmethod
    def async_get_options_flow(config_entry):
        """Offer optional Growatt OpenAPI settings to existing installations."""
        return NoahOptimizerOptionsFlow(config_entry)

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


class NoahOptimizerOptionsFlow(config_entries.OptionsFlow):
    """Configure optional NOAH diagnostics without changing source entities."""

    def __init__(self, config_entry) -> None:
        self._entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        """Configure the NOAH OpenAPI credentials."""
        errors: dict[str, str] = {}
        if user_input is not None:
            token = user_input.get(CONF_NOAH_API_TOKEN, "").strip()
            serial = user_input.get(CONF_NOAH_DEVICE_SN, "").strip()
            if bool(token) != bool(serial):
                errors["base"] = "api_credentials_incomplete"
            else:
                return self.async_create_entry(
                    data={
                        **self._entry.options,
                        CONF_NOAH_API_TOKEN: token,
                        CONF_NOAH_DEVICE_SN: serial,
                    }
                )

        options = self._entry.options
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_NOAH_API_TOKEN,
                        default=options.get(CONF_NOAH_API_TOKEN, ""),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.PASSWORD,
                        )
                    ),
                    vol.Optional(
                        CONF_NOAH_DEVICE_SN,
                        default=options.get(CONF_NOAH_DEVICE_SN, ""),
                    ): selector.TextSelector(),
                }
            ),
            errors=errors,
        )
