from typing import Iterable

from django.core.serializers import get_serializer

from admin_sync.protocol import LoadDumpProtocol, JsonSerializer
from admin_sync.utils import ForeignKeysCollector


class AuroraSyncRegistrationProtocol(LoadDumpProtocol):
    def serialize(self, data: Iterable, collect_related=True):
        from aurora.registration.models import Registration
        from aurora.core.models import Validator, FormSet, FlexFormField, OptionSet, CustomFieldType
        from aurora.i18n.models import Message
        from dbtemplates.models import Template

        assert len(data) == 1
        assert isinstance(data[0], Registration)
        reg: Registration = data[0]
        c = ForeignKeysCollector(False)
        # FIXME: improve filtering here
        c.collect(Template.objects.all())
        c.add(OptionSet.objects.all())
        c.add(Message.objects.all())
        c.add(Validator.objects.all())
        c.add(CustomFieldType.objects.all())

        c.add([reg.flex_form, reg.validator, reg])
        fs = FormSet.objects.filter(parent=reg.flex_form)
        fs_forms = [f.flex_form for f in fs] + [f.parent for f in fs]
        c.add(fs_forms)

        c.add(FlexFormField.objects.filter(flex_form=reg.flex_form), collect_related=False)
        c.add(FlexFormField.objects.filter(flex_form__in=fs_forms))
        c.add(fs)

        # forms = FlexForm.objects.filter(formset__parent=reg.flex_form)
        #
        # fields = FlexFormField.objects.filter(flex_form__in=forms)
        # fs = FormSet.objects.filter(Q(flex_form__in=forms) | Q(parent__in=forms))
        # frm2 = FlexForm.objects.filter(formset__parent=reg.flex_form)
        # c.collect(forms)
        # c.collect(fields)
        # # c.collect(fs)

        json: JsonSerializer = get_serializer("json")()
        return json.serialize(c.data, use_natural_foreign_keys=True, use_natural_primary_keys=True, indent=3)
