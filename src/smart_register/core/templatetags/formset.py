import logging

import markdown as md
from django.template import Library
from django.utils.safestring import mark_safe

from smart_register.i18n.gettext import gettext as _

from ...core.models import FormSet

logger = logging.getLogger(__name__)
register = Library()


@register.simple_tag()
def formset_config(formset):
    default = {
        "formCssClass": f"form-container-{formset.prefix}",
        "counterPrefix": "",
        "prefix": formset.prefix,
        "deleteContainerClass": f"{formset.fs.name}-delete",
        "addContainerClass": f"{formset.fs.name}-add",
        "addText": "Add Another",
        "addCssClass": "formset-add-button",
        "deleteText": "Remove",
        "deleteCssClass": "formset-delete-button",
        "keepFieldValues": False,
        "original": {},
        "onAdd": None,
        "onRemove": None,
    }
    fs_config = formset.fs.advanced.get("smart", {}).get("widget", FormSet.FORMSET_DEFAULT_ATTRS["smart"]["widget"])
    override = {k: v for k, v in fs_config.items() if v}
    config = {**default, **override}
    for e in ["addText", "deleteText", "counterPrefix"]:
        config[e] = _(config[e])
        config["original"][e] = config[e]
    return config


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
