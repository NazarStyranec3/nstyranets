import json
import logging
import re
import urllib.parse
import urllib.request

from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


SUSPICIOUS_PATHS = (
    re.compile(r"/\.env", re.IGNORECASE),
    re.compile(r"/\.git", re.IGNORECASE),
    re.compile(r"/wp-admin", re.IGNORECASE),
    re.compile(r"/wp-login", re.IGNORECASE),
    re.compile(r"/xmlrpc\.php", re.IGNORECASE),
    re.compile(r"/phpmyadmin", re.IGNORECASE),
    re.compile(r"/adminer", re.IGNORECASE),
    re.compile(r"/config\.", re.IGNORECASE),
    re.compile(r"/backup", re.IGNORECASE),
    re.compile(r"/shell", re.IGNORECASE),
)

SUSPICIOUS_QUERY = (
    re.compile(r"(<script|%3cscript)", re.IGNORECASE),
    re.compile(r"(\.\./|%2e%2e%2f)", re.IGNORECASE),
    re.compile(r"(union\s+select|information_schema)", re.IGNORECASE),
    re.compile(r"(cmd=|exec=|passthru|base64_decode)", re.IGNORECASE),
)


class SuspiciousRequestAlertMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self._check_request(request)
        return self.get_response(request)

    def _check_request(self, request):
        path = request.path_info or ""
        query = request.META.get("QUERY_STRING", "")
        matched = self._match(path, query)
        if not matched:
            return

        ip = self._client_ip(request)
        cache_key = f"security-alert:{ip}:{matched}:{path[:80]}"
        if cache.get(cache_key):
            return

        cache.set(cache_key, True, settings.SECURITY_ALERT_COOLDOWN_SECONDS)
        self._send_alert(request, ip, matched)

    def _match(self, path, query):
        for pattern in SUSPICIOUS_PATHS:
            if pattern.search(path):
                return f"path:{pattern.pattern}"
        for pattern in SUSPICIOUS_QUERY:
            if pattern.search(query):
                return f"query:{pattern.pattern}"
        return ""

    def _client_ip(self, request):
        forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", "")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "unknown")

    def _send_alert(self, request, ip, matched):
        if not settings.SECURITY_ALERTS_ENABLED:
            logger.warning("Suspicious request: %s %s from %s", matched, request.get_full_path(), ip)
            return

        token = settings.SECURITY_ALERT_TELEGRAM_BOT_TOKEN
        chat_id = settings.SECURITY_ALERT_TELEGRAM_CHAT_ID
        if not token or not chat_id:
            logger.warning("Telegram security alert skipped: token/chat id is missing")
            return

        host = request.get_host()
        user_agent = request.META.get("HTTP_USER_AGENT", "-")[:300]
        text = (
            "Security alert\n"
            f"Host: {host}\n"
            f"IP: {ip}\n"
            f"Rule: {matched}\n"
            f"Path: {request.get_full_path()[:500]}\n"
            f"UA: {user_agent}"
        )
        payload = urllib.parse.urlencode({"chat_id": chat_id, "text": text}).encode()
        url = f"https://api.telegram.org/bot{token}/sendMessage"

        try:
            request_obj = urllib.request.Request(url, data=payload, method="POST")
            with urllib.request.urlopen(request_obj, timeout=4) as response:
                if response.status >= 400:
                    body = response.read().decode("utf-8", errors="replace")
                    logger.warning("Telegram security alert failed: %s %s", response.status, body)
        except Exception:
            logger.exception("Telegram security alert failed")


def telegram_healthcheck():
    token = settings.SECURITY_ALERT_TELEGRAM_BOT_TOKEN
    chat_id = settings.SECURITY_ALERT_TELEGRAM_CHAT_ID
    if not token or not chat_id:
        return False

    payload = urllib.parse.urlencode(
        {"chat_id": chat_id, "text": "Security alerts are connected."}
    ).encode()
    request_obj = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=payload,
        method="POST",
    )
    with urllib.request.urlopen(request_obj, timeout=4) as response:
        data = json.loads(response.read().decode("utf-8"))
        return bool(data.get("ok"))
