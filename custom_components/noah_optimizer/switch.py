"""Switch entities for the Growatt NOAH Optimizer."""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import NoahOptimizerConfigEntry
from .const import (
    OPT_CONTROL_ENABLED,
    OPT_DYNAMIC_SOC_ENABLED,
    OPT_ENABLED,
    OPT_SOC_RELEASE_ENABLED,
)
from .entity import NoahOptimizerEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: NoahOptimizerConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up optimizer switches."""
    async_add_entities(
        [
            NoahOptimizerEnabledSwitch(entry.runtime_data, entry),
            NoahOptimizerControlEnabledSwitch(entry.runtime_data, entry),
            NoahOptimizerDynamicSocSwitch(entry.runtime_data, entry),
            NoahOptimizerSocReleaseSwitch(entry.runtime_data, entry),
        ]
    )


class NoahOptimizerEnabledSwitch(NoahOptimizerEntity, SwitchEntity):
    """Enable optimizer calculations."""

    _attr_translation_key = "optimizer_enabled"

    def __init__(self, coordinator, entry) -> None:
        """Initialize the switch."""
        super().__init__(coordinator, entry)
        self.entry = entry
        self._attr_unique_id = f"{entry.entry_id}_optimizer_enabled"

    @property
    def is_on(self) -> bool:
        """Return enabled state."""
        return bool(self.coordinator.get_option(OPT_ENABLED))

    async def async_turn_on(self, **kwargs) -> None:
        """Enable optimizer calculations."""
        await self.coordinator.async_set_option(OPT_ENABLED, True)

    async def async_turn_off(self, **kwargs) -> None:
        """Disable optimizer calculations."""
        await self.coordinator.async_set_option(OPT_ENABLED, False)


class NoahOptimizerControlEnabledSwitch(NoahOptimizerEntity, SwitchEntity):
    """Enable active NOAH output control."""

    _attr_translation_key = "control_enabled"

    def __init__(self, coordinator, entry) -> None:
        """Initialize the switch."""
        super().__init__(coordinator, entry)
        self.entry = entry
        self._attr_unique_id = f"{entry.entry_id}_control_enabled"

    @property
    def is_on(self) -> bool:
        """Return active control state."""
        return bool(self.coordinator.get_option(OPT_CONTROL_ENABLED))

    async def async_turn_on(self, **kwargs) -> None:
        """Enable active NOAH control."""
        await self.coordinator.async_set_option(OPT_CONTROL_ENABLED, True)
        await self._async_refresh_controller()

    async def async_turn_off(self, **kwargs) -> None:
        """Disable active NOAH control."""
        await self.coordinator.async_set_option(OPT_CONTROL_ENABLED, False)
        await self._async_refresh_controller()

    async def _async_refresh_controller(self) -> None:
        """Evaluate the controller immediately after a switch change."""
        controller = getattr(self.coordinator, "controller", None)
        if controller is not None:
            await controller.async_control_tick()

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return active controller diagnostics."""
        controller = getattr(self.coordinator, "controller", None)

        if controller is None:
            return {"control_status": "unavailable"}

        last_command_at = controller.last_command_at

        return {
            "control_status": controller.status,
            "last_command_target": controller.last_command_target,
            "last_command_at": (
                last_command_at.isoformat() if last_command_at else None
            ),
        }


class NoahOptimizerDynamicSocSwitch(NoahOptimizerEntity, SwitchEntity):
    """Enable dynamic SOC influence on automatic control."""

    _attr_translation_key = "dynamic_soc_enabled"

    def __init__(self, coordinator, entry) -> None:
        """Initialize the switch."""
        super().__init__(coordinator, entry)
        self.entry = entry
        self._attr_unique_id = f"{entry.entry_id}_dynamic_soc_enabled"

    @property
    def is_on(self) -> bool:
        """Return whether dynamic SOC control is enabled."""
        return bool(self.coordinator.get_option(OPT_DYNAMIC_SOC_ENABLED))

    async def async_turn_on(self, **kwargs) -> None:
        """Enable dynamic SOC control."""
        await self.coordinator.async_set_option(OPT_DYNAMIC_SOC_ENABLED, True)
        await self._async_refresh_controller()

    async def async_turn_off(self, **kwargs) -> None:
        """Disable dynamic SOC control."""
        await self.coordinator.async_set_option(OPT_DYNAMIC_SOC_ENABLED, False)
        await self._async_refresh_controller()

    async def _async_refresh_controller(self) -> None:
        """Evaluate the controller immediately after a switch change."""
        controller = getattr(self.coordinator, "controller", None)
        if controller is not None:
            await controller.async_control_tick()


class NoahOptimizerSocReleaseSwitch(NoahOptimizerEntity, SwitchEntity):
    """Enable predictive SOC release while the battery is safely ahead."""

    _attr_translation_key = "soc_release_enabled"

    def __init__(self, coordinator, entry) -> None:
        """Initialize the switch."""
        super().__init__(coordinator, entry)
        self.entry = entry
        self._attr_unique_id = f"{entry.entry_id}_soc_release_enabled"

    @property
    def is_on(self) -> bool:
        """Return whether predictive SOC release is enabled."""
        return bool(self.coordinator.get_option(OPT_SOC_RELEASE_ENABLED))

    async def async_turn_on(self, **kwargs) -> None:
        """Enable predictive SOC release."""
        await self.coordinator.async_set_option(OPT_SOC_RELEASE_ENABLED, True)
        await self._async_refresh_controller()

    async def async_turn_off(self, **kwargs) -> None:
        """Disable predictive SOC release."""
        await self.coordinator.async_set_option(OPT_SOC_RELEASE_ENABLED, False)
        await self._async_refresh_controller()

    async def _async_refresh_controller(self) -> None:
        """Evaluate the controller immediately after a switch change."""
        controller = getattr(self.coordinator, "controller", None)
        if controller is not None:
            await controller.async_control_tick()

