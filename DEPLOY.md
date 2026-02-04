# Deployment Guide

Quick setup for running Maple Water Tracker on your home server.

## Option 1: Systemd Service (Recommended)

This runs the app automatically on boot and restarts it if it crashes.

### Setup

```bash
# 1. Clone/copy the project to your server
cd ~
git clone https://github.com/brittleru/maple-tracker.git
cd maple-tracker

# 2. Create virtual environment and install
python3 -m venv venv
source venv/bin/activate
python -m pip install -e ".[prod]"

# 3. Initialize the database
python -c "from database.db_operations import init_database; init_database()"

# 4. Edit the service file 
# (replace YOUR_USERNAME with your actual username and where you cloned the repo)
sed -i "s/YOUR_USERNAME/$USER/g" maple-tracker.service

# 5. Install and start the service
sudo cp maple-tracker.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable maple-tracker
sudo systemctl start maple-tracker
```

### Managing the service

```bash
# Check status
sudo systemctl status maple-tracker

# View logs
sudo journalctl -u maple-tracker -f

# Restart after updates
sudo systemctl restart maple-tracker

# Stop
sudo systemctl stop maple-tracker
```

## Option 2: Quick & Dirty (for testing)

```bash
cd ~/maple-tracker
source venv/bin/activate
gunicorn --bind 0.0.0.0:5000 "web.app:create_app()"
```

Or use the built-in Flask server (not for heavy use):
```bash
python web/app.py
```

## Accessing the App

From any device on your network: `http://SERVER_IP:5000`

To find your server's IP:
```bash
hostname -I | awk '{print $1}'
```

Or with Avahi:
```bash
# Check if avahi is running
systemctl status avahi-daemon

# If not installed
sudo apt install avahi-daemon

# Find your hostname
hostname
```

Then access from any device: `http://YOUR_HOSTNAME.local:5000`

For example if hostname is `brittle`, you'd use http://brittle.local:5000


## Backup

The database is a single file. Back it up periodically:
```bash
cp ~/maple-tracker/database/data/maple.db ~/maple-backup-$(date +%Y%m%d).db
```

## Firewall

If you can't connect, open port 5000:
```bash
sudo ufw allow 5000/tcp
```