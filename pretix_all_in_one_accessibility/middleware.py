"""
middleware.py — All in One Accessibility for pretix
----------------------------------------------------

Two responsibilities:

1. /control/ (admin) pages — ALWAYS hide the widget, regardless of plugin state.
   Identical to before.

2. Frontend (presale) pages — when the plugin is DISABLED for that organizer,
   actively inject CSS + MutationObserver JS to remove any residual/cached widget.

   WHY this is needed (Odoo reference):
   In Odoo the widget lives inside a template that inherits website.layout.
   When the module is disabled the template override is gone entirely — the
   <script> tag is never rendered, so the widget never appears.

   Pretix uses a signal (html_head) to inject the <script> tag at runtime.
   When the plugin is disabled we stop injecting the tag, but the browser may
   have cached the Skynet CDN script from a previous enabled state, causing the
   widget to still appear. The hide snippet below is the pretix equivalent of
   "template removed" — it ensures the widget is erased from the DOM on every
   frontend page load when the plugin is disabled.

3. Frontend pages when plugin IS ENABLED — middleware does NOTHING.
   The signal (signals.py inject_aioa_presale) already injects the <script> tag.
"""

PLUGIN_NAME = "pretix_all_in_one_accessibility"

# ── Shared hide snippet (used for both admin and disabled-frontend pages) ────

_HIDE_SNIPPET = b"""
<style id="aioa-widget-hide">
#ada-button-frame,
#adawidget,
.adawidget,
#aioa-widget-container,
.aioa-widget-container,
#accessibility-widget-container,
iframe[id*="ada"],
iframe[src*="skynettechnologies"],
div[id*="adawidget"],
[id^="aioa-"],
[class^="aioa-widget"] {
    display: none !important;
    visibility: hidden !important;
    opacity: 0 !important;
    pointer-events: none !important;
    width: 0 !important;
    height: 0 !important;
    position: absolute !important;
    left: -9999px !important;
}
</style>
<script id="aioa-widget-remove">
(function(){
    var SEL=[
        '#ada-button-frame','#adawidget','.adawidget',
        '#aioa-widget-container','.aioa-widget-container',
        '#accessibility-widget-container',
        'iframe[src*="skynettechnologies"]'
    ];
    function rm(){
        SEL.forEach(function(s){
            try{ document.querySelectorAll(s).forEach(function(el){
                el.parentNode && el.parentNode.removeChild(el);
            }); } catch(e) {}
        });
    }
    rm();
    document.addEventListener('DOMContentLoaded', rm);
    window.addEventListener('load', rm);
    if (window.MutationObserver) {
        new MutationObserver(function(ms) {
            ms.forEach(function(m) {
                m.addedNodes.forEach(function(n) {
                    if (n.nodeType !== 1) return;
                    var id  = n.id || '';
                    var src = n.src || (n.getAttribute && n.getAttribute('src')) || '';
                    if (id.indexOf('ada')  !== -1 || id.indexOf('aioa') !== -1 ||
                        src.indexOf('skynettechnologies') !== -1) {
                        n.parentNode && n.parentNode.removeChild(n);
                    }
                });
            });
        }).observe(document.documentElement, {childList: true, subtree: true});
    }
})();
</script>
"""


def _inject_snippet(response, snippet):
    """Insert snippet just before </body> (or </head> as fallback)."""
    try:
        content = response.content
        if b'</body>' in content:
            response.content = content.replace(b'</body>', snippet + b'</body>', 1)
        elif b'</head>' in content:
            response.content = content.replace(b'</head>', snippet + b'</head>', 1)
    except Exception:
        pass
    return response


def _is_html(response):
    return (
        hasattr(response, 'content')
        and 'text/html' in response.get('Content-Type', '')
    )


def _plugin_enabled_for_organizer(organizer):
    """
    Read organizer.plugins FRESH from the DB every time.
    This is the same single source of truth used in signals.py.
    Always refresh_from_db — never trust the cached in-memory value.
    """
    try:
        organizer.refresh_from_db(fields=["plugins"])
        plugins_csv = getattr(organizer, "plugins", "") or ""
        return PLUGIN_NAME in [p.strip() for p in plugins_csv.split(",") if p.strip()]
    except Exception:
        return False  # fail closed


class AIOAAdminHideMiddleware:
    """
    Single middleware that handles both /control/ and frontend pages.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if not _is_html(response):
            return response

        # ── 1. Admin / control pages → ALWAYS hide ───────────────────────────
        if '/control/' in request.path:
            return _inject_snippet(response, _HIDE_SNIPPET)

        # ── 2. Frontend (presale) pages ──────────────────────────────────────
        # Only act when pretix has attached an organizer to the request.
        # (pretix sets request.organizer on all presale views.)
        organizer = getattr(request, 'organizer', None)
        if organizer is None:
            return response

        # If plugin is ENABLED → signal already injected the <script> tag → do nothing.
        # If plugin is DISABLED → inject the hide snippet to remove any cached widget.
        if not _plugin_enabled_for_organizer(organizer):
            return _inject_snippet(response, _HIDE_SNIPPET)

        return response
