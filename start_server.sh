#!/bin/bash
# Run the transforms as an HTTP transform server (for a Maltego iTDS / TDS setup).
# Maltego Desktop users don't need this: import tomba_transforms.mtz instead.

cd "$(dirname "$0")" || exit 1

if [ ! -f "settings.py" ] && { [ -z "$TOMBA_API_KEY" ] || [ -z "$TOMBA_SECRET_KEY" ]; }; then
    echo "Credentials not found."
    echo "Copy settings.py.template to settings.py, or export TOMBA_API_KEY and TOMBA_SECRET_KEY."
    exit 1
fi

echo "Starting the Tomba transform server on http://localhost:8080"
exec python3 project.py runserver
