import unittest
from unittest.mock import patch, MagicMock
import json

from pwhl_scraper.api.client import PWHLApiClient
from pwhl_scraper.scrapers.basic_info import update_leagues, update_teams
from pwhl_scraper.scrapers.players import update_player
from pwhl_scraper.scrapers.stats import update_season_stats_teams


class TestScrapers(unittest.TestCase):

    def setUp(self):
        # Create a mock connection for database operations
        self.mock_conn = MagicMock()
        self.mock_cursor = MagicMock()
        self.mock_conn.cursor.return_value = self.mock_cursor

        # Create a mock API client
        self.mock_client = MagicMock(spec=PWHLApiClient)

    @patch('pwhl_scraper.scrapers.basic_info.create_connection')
    @patch('pwhl_scraper.scrapers.basic_info.PWHLApiClient')
    def test_update_leagues(self, mock_api_client_class, mock_create_connection):
        # Setup mock client and connection
        mock_api_client = MagicMock()
        mock_api_client_class.return_value = mock_api_client
        mock_create_connection.return_value = self.mock_conn

        # Mock API response
        mock_api_client.fetch_basic_info.return_value = {
            "current_league_id": "1",
            "leagues": [
                {
                    "id": "1",
                    "name": "Professional Women's Hockey League",
                    "short_name": "PWHL",
                    "code": "pwhl",
                    "logo_image": "https://example.com/logo.png"
                }
            ]
        }

        # Mock cursor.fetchall to return empty list (no existing leagues)
        self.mock_cursor.fetchall.return_value = []

        # Call the function
        result = update_leagues(self.mock_conn, [
            {
                "id": "1",
                "name": "Professional Women's Hockey League",
                "short_name": "PWHL",
                "code": "pwhl",
                "logo_image": "https://example.com/logo.png"
            }
        ])

        # Assertions
        self.assertEqual(result, 1)  # One league updated
        self.mock_cursor.executemany.assert_called_once()  # Insert was called

    def test_update_teams(self):
        # Mock fetchone to simulate no existing teams
        self.mock_cursor.fetchone.return_value = None

        # Test data
        teams_data = [
            {
                "id": "1",
                "name": "Toronto",
                "nickname": "Toronto",
                "code": "TOR",
                "city": "Toronto",
                "team_logo_url": "https://example.com/toronto.png",
                "division_id": "1"
            }
        ]

        # Call the function
        result = update_teams(self.mock_conn, teams_data, 5, 1)

        # Assertions
        self.assertEqual(result, 1)  # One team updated
        self.mock_cursor.execute.assert_called()  # Database was queried

    def test_update_player(self):
        # Mock fetchone to simulate no existing player
        self.mock_cursor.fetchone.return_value = None

        # Player data
        player_data = {
            "player_id": "123",
            "first_name": "Jane",
            "last_name": "Smith",
            "tp_jersey_number": "23",
            "active": "1",
            "rookie": "0",
            "position_id": "3",
            "position": "D",
            "height": "5'9\"",
            "weight": "150",
            "birthdate": "1997-05-15",
            "shoots": "L",
            "catches": "",
            "player_image": "https://example.com/jane.jpg",
            "birthtown": "Toronto",
            "birthprov": "ON",
            "birthcntry": "CAN",
            "latest_team_id": "1"
        }

        # Call the function
        result = update_player(self.mock_conn, player_data)

        # Assertions
        self.assertEqual(result, 1)  # One player updated
        self.mock_cursor.execute.assert_called()  # Database was queried

    def test_update_season_stats_teams(self):
        # Mock fetchone to simulate no existing stats
        self.mock_cursor.fetchone.return_value = None

        # Team stats data
        team_stats = [
            {
                "team_id": "1",
                "division_id": "1",
                "wins": "10",
                "losses": "5",
                "ties": "0",
                "ot_losses": "2",
                "points": "22",
                "goals_for": "45",
                "goals_against": "35"
            }
        ]

        # Call the function
        result = update_season_stats_teams(self.mock_conn, 5, team_stats)

        # Assertions
        self.assertEqual(result, 1)  # One team stats record updated
        self.mock_cursor.execute.assert_called()  # Database was queried


if __name__ == '__main__':
    unittest.main()
