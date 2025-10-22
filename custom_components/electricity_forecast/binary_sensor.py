"""Binary sensor platform for Electricity Price Forecast."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the binary sensor platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    api = hass.data[DOMAIN][config_entry.entry_id]["api"]

    binary_sensors = [
        IsCheapNowBinarySensor(coordinator, api),
        IsExpensiveNowBinarySensor(coordinator, api),
        IsInCheapest3HoursBinarySensor(coordinator, api),
        IsInCheapest6HoursBinarySensor(coordinator, api),
        IsBelowAverageBinarySensor(coordinator, api),
        TomorrowCheaperBinarySensor(coordinator, api),
    ]

    async_add_entities(binary_sensors)


class ElectricityPriceBinarySensorBase(CoordinatorEntity, BinarySensorEntity):
    """Base class for Electricity Price binary sensors."""

    def __init__(self, coordinator, api):
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self.api = api
        self._attr_has_entity_name = True

    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self.api.region_id)},
            "name": f"Electricity Forecast {self.api.region_id}",
            "manufacturer": "Electricity Price Forecast",
            "model": f"Region {self.api.region_id}",
        }


class IsCheapNowBinarySensor(ElectricityPriceBinarySensorBase):
    """Binary sensor for whether current price is cheap (bottom 25%)."""

    _attr_name = "Is Cheap Now"
    _attr_icon = "mdi:cash-check"

    @property
    def unique_id(self):
        """Return unique ID."""
        return f"{self.api.region_id}_is_cheap_now"

    @property
    def is_on(self):
        """Return true if current price is in cheapest 25%."""
        if not self.coordinator.data:
            return False

        current = self.coordinator.data.get("current_price")
        predictions = self.coordinator.data.get("predictions_24h", [])

        if not current or not predictions:
            return False

        now = datetime.now()
        today_end = now.replace(hour=23, minute=59, second=59)
        today_prices = [
            p["predicted_price"] for p in predictions
            if now <= datetime.fromisoformat(p["timestamp"].replace("Z", "+00:00")) <= today_end
        ]

        if not today_prices:
            return False

        current_price = current["price"]
        min_price = min(today_prices)
        max_price = max(today_prices)
        cheap_threshold = min_price + (max_price - min_price) * 0.25

        return current_price <= cheap_threshold

    @property
    def extra_state_attributes(self):
        """Return additional attributes."""
        if not self.coordinator.data:
            return {}

        current = self.coordinator.data.get("current_price")
        predictions = self.coordinator.data.get("predictions_24h", [])

        if not current or not predictions:
            return {}

        now = datetime.now()
        today_end = now.replace(hour=23, minute=59, second=59)
        today_prices = [
            p["predicted_price"] for p in predictions
            if now <= datetime.fromisoformat(p["timestamp"].replace("Z", "+00:00")) <= today_end
        ]

        if today_prices:
            current_price = current["price"]
            min_price = min(today_prices)
            max_price = max(today_prices)
            cheap_threshold = min_price + (max_price - min_price) * 0.25

            return {
                "current_price": round(current_price / 1000, 5),
                "cheap_threshold": round(cheap_threshold / 1000, 5),
                "min_price_today": round(min_price / 1000, 5),
                "max_price_today": round(max_price / 1000, 5),
            }
        return {}


class IsExpensiveNowBinarySensor(ElectricityPriceBinarySensorBase):
    """Binary sensor for whether current price is expensive (top 25%)."""

    _attr_name = "Is Expensive Now"
    _attr_icon = "mdi:cash-remove"

    @property
    def unique_id(self):
        """Return unique ID."""
        return f"{self.api.region_id}_is_expensive_now"

    @property
    def is_on(self):
        """Return true if current price is in most expensive 25%."""
        if not self.coordinator.data:
            return False

        current = self.coordinator.data.get("current_price")
        predictions = self.coordinator.data.get("predictions_24h", [])

        if not current or not predictions:
            return False

        now = datetime.now()
        today_end = now.replace(hour=23, minute=59, second=59)
        today_prices = [
            p["predicted_price"] for p in predictions
            if now <= datetime.fromisoformat(p["timestamp"].replace("Z", "+00:00")) <= today_end
        ]

        if not today_prices:
            return False

        current_price = current["price"]
        min_price = min(today_prices)
        max_price = max(today_prices)
        expensive_threshold = min_price + (max_price - min_price) * 0.75

        return current_price >= expensive_threshold

    @property
    def extra_state_attributes(self):
        """Return additional attributes."""
        if not self.coordinator.data:
            return {}

        current = self.coordinator.data.get("current_price")
        predictions = self.coordinator.data.get("predictions_24h", [])

        if not current or not predictions:
            return {}

        now = datetime.now()
        today_end = now.replace(hour=23, minute=59, second=59)
        today_prices = [
            p["predicted_price"] for p in predictions
            if now <= datetime.fromisoformat(p["timestamp"].replace("Z", "+00:00")) <= today_end
        ]

        if today_prices:
            current_price = current["price"]
            min_price = min(today_prices)
            max_price = max(today_prices)
            expensive_threshold = min_price + (max_price - min_price) * 0.75

            return {
                "current_price": round(current_price / 1000, 5),
                "expensive_threshold": round(expensive_threshold / 1000, 5),
                "min_price_today": round(min_price / 1000, 5),
                "max_price_today": round(max_price / 1000, 5),
            }
        return {}


class IsInCheapest3HoursBinarySensor(ElectricityPriceBinarySensorBase):
    """Binary sensor for whether current hour is in cheapest 3 hours today."""

    _attr_name = "Is In Cheapest 3 Hours"
    _attr_icon = "mdi:medal"

    @property
    def unique_id(self):
        """Return unique ID."""
        return f"{self.api.region_id}_is_in_cheapest_3"

    @property
    def is_on(self):
        """Return true if current price is in cheapest 3 hours."""
        if not self.coordinator.data:
            return False

        current = self.coordinator.data.get("current_price")
        predictions = self.coordinator.data.get("predictions_24h", [])

        if not current or not predictions:
            return False

        now = datetime.now()
        today_end = now.replace(hour=23, minute=59, second=59)
        today_prices = [
            p["predicted_price"] for p in predictions
            if now <= datetime.fromisoformat(p["timestamp"].replace("Z", "+00:00")) <= today_end
        ]

        if not today_prices:
            return False

        current_price = current["price"]
        rank = sum(1 for p in today_prices if p < current_price) + 1

        return rank <= 3

    @property
    def extra_state_attributes(self):
        """Return additional attributes."""
        if not self.coordinator.data:
            return {}

        current = self.coordinator.data.get("current_price")
        predictions = self.coordinator.data.get("predictions_24h", [])

        if not current or not predictions:
            return {}

        now = datetime.now()
        today_end = now.replace(hour=23, minute=59, second=59)
        today_prices = [
            p["predicted_price"] for p in predictions
            if now <= datetime.fromisoformat(p["timestamp"].replace("Z", "+00:00")) <= today_end
        ]

        if today_prices:
            current_price = current["price"]
            rank = sum(1 for p in today_prices if p < current_price) + 1

            return {
                "rank": rank,
                "total_hours": len(today_prices),
                "current_price": round(current_price / 1000, 5),
            }
        return {}


class IsInCheapest6HoursBinarySensor(ElectricityPriceBinarySensorBase):
    """Binary sensor for whether current hour is in cheapest 6 hours today."""

    _attr_name = "Is In Cheapest 6 Hours"
    _attr_icon = "mdi:star-circle"

    @property
    def unique_id(self):
        """Return unique ID."""
        return f"{self.api.region_id}_is_in_cheapest_6"

    @property
    def is_on(self):
        """Return true if current price is in cheapest 6 hours."""
        if not self.coordinator.data:
            return False

        current = self.coordinator.data.get("current_price")
        predictions = self.coordinator.data.get("predictions_24h", [])

        if not current or not predictions:
            return False

        now = datetime.now()
        today_end = now.replace(hour=23, minute=59, second=59)
        today_prices = [
            p["predicted_price"] for p in predictions
            if now <= datetime.fromisoformat(p["timestamp"].replace("Z", "+00:00")) <= today_end
        ]

        if not today_prices:
            return False

        current_price = current["price"]
        rank = sum(1 for p in today_prices if p < current_price) + 1

        return rank <= 6

    @property
    def extra_state_attributes(self):
        """Return additional attributes."""
        if not self.coordinator.data:
            return {}

        current = self.coordinator.data.get("current_price")
        predictions = self.coordinator.data.get("predictions_24h", [])

        if not current or not predictions:
            return {}

        now = datetime.now()
        today_end = now.replace(hour=23, minute=59, second=59)
        today_prices = [
            p["predicted_price"] for p in predictions
            if now <= datetime.fromisoformat(p["timestamp"].replace("Z", "+00:00")) <= today_end
        ]

        if today_prices:
            current_price = current["price"]
            rank = sum(1 for p in today_prices if p < current_price) + 1

            return {
                "rank": rank,
                "total_hours": len(today_prices),
                "current_price": round(current_price / 1000, 5),
            }
        return {}


class IsBelowAverageBinarySensor(ElectricityPriceBinarySensorBase):
    """Binary sensor for whether current price is below average."""

    _attr_name = "Is Below Average Price"
    _attr_icon = "mdi:trending-down"

    @property
    def unique_id(self):
        """Return unique ID."""
        return f"{self.api.region_id}_is_below_average"

    @property
    def is_on(self):
        """Return true if current price is below average."""
        if not self.coordinator.data:
            return False

        current = self.coordinator.data.get("current_price")
        predictions = self.coordinator.data.get("predictions_24h", [])

        if not current or not predictions:
            return False

        now = datetime.now()
        today_end = now.replace(hour=23, minute=59, second=59)
        today_prices = [
            p["predicted_price"] for p in predictions
            if now <= datetime.fromisoformat(p["timestamp"].replace("Z", "+00:00")) <= today_end
        ]

        if not today_prices:
            return False

        current_price = current["price"]
        avg_price = sum(today_prices) / len(today_prices)

        return current_price < avg_price

    @property
    def extra_state_attributes(self):
        """Return additional attributes."""
        if not self.coordinator.data:
            return {}

        current = self.coordinator.data.get("current_price")
        predictions = self.coordinator.data.get("predictions_24h", [])

        if not current or not predictions:
            return {}

        now = datetime.now()
        today_end = now.replace(hour=23, minute=59, second=59)
        today_prices = [
            p["predicted_price"] for p in predictions
            if now <= datetime.fromisoformat(p["timestamp"].replace("Z", "+00:00")) <= today_end
        ]

        if today_prices:
            current_price = current["price"]
            avg_price = sum(today_prices) / len(today_prices)

            return {
                "current_price": round(current_price / 1000, 5),
                "average_price": round(avg_price / 1000, 5),
                "difference": round((current_price - avg_price) / 1000, 5),
                "difference_percent": round(((current_price - avg_price) / avg_price) * 100, 1),
            }
        return {}


class TomorrowCheaperBinarySensor(ElectricityPriceBinarySensorBase):
    """Binary sensor for whether tomorrow is cheaper than today (>10% difference)."""

    _attr_name = "Tomorrow Is Cheaper"
    _attr_icon = "mdi:calendar-check"

    @property
    def unique_id(self):
        """Return unique ID."""
        return f"{self.api.region_id}_tomorrow_is_cheaper"

    @property
    def is_on(self):
        """Return true if tomorrow is significantly cheaper (>10%)."""
        if not self.coordinator.data:
            return False

        predictions_24h = self.coordinator.data.get("predictions_24h", [])
        predictions_7d = self.coordinator.data.get("predictions_7d", [])

        if not predictions_24h or not predictions_7d:
            return False

        today = datetime.now().date()
        tomorrow = (datetime.now() + timedelta(days=1)).date()

        # Calculate today's average
        today_prices = [
            p["predicted_price"] for p in predictions_24h
            if datetime.fromisoformat(p["timestamp"].replace("Z", "+00:00")).date() == today
        ]

        # Calculate tomorrow's average
        tomorrow_prices = [
            p["predicted_price"] for p in predictions_7d
            if datetime.fromisoformat(p["timestamp"].replace("Z", "+00:00")).date() == tomorrow
        ]

        if not today_prices or not tomorrow_prices:
            return False

        today_avg = sum(today_prices) / len(today_prices)
        tomorrow_avg = sum(tomorrow_prices) / len(tomorrow_prices)

        # Tomorrow is cheaper by at least 10%
        return tomorrow_avg < today_avg * 0.9

    @property
    def extra_state_attributes(self):
        """Return additional attributes."""
        if not self.coordinator.data:
            return {}

        predictions_24h = self.coordinator.data.get("predictions_24h", [])
        predictions_7d = self.coordinator.data.get("predictions_7d", [])

        if not predictions_24h or not predictions_7d:
            return {}

        today = datetime.now().date()
        tomorrow = (datetime.now() + timedelta(days=1)).date()

        today_prices = [
            p["predicted_price"] for p in predictions_24h
            if datetime.fromisoformat(p["timestamp"].replace("Z", "+00:00")).date() == today
        ]

        tomorrow_prices = [
            p["predicted_price"] for p in predictions_7d
            if datetime.fromisoformat(p["timestamp"].replace("Z", "+00:00")).date() == tomorrow
        ]

        if not today_prices or not tomorrow_prices:
            return {}

        today_avg = sum(today_prices) / len(today_prices)
        tomorrow_avg = sum(tomorrow_prices) / len(tomorrow_prices)
        savings_percent = ((today_avg - tomorrow_avg) / today_avg) * 100

        return {
            "today_average": round(today_avg / 1000, 5),
            "tomorrow_average": round(tomorrow_avg / 1000, 5),
            "savings_percent": round(savings_percent, 1),
            "recommendation": "Delay energy-intensive tasks until tomorrow" if savings_percent > 10 else "No significant savings",
        }
