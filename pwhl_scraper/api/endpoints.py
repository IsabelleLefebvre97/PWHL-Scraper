"""
API endpoint definitions for PWHL HockeyTech API.

This module contains all the endpoint configurations for the PWHL HockeyTech API,
including paths and default parameters.
"""

# Define all API endpoints and their default parameters
API_ENDPOINTS = {
    # Basic league information
    "basic_info": {
        "path": "index.php",
        "params": {
            "feed": "statviewfeed",
            "view": "bootstrap",
            "season": "latest",
            "pageName": "scorebar",
            "site_id": "0",
            "league_id": "1",
            "conference": "-1",
            "division": "-1",
            "lang": "en"
        }
    },

    # Player information
    "player_info": {
        "path": "index.php",
        "params": {
            "feed": "statviewfeed",
            "view": "player"
        }
    },

    # Player season statistics
    "player_season_stats": {
        "path": "index.php",
        "params": {
            "feed": "modulekit",
            "view": "player",
            "category": "seasonstats"
        }
    },

    # Skater statistics
    "skater_stats": {
        "path": "index.php",
        "params": {
            "feed": "statviewfeed",
            "view": "players",
            "team": "all",
            "position": "skaters",
            "rookies": "0",
            "statsType": "standard",
            "sort": "points",
            "limit": "500",
            "league_id": "1",
            "lang": "en"
        }
    },

    # Goalie statistics
    "goalie_stats": {
        "path": "index.php",
        "params": {
            "feed": "statviewfeed",
            "view": "players",
            "team": "all",
            "position": "goalies",
            "rookies": "0",
            "statsType": "standard",
            "sort": "goals_against_average",
            "limit": "500",
            "league_id": "1",
            "lang": "en"
        }
    },

    # Team statistics
    "team_stats": {
        "path": "index.php",
        "params": {
            "feed": "statviewfeed",
            "view": "teams",
            "groupTeamsBy": "division",
            "context": "overall",
            "site_id": "0",
            "special": "false",
            "league_id": "1",
            "sort": "points",
            "lang": "en"
        }
    },

    # Schedule
    "schedule": {
        "path": "index.php",
        "params": {
            "feed": "modulekit",
            "view": "scorebar",
            "numberofdaysahead": "10000",
            "numberofdaysback": "10000",
            "limit": "10000",
            "fmt": "json",
            "site_id": "0",
            "lang": "en",
            "league_id": "1"
        }
    },

    # Game summary
    "game_summary": {
        "path": "index.php",
        "params": {
            "feed": "statviewfeed",
            "view": "gameSummary",
            "site_id": "0",
            "lang": "en"
        }
    },

    # Play-by-play
    "play_by_play": {
        "path": "index.php",
        "params": {
            "feed": "statviewfeed",
            "view": "gameCenterPlayByPlay"
        }
    },

    # Playoffs
    "playoffs": {
        "path": "index.php",
        "params": {
            "feed": "modulekit",
            "view": "brackets",
            "league_id": "1"
        }
    },

    # Teams by season
    "teams_by_season": {
        "path": "index.php",
        "params": {
            "feed": "modulekit",
            "view": "teamsbyseason"
        }
    },

    # Seasons list
    "seasons_list": {
        "path": "index.php",
        "params": {
            "feed": "modulekit",
            "view": "seasons"
        }
    },

    # Team roster
    "team_roster": {
        "path": "index.php",
        "params": {
            "feed": "modulekit",
            "view": "roster"
        }
    },

    # Game center
    "game_center": {
        "path": "index.php",
        "params": {
            "feed": "gc",
            "tab": "gamesummary"
        }
    },

    # Game center tabs
    "game_center_tabs": ["gamesummary", "clock", "pxpverbose", "preview"],

    # Team skater stats
    "team_skater_stats": {
        "path": "index.php",
        "params": {
            "feed": "modulekit",
            "view": "statviewtype",
            "type": "skaters"
        }
    },

    # Team goalie stats
    "team_goalie_stats": {
        "path": "index.php",
        "params": {
            "feed": "modulekit",
            "view": "statviewtype",
            "type": "goalies"
        }
    },

    # Player leaders
    "player_leaders": {
        "path": "index.php",
        "params": {
            "feed": "statviewfeed",
            "view": "leadersExtended",
            "league_id": "undefined",
            "team_id": "0",
            "site_id": "0",
            "playerTypes": "skaters",
            "skaterStatTypes": "points,goals",
            "goalieStatTypes": "save_percentage,wins,goals_against_average,shutouts",
            "activeOnly": "0",
            "lang": "en"
        }
    }
}
