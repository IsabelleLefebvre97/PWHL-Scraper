"""
Game data scraper for PWHL Scraper.

This module fetches and updates game information for all seasons.
"""
import logging
import sqlite3
from typing import Dict, Any, Optional, List, Tuple, Union

from pwhl_scraper.api.client import PWHLApiClient
from pwhl_scraper.database.db_manager import create_connection, fetch_all

logger = logging.getLogger(__name__)


def get_seasons(conn: sqlite3.Connection) -> List[Tuple[int]]:
    """
    Get all season IDs from the database.

    Args:
        conn: Database connection

    Returns:
        List of season IDs
    """
    try:
        # Get seasons
        seasons_query = "SELECT id FROM seasons ORDER BY id DESC"
        seasons = fetch_all(conn, seasons_query)
        return seasons
    except sqlite3.Error as e:
        logger.error(f"Error getting seasons: {e}")
        return []


def fetch_season_schedule(client: PWHLApiClient, season_id: int) -> List[Dict[str, Any]]:
    """
    Fetch schedule for a specific season.

    Args:
        client: PWHLApiClient instance
        season_id: Season ID

    Returns:
        List of game data dictionaries
    """
    logger.info(f"Fetching schedule for season {season_id}")

    # For the schedule endpoint we need to use the correct parameters
    endpoint = "index.php"
    params = {
        "feed": "modulekit",
        "view": "schedule",
        "season_id": str(season_id),
        "fmt": "json",
        "lang": "en"
    }

    schedule_data = client.fetch_data(endpoint, params)

    if not schedule_data or 'Schedule' not in schedule_data.get('SiteKit', {}):
        logger.warning(f"No schedule data found for season {season_id}")
        return []

    # Extract the schedule list
    schedule = schedule_data['SiteKit']['Schedule']

    return schedule


def update_game(conn: sqlite3.Connection, game_data: Dict[str, Any]) -> int:
    """
    Update game information in the database.

    Args:
        conn: Database connection
        game_data: Game data from API

    Returns:
        1 if game was updated, 0 otherwise
    """
    # Extract game ID
    try:
        game_id = int(game_data.get('game_id', 0))
        if not game_id:
            logger.warning("Invalid game ID")
            return 0
    except (ValueError, TypeError):
        logger.warning(f"Invalid game ID: {game_data.get('game_id')}")
        return 0

    # Extract season ID
    try:
        season_id = int(game_data.get('season_id', 0))
    except (ValueError, TypeError):
        logger.warning(f"Invalid season ID for game {game_id}: {game_data.get('season_id')}")
        return 0

    # Extract game number
    try:
        game_number = int(game_data.get('game_number', 0))
    except (ValueError, TypeError):
        game_number = None

    # Extract date (using GameDateISO8601 as specified)
    date = game_data.get('GameDateISO8601', '')
    
    # Extract team IDs
    try:
        home_team = int(game_data.get('home_team', 0))
        visiting_team = int(game_data.get('visiting_team', 0))
    except (ValueError, TypeError):
        logger.warning(f"Invalid team IDs for game {game_id}")
        return 0

    # Extract goal counts
    try:
        home_goal_count = int(game_data.get('home_goal_count', 0))
        visiting_goal_count = int(game_data.get('visiting_goal_count', 0))
    except (ValueError, TypeError):
        home_goal_count = 0
        visiting_goal_count = 0

    # Extract period information
    try:
        periods = int(game_data.get('period', 0))
    except (ValueError, TypeError):
        periods = 0

    # Extract overtime and shootout flags
    overtime = game_data.get('overtime', '0') == '1'
    shootout = game_data.get('shootout', '0') == '1'

    # Extract status
    try:
        status = int(game_data.get('status', 0))
    except (ValueError, TypeError):
        status = 0

    game_status = game_data.get('game_status', '')

    # Extract venue information
    venue_name = game_data.get('venue_name', '')
    venue_location = game_data.get('venue_location', '')

    # Extract attendance
    try:
        attendance = int(game_data.get('attendance', 0))
    except (ValueError, TypeError):
        attendance = 0

    # Check if game exists in database
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM games WHERE id = ?", (game_id,))
    exists = cursor.fetchone()

    try:
        if exists:
            # Update existing game
            query = """
            UPDATE games 
            SET season_id = ?, game_number = ?, date = ?, home_team = ?, visiting_team = ?,
                home_goal_count = ?, visiting_goal_count = ?, periods = ?, overtime = ?,
                shootout = ?, status = ?, game_status = ?, venue_name = ?, venue_location = ?,
                attendance = ?
            WHERE id = ?
            """
            cursor.execute(query, (
                season_id, game_number, date, home_team, visiting_team,
                home_goal_count, visiting_goal_count, periods, overtime,
                shootout, status, game_status, venue_name, venue_location,
                attendance, game_id
            ))
            logger.info(f"Updated game ID: {game_id}")
        else:
            # Insert new game
            query = """
            INSERT INTO games (
                id, season_id, game_number, date, home_team, visiting_team,
                home_goal_count, visiting_goal_count, periods, overtime,
                shootout, status, game_status, venue_name, venue_location,
                attendance
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            cursor.execute(query, (
                game_id, season_id, game_number, date, home_team, visiting_team,
                home_goal_count, visiting_goal_count, periods, overtime,
                shootout, status, game_status, venue_name, venue_location,
                attendance
            ))
            logger.info(f"Inserted new game ID: {game_id}")

        conn.commit()
        return 1
    except sqlite3.Error as e:
        logger.error(f"Error updating game {game_id}: {e}")
        conn.rollback()
        return 0


def fetch_game_details(client: PWHLApiClient, game_id: int) -> Optional[Dict[str, Any]]:
    """
    Fetch detailed information for a specific game.

    Args:
        client: PWHLApiClient instance
        game_id: Game ID

    Returns:
        Game details dictionary or None if request fails
    """
    logger.info(f"Fetching details for game {game_id}")

    # Get game summary
    game_data = client.fetch_game_summary(game_id)

    if not game_data:
        logger.warning(f"No details found for game {game_id}")
        return None

    return game_data


def update_games(db_path: str, season_id: Optional[int] = None) -> Union[int, None, Any]:
    """
    Update game information for all games or games in a specific season.

    Args:
        db_path: Path to the SQLite database
        season_id: Optional specific season ID to update

    Returns:
        Number of games updated
    """
    client = PWHLApiClient()
    conn = create_connection(db_path)
    updated_count = 0

    try:
        if season_id:
            # Update games for a specific season
            logger.info(f"Updating games for season ID {season_id}")

            # Fetch schedule for the season
            schedule = fetch_season_schedule(client, season_id)

            # Update each game in the schedule
            for game_data in schedule:
                if update_game(conn, game_data):
                    updated_count += 1
        else:
            # Update games for all seasons
            seasons = get_seasons(conn)

            # Process each season
            for (season_id,) in seasons:
                logger.info(f"Processing season {season_id}")

                # Fetch schedule for the season
                schedule = fetch_season_schedule(client, season_id)

                # Update each game in the schedule
                for game_data in schedule:
                    if update_game(conn, game_data):
                        updated_count += 1

    except Exception as e:
        logger.error(f"Error updating games: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

    return updated_count


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Update games
    from pwhl_scraper.config import DB_PATH

    update_games(DB_PATH)
