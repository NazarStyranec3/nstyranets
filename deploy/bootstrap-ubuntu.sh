#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/var/www/nstyranets"
APP_USER="nstyranets"

sudo apt update
sudo apt install -y python3-venv python3-pip postgresql postgresql-contrib nginx certbot python3-certbot-nginx ufw fail2ban

if ! id "$APP_USER" >/dev/null 2>&1; then
  sudo adduser --system --group --home "$APP_DIR" "$APP_USER"
fi

sudo mkdir -p "$APP_DIR" /var/log/nstyranets
sudo chown -R "$APP_USER":www-data "$APP_DIR" /var/log/nstyranets

if [ ! -f /etc/nstyranets.env ]; then
  echo "Missing /etc/nstyranets.env. Create it from deploy/env.production.example before running this script."
  exit 1
fi

set -a
. /etc/nstyranets.env
set +a

cd "$APP_DIR"
python3 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

python manage.py collectstatic --noinput --settings=nstyranets.settings_prod
python manage.py migrate --settings=nstyranets.settings_prod

sudo cp deploy/nstyranets.service /etc/systemd/system/nstyranets.service
sudo systemctl daemon-reload
sudo systemctl enable --now nstyranets

sudo cp deploy/nginx-nstyranets-http.conf /etc/nginx/sites-available/nstyranets
if [ ! -e /etc/nginx/sites-enabled/nstyranets ]; then
  sudo ln -s /etc/nginx/sites-available/nstyranets /etc/nginx/sites-enabled/nstyranets
fi
sudo nginx -t
sudo systemctl reload nginx

echo "Bootstrap complete. After DNS points to this server, add TLS with:"
echo "sudo certbot --nginx -d nstyranets.com -d www.nstyranets.com"
echo "After certbot succeeds, you can replace the nginx site with deploy/nginx-nstyranets.conf if you want the stricter handcrafted TLS config."
