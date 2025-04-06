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
git clone https://github.com/IsabelleLefebvre97/pwhl-scraper.git
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

# Get player stats for the 2024-2025 regular season
query = """
SELECT p.first_name, p.last_name, t.name as team, s.* 
FROM season_stats_skaters s
JOIN players p ON s.player_id = p.id
JOIN teams t ON s.team_id = t.id
JOIN seasons on s.season_id = seasons.id
WHERE seasons.id = 5
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
pwhl-scraper export --table season_stats_skaters --format csv --output top_scorers.csv --query "SELECT p.first_name, p.last_name, t.name as team, s.goals, s.assists, s.points FROM season_stats_skaters s JOIN players p ON s.player_id = p.id JOIN teams t ON s.team_id = t.id WHERE s.season_id = 5 ORDER BY s.goals DESC LIMIT 20"
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
                     [--games] [--game-id GAME_ID]
                     [--stats] [--skater-stats] [--goalie-stats] [--team-stats]
                     [--playoffs] [--play-by-play] [--season-id SEASON_ID]

optional arguments:
  -h, --help            show this help message and exit
  --all                 Update all data
  --basic               Update basic info (leagues, teams, seasons)
  --players             Update player information
  --player-id PLAYER_ID
                        Update specific player by ID
  --games               Update game information
  --game-id GAME_ID     Update specific game by ID
  --stats               Update all statistics
  --team-stats          Update team statistics
  --skater-stats        Update skater statistics
  --goalie-stats        Update goalie statistics
  --playoffs            Update playoff information
  --play-by-play        Update play-by-play data
  --season-id SEASON_ID
                        Update data for specific season
```

## Examples

Here are some examples of what you can create with the data collected by PWHL Scraper:

### Player Goal Scoring Visualization

```python
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Connect to the database
conn = sqlite3.connect("data/pwhl_data.db")

# Get top scorers for the 2024-2025 regular season
query = """
SELECT p.first_name || ' ' || p.last_name as player_name, 
       t.name as team,
       t.id as team_id,
       s.goals, s.assists, s.points, s.games_played
FROM season_stats_skaters s
JOIN players p ON s.player_id = p.id
JOIN teams t ON s.team_id = t.id
JOIN seasons on s.season_id = seasons.id
WHERE seasons.id = 5
ORDER BY s.goals DESC
LIMIT 10
"""
top_scorers = pd.read_sql_query(query, conn)

# Define team colors
team_colors = {
    1: '#173F35',
    2: '#A77BCA',
    3: '#862633',
    4: '#00BFB3',
    5: '#FFB81C',
    6: '#0067B9'
}
default_color = '#808080'

# Create a mapping of team names to colors
team_name_to_color = {}
for _, row in top_scorers.iterrows():
    team_name_to_color[row['team']] = team_colors.get(row['team_id'], default_color)

# Create a visualization
plt.figure(figsize=(12, 6))
ax = sns.barplot(x='player_name', y='goals', hue='team', data=top_scorers, palette=team_name_to_color)
plt.xticks(rotation=45, ha='right')
plt.title('Top 10 PWHL Goal Scorers')
plt.xlabel('')  # No x-axis label
plt.ylabel('Goals')  # Set y-axis label

# Update legend title
handles, labels = ax.get_legend_handles_labels()
ax.legend(handles=handles, labels=labels, title='Teams')

plt.tight_layout()
plt.savefig('example_1-top_scorers.svg', format='svg')
plt.show()

# Close connection
conn.close()
```

![top_scorers.svg](/examples/example_1-top_scorers.svg)

### Team Performance Analysis

```python
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# Connect to the database
conn = sqlite3.connect("data/pwhl_data.db")

# Get team stats
query = """
SELECT t.id as team_id,
       t.name as team_name, 
       COUNT(g.id) as games_played,
       SUM(CASE WHEN g.home_goal_count > g.visiting_goal_count AND g.home_team = t.id THEN 1
                WHEN g.visiting_goal_count > g.home_goal_count AND g.visiting_team = t.id THEN 1 ELSE 0 END) as wins,
       SUM(CASE WHEN g.home_goal_count < g.visiting_goal_count AND g.home_team = t.id THEN 1
                WHEN g.visiting_goal_count < g.home_goal_count AND g.visiting_team = t.id THEN 1 ELSE 0 END) as losses,
       SUM(CASE WHEN g.home_goal_count = g.visiting_goal_count THEN 1 ELSE 0 END) as ties,
       SUM(CASE WHEN g.home_team = t.id THEN g.home_goal_count ELSE g.visiting_goal_count END) as goals_for,
       SUM(CASE WHEN g.home_team = t.id THEN g.visiting_goal_count ELSE g.home_goal_count END) as goals_against
