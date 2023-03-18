from django.contrib.admin import register

from .record import Record, RecordAdmin
from .registration import Registration, RegistrationAdmin

register(Registration)(RegistrationAdmin)
register(Record)(RecordAdmin)
