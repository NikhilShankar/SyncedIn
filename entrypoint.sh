#!/bin/bash
set -e

echo "🚀 Starting SyncedIn Resume Generator..."

# Ensure /data directory exists
if [ ! -d "/data" ]; then
    echo "⚠️  Warning: /data directory not found!"
    echo "   Please ensure you've mounted your local directory to /data"
    echo "   Example: -v ~/Documents/SyncedIn:/data"
    mkdir -p /data
fi

# Set proper permissions
chmod 777 /data 2>/dev/null || true

echo "📁 Data directory: /data"
echo "✅ Initialization complete"
echo ""

# Execute the CMD from Dockerfile (Streamlit)
exec "$@"
