"""
Core API client for interacting with PWHL data sources.
"""
import time
import json
import logging
import requests
from typing import Dict, Any, Optional, List, Union, Tuple

from pwhl_scraper.api.endpoints import API_ENDPOINTS
from pwhl_scraper.config import API_CONFIG

logger = logging.getLogger(__name__)


class PWHLApiClient:
    """Client for interacting with PWHL HockeyTech API."""

    def __init__(self, rate_limit: float = 0.1, max_retries: int = 3):
        """
        Initialize the API client.

        Args:
            rate_limit: Minimum time between requests in seconds
            max_retries: Maximum number of retry attempts for failed requests
        """
        self.rate_limit = rate_limit
        self.max_retries = max_retries
        self.last_request_time = 0
        self.base_url = API_CONFIG["HOCKEYTECH_BASE_URL"]
        self.default_params = {
            "key": API_CONFIG["HOCKEYTECH_KEY"],
            "client_code": API_CONFIG["CLIENT_CODE"]
        }

    def _respect_rate_limit(self):
        if self.last_request_time == 0:
            self.last_request_time = time.time()
            return

        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time

        if time_since_last_request < self.rate_limit:
            sleep_time = self.rate_limit - time_since_last_request
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def _get(self, url: str, params: Dict[str, Any]) -> Optional[requests.Response]:
        """
        Make a GET request with retry logic and rate limiting.

        Args:
            url: API endpoint URL
            params: Query parameters

        Returns:
            Response object or None if all requests fail
        """
        for attempt in range(self.max_retries):
            self._respect_rate_limit()

            try:
                response = requests.get(url, params=params, timeout=10)

                if response.status_code == 200:
                    return response
                elif response.status_code == 429:  # Too Many Requests
                    logger.warning(f"Rate limit exceeded, retrying in {2 ** attempt} seconds")
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.warning(
                        f"Request failed with status code: {response.status_code}. Attempt {attempt + 1}/{self.max_retries}")
                    time.sleep(1)
            except requests.RequestException as e:
                logger.warning(f"Request error: {e}. Attempt {attempt + 1}/{self.max_retries}")
                time.sleep(1)

        logger.error(f"All {self.max_retries} attempts failed for URL: {url}")
        return None

    def fetch_data(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict]:
        """
        Fetch data from specified API endpoint.

        Args:
            endpoint: API endpoint path
            params: Query parameters to include

        Returns:
            Parsed JSON data or None if request fails
        """
        if params is None:
            params = {}

        # Merge default parameters with provided parameters
        merged_params = {**self.default_params, **params}

        # Build full URL
        url = self.base_url + endpoint

        # Make the request
        response = self._get(url, merged_params)
        if not response:
            return None

        text = response.text.strip()

        # Handle JSONP wrapping if present
        if text.startswith("(") and text.endswith(")"):
            text = text[1:-1]

        try:
            data = json.loads(text)
            return data
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON: {e}")
            return None

    def fetch_basic_info(self) -> Optional[Dict]:
        """Fetch basic league information (leagues, seasons, teams, etc.)."""
        endpoint_config = API_ENDPOINTS["basic_info"]
        return self.fetch_data(endpoint_config["path"], endpoint_config["params"])

    def fetch_player_info(self, player_id: int) -> Optional[Dict]:
        """
        Fetch detailed information for a specific player.

        Args:
            player_id: Player ID to fetch

        Returns:
            Player data dictionary or None if request fails
        """
        endpoint_config = API_ENDPOINTS["player_info"]
        params = endpoint_config["params"].copy()
        params["player_id"] = str(player_id)
        return self.fetch_data(endpoint_config["path"], params)

    def fetch_player_season_stats(self, player_id: int, category: str = "seasonstats") -> Optional[Dict]:
        """
        Fetch player season statistics.

        Args:
            player_id: Player ID
            category: Category of stats, one of: "seasonstats", "gamebygame", "mostrecentseasonstats"

        Returns:
            Player stats dictionary or None if request fails
        """
        endpoint_config = API_ENDPOINTS["player_season_stats"]
        params = endpoint_config["params"].copy()
        params["player_id"] = str(player_id)
        params["category"] = category
        return self.fetch_data(endpoint_config["path"], params)

    def fetch_skater_stats(self, season_id: int) -> Optional[Dict]:
        """
        Fetch statistics for all skaters in a season.

        Args:
            season_id: Season ID

        Returns:
            Skater stats dictionary or None if request fails
        """
        endpoint_config = API_ENDPOINTS["skater_stats"]
        params = endpoint_config["params"].copy()
        params["season"] = str(season_id)
        return self.fetch_data(endpoint_config["path"], params)

    def fetch_goalie_stats(self, season_id: int) -> Optional[Dict]:
        """
        Fetch statistics for all goalies in a season.

        Args:
            season_id: Season ID

        Returns:
            Goalie stats dictionary or None if request fails
        """
        endpoint_config = API_ENDPOINTS["goalie_stats"]
        params = endpoint_config["params"].copy()
        params["season"] = str(season_id)
        return self.fetch_data(endpoint_config["path"], params)

    def fetch_team_stats(self, season_id: int, special: str = "false") -> Optional[Dict]:
        """
        Fetch team statistics for a season.

        Args:
            season_id: Season ID
            special: "true" for special teams stats, "false" for regular stats

        Returns:
            Team stats dictionary or None if request fails
        """
        endpoint_config = API_ENDPOINTS["team_stats"]
        params = endpoint_config["params"].copy()
        params["season"] = str(season_id)
        params["special"] = special
        return self.fetch_data(endpoint_config["path"], params)

    def fetch_schedule(self, days_ahead: int = 10000, days_back: int = 10000) -> Optional[Dict]:
        """
        Fetch the league schedule.

        Args:
            days_ahead: Number of days ahead to fetch
            days_back: Number of days back to fetch

        Returns:
            Schedule dictionary or None if request fails
        """
        endpoint_config = API_ENDPOINTS["schedule"]
        params = endpoint_config["params"].copy()
        params["numberofdaysahead"] = str(days_ahead)
        params["numberofdaysback"] = str(days_back)
        return self.fetch_data(endpoint_config["path"], params)

    def fetch_game_summary(self, game_id: int) -> Optional[Dict]:
        """
        Fetch detailed summary for a specific game.

        Args:
            game_id: Game ID

        Returns:
            Game summary dictionary or None if request fails
        """
        endpoint_config = API_ENDPOINTS["game_summary"]
        params = endpoint_config["params"].copy()
        params["game_id"] = str(game_id)
        return self.fetch_data(endpoint_config["path"], params)

    def fetch_play_by_play(self, game_id: int) -> Optional[Dict]:
        """
        Fetch play-by-play data for a specific game.

        Args:
            game_id: Game ID

        Returns:
            Play-by-play data dictionary or None if request fails
        """
        endpoint_config = API_ENDPOINTS["play_by_play"]
        params = endpoint_config["params"].copy()
        params["game_id"] = str(game_id)
        return self.fetch_data(endpoint_config["path"], params)

    def fetch_playoffs(self, season_id: int) -> Optional[Dict]:
        """
        Fetch playoff bracket information for a season.

        Args:
            season_id: Season ID

        Returns:
            Playoff data dictionary or None if request fails
        """
        endpoint_config = API_ENDPOINTS["playoffs"]
        params = endpoint_config["params"].copy()
        params["season_id"] = str(season_id)
        return self.fetch_data(endpoint_config["path"], params)

    def fetch_teams_by_season(self, season_id: int) -> Optional[Dict]:
        """
        Fetch teams for a specific season.

        Args:
            season_id: Season ID

        Returns:
            Teams data dictionary or None if request fails
        """
        endpoint_config = API_ENDPOINTS["teams_by_season"]
        params = endpoint_config["params"].copy()
        params["season"] = str(season_id)
        return self.fetch_data(endpoint_config["path"], params)

    def fetch_seasons_list(self) -> Optional[Dict]:
        """
        Fetch list of all available seasons.

        Returns:
            Seasons list dictionary or None if request fails
        """
        endpoint_config = API_ENDPOINTS["seasons_list"]
        return self.fetch_data(endpoint_config["path"], endpoint_config["params"])

    def fetch_team_roster(self, team_id: int, season_id: int) -> Optional[Dict]:
        """
        Fetch roster for a specific team and season.

        Args:
            team_id: Team ID
            season_id: Season ID

        Returns:
            Team roster dictionary or None if request fails
        """
        endpoint_config = API_ENDPOINTS["team_roster"]
        params = endpoint_config["params"].copy()
        params["team_id"] = str(team_id)
        params["season_id"] = str(season_id)
        return self.fetch_data(endpoint_config["path"], params)

    def fetch_game_center(self, game_id: int, tab: str = "gamesummary") -> Optional[Dict]:
        """
        Fetch game center data for a specific game.

        Args:
            game_id: Game ID
            tab: Game center tab (gamesummary, clock, pxpverbose, preview)

        Returns:
            Game center dictionary or None if request fails
        """
        endpoint_config = API_ENDPOINTS["game_center"]
        params = endpoint_config["params"].copy()
        params["game_id"] = str(game_id)
        params["tab"] = tab
        return self.fetch_data(endpoint_config["path"], params)
