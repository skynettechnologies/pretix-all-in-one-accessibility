"""
signals.py — All in One Accessibility for pretix
-------------------------------------------------

Behaviour:

  1. ENABLED  → inject_aioa_presale returns the widget <script> tag.
  2. DISABLED → inject_aioa_presale returns "".
               middleware.py (AIOAAdminHideMiddleware) detects disabled state via
               request.organizer and injects CSS + MutationObserver hide snippet
               into every frontend HTML response — removes any browser-cached widget.

  3. Handles both page types correctly:
     - Event page     → html_head sender = Event     → organizer via sender.organizer
     - Organizer page → html_head sender = Organizer → organizer = sender directly

  4. Always refresh_from_db(fields=["plugins"]) — never trust stale in-memory cache.
     Disable takes effect on the very next frontend request.

  5. add-user-domain API called SERVER-SIDE exactly ONCE on first enable.
     Flagged in organizer.settings — retries only if previous call failed.

  6. widget-setting-update-platform called server-side on settings Save (views.py).

  7. Admin/control pages: middleware hides widget unconditionally.
"""

import logging

from django.dispatch import receiver

logger = logging.getLogger(__name__)

PLUGIN_NAME    = "pretix_all_in_one_accessibility"
SETTING_PREFIX = "aioa_"

EU_SCRIPT_BASE     = "https://eu.skynettechnologies.com/accessibility/js/all-in-one-accessibility-js-widget-minify.js"
NON_EU_SCRIPT_BASE = "https://www.skynettechnologies.com/accessibility/js/all-in-one-accessibility-js-widget-minify.js"

SKYNET_CONNECT = [
    "https://www.skynettechnologies.com",
    "https://eu.skynettechnologies.com",
    "https://ada.skynettechnologies.us",
    "https://freeada.skynettechnologies.com",
]
SKYNET_SCRIPT = [
    "https://www.skynettechnologies.com",
    "https://eu.skynettechnologies.com",
]
SKYNET_FONT = [
    "https://www.skynettechnologies.com",
    "https://eu.skynettechnologies.com",
    "https://fonts.googleapis.com",
    "https://fonts.gstatic.com",
]
SKYNET_IMG = [
    "https://www.skynettechnologies.com",
    "https://eu.skynettechnologies.com",
    "https://ada.skynettechnologies.us",
    "data:",
]
SKYNET_STYLE = [
    "https://www.skynettechnologies.com",
    "https://eu.skynettechnologies.com",
    "https://fonts.googleapis.com",
    "'unsafe-inline'",
]

DEFAULTS = {
    "aioa_color_code":             "420083",
    "enable_widget_icon_position": False,
    "to_the_right_px":             20,
    "to_the_right":                "to_the_left",
    "to_the_bottom_px":            20,
    "to_the_bottom":               "to_the_bottom",
    "aioa_place":                  "bottom_right",
    "aioa_size":                   "oversize",
    "aioa_icon_type":              "aioa-icon-type-1",
    "enable_icon_custom_size":     False,
    "aioa_size_value":             50,
    "aioa_icon_size":              "aioa-default-icon",
}


# ─────────────────────────────────────────────────────────────────────────────
# CSP EXTENSION
# ─────────────────────────────────────────────────────────────────────────────

def _append_csp_values(existing, additions):
    existing_parts = set(existing.split()) if existing else set()
    for val in additions:
        if val not in existing_parts:
            existing_parts.add(val)
    return " ".join(sorted(existing_parts))


def _patch_csp_settings():
    try:
        from django.conf import settings as django_settings
        additions = (
            "connect-src " + " ".join(SKYNET_CONNECT) + "; "
            "script-src "  + " ".join(SKYNET_SCRIPT)  + "; "
            "font-src "    + " ".join(SKYNET_FONT)     + "; "
            "img-src "     + " ".join(SKYNET_IMG)      + "; "
            "style-src "   + " ".join(SKYNET_STYLE)
        )
        existing = getattr(django_settings, "CSP_ADDITIONAL_HEADER", "") or ""
        if "skynettechnologies" not in existing:
            new_val = (existing.rstrip("; ") + "; " + additions).lstrip("; ")
            django_settings.CSP_ADDITIONAL_HEADER = new_val
    except Exception as e:
        logger.warning("CSP patch warning: %s", e)


