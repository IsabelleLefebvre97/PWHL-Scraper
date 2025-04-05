#!/usr/bin/env python
"""
Command-line interface for the PWHL Scraper application.
"""
import os
import sys
import argparse
import logging
import time

from pwhl_scraper.config import configure_logging, DB_PATH
from pwhl_scraper.database.db_manager import setup_database
from pwhl_scraper.scrapers.basic_info import update_basic_info
from pwhl_scraper.scrapers.players import update_players
from pwhl_scraper.scrapers.games import update_games
from pwhl_scraper.scrapers.stats import update_skater_stats, update_goalie_stats, update_team_stats
from pwhl_scraper.scrapers.playoffs import update_playoffs
from pwhl_scraper.scrapers.play_by_play import update_play_by_play

logger = logging.getLogger(__name__)


def create_parser() -> argparse.ArgumentParser:
    """Create the command-line argument parser."""
    parser = argparse.ArgumentParser(description="PWHL Scraper Data Tool")

    # Global options
    parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                        default="INFO", help="Set the logging level")
    parser.add_argument("--db-path", default=DB_PATH, help="Path to SQLite database file")

    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Setup command
    setup_parser = subparsers.add_parser("setup", help="Initialize the database")

    # Update commands
    update_parser = subparsers.add_parser("update", help="Update data")
    update_parser.add_argument("--all", action="store_true", help="Update all data")
    update_parser.add_argument("--basic", action="store_true", help="Update basic info (leagues, teams, seasons)")
    update_parser.add_argument("--players", action="store_true", help="Update player information")
    update_parser.add_argument("--player-id", type=int, help="Update specific player by ID")
    update_parser.add_argument("--games", action="store_true", help="Update games schedule")
    update_parser.add_argument("--game-details", action="store_true", help="Update game details")
    update_parser.add_argument("--game-id", type=int, help="Update specific game by ID")
    update_parser.add_argument("--stats", action="store_true", help="Update all statistics")
    update_parser.add_argument("--skater-stats", action="store_true", help="Update skater statistics")
    update_parser.add_argument("--goalie-stats", action="store_true", help="Update goalie statistics")
    update_parser.add_argument("--team-stats", action="store_true", help="Update team statistics")
    update_parser.add_argument("--playoffs", action="store_true", help="Update playoff information")
    update_parser.add_argument("--play-by-play", action="store_true", help="Update play-by-play data")
    update_parser.add_argument("--season-id", type=int, help="Update data for specific season")

    # Export command
    export_parser = subparsers.add_parser("export", help="Export data to CSV/JSON")
    export_parser.add_argument("--format", choices=["csv", "json"], default="csv", help="Export format")
    export_parser.add_argument("--table", required=True, help="Table to export")
    export_parser.add_argument("--output", required=True, help="Output directory or file")
    export_parser.add_argument("--query", help="Custom SQL query (overwrites --table)")

    return parser


def run_setup(args: argparse.Namespace) -> None:
    """Set up the database."""
    logger.info("Setting up database...")
    setup_database(args.db_path)
    logger.info("Database setup complete.")


def run_update(args: argparse.Namespace) -> None:
    """Update data based on arguments."""
    update_all = args.all

    # Setup tracking
    start_time = time.time()
    total_updates = 0

    # Basic info
    if update_all or args.basic:
        logger.info("Updating basic information...")
        count = update_basic_info(args.db_path)
        total_updates += count
        logger.info(f"Updated {count} basic info records.")

    # Players
    if update_all or args.players:
        if args.player_id:
            logger.info(f"Updating player ID {args.player_id}...")
            count = update_players(args.db_path, player_id=args.player_id)
        else:
            logger.info("Updating all players...")
            count = update_players(args.db_path)
        total_updates += count
        logger.info(f"Updated {count} player records.")

    # Games
    if update_all or args.games:
        logger.info("Updating games schedule...")
        count = update_games(args.db_path)
        total_updates += count
        logger.info(f"Updated {count} game records.")

    # Playoffs
    if update_all or args.playoffs:
        if args.season_id:
            logger.info(f"Updating playoff information for season {args.season_id}...")
            count = update_playoffs(args.db_path, season_id=args.season_id)
        else:
            logger.info("Updating all playoff information...")
            count = update_playoffs(args.db_path)
        total_updates += count
        logger.info(f"Updated {count} playoff records.")

    # Stats
    if update_all or args.stats or args.skater_stats:
        if args.season_id:
            logger.info(f"Updating skater stats for season {args.season_id}...")
            count = update_skater_stats(args.db_path, season_id=args.season_id)
        else:
            logger.info("Updating all skater stats...")
            count = update_skater_stats(args.db_path)
        total_updates += count
        logger.info(f"Updated {count} skater stat records.")

    if update_all or args.stats or args.goalie_stats:
        if args.season_id:
            logger.info(f"Updating goalie stats for season {args.season_id}...")
            count = update_goalie_stats(args.db_path, season_id=args.season_id)
        else:
            logger.info("Updating all goalie stats...")
            count = update_goalie_stats(args.db_path)
        total_updates += count
        logger.info(f"Updated {count} goalie stat records.")

    if update_all or args.stats or args.team_stats:
        if args.season_id:
            logger.info(f"Updating team stats for season {args.season_id}...")
            count = update_team_stats(args.db_path, season_id=args.season_id)
        else:
            logger.info("Updating all team stats...")
            count = update_team_stats(args.db_path)
        total_updates += count
        logger.info(f"Updated {count} team stat records.")

    # Play-by-play
    if update_all or args.play_by_play:
        if args.game_id:
            logger.info(f"Updating play-by-play data for game {args.game_id}...")
            count = update_play_by_play(args.db_path, game_id=args.game_id)
        else:
            logger.info("Updating all play-by-play data...")
            count = update_play_by_play(args.db_path)
        total_updates += count
        logger.info(f"Updated {count} play-by-play records.")

    end_time = time.time()
    logger.info(f"Update complete. Total records updated: {total_updates}")
    logger.info(f"Time elapsed: {end_time - start_time:.2f} seconds")


def run_export(args: argparse.Namespace) -> None:
    """Export data to CSV or JSON."""
    import sqlite3
    import csv
    import json
    import pandas as pd

    logger.info(f"Exporting {args.table} to {args.format}...")

    try:
        # Connect to database
        conn = sqlite3.connect(args.db_path)

        # Determine query
        if args.query:
            query = args.query
        else:
            query = f"SELECT * FROM {args.table}"

        # Run query and export
        if args.format == "csv":
            df = pd.read_sql_query(query, conn)
            output_path = args.output
            if not output_path.endswith('.csv'):
                output_path = os.path.join(output_path, f"{args.table}.csv")
            df.to_csv(output_path, index=False)
            logger.info(f"Exported {len(df)} rows to {output_path}")
        else:  # JSON
            df = pd.read_sql_query(query, conn)
            output_path = args.output
            if not output_path.endswith('.json'):
                output_path = os.path.join(output_path, f"{args.table}.json")
            df.to_json(output_path, orient="records")
            logger.info(f"Exported {len(df)} rows to {output_path}")

        conn.close()

    except Exception as e:
        logger.error(f"Export failed: {e}")
        sys.exit(1)


def main() -> None:
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args()

    # Configure logging
    configure_logging(args.log_level)

    # Run the appropriate command
    if args.command == "setup":
        run_setup(args)
    elif args.command == "update":
        run_update(args)
    elif args.command == "export":
        run_export(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
