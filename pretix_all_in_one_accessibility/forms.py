from django import forms
from django.utils.safestring import mark_safe

# ── Choice constants ──────────────────────────────────────────────────────────

AIOA_SELECT_CHOICES = [
    ("top_left",      "Top Left"),
    ("top_center",    "Top Center"),
    ("top_right",     "Top Right"),
    ("middle_left",   "Middle Left"),
    ("middle_right",  "Middle Right"),
    ("bottom_left",   "Bottom Left"),
    ("bottom_center", "Bottom Center"),
    ("bottom_right",  "Bottom Right"),
]

AIOA_SIZE_CHOICES = [
    ("regular",  "Regular Size"),
    ("oversize", "Oversize"),
]

TO_THE_RIGHT_CHOICES = [
    ("to_the_left",  "To the left"),
    ("to_the_right", "To the right"),
]

TO_THE_BOTTOM_CHOICES = [
    ("to_the_bottom", "To the bottom"),
    ("to_the_top",    "To the top"),
]

AIOA_ICON_SIZE_CHOICES = [
    ("aioa-big-icon",         "Big"),
    ("aioa-medium-icon",      "Medium"),
    ("aioa-default-icon",     "Default"),
    ("aioa-small-icon",       "Small"),
    ("aioa-extra-small-icon", "Extra Small"),
]

# ── Icon choices use Skynet CDN SVG URLs (identical to Django module) ─────────
#
# KEY: option_value = "aioa-icon-type-{i}"  (what gets stored & sent to API)
#      icon_url     = official Skynet CDN SVG  (what's displayed as thumbnail)
#
# WHY CDN URLs, not local PNGs:
#   The local PNG files (icons/1.png … 29.png) were stored in a different
#   visual order than Skynet's official type numbering.  For example, the
#   "text/Accessibility-label" icon is aioa-icon-type-13 in Skynet's system,
#   but the same visual appeared at position 29 in the local PNG list.
#   When a user selected that thumbnail in the UI, the form submitted
#   "aioa-icon-type-29" — which maps to a completely DIFFERENT icon on
#   Skynet's CDN — causing the wrong icon to appear on the frontend.
#
#   By using the exact same CDN SVG URLs as the Django reference module,
#   thumbnail index i ALWAYS equals type number i.  What you see = what you get.

ICON_CHOICES = [
    (
        f"aioa-icon-type-{i}",
        f"https://www.skynettechnologies.com/sites/default/files/aioa-icon-type-{i}.svg",
    )
    for i in range(1, 30)
]

ICON_CHOICES_DICT = dict(ICON_CHOICES)


# ── Custom form widgets ───────────────────────────────────────────────────────

class IconSelectWidget(forms.Widget):
    """
    Clickable tile-style icon selector.

    Each choice is (option_value, icon_url) where icon_url is a full
    https:// CDN URL — used directly in <img src>, no static() needed.
    Mirrors the Django module's IconSelectWidget in forms.py exactly.
    """

    def __init__(self, attrs=None, choices=()):
        super().__init__(attrs)
        self.choices = list(choices)

    def render(self, name, value, attrs=None, renderer=None):
        html = ['<div class="aioa-icon-select-wrapper">']

        for option_value, icon_url in self.choices:
            selected = "selected" if value == option_value else ""
            checked  = "checked"  if value == option_value else ""
            html.append(f"""
                <label class="aioa-icon-option {selected}">
                    <input type="radio" name="{name}" value="{option_value}" {checked} hidden>
                    <img src="{icon_url}" alt="{option_value}" class="aioa-icon-img"/>
                    <span class="aioa-checkmark">&#10004;</span>
                </label>
            """)

        html.append("</div>")
        return mark_safe("\n".join(html))


