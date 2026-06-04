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

    # v0.1.4-test:
    # Let Home Assistant build entity_id from the device name + short entity name.
    # The device name is now "Cube36 <cube friendly name>", so the result becomes:
    # sensor.cube36_aqara_cube_t1_pro_active_side
    # instead of:
    # sensor.aqara_cube_t1_pro_cube36_aqara_cube_t1_pro_active_side
    _attr_has_entity_name = True

    def __init__(self, runtime: CubeRuntime, key: str, cfg: dict[str, Any]) -> None:
        self.runtime = runtime
        self.key = key
        self.entity_description = SensorEntityDescription(
            key=key,
            name=cfg["name"],
            icon=cfg.get("icon"),
            native_unit_of_measurement=cfg.get("unit"),
        )
        # Keep unique_id stable within this integration and separate from old test entities.
        # Entity name must stay short; HA will prepend the device name "Cube36 <name>".
        self._attr_unique_id = f"cube36_v014_{runtime.entry_id}_{key}"
        self._attr_suggested_object_id = key
        self._attr_name = cfg["name"]
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
    """Expose full diagnostic payload on the main last_action sensor.

    v0.1.5-test:
    The Lovelace debug/training card is intentionally single-entity based.
    It receives only sensor.<cube>_last_action and reads all other data from
    attributes. Sibling diagnostic sensors are still created for the HA device
    page, but the card no longer depends on guessing their entity_ids.
    """
    if self.key == "event_history":
        return {"history": list(self.runtime.history)}

    if self.key == "last_action":
        return {
            "active_side": self.runtime.data.get("active_side"),
            "last_side": self.runtime.data.get("last_side"),
            "last_from_side": self.runtime.data.get("last_from_side"),
            "last_angle": self.runtime.data.get("last_angle"),
            "last_lqi": self.runtime.data.get("last_lqi"),
            "battery": self.runtime.data.get("battery"),
            "voltage": self.runtime.data.get("voltage"),
            "operation_mode": self.runtime.data.get("operation_mode"),
            "event_count": self.runtime.data.get("event_count"),
            "last_event_time": self.runtime.data.get("last_event_time"),
            "event_history": list(self.runtime.history),
        }

    return None
