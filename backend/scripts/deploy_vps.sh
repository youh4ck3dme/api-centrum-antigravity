#!/bin/bash
# backend/scripts/deploy_vps.sh
# This script runs on the VPS to update dependencies, migrate DB, and restart the service.

set -e

PROJECT_ROOT="/root/api-centrum-antiigravity"
VENV_PATH="$PROJECT_ROOT/backend/venv"
SERVICE_NAME="api-centrum"

echo "--- Starting VPS Deployment ---"

cd "$PROJECT_ROOT/backend"

# 1. Ensure Virtual Environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# 2. Update dependencies
echo "Updating dependencies..."
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

# 3. Run database migrations
echo "Running migrations..."
# Assuming production DB is local Postgres or same as configured in .env
./venv/bin/alembic upgrade head

# 4. Restart Systemd Service
echo "Restarting service: $SERVICE_NAME"
if systemctl is-active --quiet "$SERVICE_NAME"; then
    sudo systemctl restart "$SERVICE_NAME"
else
    echo "Warning: Service $SERVICE_NAME is not active. Attempting to start..."
    sudo systemctl start "$SERVICE_NAME"
fi

echo "--- Deployment Successful ---"
