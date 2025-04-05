# PWHL Scraper

[![PyPI version](https://badge.fury.io/py/pwhl-scraper.svg)](https://badge.fury.io/py/pwhl-scraper)
[![Python Versions](https://img.shields.io/pypi/pyversions/pwhl-scraper.svg)](https://pypi.org/project/pwhl-scraper/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python package for scraping and analyzing data from the Professional Women's Hockey League (PWHL).

## Features

- **Data Collection**: Scrapes comprehensive data from the PWHL HockeyTech API
- **Data Storage**: Stores data in a SQLite database with proper schema
- **Data Analysis**: Tools for analyzing PWHL statistics
- **Command-line Interface**: Easy-to-use commands for data management

## Installation

```bash
pip install pwhl-scraper
```

Or install from source:

```bash
git clone https://github.com/yourusername/pwhl-scraper.git
cd pwhl-scraper
pip install -e .
```

## Quick Start

### Setting up the database

```bash
# Initialize the database
pwhl-scraper setup

# Update all data
pwhl-scraper update --all

# Update specific data types
pwhl-scraper update --basic --games --players
```

### Accessing the data

```python
import sqlite3
import pandas as pd

# Connect to the database
conn = sqlite3.connect("data/pwhl_data.db")

# Get all teams
teams = pd.read_sql_query("SELECT * FROM teams", conn)
print(teams)

# Get player stats for current season
query = """
SELECT p.first_name, p.last_name, t.name as team, s.* 
FROM season_stats_skaters s
JOIN players p ON s.player_id = p.id
JOIN teams t ON s.team_id = t.id
JOIN seasons on s.season_id = seasons.id
WHERE seasons.current = 1
ORDER BY s.points DESC
"""
stats = pd.read_sql_query(query, conn)
print(stats)

# Close the connection
conn.close()
```

### Exporting data

```bash
# Export to CSV
pwhl-scraper export --table season_stats_skaters --output stats.csv

# Export to JSON
pwhl-scraper export --table players --format json --output players.json

# Export with custom query
pwhl-scraper export --format csv --output top_scorers.csv --query "SELECT p.first_name, p.last_name, t.name as team, s.goals, s.assists, s.points FROM season_stats_skaters s JOIN players p ON s.player_id = p.id JOIN teams t ON s.team_id = t.id WHERE s.season_id = 5 ORDER BY s.points DESC LIMIT 20"
```

## API Documentation

The package provides access to the PWHL HockeyTech API, which is the main source for historical data and statistics.

### Example of using the API client directly

```python
from pwhl_scraper.api.client import PWHLApiClient

# Create client
client = PWHLApiClient()

# Get league information
info = client.fetch_basic_info()

# Get player information
player = client.fetch_player_info(32)

# Get game play-by-play data
pbp = client.fetch_play_by_play(137)
```

## Database Schema

The database includes tables for:

- **Leagues**: League information
- **Seasons**: Season information
- **Teams**: Team information
- **Players**: Player information
- **Games**: Game schedule and results
- **Game Statistics**: Team and player statistics for each game
- **Season Statistics**: Accumulated statistics for teams, skaters, and goalies
- **Play-by-Play**: Detailed event data (goals, shots, penalties, etc.)
- **Playoffs**: Playoff series, rounds, and game information

## Command-line Reference

```
usage: pwhl-scraper [-h] [--log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}] [--db-path DB_PATH] {setup,update,export} ...

PWHL Scraper Data Tool

positional arguments:
  {setup,update,export}  Command to run
    setup                Initialize the database
    update               Update data
    export               Export data to CSV/JSON

optional arguments:
  -h, --help            show this help message and exit
  --log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        Set the logging level
  --db-path DB_PATH     Path to SQLite database file
```

### Update command options

```
usage: pwhl-scraper update [-h] [--all] [--basic] [--players] [--player-id PLAYER_ID]
                     [--games] [--game-details] [--game-id GAME_ID]
                     [--stats] [--skater-stats] [--goalie-stats] [--team-stats]
                     [--playoffs] [--play-by-play] [--season-id SEASON_ID]

optional arguments:
  -h, --help            show this help message and exit
  --all                 Update all data
  --basic               Update basic info (leagues, teams, seasons)
  --players             Update player information
  --player-id PLAYER_ID
                        Update specific player by ID
  --games               Update games schedule
  --game-details        Update game details
  --game-id GAME_ID     Update specific game by ID
  --stats               Update all statistics
  --skater-stats        Update skater statistics
  --goalie-stats        Update goalie statistics
  --team-stats          Update team statistics
  --playoffs            Update playoff information
  --play-by-play        Update play-by-play data
  --season-id SEASON_ID
                        Update data for specific season
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

To contribute:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- The PWHL for creating an exciting new professional women's hockey league
- The HockeyTech API for providing access to the data
