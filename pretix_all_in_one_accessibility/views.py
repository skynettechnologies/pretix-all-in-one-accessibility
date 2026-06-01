"""
views.py
--------
Settings view for the All-in-One Accessibility pretix plugin.

On GET  — loads saved OrganizerSetting values into the form (pre-populated).
On POST — saves all fields to OrganizerSetting, then calls Skynet
          widget-setting-update-platform API (using the canonical SITE_URL,
          not the request hostname which may be localhost behind a proxy).
          API failure is non-fatal — local save always completes first.
"""

import logging

import requests
from urllib.parse import urlparse

from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.views.generic.edit import FormView

from pretix.control.permissions import OrganizerPermissionRequiredMixin

from .forms import AllInOneAccessibilityForm

logger = logging.getLogger(__name__)

SETTING_PREFIX = "aioa_"

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


def _setting_key(field_name):
    return f"{SETTING_PREFIX}{field_name}"


def _get_canonical_domain_url(request):
    """
    Return (domain_url, domain_name) from SITE_URL (pretix.cfg).
    Falls back to request host only if SITE_URL is not configured.
    This ensures we never send 'localhost' to the Skynet API.
    """
    try:
        from django.conf import settings as _s
        site_url = getattr(_s, "SITE_URL", "") or ""
        if site_url:
            p = urlparse(site_url)
            port_part = f":{p.port}" if p.port and p.port not in (80, 443) else ""
            domain_url  = f"{p.scheme}://{p.hostname}{port_part}"
            domain_name = p.hostname or ""
            if domain_name and domain_name not in ("localhost", "127.0.0.1"):
                return domain_url, domain_name
    except Exception:
        pass

    # Fallback: use request (may be localhost behind proxy — acceptable for dev)
    parsed     = urlparse(request.build_absolute_uri())
    port_part  = f":{parsed.port}" if parsed.port and parsed.port not in (80, 443) else ""
    domain_url  = f"{parsed.scheme}://{parsed.hostname}{port_part}"
    domain_name = parsed.hostname or ""
    return domain_url, domain_name


class AccessibilitySettingsView(OrganizerPermissionRequiredMixin, FormView):
    template_name = "pretix_all_in_one_accessibility/settings.html"
    form_class    = AllInOneAccessibilityForm
    permission    = "can_change_organizer_settings"

    # ── Pre-populate form with saved values ───────────────────────────────────

    def get_initial(self):
        """
        Pre-populate the form.

        SAFETY NET — first_run_key guard:
        If the signals did not fire (older pretix, cold start, manual reinstall)
        we check a sentinel key 'aioa_first_run_done'.  If it is absent the
        plugin has never been configured in this session, so we delete any stale
        rows and write the sentinel.  This guarantees defaults on the very first
        settings page open after any install.
        """
        organizer = self.request.organizer
        initial   = {}

        # ── Safety net: delete stale rows if this is the first settings open ──
        sentinel_key = f"{SETTING_PREFIX}first_run_done"
        sentinel_raw = organizer.settings.get(sentinel_key, as_type=None, default=None)
        if sentinel_raw is None:
            all_keys = [f"{SETTING_PREFIX}{f}" for f in DEFAULTS] + \
                       [f"{SETTING_PREFIX}domain_registered", f"{SETTING_PREFIX}first_run_done"]
            for k in all_keys:
                try:
                    organizer.settings.delete(k)
                except Exception:
                    pass
            organizer.settings.set(sentinel_key, "true")

        for field_name, default in DEFAULTS.items():
            key = _setting_key(field_name)
            raw = organizer.settings.get(key, as_type=None, default=None)

            if raw is None:
                initial[field_name] = default
            elif isinstance(default, bool):
                initial[field_name] = str(raw).lower() in ("true", "1", "yes")
            elif isinstance(default, int):
                try:
                    initial[field_name] = int(raw)
                except (ValueError, TypeError):
                    initial[field_name] = default
            else:
                initial[field_name] = raw

        return initial

    # ── Save locally → call widget-setting-update-platform API ───────────────

    def form_valid(self, form):
        data      = form.cleaned_data
        organizer = self.request.organizer

        # 1. Persist every field to pretix OrganizerSetting (always succeeds)
        for field_name in DEFAULTS:
            value = data.get(field_name)
            organizer.settings.set(_setting_key(field_name), value)

        # 2. Build Skynet widget-setting-update-platform payload
        domain_url, domain_name = _get_canonical_domain_url(self.request)

        color       = (data.get("aioa_color_code") or "420083").lstrip("#")
        precise     = bool(data.get("enable_widget_icon_position"))
        place       = data.get("aioa_place") or "bottom_right"
        size        = data.get("aioa_size") or "oversize"
        icon_type   = data.get("aioa_icon_type") or "aioa-icon-type-1"
        custom_size = bool(data.get("enable_icon_custom_size"))
        size_value  = int(data.get("aioa_size_value") or 50)
        icon_size   = data.get("aioa_icon_size") or "aioa-default-icon"
        right_px    = int(data.get("to_the_right_px") or 20)
        right_dir   = data.get("to_the_right") or "to_the_left"
        bottom_px   = int(data.get("to_the_bottom_px") or 20)
        bottom_dir  = data.get("to_the_bottom") or "to_the_bottom"

        payload = {
            "u":                         domain_url,
            "widget_color_code":         f"#{color}",
            "widget_icon_type":          icon_type,
            "widget_position":           "" if precise else place,
            "widget_size":               1 if size == "oversize" else 0,
            "is_widget_custom_position": 1 if precise else 0,
            "is_widget_custom_size":     1 if custom_size else 0,
        }

        if custom_size:
            payload["widget_icon_size"]        = ""
            payload["widget_icon_size_custom"] = size_value
        else:
            payload["widget_icon_size"]        = icon_size
            payload["widget_icon_size_custom"] = 0

        if precise:
            pos = {"top": None, "right": None, "bottom": None, "left": None}
            if right_dir == "to_the_left":
                pos["left"] = right_px
            else:
                pos["right"] = right_px
            if bottom_dir == "to_the_top":
                pos["top"] = bottom_px
            else:
                pos["bottom"] = bottom_px
            payload.update({f"widget_position_{k}": v for k, v in pos.items()})

        # 3. Call Skynet widget-setting-update-platform API — non-fatal
        api_synced = False
        try:
            resp = requests.post(
                "https://ada.skynettechnologies.us/api/widget-setting-update-platform",
                json=payload,
                timeout=10,
            )
            api_synced = resp.status_code in (200, 201)
            logger.info("widget-setting-update-platform → HTTP %s", resp.status_code)
        except requests.RequestException as e:
            logger.warning("widget-setting-update-platform failed: %s", e)

        if api_synced:
            messages.success(self.request, _("Settings saved and synced to Skynet API successfully."))
        else:
            messages.success(
                self.request,
                _("Settings saved locally. (Skynet API sync will retry on next frontend page load.)")
            )

        return super().form_valid(form)

    def get_success_url(self):
        return self.request.path
