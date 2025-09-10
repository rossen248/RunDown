from PIL import Image, ImageDraw, ImageFont
import os


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

    def __init__(self, data, output_path="strava_stats.png", week_label="WEEKLY STATS"):
        """Initialize with stats data and configuration."""
        self.data = data
        self.output_path = output_path
        self.week_label = week_label
        self.width = self.LAYOUT["width"]
        self.height = self.LAYOUT["height"]

        # Create image and drawing context
        self.img = Image.new("RGB", (self.width, self.height), color=self.COLORS["background"])
        self.draw = ImageDraw.Draw(self.img)

        # Load fonts
        self.fonts = self._load_fonts()

    def _load_fonts(self):
        """Load fonts with fallbacks if needed."""
        # Get the directory where this script is located
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # Try different possible paths for the assets folder
        possible_asset_paths = [
            # If running from src/ directory, assets is one level up
            os.path.join(current_dir, "../assets/fonts/Poppins"),
            # If assets is at the same level as src
            os.path.join(current_dir, "../assets/fonts"),
            # If running from project root
            os.path.join(current_dir, "assets/fonts/Poppins"),
            # Direct path based on your file structure
            os.path.abspath(os.path.join(current_dir, "../assets/fonts/Poppins")),
        ]

        # Find the correct assets path
        assets_path = None
        for path in possible_asset_paths:
            if os.path.exists(path):
                assets_path = path
                break

        if assets_path is None:
            print("Warning: Could not find Poppins fonts directory.")
            print("Searched paths:")
            for path in possible_asset_paths:
                print(f"  - {path}")
            return self._get_default_fonts()

        # Define font files
        font_files = {
            "title": "Poppins-Bold.ttf",
            "header": "Poppins-SemiBold.ttf",
            "text": "Poppins-Medium.ttf",
            "value": "Poppins-Bold.ttf",
            "label": "Poppins-Regular.ttf"
        }

        # Define font sizes
        font_sizes = {
            "title": 90,
            "header": 65,
            "text": 34,
            "value": 50,
            "label": 28
        }

        fonts = {}
        for name, filename in font_files.items():
            font_path = os.path.join(assets_path, filename)
            try:
                if os.path.exists(font_path):
                    fonts[name] = ImageFont.truetype(font_path, font_sizes[name])
                    # Removed: print(f"Loaded {name} font from: {font_path}")
                else:
                    print(f"Warning: Font file not found: {font_path}")
                    # Use a working TrueType font as fallback
                    fonts[name] = self._get_fallback_font(font_sizes[name])
            except Exception as e:
                print(f"Warning: Could not load {name} font from {font_path}: {e}")
                fonts[name] = self._get_fallback_font(font_sizes[name])

        return fonts

    def _get_fallback_font(self, size):
        """Get a working fallback TrueType font."""
        # Common system font paths on Linux/Unix systems
        common_fonts = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/System/Library/Fonts/Arial.ttf",  # macOS
            "/System/Library/Fonts/Helvetica.ttc",  # macOS
            "C:/Windows/Fonts/arial.ttf",  # Windows
            "C:/Windows/Fonts/calibri.ttf",  # Windows
        ]

        for font_path in common_fonts:
            if os.path.exists(font_path):
                try:
                    return ImageFont.truetype(font_path, size)
                except Exception:
                    continue

        # If no system font works, create a minimal TrueType font
        print(f"Warning: Using default font with size {size}")
        try:
            # Try to load default but with a specific size
            return ImageFont.load_default()
        except Exception:
            # Last resort - return None and handle in drawing methods
            return None

    def _get_default_fonts(self):
        """Get default fonts when Poppins fonts are not available."""
        print("Using fallback fonts...")
        return {
            "title": self._get_fallback_font(105),
            "header": self._get_fallback_font(65),
            "text": self._get_fallback_font(34),
            "value": self._get_fallback_font(50),
            "label": self._get_fallback_font(28)
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
        value_font = self.fonts["value"] if self.fonts["value"] else ImageFont.load_default()
        label_font = self.fonts["label"] if self.fonts["label"] else ImageFont.load_default()

        self.draw.text((x, y), str(value), font=value_font, fill=self.COLORS["text"])

        # Calculate value text dimensions
        try:
            value_bbox = self.draw.textbbox((x, y), str(value), font=value_font)
            value_width = value_bbox[2] - value_bbox[0]
            value_height = value_bbox[3] - value_bbox[1]
        except Exception:
            # Fallback for text sizing
            value_width = len(str(value)) * 20
            value_height = 30

        # Draw the label
        label_x = x
        if center:
            try:
                label_bbox = self.draw.textbbox((0, 0), label, font=label_font)
                label_width = label_bbox[2] - label_bbox[0]
                label_x = x + (value_width - label_width) // 2
            except Exception:
                # Fallback positioning
                label_x = x

        self.draw.text((label_x, y + value_height + 18), label, font=label_font, fill=self.COLORS["text"])

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
        title_text = self.week_label.upper()
        title_font = self.fonts["title"] if self.fonts["title"] else ImageFont.load_default()
        self.draw.text((margin, current_y), title_text, font=title_font, fill=self.COLORS["text"])

        try:
            bbox = self.draw.textbbox((margin, current_y), title_text, font=title_font)
            title_height = bbox[3] - bbox[1]
        except Exception:
            title_height = 100  # Fallback height

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
        header_font = self.fonts["header"] if self.fonts["header"] else ImageFont.load_default()
        self.draw.text(
            (margin + card_padding, card_title_y),
            title,
            font=header_font,
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
            margin + card_padding + grid_width, content_y + grid_height - 20,
            str(summary.get('total_runs', 0)), "Runs"
        )

        # Total distance - top left
        self.draw_stat(
            margin + card_padding, content_y,
            summary.get('total_distance_km', 0), "Total Distance"
        )

        # Duration - top right
        self.draw_stat(
            margin + card_padding + grid_width, content_y,
            summary.get('total_duration', '0:00'), "Total Time"
        )

        # Average pace - bottom left
        self.draw_stat(
            margin + card_padding, content_y + grid_height - 20,
            summary.get('average_pace', '0:00'), "avg Pace"
        )

    def _draw_run_card(self, run_data, margin, card_padding, card_width, content_y):
        """Draw either the longest or fastest run card content."""
        if not run_data:
            text_font = self.fonts["text"] if self.fonts["text"] else ImageFont.load_default()
            self.draw.text(
                (margin + card_padding, content_y),
                "No run data available",
                font=text_font,
                fill=self.COLORS["text"]
            )
            return

        # Grid dimensions
        grid_width = (card_width - (2 * card_padding)) // 2
        grid_height = 150  # Match the same grid height as summary card

        # Distance - top left
        self.draw_stat(
            margin + card_padding, content_y,
            run_data.distance_km, "Distance"
        )

        # Duration - top right
        self.draw_stat(
            margin + card_padding + grid_width, content_y,
            run_data.duration_str, "Time"
        )

        # Pace - bottom left (to match summary card grid layout)
        self.draw_stat(
            margin + card_padding, content_y + grid_height - 20,
            run_data.pace_str, "Pace"
        )

    def _draw_watermark(self):
        """Draw the watermark at the bottom of the image."""
        watermark_text = "WEEKLY RUNNING STATS"
        watermark_font = self.fonts["label"] if self.fonts["label"] else ImageFont.load_default()

        try:
            watermark_bbox = self.draw.textbbox((0, 0), watermark_text, font=watermark_font)
            watermark_width = watermark_bbox[2] - watermark_bbox[0]
        except Exception:
            watermark_width = len(watermark_text) * 10  # Fallback width calculation

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


def generate_strava_stats_image(data, output_path="strava_stats.png", week_label="WEEKLY STATS"):
    """
    Legacy wrapper function that maintains backward compatibility with the original code.
    Creates and generates a Strava stats image.
    """
    image_generator = StravaStatsImage(data, output_path, week_label)
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