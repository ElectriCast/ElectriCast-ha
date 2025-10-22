"""Electricity Price Forecast integration for Home Assistant."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN
from .api import ElectricityForecastAPI

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BINARY_SENSOR]

SCAN_INTERVAL = timedelta(minutes=10)  # Update every 10 minutes


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Electricity Price Forecast from a config entry."""
    api_url = entry.data["api_url"]
    region_id = entry.data.get("region_id", "DE")

    session = async_get_clientsession(hass)
    api = ElectricityForecastAPI(api_url, session, region_id)

    async def async_update_data():
        """Fetch data from API."""
        try:
            _LOGGER.debug("Fetching data from API: %s", api_url)
            data = await api.async_get_all_data()
            _LOGGER.debug("Successfully fetched data for region %s", region_id)
            return data
        except Exception as err:
            _LOGGER.error("Error communicating with API %s: %s", api_url, err)
            raise UpdateFailed(f"Error communicating with API: {err}")

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=DOMAIN,
        update_method=async_update_data,
        update_interval=SCAN_INTERVAL,
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "api": api,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
