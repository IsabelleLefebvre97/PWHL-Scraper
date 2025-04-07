import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle, Wedge
from matplotlib.collections import PatchCollection
import matplotlib.path as mpath
import matplotlib.patches as mpatches
import numpy as np


def draw_rink(ax):
    # Rink dimensions
    width = 2400
    height = 1020
    x, y = 0, 0

    # Create a rounded rectangle for the rink outline.
    rink_outline = FancyBboxPatch(
        (x, y),  # Lower left corner of the rectangle
        width,  # Width of the rectangle
        height,  # Height of the rectangle
        boxstyle="round,pad=0,rounding_size=400",
        edgecolor='black',  # Outline color
        facecolor='none',  # No fill color
        lw=1  # Line width of the edge
    )
    ax.add_patch(rink_outline)

    # Calculate the center of the rectangle
    center_x = x + width / 2
    center_y = y + height / 2

    # Neutral zone
    ## Center red line
    center_line = Rectangle((center_x - 6, 0), 12, height,
                            facecolor='#CC3333')
    ax.add_patch(center_line)

    ## Center ice faceoff dot and circle
    center_faceoff_dot = Circle((center_x, center_y), 6,
                                facecolor='#3366CC')
    ax.add_patch(center_faceoff_dot)

    center_faceoff_circle = Circle((center_x, center_y), 180,
                                   edgecolor='#3366CC',
                                   fill=False,
                                   lw=1)
    ax.add_patch(center_faceoff_circle)

    ## Right blue line
    right_blue_line = Rectangle((center_x + 306 - 6, 0), 12, height,
                                facecolor='#3366CC')
    ax.add_patch(right_blue_line)

    ## Left blue line
    left_blue_line = Rectangle((center_x - 306 - 6, 0), 12, height,
                               facecolor='#3366CC')
    ax.add_patch(left_blue_line)

    ## Upper right faceoff dot
    neutral_upper_right_faceoff_dot = Circle((center_x + 240, center_y + 264), 12,
                                             facecolor='#CC3333')
    ax.add_patch(neutral_upper_right_faceoff_dot)

    ## Lower right faceoff dot
    neutral_lower_right_faceoff_dot = Circle((center_x + 240, center_y - 264), 12,
                                             facecolor='#CC3333')
    ax.add_patch(neutral_lower_right_faceoff_dot)

    ## Upper left faceoff dot
    neutral_upper_left_faceoff_dot = Circle((center_x - 240, center_y + 264), 12,
                                            facecolor='#CC3333')
    ax.add_patch(neutral_upper_left_faceoff_dot)

    ## Lower left faceoff dot
    neutral_lower_left_faceoff_dot = Circle((center_x - 240, center_y - 264), 12,
                                            facecolor='#CC3333')
    ax.add_patch(neutral_lower_left_faceoff_dot)

    # Attacking zone
    ## Upper right faceoff dot and circle
    attacking_upper_right_faceoff_dot = Circle((center_x + 828, center_y + 264), 12,
                                               facecolor='#CC3333')
    ax.add_patch(attacking_upper_right_faceoff_dot)

    attacking_upper_right_faceoff_circle = Circle((center_x + 828, center_y + 264), 180,
                                                  edgecolor='#CC3333',
                                                  fill=False,
                                                  lw=1)
    ax.add_patch(attacking_upper_right_faceoff_circle)

    attacking_upper_right_hashmarks = [
        Rectangle((center_x + 828 - 32, center_y + 264 + 179), 4, 25),
        Rectangle((center_x + 828 + 32, center_y + 264 + 179), 4, 25),
        Rectangle((center_x + 828 - 32, center_y + 264 - 179 - 25), 4, 25),
        Rectangle((center_x + 828 + 32, center_y + 264 - 179 - 25), 4, 25),
        # UL
        Rectangle((center_x + 828 - 26, center_y + 264 + 10), 4, 36),
        Rectangle((center_x + 828 - 26 - 48, center_y + 264 + 10), 48, 4),
        # UR
        Rectangle((center_x + 828 + 26 - 2, center_y + 264 + 10), 4, 36),
        Rectangle((center_x + 828 + 26 - 2, center_y + 264 + 10), 48, 4),
        # BL
        Rectangle((center_x + 828 - 26, center_y + 264 - 10 - 32), 4, 36),
        Rectangle((center_x + 828 - 26 - 48, center_y + 264 - 10), 48, 4),
        # BR
        Rectangle((center_x + 828 + 26 - 2, center_y + 264 - 10 - 32), 4, 36),
        Rectangle((center_x + 828 + 26 - 2, center_y + 264 - 10), 48, 4),
    ]
    attacking_upper_right_hashmarks_collection = PatchCollection(attacking_upper_right_hashmarks,
                                                                 facecolor='#CC3333',
                                                                 edgecolor='none')
    ax.add_collection(attacking_upper_right_hashmarks_collection)

    ## Lower right faceoff dot and circle
    attacking_lower_right_faceoff_dot = Circle((center_x + 828, center_y - 264), 12,
                                               facecolor='#CC3333')
    ax.add_patch(attacking_lower_right_faceoff_dot)

    attacking_lower_right_faceoff_circle = Circle((center_x + 828, center_y - 264), 180,
                                                  edgecolor='#CC3333',
                                                  fill=False,
                                                  lw=1)
    ax.add_patch(attacking_lower_right_faceoff_circle)

    attacking_lower_right_hashmarks = [
        Rectangle((center_x + 828 - 32, center_y - 264 + 179), 4, 25),
        Rectangle((center_x + 828 + 32, center_y - 264 + 179), 4, 25),
        Rectangle((center_x + 828 - 32, center_y - 264 - 179 - 25), 4, 25),
        Rectangle((center_x + 828 + 32, center_y - 264 - 179 - 25), 4, 25),
        # UL
        Rectangle((center_x + 828 - 26, center_y - 264 + 10), 4, 36),
        Rectangle((center_x + 828 - 26 - 48, center_y - 264 + 10), 48, 4),
        # UR
        Rectangle((center_x + 828 + 26 - 2, center_y - 264 + 10), 4, 36),
        Rectangle((center_x + 828 + 26 - 2, center_y - 264 + 10), 48, 4),
        # BL
        Rectangle((center_x + 828 - 26, center_y - 264 - 10 - 32), 4, 36),
        Rectangle((center_x + 828 - 26 - 48, center_y - 264 - 10), 48, 4),
        # BR
        Rectangle((center_x + 828 + 26 - 2, center_y - 264 - 10 - 32), 4, 36),
        Rectangle((center_x + 828 + 26 - 2, center_y - 264 - 10), 48, 4),
    ]
    attacking_lower_right_hashmarks_collection = PatchCollection(attacking_lower_right_hashmarks,
                                                                 facecolor='#CC3333',
                                                                 edgecolor='none')
    ax.add_collection(attacking_lower_right_hashmarks_collection)

    ## Right goal
    attacking_right_goal = Rectangle((center_x + 1068, center_y - 36), 38, 72,
                                     edgecolor='black', facecolor='none', lw=1)
    ax.add_patch(attacking_right_goal)

    ## Right goal crease
    attacking_right_goal_crease = Wedge((center_x + 1068, center_y), 72, 90, 270,
                                        edgecolor='#CC3333', facecolor='#3366CC', lw=1)
    ax.add_patch(attacking_right_goal_crease)

    ## Right goal line
    right_goal_line = Rectangle((center_x + 1068 - 2, 0), 4, height,
                                facecolor='#CC3333')
    right_goal_line.set_clip_path(rink_outline)
    ax.add_patch(right_goal_line)

    # Defensive zone
    ## Upper left faceoff dot and circle
    defensive_upper_left_faceoff_dot = Circle((center_x - 828, center_y + 264), 12,
                                              facecolor='#CC3333')
    ax.add_patch(defensive_upper_left_faceoff_dot)

    defensive_upper_left_faceoff_circle = Circle((center_x - 828, center_y + 264), 180,
                                                 edgecolor='#CC3333',
                                                 fill=False,
                                                 lw=1)
    ax.add_patch(defensive_upper_left_faceoff_circle)

    defensive_upper_left_hashmarks = [
        Rectangle((center_x - 828 - 32, center_y + 264 + 179), 4, 25),
        Rectangle((center_x - 828 + 32, center_y + 264 + 179), 4, 25),
        Rectangle((center_x - 828 - 32, center_y + 264 - 179 - 25), 4, 25),
        Rectangle((center_x - 828 + 32, center_y + 264 - 179 - 25), 4, 25),
        # UL
        Rectangle((center_x - 828 - 26, center_y + 264 + 10), 4, 36),
        Rectangle((center_x - 828 - 26 - 48, center_y + 264 + 10), 48, 4),
        # UR
        Rectangle((center_x - 828 + 26 - 2, center_y + 264 + 10), 4, 36),
        Rectangle((center_x - 828 + 26 - 2, center_y + 264 + 10), 48, 4),
        # BL
        Rectangle((center_x - 828 - 26, center_y + 264 - 10 - 32), 4, 36),
        Rectangle((center_x - 828 - 26 - 48, center_y + 264 - 10), 48, 4),
        # BR
        Rectangle((center_x - 828 + 26 - 2, center_y + 264 - 10 - 32), 4, 36),
        Rectangle((center_x - 828 + 26 - 2, center_y + 264 - 10), 48, 4),
    ]
    defensive_upper_left_hashmarks_collection = PatchCollection(defensive_upper_left_hashmarks,
                                                                facecolor='#CC3333',
                                                                edgecolor='none')
    ax.add_collection(defensive_upper_left_hashmarks_collection)

    ## Lower left faceoff dot and circle
    defensive_lower_left_faceoff_dot = Circle((center_x - 828, center_y - 264), 12,
                                              facecolor='#CC3333')
    ax.add_patch(defensive_lower_left_faceoff_dot)

    defensive_lower_left_faceoff_circle = Circle((center_x - 828, center_y - 264), 180,
                                                 edgecolor='#CC3333',
                                                 fill=False,
                                                 lw=1)
    ax.add_patch(defensive_lower_left_faceoff_circle)

    defensive_lower_left_hashmarks = [
        Rectangle((center_x - 828 - 32, center_y - 264 + 179), 4, 25),
        Rectangle((center_x - 828 + 32, center_y - 264 + 179), 4, 25),
        Rectangle((center_x - 828 - 32, center_y - 264 - 179 - 25), 4, 25),
        Rectangle((center_x - 828 + 32, center_y - 264 - 179 - 25), 4, 25),
        # UL
        Rectangle((center_x - 828 - 26, center_y - 264 + 10), 4, 36),
        Rectangle((center_x - 828 - 26 - 48, center_y - 264 + 10), 48, 4),
        # UR
        Rectangle((center_x - 828 + 26 - 2, center_y - 264 + 10), 4, 36),
        Rectangle((center_x - 828 + 26 - 2, center_y - 264 + 10), 48, 4),
        # BL
        Rectangle((center_x - 828 - 26, center_y - 264 - 10 - 32), 4, 36),
        Rectangle((center_x - 828 - 26 - 48, center_y - 264 - 10), 48, 4),
        # BR
        Rectangle((center_x - 828 + 26 - 2, center_y - 264 - 10 - 32), 4, 36),
        Rectangle((center_x - 828 + 26 - 2, center_y - 264 - 10), 48, 4),
    ]
    defensive_lower_left_hashmarks_collection = PatchCollection(defensive_lower_left_hashmarks,
                                                                facecolor='#CC3333',
                                                                edgecolor='none')
    ax.add_collection(defensive_lower_left_hashmarks_collection)

    ## Left goal
    defensive_left_goal = Rectangle((center_x - 1068 - 38, center_y - 36), 38, 72,
                                    edgecolor='black', facecolor='none', lw=1)
    ax.add_patch(defensive_left_goal)

    ## Left goal crease
    defensive_left_goal_crease = Wedge((center_x - 1068, center_y), 72, -90, 90,
                                       edgecolor='#CC3333', facecolor='#3366CC', lw=1)
    ax.add_patch(defensive_left_goal_crease)

    ## Left goal line
    right_goal_line = Rectangle((center_x - 1068 - 2, 0), 4, height,
                                facecolor='#CC3333')
    right_goal_line.set_clip_path(rink_outline)
    ax.add_patch(right_goal_line)

    # Set limits so that the entire rectangle is visible
    ax.set_xlim(-100, width + 100)
    ax.set_ylim(-100, height + 100)


# Main code: create the figure, call draw_rink, and display.
fig, ax = plt.subplots(figsize=(9, 5), dpi=500)
ax.set_aspect('equal')
ax.axis('off')  # Hide the axes

draw_rink(ax)
