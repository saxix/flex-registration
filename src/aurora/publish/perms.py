from django.db.models import Model
from django.http import HttpRequest

from admin_extra_buttons.handlers import BaseExtraHandler
from aurora.core.utils import is_root


def check_publish_permission(request: HttpRequest, obj: Model, handler: BaseExtraHandler, **kwargs) -> bool:
    return is_root(request.user)


def check_load_permission(request, obj, handler: BaseExtraHandler, **kwargs):
    return request.user.is_staff