class IconSizeSelectWidget(forms.Widget):
    """
    Clickable tile-style icon-size selector with live icon preview.

    icon_url: full CDN URL of the currently selected icon type.
              Updated by AllInOneAccessibilityForm.get_initial() so the
              preview always reflects the saved icon type — same as Django
              module's AllinOneAccessibilityForm.__init__() which passes
              icon_url=dict(ICON_CHOICES).get(icon_value) to IconSizeSelectWidget.
    """

    SIZE_MAP = {
        "aioa-big-icon":         85,
        "aioa-medium-icon":      65,
        "aioa-default-icon":     55,
        "aioa-small-icon":       45,
        "aioa-extra-small-icon": 35,
    }

    # Default to icon-type-1 CDN URL (same fallback as Django module)
    DEFAULT_ICON_URL = "https://www.skynettechnologies.com/sites/default/files/aioa-icon-type-1.svg"

    def __init__(self, attrs=None, icon_url=None, choices=()):
        super().__init__(attrs)
        self.icon_url = icon_url or self.DEFAULT_ICON_URL
        self.choices  = list(choices)

    def render(self, name, value, attrs=None, renderer=None):
        html = ['<div class="aioa-icon-size-select-wrapper">']

        for option_value, _ in self.choices:
            selected = "selected" if value == option_value else ""
            checked  = "checked"  if value == option_value else ""
            size     = self.SIZE_MAP.get(option_value, 55)

            html.append(f"""
                <label class="aioa-icon-option {selected}" data-size="{size}">
                    <input type="radio" name="{name}" value="{option_value}" {checked} hidden>
                    <img src="{self.icon_url}"
                         alt="{option_value}"
                         style="width:{size}px;height:{size}px;"
                         class="aioa-icon-img-size"/>
                    <span class="aioa-checkmark">&#10004;</span>
                </label>
            """)

        html.append("</div>")
        return mark_safe("\n".join(html))


# ── Main settings form ────────────────────────────────────────────────────────

class AllInOneAccessibilityForm(forms.Form):

    aioa_color_code = forms.CharField(
        required=False,
        label="Hex Color Code",
        help_text="Customize the ADA Widget color. Example: FFA500 (without #)",
    )

    enable_widget_icon_position = forms.BooleanField(
        required=False,
        initial=False,
        label="Enable precise accessibility widget icon position",
    )

    to_the_right_px = forms.IntegerField(
        min_value=0, max_value=250, initial=20,
        label="Right offset (PX)",
        help_text="0 – 250px are permitted values",
    )
    to_the_right = forms.ChoiceField(
        choices=TO_THE_RIGHT_CHOICES,
        initial="to_the_left",
        label="Horizontal direction",
    )

    to_the_bottom_px = forms.IntegerField(
        min_value=0, max_value=250, initial=20,
        label="Bottom offset (PX)",
        help_text="0 – 250px are permitted values",
    )
    to_the_bottom = forms.ChoiceField(
        choices=TO_THE_BOTTOM_CHOICES,
        initial="to_the_bottom",
        label="Vertical direction",
    )

    aioa_place = forms.ChoiceField(
        choices=AIOA_SELECT_CHOICES,
        initial="bottom_right",
        label="Where to place the accessibility icon",
    )

    aioa_size = forms.ChoiceField(
        choices=AIOA_SIZE_CHOICES,
        initial="oversize",
        label="Widget size",
    )

    aioa_icon_type = forms.ChoiceField(
        choices=ICON_CHOICES,
        widget=IconSelectWidget(choices=ICON_CHOICES),
        initial="aioa-icon-type-1",
        label="Select icon type",
    )

    enable_icon_custom_size = forms.BooleanField(
        required=False,
        initial=False,
        label="Enable custom icon size",
    )

    aioa_size_value = forms.IntegerField(
        min_value=20, max_value=150, initial=50,
        label="Exact icon size (PX)",
        help_text="20 – 150px are permitted values",
    )

    aioa_icon_size = forms.ChoiceField(
        choices=AIOA_ICON_SIZE_CHOICES,
        widget=IconSizeSelectWidget(
            choices=AIOA_ICON_SIZE_CHOICES,
        ),
        initial="aioa-default-icon",
        label="Icon size for desktop",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mirror Django module's AllinOneAccessibilityForm.__init__():
        # update the icon-size widget's preview to match the currently saved icon type.
        # initial is set by views.py get_initial(), so it's available here.
        icon_value = (
            self.initial.get("aioa_icon_type")
            or self.data.get("aioa_icon_type")
            or "aioa-icon-type-1"
        )
        icon_url = ICON_CHOICES_DICT.get(icon_value, IconSizeSelectWidget.DEFAULT_ICON_URL)
        self.fields["aioa_icon_size"].widget.icon_url = icon_url

    def clean(self):
        cleaned = super().clean()

        # Keep icon-size widget preview in sync with the submitted icon type
        # (handles the case where the form is re-rendered after a POST)
        selected  = cleaned.get("aioa_icon_type", "aioa-icon-type-1")
        icon_url  = ICON_CHOICES_DICT.get(selected, IconSizeSelectWidget.DEFAULT_ICON_URL)
        self.fields["aioa_icon_size"].widget.icon_url = icon_url

        return cleaned
