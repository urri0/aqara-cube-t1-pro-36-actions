# Changelog

## [0.1.5-test] - 2026-06-04

### Fixed
- Reworked the Lovelace debug/training card to use single-entity mode.
- The card now reads all diagnostic data from attributes of the configured `*_last_action` sensor instead of relying on fragile sibling entity name guessing.
- Added full diagnostic attributes to the `last_action` sensor:
  - `active_side`
  - `last_side`
  - `last_from_side`
  - `last_angle`
  - `last_lqi`
  - `battery`
  - `voltage`
  - `operation_mode`
  - `event_count`
  - `last_event_time`
  - `event_history`

### Changed
- Backend MQTT/event handling is intentionally left unchanged because it was already working in v0.1.4-test.
- Diagnostic sibling sensors are still created for the Home Assistant device page, but the debug card no longer depends on them.
- Manifest/version bumped to `0.1.5-test`.

### Notes
- Recommended card YAML:

```yaml
type: custom:aqara-cube-36-debug-card
entity: sensor.cube36_aqara_cube_t1_pro_last_action
show_help: true
history_size: 5
```

- Current reliable frontend deployment method:
  copy `aqara-cube-36-debug-card.js` to `/config/www/`
  and add dashboard resource `/local/aqara-cube-36-debug-card.js` as JavaScript module.

---

## [0.1.4-test] - 2026-06-04

### Added
- First visually working test state of the integration.
- Lovelace debug/training card tested successfully through manual `/config/www` deployment.

### Fixed
- Integration setup/options no longer crashes with previous `config_entry` / `mappingproxy` errors.
- Options Flow became usable in Home Assistant 2026 / Python 3.14 test environment.

### Known issues
- Integration static path for Lovelace card did not work in the tested setup.
- Working fallback:
  copy `aqara-cube-36-debug-card.js` to `/config/www/`
  and add dashboard resource:
  `/local/aqara-cube-36-debug-card.js`

---

## [0.1.3-test] - 2026-06-04

### Fixed
- Fixed Options Flow crash caused by Home Assistant returning read-only `mappingproxy` options.
- Reworked internal options handling:
  - no direct `deepcopy(config_entry.options)`
  - options converted into normal mutable dictionaries
  - internal options variable renamed away from HA reserved/read-only properties

### Changed
- Continued work on safer diagnostic entity naming.
- Added stronger `cube36_` naming attempt for diagnostic entities.

---

## [0.1.2-test] - 2026-06-04

### Fixed
- Additional attempt to fix Options Flow crash.
- Removed Python `__pycache__` from generated test archive.
- Added `.gitignore`.

### Changed
- Attempted to force `cube36_` prefix into diagnostic entity names.

---

## [0.1.1-test] - 2026-06-04

### Fixed
- Fixed first Options Flow crash:
  `AttributeError: property 'config_entry' of 'AqaraCube36OptionsFlow' object has no setter`
- Reworked Options Flow to avoid writing to read-only `config_entry`.

### Changed
- Started moving diagnostic entity naming toward `cube36_` prefix.
- Added `.gitignore`.
- Removed generated Python cache files from the intended repository structure.

---

## [0.1.0-test] - 2026-06-04

### Added
- Initial public test version.
- UI-based Home Assistant custom integration skeleton.
- Zigbee2MQTT MQTT topic input.
- Aqara Cube T1 Pro event listener.
- Side model:
  - External
  - Managed
  - Disabled
- Core concept:
  `side = context`
  `action = command inside context`
- Initial profiles:
  - Media
  - Light
  - Climate
  - Custom
- Diagnostic sensors.
- Companion Lovelace debug/training card.
- English/Russian README.
- Initial documentation and examples.
- Local brand assets.
- HACS-ready repository structure.
