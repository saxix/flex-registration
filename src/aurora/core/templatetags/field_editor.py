from typing import Dict

import logging

from django.template import Library

logger = logging.getLogger(__name__)
register = Library()


@register.filter()
def field(form, field_name):
    return form[field_name]


@register.filter()
def get(d: Dict, key: str):
    return d[key]