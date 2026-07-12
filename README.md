# SynologySwitch
Synology switch for Home Assistant. Control your Synology Diskstation with Home Assistant.

>supports DSM 5.x, 6.x and 7.x

## How to use

Install Home Assistant first.

### 1

Using [Home Assistant Community Store](https://hacs.xyz/)

OR

Copy all files from `custom_components/synology_switch/` to `homeassistant/custom_components/synology_switch/`

### 2

Go to **Settings > Devices & Services > Add Integration** and search for **Synology Switch**

### Configuration Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| url | Yes | - | DSM URL (e.g., https://192.168.1.2:5001) |
| mac | Yes | - | MAC Address for Wake-on-LAN |
| username | Yes | - | DSM username |
| password | Yes | - | DSM password |
| secure | No | False | Verify SSL certificate |
| timeout | No | 5 | Connection timeout in seconds |
| version | No | 7 | DSM version (5, 6, or 7) |

## Functions

- wake up (wake-on-lan has to be active) your diskstation
- shutdown your diskstation

### Two factor authentification (2FA)

This plugin does not support 2FA. If you have enabled 2FA, consider creating another account without 2FA.

## Issues

When you open an issue provide a detailed description of your problem.

## Support

PRs are always welcome.

## Thanks

[Homebridge-Synology](https://github.com/stfnhmplr/homebridge-synology)