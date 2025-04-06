import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Connect to the database
conn = sqlite3.connect("../data/pwhl_data.db")

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
