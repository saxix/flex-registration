"""
Create hreflang tags as specified by Google

https://support.google.com/webmasters/answer/189077?hl=en
"""

from django import template
from django.urls.base import resolve
from django.utils.safestring import mark_safe
from django.utils.translation import get_language

from smart_register.i18n.hreflang import languages, get_hreflang_info, reverse


register = template.Library()


@register.simple_tag(takes_context=True)
def translate_url(context, lang, view_name=None, *args, **kwargs):
    """
    Translate an url to a specific language.

    @param lang: Which language should the url be translated to.
    @param view_name: Which view to get url from, current if not set.
    """
    assert "request" in context, "translate_url needs request context"
    if view_name is None:
        reverse_match = resolve(context["request"].path)
        view_name = reverse_match.view_name
        args = reverse_match.args
        kwargs = reverse_match.kwargs
    return reverse(view_name, lang=lang, *args, **kwargs)


@register.simple_tag(takes_context=True)
def hreflang_tags(context, indent=0):
    """
    Create all hreflang <link> tags (which includes the current document as per the standard).
    """
    assert "request" in context, "hreflang_tags needs request context"
    hreflang_info = get_hreflang_info(context["request"].path)
    hreflang_html = []
    for lang, url in hreflang_info:
        hreflang_html.append('<link rel="alternate" hreflang="{0}" href="{1}" />\n'.format(lang, url))
    return mark_safe(("\t" * indent).join(hreflang_html))


def _make_list_html(path, incl_current):
    hreflang_info = get_hreflang_info(path, default=False)
    hreflang_html = ""
    for lang, url in hreflang_info:
        if lang == get_language() and incl_current:
            hreflang_html += '<li class="hreflang_current_language"><strong>{0}</strong></li>\n'.format(
                languages()[lang]
            )
        else:
            hreflang_html += '<li><a href="{0}" >{1}</a></li>\n'.format(url, languages()[lang])
    return hreflang_html


@register.simple_tag(takes_context=True)
def lang_list(context):
    """
    HTML list items with links to each language version of this document.
    The current document is included without link and with a special .hreflang_current_language class.
    """
    assert "request" in context, "lang_list needs request context"
    return _make_list_html(context["request"].path, incl_current=True)


@register.simple_tag(takes_context=True)
def other_lang_list(context):
    """
    Like lang_list, but the current language is excluded.
    """
    assert "request" in context, "other_lang_list needs request context"
    return _make_list_html(context["request"].path, incl_current=False)
