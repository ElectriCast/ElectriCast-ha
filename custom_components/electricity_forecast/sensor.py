"""Sensor platform for Electricity Price Forecast."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CURRENCY_EURO
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTR_AVERAGE_TODAY,
    ATTR_CHEAPEST_HOURS,
    ATTR_EXPENSIVE_HOURS,
    ATTR_FORECAST_24H,
    ATTR_FORECAST_7D,
    ATTR_MAX_TODAY,
    ATTR_MIN_TODAY,
    ATTR_RECOMMENDATION,
    DOMAIN,
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    api = hass.data[DOMAIN][config_entry.entry_id]["api"]

    sensors = [
        CurrentPriceSensor(coordinator, api),
        NextHourPriceSensor(coordinator, api),
        AveragePriceTodaySensor(coordinator, api),
        CheapestHourTodaySensor(coordinator, api),
        ExpensiveHourTodaySensor(coordinator, api),
        PriceTrendSensor(coordinator, api),
        RecommendationSensor(coordinator, api),
        ForecastSensor(coordinator, api),
        SevenDayForecastSensor(coordinator, api),
        CheapestDayNext7DSensor(coordinator, api),
        MostExpensiveDayNext7DSensor(coordinator, api),
        TomorrowVsTodaySensor(coordinator, api),
        WeeklyTrendSensor(coordinator, api),
    ]

    async_add_entities(sensors)


class ElectricityPriceSensorBase(CoordinatorEntity, SensorEntity):
    """Base class for Electricity Price sensors."""

    def __init__(self, coordinator, api):
        """Initialize the sensor."""
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


class CurrentPriceSensor(ElectricityPriceSensorBase):
    """Sensor for current electricity price."""

    _attr_name = "Current Price"
    _attr_native_unit_of_measurement = f"{CURRENCY_EURO}/kWh"
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:flash"
    _attr_suggested_display_precision = 5

    @property
    def unique_id(self):
        """Return unique ID."""
        return f"{self.api.region_id}_current_price"

    @property
    def native_value(self):
        """Return the current price in €/kWh."""
        if not self.coordinator.data:
            return None

        current = self.coordinator.data.get("current_price")
        if current:
            # Convert from €/MWh to €/kWh (divide by 1000)
            return round(current["price"] / 1000, 5)
        return None

    @property
    def extra_state_attributes(self):
        """Return additional attributes."""
        if not self.coordinator.data:
            return {}

        current = self.coordinator.data.get("current_price")
        predictions = self.coordinator.data.get("predictions_24h", [])

        if current:
            attrs = {
                "last_updated": current["timestamp"],
                "region": self.api.region_id,
                "price_mwh": round(current["price"], 2),  # Keep original unit available
            }

            # Add price ranking and comparison
            if predictions:
                now = datetime.now()
                today_end = now.replace(hour=23, minute=59, second=59)
                today_prices = [
                    p["predicted_price"] for p in predictions
                    if now <= datetime.fromisoformat(p["timestamp"].replace("Z", "+00:00")) <= today_end
                ]

                if today_prices:
                    avg_price = sum(today_prices) / len(today_prices)
                    sorted_prices = sorted(today_prices)
                    current_price = current["price"]

                    # Price rank (1 = cheapest, 24 = most expensive)
                    rank = sum(1 for p in today_prices if p < current_price) + 1

                    attrs.update({
                        "price_rank_today": rank,
                        "total_hours_today": len(today_prices),
                        "vs_average_percent": round(((current_price - avg_price) / avg_price) * 100, 1),
                        "is_below_average": current_price < avg_price,
                        "is_in_cheapest_3": rank <= 3,
                        "is_in_cheapest_6": rank <= 6,
                    })

            return attrs
        return {}


class NextHourPriceSensor(ElectricityPriceSensorBase):
    """Sensor for next hour electricity price."""

    _attr_name = "Next Hour Price"
    _attr_native_unit_of_measurement = f"{CURRENCY_EURO}/kWh"
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:clock-outline"
    _attr_suggested_display_precision = 5

    @property
    def unique_id(self):
        """Return unique ID."""
        return f"{self.api.region_id}_next_hour_price"

    @property
    def native_value(self):
        """Return the next hour price in €/kWh."""
        if not self.coordinator.data:
            return None

        predictions = self.coordinator.data.get("predictions_24h", [])
        if predictions:
            # Get the next hour prediction
            next_pred = predictions[0]
            return round(next_pred["predicted_price"] / 1000, 5)
        return None

    @property
    def extra_state_attributes(self):
        """Return additional attributes."""
        if not self.coordinator.data:
            return {}

        predictions = self.coordinator.data.get("predictions_24h", [])
        if predictions:
            next_pred = predictions[0]
            return {
                "forecast_time": next_pred["timestamp"],
                "confidence_lower": round(next_pred.get("confidence_lower", 0) / 1000, 5),
                "confidence_upper": round(next_pred.get("confidence_upper", 0) / 1000, 5),
                "price_mwh": round(next_pred["predicted_price"], 2),
                "region": self.api.region_id,
            }
        return {}


class AveragePriceTodaySensor(ElectricityPriceSensorBase):
    """Sensor for average price today."""

    _attr_name = "Average Price Today"
    _attr_native_unit_of_measurement = f"{CURRENCY_EURO}/kWh"
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:chart-bell-curve"
    _attr_suggested_display_precision = 5

    @property
    def unique_id(self):
        """Return unique ID."""
        return f"{self.api.region_id}_avg_price_today"

    @property
    def native_value(self):
        """Return the average price today in €/kWh."""
        if not self.coordinator.data:
            return None

        predictions = self.coordinator.data.get("predictions_24h", [])
        if not predictions:
            return None

        # Filter today's predictions
        now = datetime.now()
        today_end = now.replace(hour=23, minute=59, second=59)

        today_prices = [
            p["predicted_price"] for p in predictions
            if now <= datetime.fromisoformat(p["timestamp"].replace("Z", "+00:00")) <= today_end
        ]

        if today_prices:
            return round(sum(today_prices) / len(today_prices) / 1000, 5)
        return None

    @property
    def extra_state_attributes(self):
        """Return additional attributes."""
        if not self.coordinator.data:
            return {}

        predictions = self.coordinator.data.get("predictions_24h", [])
        if not predictions:
            return {}

        now = datetime.now()
        today_end = now.replace(hour=23, minute=59, second=59)

        today_prices = [
            p["predicted_price"] for p in predictions
            if now <= datetime.fromisoformat(p["timestamp"].replace("Z", "+00:00")) <= today_end
        ]

        if today_prices:
            return {
                ATTR_MIN_TODAY: round(min(today_prices) / 1000, 5),
                ATTR_MAX_TODAY: round(max(today_prices) / 1000, 5),
                "price_spread": round((max(today_prices) - min(today_prices)) / 1000, 5),
                "price_spread_mwh": round(max(today_prices) - min(today_prices), 2),
                "data_points": len(today_prices),
            }
        return {}


class CheapestHourTodaySensor(ElectricityPriceSensorBase):
    """Sensor for cheapest hour today."""

    _attr_name = "Cheapest Hour Today"
    _attr_native_unit_of_measurement = f"{CURRENCY_EURO}/kWh"
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_icon = "mdi:currency-eur-off"
    _attr_suggested_display_precision = 5

    @property
    def unique_id(self):
        """Return unique ID."""
        return f"{self.api.region_id}_cheapest_hour"

    @property
    def native_value(self):
        """Return the cheapest hour price in €/kWh."""
        if not self.coordinator.data:
            return None

        predictions = self.coordinator.data.get("predictions_24h", [])
        cheapest = self.api.get_cheapest_hours(predictions, 1)

        if cheapest:
            return round(cheapest[0]["predicted_price"] / 1000, 5)
        return None

    @property
    def extra_state_attributes(self):
        """Return additional attributes."""
        if not self.coordinator.data:
            return {}

        predictions = self.coordinator.data.get("predictions_24h", [])
        cheapest = self.api.get_cheapest_hours(predictions, 6)

        if cheapest:
            # Calculate hours until cheapest
            now = datetime.now()
            cheapest_time = datetime.fromisoformat(cheapest[0]["timestamp"].replace("Z", "+00:00"))
            hours_until = max(0, int((cheapest_time - now).total_seconds() / 3600))

            return {
                "cheapest_time": cheapest[0]["timestamp"],
                "hours_until_cheapest": hours_until,
                "starts_in_next_hour": hours_until <= 1,
                ATTR_CHEAPEST_HOURS: [
                    {
                        "time": p["timestamp"],
                        "price": round(p["predicted_price"] / 1000, 5),
                        "price_mwh": round(p["predicted_price"], 2)
                    }
                    for p in cheapest
                ],
            }
        return {}


class ExpensiveHourTodaySensor(ElectricityPriceSensorBase):
    """Sensor for most expensive hour today."""

    _attr_name = "Most Expensive Hour Today"
    _attr_native_unit_of_measurement = f"{CURRENCY_EURO}/kWh"
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_icon = "mdi:arrow-up-bold"

    @property
    def unique_id(self):
        """Return unique ID."""
        return f"{self.api.region_id}_expensive_hour"

    @property
    def native_value(self):
        """Return the most expensive hour price in €/kWh."""
        if not self.coordinator.data:
            return None

        predictions = self.coordinator.data.get("predictions_24h", [])
        expensive = self.api.get_expensive_hours(predictions, 1)

        if expensive:
            return round(expensive[0]["predicted_price"] / 1000, 5)
        return None

    @property
    def extra_state_attributes(self):
        """Return additional attributes."""
        if not self.coordinator.data:
            return {}

        predictions = self.coordinator.data.get("predictions_24h", [])
        expensive = self.api.get_expensive_hours(predictions, 6)

        if expensive:
            # Calculate hours until most expensive
            now = datetime.now()
            expensive_time = datetime.fromisoformat(expensive[0]["timestamp"].replace("Z", "+00:00"))
            hours_until = max(0, int((expensive_time - now).total_seconds() / 3600))

            return {
                "expensive_time": expensive[0]["timestamp"],
                "hours_until_expensive": hours_until,
                "starts_in_next_hour": hours_until <= 1,
                ATTR_EXPENSIVE_HOURS: [
                    {
                        "time": p["timestamp"],
                        "price": round(p["predicted_price"] / 1000, 5),
                        "price_mwh": round(p["predicted_price"], 2)
                    }
                    for p in expensive
                ],
            }
        return {}


class PriceTrendSensor(ElectricityPriceSensorBase):
    """Sensor for price trend."""

    _attr_name = "Price Trend"
    _attr_icon = "mdi:trending-up"

    @property
    def unique_id(self):
        """Return unique ID."""
        return f"{self.api.region_id}_price_trend"

    @property
    def native_value(self):
        """Return the price trend."""
        if not self.coordinator.data:
            return None

        current = self.coordinator.data.get("current_price")
        predictions = self.coordinator.data.get("predictions_24h", [])

        if not current or not predictions:
            return "unknown"

        current_price = current["price"]
        next_3h_prices = [p["predicted_price"] for p in predictions[:3]]

        if not next_3h_prices:
            return "unknown"

        avg_next_3h = sum(next_3h_prices) / len(next_3h_prices)

        if avg_next_3h > current_price * 1.05:
            return "rising"
        elif avg_next_3h < current_price * 0.95:
            return "falling"
        else:
            return "stable"

    @property
    def extra_state_attributes(self):
        """Return additional attributes."""
        if not self.coordinator.data:
            return {}

        current = self.coordinator.data.get("current_price")
        predictions = self.coordinator.data.get("predictions_24h", [])

        if not current or not predictions:
            return {}

        current_price = current["price"]
        next_3h_prices = [p["predicted_price"] for p in predictions[:3]]

        if next_3h_prices:
            avg_next_3h = sum(next_3h_prices) / len(next_3h_prices)
            change = ((avg_next_3h - current_price) / current_price) * 100

            return {
                "current_price": round(current_price, 2),
                "avg_next_3h": round(avg_next_3h, 2),
                "change_percent": round(change, 1),
            }
        return {}


class RecommendationSensor(ElectricityPriceSensorBase):
    """Sensor for action recommendation."""

    _attr_name = "Recommendation"
    _attr_icon = "mdi:lightbulb"

    @property
    def unique_id(self):
        """Return unique ID."""
        return f"{self.api.region_id}_recommendation"

    @property
    def native_value(self):
        """Return the recommendation."""
        if not self.coordinator.data:
            return None

        current = self.coordinator.data.get("current_price")
        predictions = self.coordinator.data.get("predictions_24h", [])

        if not current or not predictions:
            return "unknown"

        return self.api.get_recommendation(current["price"], predictions)

    @property
    def extra_state_attributes(self):
        """Return additional attributes."""
        recommendations = {
            "charge": "Good time to charge batteries or run appliances",
            "discharge": "Good time to use stored energy or sell to grid",
            "neutral_cheap": "Price below average but not optimal",
            "neutral_expensive": "Price above average, consider waiting",
            "unknown": "Insufficient data for recommendation",
        }

        state = self.native_value
        if state:
            return {
                "description": recommendations.get(state, "Unknown"),
                "icon_suggestion": self._get_icon_for_recommendation(state),
            }
        return {}

    def _get_icon_for_recommendation(self, recommendation: str) -> str:
        """Get icon for recommendation."""
        icons = {
            "charge": "mdi:battery-charging",
            "discharge": "mdi:battery-arrow-up",
            "neutral_cheap": "mdi:battery-50",
            "neutral_expensive": "mdi:battery-outline",
            "unknown": "mdi:help-circle",
        }
        return icons.get(recommendation, "mdi:help-circle")


class ForecastSensor(ElectricityPriceSensorBase):
    """Sensor with full forecast as attributes."""

    _attr_name = "Forecast"
    _attr_native_unit_of_measurement = f"{CURRENCY_EURO}/kWh"
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_icon = "mdi:chart-timeline-variant"

    @property
    def unique_id(self):
        """Return unique ID."""
        return f"{self.api.region_id}_forecast"

    @property
    def native_value(self):
        """Return the current/next hour price in €/kWh."""
        if not self.coordinator.data:
            return None

        predictions = self.coordinator.data.get("predictions_24h", [])
        if predictions:
            return round(predictions[0]["predicted_price"] / 1000, 5)
        return None

    @property
    def extra_state_attributes(self):
        """Return forecast data as attributes."""
        if not self.coordinator.data:
            return {}

        predictions_24h = self.coordinator.data.get("predictions_24h", [])
        predictions_7d = self.coordinator.data.get("predictions_7d", [])

        return {
            ATTR_FORECAST_24H: [
                {
                    "time": p["timestamp"],
                    "price": round(p["predicted_price"] / 1000, 5),
                    "conf_lower": round(p.get("confidence_lower", 0) / 1000, 5),
                    "conf_upper": round(p.get("confidence_upper", 0) / 1000, 5),
                }
                for p in predictions_24h
            ],
            ATTR_FORECAST_7D: [
                {
                    "time": p["timestamp"],
                    "price": round(p["predicted_price"] / 1000, 5),
                }
                for p in predictions_7d
            ],
            "forecast_24h_count": len(predictions_24h),
            "forecast_7d_count": len(predictions_7d),
        }


class SevenDayForecastSensor(ElectricityPriceSensorBase):
    """Dedicated sensor for 7-day price forecast."""

    _attr_name = "7 Day Price Forecast"
    _attr_native_unit_of_measurement = f"{CURRENCY_EURO}/kWh"
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_icon = "mdi:calendar-week"

    @property
    def unique_id(self):
        """Return unique ID."""
        return f"{self.api.region_id}_7day_forecast"

    @property
    def native_value(self):
        """Return the average price for the next 7 days in €/kWh."""
        if not self.coordinator.data:
            return None

        predictions_7d = self.coordinator.data.get("predictions_7d", [])
        if predictions_7d:
            prices = [p["predicted_price"] for p in predictions_7d]
            return round(sum(prices) / len(prices) / 1000, 5)
        return None

    @property
    def extra_state_attributes(self):
        """Return 7-day forecast data as attributes."""
        if not self.coordinator.data:
            return {}

        predictions_7d = self.coordinator.data.get("predictions_7d", [])

        if not predictions_7d:
            return {}

        prices = [p["predicted_price"] for p in predictions_7d]

        # Calculate daily averages
        daily_averages = []
        for i in range(0, len(predictions_7d), 24):
            day_data = predictions_7d[i:i+24]
            if day_data:
                day_prices = [p["predicted_price"] for p in day_data]
                daily_averages.append({
                    "date": day_data[0]["timestamp"][:10],
                    "avg_price": round(sum(day_prices) / len(day_prices) / 1000, 5),
                    "min_price": round(min(day_prices) / 1000, 5),
                    "max_price": round(max(day_prices) / 1000, 5),
                })

        return {
            "forecast_7d_full": [
                {
                    "time": p["timestamp"],
                    "price": round(p["predicted_price"] / 1000, 5),
                }
                for p in predictions_7d
            ],
            "daily_averages": daily_averages,
            "min_price_7d": round(min(prices) / 1000, 5),
            "max_price_7d": round(max(prices) / 1000, 5),
            "avg_price_7d": round(sum(prices) / len(prices) / 1000, 5),
            "total_hours": len(predictions_7d),
            "region": self.api.region_id,
        }


class CheapestDayNext7DSensor(ElectricityPriceSensorBase):
    """Sensor showing the cheapest day in next 7 days."""

    _attr_name = "Cheapest Day (7d)"
    _attr_icon = "mdi:calendar-star"

    @property
    def unique_id(self):
        """Return unique ID."""
        return f"{self.api.region_id}_cheapest_day_7d"

    @property
    def native_value(self):
        """Return the date of the cheapest day."""
        if not self.coordinator.data:
            return None

        predictions_7d = self.coordinator.data.get("predictions_7d", [])
        if not predictions_7d:
            return None

        # Calculate daily averages
        daily_data = {}
        for pred in predictions_7d:
            date = pred["timestamp"][:10]  # Get date part (YYYY-MM-DD)
            if date not in daily_data:
                daily_data[date] = []
            daily_data[date].append(pred["predicted_price"])

        # Find cheapest day
        daily_averages = {date: sum(prices) / len(prices) for date, prices in daily_data.items()}
        if not daily_averages:
            return None

        cheapest_date = min(daily_averages, key=daily_averages.get)

        # Format as weekday name
        from datetime import datetime as dt
        date_obj = dt.fromisoformat(cheapest_date)
        return date_obj.strftime("%A, %b %d")  # e.g., "Monday, Oct 23"

    @property
    def extra_state_attributes(self):
        """Return additional attributes."""
        if not self.coordinator.data:
            return {}

        predictions_7d = self.coordinator.data.get("predictions_7d", [])
        if not predictions_7d:
            return {}

        # Calculate daily averages
        daily_data = {}
        for pred in predictions_7d:
            date = pred["timestamp"][:10]
            if date not in daily_data:
                daily_data[date] = []
            daily_data[date].append(pred["predicted_price"])

        daily_averages = {date: sum(prices) / len(prices) for date, prices in daily_data.items()}
        if not daily_averages:
            return {}

        cheapest_date = min(daily_averages, key=daily_averages.get)
        cheapest_price = daily_averages[cheapest_date]

        # Days until cheapest
        from datetime import datetime as dt
        today = dt.now().date()
        cheapest_date_obj = dt.fromisoformat(cheapest_date).date()
        days_until = (cheapest_date_obj - today).days

        return {
            "date": cheapest_date,
            "average_price": round(cheapest_price / 1000, 5),
            "days_until": days_until,
            "is_today": days_until == 0,
            "is_tomorrow": days_until == 1,
            "all_daily_averages": {
                date: round(avg / 1000, 5)
                for date, avg in sorted(daily_averages.items())
            }
        }


class MostExpensiveDayNext7DSensor(ElectricityPriceSensorBase):
    """Sensor showing the most expensive day in next 7 days."""

    _attr_name = "Most Expensive Day (7d)"
    _attr_icon = "mdi:calendar-alert"

    @property
    def unique_id(self):
        """Return unique ID."""
        return f"{self.api.region_id}_expensive_day_7d"

    @property
    def native_value(self):
        """Return the date of the most expensive day."""
        if not self.coordinator.data:
            return None

        predictions_7d = self.coordinator.data.get("predictions_7d", [])
        if not predictions_7d:
            return None

        # Calculate daily averages
        daily_data = {}
        for pred in predictions_7d:
            date = pred["timestamp"][:10]
            if date not in daily_data:
                daily_data[date] = []
            daily_data[date].append(pred["predicted_price"])

        daily_averages = {date: sum(prices) / len(prices) for date, prices in daily_data.items()}
        if not daily_averages:
            return None

        expensive_date = max(daily_averages, key=daily_averages.get)

        from datetime import datetime as dt
        date_obj = dt.fromisoformat(expensive_date)
        return date_obj.strftime("%A, %b %d")

    @property
    def extra_state_attributes(self):
        """Return additional attributes."""
        if not self.coordinator.data:
            return {}

        predictions_7d = self.coordinator.data.get("predictions_7d", [])
        if not predictions_7d:
            return {}

        daily_data = {}
        for pred in predictions_7d:
            date = pred["timestamp"][:10]
            if date not in daily_data:
                daily_data[date] = []
            daily_data[date].append(pred["predicted_price"])

        daily_averages = {date: sum(prices) / len(prices) for date, prices in daily_data.items()}
        if not daily_averages:
            return {}

        expensive_date = max(daily_averages, key=daily_averages.get)
        expensive_price = daily_averages[expensive_date]

        from datetime import datetime as dt
        today = dt.now().date()
        expensive_date_obj = dt.fromisoformat(expensive_date).date()
        days_until = (expensive_date_obj - today).days

        return {
            "date": expensive_date,
            "average_price": round(expensive_price / 1000, 5),
            "days_until": days_until,
            "is_today": days_until == 0,
            "is_tomorrow": days_until == 1,
        }


class TomorrowVsTodaySensor(ElectricityPriceSensorBase):
    """Sensor comparing tomorrow's average price vs today."""

    _attr_name = "Tomorrow vs Today"
    _attr_icon = "mdi:compare-horizontal"
    _attr_native_unit_of_measurement = "%"

    @property
    def unique_id(self):
        """Return unique ID."""
        return f"{self.api.region_id}_tomorrow_vs_today"

    @property
    def native_value(self):
        """Return percentage difference (positive = tomorrow more expensive)."""
        if not self.coordinator.data:
            return None

        predictions_24h = self.coordinator.data.get("predictions_24h", [])
        predictions_7d = self.coordinator.data.get("predictions_7d", [])

        if not predictions_24h or not predictions_7d:
            return None

        from datetime import datetime as dt
        today = dt.now().date()
        tomorrow = (dt.now() + timedelta(days=1)).date()

        # Calculate today's average
        today_prices = [
            p["predicted_price"] for p in predictions_24h
            if dt.fromisoformat(p["timestamp"].replace("Z", "+00:00")).date() == today
        ]

        # Calculate tomorrow's average
        tomorrow_prices = [
            p["predicted_price"] for p in predictions_7d
            if dt.fromisoformat(p["timestamp"].replace("Z", "+00:00")).date() == tomorrow
        ]

        if not today_prices or not tomorrow_prices:
            return None

        today_avg = sum(today_prices) / len(today_prices)
        tomorrow_avg = sum(tomorrow_prices) / len(tomorrow_prices)

        # Percentage difference
        diff_percent = ((tomorrow_avg - today_avg) / today_avg) * 100

        return round(diff_percent, 1)

    @property
    def extra_state_attributes(self):
        """Return additional attributes."""
        if not self.coordinator.data:
            return {}

        predictions_24h = self.coordinator.data.get("predictions_24h", [])
        predictions_7d = self.coordinator.data.get("predictions_7d", [])

        if not predictions_24h or not predictions_7d:
            return {}

        from datetime import datetime as dt
        today = dt.now().date()
        tomorrow = (dt.now() + timedelta(days=1)).date()

        today_prices = [
            p["predicted_price"] for p in predictions_24h
            if dt.fromisoformat(p["timestamp"].replace("Z", "+00:00")).date() == today
        ]

        tomorrow_prices = [
            p["predicted_price"] for p in predictions_7d
            if dt.fromisoformat(p["timestamp"].replace("Z", "+00:00")).date() == tomorrow
        ]

        if not today_prices or not tomorrow_prices:
            return {}

        today_avg = sum(today_prices) / len(today_prices)
        tomorrow_avg = sum(tomorrow_prices) / len(tomorrow_prices)

        return {
            "today_average": round(today_avg / 1000, 5),
            "tomorrow_average": round(tomorrow_avg / 1000, 5),
            "tomorrow_cheaper": tomorrow_avg < today_avg,
            "recommendation": "Wait for tomorrow" if tomorrow_avg < today_avg * 0.9 else "Use energy today" if today_avg < tomorrow_avg * 0.9 else "Similar prices",
        }


