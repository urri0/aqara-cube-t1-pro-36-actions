"""Aqara Cube T1 Pro 36 Actions integration."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall

from .const import CONF_FRIENDLY_NAME, CONF_MQTT_TOPIC, DOMAIN, NAME
from .runtime import CubeRuntime

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


def _runtime_store(hass: HomeAssistant) -> dict[str, CubeRuntime]:
    hass.data.setdefault(DOMAIN, {})
    return hass.data[DOMAIN]


async def async_setup(hass: HomeAssistant, config: dict[str, Any]) -> bool:
    """Set up integration and static card path."""
    await _async_register_frontend_path(hass)

    async def _clear_history(call: ServiceCall) -> None:
        entry_id = call.data.get("entry_id")
        runtimes = _runtime_store(hass)
        if entry_id:
            runtime = runtimes.get(entry_id)
            if runtime:
                runtime.clear_history()
            return
        for runtime in runtimes.values():
            runtime.clear_history()

    async def _test_action(call: ServiceCall) -> None:
        entry_id = call.data.get("entry_id")
        runtime = _runtime_store(hass).get(entry_id)
        if not runtime:
            _LOGGER.warning("No Aqara Cube 36 runtime for entry_id=%s", entry_id)
            return
        payload = {
            "action": call.data.get("action"),
            "side": call.data.get("side"),
            "action_angle": call.data.get("angle", 0),
            "operation_mode": "test_action",
        }
        await runtime.async_handle_payload(payload)

    hass.services.async_register(DOMAIN, "clear_history", _clear_history)
    hass.services.async_register(DOMAIN, "test_action", _test_action)
    return True


async def _async_register_frontend_path(hass: HomeAssistant) -> None:
    """Register static path for the optional Lovelace debug card."""
    try:
        from homeassistant.components.http import StaticPathConfig, async_register_static_paths

        www_path = Path(__file__).parent / "www"
        await async_register_static_paths(
            hass,
            [
                StaticPathConfig(
                    url_path="/aqara_cube_t1_pro_36_actions",
                    path=str(www_path),
                    cache_headers=False,
                )
            ],
        )
    except Exception as err:  # noqa: BLE001
        _LOGGER.debug("Could not register Aqara Cube 36 frontend static path: %s", err)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up a config entry."""
    await _async_register_frontend_path(hass)

    topic = entry.data[CONF_MQTT_TOPIC]
    name = entry.data.get(CONF_FRIENDLY_NAME) or entry.title or NAME
    runtime = CubeRuntime(hass, entry.entry_id, name, topic, entry.options)
    _runtime_store(hass)[entry.entry_id] = runtime

    await runtime.async_start()
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload entry on options update."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    runtime = _runtime_store(hass).pop(entry.entry_id, None)
    if runtime:
        await runtime.async_stop()
    return unload_ok
