import re

import markdown as md
from django.template import Library, Node
from django.urls import reverse
from django.utils.safestring import mark_safe

from ...core.models import FormSet
from ...core.utils import dict_get_nested, dict_setdefault
from ...registration.models import Registration

register = Library()


class EscapeScriptNode(Node):
    def __init__(self, nodelist):
        super(EscapeScriptNode, self).__init__()
        self.nodelist = nodelist

    def render(self, context):
        out = self.nodelist.render(context)
        escaped_out = out.replace("</script>", "<\\/script>")
        return escaped_out


@register.tag()
def escapescript(parser, token):
    nodelist = parser.parse(("endescapescript",))
    parser.delete_first_token()
    return EscapeScriptNode(nodelist)


@register.filter
def islist(value):
    return isinstance(value, (list, tuple))


@register.filter
def isdict(value):
    return isinstance(value, (dict,))


@register.inclusion_tag("dump/dump.html")
def dump(value):
    return {"value": value}


@register.inclusion_tag("dump/list.html")
def dump_list(value):
    return {"value": value}


@register.inclusion_tag("dump/dict.html")
def dump_dict(value):
    return {"value": value}


@register.filter(name="smart")
def smart_attr(field, attr):
    return field.field.flex_field.advanced.get("smart", {}).get(attr, "")


@register.simple_tag()
def formset_config(formset):
    return formset.fs.advanced.get("smart", {}).get("widget", FormSet.FORMSET_DEFAULT_ATTRS["smart"]["widget"])


@register.filter(name="lookup")
def lookup(value, arg):
    # value_dict = ast.literal_eval(value)
    return value.get(arg, None)


@register.filter()
def is_base64(element):
    expression = "^([A-Za-z0-9+/]{4})*([A-Za-z0-9+/]{3}=|[A-Za-z0-9+/]{2}==)?$"
    return re.match(expression, element)


@register.inclusion_tag("buttons/link.html")
def link(registration):
    config = registration.advanced.copy()
    config = dict_setdefault(config, Registration.ADVANCED_DEFAULT_ATTRS)
    widget = dict_get_nested(config, "smart.buttons.link.widget")
    attrs = dict_get_nested(widget, "attrs")

    if "class" not in attrs:
        widget["attrs"]["style"] = "background-color:#01ADF1;color:white;"
        widget["attrs"]["class"] = "text-white border-0 py-4 px-8 " " rounded " " text-center text-2xl"
    widget["attrs"]["href"] = reverse("register", args=[registration.locale, registration.slug])
    return {
        "reg": registration,
        "widget": widget,
    }


@register.filter()
def markdown(value):
    if value:
        p = md.markdown(value, extensions=["markdown.extensions.fenced_code"])
        return mark_safe(p)
    return ""


@register.filter(name="md")
def _md(value):
    if value:
        p = md.markdown(value, extensions=["markdown.extensions.fenced_code"])
        return mark_safe(p.replace("<p>", "").replace("</p>", ""))
    return ""
