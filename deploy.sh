#!/bin/bash
# =============================================================================
# Koya — VPS deploy script
# Run as root (or sudo) on a fresh Ubuntu 22.04/24.04 VPS.
# Usage: bash deploy.sh
# =============================================================================
set -euo pipefail

APP_DIR="/var/www/koya"
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"   # directory this script lives in
SERVICE_USER="koya"
PYTHON="python3.12"
VENV="$APP_DIR/backend/.venv"
NGINX_CONF="/etc/nginx/sites-available/koya"
DB_NAME="koya"
DB_USER="koya"

echo "=== 1. Install system packages ==="
apt-get update -qq
apt-get install -y -qq \
    python3.12 python3.12-venv python3.12-dev \
    postgresql postgresql-contrib \
    nginx \
    certbot python3-certbot-nginx \
    git curl

echo "=== 2. Create app user ==="
id -u "$SERVICE_USER" &>/dev/null || useradd -r -s /bin/false -d "$APP_DIR" "$SERVICE_USER"

echo "=== 3. Set up PostgreSQL ==="
DB_PASS=$(openssl rand -base64 24 | tr -d '/+=')
sudo -u postgres psql -tc "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'" | grep -q 1 || \
    sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';"
sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'" | grep -q 1 || \
    sudo -u postgres psql -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"
echo "  DB_PASS generated: $DB_PASS  (write this down — it goes in .env)"

echo "=== 4. Copy files ==="
mkdir -p "$APP_DIR"
rsync -a --delete \
    --exclude='.git' \
    --exclude='backend/.venv' \
    --exclude='backend/.env' \
    --exclude='backend/__pycache__' \
    --exclude='backend/app/__pycache__' \
    "$REPO_DIR/" "$APP_DIR/"
mkdir -p /var/www/koya/uploads
chown -R "$SERVICE_USER:$SERVICE_USER" "$APP_DIR" /var/www/koya/uploads

echo "=== 5. Create .env (if it doesn't exist yet) ==="
ENV_FILE="$APP_DIR/backend/.env"
if [ ! -f "$ENV_FILE" ]; then
    JWT_SECRET=$(openssl rand -base64 48 | tr -d '/+=')
    ADMIN_PASS=$(openssl rand -base64 18 | tr -d '/+=')
    cat > "$ENV_FILE" <<EOF
DATABASE_URL=postgresql://$DB_USER:$DB_PASS@localhost:5432/$DB_NAME
ADMIN_PASSWORD=$ADMIN_PASS
JWT_SECRET=$JWT_SECRET
CORS_ORIGINS=["https://koya.living","https://www.koya.living"]
DEBUG=false
GOOGLE_CLIENT_ID=
EOF
    chmod 600 "$ENV_FILE"
    chown "$SERVICE_USER:$SERVICE_USER" "$ENV_FILE"
    echo ""
    echo "  *** IMPORTANT — save these credentials ***"
    echo "  Admin password : $ADMIN_PASS"
    echo "  DB password    : $DB_PASS"
    echo "  JWT secret     : $JWT_SECRET"
    echo ""
else
    echo "  .env already exists — skipping (not overwritten)"
fi

echo "=== 6. Python venv + dependencies ==="
sudo -u "$SERVICE_USER" $PYTHON -m venv "$VENV"
sudo -u "$SERVICE_USER" "$VENV/bin/pip" install --quiet --upgrade pip
sudo -u "$SERVICE_USER" "$VENV/bin/pip" install --quiet "$APP_DIR/backend"

echo "=== 7. Systemd service ==="
cat > /etc/systemd/system/koya.service <<EOF
[Unit]
Description=Koya FastAPI backend
After=network.target postgresql.service

[Service]
User=$SERVICE_USER
WorkingDirectory=$APP_DIR/backend
EnvironmentFile=$ENV_FILE
ExecStart=$VENV/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 2
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
systemctl daemon-reload
systemctl enable koya
systemctl restart koya
echo "  Service status:"
systemctl is-active koya && echo "  koya.service is RUNNING" || echo "  koya.service FAILED — check: journalctl -u koya -n 50"

echo "=== 8. Nginx ==="
cp "$REPO_DIR/nginx-koya.conf" "$NGINX_CONF"
ln -sf "$NGINX_CONF" /etc/nginx/sites-enabled/koya
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx

echo "=== 9. Gzip + HTTP/2 tweaks ==="
bash "$REPO_DIR/fix_nginx.sh"

echo ""
echo "============================================================"
echo " Deploy complete."
echo ""
echo " If this is a fresh server, get an SSL cert:"
echo "   certbot --nginx -d koya.living -d www.koya.living"
echo ""
echo " To check backend logs:"
echo "   journalctl -u koya -f"
echo ""
echo " To redeploy after code changes:"
echo "   bash deploy.sh   (skips DB/env/cert steps)"
echo "============================================================"
