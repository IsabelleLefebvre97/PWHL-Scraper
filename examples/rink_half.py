import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, Wedge
from matplotlib.collections import PatchCollection
import matplotlib.path as mpath
import matplotlib.patches as mpatches
import numpy as np


def draw_rink(ax):
    """
    Draws a half-rink with a rounded rectangle background and additional markings
    on the provided axis.
    """
    # Rink dimensions
    width = 1020
    height = 1200
    x, y = 0, 0

    # --- Draw the half-rink outline as a half-rounded rectangle ---
    r = 350  # Rounding radius for the top corners
    n_arc = 20  # Number of points to approximate each arc
    Path = mpath.Path

    # Build vertices and codes for the half-rounded rectangle:
    verts = []
    codes = []

    # Start at bottom-left corner
    verts.append((x, y))
    codes.append(Path.MOVETO)

    # Bottom edge: straight line to bottom-right corner
    verts.append((x + width, y))
    codes.append(Path.LINETO)

    # Right edge: straight line up to the start of the top-right arc
    verts.append((x + width, y + height - r))
    codes.append(Path.LINETO)

    # Top-right arc (from 0° to 90°) centered at (x+width - r, y+height - r)
    angles = np.linspace(0, np.pi / 2, n_arc)
    for angle in angles:
        verts.append(((x + width - r) + r * np.cos(angle),
                      (y + height - r) + r * np.sin(angle)))
        codes.append(Path.LINETO)

    # Top edge: straight line to the start of the top-left arc
    verts.append((x + r, y + height))
    codes.append(Path.LINETO)

    # Top-left arc (from 90° to 180°) centered at (x + r, y + height - r)
    angles = np.linspace(np.pi / 2, np.pi, n_arc)
    for angle in angles:
        verts.append(((x + r) + r * np.cos(angle),
                      (y + height - r) + r * np.sin(angle)))
        codes.append(Path.LINETO)

    # Left edge: straight line down to the bottom-left corner
    verts.append((x, y))
    codes.append(Path.LINETO)

    # Create and add the patch for the half-rink outline.
    custom_path = mpath.Path(verts, codes)
    half_rounded_patch = mpatches.PathPatch(custom_path, facecolor='none', edgecolor='black', lw=1)
    ax.add_patch(half_rounded_patch)

    # Calculate the center of the rectangle
    center_x = x + width / 2

    # --- Neutral Zone Markings ---
    ## Center ice faceoff circle (drawn at the bottom)
    center_faceoff_circle = Wedge((center_x, 0), 180, 0, 180,
                                  edgecolor='#3366CC', fill=False, lw=1)
    ax.add_patch(center_faceoff_circle)

    ## Center red line
    center_line = Rectangle((0, -6), width, 12,
                            facecolor='#CC3333')
    ax.add_patch(center_line)

    ## Center ice faceoff dot
    center_faceoff_dot = Circle((center_x, 0), 6,
                                facecolor='#3366CC')
    ax.add_patch(center_faceoff_dot)

    ## Blue line
    right_blue_line = Rectangle((0, 306 - 6), width, 12,
                                facecolor='#3366CC')
    ax.add_patch(right_blue_line)

    ## Upper right faceoff dot
    neutral_upper_right_faceoff_dot = Circle((center_x + 264, 240), 12,
                                             facecolor='#CC3333')
    ax.add_patch(neutral_upper_right_faceoff_dot)

    ## Lower right faceoff dot
    neutral_lower_right_faceoff_dot = Circle((center_x - 264, 240), 12,
                                             facecolor='#CC3333')
    ax.add_patch(neutral_lower_right_faceoff_dot)

    # --- Attacking Zone Markings ---
    ## Upper right faceoff dot and circle
    attacking_upper_right_faceoff_dot = Circle((center_x + 264, 828), 12,
                                               facecolor='#CC3333')
    ax.add_patch(attacking_upper_right_faceoff_dot)

    attacking_upper_right_faceoff_circle = Circle((center_x + 264, 828), 180,
                                                  edgecolor='#CC3333',
                                                  fill=False,
                                                  lw=1)
    ax.add_patch(attacking_upper_right_faceoff_circle)

    attacking_upper_right_hashmarks = [
        Rectangle((center_x + 264 + 179, 828 - 32), 25, 4),
        Rectangle((center_x + 264 + 179, 828 + 32), 25, 4),
        Rectangle((center_x + 264 - 179 - 25, 828 - 32), 25, 4),
        Rectangle((center_x + 264 - 179 - 25, 828 + 32), 25, 4),
        # UL
        Rectangle((center_x + 264 + 10, 828 - 26), 36, 4),
        Rectangle((center_x + 264 + 10, 828 - 26 - 48), 4, 48),
        # UR
        Rectangle((center_x + 264 + 10, 828 + 26 - 2), 36, 4),
        Rectangle((center_x + 264 + 10, 828 + 26 - 2), 4, 48),
        # BL
        Rectangle((center_x + 264 - 10 - 32, 828 - 26), 36, 4),
        Rectangle((center_x + 264 - 10, 828 - 26 - 48), 4, 48),
        # BR
        Rectangle((center_x + 264 - 10 - 32, 828 + 26 - 2), 36, 4),
        Rectangle((center_x + 264 - 10, 828 + 26 - 2), 4, 48),
    ]
    attacking_upper_right_hashmarks_collection = PatchCollection(attacking_upper_right_hashmarks,
                                                                 facecolor='#CC3333',
                                                                 edgecolor='none')
    ax.add_collection(attacking_upper_right_hashmarks_collection)

    ## Lower right faceoff dot and circle
    attacking_lower_right_faceoff_dot = Circle((center_x - 264, 828), 12,
                                               facecolor='#CC3333')
    ax.add_patch(attacking_lower_right_faceoff_dot)

    attacking_lower_right_faceoff_circle = Circle((center_x - 264, 828), 180,
                                                  edgecolor='#CC3333',
                                                  fill=False,
                                                  lw=1)
    ax.add_patch(attacking_lower_right_faceoff_circle)

    attacking_lower_right_hashmarks = [
        Rectangle((center_x - 264 + 179, 828 - 32), 25, 4),
        Rectangle((center_x - 264 + 179, 828 + 32), 25, 4),
        Rectangle((center_x - 264 - 179 - 25, 828 - 32), 25, 4),
        Rectangle((center_x - 264 - 179 - 25, 828 + 32), 25, 4),
        # UL
        Rectangle((center_x - 264 + 10, 828 - 26), 36, 4),
        Rectangle((center_x - 264 + 10, 828 - 26 - 48), 4, 48),
        # UR
        Rectangle((center_x - 264 + 10, 828 + 26 - 2), 36, 4),
        Rectangle((center_x - 264 + 10, 828 + 26 - 2), 4, 48),
        # BL
        Rectangle((center_x - 264 - 10 - 32, 828 - 26), 36, 4),
        Rectangle((center_x - 264 - 10, 828 - 26 - 48), 4, 48),
        # BR
        Rectangle((center_x - 264 - 10 - 32, 828 + 26 - 2), 36, 4),
        Rectangle((center_x - 264 - 10, 828 + 26 - 2), 4, 48),
    ]
    attacking_lower_right_hashmarks_collection = PatchCollection(attacking_lower_right_hashmarks,
                                                                 facecolor='#CC3333',
                                                                 edgecolor='none')
    ax.add_collection(attacking_lower_right_hashmarks_collection)

    ## Right goal
    attacking_right_goal = Rectangle((center_x - 36, 1068), 72, 38,
                                     edgecolor='black', facecolor='none', lw=1)
    ax.add_patch(attacking_right_goal)

    ## Right goal crease
    attacking_right_goal_crease = Wedge((center_x, 1068), 72, 180, 0,
                                        edgecolor='#CC3333', facecolor='#3366CC', lw=1)
    ax.add_patch(attacking_right_goal_crease)

    ## Right goal line
    right_goal_line = Rectangle((0, 1068 - 2), width, 4,
                                facecolor='#CC3333')
    right_goal_line.set_clip_path(half_rounded_patch)
    ax.add_patch(right_goal_line)

    # Set limits so that the entire figure is visible
    ax.set_xlim(-100, width + 100)
    ax.set_ylim(-100, height + 100)


# Main code: create the figure, draw the rink, then display it.
fig, ax = plt.subplots(figsize=(5, 6), dpi=500)
ax.set_aspect('equal')
ax.axis('off')  # Hide the axes

draw_rink(ax)
