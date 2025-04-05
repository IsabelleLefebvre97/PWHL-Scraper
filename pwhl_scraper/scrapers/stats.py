"""
Statistics data scraper for PWHL Scraper.

This module fetches and updates statistics for teams, players, and games.
"""
import logging
import sqlite3
import time
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


def get_teams(conn: sqlite3.Connection) -> List[Tuple[int]]:
    """
    Get all team IDs from the database.

    Args:
        conn: Database connection

    Returns:
        List of team IDs
    """
    try:
        # Get teams
        teams_query = "SELECT id FROM teams ORDER BY id"
        teams = fetch_all(conn, teams_query)
        return teams
    except sqlite3.Error as e:
        logger.error(f"Error getting teams: {e}")
        return []


def get_players(conn: sqlite3.Connection) -> List[Tuple[int]]:
    """
    Get all player IDs from the database.

    Args:
        conn: Database connection

    Returns:
        List of player IDs
    """
    try:
        # Get players
        players_query = "SELECT id FROM players ORDER BY id"
        players = fetch_all(conn, players_query)
        return players
    except sqlite3.Error as e:
        logger.error(f"Error getting players: {e}")
        return []


def get_games(conn: sqlite3.Connection) -> List[Tuple[int]]:
    """
    Get all game IDs from the database.

    Args:
        conn: Database connection

    Returns:
        List of game IDs
    """
    try:
        # Get games
        games_query = "SELECT id FROM games ORDER BY id"
        games = fetch_all(conn, games_query)
        return games
    except sqlite3.Error as e:
        logger.error(f"Error getting games: {e}")
        return []


def fetch_team_season_stats(client: PWHLApiClient, season_id: int) -> List[Dict[str, Any]]:
    """
    Fetch team standings and statistics for a specific season.

    Args:
        client: PWHLApiClient instance
        season_id: Season ID

    Returns:
        List of team stats dictionaries
    """
    logger.info(f"Fetching team stats for season {season_id}")

    # For the standings endpoint we need to use the correct parameters
    endpoint = "index.php"
    params = {
        "feed": "modulekit",
        "view": "statviewtype",
        "stat": "conference",
        "type": "standings",
        "season_id": str(season_id)
    }

    stats_data = client.fetch_data(endpoint, params)

    if not stats_data or 'Statviewtype' not in stats_data.get('SiteKit', {}):
        logger.warning(f"No team stats found for season {season_id}")
        return []

    # Extract team stats - note that first element is usually a header
    stats = stats_data['SiteKit']['Statviewtype']

    # Filter out any non-team entries (like headers, separators, etc.)
    team_stats = [stat for stat in stats if 'team_id' in stat]

    return team_stats


def update_season_stats_teams(conn: sqlite3.Connection, season_id: int, teams_stats: List[Dict[str, Any]]) -> int:
    """
    Update team season statistics in the database.

    Args:
        conn: Database connection
        season_id: Season ID
        teams_stats: List of team stats dictionaries

    Returns:
        Number of teams updated
    """
    logger.info(f"Updating team season stats for season {season_id}")

    updated_count = 0

    for team_stats in teams_stats:
        try:
            team_id = int(team_stats.get('team_id', 0))
            if not team_id:
                continue

            # Create a unique ID for this season-team stats record
            stats_id = f"{season_id}_{team_id}"

            # Extract division info
            try:
                division_id = int(team_stats.get('division_id', 0))
            except (ValueError, TypeError):
                division_id = None

            # Extract wins/losses/points info
            try:
                wins = int(team_stats.get('wins', 0))
                losses = int(team_stats.get('losses', 0))
                ties = int(team_stats.get('ties', 0))
                ot_losses = int(team_stats.get('ot_losses', 0))
                reg_ot_losses = int(team_stats.get('reg_ot_losses', 0))
                reg_losses = int(team_stats.get('reg_losses', 0))
                ot_wins = int(team_stats.get('ot_wins', 0))
                shootout_wins = int(team_stats.get('shootout_wins', 0))
                shootout_losses = int(team_stats.get('shootout_losses', 0))
                regulation_wins = int(team_stats.get('regulation_wins', 0))
                row = int(team_stats.get('row', 0))  # Regulation + Overtime Wins
                points = int(team_stats.get('points', 0))
            except (ValueError, TypeError) as e:
                logger.warning(f"Error parsing win/loss data for team {team_id}: {e}")
                wins = losses = ties = ot_losses = reg_ot_losses = reg_losses = 0
                ot_wins = shootout_wins = shootout_losses = regulation_wins = row = points = 0

            # Extract penalty info
            try:
                bench_minutes = int(team_stats.get('bench_minutes', 0))
                penalty_minutes = int(team_stats.get('penalty_minutes', 0))
            except (ValueError, TypeError):
                bench_minutes = penalty_minutes = 0

            # Extract goals info
            try:
                goals_for = int(team_stats.get('goals_for', 0))
                goals_against = int(team_stats.get('goals_against', 0))
                goals_diff = int(team_stats.get('goals_diff', 0))
            except (ValueError, TypeError):
                goals_for = goals_against = goals_diff = 0

            # Extract special teams info
            try:
                power_play_goals = int(team_stats.get('power_play_goals', 0))
                power_play_goals_against = int(team_stats.get('power_play_goals_against', 0))
                shootout_goals = int(team_stats.get('shootout_goals', 0))
                shootout_goals_against = int(team_stats.get('shootout_goals_against', 0))
                shootout_attempts = int(team_stats.get('shootout_attempts', 0))
                shootout_attempts_against = int(team_stats.get('shootout_attempts_against', 0))
                short_handed_goals_for = int(team_stats.get('short_handed_goals_for', 0))
                short_handed_goals_against = int(team_stats.get('short_handed_goals_against', 0))
            except (ValueError, TypeError):
                power_play_goals = power_play_goals_against = 0
                shootout_goals = shootout_goals_against = 0
                shootout_attempts = shootout_attempts_against = 0
                short_handed_goals_for = short_handed_goals_against = 0

            # Extract percentages
            try:
                percentage = float(team_stats.get('percentage', 0))
                percentage_full = float(team_stats.get('percentage_full', 0))
            except (ValueError, TypeError):
                percentage = percentage_full = 0.0

            # Extract games info
            try:
                shootout_games_played = int(team_stats.get('shootout_games_played', 0))
                games_played = int(team_stats.get('games_played', 0))
            except (ValueError, TypeError):
                shootout_games_played = games_played = 0

            # Extract more percentages and rates
            try:
                shootout_pct = float(team_stats.get('shootout_pct', 0))
                power_play_pct = float(team_stats.get('power_play_pct', 0))
                shootout_pct_goals_for = float(team_stats.get('shootout_pct_goals_for', 0))
                shootout_pct_goals_against = float(team_stats.get('shootout_pct_goals_against', 0))
                penalty_kill_pct = float(team_stats.get('penalty_kill_pct', 0))
                pim_pg = float(team_stats.get('pim_pg', 0))
            except (ValueError, TypeError):
                shootout_pct = power_play_pct = shootout_pct_goals_for = 0.0
                shootout_pct_goals_against = penalty_kill_pct = pim_pg = 0.0

            # Extract miscellaneous
            try:
                power_plays = int(team_stats.get('power_plays', 0))
                win_percentage = float(team_stats.get('win_percentage', 0))
                times_short_handed = int(team_stats.get('times_short_handed', 0))
            except (ValueError, TypeError):
                power_plays = 0
                win_percentage = 0.0
                times_short_handed = 0

            # Extract records
            shootout_record = team_stats.get('shootout_record', '')
            home_record = team_stats.get('home_record', '')
            visiting_record = team_stats.get('visiting_record', '')

            # Check if stats record exists in database
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM season_stats_teams WHERE id = ?", (stats_id,))
            exists = cursor.fetchone()

            try:
                if exists:
                    # Update existing stats
                    query = """
                    UPDATE season_stats_teams 
                    SET division_id = ?,
                        wins = ?, losses = ?, ties = ?, ot_losses = ?, reg_ot_losses = ?,
                        reg_losses = ?, ot_wins = ?, shootout_wins = ?, shootout_losses = ?,
                        regulation_wins = ?, row = ?, points = ?, bench_minutes = ?,
                        penalty_minutes = ?, goals_for = ?, goals_against = ?, goals_diff = ?,
                        power_play_goals = ?, power_play_goals_against = ?, shootout_goals = ?,
                        shootout_goals_against = ?, shootout_attempts = ?, shootout_attempts_against = ?,
                        short_handed_goals_for = ?, short_handed_goals_against = ?, percentage = ?,
                        percentage_full = ?, shootout_games_played = ?, games_played = ?,
                        shootout_pct = ?, power_play_pct = ?, shootout_pct_goals_for = ?,
                        shootout_pct_goals_against = ?, penalty_kill_pct = ?, pim_pg = ?,
                        power_plays = ?, win_percentage = ?, times_short_handed = ?,
                        shootout_record = ?, home_record = ?, visiting_record = ?
                    WHERE id = ?
                    """
                    cursor.execute(query, (
                        division_id,
                        wins, losses, ties, ot_losses, reg_ot_losses,
                        reg_losses, ot_wins, shootout_wins, shootout_losses,
                        regulation_wins, row, points, bench_minutes,
                        penalty_minutes, goals_for, goals_against, goals_diff,
                        power_play_goals, power_play_goals_against, shootout_goals,
                        shootout_goals_against, shootout_attempts, shootout_attempts_against,
                        short_handed_goals_for, short_handed_goals_against, percentage,
                        percentage_full, shootout_games_played, games_played,
                        shootout_pct, power_play_pct, shootout_pct_goals_for,
                        shootout_pct_goals_against, penalty_kill_pct, pim_pg,
                        power_plays, win_percentage, times_short_handed,
                        shootout_record, home_record, visiting_record,
                        stats_id
                    ))
                    logger.info(f"Updated team season stats for team {team_id}, season {season_id}")
                else:
                    # Insert new stats
                    query = """
                    INSERT INTO season_stats_teams (
                        id, season_id, team_id, division_id,
                        wins, losses, ties, ot_losses, reg_ot_losses, reg_losses, ot_wins,
                        shootout_wins, shootout_losses, regulation_wins, row, points,
                        bench_minutes, penalty_minutes, goals_for, goals_against, goals_diff,
                        power_play_goals, power_play_goals_against, shootout_goals,
                        shootout_goals_against, shootout_attempts, shootout_attempts_against,
                        short_handed_goals_for, short_handed_goals_against, percentage,
                        percentage_full, shootout_games_played, games_played, shootout_pct,
                        power_play_pct, shootout_pct_goals_for, shootout_pct_goals_against,
                        penalty_kill_pct, pim_pg, power_plays, win_percentage, times_short_handed,
                        shootout_record, home_record, visiting_record
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                               ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                               ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """
                    cursor.execute(query, (
                        stats_id, season_id, team_id, division_id,
                        wins, losses, ties, ot_losses, reg_ot_losses, reg_losses, ot_wins,
                        shootout_wins, shootout_losses, regulation_wins, row, points,
                        bench_minutes, penalty_minutes, goals_for, goals_against, goals_diff,
                        power_play_goals, power_play_goals_against, shootout_goals,
                        shootout_goals_against, shootout_attempts, shootout_attempts_against,
                        short_handed_goals_for, short_handed_goals_against, percentage,
                        percentage_full, shootout_games_played, games_played, shootout_pct,
                        power_play_pct, shootout_pct_goals_for, shootout_pct_goals_against,
                        penalty_kill_pct, pim_pg, power_plays, win_percentage, times_short_handed,
                        shootout_record, home_record, visiting_record
                    ))
                    logger.info(f"Inserted new team season stats for team {team_id}, season {season_id}")

                updated_count += 1

            except sqlite3.Error as e:
                logger.error(f"Error updating team season stats for team {team_id}, season {season_id}: {e}")
                conn.rollback()

        except Exception as e:
            logger.error(f"Error processing team stats: {e}")
            continue

    conn.commit()
    logger.info(f"Updated {updated_count} team season stats records for season {season_id}")
    return updated_count


