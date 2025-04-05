"""
Play-by-play scraper for PWHL Scraper.
This module fetches and updates detailed play-by-play information for each game including:
- Goalie changes
- Faceoffs
- Hits
- Shots
- Blocked shots
- Goals (with plus/minus players)
- Penalties
- Shootouts
"""
import sqlite3
import logging
from typing import Dict, Any, List, Optional, Tuple

from pwhl_scraper.api.client import PWHLApiClient
from pwhl_scraper.database.db_manager import create_connection, execute_query, fetch_one, fetch_all

logger = logging.getLogger(__name__)


def process_game_play_by_play(conn: sqlite3.Connection, game_id: int, season_id: int) -> int:
    """
    Fetch and process play-by-play data for a specific game.

    Args:
        conn: Database connection
        game_id: Game ID to process
        season_id: Season ID for the game

    Returns:
        Number of events processed
    """
    client = PWHLApiClient()
    pbp_data = client.fetch_play_by_play(game_id)

    if not pbp_data or 'GC' not in pbp_data or 'Pxpverbose' not in pbp_data['GC']:
        logger.warning(f"No play-by-play data found for game {game_id}")
        return 0

    # Get team information for the game
    home_team, visiting_team = get_game_teams(conn, game_id)
    if not home_team or not visiting_team:
        logger.error(f"Could not determine teams for game {game_id}")
        return 0

    events = pbp_data['GC']['Pxpverbose']
    total_processed = 0

    for event in events:
        event_type = event.get('event')

        try:
            if event_type == 'goalie_change':
                if process_goalie_change(conn, event, game_id, season_id, home_team_id, away_team_id):
                    total_processed += 1

            elif event_type == 'faceoff':
                if process_faceoff(conn, event, game_id, season_id, home_team_id, away_team_id):
                    total_processed += 1

            elif event_type == 'hit':
                if process_hit(conn, event, game_id, season_id, home_team_id, away_team_id):
                    total_processed += 1

            elif event_type == 'shot':
                if process_shot(conn, event, game_id, season_id, home_team_id, away_team_id):
                    total_processed += 1

            elif event_type == 'blocked_shot':
                if process_blocked_shot(conn, event, game_id, season_id, home_team_id, away_team_id):
                    total_processed += 1

            elif event_type == 'goal':
                if process_goal(conn, event, game_id, season_id, home_team_id, away_team_id):
                    total_processed += 1

            elif event_type == 'penalty':
                if process_penalty(conn, event, game_id, season_id, home_team_id, away_team_id):
                    total_processed += 1

            elif event_type == 'shootout':
                if process_shootout(conn, event, game_id, season_id, home_team_id, away_team_id):
                    total_processed += 1

        except Exception as e:
            logger.error(f"Error processing {event_type} event in game {game_id}: {e}")
            # Continue processing other events

    conn.commit()
    logger.info(f"Processed {total_processed} events for game {game_id}")
    return total_processed


def get_game_teams(conn: sqlite3.Connection, game_id: int) -> Tuple[Optional[int], Optional[int]]:
    """
    Get the home and away team IDs for a game.

    Args:
        conn: Database connection
        game_id: Game ID

    Returns:
        Tuple of (home_team_id, away_team_id)
    """
    cursor = conn.cursor()
    cursor.execute(
        "SELECT home_team, visiting_team FROM games WHERE id = ?",
        (game_id,)
    )
    result = cursor.fetchone()

    if result:
        return result[0], result[1]
    return None, None


