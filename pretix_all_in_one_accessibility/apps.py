import logging

from django.utils.translation import gettext_lazy as _
from pretix.base.plugins import PluginConfig, PLUGIN_LEVEL_ORGANIZER
from . import __version__

logger = logging.getLogger(__name__)


class AccessibilityPluginApp(PluginConfig):
    name         = "pretix_all_in_one_accessibility"
    verbose_name = _(u"All in One Accessibility")

    class PretixPluginMeta:
        name        = _(u"All in One Accessibility")
        author      = "Skynet Technologies USA LLC"
        description = _(
            "Website accessibility widget for improving WCAG 2.0, 2.1, 2.2 and ADA compliance!"
        )
        visible  = True
        version  = __version__
        category = "FEATURE"
        featured = True
        level    = PLUGIN_LEVEL_ORGANIZER
        settings_links = [
            (
                (_(u"All in One Accessibility"), _(u"Settings")),
                "plugins:pretix_all_in_one_accessibility:settings",
                {},
            )
        ]

    def ready(self):
        from . import signals  # noqa: F401  — wires all signal receivers
        self._install_middleware()

    def _install_middleware(self):
        """
        Dynamically append AIOAAdminHideMiddleware to Django's MIDDLEWARE list.
        Runs at startup — active regardless of plugin enabled/disabled state.
        Ensures the widget is NEVER visible on /control/ pages.
        """
        try:
            from django.conf import settings
            mw_path = "pretix_all_in_one_accessibility.middleware.AIOAAdminHideMiddleware"
            mw_list = list(getattr(settings, "MIDDLEWARE", []))
            if mw_path not in mw_list:
                mw_list.append(mw_path)
                settings.MIDDLEWARE = mw_list
                logger.debug("AIOAAdminHideMiddleware registered")
        except Exception as e:
            logger.warning("Could not register middleware: %s", e)
