import re
import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD
from homeassistant.core import callback
from .const import DOMAIN, URL, MAC, SECURE, TIMEOUT, CONF_VERSION

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema({
    vol.Required(URL): str,
    vol.Required(MAC): str,
    vol.Required(CONF_USERNAME): str,
    vol.Required(CONF_PASSWORD): str,
    vol.Optional(SECURE, default=False): bool,
    vol.Optional(TIMEOUT, default=5): int,
    vol.Required(CONF_VERSION): vol.All(vol.Coerce(int), vol.In([5, 6, 7])),
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

    async def async_step_reconfigure(self, user_input=None):
        errors = {}
        if user_input is not None:
            try:
                mac = user_input[MAC]
                if MAC_REGEX.match(mac):
                    return self.async_update_reload_and_abort(
                        self.config_entry,
                        data=user_input,
                    )
                else:
                    errors[MAC] = "invalid_mac"
            except Exception as e:
                _LOGGER.error("Reconfigure flow error: %s", e)
                errors["base"] = "unknown_error"

        current_data = self.config_entry.data
        data_schema = vol.Schema({
            vol.Required(URL, default=current_data.get(URL)): str,
            vol.Required(MAC, default=current_data.get(MAC)): str,
            vol.Required(CONF_USERNAME, default=current_data.get(CONF_USERNAME)): str,
            vol.Required(CONF_PASSWORD, default=current_data.get(CONF_PASSWORD)): str,
            vol.Optional(SECURE, default=current_data.get(SECURE, False)): bool,
            vol.Optional(TIMEOUT, default=current_data.get(TIMEOUT, 5)): int,
            vol.Required(CONF_VERSION, default=current_data.get(CONF_VERSION, 7)): vol.All(vol.Coerce(int), vol.In([5, 6, 7])),
        })

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=data_schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return SynologySwitchOptionsFlow()


class SynologySwitchOptionsFlow(config_entries.OptionsFlow):
    async def async_step_init(self, user_input=None):
        errors = {}
        if user_input is not None:
            try:
                mac = user_input[MAC]
                if MAC_REGEX.match(mac):
                    self.hass.config_entries.async_update_entry(
                        self.config_entry,
                        data=user_input,
                    )
                    await self.hass.config_entries.async_reload(self.config_entry.entry_id)
                    return self.async_create_entry(title="", data={})
                else:
                    errors[MAC] = "invalid_mac"
            except Exception as e:
                _LOGGER.error("Options flow error: %s", e)
                errors["base"] = "unknown_error"

        current_data = self.config_entry.data
        options_schema = vol.Schema({
            vol.Required(URL, default=current_data.get(URL)): str,
            vol.Required(MAC, default=current_data.get(MAC)): str,
            vol.Required(CONF_USERNAME, default=current_data.get(CONF_USERNAME)): str,
            vol.Required(CONF_PASSWORD, default=current_data.get(CONF_PASSWORD)): str,
            vol.Optional(SECURE, default=current_data.get(SECURE, False)): bool,
            vol.Optional(TIMEOUT, default=current_data.get(TIMEOUT, 5)): int,
            vol.Required(CONF_VERSION, default=current_data.get(CONF_VERSION, 7)): vol.All(vol.Coerce(int), vol.In([5, 6, 7])),
        })

        return self.async_show_form(
            step_id="init",
            data_schema=options_schema,
            errors=errors,
        )
