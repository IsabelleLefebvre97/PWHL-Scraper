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


def get_shot_locations(goalie_id=28, season_id=5):
    """
    Fetch shot locations from the database
    """
    # Connect to the database
    conn = sqlite3.connect("../data/pwhl_data.db")
    cursor = conn.cursor()

    # Query to get shot locations against the specified goalie and season with goalie and season names
    query = """
    SELECT g.x_location, g.y_location, g.home, g.game_goal_id,
           p.last_name as last_name, s.name as season_name
    FROM pbp_shots g
    JOIN players p ON g.goalie_id = p.id
    JOIN seasons s ON g.season_id = s.id
    WHERE g.goalie_id = ? AND g.season_id = ?
    """
    cursor.execute(query, (goalie_id, season_id))

    # Fetch all results
    shot_locations = cursor.fetchall()
    conn.close()

    if not shot_locations:
        print(f"No shot data found against goalie {goalie_id} in season {season_id}")
        return None

    # Get goalie name and season name from the first row
    goalie_name = shot_locations[0][4] if shot_locations else "Unknown Goalie"
    season_name = shot_locations[0][5] if shot_locations else "Unknown Season"

    print(f"Found {len(shot_locations)} shots against {goalie_name} in {season_name}")
    return shot_locations, goalie_name, season_name


def plot_shot_contour_on_rink(goalie_id=28, season_id=5):
    """
    Create a contour plot of shots overlaid on a hockey rink

    Args:
        goalie_id (int): The ID of the goalie to analyze
        season_id (int): The ID of the season to analyze
    """
    # Get shot locations and goalie/season names
    result = get_shot_locations(goalie_id, season_id)

    if not result:
        return

    shot_locations, goalie_id, season_name = result

    # Create figure with appropriate size
    fig, ax = plt.subplots(figsize=(5, 6), dpi=300)
    ax.set_aspect('equal')
    ax.axis('off')

    # Draw the rink using the imported function
    draw_rink(ax)

    # Extract x, y values and home status from shot locations
    x_locations_raw = []
    y_locations_raw = []
    home_status = []
    game_goal_id = []

    for loc in shot_locations:
        x_locations_raw.append(loc[0])
        y_locations_raw.append(loc[1])
        home_status.append(loc[2])
        game_goal_id.append(loc[3])

    x_locations_raw = np.array(x_locations_raw)
    y_locations_raw = np.array(y_locations_raw)
    home_status = np.array(home_status)
    game_goal_id = np.array(game_goal_id)

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

    valid_indices = y_locations >= 0
    x_locations = x_locations[valid_indices]
    y_locations = y_locations[valid_indices]
    home_status = home_status[valid_indices]
    game_goal_id = game_goal_id[valid_indices]

    print(f"Removed {len(y_transformed) - len(y_locations)} points with y < 0")

    # Print mapped coordinate ranges
    print(f"Mapped X range: {min(x_locations)} to {max(x_locations)}")
    print(f"Mapped Y range: {min(y_locations)} to {max(y_locations)}")

    # Add scatter points for each shot
    is_goal = np.array([gid is not None for gid in game_goal_id])
    goal_count = sum(is_goal)

    # Plot non-goals
    ax.scatter(x_locations[~is_goal], y_locations[~is_goal],
               alpha=0.7, s=30, c='black', edgecolor='white',
               linewidth=0.5, zorder=10, label='Shots')

    # Plot goals with different color/shape
    ax.scatter(x_locations[is_goal], y_locations[is_goal],
               alpha=0.9, s=100, c='red', marker='*',
               edgecolor='white', linewidth=0.8, zorder=11, label='Goals')

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
        ax.contourf(X, Y, Z_smoothed, levels=levels, cmap='viridis', alpha=0.7)

    else:
        print("Not enough points for contour plot - displaying scatter plot only")

    # Add title and annotation
    title = f"Shots Against {goalie_id} ({season_name})"
    plt.title(title, fontsize=14)

    ax.legend(loc='upper center', bbox_to_anchor=(0.5, 0.05), ncol=2)

    # Add annotation with data summary
    annotation_text = (
        f"Shots Against: {len(shot_locations)}\n"
        f"Goals Against: {goal_count}"
    )
    ax.text(0.5, 0.1, annotation_text,
            transform=ax.transAxes,
            verticalalignment='bottom',
            horizontalalignment='center',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.9),
            fontsize=10)

    plt.tight_layout()
    plt.savefig('example_6-shot_map.svg', format='svg')
    plt.show()


if __name__ == "__main__":
    # Call the function with default values (goalie_id=28, season_id=5)
    plot_shot_contour_on_rink(goalie_id=28, season_id=5)
