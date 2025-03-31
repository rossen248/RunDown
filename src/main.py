import datetime

from strava_client.auth import authenticate_strava


def main():
    # Authenticate
    client = authenticate_strava()

    # # Get activities
    # start_date, end_date = get_last_week_dates()
    # activities = client.get_activities(after=start_date, before=end_date)

    start_date = datetime.datetime(2025, 3, 17)
    end_date = datetime.datetime(2025, 3, 24)
    activities = client.get_activities(after=start_date, before=end_date)
    print(f"Fetching activities between: {start_date} and {end_date}")

    # Filter runs
    runs = [a for a in activities if a.type == 'Run']

    if not runs:
        print("No runs to report this week!")
        return

    print(f"Found {len(runs)} runs:\n")
    for idx, run in enumerate(runs, 1):
        print(f"Run #{idx}: {run.name}")
        print(f"  Date: {run.start_date}")
        print(f"  Distance: {run.distance / 1000:.2f} km")
        print(f"  Duration: {run.moving_time / 60:.1f} minutes")
        print(f"  Average Speed: {run.average_speed * 3.6:.1f} km/h")  # Convert m/s to km/h
        print(f"  Elevation Gain: {run.total_elevation_gain:.0f} m")
        print("-" * 60)


if __name__ == "__main__":
    main()