FROM games g
JOIN teams t ON g.home_team = t.id OR g.visiting_team = t.id
JOIN seasons s ON g.season_id = s.id
WHERE s.id = 5 AND g.status = '4'
GROUP BY t.id, t.name
ORDER BY wins DESC
"""
team_stats = pd.read_sql_query(query, conn)

# Calculate win percentage
team_stats['win_pct'] = team_stats['wins'] / team_stats['games_played']

# Define team colors
team_colors = {
    1: '#173F35',
    2: '#A77BCA',
    3: '#862633',
    4: '#00BFB3',
    5: '#FFB81C',
    6: '#0067B9'
}
default_color = '#808080'

# Assign colors to each team based on team_id
bar_colors = [team_colors.get(team_id, default_color) for team_id in team_stats['team_id']]

# Create a visualization
plt.figure(figsize=(10, 6))
plt.bar(team_stats['team_name'], team_stats['win_pct'], color=bar_colors)
plt.ylim(0, 1)
plt.ylabel('Win Percentage')
plt.title('PWHL Team Performance')
plt.tight_layout()
plt.savefig('example_2-team_performance.svg', format='svg')
plt.show()

# Close connection
conn.close()
```

![team_performance.svg](/examples/example_2-team_performance.svg)

### Player Shot Analysis

```python
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# Connect to the database
conn = sqlite3.connect("data/pwhl_data.db")

# Get shot data for top players including their team information
query = """
SELECT p.first_name || ' ' || p.last_name as player_name,
       t.id as team_id,
       t.name as team_name,
       s.shots, s.goals, s.games_played,
       CAST(s.goals AS FLOAT) / NULLIF(s.shots, 0) * 100 as shooting_pct
FROM season_stats_skaters s
JOIN players p ON s.player_id = p.id
JOIN teams t ON s.team_id = t.id
JOIN seasons on s.season_id = seasons.id
WHERE seasons.id = 5 AND s.shots >= 50
ORDER BY shooting_pct DESC
LIMIT 20
"""
shooting_stats = pd.read_sql_query(query, conn)

# Define team colors
team_colors = {
    1: '#173F35',
    2: '#A77BCA',
    3: '#862633',
    4: '#00BFB3',
    5: '#FFB81C',
    6: '#0067B9'
}
default_color = '#808080'

# Get colors for each player based on their team
point_colors = [team_colors.get(team_id, default_color) for team_id in shooting_stats['team_id']]

# Create a scatter plot with team colors
plt.figure(figsize=(12, 8))
scatter = plt.scatter(shooting_stats['shots'], shooting_stats['goals'],
                      s=shooting_stats['shooting_pct'] * 10,
                      alpha=0.7,
                      c=point_colors)

# Add labels for each point
for i, row in shooting_stats.iterrows():
    plt.annotate(row['player_name'],
                 (row['shots'] + 1, row['goals']),
                 fontsize=9)

# Add a legend to identify teams
handles = []
labels = []
for team_id, team_name in zip(shooting_stats['team_id'].unique(), shooting_stats['team_name'].unique()):
    color = team_colors.get(team_id, default_color)
    handles.append(plt.Line2D([0], [0], marker='o', color='w',
                              markerfacecolor=color, markersize=10))
    labels.append(team_name)

plt.legend(handles, labels, title='Teams', loc='best')

plt.xlabel('Total Shots')
plt.ylabel('Goals')
plt.title('PWHL Player Shooting Efficiency')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('example_3-shooting_efficiency.svg', format='svg')
plt.show()

# Close connection
conn.close()
```

![shooting_efficiency.svg](/examples/example_3-shooting_efficiency.svg)

### Game Analysis Over Time

```python
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Connect to the database
conn = sqlite3.connect("data/pwhl_data.db")

# Get game data over time
query = """
SELECT g.date,
       g.home_goal_count + g.visiting_goal_count as total_goals,
       t1.name as home_team, 
       t2.name as away_team
FROM games g
JOIN teams t1 ON g.home_team = t1.id
JOIN teams t2 ON g.visiting_team = t2.id
JOIN seasons s ON g.season_id = s.id
WHERE s.id = 5 AND g.status = '4'
ORDER BY g.date
"""
game_data = pd.read_sql_query(query, conn)

# Convert ISO date-time strings to datetime objects
game_data['date'] = pd.to_datetime(game_data['date'], format='ISO8601')

# Plot goals over the season
plt.figure(figsize=(14, 7))
plt.plot(game_data['date'], game_data['total_goals'], marker='o')
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=14))
plt.gcf().autofmt_xdate()
plt.ylabel('Total Goals per Game')
plt.title('PWHL Goal Scoring Trend Over Season')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('example_4-scoring_trend.svg', format='svg')
plt.show()

# Close connection
conn.close()
```

![scoring_trend.svg](/examples/example_4-scoring_trend.svg)

Each example demonstrates a different aspect of data analysis you can perform with the scraped PWHL data. You can create
visualizations to track player performance, team statistics, scoring trends, and much more.

For more advanced analysis, you can combine data from multiple tables to create comprehensive dashboards or reports on
the PWHL season.

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

- Thank you to the PWHL for inspiring and empowering young—and not so young—girls and women.
