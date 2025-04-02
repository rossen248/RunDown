from strava_client.auth import authenticate_strava

from data_processors.run_data_processor import RunDataProcessor
from src.image_generator.generate_image import generate_strava_stats_image
from src.utils.date_utils import get_last_week_dates, get_week_number


def main():
    client = authenticate_strava()

    # Get date range for last week
    start_date, end_date = get_last_week_dates()

    # Calculate week number based on the start date of the week we're processing
    week_number = get_week_number(start_date)

    print(f"Fetching activities from {start_date.date()} to {end_date.date()} (Week {week_number})")

    activities = client.get_activities(after=start_date, before=end_date)
    runs = [a for a in activities if a.type == 'Run']

    if not runs:
        print(f"No runs to report for Week {week_number}!")
        return

    processor = RunDataProcessor(runs)
    processed_data = processor.process_runs()

    # Generate a filename that includes the week number
    output_filename = f"output/images/stats_week_{week_number}.png"

    # Pass the week number to the image generator
    generate_strava_stats_image(processed_data, output_filename, week_number)
    print(f"Generated stats image for Week {week_number}: {output_filename}")


if __name__ == "__main__":
    main()
