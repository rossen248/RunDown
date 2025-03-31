from strava_client.auth import authenticate_strava

from data_processors.run_data_processor import RunDataProcessor
from src.image_generator.generate_image import generate_strava_stats_image
from src.utils.date_utils import get_last_week_dates


def main():
    client = authenticate_strava()

    start_date, end_date = get_last_week_dates()
    activities = client.get_activities(after=start_date, before=end_date)

    runs = [a for a in activities if a.type == 'Run']

    if not runs:
        print("No runs to report this week!")
        return

    processor = RunDataProcessor(runs)
    processed_data = processor.process_runs()

    generate_strava_stats_image(processed_data, "output/images/stats.png")


if __name__ == "__main__":
    main()
