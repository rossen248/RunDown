#!/usr/bin/env python3
"""
RunDown - Strava Weekly Stats Generator
Entry point for the application.
"""

import sys
import os

# Add src to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.main import main

if __name__ == "__main__":
    main()