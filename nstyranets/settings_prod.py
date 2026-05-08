from .settings_base import *

DEBUG = False

ALLOWED_HOSTS = env_list(
    "DJANGO_ALLOWED_HOSTS",
    "nstyranets.com,www.nstyranets.com,178.105.63.22",
)

CSRF_TRUSTED_ORIGINS = env_list(
    "DJANGO_CSRF_TRUSTED_ORIGINS",
    "https://nstyranets.com,https://www.nstyranets.com",
)

SECURE_SSL_REDIRECT = env_bool("DJANGO_SECURE_SSL", True)
SESSION_COOKIE_SECURE = env_bool("DJANGO_SECURE_COOKIES", True)
CSRF_COOKIE_SECURE = env_bool("DJANGO_SECURE_COOKIES", True)
SECURE_HSTS_SECONDS = int(os.environ.get("DJANGO_HSTS_SECONDS", "31536000"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool("DJANGO_HSTS_INCLUDE_SUBDOMAINS", True)
SECURE_HSTS_PRELOAD = env_bool("DJANGO_HSTS_PRELOAD", False)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

if SECRET_KEY == "django-insecure-dev-only-change-this-key-before-production":
    raise RuntimeError("DJANGO_SECRET_KEY must be set in production.")
