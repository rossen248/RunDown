#!/bin/bash

# Project root directory
PROJECT_ROOT="$(dirname "$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)")"

# Path to your main script
SCRIPT_PATH="$PROJECT_ROOT/src/main.py"

# File to track last run time
LAST_RUN_FILE="/var/tmp/weekly_script_last_run"

# Log file
LOG_FILE="$PROJECT_ROOT/output/logs/executor.log"

# Ensure logs directory exists
mkdir -p "$(dirname "$LOG_FILE")"

# Log function
log_message() {
  echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Get current day of week (0 is Sunday, 1 is Monday)
current_day=$(date +%u)
current_hour=$(date +%H)
current_minute=$(date +%M)

# Check if we're past Monday 00:01
is_after_monday_start=0
if [ $current_day -eq 1 ] && ([ $current_hour -gt 0 ] || [ $current_minute -ge 1 ]); then
  # It's Monday after 00:01
  is_after_monday_start=1
elif [ $current_day -gt 1 ]; then
  # It's after Monday
  is_after_monday_start=1
fi

# Get last run time, default to epoch start if file doesn't exist
LAST_RUN_TIME=$(cat "$LAST_RUN_FILE" 2>/dev/null || echo 0)
CURRENT_TIME=$(date +%s)

# Calculate the timestamp for Monday 00:01 of the current week
monday_this_week=$(date -d "$(date +%Y%m%d) -$(( $(date +%u) - 1 ))days" +%Y%m%d)
MONDAY_TIMESTAMP=$(date -d "${monday_this_week} 00:01" +%s)

log_message "Current time: $(date)"
log_message "Monday timestamp: $(date -d @${MONDAY_TIMESTAMP})"
log_message "Last run time: $(date -d @${LAST_RUN_TIME})"

# Only execute if we're past Monday 00:01 AND haven't run this week
if [ $is_after_monday_start -eq 1 ] && [ $LAST_RUN_TIME -lt $MONDAY_TIMESTAMP ]; then
  log_message "Conditions met to run the script"

  # Execute the script using the system's Python
  python "$SCRIPT_PATH"

  # Check if script ran successfully
  if [ $? -eq 0 ]; then
    # Update last run time
    echo $CURRENT_TIME > "$LAST_RUN_FILE"
    log_message "Script executed successfully, timestamp updated"
  else
    log_message "Script execution failed, not updating timestamp"
  fi
else
  log_message "Conditions not met, skipping execution"
fi