import re
import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD
from .const import DOMAIN, URL, MAC, SECURE, TIMEOUT, CONF_VERSION

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema({
    vol.Required(URL): str,
    vol.Required(MAC): str,
    vol.Required(CONF_USERNAME): str,
    vol.Required(CONF_PASSWORD): str,
    vol.Optional(SECURE, default=False): bool,
    vol.Optional(TIMEOUT, default=5): int,
    vol.Required(CONF_VERSION): vol.In([5, 6, 7]),
})

MAC_REGEX = re.compile(r'^([0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}$|^[0-9A-Fa-f]{12}$')


class SynologySwitchConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            try:
                mac = user_input[MAC]
                if MAC_REGEX.match(mac):
                    await self.async_set_unique_id(f"synology_{mac.replace(':', '').replace('-', '')}")
                    self._abort_if_unique_id_configured()
                    return self.async_create_entry(
                        title=f"Synology {mac[:17]}",
                        data=user_input,
                    )
                else:
                    errors[MAC] = "invalid_mac"
            except config_entries.AlreadyConfigured:
                errors["base"] = "already_configured"
            except Exception as e:
                _LOGGER.error("Config flow error: %s", e)
                errors["base"] = "unknown_error"

        return self.async_show_form(
            step_id="user",
            data_schema=DATA_SCHEMA,
            errors=errors,
        )