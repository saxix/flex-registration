import json
import logging

from django.core.cache import cache
from django.template import Library

from smart_register.state import state

logger = logging.getLogger(__name__)
register = Library()


@register.simple_tag()
def validator_status(validator):
    st = "unknown"
    if validator.trace:
        st = cache.get(f"validator-{state.request.user.pk}-{validator.pk}-status") or st
    return str(st).lower()


@register.simple_tag()
def validator_error(validator):
    err = cache.get(f"validator-{state.request.user.pk}-{validator.pk}-error")
    if err:
        err = json.loads(err)
    return err
