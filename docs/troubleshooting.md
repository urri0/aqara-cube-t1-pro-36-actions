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


## Debug card shows #0 while backend sensors update

Use v0.1.5-test or later. The card must be configured with the `*_last_action` sensor and reads all data from its attributes.

```yaml
type: custom:aqara-cube-36-debug-card
entity: sensor.cube36_aqara_cube_t1_pro_last_action
show_help: true
history_size: 5
```
