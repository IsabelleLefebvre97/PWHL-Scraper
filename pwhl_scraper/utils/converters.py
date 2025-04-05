"""
Data conversion utilities for PWHL Scraper.
"""
import re
import logging
from typing import Dict, Any, Optional, Tuple, Union

logger = logging.getLogger(__name__)


def convert_time_to_seconds(time_string: Optional[str]) -> int:
    """
    Convert a time string in the format MM:SS to total seconds.

    Args:
        time_string: Time string in MM:SS format

    Returns:
        Total seconds as integer
    """
    if not time_string:
        return 0

    try:
        parts = time_string.split(':')
        if len(parts) == 2:
            minutes, seconds = int(parts[0]), int(parts[1])
            return minutes * 60 + seconds
        elif len(parts) == 3:  # HH:MM:SS format
            hours, minutes, seconds = int(parts[0]), int(parts[1]), int(parts[2])
            return hours * 3600 + minutes * 60 + seconds
        return 0
    except (ValueError, TypeError) as e:
        logger.warning(f"Error converting time '{time_string}' to seconds: {e}")
        return 0


def get_period_number(period_obj: Union[str, Dict[str, Any], int]) -> int:
    """
    Convert period object to period number.

    Args:
        period_obj: Period identifier (string, dict, or int)

    Returns:
        Integer period number
    """
    if isinstance(period_obj, dict):
        period_id = period_obj.get("id")
    else:
        period_id = period_obj

    if period_id in ("OT1", "4"):
        return 4
    elif period_id in ("OT2", "5"):
        return 5
    elif period_id in ("OT3", "6"):
        return 6
    elif period_id == "SO":
        return 7
    else:
        try:
            return int(period_id)
        except (ValueError, TypeError):
            logger.warning(f"Unknown period format: {period_obj}, defaulting to 1")
            return 1


def extract_height_weight(height: Optional[str], weight: Optional[str]) -> Tuple[Optional[int], Optional[int]]:
    """
    Extract height in cm and weight in kg from strings.

    Args:
        height: Height string (e.g., "5' 10\"")
        weight: Weight string (e.g., "185 lbs")

    Returns:
        Tuple of (height_cm, weight_kg)
    """
    height_cm = None
    weight_kg = None

    # Process height
    if height:
        try:
            # Format typically "5' 10\""
            feet_inches = height.replace('"', '').replace("'", ' ').strip().split()
            if len(feet_inches) == 2:
                feet, inches = int(feet_inches[0]), int(feet_inches[1])
                height_cm = round((feet * 30.48) + (inches * 2.54))
        except Exception as e:
            logger.warning(f"Error converting height '{height}' to cm: {e}")

    # Process weight
    if weight:
        try:
            # Weight typically in lbs
            weight_lbs = int(''.join(c for c in weight if c.isdigit()))
            weight_kg = round(weight_lbs * 0.453592)
        except Exception as e:
            logger.warning(f"Error converting weight '{weight}' to kg: {e}")

    return height_cm, weight_kg


def extract_hometown_parts(birth_place: Optional[str]) -> Tuple[str, str]:
    """
    Split the birthPlace into hometown and hometown_div.

    Args:
        birth_place: Birth place string (e.g., "Kleinburg, Ontario, Canada")

    Returns:
        Tuple of (hometown, hometown_div)
    """
    if not birth_place:
        return "", ""

    if "," in birth_place:
        parts = birth_place.split(",", 1)  # Split only on the first comma
        hometown = parts[0].strip()
        hometown_div = parts[1].strip()
    else:
        hometown = birth_place.strip()
        hometown_div = ""

    return hometown, hometown_div


def extract_team_id_from_url(team_image_url: Optional[str]) -> Optional[int]:
    """
    Extract team ID from team image URL.

    Args:
        team_image_url: URL to team image

    Returns:
        Team ID as integer or None if not found
    """
    if not team_image_url:
        return None

    # Match pattern like "/logos/123_5.png"
    match = re.search(r"/logos/(\d+)_\d+\.png", team_image_url)
    return int(match.group(1)) if match else None


def determine_team_info(event_team_id: Optional[Union[str, int]],
                        home_team_id: int,
                        visitor_team_id: int) -> Tuple[int, bool, int]:
    """
    Determine team ID, whether it's home team, and the opponent team ID.

    Args:
        event_team_id: Team ID from event
        home_team_id: Home team ID
        visitor_team_id: Visitor team ID

    Returns:
        Tuple of (team_id, is_home, opponent_id)
    """
    if event_team_id is not None:
        try:
            team_id = int(event_team_id)
            if team_id == home_team_id:
                return team_id, True, visitor_team_id
            elif team_id == visitor_team_id:
                return team_id, False, home_team_id
        except (ValueError, TypeError):
            pass

    # Default to home team if we can't determine
    return home_team_id, True, visitor_team_id


def filter_dict(data: Dict[str, Any], filter_none: bool = True) -> Dict[str, Any]:
    """
    Filter a dictionary to remove None values or other filtering.

    Args:
        data: Dictionary to filter
        filter_none: Whether to remove None values

    Returns:
        Filtered dictionary
    """
    if filter_none:
        return {k: v for k, v in data.items() if v is not None}
    return data


def safe_cast(value: Any, to_type: type, default: Any = None) -> Any:
    """
    Safely cast a value to a specified type.

    Args:
        value: Value to cast
        to_type: Type to cast to
        default: Default value if casting fails

    Returns:
        Cast value or default
    """
    try:
        return to_type(value)
    except (ValueError, TypeError):
        return default
