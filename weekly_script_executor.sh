#!/bin/bash

# Project root directory
PROJECT_ROOT="$(dirname "$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)")"

# Activate virtual environment (assuming it exists in the project root)
source "$PROJECT_ROOT/venv/bin/activate"

# Path to your main script
SCRIPT_PATH="$PROJECT_ROOT/src/main.py"

# File to track last run time
LAST_RUN_FILE="/var/tmp/weekly_script_last_run"

# Check if we're past Monday 00:01
CURRENT_TIME=$(date +%s)
MONDAY_START=$(date -d "Monday 00:01" +%s)

# If Monday hasn't occurred yet this week, calculate it for last week
if [ $CURRENT_TIME -lt $MONDAY_START ]; then
    MONDAY_START=$(date -d "last Monday 00:01" +%s)
fi

# Get last run time, default to epoch start if file doesn't exist
LAST_RUN_TIME=$(cat "$LAST_RUN_FILE" 2>/dev/null || echo 0)

# Calculate start of current week
CURRENT_WEEK_START=$(date -d "@$((($MONDAY_START + 604800)/604800 * 604800))" +%s)

# Only execute if we're past Monday 00:01 AND haven't run this week
if [ $CURRENT_TIME -ge $MONDAY_START ] && [ $LAST_RUN_TIME -lt $CURRENT_WEEK_START ]; then
    # Execute the script
    python "$SCRIPT_PATH"

    # Update last run time
    echo $CURRENT_TIME > "$LAST_RUN_FILE"
fi