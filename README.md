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

<details>
<summary>Click to expand/collapse code</summary>

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

</details>

![top_scorers.svg](/examples/example_1-top_scorers.svg)

### Team Performance Analysis

<details>
<summary>Click to expand/collapse code</summary>

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

</details>

![team_performance.svg](/examples/example_2-team_performance.svg)

### Player Shot Analysis

<details>
<summary>Click to expand/collapse code</summary>

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

</details>

![shooting_efficiency.svg](/examples/example_3-shooting_efficiency.svg)

### Timing of Goals

<details>
<summary>Click to expand/collapse code</summary>

```python
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.gridspec import GridSpec
import numpy as np

# Connect to the database
conn = sqlite3.connect("data/pwhl_data.db")

# Update the query to include the season name
query = """
SELECT 
    g.period,
    g.time,
    g.time_formatted,
    g.seconds,
    g.goal_player_id,
    g.team_id,
    g.opponent_team_id,
    g.game_id,
    gm.date,
    s.name as season_name
FROM pbp_goals g
JOIN games gm ON g.game_id = gm.id
JOIN seasons s ON gm.season_id = s.id
WHERE g.season_id = 5
  AND gm.status = '4'
ORDER BY g.period, g.seconds
"""

goals_data = pd.read_sql_query(query, conn)

# Extract the season name from the data (all rows will have the same season name)
season_name = goals_data['season_name'].iloc[0]

# Set a modern style (without grid lines)
sns.set_style("white")

# Create a figure with four subplots side-by-side
fig = plt.figure(figsize=(16, 4))
gs = GridSpec(1, 4, width_ratios=[4, 4, 4, 1])

period_names = {
    1: "Period 1",
    2: "Period 2",
    3: "Period 3",
    4: "Overtime"
}

# Define a color palette
colors = sns.color_palette("viridis", 4)

# Process data for each period and plot in its column
axes = []
for i, period in enumerate([1, 2, 3, 4]):
    ax = plt.subplot(gs[i])
    axes.append(ax)

    # Style the plot
    ax.grid(False)
    ax.yaxis.set_visible(False)

    # Filter data for this period
    period_data = goals_data[goals_data['period'] == period]

    # Set appropriate x-axis limit for the period
    if period < 4:
        max_time = 1200  # 20 minutes in seconds
        # Set ticks at 5-minute intervals (300 seconds)
        ax.set_xticks(np.arange(0, 1201, 300))
    else:
        max_time = 300  # 5 minutes in seconds
        # For overtime, set ticks at 0 and 5 minutes
        ax.set_xticks([0, 300])

    if len(period_data) == 0:
        ax.text(0.5, 0.5, f"No data for {period_names[period]}",
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=12)
        ax.set_xlim(0, max_time)
    else:
        # Plot the KDE if enough data points exist
        if len(period_data) >= 3:
            sns.kdeplot(
                data=period_data,
                x='seconds',
                fill=True,
                alpha=0.7,
                color=colors[i],
                bw_adjust=0.8,
                ax=ax
            )

        # Always show the data points with a rug plot
        sns.rugplot(
            data=period_data,
            x='seconds',
            color=colors[i],
            height=0.1,
            ax=ax
        )
        ax.set_xlim(0, max_time)

    # Set the title for each subplot
    ax.set_title(f"{period_names[period]}\n(n={len(period_data)})", fontsize=12)

    # Format x-axis ticks to MM:SS
    ax.xaxis.set_major_formatter(plt.FuncFormatter(
        lambda x, pos: f"{int(x // 60):02d}:{int(x % 60):02d}"
    ))

    # Remove top and right spines for a cleaner look
    sns.despine(ax=ax)

    # Remove x-axis title by setting it to empty string
    ax.set_xlabel('')

# Group the subplots by sharing a common x-axis label
fig.text(0.5, 0.04, 'Time (MM:SS)', ha='center', fontsize=12)

# Add a main title with the season name
plt.suptitle(f"Timing of Goals by Period in the {season_name}", fontsize=16, y=0.98)
plt.tight_layout(rect=[0, 0.05, 1, 0.95])
plt.savefig('example_5-goal_timing.svg', format='svg')
plt.show()

conn.close()
```

</details>

![goal_timing.svg](/examples/example_5-goal_timing.svg)

### Timing of Goals

<details>
<summary>Click to expand/collapse code</summary>

