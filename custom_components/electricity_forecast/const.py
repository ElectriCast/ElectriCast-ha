"""Constants for the Electricity Price Forecast integration."""

DOMAIN = "electricity_forecast"

# Configuration
CONF_API_URL = "api_url"
CONF_REGION_ID = "region_id"

# Default values
DEFAULT_API_URL = "http://localhost:8000"
DEFAULT_REGION_ID = "DE"

# Available regions
REGIONS = {
    "DE": "Germany (National Average)",
    "DE-BY": "Bavaria (Bayern)",
    "DE-BW": "Baden-Württemberg",
    "DE-NW": "North Rhine-Westphalia (NRW)",
    "DE-NI": "Lower Saxony (Niedersachsen)",
    "DE-HE": "Hesse (Hessen)",
    "DE-BE": "Berlin & Brandenburg",
    "DE-HH": "Hamburg & Schleswig-Holstein",
}

# Services
SERVICE_GET_CHEAPEST_HOURS = "get_cheapest_hours"
SERVICE_GET_EXPENSIVE_HOURS = "get_expensive_hours"

# Attributes
ATTR_FORECAST_24H = "forecast_24h"
ATTR_FORECAST_7D = "forecast_7d"
ATTR_CHEAPEST_HOURS = "cheapest_hours_today"
ATTR_EXPENSIVE_HOURS = "expensive_hours_today"
ATTR_AVERAGE_TODAY = "average_price_today"
ATTR_MIN_TODAY = "min_price_today"
ATTR_MAX_TODAY = "max_price_today"
ATTR_RECOMMENDATION = "recommendation"
