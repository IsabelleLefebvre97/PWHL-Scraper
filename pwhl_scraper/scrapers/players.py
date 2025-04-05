"""
Player data scraper for PWHL Scraper.

This module fetches and updates player information from all teams and seasons.
"""
import sqlite3
import logging
from typing import Dict, Any, Optional, List, Tuple, Union

from pwhl_scraper.api.client import PWHLApiClient
from pwhl_scraper.database.db_manager import create_connection, fetch_all

logger = logging.getLogger(__name__)


def get_seasons_and_teams(conn: sqlite3.Connection) -> List[Tuple[int, int]]:
    """
    Get all combinations of season IDs and team IDs from the database.

    Args:
        conn: Database connection

    Returns:
        List of (season_id, team_id) tuples
    """
    try:
        # Get seasons
        seasons_query = "SELECT id FROM seasons ORDER BY id DESC"
        seasons = fetch_all(conn, seasons_query)

        # Get teams
        teams_query = "SELECT id FROM teams ORDER BY id"
        teams = fetch_all(conn, teams_query)

        # Create combinations
        combinations = [(season[0], team[0]) for season in seasons for team in teams]

        return combinations
    except sqlite3.Error as e:
        logger.error(f"Error getting seasons and teams: {e}")
        return []


def fetch_player_roster(client: PWHLApiClient, season_id: int, team_id: int) -> List[Dict[str, Any]]:
    """
    Fetch player roster for a specific team and season.

    Args:
        client: PWHLApiClient instance
        season_id: Season ID
        team_id: Team ID

    Returns:
        List of player data dictionaries
    """
    logger.info(f"Fetching roster for team {team_id} in season {season_id}")

    roster_data = client.fetch_team_roster(team_id, season_id)

    if not roster_data or 'Roster' not in roster_data.get('SiteKit', {}):
        logger.warning(f"No roster data found for team {team_id} in season {season_id}")
        return []

    # Extract the roster list
    roster = roster_data['SiteKit']['Roster']

    # Make sure we're only working with player data (not coach data)
    # Coaches are typically in a nested array at the end of the roster
    players = []
    for item in roster:
        if isinstance(item, dict) and 'player_id' in item:
            players.append(item)

    return players


def fetch_player_details(client: PWHLApiClient, player_id: int) -> Optional[Dict[str, Any]]:
    """
    Fetch detailed player information.

    Args:
        client: PWHLApiClient instance
        player_id: Player ID

    Returns:
        Player details dictionary or None if request fails
    """
    logger.info(f"Fetching details for player {player_id}")

    # Get player profile
    player_data = client.fetch_player_info(player_id)

    if not player_data:
        logger.warning(f"No details found for player {player_id}")
        return None

    return player_data


