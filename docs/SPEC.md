# SPEC — Aqara Cube T1 Pro 36 Actions

## Core model

```text
side = context
action = command inside context
```

Supported action commands per side:

```text
rotate_left
rotate_right
tap
slide
shake
throw
```

`flip90` and `flip180` are context/side changes only, not primary commands.

## Supported hardware

Tested target: Aqara Cube T1 Pro via Zigbee2MQTT.

The older Aqara Cube is not supported/tested in v0.1.0.

## UI requirements

Integration must be configurable from Home Assistant UI:

- MQTT topic / cube name
- side mode: External / Managed / Disabled
- side profile: Media / Light / Climate / Custom
- main entity per side
- optional secondary entity/script
- custom JSON action per action
- diagnostics history size
- debounce per action

## Side modes

External: visible in diagnostics, no commands executed.
Managed: integration executes configured profile/custom actions.
Disabled: no commands executed.

## Profiles

Media, Light, Climate and Custom are included as v0.1.0 test profiles.

## Diagnostics

Create diagnostic sensors for last action, active side, angle, battery, voltage, LQI, mode, event counter, event time and history.

## Debug card

Ship a companion Lovelace card that displays live cube action feed and gesture training tips.
