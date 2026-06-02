"""Config flow for Aqara Cube T1 Pro 36 Actions."""

from __future__ import annotations

from copy import deepcopy
import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    ACTIONS,
    CONF_ACTIONS,
    CONF_CUSTOM_OVERRIDES,
    CONF_DEBOUNCE,
    CONF_ENTITY,
    CONF_FRIENDLY_NAME,
    CONF_HISTORY_SIZE,
    CONF_MODE,
    CONF_MQTT_TOPIC,
    CONF_PROFILE,
    CONF_SECONDARY_ENTITY,
    CONF_SHOW_HELP,
    CONF_SIDES,
    DEFAULT_OPTIONS,
    DOMAIN,
    NAME,
    PROFILES,
    SIDE_MODES,
)

_LOGGER = logging.getLogger(__name__)


def _base_side_conf() -> dict[str, Any]:
    return {
        CONF_MODE: "disabled",
        CONF_PROFILE: "media",
        CONF_ENTITY: "",
        CONF_SECONDARY_ENTITY: "",
        CONF_CUSTOM_OVERRIDES: False,
        CONF_ACTIONS: {action: "" for action in ACTIONS},
    }


def _default_options(external_sides: list[int] | None = None) -> dict[str, Any]:
    options = deepcopy(DEFAULT_OPTIONS)
    external_sides = external_sides or []
    for side in range(1, 7):
        options[CONF_SIDES][str(side)] = _base_side_conf()
        if side in external_sides:
            options[CONF_SIDES][str(side)][CONF_MODE] = "external"
        else:
            options[CONF_SIDES][str(side)][CONF_MODE] = "disabled"
    return options


