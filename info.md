# Aqara Cube T1 Pro 36 Actions

UI-based Home Assistant integration for Aqara Cube T1 Pro via Zigbee2MQTT.

Turns the cube into a practical 6-side contextual controller:

```text
side = context
action = command inside that context
```

6 sides × 6 actions = up to 36 customizable commands.

Includes diagnostic/training Lovelace card to help users learn real cube gestures: shake, throw, slide, rotate and tap.

Русский: интеграция превращает Aqara Cube T1 Pro в понятный 6-сторонний контроллер для Home Assistant. Сторона выбирает контекст, жест выполняет команду внутри контекста.


Current test line: v0.1.6-test. Debug card is single-entity based and reads diagnostics from the last_action sensor attributes.