class WeeklyTrendSensor(ElectricityPriceSensorBase):
    """Sensor showing price trend over the next 7 days."""

    _attr_name = "Weekly Price Trend"
    _attr_icon = "mdi:chart-line-variant"

    @property
    def unique_id(self):
        """Return unique ID."""
        return f"{self.api.region_id}_weekly_trend"

    @property
    def native_value(self):
        """Return trend direction."""
        if not self.coordinator.data:
            return None

        predictions_7d = self.coordinator.data.get("predictions_7d", [])
        if not predictions_7d or len(predictions_7d) < 48:
            return None

        # Compare first 24h vs last 24h
        first_day_avg = sum(p["predicted_price"] for p in predictions_7d[:24]) / 24
        last_day_avg = sum(p["predicted_price"] for p in predictions_7d[-24:]) / 24

        diff_percent = ((last_day_avg - first_day_avg) / first_day_avg) * 100

        if diff_percent > 10:
            return "Rising ↗"
        elif diff_percent < -10:
            return "Falling ↘"
        else:
            return "Stable →"

    @property
    def extra_state_attributes(self):
        """Return additional attributes."""
        if not self.coordinator.data:
            return {}

        predictions_7d = self.coordinator.data.get("predictions_7d", [])
        if not predictions_7d or len(predictions_7d) < 48:
            return {}

        first_day_avg = sum(p["predicted_price"] for p in predictions_7d[:24]) / 24
        last_day_avg = sum(p["predicted_price"] for p in predictions_7d[-24:]) / 24
        week_avg = sum(p["predicted_price"] for p in predictions_7d) / len(predictions_7d)

        diff_percent = ((last_day_avg - first_day_avg) / first_day_avg) * 100

        return {
            "first_day_average": round(first_day_avg / 1000, 5),
            "last_day_average": round(last_day_avg / 1000, 5),
            "week_average": round(week_avg / 1000, 5),
            "change_percent": round(diff_percent, 1),
            "prices_increasing": diff_percent > 5,
            "prices_decreasing": diff_percent < -5,
        }
