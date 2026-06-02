# Troubleshooting

## Tap does not work

Tap means two light taps with the cube on the table, not tapping the top with your finger.

## Slide does not work

Use a hard surface. Move slowly. Only 2–3 cm is enough.

## Rotate works randomly

Rotate slowly on a hard surface.

## Actions fire twice

Increase debounce in integration options.

## Existing automation fires together with integration

Mark that side as External in integration options.

## Integration does not see my cube

Check Zigbee2MQTT friendly_name and manually enter:

```text
zigbee2mqtt/<friendly_name>
```
