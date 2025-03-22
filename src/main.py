from strava_client.auth import authenticate_strava
from utils.date_utils import get_last_week_dates
from image_generator.template_manager import create_base_template, add_text_to_image
import datetime


def main():
    # Authenticate
    client = authenticate_strava()

    # Get activities
    start_date, end_date = get_last_week_dates()
    activities = client.get_activities(after=start_date, before=end_date)

    # Filter runs
    runs = [a for a in activities if a.type == 'Run' and not a.manual]

    if not runs:
        print("No runs to report this week!")
        return

    # Generate image
    img = create_base_template()

    # Add title
    img = add_text_to_image(
        img,
        f"Weekly Running Summary ({start_date} - {end_date})",
        (100, 100),
        font_size=50
    )

    # Save output
    img.save("output/images/latest_summary.png")
    print("Summary image generated!")


if __name__ == "__main__":
    main()