```python
import sqlite3
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde
from scipy.ndimage import gaussian_filter
import sys

# Add the examples directory to the Python path so we can import the rink module
sys.path.append('../examples')

# Import the rink drawing function from the existing file
from rink_half import draw_rink


def get_goal_locations(team_id=3, season_id=5):
    """
    Fetch goal locations from the database
    """
    # Connect to the database
    conn = sqlite3.connect("../data/pwhl_data.db")
    cursor = conn.cursor()

    # Query to get goal locations for the specified team and season with team and season names
    query = """
    SELECT g.x_location, g.y_location, g.home, 
           t.code as team_code, s.name as season_name
    FROM pbp_goals g
    JOIN teams t ON g.team_id = t.id
    JOIN seasons s ON g.season_id = s.id
    WHERE g.team_id = ? AND g.season_id = ?
    """
    cursor.execute(query, (team_id, season_id))

    # Fetch all results
    goal_locations = cursor.fetchall()
    conn.close()

    if not goal_locations:
        print(f"No goal data found for team {team_id} in season {season_id}")
        return None

    # Get team_name and season_name from the first row
    team_name = goal_locations[0][3] if goal_locations else "Unknown Team"
    season_name = goal_locations[0][4] if goal_locations else "Unknown Season"

    print(f"Found {len(goal_locations)} goals for {team_name} in {season_name}")
    return goal_locations, team_name, season_name


def plot_goal_contour_on_rink(team_id=3, season_id=5):
    """
    Create a contour plot of goals overlaid on a hockey rink

    Args:
        team_id (int): The ID of the team to analyze
        season_id (int): The ID of the season to analyze
    """
    # Get goal locations and team/season names
    result = get_goal_locations(team_id, season_id)

    if not result:
        return

    goal_locations, team_code, season_name = result

    # Create figure with appropriate size
    fig, ax = plt.subplots(figsize=(5, 6), dpi=300)
    ax.set_aspect('equal')
    ax.axis('off')

    # Draw the rink using the imported function
    draw_rink(ax)

    # Extract x, y values and home status from goal locations
    x_locations_raw = []
    y_locations_raw = []
    home_status = []

    for loc in goal_locations:
        x_locations_raw.append(loc[0])
        y_locations_raw.append(loc[1])
        home_status.append(loc[2])

    x_locations_raw = np.array(x_locations_raw)
    y_locations_raw = np.array(y_locations_raw)
    home_status = np.array(home_status)

    # Print original coordinate ranges
    print(f"Original X range: {min(x_locations_raw)} to {max(x_locations_raw)}")
    print(f"Original Y range: {min(y_locations_raw)} to {max(y_locations_raw)}")

    # Map database coordinates to rink coordinates
    x_locations = x_locations_raw / 600 * 2400
    y_locations = y_locations_raw / 300 * 1020

    # Flip x-coordinates for away games (when home = 0)
    for i in range(len(home_status)):
        if home_status[i] == 0:
            # Flip x-coordinate across the center line (X = 1200)
            x_locations[i] = 2400 - x_locations[i]
            y_locations[i] = 1020 - y_locations[i]

    x_transformed = (y_locations - 1020 / 2) + (1020 / 2)
    y_transformed = (-(x_locations - 2400 / 2))
    x_locations = x_transformed
    y_locations = y_transformed

    # Print mapped coordinate ranges
    print(f"Mapped X range: {min(x_locations)} to {max(x_locations)}")
    print(f"Mapped Y range: {min(y_locations)} to {max(y_locations)}")

    # Add scatter points for each goal
    goal_scatter = ax.scatter(x_locations, y_locations, alpha=0.7, s=30, c='black',
                              edgecolor='white', linewidth=0.5, zorder=10)

    # Increase threshold for contour overlay - require at least 10 data points
    if len(x_locations) >= 10 and len(np.unique(np.vstack([x_locations, y_locations]).T, axis=0)) >= 5:
        # Create a meshgrid for contour plotting
        padding = 0  # Add some padding around the data for the grid
        x_grid = np.linspace(0, 1020, 100)  # Cover the entire rink width
        y_grid = np.linspace(0, 2400 / 2, 100)  # Cover the entire rink height
        X, Y = np.meshgrid(x_grid, y_grid)

        # Calculate the kernel density estimate
        positions = np.vstack([X.ravel(), Y.ravel()])
        values = np.vstack([x_locations, y_locations])

        # Use gaussian_kde for the density estimate with adjusted bandwidth
        kernel = gaussian_kde(values, bw_method='scott')
        Z = np.reshape(kernel(positions), X.shape)
        Z_smoothed = gaussian_filter(Z, sigma=2)

        # Plot the contour with viridis colormap and transparency
        # Define a minimum density threshold (adjust as needed)
        threshold = 0.000001

        # Mask density values below the threshold
        Z_masked = np.ma.masked_less(Z, threshold)

        # Define contour levels starting from the threshold
        levels = np.linspace(threshold, np.max(Z_masked), 15)

        # Plot the contour using the masked array so low-density areas remain transparent
        contour = ax.contourf(X, Y, Z_smoothed, levels=levels, cmap='viridis', alpha=0.7)

    else:
        print("Not enough points for contour plot - displaying scatter plot only")

    # Add title and annotation
    title = f"{team_code} Goals ({season_name})"
    plt.title(title, fontsize=14)

    # Count home and away goals
    home_goals = sum(home_status)
    away_goals = len(home_status) - home_goals

    # Add annotation with data summary
    annotation_text = (
        f"Total Goals: {len(goal_locations)}\n"
        f"Home Goals: {home_goals}\n"
        f"Away Goals: {away_goals}"
    )
    ax.text(0.5, 0.05, annotation_text,
            transform=ax.transAxes,
            verticalalignment='bottom',
            horizontalalignment='center',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.9),
            fontsize=10)

    plt.tight_layout()
    plt.savefig('example_6-goal_map.svg', format='svg')
    plt.show()


if __name__ == "__main__":
    # Call the function with default values (team_id=3, season_id=5)
    plot_goal_contour_on_rink(team_id=3, season_id=5)
```

</details>

![goal_map.svg](/examples/example_7-goal_map.svg)

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
