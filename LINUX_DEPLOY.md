# Linux Deployment Guide

This guide explains how to deploy the **nbr-gestao** application as a systemd service on Linux using Gunicorn.

## Prerequisites

- Linux Server (Ubuntu/Debian recommended)
- Python 3.10+ installed
- Virtual environment created and active
- Project files cloned to the server

## Setup Steps

### 1. Environment Configurations

Create a `.env` file in the project root (`nbr-gestao/`) with your production secrets:

```bash
# .env
DEBUG=False
SECRET_KEY=your_production_secret_key
# Add other variables as needed (DB_NAME, DB_USER, etc.)
```

### 2. Install Dependencies

Make sure your virtual environment is active and dependencies are installed:

```bash
cd /path/to/nbr-gestao
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Setup Service

We have provided a script `setup_service.sh` to automate the configuration. It will:
1.  Install `gunicorn` if missing.
2.  Update the `nbr-gestao.service` file with your current user and file paths.
3.  Link the service to `/etc/systemd/system/`.
4.  Start and enable the service.

**Run the script:**

```bash
chmod +x setup_service.sh
./setup_service.sh
```

### 4. Verify Service

Check the status of the service:

```bash
sudo systemctl status nbr-gestao
```

To view logs:

```bash
journalctl -u nbr-gestao -f
```

## Manual Configuration (Optional)

If you prefer to configure manually, edit `nbr-gestao.service` to match your paths and user, then copy it to `/etc/systemd/system/`.

```bash
sudo cp nbr-gestao.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable nbr-gestao
sudo systemctl start nbr-gestao
```
