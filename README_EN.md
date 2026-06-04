# Aqara Cube T1 Pro 36 Actions

**UI-based Home Assistant integration for Aqara Cube T1 Pro via Zigbee2MQTT.**

Turn the cube from a strange gesture toy into a practical 6-side physical controller:

```text
side = context
action = command inside that context
```

6 sides × 6 actions = up to **36 customizable contextual commands**.

- English: this file, first section
- Русский: [README_RU.md](README_RU.md) or the Russian section below

---

## Why this integration exists

Aqara Cube T1 Pro is usually presented as a small smart-home gadget with several gestures. In real use it can be much more useful, but only if it is configured around how the device actually behaves.

The important idea is simple:

```text
A cube side is not just a number.
A cube side is a mode/context.
A gesture is an action inside that context.
```

Instead of trying to use `flip90` or `flip180` as primary commands, this integration treats flipping as selecting the active side. Real commands are then performed with stable gestures:

```text
rotate_left
rotate_right
tap
slide
shake
throw
```

That gives a clean mental model:

```text
Side 1 = Media
Side 2 = Lights
Side 3 = Climate
Side 4 = Custom
Side 5 = Custom
Side 6 = Custom
```

The goal is not to force everyone into one hardcoded YAML automation. The goal is to provide a fully UI-driven controller where a normal user can choose profiles, and an advanced user can override every action manually.

---

## What problem it solves

Without diagnostics, Aqara Cube T1 Pro can feel unreliable:

- “tap does not work”
- “slide does not work”
- “shake and throw are confusing”
- “rotate works only sometimes”
- “soft surfaces make everything strange”

In practice, many of these are not hardware problems. They are usage and feedback problems. The cube needs the right surface, the right gesture speed, and a clear way to see what action was actually detected.

This integration includes a **Debug / Training Lovelace card** so the user can see live events from the cube:

```text
ACTION
SIDE / FROM → TO
ANGLE
LQI / BATTERY / VOLTAGE
OPERATION MODE
EVENT COUNT
LAST EVENT TIME
HISTORY
```

The card is not just decorative. It is a training tool. It helps the user learn the cube in a few minutes instead of guessing blindly.

---

## Main concept

```text
side = context
action = command inside that context
```

6 sides:

```text
Side 1
Side 2
Side 3
Side 4
Side 5
Side 6
```

6 actions per side:

```text
rotate_left
rotate_right
tap
slide
shake
throw
```

Result:

```text
6 sides × 6 actions = 36 contextual actions
```

`flip90` and `flip180` are treated as side/context changes, not as primary automation commands.

---

## Features

- UI-based setup through Home Assistant config flow
- Works via Zigbee2MQTT MQTT topic
- No mandatory YAML for normal use
- Per-side mode:
  - **External** — already handled by your own YAML/scripts
  - **Managed** — controlled by this integration
  - **Disabled** — not used
- Built-in profiles:
  - **Media**
  - **Light**
  - **Climate**
  - **Custom**
- Custom action mapping per side/action
- Custom override on top of ready-made profiles
- Diagnostic sensors
- Event history
- Companion Lovelace debug/training card
- Multi-cube-ready architecture
- Local brand assets
- AI-assisted documentation and code

---

## Gesture training tips

Use a hard surface.

```text
shake  = sharp up/down shake
throw  = short sharp downward jerk in hand
slide  = slow short slide on a hard surface, only 2–3 cm
rotate = slow rotation on a hard surface
tap    = two light taps with the cube on the table
```

Soft surfaces like beds, sofas and carpets make `slide`, `tap` and `rotate` unreliable.

Important notes:

```text
slide does not need 10–15 cm movement; 2–3 cm is enough.
tap is not a finger tap on top of the cube; tap means two light taps with the cube on the table.
rotate should be slow and controlled, not fast spinning.
shake and throw should be sharp gestures, but they are not the same movement.
```

---

## Supported device

Designed and tested for:

```text
Aqara Cube T1 Pro
Zigbee2MQTT
```

The older Aqara Cube is not supported/tested yet.

The MQTT topic is not hardcoded. Use your actual Zigbee2MQTT friendly name:

```text
zigbee2mqtt/<friendly_name>
```

Examples:

```text
zigbee2mqtt/Aqara Cube T1 Pro
zigbee2mqtt/Living Room Cube
zigbee2mqtt/Balcony Cube
```

---

## Side modes

Each side can be configured independently.

```text
External = already handled outside this integration
Managed  = controlled by this integration
Disabled = not used
```

