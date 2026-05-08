$ErrorActionPreference = "Stop"

$env:DJANGO_SETTINGS_MODULE = "nstyranets.settings_dev"
$env:DJANGO_DEBUG = "True"

python manage.py runserver 127.0.0.1:8000
