# Installation

## Manual test install

Copy:

```text
custom_components/aqara_cube_t1_pro_36_actions
```

to your Home Assistant `/config/custom_components/` folder.

Restart Home Assistant.

Add the integration from UI:

```text
Settings → Devices & services → Add integration → Aqara Cube T1 Pro 36 Actions
```

## Lovelace card resource

Resource URL:

```text
/aqara_cube_t1_pro_36_actions/aqara-cube-36-debug-card.js
```

If the card is not available in the card picker, add the resource manually as JavaScript module.
