"""API client for Electricity Price Forecast."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

import aiohttp


class ElectricityForecastAPI:
    """API client for electricity price forecasts."""

    def __init__(self, api_url: str, session: aiohttp.ClientSession, region_id: str = "DE"):
        """Initialize the API client."""
        self.api_url = api_url.rstrip("/")
        self.session = session
        self.region_id = region_id

    async def async_get_current_price(self) -> dict[str, Any]:
        """Get current electricity price."""
        url = f"{self.api_url}/api/historical/{self.region_id}/combined"
        params = {"hours": 1}

        async with self.session.get(url, params=params) as response:
            response.raise_for_status()
            data = await response.json()

            if data["historical_data"]:
                latest = data["historical_data"][-1]
                return {
                    "price": latest["price"],
                    "timestamp": latest["timestamp"],
                }
            return None

    async def async_get_predictions(self, hours: int = 24) -> list[dict[str, Any]]:
        """Get price predictions."""
        url = f"{self.api_url}/api/predictions/{self.region_id}/next-24h" if hours <= 24 else f"{self.api_url}/api/predictions/{self.region_id}/next-7d"

        async with self.session.get(url) as response:
            response.raise_for_status()
            return await response.json()

    async def async_get_historical_data(self, hours: int = 168) -> dict[str, Any]:
        """Get historical data."""
        url = f"{self.api_url}/api/historical/{self.region_id}/combined"
        params = {"hours": hours}

        async with self.session.get(url, params=params) as response:
            response.raise_for_status()
            return await response.json()

    async def async_get_all_data(self) -> dict[str, Any]:
        """Fetch all relevant data."""
        # Get predictions for next 24h and 7d
        predictions_24h = await self.async_get_predictions(24)
        predictions_7d = await self.async_get_predictions(168)

        # Get historical data (last 7 days)
        historical = await self.async_get_historical_data(168)

        # Get current price
        current = await self.async_get_current_price()

        return {
            "current_price": current,
            "predictions_24h": predictions_24h,
            "predictions_7d": predictions_7d,
            "historical": historical,
        }

    def get_cheapest_hours(self, predictions: list[dict], hours: int = 3) -> list[dict]:
        """Get N cheapest hours from predictions."""
        # Filter to only today's predictions
        now = datetime.now()
        today_end = now.replace(hour=23, minute=59, second=59)

        today_predictions = [
            p for p in predictions
            if now <= datetime.fromisoformat(p["timestamp"].replace("Z", "+00:00")) <= today_end
        ]

        # Sort by price
        sorted_predictions = sorted(today_predictions, key=lambda x: x["predicted_price"])
        return sorted_predictions[:hours]

    def get_expensive_hours(self, predictions: list[dict], hours: int = 3) -> list[dict]:
        """Get N most expensive hours from predictions."""
        # Filter to only today's predictions
        now = datetime.now()
        today_end = now.replace(hour=23, minute=59, second=59)

        today_predictions = [
            p for p in predictions
            if now <= datetime.fromisoformat(p["timestamp"].replace("Z", "+00:00")) <= today_end
        ]

        # Sort by price descending
        sorted_predictions = sorted(today_predictions, key=lambda x: x["predicted_price"], reverse=True)
        return sorted_predictions[:hours]

    def get_recommendation(self, current_price: float, predictions: list[dict]) -> str:
        """Get recommendation based on current price vs forecast."""
        if not predictions:
            return "unknown"

        # Get today's predictions
        now = datetime.now()
        today_end = now.replace(hour=23, minute=59, second=59)

        today_predictions = [
            p["predicted_price"] for p in predictions
            if now <= datetime.fromisoformat(p["timestamp"].replace("Z", "+00:00")) <= today_end
        ]

        if not today_predictions:
            return "unknown"

        avg_price = sum(today_predictions) / len(today_predictions)
        min_price = min(today_predictions)
        max_price = max(today_predictions)

        # Calculate thresholds (bottom 25% = cheap, top 25% = expensive)
        cheap_threshold = min_price + (max_price - min_price) * 0.25
        expensive_threshold = min_price + (max_price - min_price) * 0.75

        if current_price <= cheap_threshold:
            return "charge"  # Good time to charge batteries / run appliances
        elif current_price >= expensive_threshold:
            return "discharge"  # Good time to use stored energy / sell to grid
        elif current_price < avg_price:
            return "neutral_cheap"
        else:
            return "neutral_expensive"
