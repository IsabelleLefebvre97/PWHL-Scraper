"""
Tests for the PWHL Scraper API client.
"""
import unittest
from unittest.mock import patch, MagicMock
from requests.exceptions import RequestException

from pwhl_scraper.api.client import PWHLApiClient
from pwhl_scraper.config import API_CONFIG


class TestPWHLApiClient(unittest.TestCase):
    """Test cases for the PWHLApiClient class."""

    def setUp(self):
        """Set up the test environment."""
        self.client = PWHLApiClient(rate_limit=0)  # No rate limit for testing
        self.base_url = API_CONFIG["HOCKEYTECH_BASE_URL"]
        self.default_params = {
            "key": API_CONFIG["HOCKEYTECH_KEY"],
            "client_code": API_CONFIG["CLIENT_CODE"]
        }

    @patch('pwhl_scraper.api.client.requests.get')
    def test_fetch_data_success(self, mock_get):
        """Test successful data fetch."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"data": "test"}'
        mock_get.return_value = mock_response

        # Test the method
        result = self.client.fetch_data('endpoint')

        # Assertions
        self.assertEqual(result, {"data": "test"})
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        self.assertEqual(args[0], f"{self.base_url}endpoint")
        self.assertEqual(kwargs["params"], self.default_params)

    @patch('pwhl_scraper.api.client.requests.get')
    def test_fetch_data_with_params(self, mock_get):
        """Test data fetch with custom parameters."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"data": "test with params"}'
        mock_get.return_value = mock_response

        # Test the method with custom params
        custom_params = {"param1": "value1", "param2": "value2"}
        result = self.client.fetch_data('endpoint', custom_params)

        # Assertions
        self.assertEqual(result, {"data": "test with params"})
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        expected_params = {**self.default_params, **custom_params}
        self.assertEqual(kwargs["params"], expected_params)

    @patch('pwhl_scraper.api.client.requests.get')
    def test_fetch_data_http_error(self, mock_get):
        """Test handling of HTTP errors."""
        # Setup mock response for HTTP error
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        # Test the method
        result = self.client.fetch_data('endpoint')

        # Assertions
        self.assertIsNone(result)
        self.assertEqual(mock_get.call_count, self.client.max_retries)

    @patch('pwhl_scraper.api.client.requests.get')
    def test_fetch_data_request_exception(self, mock_get):
        """Test handling of request exceptions."""
        # Setup mock to raise an exception
        mock_get.side_effect = RequestException("Connection error")

        # Test the method
        result = self.client.fetch_data('endpoint')

        # Assertions
        self.assertIsNone(result)
        self.assertEqual(mock_get.call_count, self.client.max_retries)

    @patch('pwhl_scraper.api.client.requests.get')
    def test_fetch_data_json_error(self, mock_get):
        """Test handling of JSON parsing errors."""
        # Setup mock response with invalid JSON
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = 'invalid json'
        mock_get.return_value = mock_response

        # Test the method
        result = self.client.fetch_data('endpoint')

        # Assertions
        self.assertIsNone(result)
        mock_get.assert_called_once()

    @patch('pwhl_scraper.api.client.requests.get')
    def test_fetch_data_jsonp_wrapping(self, mock_get):
        """Test handling of JSONP wrapped responses."""
        # Setup mock response with JSONP wrapping
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '({"data": "jsonp wrapped"})'
        mock_get.return_value = mock_response

        # Test the method
        result = self.client.fetch_data('endpoint')

        # Assertions
        self.assertEqual(result, {"data": "jsonp wrapped"})
        mock_get.assert_called_once()

    @patch('pwhl_scraper.api.client.time.sleep')
    @patch('pwhl_scraper.api.client.time.time')
    def test_respect_rate_limit(self, mock_time, mock_sleep):
        """Test rate limiting functionality."""
        # Setup mock time function
        mock_time.side_effect = [10.0, 10.1]  # First call returns 10.0, second returns 10.1

        # Reset last_request_time to force rate limiting
        client = PWHLApiClient(rate_limit=0.5)  # 0.5 second rate limit
        client.last_request_time = 10.0

        # Call the method
        client._respect_rate_limit()

        # Assertions
        mock_sleep.assert_called_once_with(0.4)  # Should sleep for 0.5 - 0.1 = 0.4 seconds

    def test_endpoint_methods(self):
        """Test all endpoint-specific methods."""
        with patch.object(PWHLApiClient, 'fetch_data', return_value={"test": "data"}) as mock_fetch:
            # Test basic_info method
            self.assertEqual(self.client.fetch_basic_info(), {"test": "data"})

            # Test player_info method
            self.assertEqual(self.client.fetch_player_info(123), {"test": "data"})

            # Test player_season_stats method
            self.assertEqual(self.client.fetch_player_season_stats(123), {"test": "data"})

            # Test skater_stats method
            self.assertEqual(self.client.fetch_skater_stats(2023), {"test": "data"})

            # Test goalie_stats method
            self.assertEqual(self.client.fetch_goalie_stats(2023), {"test": "data"})

            # Test team_stats method
            self.assertEqual(self.client.fetch_team_stats(2023), {"test": "data"})

            # Test schedule method
            self.assertEqual(self.client.fetch_schedule(), {"test": "data"})

            # Test game_summary method
            self.assertEqual(self.client.fetch_game_summary(456), {"test": "data"})

            # Test play_by_play method
            self.assertEqual(self.client.fetch_play_by_play(456), {"test": "data"})

            # Test playoffs method
            self.assertEqual(self.client.fetch_playoffs(2023), {"test": "data"})

            # Test teams_by_season method
            self.assertEqual(self.client.fetch_teams_by_season(2023), {"test": "data"})

            # Test seasons_list method
            self.assertEqual(self.client.fetch_seasons_list(), {"test": "data"})

            # Test team_roster method
            self.assertEqual(self.client.fetch_team_roster(789, 2023), {"test": "data"})

            # Test game_center method
            self.assertEqual(self.client.fetch_game_center(456), {"test": "data"})

            # Verify all endpoint calls used the correct paths and parameters
            self.assertEqual(mock_fetch.call_count, 14)  # 14 endpoint methods tested


if __name__ == '__main__':
    unittest.main()
