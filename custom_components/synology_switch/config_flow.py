import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_USERNAME, CONF_PASSWORD
from .const import DOMAIN, URL, MAC, SECURE, TIMEOUT, CONF_VERSION

DATA_SCHEMA = vol.Schema({
    vol.Required(URL): str,
    vol.Required(MAC): str,
    vol.Required(CONF_USERNAME): str,
    vol.Required(CONF_PASSWORD): str,
    vol.Optional(SECURE, default=False): bool,
    vol.Optional(TIMEOUT, default=5): int,
    vol.Optional(CONF_VERSION, default=7): vol.All(int, vol.Clamp(min=5, max=7)),
})


class SynologySwitchConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            try:
                mac = user_input[MAC]
                if len(mac) == 12 or len(mac) == 17:
                    await self.async_set_unique_id(f"synology_{mac.replace(':', '').replace('-', '')}")
                    self._abort_if_unique_id_configured()
                    return self.async_create_entry(
                        title=f"Synology {mac[:17]}",
                        data=user_input,
                    )
                else:
                    errors[MAC] = "invalid_mac"
            except Exception:
                errors["base"] = "connection_error"

        return self.async_show_form(
            step_id="user",
            data_schema=DATA_SCHEMA,
            errors=errors,
        )