try:
    from pretix.base.signals import csp_set_header as _csp_signal

    @receiver(_csp_signal)
    def aioa_extend_csp(sender, headers, **kwargs):
        headers["connect-src"] = _append_csp_values(headers.get("connect-src", ""), SKYNET_CONNECT)
        headers["script-src"]  = _append_csp_values(headers.get("script-src", ""),  SKYNET_SCRIPT)
        headers["font-src"]    = _append_csp_values(headers.get("font-src", ""),    SKYNET_FONT)
        headers["img-src"]     = _append_csp_values(headers.get("img-src", ""),     SKYNET_IMG)
        headers["style-src"]   = _append_csp_values(headers.get("style-src", ""),   SKYNET_STYLE)

except ImportError:
    _patch_csp_settings()


# ─────────────────────────────────────────────────────────────────────────────
# CORE PLUGIN-ENABLED CHECK
# ─────────────────────────────────────────────────────────────────────────────

def _is_plugin_enabled_for_organizer(organizer):
    """
    Single source of truth: read organizer.plugins directly.

    pretix stores the list of enabled organizer-level plugins as a
    comma-separated string in the Organizer model's `plugins` DB field.
    Reading it here gives us real-time accuracy: the moment an admin
    disables the plugin via the UI, this field is updated in the DB,
    and the very next frontend request returns False.
    """
    try:
        plugins_csv = getattr(organizer, "plugins", None)
        if plugins_csv is None:
            organizer.refresh_from_db(fields=["plugins"])
            plugins_csv = getattr(organizer, "plugins", "") or ""
        enabled = [p.strip() for p in plugins_csv.split(",") if p.strip()]
        return PLUGIN_NAME in enabled
    except Exception as e:
        logger.error("Plugin-enabled check error: %s", e)
        return False   # fail closed — never inject if check fails


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _get_no_required_eu():
    try:
        from .registration import get_no_required_eu
        return get_no_required_eu()
    except Exception:
        return 1


def _read_setting(organizer, field_name):
    key     = f"{SETTING_PREFIX}{field_name}"
    default = DEFAULTS.get(field_name)
    raw     = organizer.settings.get(key, as_type=None, default=None)
    if raw is None:
        return default
    if isinstance(default, bool):
        return str(raw).lower() in ("true", "1", "yes")
    if isinstance(default, int):
        try:
            return int(raw)
        except (ValueError, TypeError):
            return default
    return raw


def _get_domain_url():
    """Return (domain_url, domain_name) from SITE_URL — never localhost."""
    try:
        from django.conf import settings as _s
        from urllib.parse import urlparse as _up
        _p = _up(getattr(_s, "SITE_URL", "") or "")
        _port = f":{_p.port}" if _p.port and _p.port not in (80, 443) else ""
        if _p.hostname and _p.hostname not in ("localhost", "127.0.0.1"):
            return f"{_p.scheme}://{_p.hostname}{_port}", _p.hostname
    except Exception:
        pass
    return "", ""