def fetch_player_season_stats(client: PWHLApiClient, player_id: int) -> Optional[Dict[str, Any]]:
    """
    Fetch season statistics for a specific player.

    Args:
        client: PWHLApiClient instance
        player_id: Player ID

    Returns:
        Player stats dictionary or None if request fails
    """
    logger.info(f"Fetching season stats for player {player_id}")

    # Get player stats
    player_stats = client.fetch_player_season_stats(player_id)

    if not player_stats or 'Player' not in player_stats.get('SiteKit', {}):
        logger.warning(f"No season stats found for player {player_id}")
        return None

    return player_stats['SiteKit']['Player']


def update_season_stats_skaters(conn: sqlite3.Connection, player_id: int, season_stats: Dict[str, Any]) -> int:
    """
    Update skater season statistics in the database.

    Args:
        conn: Database connection
        player_id: Player ID
        season_stats: Dictionary of player season stats

    Returns:
        Number of season stats records updated
    """
    logger.info(f"Updating season stats for skater {player_id}")

    updated_count = 0

    # Get season stats for regular, exhibition, and playoff seasons
    all_stats_raw = [season_stats.get(key, {}) for key in ['regular', 'exhibition', 'playoff']]

    # Normalize into a flat list of stats dictionaries
    all_stats = []
    for s in all_stats_raw:
        if isinstance(s, list):
            all_stats.extend(s)
        elif isinstance(s, dict):
            all_stats.append(s)
        else:
            logger.warning("Unexpected type for season stats, skipping")

    # Process each season
    for stats in all_stats:
        try:
            # Skip "Total" entries
            if stats.get('shortname') == 'Total':
                continue

            # Extract season ID
            try:
                season_id = int(stats.get('season_id', 0))
                if not season_id:
                    continue
            except (ValueError, TypeError):
                continue

            # Create a unique ID for this season-player stats record
            stats_id = f"{season_id}_{player_id}"

            # Extract team info
            try:
                team_id = int(stats.get('team_id', 0))
            except (ValueError, TypeError):
                team_id = None

            # Extract jersey number
            try:
                jersey_number = int(stats.get('jersey_number', 0))
            except (ValueError, TypeError):
                jersey_number = None

            # Extract handedness
            shoots = stats.get('shoots', '')

            # Extract basic game stats
            try:
                games_played = int(stats.get('games_played', 0))
                game_winning_goals = int(stats.get('game_winning_goals', 0))
                game_tieing_goals = int(stats.get('game_tieing_goals', 0))
                first_goals = int(stats.get('first_goals', 0))
                insurance_goals = int(stats.get('insurance_goals', 0))
                unassisted_goals = int(stats.get('unassisted_goals', 0))
                empty_net_goals = int(stats.get('empty_net_goals', 0))
                overtime_goals = int(stats.get('overtime_goals', 0))
            except (ValueError, TypeError):
                games_played = game_winning_goals = game_tieing_goals = 0
                first_goals = insurance_goals = unassisted_goals = 0
                empty_net_goals = overtime_goals = 0

            # Extract ice time
            try:
                ice_time = int(stats.get('ice_time', 0))
                ice_time_avg = float(ice_time / games_played) if games_played > 0 else 0.0
                ice_time_minutes_seconds = stats.get('ice_time_minutes_seconds', '')
            except (ValueError, TypeError):
                ice_time = 0
                ice_time_avg = 0.0
                ice_time_minutes_seconds = ''

            # Extract offensive stats
            try:
                goals = int(stats.get('goals', 0))
                assists = int(stats.get('assists', 0))
                points = int(stats.get('points', 0))
                points_per_game = float(stats.get('points_per_game', 0))
                plus_minus = int(stats.get('plus_minus', 0))
                shots = int(stats.get('shots', 0))
                shooting_percentage = float(stats.get('shooting_percentage', 0))
            except (ValueError, TypeError):
                goals = assists = points = plus_minus = shots = 0
                points_per_game = shooting_percentage = 0.0

            # Extract defensive stats
            try:
                hits = int(stats.get('hits', 0))
                shots_blocked_by_player = int(stats.get('shots_blocked_by_player', 0))
            except (ValueError, TypeError):
                hits = shots_blocked_by_player = 0

            # Extract penalty stats
            try:
                penalty_minutes = int(stats.get('penalty_minutes', 0))
                penalty_minutes_per_game = float(stats.get('penalty_minutes_per_game', 0))
                minor_penalties = int(stats.get('minor_penalties', 0))
                major_penalties = int(stats.get('major_penalties', 0))
            except (ValueError, TypeError):
                penalty_minutes = minor_penalties = major_penalties = 0
                penalty_minutes_per_game = 0.0

            # Extract special teams stats
            try:
                power_play_goals = int(stats.get('power_play_goals', 0))
                power_play_assists = int(stats.get('power_play_assists', 0))
                power_play_points = int(stats.get('power_play_points', 0))
                short_handed_goals = int(stats.get('short_handed_goals', 0))
                short_handed_assists = int(stats.get('short_handed_assists', 0))
                short_handed_points = int(stats.get('short_handed_points', 0))
            except (ValueError, TypeError):
                power_play_goals = power_play_assists = power_play_points = 0
                short_handed_goals = short_handed_assists = short_handed_points = 0

            # Extract shootout stats
            try:
                shootout_goals = int(stats.get('shootout_goals', 0))
                shootout_attempts = int(stats.get('shootout_attempts', 0))
                shootout_winning_goals = int(stats.get('shootout_winning_goals', 0))
                shootout_games_played = int(stats.get('shootout_games_played', 0))
                shootout_percentage = float(stats.get('shootout_percentage', 0))
            except (ValueError, TypeError):
                shootout_goals = shootout_attempts = shootout_winning_goals = 0
                shootout_games_played = 0
                shootout_percentage = 0.0

            # Extract faceoff stats
            try:
                faceoff_attempts = int(stats.get('faceoff_attempts', 0))
                faceoff_wins = int(stats.get('faceoff_wins', 0))
                faceoff_pct = float(stats.get('faceoff_pct', 0))
                faceoff_wa = stats.get('faceoff_wa', '')
            except (ValueError, TypeError):
                faceoff_attempts = faceoff_wins = 0
                faceoff_pct = 0.0
                faceoff_wa = ''

            # Extract shots on goal
            try:
                shots_on = int(stats.get('shots_on', 0))
            except (ValueError, TypeError):
                shots_on = 0

            # Check if stats record exists in database
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM season_stats_skaters WHERE id = ?", (stats_id,))
            exists = cursor.fetchone()

            try:
                if exists:
                    # Update existing stats
                    query = """
                    UPDATE season_stats_skaters 
                    SET team_id = ?, jersey_number = ?, shoots = ?, games_played = ?,
                        game_winning_goals = ?, game_tieing_goals = ?, first_goals = ?,
                        insurance_goals = ?, unassisted_goals = ?, empty_net_goals = ?,
                        overtime_goals = ?, ice_time = ?, ice_time_avg = ?,
                        ice_time_minutes_seconds = ?, goals = ?, assists = ?, points = ?,
                        points_per_game = ?, plus_minus = ?, shots = ?, shooting_percentage = ?,
                        hits = ?, shots_blocked_by_player = ?, penalty_minutes = ?,
                        penalty_minutes_per_game = ?, minor_penalties = ?, major_penalties = ?,
                        power_play_goals = ?, power_play_assists = ?, power_play_points = ?,
                        short_handed_goals = ?, short_handed_assists = ?, short_handed_points = ?,
                        shootout_goals = ?, shootout_attempts = ?, shootout_winning_goals = ?,
                        shootout_games_played = ?, shootout_percentage = ?, faceoff_attempts = ?,
                        faceoff_wins = ?, faceoff_pct = ?, faceoff_wa = ?, shots_on = ?
                    WHERE id = ?
                    """
                    cursor.execute(query, (
                        team_id, jersey_number, shoots, games_played,
                        game_winning_goals, game_tieing_goals, first_goals,
                        insurance_goals, unassisted_goals, empty_net_goals,
                        overtime_goals, ice_time, ice_time_avg,
                        ice_time_minutes_seconds, goals, assists, points,
                        points_per_game, plus_minus, shots, shooting_percentage,
                        hits, shots_blocked_by_player, penalty_minutes,
                        penalty_minutes_per_game, minor_penalties, major_penalties,
                        power_play_goals, power_play_assists, power_play_points,
                        short_handed_goals, short_handed_assists, short_handed_points,
                        shootout_goals, shootout_attempts, shootout_winning_goals,
                        shootout_games_played, shootout_percentage, faceoff_attempts,
                        faceoff_wins, faceoff_pct, faceoff_wa, shots_on,
                        stats_id
                    ))
                    logger.info(f"Updated skater season stats for player {player_id}, season {season_id}")
                else:
                    # Insert new stats
                    query = """
                    INSERT INTO season_stats_skaters (
                        id, player_id, season_id, team_id, jersey_number, shoots, games_played,
                        game_winning_goals, game_tieing_goals, first_goals, insurance_goals,
                        unassisted_goals, empty_net_goals, overtime_goals, ice_time, ice_time_avg,
                        ice_time_minutes_seconds, goals, assists, points, points_per_game,
                        plus_minus, shots, shooting_percentage, hits, shots_blocked_by_player,
                        penalty_minutes, penalty_minutes_per_game, minor_penalties, major_penalties,
                        power_play_goals, power_play_assists, power_play_points, short_handed_goals,
                        short_handed_assists, short_handed_points, shootout_goals, shootout_attempts,
                        shootout_winning_goals, shootout_games_played, shootout_percentage,
                        faceoff_attempts, faceoff_wins, faceoff_pct, faceoff_wa, shots_on
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                              ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                              ?, ?, ?, ?, ?)
                    """
                    cursor.execute(query, (
                        stats_id, player_id, season_id, team_id, jersey_number, shoots, games_played,
                        game_winning_goals, game_tieing_goals, first_goals, insurance_goals,
                        unassisted_goals, empty_net_goals, overtime_goals, ice_time, ice_time_avg,
                        ice_time_minutes_seconds, goals, assists, points, points_per_game,
                        plus_minus, shots, shooting_percentage, hits, shots_blocked_by_player,
                        penalty_minutes, penalty_minutes_per_game, minor_penalties, major_penalties,
                        power_play_goals, power_play_assists, power_play_points, short_handed_goals,
                        short_handed_assists, short_handed_points, shootout_goals, shootout_attempts,
                        shootout_winning_goals, shootout_games_played, shootout_percentage,
                        faceoff_attempts, faceoff_wins, faceoff_pct, faceoff_wa, shots_on,
                    ))
                    logger.info(f"Inserted new skater season stats for player {player_id}, season {season_id}")

                updated_count += 1

            except sqlite3.Error as e:
                logger.error(f"Error updating skater season stats for player {player_id}, season {season_id}: {e}")
                # Don't rollback here to continue with other seasons

        except Exception as e:
            logger.error(f"Error processing skater season stats: {e}")
            continue

    conn.commit()
    logger.info(f"Updated {updated_count} skater season stats records for player {player_id}")
    return updated_count


