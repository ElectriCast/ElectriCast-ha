"""Config flow for Electricity Price Forecast integration."""
from __future__ import annotations

import logging
from typing import Any
from urllib.parse import urlparse

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_URL
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import CONF_API_URL, CONF_REGION_ID, DEFAULT_API_URL, DEFAULT_REGION_ID, DOMAIN, REGIONS

_LOGGER = logging.getLogger(__name__)


def validate_url(url: str) -> bool:
    """Validate URL format."""
    try:
        result = urlparse(url)
        return all([result.scheme in ["http", "https"], result.netloc])
    except Exception:
        return False


async def validate_api(hass: HomeAssistant, api_url: str, region_id: str) -> dict[str, Any]:
    """Validate the API connection."""
    session = async_get_clientsession(hass)

    try:
        # Test health endpoint
        async with session.get(f"{api_url}/health", timeout=10) as response:
            if response.status != 200:
                raise Exception("API health check failed")

        # Test predictions endpoint
        async with session.get(
            f"{api_url}/api/predictions/{region_id}/next-24h", timeout=10
        ) as response:
            if response.status != 200:
                raise Exception(f"Cannot fetch predictions for region {region_id}")
            data = await response.json()
            if not data:
                raise Exception("No prediction data available")

        return {"title": f"Electricity Forecast ({region_id})"}

    except aiohttp.ClientError as err:
        _LOGGER.error("Error connecting to API: %s", err)
        raise Exception("Cannot connect to API") from err
    except Exception as err:
        _LOGGER.error("Unexpected error: %s", err)
        raise


class ElectricityForecastConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Electricity Price Forecast."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Validate URL format
            api_url = user_input[CONF_API_URL].rstrip("/")
            if not validate_url(api_url):
                errors["base"] = "invalid_url"
            else:
                try:
                    info = await validate_api(
                        self.hass,
                        api_url,
                        user_input[CONF_REGION_ID],
                    )

                    # Create unique ID based on API URL and region
                    await self.async_set_unique_id(
                        f"{api_url}_{user_input[CONF_REGION_ID]}"
                    )
                    self._abort_if_unique_id_configured()

                    # Store normalized URL (without trailing slash)
                    user_input[CONF_API_URL] = api_url

                    return self.async_create_entry(
                        title=info["title"],
                        data=user_input,
                    )
                except Exception as err:
                    _LOGGER.error("Error validating API: %s", err)
                    errors["base"] = "cannot_connect"

        # Show configuration form
        data_schema = vol.Schema(
            {
                vol.Required(CONF_API_URL, default=DEFAULT_API_URL): str,
                vol.Required(CONF_REGION_ID, default=DEFAULT_REGION_ID): vol.In(REGIONS),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> ElectricityForecastOptionsFlow:
        """Get the options flow for this handler."""
        return ElectricityForecastOptionsFlow(config_entry)


class ElectricityForecastOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Electricity Price Forecast."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Validate URL format
            api_url = user_input[CONF_API_URL].rstrip("/")
            if not validate_url(api_url):
                errors["base"] = "invalid_url"
            else:
                try:
                    await validate_api(
                        self.hass,
                        api_url,
                        user_input[CONF_REGION_ID],
                    )

                    # Store normalized URL (without trailing slash)
                    user_input[CONF_API_URL] = api_url

                    # Update config entry data with new values
                    self.hass.config_entries.async_update_entry(
                        self.config_entry,
                        data=user_input,
                    )

                    # Reload the integration to apply new settings
                    await self.hass.config_entries.async_reload(self.config_entry.entry_id)

                    return self.async_create_entry(title="", data={})

                except Exception as err:
                    _LOGGER.error("Error validating API: %s", err)
                    errors["base"] = "cannot_connect"

        # Get current values
        current_api_url = self.config_entry.data.get(CONF_API_URL, DEFAULT_API_URL)
        current_region = self.config_entry.data.get(CONF_REGION_ID, DEFAULT_REGION_ID)

        data_schema = vol.Schema(
            {
                vol.Required(CONF_API_URL, default=current_api_url): str,
                vol.Required(CONF_REGION_ID, default=current_region): vol.In(REGIONS),
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=data_schema,
            errors=errors,
        )
