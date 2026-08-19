#!/bin/bash

# Find the relative path to the script's folder
SCRIPT_DIR=$(dirname "${BASH_SOURCE[0]}")

# Run Python using the relative path prefix
python3 "$SCRIPT_DIR/__main__.py"
