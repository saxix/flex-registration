import json
import logging

from django.core.cache import cache
from django.template import Library

from smart_register.state import state

logger = logging.getLogger(__name__)
register = Library()


@register.filter()
def validator_status(validator):
    if validator.trace:
        return cache.get(f"validator-{state.request.user.pk}-{validator.pk}-status").lower()


@register.simple_tag()
def validator_error(validator):
    err = cache.get(f"validator-{state.request.user.pk}-{validator.pk}-error")
    if err:
        err = json.loads(err)
    return err