def _build_widget_script(organizer):
    """Return the widget <script> tag plus an optional inline <style> for precise positioning."""
    color   = (_read_setting(organizer, "aioa_color_code") or "420083").lstrip("#")
    precise = bool(_read_setting(organizer, "enable_widget_icon_position"))
    place   = _read_setting(organizer, "aioa_place") or "bottom_right"

    no_eu       = _get_no_required_eu()
    script_base = EU_SCRIPT_BASE if no_eu == 0 else NON_EU_SCRIPT_BASE

    if not precise:
        script_src = f"{script_base}?colorcode=%23{color}&position={place}"
        return f'<script id="aioa-adawidget" src="{script_src}" defer></script>\n'

    # ── Precise position mode ────────────────────────────────────────────────
    right_px   = int(_read_setting(organizer, "to_the_right_px")  or 20)
    right_dir  = _read_setting(organizer, "to_the_right")  or "to_the_left"
    bottom_px  = int(_read_setting(organizer, "to_the_bottom_px") or 20)
    bottom_dir = _read_setting(organizer, "to_the_bottom") or "to_the_bottom"

    h_prop = "left"   if right_dir  == "to_the_left"   else "right"
    v_prop = "bottom" if bottom_dir == "to_the_bottom" else "top"

    script_src = f"{script_base}?colorcode=%23{color}&position="

    h_opposite = "right"  if h_prop == "left"   else "left"
    v_opposite = "top"    if v_prop == "bottom"  else "bottom"

    inline_style = (
        f'<style id="aioa-precise-position">'
        f'#ada-button-frame, #adawidget, .adawidget, #aioa-widget-container {{'
        f' position: fixed !important;'
        f' {h_prop}: {right_px}px !important;'
        f' {h_opposite}: auto !important;'
        f' {v_prop}: {bottom_px}px !important;'
        f' {v_opposite}: auto !important;'
        f'}}'
        f'</style>\n'
    )

    return (
        f'<script id="aioa-adawidget" src="{script_src}" defer></script>\n'
        + inline_style
    )


# ─────────────────────────────────────────────────────────────────────────────
# add-user-domain — called ONCE server-side when plugin is first enabled
# ─────────────────────────────────────────────────────────────────────────────

def _call_add_user_domain_once(organizer):
    """
    POST add-user-domain API exactly once per organizer.
    Flag stored in organizer.settings.
    If API call fails (non-2xx or exception), flag is NOT set → retries on next enable.
    """
    flag_key = f"{SETTING_PREFIX}domain_registered"
    already  = organizer.settings.get(flag_key, as_type=None, default=None)
    if str(already).lower() in ("true", "1", "yes"):
        return

    domain_url, domain_name = _get_domain_url()
    if not domain_name:
        return

    try:
        import requests as _req
        import base64
        from datetime import datetime

        no_eu = _get_no_required_eu()
        payload = {
            "name":            domain_name,
            "email":           f"no-reply@{domain_name}",
            "company_name":    "",
            "website":         base64.b64encode(domain_url.encode()).decode(),
            "package_type":    "free-widget",
            "start_date":      datetime.utcnow().isoformat(),
            "end_date":        "",
            "price":           "",
            "discount_price":  "0",
            "platform":        "Pretix",
            "api_key":         "",
            "is_trial_period": "",
            "is_free_widget":  "1",
            "bill_address":    "",
            "country":         "",
            "state":           "",
            "city":            "",
            "post_code":       "",
            "transaction_id":  "",
            "subscr_id":       "",
            "payment_source":  "",
            "no_required_eu":  no_eu,
        }
        resp = _req.post(
            "https://ada.skynettechnologies.us/api/add-user-domain",
            json=payload,
            timeout=10,
        )
        if 200 <= resp.status_code < 300:
            organizer.settings.set(flag_key, "true")
            logger.info("add-user-domain registered: %s (HTTP %s)", domain_name, resp.status_code)
        else:
            logger.warning("add-user-domain HTTP %s — will retry on next enable", resp.status_code)

    except Exception as e:
        logger.warning("add-user-domain exception: %s — will retry on next enable", e)


# ─────────────────────────────────────────────────────────────────────────────
# PLUGIN ENABLED signal
# ─────────────────────────────────────────────────────────────────────────────

def _delete_all_settings(organizer):
    """
    HARD DELETE every aioa_* key from the organizer's OrganizerSetting table.

    pretix persists OrganizerSetting rows in the database permanently — they
    survive plugin disable, uninstall, and reinstall. Simply writing default
    values back would leave the rows present, so `organizer.settings.get(key)`
    returns a stored value and `raw is None` is NEVER true.

    After deletion:
      • organizer.settings.get(key) returns None
      • get_initial() in views.py sees raw=None → falls through to DEFAULTS
      • The settings page shows the canonical defaults on first open
    """
    all_keys = (
        [f"{SETTING_PREFIX}{f}" for f in DEFAULTS]
        + [f"{SETTING_PREFIX}domain_registered", f"{SETTING_PREFIX}first_run_done"]
    )

    for key in all_keys:
        try:
            organizer.settings.delete(key)
        except Exception:
            pass


