"""
Data validation utilities.

Provides validation functions for user inputs and data structures.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

import logging

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Custom exception for validation errors."""

    pass


def validate_destination(destination: str) -> str:
    """
    Validate destination input.

    Args:
        destination: Destination string to validate.

    Returns:
        Validated and cleaned destination string.

    Raises:
        ValidationError: If destination is invalid.
    """
    if not destination or not destination.strip():
        raise ValidationError("Destination cannot be empty")

    cleaned = destination.strip()
    if len(cleaned) < 2:
        raise ValidationError("Destination must be at least 2 characters long")

    if len(cleaned) > 200:
        raise ValidationError("Destination must be less than 200 characters")

    return cleaned


def validate_date(date_str: str) -> datetime:
    """
    Validate and parse date string.

    Args:
        date_str: Date string to validate.

    Returns:
        Parsed datetime object.

    Raises:
        ValidationError: If date is invalid or cannot be parsed.
    """
    if not date_str or not date_str.strip():
        raise ValidationError("Date cannot be empty")

    try:
        # Try common date formats
        formats = ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y-%m-%d %H:%M:%S"]
        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue

        raise ValidationError(f"Date format not recognized: {date_str}")

    except Exception as e:
        if isinstance(e, ValidationError):
            raise
        raise ValidationError(f"Invalid date: {e}") from e


def validate_duration(days: int) -> int:
    """
    Validate trip duration in days.

    Args:
        days: Number of days.

    Returns:
        Validated number of days.

    Raises:
        ValidationError: If duration is invalid.
    """
    if not isinstance(days, int):
        raise ValidationError("Duration must be an integer")

    if days < 1:
        raise ValidationError("Duration must be at least 1 day")

    if days > 365:
        raise ValidationError("Duration cannot exceed 365 days")

    return days


def validate_budget(budget: Optional[float]) -> Optional[float]:
    """
    Validate budget amount.

    Args:
        budget: Budget amount in currency units.

    Returns:
        Validated budget amount.

    Raises:
        ValidationError: If budget is invalid.
    """
    if budget is None:
        return None

    if not isinstance(budget, (int, float)):
        raise ValidationError("Budget must be a number")

    if budget < 0:
        raise ValidationError("Budget cannot be negative")

    if budget > 10000000:  # Reasonable upper limit
        raise ValidationError("Budget exceeds maximum allowed value")

    return float(budget)


def validate_preferences(preferences: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate user preferences dictionary.

    Args:
        preferences: Preferences dictionary to validate.

    Returns:
        Validated preferences dictionary.

    Raises:
        ValidationError: If preferences are invalid.
    """
    if not isinstance(preferences, dict):
        raise ValidationError("Preferences must be a dictionary")

    validated = {}

    # Validate optional fields
    if "interests" in preferences:
        interests = preferences["interests"]
        if isinstance(interests, list):
            validated["interests"] = [str(i) for i in interests if i]
        elif isinstance(interests, str):
            validated["interests"] = [interests] if interests else []
        else:
            validated["interests"] = []

    if "travel_style" in preferences:
        travel_style = str(preferences["travel_style"])
        if travel_style:
            validated["travel_style"] = travel_style

    if "accommodation_type" in preferences:
        acc_type = str(preferences["accommodation_type"])
        if acc_type:
            validated["accommodation_type"] = acc_type

    if "dietary_restrictions" in preferences:
        dietary = preferences["dietary_restrictions"]
        if isinstance(dietary, list):
            validated["dietary_restrictions"] = [str(d) for d in dietary if d]
        elif isinstance(dietary, str):
            validated["dietary_restrictions"] = [dietary] if dietary else []
        else:
            validated["dietary_restrictions"] = []

    return validated

