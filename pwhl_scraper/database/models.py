"""
Database models and schema definitions for PWHL Scraper.

This module contains the database schema definition for the
PWHL Scraper, including tables, indexes, and relationships.
"""
from typing import Dict, Any, List

# Database schema definition
DB_SCHEMA = {
    "tables": {
        # Leagues
        "leagues": {
            "schema": """
            CREATE TABLE IF NOT EXISTS leagues (
                id INTEGER PRIMARY KEY,
                name TEXT,
                short_name TEXT,
                code TEXT,
                logo_url TEXT
            );
            """
        },

        # Conferences
        "conferences": {
            "schema": """
            CREATE TABLE IF NOT EXISTS conferences (
                id INTEGER PRIMARY KEY,
                name TEXT
            );
            """
        },

        # Divisions
        "divisions": {
            "schema": """
            CREATE TABLE IF NOT EXISTS divisions (
                id INTEGER PRIMARY KEY,
                name TEXT
            );
            """
        },

        # Seasons
        "seasons": {
            "schema": """
            CREATE TABLE IF NOT EXISTS seasons (
                id INTEGER PRIMARY KEY,
                name TEXT,
                career BOOLEAN,
                playoff BOOLEAN,
                start_date TEXT,
                end_date TEXT
            );
            """
        },

        # Teams
        "teams": {
            "schema": """
            CREATE TABLE IF NOT EXISTS teams (
                id INTEGER PRIMARY KEY,
                name TEXT,
                nickname TEXT,
                code TEXT,
                city TEXT,
                logo_url TEXT,
                league_id INTEGER,
                conference_id INTEGER,
                division_id INTEGER
            );
            """
        },

        # Players
        "players": {
            "schema": """
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY,
                first_name TEXT,
                last_name TEXT,
                jersey_number INTEGER,
                active BOOLEAN,
                rookie BOOLEAN,
                position_id INTEGER,
                position TEXT,
                height TEXT,
                weight TEXT,
                birthdate TEXT,
                shoots TEXT,
                catches TEXT,
                bio TEXT,
                image_url TEXT,
                birthtown TEXT,
                birthprov TEXT,
                birthcntry TEXT,
                nationality TEXT,
                draft_type TEXT,
                veteran_status INTEGER,
                veteran_description TEXT,
                latest_team_id INTEGER,
                FOREIGN KEY (latest_team_id) REFERENCES teams(id)
            );
            """
        },

        # Games
        "games": {
            "schema": """
            CREATE TABLE IF NOT EXISTS games (
                id INTEGER PRIMARY KEY,
                game_number INTEGER,
                date TEXT,
                game_date TEXT,
                game_time TEXT,
                timezone TEXT,
                home_team INTEGER,
                visitor_team INTEGER,
                home_goals INTEGER,
                visitor_goals INTEGER,
                periods INTEGER,
                status INTEGER,
                status_string TEXT,
                venue_name TEXT,
                venue_location TEXT,
                start_time TEXT,
                end_time TEXT,
                duration TEXT,
                toi INTEGER,
                attendance INTEGER,
                game_report_url TEXT,
                text_boxscore_url TEXT,
                season_id INTEGER,
                FOREIGN KEY (season_id) REFERENCES seasons(id),
                FOREIGN KEY (home_team) REFERENCES teams(id),
                FOREIGN KEY (visitor_team) REFERENCES teams(id)
            );
            """
        },

        # Playoff Rounds
        "playoff_rounds": {
            "schema": """
        CREATE TABLE IF NOT EXISTS playoff_rounds (
            id TEXT PRIMARY KEY,
            season_id INTEGER,
            round INTEGER,
            round_name TEXT,
            round_type_id INTEGER,
            round_type_name TEXT,
            FOREIGN KEY (season_id) REFERENCES seasons(id)
        );
        """
        },

        # Playoff Series
        "playoff_series": {
            "schema": """
        CREATE TABLE IF NOT EXISTS playoff_series (
            id TEXT PRIMARY KEY,
            season_id INTEGER,
            round_id TEXT,
            series_letter TEXT,
            series_name TEXT,
            series_logo_url TEXT,
            active BOOLEAN,
            team1 INTEGER,
            team2 INTEGER,
            content_en TEXT,
            winner INTEGER,
            team1_wins INTEGER,
            team2_wins INTEGER,
            ties INTEGER,
            feeder_series_1 TEXT,
            feeder_series_2 TEXT,
            round INTEGER,
            FOREIGN KEY (season_id) REFERENCES seasons(id),
            FOREIGN KEY (round_id) REFERENCES playoff_rounds(id),
            FOREIGN KEY (team1) REFERENCES teams(id),
            FOREIGN KEY (team2) REFERENCES teams(id)
        );
        """
        },

        # Playoff Games
        "playoff_games": {
            "schema": """
        CREATE TABLE IF NOT EXISTS playoff_games (
            id TEXT PRIMARY KEY,
            season_id INTEGER,
            round_id TEXT,
            series_id TEXT,
            game_id INTEGER,
            FOREIGN KEY (season_id) REFERENCES seasons(id),
            FOREIGN KEY (round_id) REFERENCES playoff_rounds(id),
            FOREIGN KEY (series_id) REFERENCES playoff_series(id),
            FOREIGN KEY (game_id) REFERENCES games(id)
        );
        """
        }
    },

    # Season Stats: Teams
    "season_stats_teams": {
        "schema": """
            CREATE TABLE IF NOT EXISTS season_stats_teams (
                id TEXT PRIMARY KEY,
                season_id INTEGER,
                team_id INTEGER,
                name TEXT,
                nickname TEXT,
                city TEXT,
                team_code TEXT,
                division_id INTEGER,
                wins INTEGER,
                losses INTEGER,
                ties INTEGER,
                ot_losses INTEGER,
                reg_ot_losses INTEGER,
                reg_losses INTEGER,
                ot_wins INTEGER,
                shootout_wins INTEGER,
                shootout_losses INTEGER,
                regulation_wins INTEGER,
                row INTEGER,
                points INTEGER,
                bench_minutes INTEGER,
                penalty_minutes INTEGER,
                goals_for INTEGER,
                goals_against INTEGER,
                goals_diff INTEGER,
                power_play_goals INTEGER,
                power_play_goals_against INTEGER,
                shootout_goals INTEGER,
                shootout_goals_against INTEGER,
                shootout_attempts INTEGER,
                shootout_attempts_against INTEGER,
                short_handed_goals_for INTEGER,
                short_handed_goals_against INTEGER,
                percentage REAL,
                percentage_full REAL,
                shootout_games_played INTEGER,
                games_played INTEGER,
                shootout_pct REAL,
                power_play_pct REAL,
                shootout_pct_goals_for REAL,
                shootout_pct_goals_against REAL,
                penalty_kill_pct REAL,
                pim_pg REAL,
                power_plays INTEGER,
                win_percentage REAL,
                times_short_handed INTEGER,
                shootout_record TEXT,
                home_record TEXT,
                visiting_record TEXT,
                FOREIGN KEY (season_id) REFERENCES seasons(id),
                FOREIGN KEY (team_id) REFERENCES teams(id)
            );
            """
    },

    # Season Stats: Skaters
    "season_stats_skaters": {
        "schema": """
            CREATE TABLE IF NOT EXISTS season_stats_skaters (
                id TEXT PRIMARY KEY,
                player_id INTEGER,
                season_id INTEGER,
                team_id INTEGER,
                jersey_number INTEGER,
                shoots TEXT,
                games_played INTEGER,
                game_winning_goals INTEGER,
                game_tieing_goals INTEGER,
                first_goals INTEGER,
                insurance_goals INTEGER,
                unassisted_goals INTEGER,
                empty_net_goals INTEGER,
                overtime_goals INTEGER,
                ice_time INTEGER,
                ice_time_avg REAL,
                goals INTEGER,
                shots INTEGER,
                loose_ball_recoveries INTEGER,
                caused_turnovers INTEGER,
                turnovers INTEGER,
                hits INTEGER,
                shots_blocked_by_player INTEGER,
                ice_time_minutes_seconds TEXT,
                shooting_percentage REAL,
                assists INTEGER,
                points INTEGER,
                points_per_game REAL,
                plus_minus INTEGER,
                penalty_minutes INTEGER,
                penalty_minutes_per_game REAL,
                minor_penalties INTEGER,
                major_penalties INTEGER,
                power_play_goals INTEGER,
                power_play_assists INTEGER,
                power_play_points INTEGER,
                short_handed_goals INTEGER,
                short_handed_assists INTEGER,
                short_handed_points INTEGER,
                shootout_goals INTEGER,
                shootout_attempts INTEGER,
                shootout_winning_goals INTEGER,
                shootout_games_played INTEGER,
                faceoff_attempts INTEGER,
                faceoff_wins INTEGER,
                faceoff_pct REAL,
                faceoff_wa TEXT,
                shots_on INTEGER,
                shootout_percentage REAL,
                latest_team_id INTEGER,
                num_teams INTEGER,
                FOREIGN KEY (player_id) REFERENCES players(id),
                FOREIGN KEY (season_id) REFERENCES seasons(id),
                FOREIGN KEY (team_id) REFERENCES teams(id)
            );
            """
    },

    # Season Stats: Goalies
    "season_stats_goalies": {
        "schema": """
        CREATE TABLE IF NOT EXISTS season_stats_goalies (
            id TEXT PRIMARY KEY,
            player_id INTEGER,
            season_id INTEGER,
            team_id INTEGER,
            jersey_number INTEGER,
            shoots TEXT,
            catches TEXT,
            games_played INTEGER,
            ice_time INTEGER,
            ice_time_avg REAL,
            has_games_played BOOLEAN,
            minutes_played TEXT,
            minutes_played_g INTEGER,
            seconds_played INTEGER,
            saves INTEGER,
            shots INTEGER,
            save_percentage REAL,
            goals_against INTEGER,
            empty_net_goals_against INTEGER,
            shutouts INTEGER,
            wins INTEGER,
            losses INTEGER,
            ot_losses INTEGER,
            total_losses INTEGER,
            shootout_games_played INTEGER,
            shootout_losses INTEGER,
            shootout_wins INTEGER,
            shootout_goals_against INTEGER,
            shootout_saves INTEGER,
            shootout_attempts INTEGER,
            goals INTEGER,
            assists INTEGER,
            points INTEGER,
            penalty_minutes INTEGER,
            loose_ball_recoveries INTEGER,
            caused_turnovers INTEGER,
            turnovers INTEGER,
            shootout_percentage REAL,
            ot INTEGER,
            ties INTEGER,
            shots_against_average REAL,
            goals_against_average REAL,
            latest_team_id INTEGER,
            num_teams INTEGER,
            FOREIGN KEY (player_id) REFERENCES players(id),
            FOREIGN KEY (season_id) REFERENCES seasons(id),
            FOREIGN KEY (team_id) REFERENCES teams(id)
        );
        """
    },

    # Game Stats: Teams
    "game_stats_teams": {
        "schema": """
            CREATE TABLE IF NOT EXISTS game_stats_teams (
                id TEXT PRIMARY KEY,
                game_id INTEGER,
                team_id INTEGER,
                season_id INTEGER,
                goals INTEGER,
                shots_on_goal INTEGER,
                power_play_total INTEGER,
                power_play_goals INTEGER,
                fow INTEGER, -- faceoff wins
                hits INTEGER,
                FOREIGN KEY (game_id) REFERENCES games(id),
                FOREIGN KEY (team_id) REFERENCES teams(id),
                FOREIGN KEY (season_id) REFERENCES seasons(id)
            );
            """
    },

    # Game Stats: Skaters
    "game_stats_skaters": {
        "schema": """
            CREATE TABLE IF NOT EXISTS game_stats_skaters (
                id TEXT PRIMARY KEY,
                game_id INTEGER,
                player_id INTEGER,
                team_id INTEGER,
                season_id INTEGER,
                jersey_number INTEGER,
                position TEXT,
                rookie BOOLEAN,
                start BOOLEAN,
                status TEXT,
                goals INTEGER,
                assists INTEGER,
                plusminus INTEGER,
                pim INTEGER, -- penalty minutes
                faceoff_wins INTEGER,
                faceoff_attempts INTEGER,
                hits INTEGER,
                shots INTEGER,
                shots_on INTEGER,
                shots_blocked_by_player INTEGER,
                shots_blocked INTEGER,
                power_play_goals INTEGER,
                short_handed_goals INTEGER,
                game_winning_goal BOOLEAN,
                FOREIGN KEY (game_id) REFERENCES games(id),
                FOREIGN KEY (player_id) REFERENCES players(id),
                FOREIGN KEY (team_id) REFERENCES teams(id),
                FOREIGN KEY (season_id) REFERENCES seasons(id)
            );
            """
    },

    # Game Stats: Goalies
    "game_stats_goalies": {
        "schema": """
            CREATE TABLE IF NOT EXISTS game_stats_goalies (
                id TEXT PRIMARY KEY,
                game_id INTEGER,
                player_id INTEGER,
                team_id INTEGER,
                season_id INTEGER,
                jersey_number INTEGER,
                rookie BOOLEAN,
                start BOOLEAN,
                position TEXT,
                status TEXT,
                seconds INTEGER,
                time TEXT,
                shots_against INTEGER,
                goals_against INTEGER,
                saves INTEGER,
                goals INTEGER,
                assists INTEGER,
                pim INTEGER,
                shots INTEGER,
                FOREIGN KEY (game_id) REFERENCES games(id),
                FOREIGN KEY (player_id) REFERENCES players(id),
                FOREIGN KEY (team_id) REFERENCES teams(id),
                FOREIGN KEY (season_id) REFERENCES seasons(id)
            );
            """
    },

    # Play-By-Play: Goalie Changes
    "pbp_goalie_changes": {
        "schema": """
        CREATE TABLE IF NOT EXISTS pbp_goalie_changes (
            id TEXT PRIMARY KEY,
            game_id INTEGER,
            season_id INTEGER,
            period INTEGER,
            time TEXT,
            seconds INTEGER,
            team_id INTEGER,
            opponent_team_id INTEGER,
            goalie_in_id INTEGER,
            goalie_out_id INTEGER,
            FOREIGN KEY (game_id) REFERENCES games(id),
            FOREIGN KEY (season_id) REFERENCES seasons(id),
            FOREIGN KEY (team_id) REFERENCES teams(id),
            FOREIGN KEY (opponent_team_id) REFERENCES teams(id),
            FOREIGN KEY (goalie_in_id) REFERENCES players(id),
            FOREIGN KEY (goalie_out_id) REFERENCES players(id)
        );
        """
    },

    # Play-By-Play: Faceoffs
    "pbp_faceoffs": {
        "schema": """
        CREATE TABLE IF NOT EXISTS pbp_faceoffs (
            id TEXT PRIMARY KEY,
            game_id INTEGER,
            season_id INTEGER,
            period INTEGER,
            time TEXT,
            time_formatted TEXT,
            seconds INTEGER,
            home_player_id INTEGER,
            visitor_player_id INTEGER,
            home_win BOOLEAN,
            win_team_id INTEGER,
            opponent_team_id INTEGER,
            x_location INTEGER,
            y_location INTEGER,
            location_id INTEGER,
            FOREIGN KEY (game_id) REFERENCES games(id),
            FOREIGN KEY (season_id) REFERENCES seasons(id),
            FOREIGN KEY (home_player_id) REFERENCES players(id),
            FOREIGN KEY (visitor_player_id) REFERENCES players(id),
            FOREIGN KEY (win_team_id) REFERENCES teams(id),
            FOREIGN KEY (opponent_team_id) REFERENCES teams(id)
        );
        """
    },

    # Play-By-Play: Hits
    "pbp_hits": {
        "schema": """
        CREATE TABLE IF NOT EXISTS pbp_hits (
            id TEXT PRIMARY KEY,
            game_id INTEGER,
            season_id INTEGER,
            period INTEGER,
            time TEXT,
            time_formatted TEXT,
            seconds INTEGER,
            player_id INTEGER,
            team_id INTEGER,
            opponent_team_id INTEGER,
            home BOOLEAN,
            x_location INTEGER,
            y_location INTEGER,
            hit_type INTEGER,
            FOREIGN KEY (game_id) REFERENCES games(id),
            FOREIGN KEY (season_id) REFERENCES seasons(id),
            FOREIGN KEY (player_id) REFERENCES players(id),
            FOREIGN KEY (team_id) REFERENCES teams(id),
            FOREIGN KEY (opponent_team_id) REFERENCES teams(id)
        );
        """
    },

    # Play-By-Play: Shots
    "pbp_shots": {
        "schema": """
        CREATE TABLE IF NOT EXISTS pbp_shots (
            id TEXT PRIMARY KEY,
            game_id INTEGER,
            season_id INTEGER,
            player_id INTEGER,
            goalie_id INTEGER,
            team_id INTEGER,
            opponent_team_id INTEGER,
            home BOOLEAN,
            period INTEGER,
            time TEXT,
            time_formatted TEXT,
            seconds INTEGER,
            x_location INTEGER,
            y_location INTEGER,
            shot_type INTEGER,
            shot_type_description TEXT,
            quality INTEGER,
            shot_quality_description TEXT,
            game_goal_id TEXT,
            FOREIGN KEY (game_id) REFERENCES games(id),
            FOREIGN KEY (season_id) REFERENCES seasons(id),
            FOREIGN KEY (player_id) REFERENCES players(id),
            FOREIGN KEY (goalie_id) REFERENCES players(id),
            FOREIGN KEY (team_id) REFERENCES teams(id),
            FOREIGN KEY (opponent_team_id) REFERENCES teams(id)
        );
        """
    },

    # Play-By-Play: Blocked Shots
    "pbp_blocked_shots": {
        "schema": """
        CREATE TABLE IF NOT EXISTS pbp_blocked_shots (
            id TEXT PRIMARY KEY,
            game_id INTEGER,
            season_id INTEGER,
            player_id INTEGER,
            goalie_id INTEGER,
            team_id INTEGER,
            blocker_player_id INTEGER,
            blocker_team_id INTEGER,
            home BOOLEAN,
            period INTEGER,
            time TEXT,
            time_formatted TEXT,
            seconds INTEGER,
            x_location INTEGER,
            y_location INTEGER,
            orientation INTEGER,
            shot_type INTEGER,
            shot_type_description TEXT,
            quality INTEGER,
            shot_quality_description TEXT,
            FOREIGN KEY (game_id) REFERENCES games(id),
            FOREIGN KEY (season_id) REFERENCES seasons(id),
            FOREIGN KEY (player_id) REFERENCES players(id),
            FOREIGN KEY (goalie_id) REFERENCES players(id), 
            FOREIGN KEY (blocker_player_id) REFERENCES players(id),
            FOREIGN KEY (team_id) REFERENCES teams(id),
            FOREIGN KEY (blocker_team_id) REFERENCES teams(id),
            FOREIGN KEY (opponent_team_id) REFERENCES teams(id)
        );
        """
    },

    # Play-By-Play: Goals
    "pbp_goals": {
        "schema": """
        CREATE TABLE IF NOT EXISTS pbp_goals (
            id TEXT PRIMARY KEY,
            game_id INTEGER,
            season_id INTEGER,
            team_id INTEGER,
            opponent_team_id INTEGER,
            home BOOLEAN,
            goal_player_id INTEGER,
            assist1_player_id INTEGER,
            assist2_player_id INTEGER,
            period INTEGER,
            time TEXT,
            time_formatted TEXT,
            seconds INTEGER,
            x_location INTEGER,
            y_location INTEGER,
            location_set BOOLEAN,
            power_play BOOLEAN,
            empty_net BOOLEAN,
            penalty_shot BOOLEAN,
            short_handed BOOLEAN,
            insurance_goal BOOLEAN,
            game_winning BOOLEAN,
            game_tieing BOOLEAN,
            scorer_goal_num INTEGER,
            goal_type TEXT,
            FOREIGN KEY (game_id) REFERENCES games(id),
            FOREIGN KEY (season_id) REFERENCES seasons(id),
            FOREIGN KEY (team_id) REFERENCES teams(id),
            FOREIGN KEY (opponent_team_id) REFERENCES teams(id),
            FOREIGN KEY (goal_player_id) REFERENCES players(id),
            FOREIGN KEY (assist1_player_id) REFERENCES players(id),
            FOREIGN KEY (assist2_player_id) REFERENCES players(id)
        );
        """
    },

    # Play-By-Play: Goal Plus Players
    "pbp_goals_plus": {
        "schema": """
        CREATE TABLE IF NOT EXISTS pbp_goals_plus (
            id TEXT PRIMARY KEY,
            goal_id TEXT,
            game_id INTEGER,
            season_id INTEGER,
            team_id INTEGER,
            player_id INTEGER,
            jersey_number INTEGER,
            FOREIGN KEY (goal_id) REFERENCES pbp_goals(id),
            FOREIGN KEY (game_id) REFERENCES games(id),
            FOREIGN KEY (season_id) REFERENCES seasons(id),
            FOREIGN KEY (team_id) REFERENCES teams(id),
            FOREIGN KEY (player_id) REFERENCES players(id)
        );
        """
    },

    # Play-By-Play: Goal Minus Players
    "pbp_goals_minus": {
        "schema": """
        CREATE TABLE IF NOT EXISTS pbp_goals_minus (
            id TEXT PRIMARY KEY,
            goal_id TEXT,
            game_id INTEGER,
            season_id INTEGER,
            team_id INTEGER,
            player_id INTEGER,
            jersey_number INTEGER,
            FOREIGN KEY (goal_id) REFERENCES pbp_goals(id),
            FOREIGN KEY (game_id) REFERENCES games(id),
            FOREIGN KEY (season_id) REFERENCES seasons(id),
            FOREIGN KEY (team_id) REFERENCES teams(id),
            FOREIGN KEY (player_id) REFERENCES players(id)
        );
        """
    },

    # Play-By-Play: Penalties
    "pbp_penalties": {
        "schema": """
        CREATE TABLE IF NOT EXISTS pbp_penalties (
            id TEXT PRIMARY KEY,
            game_id INTEGER,
            season_id INTEGER,
            player_id INTEGER,
            player_served INTEGER,
            team_id INTEGER,
            opponent_team_id INTEGER,
            home BOOLEAN,
            period INTEGER,
            time_off_formatted TEXT,
            minutes REAL,
            minutes_formatted TEXT,
            bench BOOLEAN,
            penalty_shot BOOLEAN,
            pp BOOLEAN,
            offence INTEGER,
            penalty_class_id INTEGER,
            penalty_class TEXT,
            lang_penalty_description TEXT,
            FOREIGN KEY (game_id) REFERENCES games(id),
            FOREIGN KEY (season_id) REFERENCES seasons(id),
            FOREIGN KEY (player_id) REFERENCES players(id),
            FOREIGN KEY (team_id) REFERENCES teams(id),
            FOREIGN KEY (opponent_team_id) REFERENCES teams(id)
        );
        """
    },

    # Play-By-Play: Shootouts
    "pbp_shootouts": {
        "schema": """
        CREATE TABLE IF NOT EXISTS pbp_shootouts (
            id TEXT PRIMARY KEY,
            game_id INTEGER,
            season_id INTEGER,
            player_id INTEGER,
            goalie_id INTEGER,
            team_id INTEGER,
            opponent_team_id INTEGER,
            home BOOLEAN,
            shot_order INTEGER,
            goal BOOLEAN,
            winning_goal BOOLEAN,
            seconds INTEGER,
            FOREIGN KEY (game_id) REFERENCES games(id),
            FOREIGN KEY (season_id) REFERENCES seasons(id),
            FOREIGN KEY (player_id) REFERENCES players(id),
            FOREIGN KEY (goalie_id) REFERENCES players(id),
            FOREIGN KEY (team_id) REFERENCES teams(id),
            FOREIGN KEY (opponent_team_id) REFERENCES teams(id)
        );
        """
    },

    # Indexes for Efficient Querying
    "indexes": {
        "players": [
            "CREATE INDEX IF NOT EXISTS idx_players_team_id ON players(latest_team_id);",
            "CREATE INDEX IF NOT EXISTS idx_players_position ON players(position);",
            "CREATE INDEX IF NOT EXISTS idx_players_active ON players(active);",
            "CREATE INDEX IF NOT EXISTS idx_players_rookie ON players(rookie);",
            "CREATE INDEX IF NOT EXISTS idx_players_birthcntry ON players(birthcntry);"
        ],

        "games": [
            "CREATE INDEX IF NOT EXISTS idx_games_season_id ON games(season_id);",
            "CREATE INDEX IF NOT EXISTS idx_games_date ON games(date);",
            "CREATE INDEX IF NOT EXISTS idx_games_home_team ON games(home_team);",
            "CREATE INDEX IF NOT EXISTS idx_games_visitor_team ON games(visitor_team);"
        ],

        "playoffs": [
            "CREATE INDEX IF NOT EXISTS idx_playoff_rounds_season_id ON playoff_rounds(season_id);",
            "CREATE INDEX IF NOT EXISTS idx_playoff_series_season_id ON playoff_series(season_id);",
            "CREATE INDEX IF NOT EXISTS idx_playoff_games_season_id ON playoff_games(season_id);",
            "CREATE INDEX IF NOT EXISTS idx_playoff_games_game_id ON playoff_games(game_id);"
        ],

        "season_stats": [
            "CREATE INDEX IF NOT EXISTS idx_season_stats_teams_season ON season_stats_teams(season_id);",
            "CREATE INDEX IF NOT EXISTS idx_season_stats_teams_team ON season_stats_teams(team_id);",
            "CREATE INDEX IF NOT EXISTS idx_season_stats_skaters_season ON season_stats_skaters(season_id);",
            "CREATE INDEX IF NOT EXISTS idx_season_stats_skaters_player ON season_stats_skaters(player_id);",
            "CREATE INDEX IF NOT EXISTS idx_season_stats_skaters_team ON season_stats_skaters(team_id);",
            "CREATE INDEX IF NOT EXISTS idx_season_stats_goalies_season ON season_stats_goalies(season_id);",
            "CREATE INDEX IF NOT EXISTS idx_season_stats_goalies_player ON season_stats_goalies(player_id);",
            "CREATE INDEX IF NOT EXISTS idx_season_stats_goalies_team ON season_stats_goalies(team_id);"
        ],

        "game_stats": [
            "CREATE INDEX IF NOT EXISTS idx_game_stats_teams_game ON game_stats_teams(game_id);",
            "CREATE INDEX IF NOT EXISTS idx_game_stats_teams_team ON game_stats_teams(team_id);",
            "CREATE INDEX IF NOT EXISTS idx_game_stats_teams_season ON game_stats_teams(season_id);",
            "CREATE INDEX IF NOT EXISTS idx_game_stats_skaters_game ON game_stats_skaters(game_id);",
            "CREATE INDEX IF NOT EXISTS idx_game_stats_skaters_player ON game_stats_skaters(player_id);",
            "CREATE INDEX IF NOT EXISTS idx_game_stats_skaters_team ON game_stats_skaters(team_id);",
            "CREATE INDEX IF NOT EXISTS idx_game_stats_skaters_season ON game_stats_skaters(season_id);",
            "CREATE INDEX IF NOT EXISTS idx_game_stats_goalies_game ON game_stats_goalies(game_id);",
            "CREATE INDEX IF NOT EXISTS idx_game_stats_goalies_player ON game_stats_goalies(player_id);",
            "CREATE INDEX IF NOT EXISTS idx_game_stats_goalies_team ON game_stats_goalies(team_id);",
            "CREATE INDEX IF NOT EXISTS idx_game_stats_goalies_season ON game_stats_goalies(season_id);"
        ],

        "play_by_play": [
            "CREATE INDEX IF NOT EXISTS idx_pbp_goalie_changes_game ON pbp_goalie_changes(game_id);",
            "CREATE INDEX IF NOT EXISTS idx_pbp_goalie_changes_season ON pbp_goalie_changes(season_id);",
            "CREATE INDEX IF NOT EXISTS idx_pbp_goalie_changes_team ON pbp_goalie_changes(team_id);",
            "CREATE INDEX IF NOT EXISTS idx_pbp_goalie_changes_goalie_in ON pbp_goalie_changes(goalie_in_id);",
            "CREATE INDEX IF NOT EXISTS idx_pbp_goalie_changes_goalie_out ON pbp_goalie_changes(goalie_out_id);",
            "CREATE INDEX IF NOT EXISTS idx_pbp_faceoffs_game ON pbp_faceoffs(game_id);",
            "CREATE INDEX IF NOT EXISTS idx_pbp_faceoffs_season ON pbp_faceoffs(season_id);",
            "CREATE INDEX IF NOT EXISTS idx_pbp_faceoffs_home_player ON pbp_faceoffs(home_player_id);",
            "CREATE INDEX IF NOT EXISTS idx_pbp_faceoffs_visitor_player ON pbp_faceoffs(visitor_player_id);",
            "CREATE INDEX IF NOT EXISTS idx_pbp_faceoffs_win_team ON pbp_faceoffs(win_team_id);",
            "CREATE INDEX IF NOT EXISTS idx_pbp_hits_game ON pbp_hits(game_id);",
            "CREATE INDEX IF NOT EXISTS idx_pbp_hits_season ON pbp_hits(season_id);",
            "CREATE INDEX IF NOT EXISTS idx_pbp_hits_player ON pbp_hits(player_id);",
            "CREATE INDEX IF NOT EXISTS idx_pbp_hits_team ON pbp_hits(team_id);",
            "CREATE INDEX IF NOT EXISTS idx_pbp_hits_opponent ON pbp_hits(opponent_team_id);",
            "CREATE INDEX IF NOT EXISTS idx_pbp_shots_game ON pbp_shots(game_id);",
            "CREATE INDEX IF NOT EXISTS idx_pbp_shots_season ON pbp_shots(season_id);",
            "CREATE INDEX IF NOT EXISTS idx_pbp_shots_player ON pbp_shots(player_id);",
            "CREATE INDEX IF NOT EXISTS idx_pbp_shots_goalie ON pbp_shots(goalie_id);",
            "CREATE INDEX IF NOT EXISTS idx_pbp_shots_team ON pbp_shots(team_id);",
            "CREATE INDEX IF NOT EXISTS idx_pbp_shots_opponent ON pbp_shots(opponent_team_id);",
            "CREATE INDEX IF NOT EXISTS idx_pbp_shots_period ON pbp_shots(period_id);",
            "CREATE INDEX IF NOT EXISTS idx_pbp_blocked_shots_game ON pbp_blocked_shots(game_id);",
            "CREATE INDEX IF NOT EXISTS idx_pbp_blocked_shots_season ON pbp_blocked_shots(season_id);",
            "CREATE INDEX IF NOT EXISTS idx_pbp_blocked_shots_player ON pbp_blocked_shots(player_id);",
            "CREATE INDEX IF NOT EXISTS idx_pbp_blocked_shots_blocker ON pbp_blocked_shots(blocker_player_id);",
            "CREATE INDEX IF NOT EXISTS idx_pbp_blocked_shots_team ON pbp_blocked_shots(team_id);",
            "CREATE INDEX IF NOT EXISTS idx_pbp_blocked_shots_blocker_team ON pbp_blocked_shots(blocker_team_id);",
            "CREATE INDEX IF NOT EXISTS idx_pbp_blocked_shots_opponent ON pbp_blocked_shots(opponent_team_id);",
            "CREATE INDEX IF NOT EXISTS idx_pbp_goals_game ON pbp_goals(game_id);",
            "CREATE INDEX IF NOT EXISTS idx_pbp_goals_season ON pbp_goals(season_id);",
            "CREATE INDEX IF NOT EXISTS idx_pbp_goals_team ON pbp_goals(team_id);",
            "CREATE INDEX IF NOT EXISTS idx_pbp_goals_opponent ON pbp_goals(opponent_team_id);",
            "CREATE INDEX IF NOT EXISTS idx_pbp_goals_scorer ON pbp_goals(goal_player_id);",
            "CREATE INDEX IF NOT EXISTS idx_pbp_goals_assist1 ON pbp_goals(assist1_player_id);",
            "CREATE INDEX IF NOT EXISTS idx_pbp_goals_assist2 ON pbp_goals(assist2_player_id);",
            "CREATE INDEX IF NOT EXISTS idx_pbp_goals_period ON pbp_goals(period_id);",
            "CREATE INDEX IF NOT EXISTS idx_pbp_goals_plus_goal ON pbp_goals_plus(goal_id);",
            "CREATE INDEX IF NOT EXISTS idx_pbp_goals_plus_game ON pbp_goals_plus(game_id);",
            "CREATE INDEX IF NOT EXISTS idx_pbp_goals_plus_season ON pbp_goals_plus(season_id);",
            "CREATE INDEX IF NOT EXISTS idx_pbp_goals_plus_team ON pbp_goals_plus(team_id);",
            "CREATE INDEX IF NOT EXISTS idx_pbp_goals_plus_player ON pbp_goals_plus(player_id);",
            "CREATE INDEX IF NOT EXISTS idx_pbp_goals_minus_goal ON pbp_goals_minus(goal_id);",
            "CREATE INDEX IF NOT EXISTS idx_pbp_goals_minus_game ON pbp_goals_minus(game_id);",
            "CREATE INDEX IF NOT EXISTS idx_pbp_goals_minus_season ON pbp_goals_minus(season_id);",
            "CREATE INDEX IF NOT EXISTS idx_pbp_goals_minus_team ON pbp_goals_minus(team_id);",
            "CREATE INDEX IF NOT EXISTS idx_pbp_goals_minus_player ON pbp_goals_minus(player_id);",
            "CREATE INDEX IF NOT EXISTS idx_pbp_penalties_game ON pbp_penalties(game_id);",
            "CREATE INDEX IF NOT EXISTS idx_pbp_penalties_season ON pbp_penalties(season_id);",
            "CREATE INDEX IF NOT EXISTS idx_pbp_penalties_player ON pbp_penalties(player_id);",
            "CREATE INDEX IF NOT EXISTS idx_pbp_penalties_team ON pbp_penalties(team_id);",
            "CREATE INDEX IF NOT EXISTS idx_pbp_penalties_opponent ON pbp_penalties(opponent_team_id);",
            "CREATE INDEX IF NOT EXISTS idx_pbp_penalties_period ON pbp_penalties(period_id);",
            "CREATE INDEX IF NOT EXISTS idx_pbp_shootouts_game ON pbp_shootouts(game_id);",
            "CREATE INDEX IF NOT EXISTS idx_pbp_shootouts_season ON pbp_shootouts(season_id);",
            "CREATE INDEX IF NOT EXISTS idx_pbp_shootouts_player ON pbp_shootouts(player_id);",
            "CREATE INDEX IF NOT EXISTS idx_pbp_shootouts_goalie ON pbp_shootouts(goalie_id);",
            "CREATE INDEX IF NOT EXISTS idx_pbp_shootouts_team ON pbp_shootouts(team_id);",
            "CREATE INDEX IF NOT EXISTS idx_pbp_shootouts_opponent ON pbp_shootouts(opponent_team_id);",
            "CREATE INDEX IF NOT EXISTS idx_pbp_shootouts_shot_order ON pbp_shootouts(shot_order);",
        ],

    }
}


def get_table_schema(table_name: str) -> str:
    """
    Get the SQL schema definition for a specific table.

    Args:
        table_name: Name of the table

    Returns:
        SQL schema definition

    Raises:
        ValueError: If table_name is not found in the schema
    """
    if table_name in DB_SCHEMA["tables"]:
        return DB_SCHEMA["tables"][table_name]["schema"]

    raise ValueError(f"Table '{table_name}' not found in schema")


def get_table_names() -> List[str]:
    """
    Get a list of all table names in the schema.

    Returns:
        List of table names
    """
    return list(DB_SCHEMA["tables"].keys())


def get_index_statements(index_group: str = None) -> List[str]:
    """
    Get a list of index creation statements.

    Args:
        index_group: Specific index group or None for all indexes

    Returns:
        List of index creation SQL statements
    """
    if index_group:
        if index_group in DB_SCHEMA["indexes"]:
            return DB_SCHEMA["indexes"][index_group]
        raise ValueError(f"Index group '{index_group}' not found in schema")

    # Return all indexes flattened into a single list
    return [stmt for group in DB_SCHEMA["indexes"].values() for stmt in group]
