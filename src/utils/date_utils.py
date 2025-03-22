from datetime import datetime, timedelta

def get_last_week_dates():
    today = datetime.now()
    last_sunday = today - timedelta(days=(today.weekday() + 1) % 7)
    last_monday = last_sunday - timedelta(days=6)
    return last_monday.date(), last_sunday.date()