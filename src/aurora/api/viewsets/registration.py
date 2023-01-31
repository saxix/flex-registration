from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from strategy_field.utils import fqn

from ...core.models import FlexFormField
from ...core.utils import get_session_id
from ...registration.models import Registration
from .base import SmartViewSet


class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Registration
        exclude = ()
        lookup_field = "slug"


class RegistrationViewSet(SmartViewSet):
    queryset = Registration.objects.all()
    serializer_class = RegistrationSerializer
    lookup_field = "slug"

    def get_permissions(self):
        return [permission() for permission in self.permission_classes]

    @action(detail=True, permission_classes=[AllowAny])
    def metadata(self, request, slug=None):
        def _get_field_details(flex_field: FlexFormField):
            kwargs = flex_field.get_field_kwargs()
            return {
                "type": fqn(flex_field.field_type),
                "smart_attrs": kwargs["smart_attrs"],
                "widget_kwargs": kwargs["widget_kwargs"],
                "choices": kwargs.get("choices"),
            }

        reg: Registration = self.get_object()
        metadata = {"base": {"fields": []}}
        for field in reg.flex_form.fields.all():
            metadata["base"]["fields"].append({field.name: _get_field_details(field)})
        for name, fs in reg.flex_form.get_formsets({}).items():
            metadata[name] = {
                "fields": [],
                "min_num": fs.min_num,
                "max_num": fs.max_num,
            }
            for field in fs.form.flex_form.fields.all():
                metadata[name]["fields"].append({field.name: _get_field_details(field)})

        return Response(metadata)

    @action(detail=True, permission_classes=[AllowAny])
    def version(self, request, slug=None):
        reg: Registration = self.get_object()
        return Response(
            {
                "version": reg.version,
                "url": reg.get_absolute_url(),
                "auth": request.user.is_authenticated,
                "session_id": get_session_id(request),
                "active": reg.active,
                "protected": reg.protected,
            }
        )