def process_goalie_change(conn: sqlite3.Connection, event: Dict[str, Any],
                          game_id: int, season_id: int,
                          home_team_id: int, away_team_id: int) -> bool:
    """
    Process a goalie change event and store it in the database.

    Args:
        conn: Database connection
        event: Goalie change event data
        game_id: Game ID
        season_id: Season ID
        home_team_id: Home team ID
        away_team_id: Away team ID

    Returns:
        True if processed successfully, False otherwise
    """
    cursor = conn.cursor()

    # Generate a unique ID for this event
    event_id = f"{game_id}_goalie_{event.get('period_id', '')}_" \
               f"{event.get('time', '').replace(':', '_')}_{event.get('team_code', '')}"

    # Extract data from the event
    period = int(event.get('period_id', 0))
    time = event.get('time', '')
    seconds = int(event.get('s', 0))
    team_id = int(event.get('team_id', 0))
    opponent_team_id = away_team_id if team_id == home_team_id else home_team_id

    # Get goalie IDs, handle possible None values
    goalie_in_id = event.get('goalie_in_id')
    goalie_out_id = event.get('goalie_out_id')

    # Convert 'null' strings to None
    if goalie_in_id == 'null' or not goalie_in_id:
        goalie_in_id = None

    if goalie_out_id == 'null' or not goalie_out_id:
        goalie_out_id = None

    try:
        # Check if this event already exists
        cursor.execute(
            "SELECT id FROM pbp_goalie_changes WHERE game_id = ? AND period = ? AND time = ? AND team_id = ?",
            (game_id, period, time, team_id)
        )
        exists = cursor.fetchone()

        if exists:
            # Update existing record
            query = """
            UPDATE pbp_goalie_changes
            SET goalie_in_id = ?, goalie_out_id = ?, seconds = ?
            WHERE id = ?
            """
            cursor.execute(query, (goalie_in_id, goalie_out_id, seconds, exists[0]))
        else:
            # Insert the goalie change
            query = """
            INSERT INTO pbp_goalie_changes (
                id, game_id, season_id, period, time, seconds,
                team_id, opponent_team_id, goalie_in_id, goalie_out_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            cursor.execute(query, (
                event_id, game_id, season_id, period, time, seconds,
                team_id, opponent_team_id, goalie_in_id, goalie_out_id
            ))

        return True

    except sqlite3.Error as e:
        logger.error(f"Database error processing goalie change: {e}")
        return False


def process_faceoff(conn: sqlite3.Connection, event: Dict[str, Any],
                    game_id: int, season_id: int,
                    home_team_id: int, away_team_id: int) -> bool:
    """
    Process a faceoff event and store it in the database.

    Args:
        conn: Database connection
        event: Faceoff event data
        game_id: Game ID
        season_id: Season ID
        home_team_id: Home team ID
        away_team_id: Away team ID

    Returns:
        True if processed successfully, False otherwise
    """
    cursor = conn.cursor()

    # Use the event ID from the data or generate a unique ID
    event_id = f"{game_id}_faceoff_{event.get('period', '')}_{event.get('time_formatted', '').replace(':', '_')}"

    # Extract data from the event
    period = int(event.get('period', 0))
    time = event.get('time', '')
    time_formatted = event.get('time_formatted', '')
    seconds = int(event.get('s', 0))

    home_player_id = int(event.get('home_player_id', 0))
    visitor_player_id = int(event.get('visitor_player_id', 0))

    home_win = event.get('home_win') == '1'

    # Determine the winning team
    win_team_id = int(event.get('win_team_id', 0))
    opponent_team_id = away_team_id if win_team_id == home_team_id else home_team_id

    # Location data
    x_location = int(event.get('x_location', 0))
    y_location = int(event.get('y_location', 0))
    location_id = int(event.get('location_id', 0))

    try:
        # Check if this event already exists
        cursor.execute(
            "SELECT id FROM pbp_faceoffs WHERE game_id = ? AND period = ? AND time = ? AND home_player_id = ? AND visitor_player_id = ?",
            (game_id, period, time, home_player_id, visitor_player_id)
        )
        exists = cursor.fetchone()

        if exists:
            # Update existing record
            query = """
            UPDATE pbp_faceoffs
            SET time_formatted = ?, seconds = ?, home_win = ?, win_team_id = ?, opponent_team_id = ?,
                x_location = ?, y_location = ?, location_id = ?
            WHERE id = ?
            """
            cursor.execute(query, (
                time_formatted, seconds, home_win, win_team_id, opponent_team_id,
                x_location, y_location, location_id, exists[0]
            ))
        else:
            # Insert the faceoff
            query = """
            INSERT INTO pbp_faceoffs (
                id, game_id, season_id, period, time, time_formatted, seconds,
                home_player_id, visitor_player_id, home_win, win_team_id, opponent_team_id,
                x_location, y_location, location_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            cursor.execute(query, (
                event_id, game_id, season_id, period, time, time_formatted, seconds,
                home_player_id, visitor_player_id, home_win, win_team_id, opponent_team_id,
                x_location, y_location, location_id
            ))

        return True

    except sqlite3.Error as e:
        logger.error(f"Database error processing faceoff: {e}")
        return False


def process_hit(conn: sqlite3.Connection, event: Dict[str, Any],
                game_id: int, season_id: int,
                home_team_id: int, away_team_id: int) -> bool:
    """
    Process a hit event and store it in the database.

    Args:
        conn: Database connection
        event: Hit event data
        game_id: Game ID
        season_id: Season ID
        home_team_id: Home team ID
        away_team_id: Away team ID

    Returns:
        True if processed successfully, False otherwise
    """
    cursor = conn.cursor()

    # Use the event ID from the data or generate a unique ID
    event_id = f"{game_id}_hit_{event.get('id', '')}"

    # Extract data from the event
    period = int(event.get('period', 0))
    time = event.get('time', '')
    time_formatted = event.get('time_formatted', '')
    seconds = int(event.get('s', 0))

    player_id = int(event.get('player_id', 0))
    team_id = int(event.get('team_id', 0))
    opponent_team_id = away_team_id if team_id == home_team_id else home_team_id

    home = event.get('home') == '1'

    # Location data
    x_location = int(event.get('x_location', 0))
    y_location = int(event.get('y_location', 0))
    hit_type = int(event.get('hit_type', 0))

    try:
        # Check if this event already exists
        cursor.execute(
            "SELECT id FROM pbp_hits WHERE game_id = ? AND id = ?",
            (game_id, event_id)
        )
        exists = cursor.fetchone()

        if exists:
            # Update existing record
            query = """
            UPDATE pbp_hits
            SET period = ?, time = ?, time_formatted = ?, seconds = ?,
                player_id = ?, team_id = ?, opponent_team_id = ?, home = ?,
                x_location = ?, y_location = ?, hit_type = ?
            WHERE id = ?
            """
            cursor.execute(query, (
                period, time, time_formatted, seconds,
                player_id, team_id, opponent_team_id, home,
                x_location, y_location, hit_type, exists[0]
            ))
        else:
            # Insert the hit
            query = """
            INSERT INTO pbp_hits (
                id, game_id, season_id, period, time, time_formatted, seconds,
                player_id, team_id, opponent_team_id, home, 
                x_location, y_location, hit_type
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            cursor.execute(query, (
                event_id, game_id, season_id, period, time, time_formatted, seconds,
                player_id, team_id, opponent_team_id, home,
                x_location, y_location, hit_type
            ))

        return True

    except sqlite3.Error as e:
        logger.error(f"Database error processing hit: {e}")
        return False


def process_shot(conn: sqlite3.Connection, event: Dict[str, Any],
                 game_id: int, season_id: int,
                 home_team_id: int, away_team_id: int) -> bool:
    """
    Process a shot event and store it in the database.

    Args:
        conn: Database connection
        event: Shot event data
        game_id: Game ID
        season_id: Season ID
        home_team_id: Home team ID
        away_team_id: Away team ID

    Returns:
        True if processed successfully, False otherwise
    """
    cursor = conn.cursor()

    # Use the event ID from the data or generate a unique ID
    event_id = f"{game_id}_shot_{event.get('id', '')}"

    # Extract data from the event
    player_id = int(event.get('player_id', 0))
    goalie_id = int(event.get('goalie_id', 0)) if event.get('goalie_id') else None

    team_id = int(event.get('player_team_id', event.get('team_id', 0)))
    opponent_team_id = away_team_id if team_id == home_team_id else home_team_id

    home = event.get('home') == '1'

    period = int(event.get('period_id', 0))
    time = event.get('time', '')
    time_formatted = event.get('time_formatted', '')
    seconds = int(event.get('s', 0))

    # Location and shot details
    x_location = int(event.get('x_location', 0))
    y_location = int(event.get('y_location', 0))

    shot_type = int(event.get('shot_type', 0))
    shot_type_description = event.get('shot_type_description', '')

    quality = int(event.get('quality', 0))
    shot_quality_description = event.get('shot_quality_description', '')

    game_goal_id = event.get('game_goal_id', '')

    try:
        # Check if this event already exists
        cursor.execute(
            "SELECT id FROM pbp_shots WHERE game_id = ? AND id = ?",
            (game_id, event_id)
        )
        exists = cursor.fetchone()

        if exists:
            # Update existing record
            query = """
            UPDATE pbp_shots
            SET player_id = ?, goalie_id = ?, team_id = ?, opponent_team_id = ?,
                home = ?, period = ?, time = ?, time_formatted = ?, seconds = ?,
                x_location = ?, y_location = ?, shot_type = ?, shot_type_description = ?,
                quality = ?, shot_quality_description = ?, game_goal_id = ?
            WHERE id = ?
            """
            cursor.execute(query, (
                player_id, goalie_id, team_id, opponent_team_id,
                home, period, time, time_formatted, seconds,
                x_location, y_location, shot_type, shot_type_description,
                quality, shot_quality_description, game_goal_id, exists[0]
            ))
        else:
            # Insert the shot
            query = """
            INSERT INTO pbp_shots (
                id, game_id, season_id, player_id, goalie_id, team_id, opponent_team_id,
                home, period, time, time_formatted, seconds,
                x_location, y_location, shot_type, shot_type_description,
                quality, shot_quality_description, game_goal_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            cursor.execute(query, (
                event_id, game_id, season_id, player_id, goalie_id, team_id, opponent_team_id,
                home, period, time, time_formatted, seconds,
                x_location, y_location, shot_type, shot_type_description,
                quality, shot_quality_description, game_goal_id
            ))

        return True

    except sqlite3.Error as e:
        logger.error(f"Database error processing shot: {e}")
        return False


def process_blocked_shot(conn: sqlite3.Connection, event: Dict[str, Any],
                         game_id: int, season_id: int,
                         home_team_id: int, away_team_id: int) -> bool:
    """
    Process a blocked shot event and store it in the database.

    Args:
        conn: Database connection
        event: Blocked shot event data
        game_id: Game ID
        season_id: Season ID
        home_team_id: Home team ID
        away_team_id: Away team ID

    Returns:
        True if processed successfully, False otherwise
    """
    cursor = conn.cursor()

    # Use the event ID from the data or generate a unique ID
    event_id = f"{game_id}_blocked_{event.get('id', '')}"

    # Extract data from the event
    player_id = int(event.get('player_id', 0))
    goalie_id = int(event.get('goalie_id', 0)) if event.get('goalie_id') else None

    team_id = int(event.get('player_team_id', event.get('team_id', 0)))
    blocker_player_id = int(event.get('blocker_player_id', 0))
    blocker_team_id = int(event.get('blocker_team_id', 0))

    home = event.get('home') == '1'

    period = int(event.get('period', 0))
    time = event.get('time', '')
    time_formatted = event.get('time_formatted', '')
    seconds = int(event.get('seconds', event.get('s', 0)))

    # Location and shot details
    x_location = int(event.get('x_location', 0))
    y_location = int(event.get('y_location', 0))
    orientation = int(event.get('orientation', 0))

    shot_type = int(event.get('shot_type', 0))
    shot_type_description = event.get('shot_type_description', '')

    quality = int(event.get('quality', 0))
    shot_quality_description = event.get('shot_quality_description', '')

    try:
        # Check if this event already exists
        cursor.execute(
            "SELECT id FROM pbp_blocked_shots WHERE game_id = ? AND id = ?",
            (game_id, event_id)
        )
        exists = cursor.fetchone()

        if exists:
            # Update existing record
            query = """
            UPDATE pbp_blocked_shots
            SET player_id = ?, goalie_id = ?, team_id = ?, blocker_player_id = ?, blocker_team_id = ?,
                home = ?, period = ?, time = ?, time_formatted = ?, seconds = ?,
                x_location = ?, y_location = ?, orientation = ?, shot_type = ?, shot_type_description = ?,
                quality = ?, shot_quality_description = ?
            WHERE id = ?
            """
            cursor.execute(query, (
                player_id, goalie_id, team_id, blocker_player_id, blocker_team_id,
                home, period, time, time_formatted, seconds,
                x_location, y_location, orientation, shot_type, shot_type_description,
                quality, shot_quality_description, exists[0]
            ))
        else:
            # Insert the blocked shot
            query = """
            INSERT INTO pbp_blocked_shots (
                id, game_id, season_id, player_id, goalie_id, team_id,
                blocker_player_id, blocker_team_id, home, period, time, time_formatted, seconds,
                x_location, y_location, orientation, shot_type, shot_type_description,
                quality, shot_quality_description
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            cursor.execute(query, (
                event_id, game_id, season_id, player_id, goalie_id, team_id,
                blocker_player_id, blocker_team_id, home, period, time, time_formatted, seconds,
                x_location, y_location, orientation, shot_type, shot_type_description,
                quality, shot_quality_description
            ))

        return True

    except sqlite3.Error as e:
        logger.error(f"Database error processing blocked shot: {e}")
        return False


def process_goal(conn: sqlite3.Connection, event: Dict[str, Any],
                 game_id: int, season_id: int,
                 home_team_id: int, away_team_id: int) -> bool:
    """
    Process a goal event and store it in the database.

    Args:
        conn: Database connection
        event: Goal event data
        game_id: Game ID
        season_id: Season ID
        home_team_id: Home team ID
        away_team_id: Away team ID

    Returns:
        True if processed successfully, False otherwise
    """
    cursor = conn.cursor()

    # Use the event ID from the data or generate a unique ID
    event_id = f"{game_id}_goal_{event.get('id', '')}"

    # Extract data from the event
    team_id = int(event.get('team_id', 0))
    opponent_team_id = away_team_id if team_id == home_team_id else home_team_id

    home = event.get('home') == '1'

    goal_player_id = int(event.get('goal_player_id', 0))

    # Handle assists, which might be empty
    assist1_player_id = event.get('assist1_player_id')
    assist2_player_id = event.get('assist2_player_id')

    if assist1_player_id == '':
        assist1_player_id = None

    if assist2_player_id == '':
        assist2_player_id = None

    # Handle period format (removing suffixes like "st", "nd", etc.)
    period_str = event.get('period', '')
    if period_str:
        period_str = period_str.replace('st', '').replace('nd', '').replace('rd', '').replace('th', '')
        period = int(period_str) if period_str.isdigit() else 0
    else:
        period = 0

    time = event.get('time', '')
    time_formatted = event.get('time_formatted', '')
    seconds = int(event.get('s', 0))

    # Location data
    x_location = int(event.get('x_location', 0))
    y_location = int(event.get('y_location', 0))

    # Goal attributes
    location_set = event.get('location_set') == '1'
    power_play = event.get('power_play') == '1'
    empty_net = event.get('empty_net') == '1'
    penalty_shot = event.get('penalty_shot') == '1'
    short_handed = event.get('short_handed') == '1'
    insurance_goal = event.get('insurance_goal') == '1'
    game_winning = event.get('game_winning') == '1'
    game_tieing = event.get('game_tieing') == '1'

    scorer_goal_num = int(event.get('scorer_goal_num', 0))
    goal_type = event.get('goal_type', '')

    try:
        # Check if this goal already exists
        cursor.execute(
            "SELECT id FROM pbp_goals WHERE game_id = ? AND id = ?",
            (game_id, event_id)
        )
        exists = cursor.fetchone()

        if exists:
            # Update existing goal
            query = """
            UPDATE pbp_goals
            SET team_id = ?, opponent_team_id = ?, home = ?,
                goal_player_id = ?, assist1_player_id = ?, assist2_player_id = ?,
                period = ?, time = ?, time_formatted = ?, seconds = ?,
                x_location = ?, y_location = ?, location_set = ?, power_play = ?, empty_net = ?,
                penalty_shot = ?, short_handed = ?, insurance_goal = ?, game_winning = ?, game_tieing = ?,
                scorer_goal_num = ?, goal_type = ?
            WHERE id = ?
            """
            cursor.execute(query, (
                team_id, opponent_team_id, home,
                goal_player_id, assist1_player_id, assist2_player_id,
                period, time, time_formatted, seconds,
                x_location, y_location, location_set, power_play, empty_net,
                penalty_shot, short_handed, insurance_goal, game_winning, game_tieing,
                scorer_goal_num, goal_type, exists[0]
            ))

            # Delete existing plus/minus records for this goal
            cursor.execute("DELETE FROM pbp_goals_plus WHERE goal_id = ?", (event_id,))
            cursor.execute("DELETE FROM pbp_goals_minus WHERE goal_id = ?", (event_id,))
        else:
            # Insert the goal
            query = """
            INSERT INTO pbp_goals (
                id, game_id, season_id, team_id, opponent_team_id, home,
                goal_player_id, assist1_player_id, assist2_player_id,
                period, time, time_formatted, seconds,
                x_location, y_location, location_set, power_play, empty_net,
                penalty_shot, short_handed, insurance_goal, game_winning, game_tieing,
                scorer_goal_num, goal_type
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            cursor.execute(query, (
                event_id, game_id, season_id, team_id, opponent_team_id, home,
                goal_player_id, assist1_player_id, assist2_player_id,
                period, time, time_formatted, seconds,
                x_location, y_location, location_set, power_play, empty_net,
                penalty_shot, short_handed, insurance_goal, game_winning, game_tieing,
                scorer_goal_num, goal_type
            ))

        # Process players with plus ratings
        if 'plus' in event:
            process_goal_plus_players(conn, event_id, game_id, season_id, event.get('plus', []))

        # Process players with minus ratings
        if 'minus' in event:
            process_goal_minus_players(conn, event_id, game_id, season_id, event.get('minus', []))

        return True

    except sqlite3.Error as e:
        logger.error(f"Database error processing goal: {e}")
        return False


def process_goal_plus_players(conn: sqlite3.Connection, goal_id: str,
                              game_id: int, season_id: int,
                              plus_players: List[Dict[str, Any]]) -> None:
    """
    Process players who received a plus on a goal.

    Args:
        conn: Database connection
        goal_id: Goal event ID
        game_id: Game ID
        season_id: Season ID
        plus_players: List of players who received a plus
    """
    cursor = conn.cursor()

    for player in plus_players:
        try:
            player_id = int(player.get('player_id', 0))
            team_id = int(player.get('team_id', 0))
            jersey_number = int(player.get('jersey_number', 0))

            # Generate a unique ID for this plus record
            plus_id = f"{goal_id}_plus_{player_id}"

            # Check if this plus record already exists
            cursor.execute(
                "SELECT id FROM pbp_goals_plus WHERE goal_id = ? AND player_id = ?",
                (goal_id, player_id)
            )
            exists = cursor.fetchone()

            if not exists:
                query = """
                INSERT INTO pbp_goals_plus (
                    id, goal_id, game_id, season_id, team_id, player_id, jersey_number
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """

                cursor.execute(query, (
                    plus_id, goal_id, game_id, season_id, team_id, player_id, jersey_number
                ))

        except sqlite3.Error as e:
            logger.error(f"Database error processing goal plus player: {e}")


def process_goal_minus_players(conn: sqlite3.Connection, goal_id: str,
                               game_id: int, season_id: int,
                               minus_players: List[Dict[str, Any]]) -> None:
    """
    Process players who received a minus on a goal.

    Args:
        conn: Database connection
        goal_id: Goal event ID
        game_id: Game ID
        season_id: Season ID
        minus_players: List of players who received a minus
    """
    cursor = conn.cursor()

    for player in minus_players:
        try:
            player_id = int(player.get('player_id', 0))
            team_id = int(player.get('team_id', 0))
            jersey_number = int(player.get('jersey_number', 0))

            # Generate a unique ID for this minus record
            minus_id = f"{goal_id}_minus_{player_id}"

            # Check if this minus record already exists
            cursor.execute(
                "SELECT id FROM pbp_goals_minus WHERE goal_id = ? AND player_id = ?",
                (goal_id, player_id)
            )
            exists = cursor.fetchone()

            if not exists:
                query = """
                INSERT INTO pbp_goals_minus (
                    id, goal_id, game_id, season_id, team_id, player_id, jersey_number
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """

                cursor.execute(query, (
                    minus_id, goal_id, game_id, season_id, team_id, player_id, jersey_number
                ))

        except sqlite3.Error as e:
            logger.error(f"Database error processing goal minus player: {e}")


def process_penalty(conn: sqlite3.Connection, event: Dict[str, Any],
                    game_id: int, season_id: int,
                    home_team_id: int, away_team_id: int) -> bool:
    """
    Process a penalty event and store it in the database.

    Args:
        conn: Database connection
        event: Penalty event data
        game_id: Game ID
        season_id: Season ID
        home_team_id: Home team ID
        away_team_id: Away team ID

    Returns:
        True if processed successfully, False otherwise
    """
    cursor = conn.cursor()

    # Use the event ID from the data or generate a unique ID
    event_id = f"{game_id}_penalty_{event.get('id', '')}"

    # Extract data from the event
    player_id = int(event.get('player_id', 0))
    player_served = int(event.get('player_served', 0))

    team_id = int(event.get('team_id', 0))
    opponent_team_id = away_team_id if team_id == home_team_id else home_team_id

    home = event.get('home') == '1'

    # Handle period format (removing suffixes like "st", "nd", etc.)
    period_str = event.get('period', '')
    if period_str:
        period_str = period_str.replace('st', '').replace('nd', '').replace('rd', '').replace('th', '')
        period = int(period_str) if period_str.isdigit() else 0
    else:
        period = 0

    time_off_formatted = event.get('time_off_formatted', '')
    minutes = float(event.get('minutes', 0))
    minutes_formatted = event.get('minutes_formatted', '')

    # Penalty attributes
    bench = event.get('bench') == '1'
    penalty_shot = event.get('penalty_shot') == '1'
    pp = event.get('pp') == '1'

    offence = int(event.get('offence', 0))
    penalty_class_id = int(event.get('penalty_class_id', 0))
    penalty_class = event.get('penalty_class', '')
    lang_penalty_description = event.get('lang_penalty_description', '')

    try:
        # Check if this penalty already exists
        cursor.execute(
            "SELECT id FROM pbp_penalties WHERE game_id = ? AND id = ?",
            (game_id, event_id)
        )
        exists = cursor.fetchone()

        if exists:
            # Update existing penalty
            query = """
            UPDATE pbp_penalties
            SET player_id = ?, player_served = ?, team_id = ?, opponent_team_id = ?,
                home = ?, period = ?, time_off_formatted = ?, minutes = ?, minutes_formatted = ?,
                bench = ?, penalty_shot = ?, pp = ?, offence = ?, penalty_class_id = ?, penalty_class = ?,
                lang_penalty_description = ?
            WHERE id = ?
            """
            cursor.execute(query, (
                player_id, player_served, team_id, opponent_team_id,
                home, period, time_off_formatted, minutes, minutes_formatted,
                bench, penalty_shot, pp, offence, penalty_class_id, penalty_class,
                lang_penalty_description, exists[0]
            ))
        else:
            # Insert the penalty
            query = """
            INSERT INTO pbp_penalties (
                id, game_id, season_id, player_id, player_served, team_id, opponent_team_id,
                home, period, time_off_formatted, minutes, minutes_formatted,
                bench, penalty_shot, pp, offence, penalty_class_id, penalty_class,
                lang_penalty_description
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            cursor.execute(query, (
                event_id, game_id, season_id, player_id, player_served, team_id, opponent_team_id,
                home, period, time_off_formatted, minutes, minutes_formatted,
                bench, penalty_shot, pp, offence, penalty_class_id, penalty_class,
                lang_penalty_description
            ))

        return True

    except sqlite3.Error as e:
        logger.error(f"Database error processing penalty: {e}")
        return False


def process_shootout(conn: sqlite3.Connection, event: Dict[str, Any],
                     game_id: int, season_id: int,
                     home_team_id: int, away_team_id: int) -> bool:
    """
    Process a shootout event and store it in the database.

    Args:
        conn: Database connection
        event: Shootout event data
        game_id: Game ID
        season_id: Season ID
        home_team_id: Home team ID
        away_team_id: Away team ID

    Returns:
        True if processed successfully, False otherwise
    """
    cursor = conn.cursor()

    # Use the event ID from the data or generate a unique ID
    event_id = f"{game_id}_shootout_{event.get('id', '')}"

    # Extract data from the event
    player_id = int(event.get('player_id', 0))
    goalie_id = int(event.get('goalie_id', 0)) if event.get('goalie_id') else None

    team_id = int(event.get('team_id', 0))
    opponent_team_id = away_team_id if team_id == home_team_id else home_team_id

    home = event.get('home') == '1'

    shot_order = int(event.get('shot_order', 0))
    goal = event.get('goal') == '1'
    winning_goal = event.get('winning_goal') == '1'
    seconds = int(event.get('s', 0))

    try:
        # Check if this shootout already exists
        cursor.execute(
            "SELECT id FROM pbp_shootouts WHERE game_id = ? AND id = ?",
            (game_id, event_id)
        )
        exists = cursor.fetchone()

        if exists:
            # Update existing shootout
            query = """
            UPDATE pbp_shootouts
            SET player_id = ?, goalie_id = ?, team_id = ?, opponent_team_id = ?,
                home = ?, shot_order = ?, goal = ?, winning_goal = ?, seconds = ?
            WHERE id = ?
            """
            cursor.execute(query, (
                player_id, goalie_id, team_id, opponent_team_id,
                home, shot_order, goal, winning_goal, seconds, exists[0]
            ))
        else:
            # Insert the shootout
            query = """
            INSERT INTO pbp_shootouts (
                id, game_id, season_id, player_id, goalie_id, team_id, opponent_team_id,
                home, shot_order, goal, winning_goal, seconds
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            cursor.execute(query, (
                event_id, game_id, season_id, player_id, goalie_id, team_id, opponent_team_id,
                home, shot_order, goal, winning_goal, seconds
            ))

        return True

    except sqlite3.Error as e:
        logger.error(f"Database error processing shootout: {e}")
        return False


def get_games_without_play_by_play(conn: sqlite3.Connection) -> List[Tuple[int, int]]:
    """
    Get a list of game IDs that don't have play-by-play data yet.

    Args:
        conn: Database connection

    Returns:
        List of tuples containing (game_id, season_id)
    """
    cursor = conn.cursor()

    # Find games that don't have any records in the play-by-play tables
    query = """
    SELECT g.id, g.season_id
    FROM games g
    LEFT JOIN (
        SELECT DISTINCT game_id FROM pbp_faceoffs
        UNION SELECT DISTINCT game_id FROM pbp_shots
        UNION SELECT DISTINCT game_id FROM pbp_goals
        UNION SELECT DISTINCT game_id FROM pbp_hits
        UNION SELECT DISTINCT game_id FROM pbp_penalties
        UNION SELECT DISTINCT game_id FROM pbp_blocked_shots
        UNION SELECT DISTINCT game_id FROM pbp_goalie_changes
        UNION SELECT DISTINCT game_id FROM pbp_shootouts
    ) pbp ON g.id = pbp.game_id
    WHERE pbp.game_id IS NULL
    AND g.status = 'Final'
    ORDER BY g.id
    """

    cursor.execute(query)
    return cursor.fetchall()


def get_season_id_for_game(conn: sqlite3.Connection, game_id: int) -> Optional[int]:
    """
    Get the season ID for a specific game.

    Args:
        conn: Database connection
        game_id: Game ID

    Returns:
        Season ID or None if not found
    """
    cursor = conn.cursor()
    cursor.execute("SELECT season_id FROM games WHERE id = ?", (game_id,))
    result = cursor.fetchone()

    return result[0] if result else None


def update_play_by_play(db_path: str, game_id: Optional[int] = None, limit: Optional[int] = None) -> int:
    """
    Update play-by-play data for all games without it or a specific game.

    Args:
        db_path: Path to the SQLite database
        game_id: Optional specific game ID to update
        limit: Optional limit on the number of games to process

    Returns:
        Total number of events processed
    """
    conn = create_connection(db_path)
    total_processed = 0

    try:
        if game_id:
            # Process a specific game
            season_id = get_season_id_for_game(conn, game_id)
            if season_id:
                events_processed = process_game_play_by_play(conn, game_id, season_id)
                total_processed += events_processed
                logger.info(f"Processed game {game_id}: {events_processed} events")
            else:
                logger.error(f"Could not find season_id for game {game_id}")
        else:
            # Process all games without play-by-play data
            games_to_process = get_games_without_play_by_play(conn)
            logger.info(f"Found {len(games_to_process)} games without play-by-play data")

            if limit:
                games_to_process = games_to_process[:limit]

            for game_id, season_id in games_to_process:
                events_processed = process_game_play_by_play(conn, game_id, season_id)
                total_processed += events_processed
                logger.info(f"Processed game {game_id}: {events_processed} events")

    except Exception as e:
        logger.error(f"Error updating play-by-play data: {e}")
        conn.rollback()
        raise

    finally:
        conn.close()

    return total_processed


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Update play-by-play data
    from pwhl_scraper.config import DB_PATH
    import argparse

    parser = argparse.ArgumentParser(description='Update play-by-play data for PWHL games')
    parser.add_argument('--game-id', type=int, help='Specific game ID to update')
    parser.add_argument('--limit', type=int, help='Limit the number of games to process')

    args = parser.parse_args()

    update_play_by_play(DB_PATH, game_id=args.game_id, limit=args.limit)
