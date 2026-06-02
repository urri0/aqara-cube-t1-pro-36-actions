# Custom actions

Custom action fields accept JSON object or JSON array.

Single service call:

```json
{"service":"light.toggle","target":{"entity_id":"light.room"}}
```

Sequence:

```json
[
  {"service":"script.turn_on","target":{"entity_id":"script.my_script"}},
  {"delay":{"seconds":5}},
  {"service":"media_player.turn_off","target":{"entity_id":"media_player.main_receiver"}}
]
```

Supported basic action items in v0.1.0:

```text
service
delay
```
