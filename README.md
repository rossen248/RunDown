# Strava Weekly Running Summary 🏃♂️📊

A Python automation tool that generates Instagram-ready weekly running summaries using your Strava data.

![Sample Summary Image](output/images/sample_summary.png) *Example output*

## Features

- 📅 **Automatic Weekly Reports** - Runs every Sunday to compile your week's running stats
- 📸 **Instagram-Ready Images** - Generates styled images with key metrics
- 🔒 **Secure Authentication** - OAuth2 with automatic token refresh
- 📊 **Key Metrics** - Tracks distance, pace, elevation, and more
- ⚙️ **Customizable Templates** - Easy to modify colors, fonts, and layout

## Requirements

- Python 3.9+
- [Strava Developer Account](https://www.strava.com/settings/api)
- Basic Linux/Unix environment (for cron scheduling)

## Installation

```bash
# Clone repository
git clone https://github.com/yourusername/strava-weekly-summary.git
cd strava-weekly-summary

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration

1. **Strava API Setup**
    - Create an app at [Strava API Settings](https://www.strava.com/settings/api)
    - Get your `CLIENT_ID` and `CLIENT_SECRET`

2. **Environment Setup**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your credentials:
   ```ini
   STRAVA_CLIENT_ID=your_id_here
   STRAVA_CLIENT_SECRET=your_secret_here
   ```

3. **Font Setup**
    - Place your preferred fonts in `assets/fonts/`
    - Update `config/font_settings.yaml`

## Usage

### First-Time Authentication

```bash
python src/main.py
```

Follow the OAuth flow when prompted. This will generate tokens in your `.env` file.

### Manual Run

```bash
python src/main.py
```

Output images will be saved to `output/images/`

### Automated Scheduling (cron)

```bash
# Edit cron jobs
crontab -e
```

Add this line to run every Sunday at 9 PM:

```bash
0 21 * * 0 /path/to/project/.venv/bin/python /path/to/project/src/main.py
```

## Directory Structure

```
.
├── config/               # Configuration files
├── src/                  # Python source code
├── assets/               # Fonts and templates
├── output/               # Generated images and logs
├── scripts/              # Deployment helpers
└── tests/                # Unit tests
```

## Customization

Modify these files to change the output:

- `config/settings.yaml` - Color schemes and layout
- `src/image_generator/stats_visualizer.py` - Metrics calculation
- `assets/templates/` - Add background images

## Contributing

1. Fork the project
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Acknowledgments

- Strava API team for maintaining their excellent service
- `stravalib` developers for the Python client library
- Pillow maintainers for image processing capabilities

```

This README includes:
1. Clear visual hierarchy with emojis
2. Installation and configuration instructions
3. Usage examples for both manual and automated runs
4. Customization guidance
5. Contribution guidelines
6. License information

Would you like me to add any specific sections or modify existing ones?