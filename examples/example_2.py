import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# Connect to the database
conn = sqlite3.connect("../data/pwhl_data.db")

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
