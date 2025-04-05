"""
Basic information scraper for PWHL Scraper.

This module fetches and updates basic league information including:
- Leagues
- Conferences
- Divisions
- Seasons
- Teams
"""
import sqlite3
import logging
from typing import Dict, Any, Optional, List

from pwhl_scraper.api.client import PWHLApiClient
from pwhl_scraper.database.db_manager import create_connection

logger = logging.getLogger(__name__)


def update_leagues(conn: sqlite3.Connection, leagues_data: List[Dict[str, Any]]) -> int:
    """
    Update league information in the database.

    Args:
        conn: Database connection
        leagues_data: List of league data dictionaries

    Returns:
        Number of leagues added or updated
    """
    logger.info("Updating leagues...")
    cursor = conn.cursor()
    updated_count = 0

    for league in leagues_data:
        league_id = int(league.get("id", 0))
        if not league_id:
            continue

        name = league.get("name", "")
        short_name = league.get("short_name", "")
        code = league.get("code", "")
        logo_url = league.get("logo_image", "")

        # Check if league exists
        cursor.execute("SELECT id FROM leagues WHERE id = ?", (league_id,))
        exists = cursor.fetchone()

        if exists:
            # Update existing league
            query = """
            UPDATE leagues 
            SET name = ?, short_name = ?, code = ?, logo_url = ?
            WHERE id = ?
            """
            cursor.execute(query, (name, short_name, code, logo_url, league_id))
        else:
            # Insert new league
            query = """
            INSERT INTO leagues (id, name, short_name, code, logo_url)
            VALUES (?, ?, ?, ?, ?)
            """
            cursor.execute(query, (league_id, name, short_name, code, logo_url))

        updated_count += 1

    conn.commit()
    logger.info(f"Updated {updated_count} leagues")
    return updated_count


def update_conferences(conn: sqlite3.Connection, conferences_data: List[Dict[str, Any]], league_id: int) -> int:
    """
    Update conference information in the database.

    Args:
        conn: Database connection
        conferences_data: List of conference data dictionaries
        league_id: League ID to associate with conferences

    Returns:
        Number of conferences added or updated
    """
    logger.info("Updating conferences...")
    cursor = conn.cursor()
    updated_count = 0

    for conference in conferences_data:
        conf_id = int(conference.get("conference_id", 0))
        if not conf_id:
            continue

        name = conference.get("conference_name", "")

        # Check if conference exists
        cursor.execute("SELECT id FROM conferences WHERE id = ?", (conf_id,))
        exists = cursor.fetchone()

        if exists:
            # Update existing conference
            query = """
            UPDATE conferences 
            SET name = ?, league_id = ?
            WHERE id = ?
            """
            cursor.execute(query, (name, league_id, conf_id))
        else:
            # Insert new conference
            query = """
            INSERT INTO conferences (id, name, league_id)
            VALUES (?, ?, ?)
            """
            cursor.execute(query, (conf_id, name, league_id))

        updated_count += 1

    conn.commit()
    logger.info(f"Updated {updated_count} conferences")
    return updated_count


def update_divisions(conn: sqlite3.Connection, divisions_data: List[Dict[str, Any]], league_id: int) -> int:
    """
    Update division information in the database.

    Args:
        conn: Database connection
        divisions_data: List of division data dictionaries
        league_id: League ID to associate with divisions

    Returns:
        Number of divisions added or updated
    """
    logger.info("Updating divisions...")
    cursor = conn.cursor()
    updated_count = 0

    for division in divisions_data:
        div_id = int(division.get("id", 0))
        if not div_id:
            continue

        name = division.get("name", "")

        # Try to get conference_id from the division data
        conference_id = None
        try:
            if "conference_id" in division:
                conference_id = int(division.get("conference_id"))
        except (ValueError, TypeError):
            pass

        # Check if division exists
        cursor.execute("SELECT id FROM divisions WHERE id = ?", (div_id,))
        exists = cursor.fetchone()

        if exists:
            # Update existing division
            query = """
            UPDATE divisions 
            SET name = ?, league_id = ?, conference_id = ?
            WHERE id = ?
            """
            cursor.execute(query, (name, league_id, conference_id, div_id))
        else:
            # Insert new division
            query = """
            INSERT INTO divisions (id, name, league_id, conference_id)
            VALUES (?, ?, ?, ?)
            """
            cursor.execute(query, (div_id, name, league_id, conference_id))

        updated_count += 1

    conn.commit()
    logger.info(f"Updated {updated_count} divisions")
    return updated_count


def update_seasons(conn: sqlite3.Connection, seasons_data: List[Dict[str, Any]]) -> int:
    """
    Update season information in the database.

    Args:
        conn: Database connection
        seasons_data: List of season data dictionaries

    Returns:
        Number of seasons added or updated
    """
    logger.info("Updating seasons...")
    cursor = conn.cursor()
    updated_count = 0

    for season in seasons_data:
        season_id = int(season.get("season_id", 0))
        if not season_id:
            continue

        name = season.get("season_name", "")

        # Get career and playoff flags
        career = 1 if season.get("career") == "1" else 0
        playoff = 1 if season.get("playoff") == "1" else 0

        # Get dates
        start_date = season.get("start_date", "")
        end_date = season.get("end_date", "")

        # Check if season exists
        cursor.execute("SELECT id FROM seasons WHERE id = ?", (season_id,))
        exists = cursor.fetchone()

        if exists:
            # Update existing season
            query = """
            UPDATE seasons 
            SET name = ?, career = ?, playoff = ?, start_date = ?, end_date = ?
            WHERE id = ?
            """
            cursor.execute(query, (name, career, playoff, start_date, end_date, season_id))
        else:
            # Insert new season
            query = """
            INSERT INTO seasons (id, name, career, playoff, start_date, end_date)
            VALUES (?, ?, ?, ?, ?, ?)
            """
            cursor.execute(query, (season_id, name, career, playoff, start_date, end_date))

        updated_count += 1

    conn.commit()
    logger.info(f"Updated {updated_count} seasons")
    return updated_count


