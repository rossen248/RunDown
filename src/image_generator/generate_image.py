import os

from PIL import Image, ImageDraw, ImageFont


def generate_strava_stats_image(data, output_path="strava_stats.png", week_number=1):
    # Image dimensions and colors
    width, height = 1080, 1920
    background_color = (16, 16, 16)  # Slightly off-black for softer look
    text_color = (240, 240, 240)  # Slightly off-white for softer look
    accent_color = (252, 76, 2)  # Strava orange
    secondary_color = (40, 40, 40)  # For card backgrounds

    # Create the image and drawing context
    img = Image.new("RGB", (width, height), color=background_color)
    draw = ImageDraw.Draw(img)

    # Load fonts (with fallbacks)
    fonts_dir = os.path.dirname(os.path.abspath(__file__))
    try:
        title_font = ImageFont.truetype("Poppins-Bold.ttf", 70)
        header_font = ImageFont.truetype("Poppins-SemiBold.ttf", 40)
        text_font = ImageFont.truetype("Poppins-Medium.ttf", 34)
        value_font = ImageFont.truetype("Poppins-Bold.ttf", 50)
        label_font = ImageFont.truetype("Poppins-Regular.ttf", 28)
    except IOError:
        print("Warning: Default fonts used as Poppins fonts were not found.")
        title_font = ImageFont.load_default()
        header_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
        value_font = ImageFont.load_default()
        label_font = ImageFont.load_default()

    # Constants for layout
    margin = 60
    card_padding = 40
    card_radius = 20

    # Draw header with accent line
    current_y = margin + 40
    title_text = f"WEEK {week_number}"

    # Draw accent line above the title
    line_width = 120
    line_height = 8
    draw.rectangle([(margin, current_y - 20), (margin + line_width, current_y - 20 + line_height)],
                   fill=accent_color)

    current_y += 30

    # Draw title
    draw.text((margin, current_y), title_text, font=title_font, fill=text_color)
    bbox = draw.textbbox((margin, current_y), title_text, font=title_font)
    title_height = bbox[3] - bbox[1]
    current_y += title_height + 60

    # Summary Stats Section - Card style
    summary = data.get("summary_stats", {})

    # Draw the card background
    card_width = width - (2 * margin)
    card_height = 450
    draw_rounded_rectangle(draw, (margin, current_y, margin + card_width, current_y + card_height),
                           radius=card_radius, fill=secondary_color)

    # Card title
    card_title_y = current_y + card_padding
    card_content_y = card_title_y + 60
    draw.text((margin + card_padding, card_title_y), "SUMMARY", font=header_font, fill=accent_color)

    # Create a 2x2 grid for summary stats
    grid_width = (card_width - (2 * card_padding)) // 2
    grid_height = (card_height - card_padding - 60 - card_padding) // 2

    # Total runs - top left
    draw_stat(draw, margin + card_padding, card_content_y,
              str(summary.get('total_runs', 0)), "RUNS",
              value_font, label_font, text_color)

    # Total distance - top right
    draw_stat(draw, margin + card_padding + grid_width, card_content_y,
              f"{summary.get('total_distance_km', 0):.1f}", "KM",
              value_font, label_font, text_color)

    # Duration - bottom left
    draw_stat(draw, margin + card_padding, card_content_y + grid_height - 20,
              summary.get('total_duration', '0:00'), "TOTAL TIME",
              value_font, label_font, text_color)

    # Average pace - bottom right
    draw_stat(draw, margin + card_padding + grid_width, card_content_y + grid_height - 20,
              summary.get('average_pace', '0:00'), "AVG PACE",
              value_font, label_font, text_color)

    current_y += card_height + 50

    # Draw Longest Run Card
    card_height = 360
    draw_rounded_rectangle(draw, (margin, current_y, margin + card_width, current_y + card_height),
                           radius=card_radius, fill=secondary_color)

    card_title_y = current_y + card_padding
    card_content_y = card_title_y + 60
    draw.text((margin + card_padding, card_title_y), "LONGEST RUN", font=header_font, fill=accent_color)

    longest_run = data.get("longest_run")
    if longest_run:
        # Distance
        draw_stat(draw, margin + card_padding, card_content_y,
                  f"{longest_run.get('distance_km', 0):.1f}", "KM",
                  value_font, label_font, text_color)

        # Duration
        draw_stat(draw, margin + card_padding + grid_width, card_content_y,
                  longest_run.get('duration_str', '0:00'), "TIME",
                  value_font, label_font, text_color)

        # Pace - centered underneath
        pace_y = card_content_y + 90
        draw_stat(draw, margin + card_width // 2 - 80, pace_y,
                  longest_run.get('pace_str', '0:00'), "MIN/KM",
                  value_font, label_font, text_color, center=True)
    else:
        draw.text((margin + card_padding, card_content_y), "No run data available",
                  font=text_font, fill=text_color)

    current_y += card_height + 50

    # Draw Fastest Run Card
    card_height = 360
    draw_rounded_rectangle(draw, (margin, current_y, margin + card_width, current_y + card_height),
                           radius=card_radius, fill=secondary_color)

    card_title_y = current_y + card_padding
    card_content_y = card_title_y + 60
    draw.text((margin + card_padding, card_title_y), "FASTEST RUN", font=header_font, fill=accent_color)

    fastest_run = data.get("fastest_run")
    if fastest_run:
        # Distance
        draw_stat(draw, margin + card_padding, card_content_y,
                  f"{fastest_run.get('distance_km', 0):.1f}", "KM",
                  value_font, label_font, text_color)

        # Duration
        draw_stat(draw, margin + card_padding + grid_width, card_content_y,
                  fastest_run.get('duration_str', '0:00'), "TIME",
                  value_font, label_font, text_color)

        # Pace - centered underneath
        pace_y = card_content_y + 90
        draw_stat(draw, margin + card_width // 2 - 80, pace_y,
                  fastest_run.get('pace_str', '0:00'), "MIN/KM",
                  value_font, label_font, text_color, center=True)
    else:
        draw.text((margin + card_padding, card_content_y), "No run data available",
                  font=text_font, fill=text_color)

    # Add a small watermark at the bottom
    watermark_text = "WEEKLY RUNNING STATS"
    watermark_font = label_font
    watermark_bbox = draw.textbbox((0, 0), watermark_text, font=watermark_font)
    watermark_width = watermark_bbox[2] - watermark_bbox[0]
    draw.text((width // 2 - watermark_width // 2, height - margin),
              watermark_text, font=watermark_font, fill=(80, 80, 80))

    # Save the generated image
    img.save(output_path)
    print(f"Image saved to {output_path}")


def draw_rounded_rectangle(draw, xy, radius=10, fill=None):
    """Draw a rounded rectangle"""
    x1, y1, x2, y2 = xy
    draw.rectangle((x1 + radius, y1, x2 - radius, y2), fill=fill)
    draw.rectangle((x1, y1 + radius, x2, y2 - radius), fill=fill)
    draw.pieslice((x1, y1, x1 + 2 * radius, y1 + 2 * radius), 180, 270, fill=fill)
    draw.pieslice((x2 - 2 * radius, y1, x2, y1 + 2 * radius), 270, 360, fill=fill)
    draw.pieslice((x1, y2 - 2 * radius, x1 + 2 * radius, y2), 90, 180, fill=fill)
    draw.pieslice((x2 - 2 * radius, y2 - 2 * radius, x2, y2), 0, 90, fill=fill)


def draw_stat(draw, x, y, value, label, value_font, label_font, color, center=False):
    """Draw a stat with value and label"""
    # Draw the value
    draw.text((x, y), str(value), font=value_font, fill=color)

    # Calculate value text dimensions
    value_bbox = draw.textbbox((x, y), str(value), font=value_font)
    value_width = value_bbox[2] - value_bbox[0]
    value_height = value_bbox[3] - value_bbox[1]

    # Draw the label
    label_x = x
    if center:
        label_bbox = draw.textbbox((0, 0), label, font=label_font)
        label_width = label_bbox[2] - label_bbox[0]
        label_x = x + (value_width - label_width) // 2

    draw.text((label_x, y + value_height + 5), label, font=label_font, fill=color)


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

    generate_strava_stats_image(sample_data, output_path="strava_stats.png", week_number=1)
