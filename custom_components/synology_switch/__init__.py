from .const import DOMAIN

async def async_setup(hass, config):
    if DOMAIN not in config:
        return True
    return True

async def async_setup_entry(hass, entry):
    await hass.config_entries.async_forward_entry_setups(entry, ["switch"])
    return True

async def async_unload_entry(hass, entry):
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["switch"])
    return unload_ok

async def async_reload_entry(hass, entry):
    await hass.config_entries.async_reload(entry.entry_id)