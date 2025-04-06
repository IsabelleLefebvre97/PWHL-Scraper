import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# Connect to the database
conn = sqlite3.connect("../data/pwhl_data.db")

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
