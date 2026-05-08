# Production security checklist

Use this as the server-side checklist after copying the project to the host.

## 1. Environment file

Create `/etc/nstyranets.env` from `.env.example` and make it private:

```bash
sudo chown root:root /etc/nstyranets.env
sudo chmod 600 /etc/nstyranets.env
```

Generate a real secret key on the server:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Required production values:

```env
DJANGO_DEBUG=False
DJANGO_SETTINGS_MODULE=nstyranets.settings_prod
DJANGO_SECRET_KEY=replace-with-generated-key
DJANGO_ALLOWED_HOSTS=nstyranets.com,www.nstyranets.com,178.105.63.22
DJANGO_CSRF_TRUSTED_ORIGINS=https://nstyranets.com,https://www.nstyranets.com
DJANGO_SECURE_SSL=True
DJANGO_SECURE_COOKIES=True
SECURITY_ALERTS_ENABLED=True
SECURITY_ALERT_TELEGRAM_BOT_TOKEN=replace
SECURITY_ALERT_TELEGRAM_CHAT_ID=replace
```

## 2. App user and folders

```bash
sudo adduser --system --group --home /var/www/nstyranets nstyranets
sudo mkdir -p /var/www/nstyranets /var/log/nstyranets
sudo chown -R nstyranets:www-data /var/www/nstyranets /var/log/nstyranets
```

Install dependencies in `/var/www/nstyranets`:

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python manage.py collectstatic --noinput --settings=nstyranets.settings_prod
python manage.py migrate --settings=nstyranets.settings_prod
```

## 3. Gunicorn + Nginx

Copy:

```bash
sudo cp deploy/nstyranets.service /etc/systemd/system/nstyranets.service
sudo systemctl daemon-reload
sudo systemctl enable --now nstyranets
sudo cp deploy/nginx-nstyranets.conf /etc/nginx/sites-available/nstyranets
sudo ln -s /etc/nginx/sites-available/nstyranets /etc/nginx/sites-enabled/nstyranets
sudo nginx -t
sudo systemctl reload nginx
```

Add TLS:

```bash
sudo certbot --nginx -d nstyranets.com -d www.nstyranets.com
```

## 3.1. Fast bootstrap option

After the project is already copied into `/var/www/nstyranets` and
`/etc/nstyranets.env` exists, you can run:

```bash
bash deploy/bootstrap-ubuntu.sh
```

## 4. Firewall and real SSH port

Move real SSH away from port 22, for example to `2222`.

Edit `/etc/ssh/sshd_config`:

```conf
Port 2222
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
MaxAuthTries 3
AllowUsers your-server-user
```

Before reloading SSH, open the new port:

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 2222/tcp
sudo ufw enable
sudo systemctl reload ssh
```

Keep your current SSH session open, then test a second login on port `2222`.

## 5. Fake port 22 honeypot

Use Cowrie as a fake SSH service. Do not run it as root.

Recommended layout:

- real SSH: `2222`
- fake SSH: public `22`
- Cowrie internal listen port: `22222`

Redirect public port 22 to Cowrie:

```bash
sudo ufw allow 22/tcp
sudo iptables -t nat -A PREROUTING -p tcp --dport 22 -j REDIRECT --to-port 22222
```

Make the NAT rule persistent with `iptables-persistent` or your host firewall tooling.

Cowrie records attacker commands and slows them down safely. Do not execute attacker commands, do not return attacks, and do not put real credentials inside the honeypot.

## 6. Telegram alerts

The Django middleware sends Telegram alerts for suspicious web paths like:

- `/.env`
- `/.git`
- `/wp-admin`
- `/wp-login.php`
- `/phpmyadmin`
- SQL/XSS-looking query strings

Test after `SECURITY_ALERTS_ENABLED=True`:

```bash
curl https://nstyranets.com/.env
```

For SSH brute-force alerts, add `fail2ban` and connect a Telegram action. Keep this separate from Django alerts because SSH attacks happen before traffic reaches the website.
