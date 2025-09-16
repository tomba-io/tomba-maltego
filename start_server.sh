#!/bin/bash

echo "🚀 Starting Tomba.io Maltego Transform Server..."

# Check if configuration exists
if [ ! -f "settings.py" ]; then
    echo "⚠️  Configuration not found!"
    echo "Please copy settings.py.template to settings.py"
    echo "and configure your Tomba.io API credentials."
    exit 1
fi

# Start the server
echo "🌐 Server starting at http://localhost:8080"
echo "🔧 Add this URL to Maltego Transform Hub"
echo ""

maltego-trx start .
