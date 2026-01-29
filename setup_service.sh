#!/bin/bash

# Configuration
PROJECT_DIR=$(pwd)
SERVICE_NAME="nbr-gestao"
SERVICE_FILE="${PROJECT_DIR}/${SERVICE_NAME}.service"
SYSTEMD_DIR="/etc/systemd/system"
ENV_FILE="${PROJECT_DIR}/.env"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}Starting setup for ${SERVICE_NAME}...${NC}"

# Check for .env file
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${RED}Error: .env file not found inside ${PROJECT_DIR}!${NC}"
    echo "Please create a .env file with your secrets (SECRET_KEY, DB config, etc.)"
    exit 1
fi

# Check for Gunicorn
if ! grep -q "gunicorn" requirements.txt; then
    echo -e "${GREEN}Installing Gunicorn...${NC}"
    pip install gunicorn
else
    echo "Gunicorn already in requirements (or check skipped), ensuring it's installed..."
    pip install gunicorn
fi

# Update Service File Paths
# This simple sed replaces placeholders with current directory and user
CURRENT_USER=$(whoami)
CURRENT_GROUP=$(id -gn)

echo -e "${GREEN}Configuring service file with current user/path...${NC}"
sed -i "s|User=ubuntu|User=${CURRENT_USER}|g" "$SERVICE_FILE"
sed -i "s|Group=www-data|Group=${CURRENT_GROUP}|g" "$SERVICE_FILE"
sed -i "s|WorkingDirectory=/home/ubuntu/nbr-gestao|WorkingDirectory=${PROJECT_DIR}|g" "$SERVICE_FILE"
sed -i "s|ExecStart=/home/ubuntu/nbr-gestao/venv/bin/gunicorn|ExecStart=${PROJECT_DIR}/venv/bin/gunicorn|g" "$SERVICE_FILE"
sed -i "s|Environment=\"PATH=/home/ubuntu/nbr-gestao/venv/bin\"|Environment=\"PATH=${PROJECT_DIR}/venv/bin\"|g" "$SERVICE_FILE"


# Link Service File
echo -e "${GREEN}Linking service file to systemd...${NC}"
if [ -L "${SYSTEMD_DIR}/${SERVICE_NAME}.service" ]; then
    sudo rm "${SYSTEMD_DIR}/${SERVICE_NAME}.service"
fi
sudo ln -s "$SERVICE_FILE" "${SYSTEMD_DIR}/${SERVICE_NAME}.service"

# Reload and Start
echo -e "${GREEN}Reloading systemd and starting service...${NC}"
sudo systemctl daemon-reload
sudo systemctl enable "${SERVICE_NAME}"
sudo systemctl restart "${SERVICE_NAME}"

echo -e "${GREEN}Status:${NC}"
sudo systemctl status "${SERVICE_NAME}" --no-pager

echo -e "${GREEN}Setup Complete!${NC}"
