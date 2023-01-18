from django.db.models import Q
from typing import Iterable

from admin_sync.protocol import LoadDumpProtocol
from admin_sync.collector import ForeignKeysCollector


class AuroraSyncRegistrationProtocol(LoadDumpProtocol):
    def collect(self, data: Iterable, collect_related=True):
        from aurora.registration.models import Registration
        from aurora.core.models import FormSet, FlexFormField

        assert len(data) == 1
        assert isinstance(data[0], Registration)
        reg: Registration = data[0]
        c = ForeignKeysCollector(False)
        # FIXME: improve filtering here
        c.collect([reg.flex_form, reg.validator, reg])
        c.add(reg.scripts.all())

        fs = FormSet.objects.filter(parent=reg.flex_form)
        fs_forms = [f.flex_form for f in fs] + [f.parent for f in fs]
        c.add(fs_forms)

        fields = FlexFormField.objects.filter(Q(flex_form=reg.flex_form) | Q(flex_form__in=fs_forms))
        validators = [f.validator for f in fields]
        validators.extend([f.validator for f in fs])
        c.add(validators)
        c.add(fields)
        c.add(fs)
        return c.data