def update_season_stats_goalies(conn: sqlite3.Connection, player_id: int, season_stats: Dict[str, Any]) -> int:
    """
    Update goalie season statistics in the database.

    Args:
        conn: Database connection
        player_id: Player ID
        season_stats: Dictionary of player season stats

    Returns:
        Number of season stats records updated
    """
    logger.info(f"Updating season stats for goalie {player_id}")

    updated_count = 0

    # Get season stats for regular, exhibition, and playoff seasons
    all_stats_raw = [season_stats.get(key, {}) for key in ['regular', 'exhibition', 'playoff']]

    # Normalize into a flat list of stats dictionaries
    all_stats = []
    for s in all_stats_raw:
        if isinstance(s, list):
            all_stats.extend(s)
        elif isinstance(s, dict):
            all_stats.append(s)
        else:
            logger.warning("Unexpected type for season stats, skipping")

    # Process each season
    for stats in all_stats:
        try:
            # Skip "Total" entries
            if stats.get('shortname') == 'Total':
                continue

            # Extract season ID
            try:
                season_id = int(stats.get('season_id', 0))
                if not season_id:
                    continue
            except (ValueError, TypeError):
                continue

            # Create a unique ID for this season-player stats record
            stats_id = f"{season_id}_{player_id}"

            # Extract team info
            try:
                team_id = int(stats.get('team_id', 0))
            except (ValueError, TypeError):
                team_id = None

            # Extract jersey number
            try:
                jersey_number = int(stats.get('jersey_number', 0))
            except (ValueError, TypeError):
                jersey_number = None

            # Extract handedness
            shoots = stats.get('shoots', '')
            catches = stats.get('catches', '')

            # Extract basic game stats
            try:
                games_played = int(stats.get('games_played', 0))
                has_games_played = games_played > 0
            except (ValueError, TypeError):
                games_played = 0
                has_games_played = False

            # Extract ice time
            try:
                ice_time = int(stats.get('ice_time', 0))
                ice_time_avg = float(ice_time / games_played) if games_played > 0 else 0.0
                minutes_played = stats.get('minutes_played', '')
                minutes_played_g = int(ice_time / 60) if ice_time > 0 else 0
                seconds_played = ice_time
            except (ValueError, TypeError):
                ice_time = 0
                ice_time_avg = 0.0
                minutes_played = ''
                minutes_played_g = 0
                seconds_played = 0

            # Extract save stats
            try:
                saves = int(stats.get('saves', 0))
                shots = int(stats.get('shots', 0))
                save_percentage = float(stats.get('save_percentage', 0))
                goals_against = int(stats.get('goals_against', 0))
                empty_net_goals_against = int(stats.get('empty_net_goals_against', 0))
                shutouts = int(stats.get('shutouts', 0))
            except (ValueError, TypeError):
                saves = shots = goals_against = empty_net_goals_against = shutouts = 0
                save_percentage = 0.0

            # Extract record stats
            try:
                wins = int(stats.get('wins', 0))
                losses = int(stats.get('losses', 0))
                ot_losses = int(stats.get('ot_losses', 0))
                total_losses = losses + ot_losses
                ot = int(stats.get('ot', 0))
                ties = int(stats.get('ties', 0))
            except (ValueError, TypeError):
                wins = losses = ot_losses = total_losses = ot = ties = 0

            # Extract shootout stats
            try:
                shootout_games_played = int(stats.get('shootout_games_played', 0))
                shootout_losses = int(stats.get('shootout_losses', 0))
                shootout_wins = int(stats.get('shootout_wins', 0))
                shootout_goals_against = int(stats.get('shootout_goals_against', 0))
                shootout_saves = int(stats.get('shootout_saves', 0))
                shootout_attempts = int(stats.get('shootout_attempts', 0))
                shootout_percentage = float(stats.get('shootout_percentage', 0))
            except (ValueError, TypeError):
                shootout_games_played = shootout_losses = shootout_wins = 0
                shootout_goals_against = shootout_saves = shootout_attempts = 0
                shootout_percentage = 0.0

            # Extract offensive stats (rare for goalies)
            try:
                goals = int(stats.get('goals', 0))
                assists = int(stats.get('assists', 0))
                points = int(stats.get('points', 0))
                penalty_minutes = int(stats.get('penalty_minutes', 0))
            except (ValueError, TypeError):
                goals = assists = points = penalty_minutes = 0

            # Extract advanced stats
            try:
                shots_against_average = shots / games_played if games_played > 0 else 0.0
                goals_against_average = float(stats.get('goals_against_average', 0))
            except (ValueError, TypeError):
                shots_against_average = goals_against_average = 0.0

            # Check if stats record exists in database
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM season_stats_goalies WHERE id = ?", (stats_id,))
            exists = cursor.fetchone()

            try:
                if exists:
                    # Update existing stats
                    query = """
                    UPDATE season_stats_goalies
                    SET team_id = ?, jersey_number = ?, shoots = ?, catches = ?, games_played = ?,
                        ice_time = ?, ice_time_avg = ?, has_games_played = ?, minutes_played = ?,
                        minutes_played_g = ?, seconds_played = ?, saves = ?, shots = ?,
                        save_percentage = ?, goals_against = ?, empty_net_goals_against = ?,
                        shutouts = ?, wins = ?, losses = ?, ot_losses = ?, total_losses = ?,
                        shootout_games_played = ?, shootout_losses = ?, shootout_wins = ?,
                        shootout_goals_against = ?, shootout_saves = ?, shootout_attempts = ?,
                        goals = ?, assists = ?, points = ?, penalty_minutes = ?,
                        shootout_percentage = ?, ot = ?, ties = ?, shots_against_average = ?,
                        goals_against_average = ?
                    WHERE id = ?
                    """
                    cursor.execute(query, (
                        team_id, jersey_number, shoots, catches, games_played,
                        ice_time, ice_time_avg, has_games_played, minutes_played,
                        minutes_played_g, seconds_played, saves, shots,
                        save_percentage, goals_against, empty_net_goals_against,
                        shutouts, wins, losses, ot_losses, total_losses,
                        shootout_games_played, shootout_losses, shootout_wins,
                        shootout_goals_against, shootout_saves, shootout_attempts,
                        goals, assists, points, penalty_minutes,
                        shootout_percentage, ot, ties, shots_against_average,
                        goals_against_average,
                        stats_id
                    ))
                    logger.info(f"Updated goalie season stats for player {player_id}, season {season_id}")
                else:
                    # Insert new stats
                    query = """
                    INSERT INTO season_stats_goalies (
                        id, player_id, season_id, team_id, jersey_number, shoots, catches,
                        games_played, ice_time, ice_time_avg, has_games_played, minutes_played,
                        minutes_played_g, seconds_played, saves, shots, save_percentage,
                        goals_against, empty_net_goals_against, shutouts, wins, losses,
                        ot_losses, total_losses, shootout_games_played, shootout_losses,
                        shootout_wins, shootout_goals_against, shootout_saves, shootout_attempts,
                        goals, assists, points, penalty_minutes, shootout_percentage, ot, ties,
                        shots_against_average, goals_against_average
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                              ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """
                    cursor.execute(query, (
                        stats_id, player_id, season_id, team_id, jersey_number, shoots, catches,
                        games_played, ice_time, ice_time_avg, has_games_played, minutes_played,
                        minutes_played_g, seconds_played, saves, shots, save_percentage,
                        goals_against, empty_net_goals_against, shutouts, wins, losses,
                        ot_losses, total_losses, shootout_games_played, shootout_losses,
                        shootout_wins, shootout_goals_against, shootout_saves, shootout_attempts,
                        goals, assists, points, penalty_minutes, shootout_percentage, ot, ties,
                        shots_against_average, goals_against_average,
                    ))
                    logger.info(f"Inserted new goalie season stats for player {player_id}, season {season_id}")

                updated_count += 1

            except sqlite3.Error as e:
                logger.error(f"Error updating goalie season stats for player {player_id}, season {season_id}: {e}")
                # Don't rollback here to continue with other seasons

        except Exception as e:
            logger.error(f"Error processing goalie season stats: {e}")
            continue

    conn.commit()
    logger.info(f"Updated {updated_count} goalie season stats records for player {player_id}")
    return updated_count


