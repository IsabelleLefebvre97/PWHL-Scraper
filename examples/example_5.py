import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.gridspec import GridSpec
import numpy as np

# Connect to the database
conn = sqlite3.connect("../data/pwhl_data.db")

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
plt.suptitle(f"Timing of Goals by Period ({season_name})", fontsize=16, y=0.98)
plt.tight_layout(rect=[0, 0.05, 1, 0.95])
plt.savefig('example_5-goal_timing.svg', format='svg')
plt.show()

conn.close()
