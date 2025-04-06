import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Connect to the database
conn = sqlite3.connect("../data/pwhl_data.db")

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