class AqaraCube36ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Create integration from UI."""
        errors: dict[str, str] = {}

        if user_input is not None:
            topic = user_input[CONF_MQTT_TOPIC].strip()
            friendly_name = user_input.get(CONF_FRIENDLY_NAME, NAME).strip() or NAME
            if not topic.startswith("zigbee2mqtt/"):
                errors[CONF_MQTT_TOPIC] = "topic_format"
            else:
                await self.async_set_unique_id(topic)
                self._abort_if_unique_id_configured()
                external_sides = [side for side in range(1, 7) if user_input.get(f"external_side_{side}")]
                options = _default_options(external_sides)
                data = {
                    CONF_MQTT_TOPIC: topic,
                    CONF_FRIENDLY_NAME: friendly_name,
                }
                return self.async_create_entry(title=friendly_name, data=data, options=options)

        schema = vol.Schema(
            {
                vol.Required(CONF_MQTT_TOPIC, default="zigbee2mqtt/Aqara Cube T1 Pro"): str,
                vol.Optional(CONF_FRIENDLY_NAME, default="Aqara Cube T1 Pro"): str,
                vol.Optional("external_side_1", default=False): bool,
                vol.Optional("external_side_2", default=False): bool,
                vol.Optional("external_side_3", default=False): bool,
                vol.Optional("external_side_4", default=False): bool,
                vol.Optional("external_side_5", default=False): bool,
                vol.Optional("external_side_6", default=False): bool,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
            description_placeholders={
                "hint": "Use your Zigbee2MQTT friendly_name, for example zigbee2mqtt/Living Room Cube. Mark sides already handled by external YAML/scripts.",
            },
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        return AqaraCube36OptionsFlow(config_entry)


class AqaraCube36OptionsFlow(config_entries.OptionsFlow):
    """Options flow."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry
        self.options = deepcopy(config_entry.options or _default_options())

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        """Options entry menu."""
        if user_input is not None:
            section = user_input["section"]
            if section == "diagnostics":
                return await self.async_step_diagnostics()
            if section == "mqtt":
                return await self.async_step_mqtt()
            if section.startswith("side_"):
                side = int(section.split("_")[1])
                return await self._async_step_side(side)
            if section == "save":
                return self.async_create_entry(title="", data=self.options)

        schema = vol.Schema(
            {
                vol.Required("section", default="side_1"): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[
                            {"value": "mqtt", "label": "MQTT topic / cube name"},
                            {"value": "side_1", "label": "Configure Side 1"},
                            {"value": "side_2", "label": "Configure Side 2"},
                            {"value": "side_3", "label": "Configure Side 3"},
                            {"value": "side_4", "label": "Configure Side 4"},
                            {"value": "side_5", "label": "Configure Side 5"},
                            {"value": "side_6", "label": "Configure Side 6"},
                            {"value": "diagnostics", "label": "Diagnostics / debounce"},
                            {"value": "save", "label": "Save and close"},
                        ],
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                )
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)

    async def async_step_mqtt(self, user_input: dict[str, Any] | None = None):
        """Update MQTT-ish displayed data. Real topic lives in config entry data, so re-create entry is safer for changing topic."""
        if user_input is not None:
            # Options cannot safely mutate config_entry.data. Store a requested topic override in options.
            # Runtime in v0.1.0 still uses config_entry.data; changing topic requires re-adding integration.
            self.options[CONF_MQTT_TOPIC] = user_input.get(CONF_MQTT_TOPIC, "").strip()
            self.options[CONF_FRIENDLY_NAME] = user_input.get(CONF_FRIENDLY_NAME, "").strip()
            return await self.async_step_init()

        schema = vol.Schema(
            {
                vol.Optional(CONF_MQTT_TOPIC, default=self.config_entry.data.get(CONF_MQTT_TOPIC, "")): str,
                vol.Optional(CONF_FRIENDLY_NAME, default=self.config_entry.data.get(CONF_FRIENDLY_NAME, self.config_entry.title)): str,
            }
        )
        return self.async_show_form(
            step_id="mqtt",
            data_schema=schema,
            description_placeholders={
                "note": "In v0.1.0 MQTT topic is primarily set at integration creation. If you renamed the cube, remove and add the integration again, or test topic override after reload."
            },
        )

    async def _async_step_side(self, side: int, user_input: dict[str, Any] | None = None):
        """Configure one side."""
        side_key = str(side)
        sides = self.options.setdefault(CONF_SIDES, {})
        conf = sides.setdefault(side_key, _base_side_conf())
        conf.setdefault(CONF_ACTIONS, {action: "" for action in ACTIONS})

        if user_input is not None:
            conf[CONF_MODE] = user_input[CONF_MODE]
            conf[CONF_PROFILE] = user_input[CONF_PROFILE]
            conf[CONF_ENTITY] = user_input.get(CONF_ENTITY, "").strip()
            conf[CONF_SECONDARY_ENTITY] = user_input.get(CONF_SECONDARY_ENTITY, "").strip()
            conf[CONF_CUSTOM_OVERRIDES] = bool(user_input.get(CONF_CUSTOM_OVERRIDES))
            actions = conf.setdefault(CONF_ACTIONS, {})
            for action in ACTIONS:
                actions[action] = user_input.get(f"custom_{action}", "").strip()
            return await self.async_step_init()

        schema_dict: dict[Any, Any] = {
            vol.Required(CONF_MODE, default=conf.get(CONF_MODE, "disabled")): selector.SelectSelector(
                selector.SelectSelectorConfig(options=SIDE_MODES, mode=selector.SelectSelectorMode.DROPDOWN)
            ),
            vol.Required(CONF_PROFILE, default=conf.get(CONF_PROFILE, "media")): selector.SelectSelector(
                selector.SelectSelectorConfig(options=PROFILES, mode=selector.SelectSelectorMode.DROPDOWN)
            ),
            vol.Optional(CONF_ENTITY, default=conf.get(CONF_ENTITY, "")): str,
            vol.Optional(CONF_SECONDARY_ENTITY, default=conf.get(CONF_SECONDARY_ENTITY, "")): str,
            vol.Optional(CONF_CUSTOM_OVERRIDES, default=bool(conf.get(CONF_CUSTOM_OVERRIDES))): bool,
        }
        actions = conf.get(CONF_ACTIONS, {})
        for action in ACTIONS:
            schema_dict[vol.Optional(f"custom_{action}", default=actions.get(action, ""))] = selector.TextSelector(
                selector.TextSelectorConfig(multiline=True)
            )

        return self.async_show_form(
            step_id=f"side_{side}",
            data_schema=vol.Schema(schema_dict),
            description_placeholders={
                "side": str(side),
                "custom_help": "Custom fields accept JSON object or array, for example: {\"service\":\"light.toggle\",\"target\":{\"entity_id\":\"light.room\"}}",
            },
        )

    async def async_step_side_1(self, user_input: dict[str, Any] | None = None):
        return await self._async_step_side(1, user_input)

    async def async_step_side_2(self, user_input: dict[str, Any] | None = None):
        return await self._async_step_side(2, user_input)

    async def async_step_side_3(self, user_input: dict[str, Any] | None = None):
        return await self._async_step_side(3, user_input)

    async def async_step_side_4(self, user_input: dict[str, Any] | None = None):
        return await self._async_step_side(4, user_input)

    async def async_step_side_5(self, user_input: dict[str, Any] | None = None):
        return await self._async_step_side(5, user_input)

    async def async_step_side_6(self, user_input: dict[str, Any] | None = None):
        return await self._async_step_side(6, user_input)

    async def async_step_diagnostics(self, user_input: dict[str, Any] | None = None):
        """Configure diagnostics."""
        debounce = self.options.setdefault(CONF_DEBOUNCE, {})

        if user_input is not None:
            self.options[CONF_HISTORY_SIZE] = int(user_input[CONF_HISTORY_SIZE])
            self.options[CONF_SHOW_HELP] = bool(user_input.get(CONF_SHOW_HELP))
            for action in [*ACTIONS, "flip90", "flip180"]:
                debounce[action] = float(user_input.get(f"debounce_{action}", debounce.get(action, 0)))
            return await self.async_step_init()

        schema_dict: dict[Any, Any] = {
            vol.Required(CONF_HISTORY_SIZE, default=int(self.options.get(CONF_HISTORY_SIZE, 10))): selector.NumberSelector(
                selector.NumberSelectorConfig(min=5, max=50, step=5, mode=selector.NumberSelectorMode.BOX)
            ),
            vol.Optional(CONF_SHOW_HELP, default=bool(self.options.get(CONF_SHOW_HELP, True))): bool,
        }
        for action in [*ACTIONS, "flip90", "flip180"]:
            schema_dict[vol.Optional(f"debounce_{action}", default=float(debounce.get(action, 0)))] = selector.NumberSelector(
                selector.NumberSelectorConfig(min=0, max=10, step=0.1, mode=selector.NumberSelectorMode.BOX)
            )

        return self.async_show_form(step_id="diagnostics", data_schema=vol.Schema(schema_dict))
