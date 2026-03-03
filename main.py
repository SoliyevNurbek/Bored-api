from __future__ import annotations

from typing import Any, Dict

import requests
from requests import Response


class Bored:
    """Client for the Bored API.

    The API provides random activity suggestions and supports filtering by
    several query parameters.
    """

    ALLOWED_TYPES = {
        "education",
        "recreational",
        "social",
        "diy",
        "charity",
        "cooking",
        "relaxation",
        "music",
        "busywork",
    }

    def __init__(self, timeout: float = 5.0) -> None:
        self.url = "https://www.boredapi.com/api/"
        self.timeout = timeout

    def _request(self, params: Dict[str, Any] | None = None) -> Dict[str, Any]:
        """Call the activity endpoint and return parsed JSON."""
        endpoint = f"{self.url}activity"
        try:
            response: Response = requests.get(endpoint, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as exc:
            raise RuntimeError("Bored API request failed") from exc
        except ValueError as exc:
            raise RuntimeError("Bored API returned non-JSON data") from exc

        if not isinstance(data, dict):
            raise RuntimeError("Unexpected Bored API response format")

        if "error" in data:
            raise RuntimeError(f"Bored API error: {data['error']}")

        return data

    @staticmethod
    def _validate_unit_interval(value: float, field_name: str) -> None:
        if not 0 <= value <= 1:
            raise ValueError(f"{field_name} must be between 0 and 1")

    def get_activity(self) -> str:
        """Get a random activity text."""
        data = self._request()
        activity = data.get("activity")
        if not isinstance(activity, str):
            raise RuntimeError("Bored API response missing valid 'activity' field")
        return activity

    def get_activity_by_type(self, type: str) -> dict:
        """Get activity by type."""
        if type not in self.ALLOWED_TYPES:
            allowed = ", ".join(sorted(self.ALLOWED_TYPES))
            raise ValueError(f"type must be one of: {allowed}")
        return self._request(params={"type": type})

    def get_activity_by_id(self, key: int) -> dict:
        """Get activity by key."""
        if not 1_000_000 <= key <= 9_999_999:
            raise ValueError("key must be between 1000000 and 9999999")
        return self._request(params={"key": key})

    def get_activity_by_accessibility(self, accessibility: float) -> dict:
        """Get activity by accessibility factor."""
        self._validate_unit_interval(accessibility, "accessibility")
        return self._request(params={"accessibility": accessibility})

    def get_activity_by_price(self, price: float) -> dict:
        """Get activity by price factor."""
        self._validate_unit_interval(price, "price")
        return self._request(params={"price": price})

    def get_activity_by_price_range(self, minprice: float, maxprice: float) -> dict:
        """Get activity by price range."""
        self._validate_unit_interval(minprice, "minprice")
        self._validate_unit_interval(maxprice, "maxprice")
        if minprice > maxprice:
            raise ValueError("minprice must be less than or equal to maxprice")
        return self._request(params={"minprice": minprice, "maxprice": maxprice})
