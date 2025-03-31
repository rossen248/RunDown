from PIL import Image, ImageDraw, ImageFont


def generate_strava_stats_image(data, output_path="strava_stats.png"):
    # Image dimensions and background color
    width, height = 1080, 1920
    background_color = (255, 255, 255)  # white background

    # Create the image and drawing context
    img = Image.new("RGB", (width, height), color=background_color)
    draw = ImageDraw.Draw(img)

    # Load fonts (update the font path as necessary)
    try:
        title_font = ImageFont.truetype("arial.ttf", 60)
        header_font = ImageFont.truetype("arial.ttf", 40)
        text_font = ImageFont.truetype("arial.ttf", 30)
    except IOError:
        title_font = ImageFont.load_default()
        header_font = ImageFont.load_default()
        text_font = ImageFont.load_default()

    margin = 50
    current_y = margin

    # Title
    title_text = "Weekly Strava Stats"
    draw.text((margin, current_y), title_text, font=title_font, fill=(0, 0, 0))
    bbox = draw.textbbox((margin, current_y), title_text, font=title_font)
    title_height = bbox[3] - bbox[1]
    current_y += title_height + 30

    # Summary Stats Section
    header_text = "Summary Stats:"
    draw.text((margin, current_y), header_text, font=header_font, fill=(0, 0, 0))
    bbox = draw.textbbox((margin, current_y), header_text, font=header_font)
    header_height = bbox[3] - bbox[1]
    current_y += header_height + 10

    summary = data.get("summary_stats", {})
    summary_lines = [
        f"Total Runs: {summary.get('total_runs', 0)}",
        f"Total Distance (km): {summary.get('total_distance_km', 0):.2f}",
        f"Total Duration: {summary.get('total_duration', '00:00')}",
        f"Average Pace: {summary.get('average_pace', '00:00')}",
    ]
    for line in summary_lines:
        draw.text((margin + 20, current_y), line, font=text_font, fill=(0, 0, 0))
        bbox = draw.textbbox((margin + 20, current_y), line, font=text_font)
        line_height = bbox[3] - bbox[1]
        current_y += line_height + 5

    current_y += 20

    # Longest Run Section
    header_text = "Longest Run:"
    draw.text((margin, current_y), header_text, font=header_font, fill=(0, 0, 0))
    bbox = draw.textbbox((margin, current_y), header_text, font=header_font)
    header_height = bbox[3] - bbox[1]
    current_y += header_height + 10

    longest_run = data.get("longest_run")
    if longest_run:
        longest_lines = [
            f"Distance (km): {longest_run.get('distance_km', 0):.2f}",
            f"Duration: {longest_run.get('duration_str', '00:00')}",
            f"Pace: {longest_run.get('pace_str', '00:00')}",
        ]
        for line in longest_lines:
            draw.text((margin + 20, current_y), line, font=text_font, fill=(0, 0, 0))
            bbox = draw.textbbox((margin + 20, current_y), line, font=text_font)
            line_height = bbox[3] - bbox[1]
            current_y += line_height + 5
    else:
        no_data_text = "No run data available"
        draw.text((margin + 20, current_y), no_data_text, font=text_font, fill=(0, 0, 0))
        bbox = draw.textbbox((margin + 20, current_y), no_data_text, font=text_font)
        current_y += (bbox[3] - bbox[1]) + 5

    current_y += 20

    # Fastest Run Section
    header_text = "Fastest Run:"
    draw.text((margin, current_y), header_text, font=header_font, fill=(0, 0, 0))
    bbox = draw.textbbox((margin, current_y), header_text, font=header_font)
    header_height = bbox[3] - bbox[1]
    current_y += header_height + 10

    fastest_run = data.get("fastest_run")
    if fastest_run:
        fastest_lines = [
            f"Distance (km): {fastest_run.get('distance_km', 0):.2f}",
            f"Duration: {fastest_run.get('duration_str', '00:00')}",
            f"Pace: {fastest_run.get('pace_str', '00:00')}",
        ]
        for line in fastest_lines:
            draw.text((margin + 20, current_y), line, font=text_font, fill=(0, 0, 0))
            bbox = draw.textbbox((margin + 20, current_y), line, font=text_font)
            line_height = bbox[3] - bbox[1]
            current_y += line_height + 5
    else:
        no_data_text = "No run data available"
        draw.text((margin + 20, current_y), no_data_text, font=text_font, fill=(0, 0, 0))
        bbox = draw.textbbox((margin + 20, current_y), no_data_text, font=text_font)
        current_y += (bbox[3] - bbox[1]) + 5

    # Save the generated image
    img.save(output_path)
    print(f"Image saved to {output_path}")


if __name__ == "__main__":
    sample_data = {
        "summary_stats": {
            "total_runs": 3,
            "total_distance_km": 28.5,
            "total_duration": "2:45:30",
            "average_pace": "5:45"
        },
        "longest_run": {
            "distance_km": 15.12,
            "duration_str": "1:15:30",
            "pace_str": "5:45"
        },
        "fastest_run": {
            "distance_km": 10.0,
            "duration_str": "50:00",
            "pace_str": "5:00"
        }
    }

    generate_strava_stats_image(sample_data, output_path="strava_stats.png")
