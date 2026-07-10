#!/bin/bash
set -e

# Package script for Document AI Portal
# This script follows the global solution-composition-contract.
# It uses deploy/package-map.yaml via deploy/package.py to assemble building blocks into deployable artifacts.

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PYTHON_SCRIPT="$SCRIPT_DIR/package.py"

echo "Starting packaging for Document AI Portal..."

if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "ERROR: Packaging script not found at $PYTHON_SCRIPT"
    exit 1
fi

# Run the python packaging logic
python3 "$PYTHON_SCRIPT"

echo "Packaging process finished successfully."
