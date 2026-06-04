# Changelog

## v0.1.1-test

### Fixed
- Fixed Home Assistant options flow crash: `AttributeError: property config_entry has no setter`.
- Added safe diagnostic entity naming with `cube36_` prefix to avoid collisions with existing user helpers/entities.
- Added `.gitignore` for Python cache and local Home Assistant runtime files.

## 0.1.0-test

- Initial test build.
- UI config flow.
- Per-side External / Managed / Disabled modes.
- Media, Light, Climate and Custom profiles.
- Diagnostic sensors.
- MQTT action listener for Aqara Cube T1 Pro via Zigbee2MQTT.
- Companion Lovelace debug/training card.
- Local brand assets.
- Polished bilingual README: English and Russian project description, purpose, gesture training and tested scenarios.