def update_teams(conn: sqlite3.Connection, teams_data: List[Dict[str, Any]],
                 season_id: int, league_id: int) -> int:
    """
    Update team information in the database.

    Args:
        conn: Database connection
        teams_data: List of team data dictionaries
        season_id: Current season ID
        league_id: League ID

    Returns:
        Number of teams added or updated
    """
    logger.info(f"Updating teams for season {season_id}...")
    cursor = conn.cursor()
    updated_count = 0

    for team in teams_data:
        try:
            team_id = int(team.get("id", 0))
        except (ValueError, TypeError):
            continue

        if not team_id:
            continue

        name = team.get("name", "")
        nickname = team.get("nickname", "")
        code = team.get("code", "")
        city = team.get("city", "")
        logo_url = team.get("team_logo_url", "")

        # Get division_id if present
        try:
            division_id = int(team.get("division_id", 0))
        except (ValueError, TypeError):
            division_id = None

        # Default conference_id to null
        conference_id = None

        # If division_id is present, try to find associated conference_id
        if division_id:
            cursor.execute(
                "SELECT conference_id FROM divisions WHERE id = ?",
                (division_id,)
            )
            result = cursor.fetchone()
            if result:
                conference_id = result[0]

            # If we couldn't find the conference_id through the division,
            # ensure the division has the correct league_id
            cursor.execute(
                "UPDATE divisions SET league_id = ? WHERE id = ? AND (league_id IS NULL OR league_id != ?)",
                (league_id, division_id, league_id)
            )

        # Ensure we have a valid conference_id before inserting/updating team
        if conference_id is None and division_id is not None:
            # Log a warning about the missing relation
            logger.warning(f"Division {division_id} does not have an associated conference_id")

        # Check if team exists
        cursor.execute("SELECT id FROM teams WHERE id = ?", (team_id,))
        exists = cursor.fetchone()

        if exists:
            # Update existing team
            query = """
            UPDATE teams 
            SET name = ?, nickname = ?, code = ?, city = ?, logo_url = ?,
                league_id = ?, conference_id = ?, division_id = ?
            WHERE id = ?
            """
            cursor.execute(query, (
                name, nickname, code, city, logo_url,
                league_id, conference_id, division_id,
                team_id
            ))
        else:
            # Insert new team
            query = """
            INSERT INTO teams (
                id, name, nickname, code, city, logo_url,
                league_id, conference_id, division_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            cursor.execute(query, (
                team_id, name, nickname, code, city, logo_url,
                league_id, conference_id, division_id
            ))

        updated_count += 1

    conn.commit()
    logger.info(f"Updated {updated_count} teams")
    return updated_count


def get_current_season_id(conn: sqlite3.Connection) -> Optional[int]:
    """
    Get the current season ID from the database.

    Args:
        conn: Database connection

    Returns:
        Current season ID or None if not found
    """
    # Get the most recent season based on start_date
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id FROM seasons 
        WHERE playoff = 0 AND career = 1
        ORDER BY start_date DESC LIMIT 1
    """)
    result = cursor.fetchone()

    if result:
        return result[0]

    # If no seasons found, get the one with the highest ID
    cursor.execute("SELECT id FROM seasons ORDER BY id DESC LIMIT 1")
    result = cursor.fetchone()

    return result[0] if result else None


def update_basic_info(db_path: str) -> int | None:
    """
    Update basic information (leagues, conferences, divisions, seasons, teams).

    Args:
        db_path: Path to the SQLite database

    Returns:
        Total number of records updated
    """
    client = PWHLApiClient()
    conn = create_connection(db_path)
    total_updated = 0

    try:
        # Get bootstrap data (contains leagues, conferences, divisions)
        bootstrap_data = client.fetch_basic_info()

        if bootstrap_data:
            # Store current league ID for use throughout the process
            league_id = int(bootstrap_data.get("current_league_id", 1))

            # Update leagues
            leagues_data = bootstrap_data.get("leagues", [])
            total_updated += update_leagues(conn, leagues_data)

            # Update conferences with league_id
            conferences_data = bootstrap_data.get("conferences", [])
            total_updated += update_conferences(conn, conferences_data, league_id)

            # Update divisions with league_id
            divisions_data = bootstrap_data.get("divisions", [])
            total_updated += update_divisions(conn, divisions_data, league_id)
        else:
            logger.error("Failed to fetch bootstrap data")
            league_id = 1  # Default to 1 if not available

        # Get seasons data
        seasons_response = client.fetch_seasons_list()

        if seasons_response and 'Seasons' in seasons_response.get('SiteKit', {}):
            seasons_data = seasons_response['SiteKit']['Seasons']
            total_updated += update_seasons(conn, seasons_data)
        else:
            logger.error("Failed to fetch seasons data")

        # Get the current season ID
        current_season_id = get_current_season_id(conn)

        if current_season_id:
            # Get teams data for the current season
            teams_response = client.fetch_teams_by_season(current_season_id)

            if teams_response and 'Teamsbyseason' in teams_response.get('SiteKit', {}):
                teams_data = teams_response['SiteKit']['Teamsbyseason']
                total_updated += update_teams(conn, teams_data, current_season_id, league_id)
            else:
                logger.error(f"Failed to fetch teams data for season {current_season_id}")
        else:
            logger.error("No current season found")

    except Exception as e:
        logger.error(f"Error updating basic info: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

    return total_updated


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Update basic info
    from pwhl_scraper.config import DB_PATH

    update_basic_info(DB_PATH)
