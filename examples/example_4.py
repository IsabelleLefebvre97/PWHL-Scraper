import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# Connect to the database
conn = sqlite3.connect("../data/pwhl_data.db")

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

# First get all teams to know how many we're dealing with
teams_query = """
SELECT id, name, code
FROM teams
WHERE teams.id IN (
    SELECT DISTINCT home_team FROM games WHERE season_id = 5
    UNION 
    SELECT DISTINCT visiting_team FROM games WHERE season_id = 5
)
"""
teams_df = pd.read_sql_query(teams_query, conn)

# Get all games for the season
games_query = """
SELECT 
    g.id,
    g.date,
    g.game_number,
    g.home_team,
    g.visiting_team,
    g.home_goal_count,
    g.visiting_goal_count,
    g.overtime,
    g.shootout,
    g.game_status,
    t1.name as home_team_name,
    t1.code as home_team_code,
    t2.name as away_team_name,
    t2.code as away_team_code,
    s.id as season_id,
    s.name as season_name
FROM games g
JOIN teams t1 ON g.home_team = t1.id
JOIN teams t2 ON g.visiting_team = t2.id
JOIN seasons s ON g.season_id = s.id
WHERE g.season_id = 5 AND g.status = 4
ORDER BY g.date, g.id
"""
games_df = pd.read_sql_query(games_query, conn)
season_name = games_df['season_name'].iloc[0]


# Calculate points for each game
def calculate_points(row):
    # Home team points
    if row['home_goal_count'] > row['visiting_goal_count']:
        if not row['overtime'] and not row['shootout']:
            home_points = 3  # Regulation win
        else:
            home_points = 2  # OT/SO win
        away_points = 0 if not (row['overtime'] or row['shootout']) else 1
    else:
        if not row['overtime'] and not row['shootout']:
            home_points = 0  # Regulation loss
        else:
            home_points = 1  # OT/SO loss
        away_points = 3 if not (row['overtime'] or row['shootout']) else 2

    return pd.Series([home_points, away_points])


games_df[['home_points', 'away_points']] = games_df.apply(calculate_points, axis=1)

# Create a points history for each team
team_points = {}
for _, team in teams_df.iterrows():
    team_id = team['id']
    team_name = team['name']
    # Use the team_colors dictionary instead of database field
    team_color = team_colors.get(team_id, default_color)

    # Filter games for this team
    home_games = games_df[games_df['home_team'] == team_id].copy()
    away_games = games_df[games_df['visiting_team'] == team_id].copy()

    # Create a dataframe with game numbers and points
    home_points = pd.DataFrame({
        'game_number': home_games['game_number'],
        'date': home_games['date'],
        'points': home_games['home_points']
    })

    away_points = pd.DataFrame({
        'game_number': away_games['game_number'],
        'date': away_games['date'],
        'points': away_games['away_points']
    })

    # Combine home and away games
    all_points = pd.concat([home_points, away_points])
    all_points = all_points.sort_values('date')

    # Calculate running total and points above pace
    all_points['total_points'] = all_points['points'].cumsum()
    all_points['games_played'] = range(len(all_points))
    all_points['max_possible'] = (all_points['games_played'] + 1) * 3
    all_points['pace_points'] = (all_points['games_played'] + 1) * 1.5  # Average pace (1.5 points per game)
    all_points['points_above_pace'] = all_points['total_points'] - all_points['pace_points']

    team_points[team_name] = {
        'data': all_points,
        'color': team_color
    }

# Plot points above pace for each team
plt.figure(figsize=(14, 8))

for team_name, team_data in team_points.items():
    data = team_data['data']
    color = team_data['color']
    plt.plot(data['games_played'], data['points_above_pace'], marker='o',
             label=team_name, color=color, linewidth=3)

# Add reference line at y=0 (exactly on pace)
plt.axhline(y=0, color='black', linestyle='--', alpha=0.5)

plt.xlabel('Games Played')
plt.ylabel('Points Above Pace')
plt.title(f"PWHL Team Performance: Points Above Pace ({season_name})")
plt.grid(True, alpha=0.3)
plt.legend(loc='best')

# Add x-axis gridlines at regular intervals
max_games = max([len(team_data['data']) for team_data in team_points.values()])
plt.xticks(range(0, max_games + 1, 2))

plt.tight_layout()
plt.savefig('example_4-points_above_pace.svg', format='svg')
plt.show()

# Close connection
conn.close()
