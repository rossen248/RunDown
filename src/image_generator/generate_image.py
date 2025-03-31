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
        import os

        # Get the absolute path to the project root (2 levels up from generate_image.py)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(current_dir, "../.."))

        # Define font paths relative to project root
        font_paths = {
            "title": os.path.join(project_root, "assets/fonts/Poppins/Poppins-Bold.ttf"),
            "header": os.path.join(project_root, "assets/fonts/Poppins/Poppins-SemiBold.ttf"),
            "text": os.path.join(project_root, "assets/fonts/Poppins/Poppins-Medium.ttf"),
            "value": os.path.join(project_root, "assets/fonts/Poppins/Poppins-Bold.ttf"),
            "label": os.path.join(project_root, "assets/fonts/Poppins/Poppins-Regular.ttf")
        }

        try:
            return {
                name: ImageFont.truetype(path, size)
                for name, (path, size) in {
                    "title": (font_paths["title"], 105),
                    "header": (font_paths["header"], 65),
                    "text": (font_paths["text"], 34),
                    "value": (font_paths["value"], 50),
                    "label": (font_paths["label"], 28)
                }.items()
            }
        except IOError as e:
            print(f"Warning: Font loading error: {e}")
            print("Using default fonts as fallback.")
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
        card_content_y = card_title_y + 110
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

        # Total runs - bottom right
        self.draw_stat(
            # margin + card_padding, content_y,
            margin + card_padding + grid_width, content_y + grid_height - 20,
            str(summary.get('total_runs', 0)), "RUNS"
        )

        # Total distance - top left
        self.draw_stat(
            # margin + card_padding + grid_width, content_y,
            margin + card_padding, content_y,
            f"{summary.get('total_distance_km', 0):.1f}", "KM"
        )

        # Duration - top right
        self.draw_stat(
            # margin + card_padding, content_y + grid_height - 20,
            margin + card_padding + grid_width, content_y,
            summary.get('total_duration', '0:00'), "TOTAL TIME"
        )

        # Average pace - bottom left
        self.draw_stat(
            # margin + card_padding + grid_width, content_y + grid_height - 20,
            margin + card_padding, content_y + grid_height - 20,
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

        # Grid dimensions
        grid_width = (card_width - (2 * card_padding)) // 2
        grid_height = 150  # Match the same grid height as summary card

        # Distance - top left
        self.draw_stat(
            margin + card_padding, content_y,
            f"{run_data.distance_km:.1f}", "KM"
        )

        # Duration - top right
        self.draw_stat(
            margin + card_padding + grid_width, content_y,
            run_data.duration_str, "TIME"
        )

        # Pace - bottom left (to match summary card grid layout)
        self.draw_stat(
            margin + card_padding, content_y + grid_height - 20,
            run_data.pace_str, "PACE"
        )

        # Empty bottom right (or could add another stat here)
        # Leaving it empty to match the summary card's 2x2 grid layout

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

        # Draw fastest run card
        fastest_run = self.data.get("fastest_run")
        current_y = self._draw_card(
            "FASTEST RUN",
            lambda m, p, w, y: self._draw_run_card(fastest_run, m, p, w, y),
            current_y,
            450  # Same height as summary card
        )

        # Draw longest run card
        longest_run = self.data.get("longest_run")
        current_y = self._draw_card(
            "LONGEST RUN",
            lambda m, p, w, y: self._draw_run_card(longest_run, m, p, w, y),
            current_y,
            450  # Same height as summary card
        )

        # Draw summary card
        current_y = self._draw_card(
            "SUMMARY",
            self._draw_summary_card,
            current_y,
            450  # Fixed height for summary card
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
