#!/usr/bin/env python3
"""
RunDown - Strava Weekly Running Stats Generator
Generate beautiful weekly summary images of your Strava running activities.
"""

import argparse
import sys
from pathlib import Path

from src.auth import authenticate_strava
from src.run_data_processor import RunDataProcessor
from src.generate_image import generate_strava_stats_image
from src.date_utils import get_week_range, parse_date_input


def main():
    parser = argparse.ArgumentParser(
        description="Generate Strava weekly running stats image",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Last complete week
  %(prog)s --date 2024-03-15        # Week containing March 15, 2024
  %(prog)s --week-of 2024-03-15     # Same as --date
  %(prog)s --start 2024-03-11 --end 2024-03-17  # Custom date range
  %(prog)s --last-week --label "Training Week 5"  # Custom label
        """
    )

    # Date selection (mutually exclusive)
    date_group = parser.add_mutually_exclusive_group()
    date_group.add_argument(
        '--date', '--week-of',
        help='Date within the week you want stats for (YYYY-MM-DD)'
    )
    date_group.add_argument(
        '--last-week',
        action='store_true',
        help='Generate stats for last complete week (default)'
    )
    date_group.add_argument(
        '--start',
        help='Custom start date (YYYY-MM-DD). Must be used with --end'
    )

    parser.add_argument(
        '--end',
        help='Custom end date (YYYY-MM-DD). Must be used with --start'
    )

    # Output options
    parser.add_argument(
        '--output', '-o',
        help='Output file path (default: output/images/stats_YYYY-MM-DD.png)'
    )
    parser.add_argument(
        '--label', '-l',
        help='Custom label for the image (default: week dates)'
    )

    # Parse arguments
    args = parser.parse_args()

    # Validate custom date range
    if args.start and not args.end:
        parser.error("--start requires --end")
    if args.end and not args.start:
        parser.error("--end requires --start")

    try:
        # Determine date range
        if args.start and args.end:
            start_date = parse_date_input(args.start)
            end_date = parse_date_input(args.end)
            date_label = f"{start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}"
        elif args.date:
            start_date, end_date = get_week_range(parse_date_input(args.date))
            date_label = f"{start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}"
        else:
            # Default: last complete week
            start_date, end_date = get_week_range()
            date_label = f"{start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}"

        # Use custom label if provided
        week_label = args.label or date_label

        print(f"Generating stats for: {date_label}")
        print(f"Date range: {start_date.date()} to {end_date.date()}")

        # Authenticate and fetch data
        client = authenticate_strava()
        activities = client.get_activities(after=start_date, before=end_date)
        runs = [activity for activity in activities if activity.type == 'Run']

        if not runs:
            print(f"No runs found for the specified period.")
            sys.exit(1)

        print(f"Found {len(runs)} runs")

        # Process the data
        processor = RunDataProcessor(runs)
        processed_data = processor.process_runs()

        # Generate output filename
        if args.output:
            output_path = args.output
        else:
            # Create output directory if it doesn't exist
            output_dir = Path("output")
            output_dir.mkdir(parents=True, exist_ok=True)
            filename = f"stats_{start_date.strftime('%Y-%m-%d')}.png"
            output_path = output_dir / filename

        # Generate the image
        generate_strava_stats_image(
            processed_data,
            str(output_path),
            week_label
        )

        print(f"✓ Generated: {output_path}")

    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nCancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()