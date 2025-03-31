from PIL import Image, ImageDraw, ImageFont


class StravaStatsImage:
    """Class to generate Strava weekly statistics images."""

    # Color definitions
    COLORS = {
        "background": (16, 16, 16),  # Slightly off-black for softer look
        "text": (240, 240, 240),  # Slightly off-white for softer look
        "accent": (252, 76, 2),  # Strava orange
        "secondary": (40, 40, 40),  # Card backgrounds
        "watermark": (80, 80, 80)  # Watermark color
    }

    # Layout constants
    LAYOUT = {
        "margin": 60,
        "card_padding": 40,
        "card_radius": 20,
        "width": 1080,
        "height": 1920
    }

    def __init__(self, data, output_path="strava_stats.png", week_number=1):
        """Initialize with stats data and configuration."""
        self.data = data
        self.output_path = output_path
        self.week_number = week_number
        self.width = self.LAYOUT["width"]
        self.height = self.LAYOUT["height"]

        # Create image and drawing context
        self.img = Image.new("RGB", (self.width, self.height), color=self.COLORS["background"])
        self.draw = ImageDraw.Draw(self.img)

        # Load fonts
        self.fonts = self._load_fonts()

    def _load_fonts(self):
        """Load fonts with fallbacks if needed."""
        try:
            return {
                "title": ImageFont.truetype("Poppins-Bold.ttf", 105),
                "header": ImageFont.truetype("Poppins-SemiBold.ttf", 60),
                "text": ImageFont.truetype("Poppins-Medium.ttf", 34),
                "value": ImageFont.truetype("Poppins-Bold.ttf", 50),
                "label": ImageFont.truetype("Poppins-Regular.ttf", 28)
            }
        except IOError:
            print("Warning: Default fonts used as Poppins fonts were not found.")
            default = ImageFont.load_default()
            return {
                "title": default,
                "header": default,
                "text": default,
                "value": default,
                "label": default
            }

    @staticmethod
    def draw_rounded_rectangle(draw, xy, radius=10, fill=None):
        """Draw a rounded rectangle on the image."""
        x1, y1, x2, y2 = xy
        draw.rectangle((x1 + radius, y1, x2 - radius, y2), fill=fill)
        draw.rectangle((x1, y1 + radius, x2, y2 - radius), fill=fill)
        draw.pieslice((x1, y1, x1 + 2 * radius, y1 + 2 * radius), 180, 270, fill=fill)
        draw.pieslice((x2 - 2 * radius, y1, x2, y1 + 2 * radius), 270, 360, fill=fill)
        draw.pieslice((x1, y2 - 2 * radius, x1 + 2 * radius, y2), 90, 180, fill=fill)
        draw.pieslice((x2 - 2 * radius, y2 - 2 * radius, x2, y2), 0, 90, fill=fill)

    def draw_stat(self, x, y, value, label, center=False):
        """Draw a stat with value and label."""
        # Draw the value
        self.draw.text((x, y), str(value), font=self.fonts["value"], fill=self.COLORS["text"])

        # Calculate value text dimensions
        value_bbox = self.draw.textbbox((x, y), str(value), font=self.fonts["value"])
        value_width = value_bbox[2] - value_bbox[0]
        value_height = value_bbox[3] - value_bbox[1]

        # Draw the label
        label_x = x
        if center:
            label_bbox = self.draw.textbbox((0, 0), label, font=self.fonts["label"])
            label_width = label_bbox[2] - label_bbox[0]
            label_x = x + (value_width - label_width) // 2

        self.draw.text((label_x, y + value_height + 18), label, font=self.fonts["label"], fill=self.COLORS["text"])

    def _draw_header(self, current_y):
        """Draw the header section with accent line and title."""
        margin = self.LAYOUT["margin"]

        # Draw accent line above the title
        line_width = 120
        line_height = 8
        self.draw.rectangle(
            [(margin, current_y - 20), (margin + line_width, current_y - 20 + line_height)],
            fill=self.COLORS["accent"]
        )

        current_y += 30

        # Draw title
        title_text = f"WEEK {self.week_number}"
        self.draw.text((margin, current_y), title_text, font=self.fonts["title"], fill=self.COLORS["text"])
        bbox = self.draw.textbbox((margin, current_y), title_text, font=self.fonts["title"])
        title_height = bbox[3] - bbox[1]

        return current_y + title_height + 90

    def _draw_card(self, title, content_callback, current_y, height):
        """Draw a card with title and content."""
        margin = self.LAYOUT["margin"]
        card_padding = self.LAYOUT["card_padding"]
        card_radius = self.LAYOUT["card_radius"]

        # Calculate card dimensions
        card_width = self.width - (2 * margin)

        # Draw the card background
        self.draw_rounded_rectangle(
            self.draw,
            (margin, current_y, margin + card_width, current_y + height),
            radius=card_radius,
            fill=self.COLORS["secondary"]
        )

        # Card title
        card_title_y = current_y + card_padding
        card_content_y = card_title_y + 90
        self.draw.text(
            (margin + card_padding, card_title_y),
            title,
            font=self.fonts["header"],
            fill=self.COLORS["accent"]
        )

        # Draw card content using the callback
        content_callback(margin, card_padding, card_width, card_content_y)

        return current_y + height + 50

    def _draw_summary_card(self, margin, card_padding, card_width, content_y):
        """Draw the summary statistics card content."""
        summary = self.data.get("summary_stats", {})

        # Grid dimensions
        grid_width = (card_width - (2 * card_padding)) // 2
        grid_height = 150  # Approximate height for each grid item

        # Total runs - top left
        self.draw_stat(
            margin + card_padding, content_y,
            str(summary.get('total_runs', 0)), "RUNS"
        )

        # Total distance - top right
        self.draw_stat(
            margin + card_padding + grid_width, content_y,
            f"{summary.get('total_distance_km', 0):.1f}", "KM"
        )

        # Duration - bottom left
        self.draw_stat(
            margin + card_padding, content_y + grid_height - 20,
            summary.get('total_duration', '0:00'), "TOTAL TIME"
        )

        # Average pace - bottom right
        self.draw_stat(
            margin + card_padding + grid_width, content_y + grid_height - 20,
            summary.get('average_pace', '0:00'), "AVG PACE"
        )

    def _draw_run_card(self, run_data, margin, card_padding, card_width, content_y):
        """Draw either the longest or fastest run card content."""
        if not run_data:
            self.draw.text(
                (margin + card_padding, content_y),
                "No run data available",
                font=self.fonts["text"],
                fill=self.COLORS["text"]
            )
            return

        # Grid dimensions for layout
        grid_width = (card_width - (2 * card_padding)) // 2

        # Distance
        self.draw_stat(
            margin + card_padding, content_y,
            f"{run_data.get('distance_km', 0):.1f}", "KM"
        )

        # Duration
        self.draw_stat(
            margin + card_padding + grid_width, content_y,
            run_data.get('duration_str', '0:00'), "TIME"
        )

        # Pace - centered underneath
        pace_y = content_y + 90
        self.draw_stat(
            margin + card_padding, pace_y,
            run_data.get('pace_str', '0:00'), "MIN/KM", center=True
        )

    def _draw_watermark(self):
        """Draw the watermark at the bottom of the image."""
        watermark_text = "WEEKLY RUNNING STATS"
        watermark_font = self.fonts["label"]
        watermark_bbox = self.draw.textbbox((0, 0), watermark_text, font=watermark_font)
        watermark_width = watermark_bbox[2] - watermark_bbox[0]

        self.draw.text(
            (self.width // 2 - watermark_width // 2, self.height - self.LAYOUT["margin"]),
            watermark_text,
            font=watermark_font,
            fill=self.COLORS["watermark"]
        )

    def generate(self):
        """Generate the complete Strava stats image."""
        # Start layout from top margin
        current_y = self.LAYOUT["margin"] + 40

        # Draw header section
        current_y = self._draw_header(current_y)

        # Draw summary card
        current_y = self._draw_card(
            "SUMMARY",
            self._draw_summary_card,
            current_y,
            450  # Fixed height for summary card
        )

        # Draw longest run card
        longest_run = self.data.get("longest_run")
        current_y = self._draw_card(
            "LONGEST RUN",
            lambda m, p, w, y: self._draw_run_card(longest_run, m, p, w, y),
            current_y,
            450  # Fixed height for run cards
        )

        # Draw fastest run card
        fastest_run = self.data.get("fastest_run")
        current_y = self._draw_card(
            "FASTEST RUN",
            lambda m, p, w, y: self._draw_run_card(fastest_run, m, p, w, y),
            current_y,
            450  # Fixed height for run cards
        )

        # Add watermark
        self._draw_watermark()

        # Save the generated image
        self.img.save(self.output_path)
        print(f"Image saved to {self.output_path}")


def generate_strava_stats_image(data, output_path="strava_stats.png", week_number=1):
    """
    Legacy wrapper function that maintains backward compatibility with the original code.
    Creates and generates a Strava stats image.
    """
    image_generator = StravaStatsImage(data, output_path, week_number)
    image_generator.generate()


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

    # Use the class directly
    stats_image = StravaStatsImage(sample_data, "strava_stats.png", 1)
    stats_image.generate()

    # Alternatively, use the legacy wrapper function
    # generate_strava_stats_image(sample_data, "strava_stats.png", 1)
