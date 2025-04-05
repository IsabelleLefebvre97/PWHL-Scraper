"""
Player data scraper for PWHL Scraper.
"""
import sqlite3
import logging
import time
from typing import Dict, Any, Optional, List, Tuple, Union

from pwhl_scraper.api.client import PWHLApiClient
from pwhl_scraper.utils.converters import (
    extract_height_weight,
    extract_hometown_parts,
    extract_team_id_from_url,
    filter_dict
)

logger = logging.getLogger(__name__)


def extract_player_fields(player_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Extract relevant player fields from the API response.

    Args:
        player_data: Raw player data from API

    Returns:
        Dictionary of processed player fields
    """
    if not player_data:
        return None

    player_info = player_data.get("info", {})

    # Extract basic info
    player_id = int(player_info.get("playerId", 0))
    first_name = player_info.get("firstName", "").strip()
    last_name = player_info.get("lastName", "").strip()
    player_type = player_info.get("playerType", None)
    position = player_info.get("position", None)

    # Classify position
    position_analysis = (
        "G" if position == "G" else
        "D" if position in ("D", "LD", "RD") else
        "F" if position in ("F", "C", "LW", "RW") else
        ""
    )

    birth_date = player_info.get("birthDate", None)
    height = player_info.get("height", None)
    weight = player_info.get("weight", None)
    shoots = player_info.get("shoots", None)
    catches = player_info.get("catches", None)
    biography = player_info.get("bio", None)

    try:
        jersey_number = int(player_info.get("jerseyNumber", 0)) if player_info.get("jerseyNumber") else None
    except ValueError:
        jersey_number = None

    # Handle location information
    birth_place = player_info.get("birthPlace", "")
    hometown, hometown_div = extract_hometown_parts(birth_place)

    nationality_obj = player_info.get("nationality", {})
    nationality = nationality_obj.get("name", "") if isinstance(nationality_obj, dict) else ""

    # Extract profile image
    image_url = player_info.get("profileImage", None)

    # Extract high-quality images
    media_section = player_data.get("media", {})
    media_images = media_section.get("images", []) if isinstance(media_section, dict) else []
    photo_1_url = media_images[0]["url"] if len(media_images) > 0 else None
    photo_2_url = media_images[1]["url"] if len(media_images) > 1 else None

    # Extract team ID from teamImage URL
    team_image_url = player_info.get("teamImage", None)
    team_id = extract_team_id_from_url(team_image_url)

    # Convert height/weight to metric
    height_cm, weight_kg = extract_height_weight(height, weight)

    return {
        "id": player_id,
        "team_id": team_id,
        "jersey_number": jersey_number,
        "first_name": first_name,
        "last_name": last_name,
        "birth_date": birth_date,
        "type": player_type,
        "position": position,
        "position_analysis": position_analysis,
        "shoots": shoots,
        "catches": catches,
        "height_cm": height_cm,
        "weight_kg": weight_kg,
        "height": height,
        "weight": weight,
        "hometown": hometown,
        "hometown_div": hometown_div,
        "nationality": nationality,
        "biography": biography,
        "image_url": image_url,
        "photo_1_url": photo_1_url,
        "photo_2_url": photo_2_url
    }


def update_player(conn: sqlite3.Connection, player_data: Dict[str, Any]) -> bool:
    """
    Update a player record in the database, only if data has changed.

    Args:
        conn: Database connection
        player_data: Player data from API

    Returns:
        True if the player was added or updated, False otherwise
    """
    cursor = conn.cursor()

    # Extract player fields from API data
    fields = extract_player_fields(player_data)
    if not fields:
        return False

    player_id = fields["id"]

    # Check if player already exists in database
    cursor.execute("SELECT * FROM players WHERE id = ?", (player_id,))
    existing_player = cursor.fetchone()

    if existing_player is None:
        # Player doesn't exist, insert new record
        column_names = ', '.join(fields.keys())
        placeholders = ', '.join(['?'] * len(fields))
        insert_query = f"INSERT INTO players ({column_names}) VALUES ({placeholders})"

        cursor.execute(insert_query, list(fields.values()))
        conn.commit()

        logger.info(f"Added new player: {fields['first_name']} {fields['last_name']} (ID: {player_id})")
        return True
    else:
        # Player exists, check if any fields have changed
        # Get column names from the players table
        cursor.execute("PRAGMA table_info(players)")
        columns = [info[1] for info in cursor.fetchall()]

        # Create a dictionary from the existing record
        existing_fields = {columns[i]: existing_player[i] for i in range(len(columns))}

        # List of fields that should not be set to None or empty values if they already have a value
        preserve_fields = ['hometown', 'hometown_div', 'nationality', 'weight_kg', 'height_cm']

        # Compare fields and build update if needed
        changes = {}
        for column in columns:
            if column in fields:
                # Special handling for fields we want to preserve
                if column in preserve_fields:
                    # Only update if the API provides a non-empty value
                    if fields[column] and fields[column] != existing_fields.get(column):
                        changes[column] = fields[column]
                # For all other fields, update if different
                elif fields[column] != existing_fields.get(column):
                    changes[column] = fields[column]

        if changes:
            # Build dynamic update query for only changed fields
            update_parts = [f"{field} = ?" for field in changes.keys()]
            update_query = f"UPDATE players SET {', '.join(update_parts)} WHERE id = ?"

            # Build parameters list
            params = list(changes.values())
            params.append(player_id)

            cursor.execute(update_query, params)
            conn.commit()

            logger.info(f"Updated player: {fields['first_name']} {fields['last_name']} (ID: {player_id})")
            logger.debug(f"Fields changed: {', '.join(changes.keys())}")
            return True
        else:
            logger.debug(f"No changes needed for player ID {player_id}")
            return False


def update_players(db_path: str, player_id: Optional[int] = None, max_id: int = 500) -> int:
    """
    Update player information in the database.

    Args:
        db_path: Path to database file
        player_id: Specific player ID to update, or None for all
        max_id: Maximum player ID to check if updating all

    Returns:
        Number of players updated
    """
    start_time = time.time()
    api_client = PWHLApiClient()
    conn = sqlite3.connect(db_path)

    # Stats for tracking
    players_checked = 0
    players_found = 0
    players_added_or_updated = 0

    try:
        if player_id is not None:
            # Update a specific player
            player_data = api_client.fetch_player_info(player_id)

            if player_data:
                players_found += 1
                if update_player(conn, player_data):
                    players_added_or_updated += 1

            players_checked = 1
        else:
            # Loop through player_ids from 0 to max_id
            for pid in range(max_id + 1):
                players_checked += 1

                # Progress indicator every 20 players
                if pid % 20 == 0:
                    elapsed = time.time() - start_time
                    logger.info(f"Progress: Checking player ID {pid}/{max_id} ({elapsed:.1f} seconds elapsed)")

                # Fetch player data
                player_data = api_client.fetch_player_info(pid)

                if player_data:
                    players_found += 1

                    # Update player in database
                    if update_player(conn, player_data):
                        players_added_or_updated += 1

    except Exception as e:
        logger.error(f"Error updating players: {e}")
        conn.rollback()
    finally:
        # Final stats
        elapsed = time.time() - start_time
        logger.info(f"Player data update summary:")
        logger.info(f"- Time elapsed: {elapsed:.2f} seconds")
        logger.info(f"- Players checked: {players_checked}")
        logger.info(f"- Players found in API: {players_found}")
        logger.info(f"- Players added or updated: {players_added_or_updated}")

        conn.close()

    return players_added_or_updated
