"""
Date utilities for RunDown - simplified for flexible date handling
"""

from datetime import datetime, timedelta, timezone
from typing import Tuple


def parse_date_input(date_str: str) -> datetime:
    """
    Parse a date string in YYYY-MM-DD format and return a timezone-aware datetime.

    Args:
        date_str: Date string in YYYY-MM-DD format

    Returns:
        datetime: Timezone-aware datetime object

    Raises:
        ValueError: If date string is invalid
    """
    try:
        # Parse the date and make it timezone-aware
        naive_date = datetime.strptime(date_str, '%Y-%m-%d')
        return naive_date.replace(tzinfo=timezone.utc)
    except ValueError:
        raise ValueError(f"Invalid date format: {date_str}. Use YYYY-MM-DD format.")


def get_week_range(reference_date: datetime = None) -> Tuple[datetime, datetime]:
    """
    Get the Monday-Sunday week range for a given date.

    Args:
        reference_date: Date within the desired week. If None, uses last complete week.

    Returns:
        Tuple of (monday_start, sunday_end) as timezone-aware datetimes
    """
    if reference_date is None:
        # Default to last complete week
        today = datetime.now(timezone.utc)
        # Get the most recent Sunday (end of last complete week)
        days_since_sunday = (today.weekday() + 1) % 7
        last_sunday = today - timedelta(days=days_since_sunday)
        reference_date = last_sunday - timedelta(days=3)  # Middle of last week

    # Ensure reference_date is timezone-aware
    if reference_date.tzinfo is None:
        reference_date = reference_date.replace(tzinfo=timezone.utc)

    # Find Monday of the week containing reference_date
    days_since_monday = reference_date.weekday()
    monday = reference_date - timedelta(days=days_since_monday)

    # Find Sunday of the same week
    sunday = monday + timedelta(days=6)

    # Set time to start/end of day
    monday_start = monday.replace(hour=0, minute=0, second=0, microsecond=0)
    sunday_end = sunday.replace(hour=23, minute=59, second=59, microsecond=999999)

    return monday_start, sunday_end


def format_date_range(start_date: datetime, end_date: datetime) -> str:
    """
    Format a date range for display.

    Args:
        start_date: Start of the range
        end_date: End of the range

    Returns:
        Formatted string like "Mar 11 - Mar 17, 2024"
    """
    if start_date.year == end_date.year and start_date.month == end_date.month:
        return f"{start_date.strftime('%b %d')} - {end_date.strftime('%d, %Y')}"
    elif start_date.year == end_date.year:
        return f"{start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}"
    else:
        return f"{start_date.strftime('%b %d, %Y')} - {end_date.strftime('%b %d, %Y')}"


# Backwards compatibility - remove these after updating imports
def get_last_week_dates():
    """DEPRECATED: Use get_week_range() instead"""
    return get_week_range()


def get_week_number(date=None):
    """DEPRECATED: Week numbering removed for simplicity"""
    raise NotImplementedError("Week numbering has been removed. Use date ranges instead.")