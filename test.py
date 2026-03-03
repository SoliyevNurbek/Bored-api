import unittest
from unittest.mock import Mock, patch

import requests

from main import Bored


class TestBored(unittest.TestCase):
    def setUp(self) -> None:
        self.client = Bored(timeout=1)

    @patch("main.requests.get")
    def test_get_activity(self, mock_get):
        response = Mock()
        response.json.return_value = {"activity": "Take a walk"}
        response.raise_for_status.return_value = None
        mock_get.return_value = response

        self.assertEqual(self.client.get_activity(), "Take a walk")

    @patch("main.requests.get")
    def test_get_activity_by_type_uses_query_param(self, mock_get):
        response = Mock()
        response.json.return_value = {"activity": "Learn origami", "type": "education"}
        response.raise_for_status.return_value = None
        mock_get.return_value = response

        data = self.client.get_activity_by_type("education")

        self.assertEqual(data["type"], "education")
        mock_get.assert_called_once_with(
            "https://www.boredapi.com/api/activity",
            params={"type": "education"},
            timeout=1,
        )

    def test_get_activity_by_type_rejects_invalid_type(self):
        with self.assertRaises(ValueError):
            self.client.get_activity_by_type("invalid")

    def test_price_range_rejects_invalid_order(self):
        with self.assertRaises(ValueError):
            self.client.get_activity_by_price_range(0.8, 0.2)

    def test_accessibility_rejects_out_of_range(self):
        with self.assertRaises(ValueError):
            self.client.get_activity_by_accessibility(1.2)

    @patch("main.requests.get", side_effect=requests.Timeout)
    def test_request_exception_wrapped(self, _):
        with self.assertRaises(RuntimeError):
            self.client.get_activity()

    @patch("main.requests.get")
    def test_api_error_payload_raises(self, mock_get):
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = {"error": "No activity found"}
        mock_get.return_value = response

        with self.assertRaises(RuntimeError):
            self.client.get_activity_by_price(0.4)


if __name__ == "__main__":
    unittest.main()
