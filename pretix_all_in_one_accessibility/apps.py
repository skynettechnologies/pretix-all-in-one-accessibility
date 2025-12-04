from django.utils.translation import gettext_lazy as _
from pretix.base.plugins import PluginConfig, PLUGIN_LEVEL_ORGANIZER
from . import __version__


class AccessibilityPluginApp(PluginConfig):
    name = "pretix_all_in_one_accessibility"
    verbose_name = _("All In One Accessibility")

    class PretixPluginMeta:
        name = _("All In One Accessibility")
        author = "Your Name"
        description = _("")
        visible = True
        version = __version__
        # category = "INTEGRATION"
        category = "FEATURE"
        featured = True
        level = PLUGIN_LEVEL_ORGANIZER
        # level = PLUGIN_LEVEL_EVENT
        settings_links = [
            (("Accessibility", "Settings"), "plugins:pretix_all_in_one_accessibility:settings", {})
        ]

    def ready(self):
        from . import views  # noqa

    
       
