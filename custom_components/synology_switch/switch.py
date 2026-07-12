from wakeonlan import send_magic_packet
from homeassistant.components.switch import SwitchEntity
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD
from homeassistant.helpers.device_registry import DeviceInfo
from .const import DOMAIN, URL, MAC, SECURE, TIMEOUT, CONF_VERSION
import urllib
import requests
import time
import random
import string
import logging

_LOGGER = logging.getLogger(__name__)


class Synology:
    def __init__(self, url, mac, username, password, secure=False, timeout=5, version=6):
        self.url = url
        self.mac = mac
        self.username = username
        self.password = password
        self.secure = secure
        self.version = version
        self.timeout = timeout
        self.auth = {
            "sid": "",
            "time": 0,
            "timeout": 15 * 60
        }

    def is_logged_in(self):
        return self.auth["sid"] != "" and (self.auth["time"] + self.auth["timeout"] > time.time())

    def login(self):
        if self.is_logged_in():
            return True
        params = urllib.parse.urlencode({
            "api": "SYNO.API.Auth",
            "method": "login",
            "version": "3",
            "account": self.username,
            "passwd": self.password,
            "session": "homebridge-synology-" + "".join(random.sample(string.ascii_lowercase, 8)),
            "format": "sid"
        })
        sid = ""
        try:
            resp = requests.get(self.url + "/webapi/auth.cgi?" + params, verify=self.secure, timeout=self.timeout)
            sid = resp.json()["data"]["sid"]
            self.auth["time"] = int(time.time())
        except Exception as e:
            _LOGGER.error("Login failed: %s", e)
            sid = ""
        self.auth["sid"] = sid
        return sid != ""

    def shutdown(self):
        self.login()
        api_url = "/webapi/entry.cgi?" if self.version >= 6 else "/webapi/dsm/system.cgi?"
        params = urllib.parse.urlencode({
            "api": "SYNO.Core.System" if self.version >= 6 else "SYNO.DSM.System",
            "method": "shutdown",
            "version": "1",
            "_sid": self.auth["sid"]
        })
        try:
            resp = requests.get(self.url + api_url + params, verify=self.secure, timeout=self.timeout)
        except Exception as e:
            _LOGGER.error("Shutdown failed: %s", e)

    def get_power_state(self):
        try:
            resp = requests.get(self.url + "/webman/index.cgi", timeout=self.timeout, verify=self.secure)
            if resp and resp.status_code == 200:
                return True
            else:
                return False
        except Exception as e:
            _LOGGER.debug("Power state check failed: %s", e)
            return False

    def wake_up(self):
        send_magic_packet(self.mac)


class SynologySwitchEntity(SwitchEntity):
    _attr_should_poll = True

    def __init__(self, config_entry):
        self.config_entry = config_entry
        self.url = config_entry.data[URL]
        self.mac = config_entry.data[MAC]
        self.username = config_entry.data[CONF_USERNAME]
        self.password = config_entry.data[CONF_PASSWORD]
        self.secure = config_entry.data.get(SECURE, False)
        self.timeout = config_entry.data.get(TIMEOUT, 5)
        self.version = config_entry.data.get(CONF_VERSION, 7)
        self.synology = Synology(
            self.url, self.mac, self.username, self.password,
            self.secure, self.timeout, self.version
        )
        self._is_on = False
        mac_clean = self.mac.replace(":", "").replace("-", "")
        self._attr_unique_id = f"synology_{mac_clean}_power"
        self._attr_translation_key = "power"
        self._attr_has_entity_name = True
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, mac_clean)},
            name=f"Synology NAS ({self.mac[:17]})",
            manufacturer="Synology",
            model="DiskStation",
            configuration_url=self.url,
        )

    @property
    def available(self):
        return True

    @property
    def is_on(self):
        return self._is_on

    async def async_turn_on(self, **kwargs):
        await self.hass.async_add_executor_job(self.synology.wake_up)
        self._is_on = True

    async def async_turn_off(self, **kwargs):
        await self.hass.async_add_executor_job(self.synology.shutdown)
        self._is_on = False

    async def async_update(self):
        self._is_on = await self.hass.async_add_executor_job(self.synology.get_power_state)


async def async_setup_entry(hass, config_entry, async_add_entities):
    async_add_entities([SynologySwitchEntity(config_entry)], update_before_add=True)