def fetch_game_stats(client: PWHLApiClient, game_id: int) -> Optional[Dict[str, Any]]:
    """
    Fetch detailed statistics for a specific game.

    Args:
        client: PWHLApiClient instance
        game_id: Game ID

    Returns:
        Game stats dictionary or None if request fails
    """
    logger.info(f"Fetching stats for game {game_id}")

    # For the game center endpoint we need to use the correct parameters
    endpoint = "index.php"
    params = {
        "feed": "gc",
        "game_id": str(game_id),
        "tab": "gamesummary"
    }

    game_data = client.fetch_data(endpoint, params)

    if not game_data or 'GC' not in game_data or 'Gamesummary' not in game_data['GC']:
        logger.warning(f"No stats found for game {game_id}")
        return None

    return game_data['GC']['Gamesummary']


def update_game_stats_teams(conn: sqlite3.Connection, game_id: int, game_stats: Dict[str, Any]) -> int:
    """
    Update team game statistics in the database.

    Args:
        conn: Database connection
        game_id: Game ID
        game_stats: Game stats dictionary

    Returns:
        Number of team stats records updated
    """
    logger.info(f"Updating team game stats for game {game_id}")

    updated_count = 0

    try:
        # Extract season ID
        try:
            season_id = int(game_stats['meta']['season_id'])
        except (KeyError, ValueError, TypeError):
            logger.warning(f"Could not determine season ID for game {game_id}")
            return 0

        # Extract home team stats
        try:
            home_team_id = int(game_stats['meta']['home_team'])
            home_goals = int(game_stats['meta']['home_goal_count'])
            home_shots = int(game_stats['shotsByPeriod']['home']['1']) + int(
                game_stats['shotsByPeriod']['home']['2']) + int(game_stats['shotsByPeriod']['home']['3'])
            home_pp_total = int(game_stats['powerPlayCount']['home'])
            home_pp_goals = int(game_stats['powerPlayGoals']['home'])
            home_fow = int(game_stats['totalFaceoffs']['home']['won'])
            home_hits = int(game_stats['totalHits']['home'])

            # Create a unique ID for home team game stats
            home_stats_id = f"{game_id}_home_{home_team_id}"

            # Check if home team stats record exists
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM game_stats_teams WHERE id = ?", (home_stats_id,))
            exists = cursor.fetchone()

            if exists:
                # Update existing home team stats
                query = """
                UPDATE game_stats_teams
                SET season_id = ?, goals = ?, shots_on_goal = ?, power_play_total = ?,
                    power_play_goals = ?, fow = ?, hits = ?
                WHERE id = ?
                """
                cursor.execute(query, (
                    season_id, home_goals, home_shots, home_pp_total,
                    home_pp_goals, home_fow, home_hits,
                    home_stats_id
                ))
                logger.info(f"Updated home team game stats for game {game_id}")
            else:
                # Insert new home team stats
                query = """
                INSERT INTO game_stats_teams (
                    id, game_id, team_id, season_id, goals, shots_on_goal,
                    power_play_total, power_play_goals, fow, hits
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                cursor.execute(query, (
                    home_stats_id, game_id, home_team_id, season_id, home_goals, home_shots,
                    home_pp_total, home_pp_goals, home_fow, home_hits
                ))
                logger.info(f"Inserted new home team game stats for game {game_id}")

            updated_count += 1

        except (KeyError, ValueError, TypeError) as e:
            logger.warning(f"Error processing home team stats for game {game_id}: {e}")

        # Extract visitor team stats
        try:
            visitor_team_id = int(game_stats['meta']['visiting_team'])
            visitor_goals = int(game_stats['meta']['visiting_goal_count'])
            visitor_shots = int(game_stats['shotsByPeriod']['visitor']['1']) + int(
                game_stats['shotsByPeriod']['visitor']['2']) + int(game_stats['shotsByPeriod']['visitor']['3'])
            visitor_pp_total = int(game_stats['powerPlayCount']['visitor'])
            visitor_pp_goals = int(game_stats['powerPlayGoals']['visitor'])
            visitor_fow = int(game_stats['totalFaceoffs']['visitor']['won'])
            visitor_hits = int(game_stats['totalHits']['visitor'])

            # Create a unique ID for visitor team game stats
            visitor_stats_id = f"{game_id}_visitor_{visitor_team_id}"

            # Check if visitor team stats record exists
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM game_stats_teams WHERE id = ?", (visitor_stats_id,))
            exists = cursor.fetchone()

            if exists:
                # Update existing visitor team stats
                query = """
                UPDATE game_stats_teams
                SET season_id = ?, goals = ?, shots_on_goal = ?, power_play_total = ?,
                    power_play_goals = ?, fow = ?, hits = ?
                WHERE id = ?
                """
                cursor.execute(query, (
                    season_id, visitor_goals, visitor_shots, visitor_pp_total,
                    visitor_pp_goals, visitor_fow, visitor_hits,
                    visitor_stats_id
                ))
                logger.info(f"Updated visitor team game stats for game {game_id}")
            else:
                # Insert new visitor team stats
                query = """
                INSERT INTO game_stats_teams (
                    id, game_id, team_id, season_id, goals, shots_on_goal,
                    power_play_total, power_play_goals, fow, hits
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                cursor.execute(query, (
                    visitor_stats_id, game_id, visitor_team_id, season_id, visitor_goals, visitor_shots,
                    visitor_pp_total, visitor_pp_goals, visitor_fow, visitor_hits
                ))
                logger.info(f"Inserted new visitor team game stats for game {game_id}")

            updated_count += 1

        except (KeyError, ValueError, TypeError) as e:
            logger.warning(f"Error processing visitor team stats for game {game_id}: {e}")

        conn.commit()

    except Exception as e:
        logger.error(f"Error updating team game stats for game {game_id}: {e}")
        conn.rollback()

    return updated_count


def update_game_stats_skaters(conn: sqlite3.Connection, game_id: int, game_stats: Dict[str, Any]) -> int:
    """
    Update skater game statistics in the database.

    Args:
        conn: Database connection
        game_id: Game ID
        game_stats: Game stats dictionary

    Returns:
        Number of skater stats records updated
    """
    logger.info(f"Updating skater game stats for game {game_id}")

    updated_count = 0

    try:
        # Extract season ID
        try:
            season_id = int(game_stats['meta']['season_id'])
        except (KeyError, ValueError, TypeError):
            logger.warning(f"Could not determine season ID for game {game_id}")
            return 0

        # Extract home team ID
        try:
            home_team_id = int(game_stats['meta']['home_team'])
        except (KeyError, ValueError, TypeError):
            logger.warning(f"Could not determine home team ID for game {game_id}")
            return 0

        # Extract visitor team ID
        try:
            visitor_team_id = int(game_stats['meta']['visiting_team'])
        except (KeyError, ValueError, TypeError):
            logger.warning(f"Could not determine visitor team ID for game {game_id}")
            return 0

        # Process home team skaters
        try:
            home_skaters = [player for player in game_stats['home_team_lineup']['players']
                            if player['position_str'] != 'G']

            for skater in home_skaters:
                try:
                    player_id = int(skater['player_id'])

                    # Create a unique ID for this skater game stats record
                    stats_id = f"{game_id}_{player_id}"

                    # Extract jersey number
                    try:
                        jersey_number = int(skater['jersey_number'])
                    except (ValueError, TypeError):
                        jersey_number = None

                    # Extract position and status
                    position = skater['position_str']
                    rookie = skater['rookie'] == '1'
                    start = skater['start'] == '1'
                    status = skater['status']

                    # Extract game stats
                    try:
                        goals = int(skater['goals'])
                        assists = int(skater['assists'])
                        try:
                            plusminus = int(str(skater.get('plusminus', '')).replace('+', ''))
                        except (ValueError, TypeError):
                            plusminus = 0
                        pim = int(skater['pim'])
                    except (ValueError, TypeError):
                        goals = assists = plusminus = pim = 0

                    # Extract faceoff stats
                    try:
                        faceoff_wins = int(skater['faceoff_wins'])
                        faceoff_attempts = int(skater['faceoff_attempts'])
                    except (ValueError, TypeError):
                        faceoff_wins = faceoff_attempts = 0

                    # Extract other stats
                    try:
                        hits = int(skater['hits'])
                        shots = int(skater['shots'])
                        shots_on = int(skater['shots_on'])
                        shots_blocked_by_player = int(skater['shots_blocked_by_player'])
                        shots_blocked = int(skater['shots_blocked'])
                    except (ValueError, TypeError):
                        hits = shots = shots_on = shots_blocked_by_player = shots_blocked = 0

                    # Extract special teams and game-winning goal info
                    try:
                        power_play_goals = int(skater.get('power_play_goals', 0))
                        short_handed_goals = int(skater.get('short_handed_goals', 0))
                        game_winning_goal = skater.get('game_winning_goal', 0) == 1
                    except (ValueError, TypeError):
                        power_play_goals = short_handed_goals = 0
                        game_winning_goal = False

                    # Check if stats record exists in database
                    cursor = conn.cursor()
                    cursor.execute("SELECT id FROM game_stats_skaters WHERE id = ?", (stats_id,))
                    exists = cursor.fetchone()

                    if exists:
                        # Update existing stats
                        query = """
                        UPDATE game_stats_skaters
                        SET season_id = ?, team_id = ?, jersey_number = ?, position = ?,
                            rookie = ?, start = ?, status = ?, goals = ?, assists = ?,
                            plusminus = ?, pim = ?, faceoff_wins = ?, faceoff_attempts = ?,
                            hits = ?, shots = ?, shots_on = ?, shots_blocked_by_player = ?,
                            shots_blocked = ?, power_play_goals = ?, short_handed_goals = ?,
                            game_winning_goal = ?
                        WHERE id = ?
                        """
                        cursor.execute(query, (
                            season_id, home_team_id, jersey_number, position,
                            rookie, start, status, goals, assists,
                            plusminus, pim, faceoff_wins, faceoff_attempts,
                            hits, shots, shots_on, shots_blocked_by_player,
                            shots_blocked, power_play_goals, short_handed_goals,
                            game_winning_goal,
                            stats_id
                        ))
                        logger.info(f"Updated skater game stats for player {player_id} in game {game_id}")
                    else:
                        # Insert new stats
                        query = """
                        INSERT INTO game_stats_skaters (
                            id, game_id, player_id, team_id, season_id, jersey_number,
                            position, rookie, start, status, goals, assists, plusminus,
                            pim, faceoff_wins, faceoff_attempts, hits, shots, shots_on,
                            shots_blocked_by_player, shots_blocked, power_play_goals,
                            short_handed_goals, game_winning_goal
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """
                        cursor.execute(query, (
                            stats_id, game_id, player_id, home_team_id, season_id, jersey_number,
                            position, rookie, start, status, goals, assists, plusminus,
                            pim, faceoff_wins, faceoff_attempts, hits, shots, shots_on,
                            shots_blocked_by_player, shots_blocked, power_play_goals,
                            short_handed_goals, game_winning_goal
                        ))
                        logger.info(f"Inserted new skater game stats for player {player_id} in game {game_id}")

                    updated_count += 1

                except (KeyError, ValueError, TypeError) as e:
                    logger.warning(
                        f"Error processing home skater {skater.get('player_id')} stats for game {game_id}: {e}")
                    continue

        except (KeyError, TypeError) as e:
            logger.warning(f"Error processing home team skaters for game {game_id}: {e}")

        # Process visitor team skaters
        try:
            visitor_skaters = [player for player in game_stats['visitor_team_lineup']['players']
                               if player['position_str'] != 'G']

            for skater in visitor_skaters:
                try:
                    player_id = int(skater['player_id'])

                    # Create a unique ID for this skater game stats record
                    stats_id = f"{game_id}_{player_id}"

                    # Extract jersey number
                    try:
                        jersey_number = int(skater['jersey_number'])
                    except (ValueError, TypeError):
                        jersey_number = None

                    # Extract position and status
                    position = skater['position_str']
                    rookie = skater['rookie'] == '1'
                    start = skater['start'] == '1'
                    status = skater['status']

                    # Extract game stats
                    try:
                        goals = int(skater['goals'])
                        assists = int(skater['assists'])
                        try:
                            plusminus = int(str(skater.get('plusminus', '')).replace('+', ''))
                        except (ValueError, TypeError):
                            plusminus = 0
                        pim = int(skater['pim'])
                    except (ValueError, TypeError):
                        goals = assists = plusminus = pim = 0

                    # Extract faceoff stats
                    try:
                        faceoff_wins = int(skater['faceoff_wins'])
                        faceoff_attempts = int(skater['faceoff_attempts'])
                    except (ValueError, TypeError):
                        faceoff_wins = faceoff_attempts = 0

                    # Extract other stats
                    try:
                        hits = int(skater['hits'])
                        shots = int(skater['shots'])
                        shots_on = int(skater['shots_on'])
                        shots_blocked_by_player = int(skater['shots_blocked_by_player'])
                        shots_blocked = int(skater['shots_blocked'])
                    except (ValueError, TypeError):
                        hits = shots = shots_on = shots_blocked_by_player = shots_blocked = 0

                    # Extract special teams and game-winning goal info
                    try:
                        power_play_goals = int(skater.get('power_play_goals', 0))
                        short_handed_goals = int(skater.get('short_handed_goals', 0))
                        game_winning_goal = skater.get('game_winning_goal', 0) == 1
                    except (ValueError, TypeError):
                        power_play_goals = short_handed_goals = 0
                        game_winning_goal = False

                    # Check if stats record exists in database
                    cursor = conn.cursor()
                    cursor.execute("SELECT id FROM game_stats_skaters WHERE id = ?", (stats_id,))
                    exists = cursor.fetchone()

                    if exists:
                        # Update existing stats
                        query = """
                        UPDATE game_stats_skaters
                        SET season_id = ?, team_id = ?, jersey_number = ?, position = ?,
                            rookie = ?, start = ?, status = ?, goals = ?, assists = ?,
                            plusminus = ?, pim = ?, faceoff_wins = ?, faceoff_attempts = ?,
                            hits = ?, shots = ?, shots_on = ?, shots_blocked_by_player = ?,
                            shots_blocked = ?, power_play_goals = ?, short_handed_goals = ?,
                            game_winning_goal = ?
                        WHERE id = ?
                        """
                        cursor.execute(query, (
                            season_id, visitor_team_id, jersey_number, position,
                            rookie, start, status, goals, assists,
                            plusminus, pim, faceoff_wins, faceoff_attempts,
                            hits, shots, shots_on, shots_blocked_by_player,
                            shots_blocked, power_play_goals, short_handed_goals,
                            game_winning_goal,
                            stats_id
                        ))
                        logger.info(f"Updated skater game stats for player {player_id} in game {game_id}")
                    else:
                        # Insert new stats
                        query = """
                        INSERT INTO game_stats_skaters (
                            id, game_id, player_id, team_id, season_id, jersey_number,
                            position, rookie, start, status, goals, assists, plusminus,
                            pim, faceoff_wins, faceoff_attempts, hits, shots, shots_on,
                            shots_blocked_by_player, shots_blocked, power_play_goals,
                            short_handed_goals, game_winning_goal
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """
                        cursor.execute(query, (
                            stats_id, game_id, player_id, visitor_team_id, season_id, jersey_number,
                            position, rookie, start, status, goals, assists, plusminus,
                            pim, faceoff_wins, faceoff_attempts, hits, shots, shots_on,
                            shots_blocked_by_player, shots_blocked, power_play_goals,
                            short_handed_goals, game_winning_goal
                        ))
                        logger.info(f"Inserted new skater game stats for player {player_id} in game {game_id}")

                    updated_count += 1

                except (KeyError, ValueError, TypeError) as e:
                    logger.warning(
                        f"Error processing visitor skater {skater.get('player_id')} stats for game {game_id}: {e}")
                    continue

        except (KeyError, TypeError) as e:
            logger.warning(f"Error processing visitor team skaters for game {game_id}: {e}")

        conn.commit()

    except Exception as e:
        logger.error(f"Error updating skater game stats for game {game_id}: {e}")
        conn.rollback()

    return updated_count


def update_game_stats_goalies(conn: sqlite3.Connection, game_id: int, game_stats: Dict[str, Any]) -> int:
    """
    Update goalie game statistics in the database.

    Args:
        conn: Database connection
        game_id: Game ID
        game_stats: Game stats dictionary

    Returns:
        Number of goalie stats records updated
    """
    logger.info(f"Updating goalie game stats for game {game_id}")

    updated_count = 0

    try:
        # Extract season ID
        try:
            season_id = int(game_stats['meta']['season_id'])
        except (KeyError, ValueError, TypeError):
            logger.warning(f"Could not determine season ID for game {game_id}")
            return 0

        # Extract home team ID
        try:
            home_team_id = int(game_stats['meta']['home_team'])
        except (KeyError, ValueError, TypeError):
            logger.warning(f"Could not determine home team ID for game {game_id}")
            return 0

        # Extract visitor team ID
        try:
            visitor_team_id = int(game_stats['meta']['visiting_team'])
        except (KeyError, ValueError, TypeError):
            logger.warning(f"Could not determine visitor team ID for game {game_id}")
            return 0

        # Process home team goalies
        try:
            home_goalies = game_stats['home_team_lineup']['goalies']

            for goalie in home_goalies:
                try:
                    player_id = int(goalie['player_id'])

                    # Create a unique ID for this goalie game stats record
                    stats_id = f"{game_id}_{player_id}"

                    # Skip goalies with no ice time
                    if goalie['seconds'] == 0:
                        continue

                    # Extract jersey number
                    try:
                        jersey_number = int(goalie['jersey_number'])
                    except (ValueError, TypeError):
                        jersey_number = None

                    # Extract position and status
                    position = goalie['position_str']
                    rookie = goalie['rookie'] == '1'
                    start = goalie['start'] == '1'
                    status = goalie['status']

                    # Extract time stats
                    try:
                        seconds = int(goalie['seconds'])
                        time = goalie['time']
                    except (ValueError, TypeError):
                        seconds = 0
                        time = ''

                    # Extract goalie stats
                    try:
                        shots_against = int(goalie['shots_against'])
                        goals_against = int(goalie['goals_against'])
                        saves = int(goalie['saves'])
                    except (ValueError, TypeError):
                        shots_against = goals_against = saves = 0

                    # Extract other stats
                    try:
                        goals = int(goalie['goals'])
                        assists = int(goalie['assists'])
                        pim = int(goalie['pim'])
                        shots = int(goalie['shots'])
                    except (ValueError, TypeError):
                        goals = assists = pim = shots = 0

                    # Check if stats record exists in database
                    cursor = conn.cursor()
                    cursor.execute("SELECT id FROM game_stats_goalies WHERE id = ?", (stats_id,))
                    exists = cursor.fetchone()

                    if exists:
                        # Update existing stats
                        query = """
                        UPDATE game_stats_goalies
                        SET season_id = ?, team_id = ?, jersey_number = ?, position = ?,
                            rookie = ?, start = ?, status = ?, seconds = ?, time = ?,
                            shots_against = ?, goals_against = ?, saves = ?, goals = ?,
                            assists = ?, pim = ?, shots = ?
                        WHERE id = ?
                        """
                        cursor.execute(query, (
                            season_id, home_team_id, jersey_number, position,
                            rookie, start, status, seconds, time,
                            shots_against, goals_against, saves, goals,
                            assists, pim, shots,
                            stats_id
                        ))
                        logger.info(f"Updated goalie game stats for player {player_id} in game {game_id}")
                    else:
                        # Insert new stats
                        query = """
                        INSERT INTO game_stats_goalies (
                            id, game_id, player_id, team_id, season_id, jersey_number,
                            position, rookie, start, status, seconds, time,
                            shots_against, goals_against, saves, goals, assists, pim, shots
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """
                        cursor.execute(query, (
                            stats_id, game_id, player_id, home_team_id, season_id, jersey_number,
                            position, rookie, start, status, seconds, time,
                            shots_against, goals_against, saves, goals, assists, pim, shots
                        ))
                        logger.info(f"Inserted new goalie game stats for player {player_id} in game {game_id}")

                    updated_count += 1

                except (KeyError, ValueError, TypeError) as e:
                    logger.warning(
                        f"Error processing home goalie {goalie.get('player_id')} stats for game {game_id}: {e}")
                    continue

        except (KeyError, TypeError) as e:
            logger.warning(f"Error processing home team goalies for game {game_id}: {e}")

        # Process visitor team goalies
        try:
            visitor_goalies = game_stats['visitor_team_lineup']['goalies']

            for goalie in visitor_goalies:
                try:
                    player_id = int(goalie['player_id'])

                    # Create a unique ID for this goalie game stats record
                    stats_id = f"{game_id}_{player_id}"

                    # Skip goalies with no ice time
                    if goalie['seconds'] == 0:
                        continue

                    # Extract jersey number
                    try:
                        jersey_number = int(goalie['jersey_number'])
                    except (ValueError, TypeError):
                        jersey_number = None

                    # Extract position and status
                    position = goalie['position_str']
                    rookie = goalie['rookie'] == '1'
                    start = goalie['start'] == '1'
                    status = goalie['status']

                    # Extract time stats
                    try:
                        seconds = int(goalie['seconds'])
                        time = goalie['time']
                    except (ValueError, TypeError):
                        seconds = 0
                        time = ''

                    # Extract goalie stats
                    try:
                        shots_against = int(goalie['shots_against'])
                        goals_against = int(goalie['goals_against'])
                        saves = int(goalie['saves'])
                    except (ValueError, TypeError):
                        shots_against = goals_against = saves = 0

                    # Extract other stats
                    try:
                        goals = int(goalie['goals'])
                        assists = int(goalie['assists'])
                        pim = int(goalie['pim'])
                        shots = int(goalie['shots'])
                    except (ValueError, TypeError):
                        goals = assists = pim = shots = 0

                    # Check if stats record exists in database
                    cursor = conn.cursor()
                    cursor.execute("SELECT id FROM game_stats_goalies WHERE id = ?", (stats_id,))
                    exists = cursor.fetchone()

                    if exists:
                        # Update existing stats
                        query = """
                        UPDATE game_stats_goalies
                        SET season_id = ?, team_id = ?, jersey_number = ?, position = ?,
                            rookie = ?, start = ?, status = ?, seconds = ?, time = ?,
                            shots_against = ?, goals_against = ?, saves = ?, goals = ?,
                            assists = ?, pim = ?, shots = ?
                        WHERE id = ?
                        """
                        cursor.execute(query, (
                            season_id, visitor_team_id, jersey_number, position,
                            rookie, start, status, seconds, time,
                            shots_against, goals_against, saves, goals,
                            assists, pim, shots,
                            stats_id
                        ))
                        logger.info(f"Updated goalie game stats for player {player_id} in game {game_id}")
                    else:
                        # Insert new stats
                        query = """
                        INSERT INTO game_stats_goalies (
                            id, game_id, player_id, team_id, season_id, jersey_number,
                            position, rookie, start, status, seconds, time,
                            shots_against, goals_against, saves, goals, assists, pim, shots
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """
                        cursor.execute(query, (
                            stats_id, game_id, player_id, visitor_team_id, season_id, jersey_number,
                            position, rookie, start, status, seconds, time,
                            shots_against, goals_against, saves, goals, assists, pim, shots
                        ))
                        logger.info(f"Inserted new goalie game stats for player {player_id} in game {game_id}")

                    updated_count += 1

                except (KeyError, ValueError, TypeError) as e:
                    logger.warning(
                        f"Error processing visitor goalie {goalie.get('player_id')} stats for game {game_id}: {e}")
                    continue

        except (KeyError, TypeError) as e:
            logger.warning(f"Error processing visitor team goalies for game {game_id}: {e}")

        conn.commit()

    except Exception as e:
        logger.error(f"Error updating goalie game stats for game {game_id}: {e}")
        conn.rollback()

    return updated_count


def update_team_stats(db_path: str, season_id: Optional[int] = None) -> Union[int, None, Any]:
    """
    Update team statistics for all seasons or a specific season.

    Args:
        db_path: Path to the SQLite database
        season_id: Optional specific season ID to update

    Returns:
        Number of teams updated
    """
    client = PWHLApiClient()
    conn = create_connection(db_path)
    updated_count = 0

    try:
        if season_id:
            # Update team stats for a specific season
            logger.info(f"Updating team stats for season ID {season_id}")

            # Fetch team stats for the season
            team_stats = fetch_team_season_stats(client, season_id)

            # Update team stats in the database
            if team_stats:
                updated_count = update_season_stats_teams(conn, season_id, team_stats)
            else:
                logger.warning(f"No team stats found for season {season_id}")
        else:
            # Update team stats for all seasons
            seasons = get_seasons(conn)

            # Process each season
            for (season_id,) in seasons:
                logger.info(f"Processing season {season_id}")

                # Fetch team stats for the season
                team_stats = fetch_team_season_stats(client, season_id)

                # Update team stats in the database
                if team_stats:
                    season_updated = update_season_stats_teams(conn, season_id, team_stats)
                    updated_count += season_updated
                    logger.info(f"Updated {season_updated} team stats for season {season_id}")
                else:
                    logger.warning(f"No team stats found for season {season_id}")

    except Exception as e:
        logger.error(f"Error updating team stats: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

    return updated_count


def update_skater_stats(db_path: str, season_id: Optional[int] = None,
                        player_id: Optional[int] = None) -> Union[int, None, Any]:
    """
    Update skater statistics for all players or a specific player.

    Args:
        db_path: Path to the SQLite database
        season_id: Optional specific season ID to update
        player_id: Optional specific player ID to update

    Returns:
        Number of players updated
    """
    client = PWHLApiClient()
    conn = create_connection(db_path)
    updated_count = 0

    try:
        if player_id:
            # Update stats for a specific player
            logger.info(f"Updating skater stats for player ID {player_id}")

            # Check if player is a skater
            cursor = conn.cursor()
            cursor.execute("SELECT position FROM players WHERE id = ?", (player_id,))
            result = cursor.fetchone()

            if result and result[0] in ('F', 'D'):
                # Fetch player's season stats
                player_stats = fetch_player_season_stats(client, player_id)

                # Update skater stats in the database
                if player_stats:
                    updated_count = update_season_stats_skaters(conn, player_id, player_stats)
                else:
                    logger.warning(f"No stats found for player {player_id}")
            else:
                logger.info(f"Player {player_id} is not a skater, skipping")
        else:
            # Get all players from the database
            players = get_players(conn)

            # Process each player
            for (player_id,) in players:
                # Check if player is a skater
                cursor = conn.cursor()
                cursor.execute("SELECT position FROM players WHERE id = ?", (player_id,))
                result = cursor.fetchone()

                if result and result[0] in ('F', 'D'):
                    logger.info(f"Processing skater {player_id}")

                    # Fetch player's season stats
                    player_stats = fetch_player_season_stats(client, player_id)

                    # Update skater stats in the database
                    if player_stats:
                        player_updated = update_season_stats_skaters(conn, player_id, player_stats)
                        updated_count += player_updated
                        logger.info(f"Updated {player_updated} skater stats for player {player_id}")
                    else:
                        logger.warning(f"No stats found for player {player_id}")
                else:
                    logger.debug(f"Player {player_id} is not a skater, skipping")

                # Add a small delay to avoid overwhelming the API
                time.sleep(0.1)

    except Exception as e:
        logger.error(f"Error updating skater stats: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

    return updated_count


def update_goalie_stats(db_path: str, season_id: Optional[int] = None,
                        player_id: Optional[int] = None) -> Union[int, None, Any]:
    """
    Update goalie statistics for all players or a specific player.

    Args:
        db_path: Path to the SQLite database
        season_id: Optional specific season ID to update
        player_id: Optional specific player ID to update

    Returns:
        Number of players updated
    """
    client = PWHLApiClient()
    conn = create_connection(db_path)
    updated_count = 0

    try:
        if player_id:
            # Update stats for a specific player
            logger.info(f"Updating goalie stats for player ID {player_id}")

            # Check if player is a goalie
            cursor = conn.cursor()
            cursor.execute("SELECT position FROM players WHERE id = ?", (player_id,))
            result = cursor.fetchone()

            if result and result[0] == 'G':
                # Fetch player's season stats
                player_stats = fetch_player_season_stats(client, player_id)

                # Update goalie stats in the database
                if player_stats:
                    updated_count = update_season_stats_goalies(conn, player_id, player_stats)
                else:
                    logger.warning(f"No stats found for player {player_id}")
            else:
                logger.info(f"Player {player_id} is not a goalie, skipping")
        else:
            # Get all players from the database
            players = get_players(conn)

            # Process each player
            for (player_id,) in players:
                # Check if player is a goalie
                cursor = conn.cursor()
                cursor.execute("SELECT position FROM players WHERE id = ?", (player_id,))
                result = cursor.fetchone()

                if result and result[0] == 'G':
                    logger.info(f"Processing goalie {player_id}")

                    # Fetch player's season stats
                    player_stats = fetch_player_season_stats(client, player_id)

                    # Update goalie stats in the database
                    if player_stats:
                        player_updated = update_season_stats_goalies(conn, player_id, player_stats)
                        updated_count += player_updated
                        logger.info(f"Updated {player_updated} goalie stats for player {player_id}")
                    else:
                        logger.warning(f"No stats found for player {player_id}")
                else:
                    logger.debug(f"Player {player_id} is not a goalie, skipping")

                # Add a small delay to avoid overwhelming the API
                time.sleep(0.1)

    except Exception as e:
        logger.error(f"Error updating goalie stats: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

    return updated_count


def update_game_stats(db_path: str, game_id: Optional[int] = None) -> Union[int, None, Any]:
    """
    Update game statistics for all games or a specific game.

    Args:
        db_path: Path to the SQLite database
        game_id: Optional specific game ID to update

    Returns:
        Number of stats records updated
    """
    client = PWHLApiClient()
    conn = create_connection(db_path)
    updated_count = 0

    try:
        if game_id:
            # Update stats for a specific game
            logger.info(f"Updating game stats for game ID {game_id}")

            # Fetch game stats
            game_stats = fetch_game_stats(client, game_id)

            # Update game stats in the database
            if game_stats:
                # Update team stats
                team_updated = update_game_stats_teams(conn, game_id, game_stats)
                updated_count += team_updated

                # Update skater stats
                skater_updated = update_game_stats_skaters(conn, game_id, game_stats)
                updated_count += skater_updated

                # Update goalie stats
                goalie_updated = update_game_stats_goalies(conn, game_id, game_stats)
                updated_count += goalie_updated

                logger.info(f"Updated {updated_count} stats records for game {game_id}")
            else:
                logger.warning(f"No stats found for game {game_id}")
        else:
            # Get all games from the database
            games = get_games(conn)

            # Process each game
            for (game_id,) in games:
                logger.info(f"Processing game {game_id}")

                # Fetch game stats
                game_stats = fetch_game_stats(client, game_id)

                # Update game stats in the database
                if game_stats:
                    # Update team stats
                    team_updated = update_game_stats_teams(conn, game_id, game_stats)

                    # Update skater stats
                    skater_updated = update_game_stats_skaters(conn, game_id, game_stats)

                    # Update goalie stats
                    goalie_updated = update_game_stats_goalies(conn, game_id, game_stats)

                    game_updated = team_updated + skater_updated + goalie_updated
                    updated_count += game_updated

                    logger.info(f"Updated {game_updated} stats records for game {game_id}")
                else:
                    logger.warning(f"No stats found for game {game_id}")

                # Add a small delay to avoid overwhelming the API
                time.sleep(0.5)

    except Exception as e:
        logger.error(f"Error updating game stats: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

    return updated_count


def update_stats(db_path: str, all_stats: bool = False) -> int:
    """
    Update all statistics or specific types based on arguments.

    Args:
        db_path: Path to the SQLite database
        all_stats: Whether to update all types of stats

    Returns:
        Number of records updated
    """
    updated_count = 0

    # Update team stats
    team_updated = update_team_stats(db_path)
    updated_count += team_updated
    logger.info(f"Updated {team_updated} team stats records")

    # Update skater stats
    skater_updated = update_skater_stats(db_path)
    updated_count += skater_updated
    logger.info(f"Updated {skater_updated} skater stats records")

    # Update goalie stats
    goalie_updated = update_goalie_stats(db_path)
    updated_count += goalie_updated
    logger.info(f"Updated {goalie_updated} goalie stats records")

    # Update game stats if requested
    if all_stats:
        game_updated = update_game_stats(db_path)
        updated_count += game_updated
        logger.info(f"Updated {game_updated} game stats records")

    return updated_count


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Update stats
    from pwhl_scraper.config import DB_PATH

    update_stats(DB_PATH, all_stats=True)
