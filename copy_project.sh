#!/bin/bash

# Check required commands
if ! command -v tree &> /dev/null; then
    echo "Error: Please install 'tree' command"
    exit 1
fi

if ! command -v xclip &> /dev/null; then
    echo "Error: Please install 'xclip' for clipboard support"
    exit 1
fi

# Create temporary file
temp_file=$(mktemp)

# Generate project tree with exclusions
echo "PROJECT STRUCTURE:" >> "$temp_file"
echo "==================" >> "$temp_file"
tree -I "__pycache__|build|RunDown.egg-info|.git|.venv" --noreport >> "$temp_file"

# Add files content
echo -e "\n\nESSENTIAL FILES CONTENT:" >> "$temp_file"
echo "===========================" >> "$temp_file"

# Fixed find command
find . -type f \( -name "*.py" -o -name "*.yaml" -o -name "*.toml" -o -name "*.md" -o -name "*.sh" \) \
    ! -path "./build/*" \
    ! -path "./assets/*" \
    ! -path "./output/*" \
    ! -path "*__pycache__*" \
    ! -path "./.venv/*" | \
while read -r file; do
    echo -e "\n=== ${file#./} ===\n" >> "$temp_file"
    cat "$file" >> "$temp_file"
done

# Copy to clipboard and clean up
cat "$temp_file" | xclip -selection clipboard
rm "$temp_file"

echo "Project essentials copied to clipboard!"
