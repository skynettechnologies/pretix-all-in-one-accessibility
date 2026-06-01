"""
registration.py
---------------
Utility helpers for the All in One Accessibility pretix plugin.

Domain registration is now handled SERVER-SIDE in signals.py via the
pretix plugin_enabled signal — NOT client-side in the browser and NOT
from here on every page load.

This file provides:
  - get_no_required_eu()  — reads EU/non-EU preference (flag file)
  - _detect_eu()          — IP geolocation helper used on first install
"""

import os
import json
import logging

import requests

logger = logging.getLogger(__name__)


def _get_flag_file():
    try:
        from django.conf import settings
        if hasattr(settings, "BASE_DIR"):
            return os.path.join(str(settings.BASE_DIR), ".aioa_registered.json")
    except Exception:
        pass
    return os.path.join(
        os.path.dirname(os.path.abspath(__file__)), ".aioa_registered.json"
    )


def _read_flag():
    flag_file = _get_flag_file()
    if not os.path.exists(flag_file):
        return {}
    try:
        with open(flag_file, "r") as f:
            data = json.load(f)
        if isinstance(data, dict) and "domain" in data and "domains" not in data:
            return {data["domain"]: data}
        return data.get("domains", {})
    except Exception:
        return {}


def _write_flag(domains):
    flag_file = _get_flag_file()
    try:
        with open(flag_file, "w") as f:
            json.dump({"domains": domains}, f, indent=2)
    except Exception as e:
        logger.warning("Could not write flag file: %s", e)


def get_no_required_eu():
    """
    Returns 1 (non-EU CDN) or 0 (EU CDN).
    Used by signals.py to choose the correct widget script URL.
    """
    try:
        flag_file = _get_flag_file()
        if not os.path.exists(flag_file):
            return 1
        with open(flag_file, "r") as f:
            data = json.load(f)
        domains = data.get("domains", {})
        if domains:
            first = next(iter(domains.values()))
            return first.get("no_required_eu", 1)
        return data.get("no_required_eu", 1)
    except Exception:
        return 1


def _detect_eu():
    """Detect whether the server is in the EU via IP geolocation."""
    try:
        resp = requests.get("https://ipapi.co/json/", timeout=5)
        if resp.status_code == 200:
            return resp.json().get("in_eu", False)
    except Exception:
        pass
    return False