def update_player(conn: sqlite3.Connection, player_roster_data: Dict[str, Any],
                  player_details: Optional[Dict[str, Any]] = None) -> int:
    """
    Update player information in the database.

    Args:
        conn: Database connection
        player_roster_data: Player data from roster API
        player_details: Additional player details from profile API

    Returns:
        1 if player was updated, 0 otherwise
    """
    # Extract player ID
    try:
        player_id = int(player_roster_data.get('player_id', 0))
        if not player_id:
            logger.warning("Invalid player ID")
            return 0
    except (ValueError, TypeError):
        logger.warning(f"Invalid player ID: {player_roster_data.get('player_id')}")
        return 0

    # Extract basic info from roster data
    first_name = player_roster_data.get('first_name', '')
    last_name = player_roster_data.get('last_name', '')

    # Get jersey number
    try:
        jersey_number = int(player_roster_data.get('tp_jersey_number', 0))
    except (ValueError, TypeError):
        jersey_number = None

    # Get active status
    active = player_roster_data.get('active', '0') == '1'

    # Get rookie status
    rookie = player_roster_data.get('rookie', '0') == '1'

    # Get position info
    try:
        position_id = int(player_roster_data.get('position_id', 0))
    except (ValueError, TypeError):
        position_id = None

    position = player_roster_data.get('position', '')

    # Get physical attributes
    height = player_roster_data.get('height', '')
    weight = player_roster_data.get('weight', '0')

    # Get birthdate
    birthdate = player_roster_data.get('birthdate', '')

    # Get shooting/catching hand
    shoots = player_roster_data.get('shoots', '')
    catches = player_roster_data.get('catches', '')

    # Get image URL
    image_url = player_roster_data.get('player_image', '')

    # Get birthplace info
    birthtown = player_roster_data.get('birthtown', '')
    birthprov = player_roster_data.get('birthprov', '')
    birthcntry = player_roster_data.get('birthcntry', '')

    # Get nationality (we'll use birthcntry if we have it)
    nationality = birthcntry

    # Get veteran status
    try:
        veteran_status = int(player_roster_data.get('veteran_status', 0))
    except (ValueError, TypeError):
        veteran_status = 0

    veteran_description = player_roster_data.get('veteran_description', '')

    # Get team ID
    try:
        latest_team_id = int(player_roster_data.get('latest_team_id', 0))
    except (ValueError, TypeError):
        latest_team_id = None

    draft_type = ''

    if player_details:
        # The API response structure for player details varies, so we need to handle different possibilities
        if isinstance(player_details, dict):
            # Attempt to extract draft info
            draft_info = player_roster_data.get('draftinfo', [])
            if draft_info and isinstance(draft_info, list) and len(draft_info) > 0:
                draft_type = draft_info[0].get('draft_type', '')
            elif 'SiteKit' in player_details and 'Player' in player_details['SiteKit']:
                player_data = player_details['SiteKit']['Player']
                if 'draft_type' in player_data:
                    draft_type = player_data.get('draft_type', '')

    # Check if player exists in database
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM players WHERE id = ?", (player_id,))
    exists = cursor.fetchone()

    try:
        if exists:
            # Update existing player
            query = """
            UPDATE players 
            SET first_name = ?, last_name = ?, jersey_number = ?, active = ?, rookie = ?,
                position_id = ?, position = ?, height = ?, weight = ?, birthdate = ?,
                shoots = ?, catches = ?, image_url = ?, birthtown = ?,
                birthprov = ?, birthcntry = ?, nationality = ?, draft_type = ?,
                veteran_status = ?, veteran_description = ?, latest_team_id = ?
            WHERE id = ?
            """
            cursor.execute(query, (
                first_name, last_name, jersey_number, active, rookie,
                position_id, position, height, weight, birthdate,
                shoots, catches, image_url, birthtown,
                birthprov, birthcntry, nationality, draft_type,
                veteran_status, veteran_description, latest_team_id,
                player_id
            ))
            logger.info(f"Updated player: {first_name} {last_name} (ID: {player_id})")
        else:
            # Insert new player
            query = """
            INSERT INTO players (
                id, first_name, last_name, jersey_number, active, rookie,
                position_id, position, height, weight, birthdate,
                shoots, catches, image_url, birthtown,
                birthprov, birthcntry, nationality, draft_type,
                veteran_status, veteran_description, latest_team_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            cursor.execute(query, (
                player_id, first_name, last_name, jersey_number, active, rookie,
                position_id, position, height, weight, birthdate,
                shoots, catches, image_url, birthtown,
                birthprov, birthcntry, nationality, draft_type,
                veteran_status, veteran_description, latest_team_id
            ))
            logger.info(f"Inserted new player: {first_name} {last_name} (ID: {player_id})")

        conn.commit()
        return 1
    except sqlite3.Error as e:
        logger.error(f"Error updating player {player_id}: {e}")
        conn.rollback()
        return 0


def update_players(db_path: str, player_id: Optional[int] = None) -> Union[int, None, Any]:
    """
    Update player information for all players or a specific player.

    Args:
        db_path: Path to the SQLite database
        player_id: Optional specific player ID to update

    Returns:
        Number of players updated
    """
    client = PWHLApiClient()
    conn = create_connection(db_path)
    updated_count = 0

    try:
        if player_id:
            # Update a specific player
            logger.info(f"Updating player ID {player_id}")

            # Get player details
            player_details = fetch_player_details(client, player_id)

            # We need some basic info that comes from the roster, but we don't know which team/season
            # So we'll check if the player exists first
            cursor = conn.cursor()
            cursor.execute("SELECT latest_team_id FROM players WHERE id = ?", (player_id,))
            result = cursor.fetchone()

            if result and result[0]:
                team_id = result[0]

                # Get the current season
                cursor.execute("SELECT id FROM seasons WHERE playoff = 0 ORDER BY id DESC LIMIT 1")
                season_result = cursor.fetchone()

                if season_result:
                    season_id = season_result[0]

                    # Fetch roster to get basic player info
                    roster = fetch_player_roster(client, season_id, team_id)

                    # Find the player in the roster
                    player_roster_data = None
                    for player in roster:
                        if int(player.get('player_id', 0)) == player_id:
                            player_roster_data = player
                            break

                    if player_roster_data:
                        # Update the player
                        if update_player(conn, player_roster_data, player_details):
                            updated_count += 1
                    else:
                        logger.warning(f"Player {player_id} not found in current roster")
                else:
                    logger.warning("No current season found in database")
            else:
                logger.warning(f"Player {player_id} not found in database with team information")

                # Try to get player details directly from API
                if player_details and 'SiteKit' in player_details and 'Player' in player_details['SiteKit']:
                    player_data = player_details['SiteKit']['Player']

                    # Create a minimal player roster data object
                    player_roster_data = {
                        'player_id': str(player_id),
                        'first_name': player_data.get('first_name', ''),
                        'last_name': player_data.get('last_name', ''),
                        'tp_jersey_number': player_data.get('jersey_number', ''),
                        'active': '1',  # Assume active
                        'rookie': '0',  # Assume not rookie
                        'position_id': player_data.get('position_id', ''),
                        'position': player_data.get('position', ''),
                        'height': player_data.get('height', ''),
                        'weight': player_data.get('weight', '0'),
                        'birthdate': player_data.get('birthdate', ''),
                        'shoots': player_data.get('shoots', ''),
                        'catches': player_data.get('catches', ''),
                        'player_image': player_data.get('image', ''),
                        'birthtown': player_data.get('birthtown', ''),
                        'birthprov': player_data.get('birthprov', ''),
                        'birthcntry': player_data.get('birthcntry', ''),
                        'latest_team_id': player_data.get('latest_team_id', '0'),
                        'veteran_status': player_data.get('veteran_status', '0'),
                        'veteran_description': player_data.get('veteran_description', '')
                    }

                    # Update the player
                    if update_player(conn, player_roster_data, player_details):
                        updated_count += 1
        else:
            # Update all players
            # Get all combinations of seasons and teams
            season_team_combinations = get_seasons_and_teams(conn)

            # Keep track of which players we've already processed
            processed_players = set()

            # Process each season and team
            for season_id, team_id in season_team_combinations:
                logger.info(f"Processing season {season_id}, team {team_id}")

                # Fetch roster
                roster = fetch_player_roster(client, season_id, team_id)

                # Process each player in the roster
                for player_roster_data in roster:
                    try:
                        player_id = int(player_roster_data.get('player_id', 0))

                        # Skip if we've already processed this player
                        if player_id in processed_players:
                            continue

                        # Get player details
                        player_details = fetch_player_details(client, player_id)

                        # Update the player
                        if update_player(conn, player_roster_data, player_details):
                            updated_count += 1

                        # Mark as processed
                        processed_players.add(player_id)

                    except (ValueError, TypeError) as e:
                        logger.warning(f"Error processing player: {e}")
                        continue

    except Exception as e:
        logger.error(f"Error updating players: {e}")
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

    # Update players
    from pwhl_scraper.config import DB_PATH

    update_players(DB_PATH)
