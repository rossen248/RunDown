from datetime import datetime, timedelta, timezone


def get_last_week_dates():
    today = datetime.now(timezone.utc)
    last_sunday = today - timedelta(days=(today.weekday() + 1) % 7)
    last_monday = last_sunday - timedelta(days=6)
    return last_monday, last_sunday


def get_week_number(date=None):
    """
    Calculate the week number relative to the first week (March 31 - April 6, 2025)

    Args:
        date: The date to calculate week number for. If None, uses the start of last week.

    Returns:
        int: Week number, where week 1 is March 31 - April 6, 2025
    """
    # First week starts on March 31, 2025
    first_week_start = datetime(2025, 3, 31, tzinfo=timezone.utc)

    # If no date specified, use the start of last week
    if date is None:
        today = datetime.now(timezone.utc)
        last_sunday = today - timedelta(days=(today.weekday() + 1) % 7)
        last_monday = last_sunday - timedelta(days=6)
        date = last_monday

    # Calculate days since start date
    days_diff = (date - first_week_start).days

    # Calculate week number (week 1 is March 31 - April 6)
    week_number = (days_diff // 7) + 1

    # If date is before the first week, return 0 or handle as needed
    if week_number < 1:
        return 1

    return week_number
