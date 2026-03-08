# Deployment script for api-centrum-antiigravity
# This script bundles the project, transfers it to the VPS, and starts it.

$VPS_IP = "194.182.87.6"
$SSH_KEY = "C:\Users\42195\.ssh\vps_repaircode"
$REMOTE_DIR = "/root/api-centrum-antiigravity"
$TAR_FILE = "deploy_api_centrum.tar.gz"

Write-Host "Creating deployment bundle..." -ForegroundColor Cyan
if (Test-Path $TAR_FILE) { Remove-Item $TAR_FILE }

# Using tar (available in modern Windows) to bundle the project
tar --exclude="backend/venv" --exclude="__pycache__" --exclude=".git" --exclude="node_modules" --exclude=".pytest_cache" --exclude="dist" -czf $TAR_FILE .

Write-Host "Transferring bundle to VPS..." -ForegroundColor Cyan
# Fixing the variable interpolation and ensure using the identity file
scp -i "$SSH_KEY" "$TAR_FILE" "root@${VPS_IP}:/root/"

Write-Host "Extracting and starting services on VPS..." -ForegroundColor Cyan
ssh -i "$SSH_KEY" "root@${VPS_IP}" "mkdir -p $REMOTE_DIR && tar -xzf /root/$TAR_FILE -C $REMOTE_DIR && cd $REMOTE_DIR && docker compose up -d --build"

Write-Host "Cleaning up local bundle..." -ForegroundColor Cyan
Remove-Item $TAR_FILE

Write-Host "Deployment complete!" -ForegroundColor Green
