from django.contrib.admin import register

from .record import RecordAdmin
from .registration import RegistrationAdmin
from ..models import Record, Registration

register(Registration)(RegistrationAdmin)
register(Record)(RecordAdmin)
