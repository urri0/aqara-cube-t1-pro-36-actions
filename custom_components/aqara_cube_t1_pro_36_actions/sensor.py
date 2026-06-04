"""Sensors for Aqara Cube T1 Pro 36 Actions."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, SENSOR_TYPES
from .runtime import CubeRuntime


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors for one cube."""
    runtime: CubeRuntime = hass.data[DOMAIN][entry.entry_id]
    entities = [Cube36Sensor(runtime, key, cfg) for key, cfg in SENSOR_TYPES.items()]
    async_add_entities(entities)


class Cube36Sensor(SensorEntity):
    """Diagnostic sensor backed by CubeRuntime."""

    # Keep entity_id generation independent from the Home Assistant device name.
    # This prevents collisions with existing user helpers like aqara_cube_t1_pro_* .
    _attr_has_entity_name = False

    def __init__(self, runtime: CubeRuntime, key: str, cfg: dict[str, Any]) -> None:
        self.runtime = runtime
        self.key = key
        self.entity_description = SensorEntityDescription(
            key=key,
            name=cfg["name"],
            icon=cfg.get("icon"),
            native_unit_of_measurement=cfg.get("unit"),
        )
        # v0.1.3-test:
        # Use both unique_id and suggested_object_id with cube36_ namespace.
        # _attr_has_entity_name is False, so HA should generate object_id from
        # suggested_object_id directly, e.g.:
        # sensor.cube36_aqara_cube_t1_pro_last_action
        self._attr_unique_id = f"cube36_{runtime.entry_id}_{runtime.entity_prefix}_{key}"
        self._attr_suggested_object_id = f"{runtime.entity_prefix}_{key}"
        self._attr_name = f"{runtime.entity_prefix} {cfg['name']}"
        self._attr_device_info = runtime.device_info
        self._remove_listener = None

    async def async_added_to_hass(self) -> None:
        self._remove_listener = self.runtime.async_add_listener(self.async_write_ha_state)

    async def async_will_remove_from_hass(self) -> None:
        if self._remove_listener:
            self._remove_listener()
            self._remove_listener = None

    @property
    def native_value(self) -> Any:
        value = self.runtime.data.get(self.key)
        if self.key in ("active_side", "last_side", "last_from_side") and value is None:
            return "unknown"
        if self.key == "event_history":
            return value or "none"
        return value

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        if self.key == "event_history":
            return {"history": list(self.runtime.history)}
        if self.key == "last_action":
            return {
                "active_side": self.runtime.data.get("active_side"),
                "last_side": self.runtime.data.get("last_side"),
                "last_from_side": self.runtime.data.get("last_from_side"),
                "last_angle": self.runtime.data.get("last_angle"),
                "event_count": self.runtime.data.get("event_count"),
                "event_history": list(self.runtime.history),
            }
        return None
