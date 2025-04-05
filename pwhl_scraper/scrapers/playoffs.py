"""
Playoff data scraper for PWHL Scraper.

This module fetches and updates playoff information for all playoff seasons.
"""
import sqlite3
import logging
from typing import Dict, Any, Optional, List, Tuple

from pwhl_scraper.api.client import PWHLApiClient
from pwhl_scraper.database.db_manager import create_connection, execute_query, fetch_one, fetch_all

logger = logging.getLogger(__name__)


def get_playoff_seasons(conn: sqlite3.Connection) -> List[Tuple[int]]:
    """
    Get all playoff season IDs from the database.

    Args:
        conn: Database connection

    Returns:
        List of playoff season IDs
    """
    try:
        # Get playoff seasons
        seasons_query = "SELECT id FROM seasons WHERE playoff = 1 ORDER BY id DESC"
        seasons = fetch_all(conn, seasons_query)
        return seasons
    except sqlite3.Error as e:
        logger.error(f"Error getting playoff seasons: {e}")
        return []


def fetch_playoff_bracket(client: PWHLApiClient, season_id: int) -> Optional[Dict[str, Any]]:
    """
    Fetch playoff bracket data for a specific season.

    Args:
        client: PWHLApiClient instance
        season_id: Season ID

    Returns:
        Playoff bracket data dictionary or None if request fails
    """
    logger.info(f"Fetching playoff bracket for season {season_id}")

    # Get playoff bracket
    bracket_data = client.fetch_playoffs(season_id)

    if not bracket_data or 'Brackets' not in bracket_data.get('SiteKit', {}):
        logger.warning(f"No playoff bracket data found for season {season_id}")
        return None

    return bracket_data['SiteKit']['Brackets']


def update_playoff_rounds(conn: sqlite3.Connection, season_id: int, rounds_data: List[Dict[str, Any]]) -> int:
    """
    Update playoff rounds information in the database.

    Args:
        conn: Database connection
        season_id: Season ID
        rounds_data: List of playoff round data dictionaries

    Returns:
        Number of rounds updated
    """
    logger.info(f"Updating playoff rounds for season {season_id}")

    updated_count = 0

    for round_data in rounds_data:
        # Create a unique ID for the round
        round_id = f"{season_id}_{round_data.get('round', '')}"

        # Extract round info
        try:
            round_num = int(round_data.get('round', 0))
        except (ValueError, TypeError):
            round_num = 0

        round_name = round_data.get('round_name', '')

        try:
            round_type_id = int(round_data.get('round_type_id', 0))
        except (ValueError, TypeError):
            round_type_id = 0

        round_type_name = round_data.get('round_type_name', '')

        # Check if round exists in database
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM playoff_rounds WHERE id = ?", (round_id,))
        exists = cursor.fetchone()

        try:
            if exists:
                # Update existing round
                query = """
                UPDATE playoff_rounds 
                SET season_id = ?, round = ?, round_name = ?, round_type_id = ?, round_type_name = ?
                WHERE id = ?
                """
                cursor.execute(query, (
                    season_id, round_num, round_name, round_type_id, round_type_name, round_id
                ))
            else:
                # Insert new round
                query = """
                INSERT INTO playoff_rounds (
                    id, season_id, round, round_name, round_type_id, round_type_name
                ) VALUES (?, ?, ?, ?, ?, ?)
                """
                cursor.execute(query, (
                    round_id, season_id, round_num, round_name, round_type_id, round_type_name
                ))

            updated_count += 1

            # Now update series for this round
            series_count = update_playoff_series(conn, season_id, round_id, round_num, round_data.get('matchups', []))
            logger.info(f"Updated {series_count} playoff series for round {round_id}")

        except sqlite3.Error as e:
            logger.error(f"Error updating playoff round {round_id}: {e}")
            conn.rollback()

    conn.commit()
    logger.info(f"Updated {updated_count} playoff rounds for season {season_id}")
    return updated_count