### External

Use this when you already have your own automation for a cube side.

External sides are still visible in diagnostics, but the integration will **not run actions** for them. This prevents double-fire when an existing YAML/script already handles a side.

### Managed

The integration handles the side using the selected profile and action mapping.

### Disabled

The side is ignored for actions but can still be visible in diagnostics.

---

## Profiles

### Media

```text
rotate_left  = volume down
rotate_right = volume up
tap          = mute / unmute
slide        = next track
shake        = play/pause or optional script
throw        = stop/off
```

### Light

```text
rotate_left  = brightness down
rotate_right = brightness up
tap          = toggle
slide        = optional scene
shake        = favorite/full brightness
throw        = off
```

### Climate

```text
rotate_left  = temperature down
rotate_right = temperature up
tap          = mode/power toggle
slide        = preset/fan mode
shake        = power toggle
throw        = off
```

### Custom

Every action can run a custom JSON action from UI.

Single action example:

```json
{"service":"light.toggle","target":{"entity_id":"light.room"}}
```

Multi-action sequence example:

```json
[
  {"service":"script.turn_on","target":{"entity_id":"script.my_script"}},
  {"delay":{"seconds":5}},
  {"service":"media_player.turn_off","target":{"entity_id":"media_player.main_receiver"}}
]
```

---

## Debug / Training card

The integration includes a companion Lovelace card:

```yaml
type: custom:aqara-cube-36-debug-card
entity: sensor.<your_cube>_last_action
show_help: true
history_size: 5
```

Resource URL after integration setup:

```text
/aqara_cube_t1_pro_36_actions/aqara-cube-36-debug-card.js
```

If Home Assistant does not auto-list the card, add the resource manually:

```text
Settings → Dashboards → Resources → Add Resource
URL: /aqara_cube_t1_pro_36_actions/aqara-cube-36-debug-card.js
Type: JavaScript module
```

The card shows:

```text
ACTION
SIDE / FROM → TO
ANGLE
LQI / BATTERY / VOLTAGE
OPERATION MODE
EVENT COUNT
LAST EVENT TIME
HISTORY
```

Use this card to train your gestures and understand how the cube reacts to different surfaces and movement speeds.

---

## Installation

### Manual install for testing

Copy this folder into Home Assistant:

```text
custom_components/aqara_cube_t1_pro_36_actions
```

Final path:

```text
/config/custom_components/aqara_cube_t1_pro_36_actions/
```

Restart Home Assistant.

### Add integration

Go to:

```text
Settings → Devices & services → Add integration → Aqara Cube T1 Pro 36 Actions
```

Enter your Zigbee2MQTT topic:

```text
zigbee2mqtt/<your_cube_friendly_name>
```

---

## Field-tested media scenario

The advanced media behavior was field-tested with generic classes of equipment:

```text
- a Roon Tested integrated amplifier / network receiver
- Roon playback through an AirPlay-like receiver input
- a voice assistant / music service routed to the receiver
- a protected TV Audio / ARC receiver input
```

Observed source mapping in the tested setup:

```text
URL Stream     = music service routed to receiver
AirPlay        = Roon / network music player input
TV Audio / ARC = protected non-music receiver mode
```

Other receivers, music services and routing setups may work, but need community testing.

Do not treat this as official support or certification by Aqara, Roon, receiver manufacturers or any music service.

---

## Project status

Version: **0.1.0 test build**

This is an early test release for live Home Assistant testing.

---

## AI-assisted disclosure

AI-assisted project.

The integration code, documentation and examples are developed with AI assistance.

Architecture, testing, validation and real-world UX decisions are based on actual Aqara Cube T1 Pro usage by the repository owner.

This project exists because real-world behavior of the cube is often different from short reviews and marketing descriptions.

---

## Disclaimer

This project is not affiliated with Aqara.

Aqara Cube T1 Pro is a product name/trademark of its owner.

This is a community Home Assistant custom integration.

---

## License

MIT License.


## v0.1.6-test note

The Lovelace debug/training card is now single-entity based. Use the `*_last_action` sensor as the only configured entity; the card reads side, angle, radio, battery and history from its attributes.

Recommended card YAML:

```yaml
type: custom:aqara-cube-36-debug-card
entity: sensor.cube36_aqara_cube_t1_pro_last_action
show_help: true
history_size: 5
```

If the integration static card path does not load, copy `aqara-cube-36-debug-card.js` to `/config/www/` and add `/local/aqara-cube-36-debug-card.js` as a JavaScript module dashboard resource.
