from datetime import datetime, timedelta, timezone

def get_last_week_dates():
    today = datetime.now(timezone.utc)
    last_sunday = today - timedelta(days=(today.weekday() + 1) % 7)
    last_monday = last_sunday - timedelta(days=6)
    return last_monday, last_sunday