try:
    from pretix.base.signals import plugin_enabled as _plugin_enabled_signal

    @receiver(_plugin_enabled_signal)
    def aioa_on_plugin_enabled(sender, plugin, organizer=None, **kwargs):
        """
        Fired by pretix when organizer enables the plugin.

        Two responsibilities:
          1. Ensure all AIOA settings exist with their default values.
          2. Call add-user-domain API once per organizer (domain registration).
        """
        if plugin != PLUGIN_NAME:
            return
        _org = organizer or (sender if hasattr(sender, "settings") else None)
        if _org is None:
            return
        _delete_all_settings(_org)
        _call_add_user_domain_once(_org)

except ImportError:
    logger.debug("pretix.base.signals.plugin_enabled not available")


# ─────────────────────────────────────────────────────────────────────────────
# PLUGIN DISABLED signal
# ─────────────────────────────────────────────────────────────────────────────

try:
    from pretix.base.signals import plugin_disabled as _plugin_disabled_signal

    @receiver(_plugin_disabled_signal)
    def aioa_on_plugin_disabled(sender, plugin, organizer=None, **kwargs):
        """
        Fired by pretix when an organizer disables the plugin.
        Resets every aioa_* organizer setting so re-enabling starts with a clean slate.
        """
        if plugin != PLUGIN_NAME:
            return
        _org = organizer or (sender if hasattr(sender, "settings") else None)
        if _org is None:
            return
        _delete_all_settings(_org)

except ImportError:
    logger.debug("pretix.base.signals.plugin_disabled not available")


# ─────────────────────────────────────────────────────────────────────────────
# PRESALE (FRONTEND) SIGNAL
# Widget injected ONLY when plugin is enabled. Disabled = empty string returned.
# ─────────────────────────────────────────────────────────────────────────────

def _resolve_organizer(sender):
    """
    pretix fires html_head with different sender types:
      - Event page     → sender is an Event instance  → organizer via sender.organizer
      - Organizer page → sender IS the Organizer instance (has .plugins field)

    Returns the Organizer instance, or None if it cannot be resolved.
    """
    if sender is None:
        return None
    organizer = getattr(sender, "organizer", None)
    if organizer is not None:
        return organizer
    if hasattr(sender, "plugins"):
        return sender
    return None


try:
    from pretix.presale.signals import html_head as _presale_html_head

    @receiver(_presale_html_head)
    def inject_aioa_presale(sender, request=None, **kwargs):
        """
        Inject the Skynet widget <script> tag into frontend HTML pages.

        Works on BOTH:
          - Event pages   (sender = Event,     organizer = sender.organizer)
          - Organizer pages (sender = Organizer, organizer = sender directly)

        Always reads organizer.plugins FRESH from the DB (refresh_from_db)
        so disable takes effect on the very next request — no stale cache.

        When plugin is DISABLED this returns "" (no script tag injected).
        The middleware (AIOAAdminHideMiddleware) then injects the hide snippet
        to remove any browser-cached widget from the DOM.
        """
        organizer = _resolve_organizer(sender)
        if organizer is None:
            return ""

        try:
            organizer.refresh_from_db(fields=["plugins"])
            plugins_csv = getattr(organizer, "plugins", "") or ""
            enabled_plugins = [p.strip() for p in plugins_csv.split(",") if p.strip()]
            plugin_active = PLUGIN_NAME in enabled_plugins
        except Exception as e:
            logger.error("Plugin-enabled check error: %s", e)
            plugin_active = False  # fail closed — never inject on error

        if not plugin_active:
            return ""  # Middleware handles hide snippet on disabled state

        try:
            return _build_widget_script(organizer)
        except Exception as e:
            logger.error("Widget injection error: %s", e)
            return ""

except ImportError as e:
    logger.error("Could not wire presale html_head: %s", e)