def update_playoff_series(conn: sqlite3.Connection, season_id: int, round_id: str,
                          round_num: int, series_data: List[Dict[str, Any]]) -> int:
    """
    Update playoff series information in the database.

    Args:
        conn: Database connection
        season_id: Season ID
        round_id: Round ID
        round_num: Round number
        series_data: List of playoff series data dictionaries

    Returns:
        Number of series updated
    """
    logger.info(f"Updating playoff series for round {round_id}")

    updated_count = 0

    for series in series_data:
        # Create a unique ID for the series
        series_letter = series.get('series_letter', '')
        series_id = f"{round_id}_{series_letter}"

        # Extract series info
        series_name = series.get('series_name', '')
        series_logo_url = series.get('series_logo', '')
        active = series.get('active', '0') == '1'

        try:
            team1 = int(series.get('team1', 0))
            team2 = int(series.get('team2', 0))
        except (ValueError, TypeError):
            team1 = None
            team2 = None

        content_en = series.get('content_en', '')

        # Extract winner info
        winner = None
        winner_str = series.get('winner', '')
        if winner_str and winner_str in ('1', '2'):
            if winner_str == '1':
                winner = team1
            else:
                winner = team2

        try:
            team1_wins = int(series.get('team1_wins', 0))
            team2_wins = int(series.get('team2_wins', 0))
            ties = int(series.get('ties', 0))
        except (ValueError, TypeError):
            team1_wins = 0
            team2_wins = 0
            ties = 0

        feeder_series_1 = series.get('feeder_series1', '')
        feeder_series_2 = series.get('feeder_series2', '')

        # Check if series exists in database
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM playoff_series WHERE id = ?", (series_id,))
        exists = cursor.fetchone()

        try:
            if exists:
                # Update existing series
                query = """
                UPDATE playoff_series 
                SET season_id = ?, round_id = ?, series_letter = ?, series_name = ?,
                    series_logo_url = ?, active = ?, team1 = ?, team2 = ?, content_en = ?,
                    winner = ?, team1_wins = ?, team2_wins = ?, ties = ?,
                    feeder_series_1 = ?, feeder_series_2 = ?, round = ?
                WHERE id = ?
                """
                cursor.execute(query, (
                    season_id, round_id, series_letter, series_name,
                    series_logo_url, active, team1, team2, content_en,
                    winner, team1_wins, team2_wins, ties,
                    feeder_series_1, feeder_series_2, round_num,
                    series_id
                ))
            else:
                # Insert new series
                query = """
                INSERT INTO playoff_series (
                    id, season_id, round_id, series_letter, series_name,
                    series_logo_url, active, team1, team2, content_en,
                    winner, team1_wins, team2_wins, ties,
                    feeder_series_1, feeder_series_2, round
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                cursor.execute(query, (
                    series_id, season_id, round_id, series_letter, series_name,
                    series_logo_url, active, team1, team2, content_en,
                    winner, team1_wins, team2_wins, ties,
                    feeder_series_1, feeder_series_2, round_num
                ))

            updated_count += 1

            # Now update games for this series
            games_count = update_playoff_games(conn, season_id, round_id, series_id, series.get('games', []))
            logger.info(f"Updated {games_count} playoff games for series {series_id}")

        except sqlite3.Error as e:
            logger.error(f"Error updating playoff series {series_id}: {e}")
            # Don't rollback here, we want to continue with other series

    return updated_count


def update_playoff_games(conn: sqlite3.Connection, season_id: int, round_id: str,
                         series_id: str, games_data: List[Dict[str, Any]]) -> int:
    """
    Update playoff games information in the database.

    Args:
        conn: Database connection
        season_id: Season ID
        round_id: Round ID
        series_id: Series ID
        games_data: List of playoff game data dictionaries

    Returns:
        Number of games updated
    """
    logger.info(f"Updating playoff games for series {series_id}")

    updated_count = 0

    for game in games_data:
        try:
            game_id = int(game.get('game_id', 0))
            if not game_id:
                continue
        except (ValueError, TypeError):
            continue

        # Create a unique ID for the playoff game
        playoff_game_id = f"{series_id}_{game_id}"

        # Check if game exists in database
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM playoff_games WHERE id = ?", (playoff_game_id,))
        exists = cursor.fetchone()

        try:
            if exists:
                # Update existing playoff game
                query = """
                UPDATE playoff_games 
                SET season_id = ?, round_id = ?, series_id = ?, game_id = ?
                WHERE id = ?
                """
                cursor.execute(query, (
                    season_id, round_id, series_id, game_id, playoff_game_id
                ))
            else:
                # Insert new playoff game
                query = """
                INSERT INTO playoff_games (
                    id, season_id, round_id, series_id, game_id
                ) VALUES (?, ?, ?, ?, ?)
                """
                cursor.execute(query, (
                    playoff_game_id, season_id, round_id, series_id, game_id
                ))

            updated_count += 1

        except sqlite3.Error as e:
            logger.error(f"Error updating playoff game {playoff_game_id}: {e}")
            # Don't rollback here, we want to continue with other games

    return updated_count


def update_playoffs(db_path: str, season_id: Optional[int] = None) -> int:
    """
    Update playoff information for all playoff seasons or a specific season.

    Args:
        db_path: Path to the SQLite database
        season_id: Optional specific season ID to update

    Returns:
        Number of playoff rounds updated
    """
    client = PWHLApiClient()
    conn = create_connection(db_path)
    updated_count = 0

    try:
        if season_id:
            # Update playoffs for a specific season
            logger.info(f"Updating playoffs for season ID {season_id}")

            # Fetch playoff bracket for the season
            bracket_data = fetch_playoff_bracket(client, season_id)

            # Update playoff rounds, series, and games
            if bracket_data and 'rounds' in bracket_data:
                updated_count = update_playoff_rounds(conn, season_id, bracket_data['rounds'])
        else:
            # Update playoffs for all playoff seasons
            seasons = get_playoff_seasons(conn)

            # Process each playoff season
            for (season_id,) in seasons:
                logger.info(f"Processing playoff season {season_id}")

                # Fetch playoff bracket for the season
                bracket_data = fetch_playoff_bracket(client, season_id)

                # Update playoff rounds, series, and games
                if bracket_data and 'rounds' in bracket_data:
                    round_count = update_playoff_rounds(conn, season_id, bracket_data['rounds'])
                    updated_count += round_count

    except Exception as e:
        logger.error(f"Error updating playoffs: {e}")
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

    # Update playoffs
    from pwhl_scraper.config import DB_PATH

    update_playoffs(DB_PATH)
