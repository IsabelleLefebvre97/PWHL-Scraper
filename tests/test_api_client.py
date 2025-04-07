import unittest
from unittest.mock import patch, MagicMock
import json
from pwhl_scraper.api.client import PWHLApiClient


class TestPWHLApiClient(unittest.TestCase):

    def setUp(self):
        # Disable rate limiting and caching for tests
        self.client = PWHLApiClient(rate_limit=0, enable_cache=False)

    def test_fetch_data(self):
        # Create a test response with our test data
        expected_data = {"data": "test"}

        # Mock the _get method directly
        self.client._get = MagicMock()
        mock_response = MagicMock()
        mock_response.text = json.dumps(expected_data)
        mock_response.status_code = 200
        self.client._get.return_value = mock_response

        # Test method
        result = self.client.fetch_data('index.php', {'param': 'value'})

        # Assertions
        self.assertEqual(result, expected_data)
        # Verify the _get method was called
        self.client._get.assert_called_once()

    def test_fetch_basic_info(self):
        # Mock the fetch_data method that fetch_basic_info will call
        expected_data = {"leagues": [{"id": 1, "name": "PWHL"}]}
        self.client.fetch_data = MagicMock(return_value=expected_data)

        # Test the method
        result = self.client.fetch_basic_info()

        # Assertions
        self.assertEqual(result, expected_data)
        self.client.fetch_data.assert_called_once()


if __name__ == '__main__':
    unittest.main()
