"""Runtime and MQTT/action handling for Aqara Cube T1 Pro 36 Actions."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from copy import deepcopy
from datetime import datetime
import json
import logging
from typing import Any

from homeassistant.components import mqtt
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.util import slugify

from .const import (
    ACTIONS,
    CONF_ACTIONS,
    CONF_CUSTOM_OVERRIDES,
    CONF_DEBOUNCE,
    CONF_ENTITY,
    CONF_HISTORY_SIZE,
    CONF_MODE,
    CONF_PROFILE,
    CONF_SECONDARY_ENTITY,
    CONF_SIDES,
    DEFAULT_OPTIONS,
    DOMAIN,
    FLIP_ACTIONS,
)

_LOGGER = logging.getLogger(__name__)


class CubeRuntime:
    """Per-config-entry runtime state."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry_id: str,
        name: str,
        topic: str,
        options: dict[str, Any],
    ) -> None:
        self.hass = hass
        self.entry_id = entry_id
        self.name = name
        self.topic = topic
        self.options = self._merge_options(options)
        self._listeners: list[Callable[[], None]] = []
        self._unsubscribe_mqtt: Callable[[], None] | None = None
        self._last_action_ts: dict[str, float] = {}
        self.context_side: int | None = None
        self.history: list[str] = []
        self.data: dict[str, Any] = {
            "last_action": None,
            "active_side": None,
            "last_side": None,
            "last_from_side": None,
            "last_angle": None,
            "last_lqi": None,
            "battery": None,
            "voltage": None,
            "operation_mode": None,
            "event_count": 0,
            "last_event_time": None,
            "event_history": None,
        }

    @staticmethod
    def _merge_options(options: dict[str, Any] | None) -> dict[str, Any]:
        merged = deepcopy(DEFAULT_OPTIONS)
        if not options:
            return merged

        for key, value in options.items():
            if key == CONF_SIDES and isinstance(value, dict):
                for side, side_conf in value.items():
                    if side not in merged[CONF_SIDES]:
                        merged[CONF_SIDES][side] = {}
                    if isinstance(side_conf, dict):
                        merged[CONF_SIDES][side].update(side_conf)
                        actions = side_conf.get(CONF_ACTIONS)
                        if isinstance(actions, dict):
                            merged[CONF_SIDES][side].setdefault(CONF_ACTIONS, {})
                            merged[CONF_SIDES][side][CONF_ACTIONS].update(actions)
            elif key == CONF_DEBOUNCE and isinstance(value, dict):
                merged[CONF_DEBOUNCE].update(value)
            else:
                merged[key] = value
        return merged

    @property
    def entity_prefix(self) -> str:
        """Stable suggested entity prefix, independent from existing helpers."""
        return f"cube36_{slugify(self.name)}"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self.entry_id)},
            name=f"Cube36 {self.name}",
            manufacturer="Aqara / Lumi",
            model="Aqara Cube T1 Pro",
            sw_version="36 Actions 0.1.4-test",
        )

    async def async_start(self) -> None:
        """Subscribe to MQTT topic."""
        if self._unsubscribe_mqtt is not None:
            return

        async def _message_received(msg: Any) -> None:
            self.hass.async_create_task(self.async_handle_payload(msg.payload))

        _LOGGER.info("Subscribing to Aqara Cube topic: %s", self.topic)
        self._unsubscribe_mqtt = await mqtt.async_subscribe(
            self.hass,
            self.topic,
            _message_received,
            qos=0,
            encoding="utf-8",
        )

    async def async_stop(self) -> None:
        """Unsubscribe MQTT."""
        if self._unsubscribe_mqtt is not None:
            self._unsubscribe_mqtt()
            self._unsubscribe_mqtt = None

    @callback
    def async_add_listener(self, listener: Callable[[], None]) -> Callable[[], None]:
        self._listeners.append(listener)

        @callback
        def _remove() -> None:
            if listener in self._listeners:
                self._listeners.remove(listener)

        return _remove

    @callback
    def _notify(self) -> None:
        for listener in list(self._listeners):
            listener()

    async def async_handle_payload(self, raw_payload: str | bytes | dict[str, Any]) -> None:
        """Handle real or simulated MQTT payload."""
        try:
            if isinstance(raw_payload, dict):
                payload = raw_payload
            elif isinstance(raw_payload, bytes):
                payload = json.loads(raw_payload.decode("utf-8"))
            else:
                payload = json.loads(raw_payload)
        except Exception as err:  # noqa: BLE001
            _LOGGER.warning("Invalid cube MQTT payload on %s: %s", self.topic, err)
            return

        action = payload.get("action")
        if not action:
            return

        side = self._normalize_side(payload.get("side"))
        from_side = self._normalize_side(payload.get("action_from_side"))
        effective_side = self._effective_side(side)

        if side is not None and action not in ("shake", "throw"):
            self.context_side = side
            effective_side = side

        angle = self._to_float(payload.get("action_angle"))
        event_time = datetime.now().replace(microsecond=0).isoformat(sep=" ")

        self.data.update(
            {
                "last_action": action,
                "active_side": effective_side,
                "last_side": side,
                "last_from_side": from_side,
                "last_angle": round(angle, 1) if angle is not None else None,
                "last_lqi": payload.get("linkquality"),
                "battery": payload.get("battery"),
                "voltage": payload.get("voltage"),
                "operation_mode": payload.get("operation_mode"),
                "event_count": int(self.data.get("event_count") or 0) + 1,
                "last_event_time": event_time,
            }
        )

        event_line = self._format_event_line(event_time, action, side, from_side, angle)
        self.history.insert(0, event_line)
        self.history = self.history[: self._history_size]
        self.data["event_history"] = self.history[0] if self.history else None
        self._notify()

        if action in FLIP_ACTIONS:
            _LOGGER.debug("Cube flip event updated context only: %s", event_line)
            return

        if effective_side is None:
            _LOGGER.debug("Cube action ignored because effective side is unknown: %s", event_line)
            return

        await self._execute_side_action(effective_side, action, payload)

    @property
    def _history_size(self) -> int:
        return int(self.options.get(CONF_HISTORY_SIZE, 10) or 10)

    def _normalize_side(self, value: Any) -> int | None:
        try:
            side = int(value)
        except (TypeError, ValueError):
            return None
        if 1 <= side <= 6:
            return side
        return None

    def _effective_side(self, payload_side: int | None) -> int | None:
        if payload_side is not None:
            return payload_side
        if self.context_side is not None and 1 <= self.context_side <= 6:
            return self.context_side
        return None

    @staticmethod
    def _to_float(value: Any) -> float | None:
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _format_event_line(
        event_time: str,
        action: str,
        side: int | None,
        from_side: int | None,
        angle: float | None,
    ) -> str:
        short_time = event_time.split(" ")[-1]
        if action in FLIP_ACTIONS:
            return f"{short_time} · {action} · {from_side or '—'}→{side or '—'}"
        if action in ("rotate_left", "rotate_right"):
            angle_text = "—" if angle is None else f"{angle:.1f}°"
            return f"{short_time} · {action} · {angle_text}"
        return f"{short_time} · {action} · side {side or '—'}"

    async def _execute_side_action(
        self,
        side: int,
        action: str,
        payload: dict[str, Any],
    ) -> None:
        if action not in ACTIONS:
            return

        side_conf = self.options.get(CONF_SIDES, {}).get(str(side), {})
        mode = side_conf.get(CONF_MODE, "disabled")
        if mode != "managed":
            _LOGGER.debug("Side %s action %s ignored because mode=%s", side, action, mode)
            return

        if not self._debounce_ok(side, action):
            _LOGGER.debug("Side %s action %s ignored by debounce", side, action)
            return

        profile = side_conf.get(CONF_PROFILE, "custom")
        custom_enabled = bool(side_conf.get(CONF_CUSTOM_OVERRIDES)) or profile == "custom"
        custom_action = (side_conf.get(CONF_ACTIONS) or {}).get(action, "")

        if custom_enabled and custom_action:
            await self._run_custom_action(custom_action)
            return

        if profile == "media":
            await self._run_media_action(side_conf, action, payload)
        elif profile == "light":
            await self._run_light_action(side_conf, action, payload)
        elif profile == "climate":
            await self._run_climate_action(side_conf, action, payload)
        elif profile == "custom":
            _LOGGER.debug("Custom profile side %s action %s has no custom action", side, action)

    def _debounce_ok(self, side: int, action: str) -> bool:
        now = asyncio.get_running_loop().time()
        key = f"{side}:{action}"
        debounce = float((self.options.get(CONF_DEBOUNCE) or {}).get(action, 0) or 0)
        last = self._last_action_ts.get(key, 0.0)
        if now - last < debounce:
            return False
        self._last_action_ts[key] = now
        return True

    async def _run_media_action(self, side_conf: dict[str, Any], action: str, payload: dict[str, Any]) -> None:
        entity = side_conf.get(CONF_ENTITY)
        secondary = side_conf.get(CONF_SECONDARY_ENTITY)
        if not entity:
            return

        if action == "rotate_left":
            await self._call_service("media_player.volume_down", entity_id=entity)
        elif action == "rotate_right":
            await self._call_service("media_player.volume_up", entity_id=entity)
        elif action == "tap":
            muted = bool(self.hass.states.get(entity).attributes.get("is_volume_muted", False)) if self.hass.states.get(entity) else False
            await self._call_service("media_player.volume_mute", entity_id=entity, data={"is_volume_muted": not muted})
        elif action == "slide":
            await self._call_service("media_player.media_next_track", entity_id=entity)
        elif action == "shake":
            if secondary and secondary.startswith("script."):
                await self._call_service("script.turn_on", entity_id=secondary)
            else:
                await self._call_service("media_player.media_play_pause", entity_id=entity)
        elif action == "throw":
            await self._call_service("media_player.media_stop", entity_id=entity)

    async def _run_light_action(self, side_conf: dict[str, Any], action: str, payload: dict[str, Any]) -> None:
        entity = side_conf.get(CONF_ENTITY)
        secondary = side_conf.get(CONF_SECONDARY_ENTITY)
        if not entity:
            return

        if action == "rotate_left":
            await self._call_service("light.turn_on", entity_id=entity, data={"brightness_step_pct": -10})
        elif action == "rotate_right":
            await self._call_service("light.turn_on", entity_id=entity, data={"brightness_step_pct": 10})
        elif action == "tap":
            await self._call_service("light.toggle", entity_id=entity)
        elif action == "slide":
            if secondary and secondary.startswith("scene."):
                await self._call_service("scene.turn_on", entity_id=secondary)
        elif action == "shake":
            await self._call_service("light.turn_on", entity_id=entity, data={"brightness_pct": 100})
        elif action == "throw":
            await self._call_service("light.turn_off", entity_id=entity)

    async def _run_climate_action(self, side_conf: dict[str, Any], action: str, payload: dict[str, Any]) -> None:
        entity = side_conf.get(CONF_ENTITY)
        if not entity:
            return

        state = self.hass.states.get(entity)
        current_temp = None
        if state:
            current_temp = state.attributes.get("temperature") or state.attributes.get("target_temp")
        try:
            current_temp_float = float(current_temp)
        except (TypeError, ValueError):
            current_temp_float = 24.0

        if action == "rotate_left":
            await self._call_service("climate.set_temperature", entity_id=entity, data={"temperature": current_temp_float - 1})
        elif action == "rotate_right":
            await self._call_service("climate.set_temperature", entity_id=entity, data={"temperature": current_temp_float + 1})
        elif action in ("tap", "shake"):
            hvac_mode = "cool" if not state or state.state == "off" else "off"
            await self._call_service("climate.set_hvac_mode", entity_id=entity, data={"hvac_mode": hvac_mode})
        elif action == "throw":
            await self._call_service("climate.set_hvac_mode", entity_id=entity, data={"hvac_mode": "off"})

    async def _run_custom_action(self, raw: str) -> None:
        raw = raw.strip()
        if not raw:
            return
        try:
            action_obj = json.loads(raw)
        except json.JSONDecodeError as err:
            _LOGGER.warning("Invalid custom action JSON: %s", err)
            return

        if isinstance(action_obj, dict):
            await self._run_action_item(action_obj)
        elif isinstance(action_obj, list):
            for item in action_obj:
                if isinstance(item, dict):
                    await self._run_action_item(item)
        else:
            _LOGGER.warning("Custom action must be JSON object or array, got %s", type(action_obj).__name__)

    async def _run_action_item(self, item: dict[str, Any]) -> None:
        if "delay" in item:
            delay = item["delay"]
            seconds = 0.0
            if isinstance(delay, (int, float)):
                seconds = float(delay)
            elif isinstance(delay, dict):
                seconds = float(delay.get("seconds", 0) or 0)
                seconds += float(delay.get("milliseconds", 0) or 0) / 1000
            if seconds > 0:
                await asyncio.sleep(seconds)
            return

        service = item.get("service")
        if not service:
            return
        target = item.get("target") or {}
        data = item.get("data") or {}
        entity_id = target.get("entity_id") if isinstance(target, dict) else None
        await self._call_service(service, entity_id=entity_id, data=data)

    async def _call_service(
        self,
        service_name: str,
        entity_id: str | list[str] | None = None,
        data: dict[str, Any] | None = None,
    ) -> None:
        if "." not in service_name:
            _LOGGER.warning("Invalid service name: %s", service_name)
            return
        domain, service = service_name.split(".", 1)
        service_data = dict(data or {})
        if entity_id and "entity_id" not in service_data:
            service_data["entity_id"] = entity_id
        await self.hass.services.async_call(domain, service, service_data, blocking=False)

    def clear_history(self) -> None:
        self.history.clear()
        self.data["event_history"] = None
        self._notify()
