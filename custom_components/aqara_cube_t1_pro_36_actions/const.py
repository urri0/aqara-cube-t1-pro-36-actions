"""Constants for Aqara Cube T1 Pro 36 Actions."""

from __future__ import annotations

DOMAIN = "aqara_cube_t1_pro_36_actions"
NAME = "Aqara Cube T1 Pro 36 Actions"
VERSION = "0.1.4-test"

CONF_MQTT_TOPIC = "mqtt_topic"
CONF_FRIENDLY_NAME = "friendly_name"
CONF_HISTORY_SIZE = "history_size"
CONF_SIDES = "sides"
CONF_MODE = "mode"
CONF_PROFILE = "profile"
CONF_ENTITY = "entity"
CONF_SECONDARY_ENTITY = "secondary_entity"
CONF_CUSTOM_OVERRIDES = "custom_overrides"
CONF_ACTIONS = "actions"
CONF_DEBOUNCE = "debounce"
CONF_SHOW_HELP = "show_help"

SIDE_MODES = ["external", "managed", "disabled"]
PROFILES = ["media", "light", "climate", "custom"]
ACTIONS = ["rotate_left", "rotate_right", "tap", "slide", "shake", "throw"]
FLIP_ACTIONS = ["flip90", "flip180"]

DEFAULT_HISTORY_SIZE = 10
DEFAULT_DEBOUNCE = {
    "rotate_left": 0.2,
    "rotate_right": 0.2,
    "tap": 0.5,
    "slide": 0.8,
    "shake": 1.5,
    "throw": 3.0,
    "flip90": 0.5,
    "flip180": 0.5,
}

DEFAULT_OPTIONS = {
    CONF_HISTORY_SIZE: DEFAULT_HISTORY_SIZE,
    CONF_SHOW_HELP: True,
    CONF_DEBOUNCE: DEFAULT_DEBOUNCE,
    CONF_SIDES: {
        str(i): {
            CONF_MODE: "disabled",
            CONF_PROFILE: "media",
            CONF_ENTITY: "",
            CONF_SECONDARY_ENTITY: "",
            CONF_CUSTOM_OVERRIDES: False,
            CONF_ACTIONS: {action: "" for action in ACTIONS},
        }
        for i in range(1, 7)
    },
}

SENSOR_TYPES = {
    "last_action": {"name": "Last Action", "icon": "mdi:gesture-tap"},
    "active_side": {"name": "Active Side", "icon": "mdi:cube-outline"},
    "last_side": {"name": "Last Side", "icon": "mdi:cube-send"},
    "last_from_side": {"name": "Last From Side", "icon": "mdi:cube-scan"},
    "last_angle": {"name": "Last Angle", "icon": "mdi:angle-acute", "unit": "°"},
    "last_lqi": {"name": "LQI", "icon": "mdi:signal", "unit": "LQI"},
    "battery": {"name": "Battery", "icon": "mdi:battery", "unit": "%"},
    "voltage": {"name": "Voltage", "icon": "mdi:sine-wave", "unit": "mV"},
    "operation_mode": {"name": "Operation Mode", "icon": "mdi:cog-outline"},
    "event_count": {"name": "Event Count", "icon": "mdi:counter"},
    "last_event_time": {"name": "Last Event Time", "icon": "mdi:clock-outline"},
    "event_history": {"name": "Event History", "icon": "mdi:history"},
}
