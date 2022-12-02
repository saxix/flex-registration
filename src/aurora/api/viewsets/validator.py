from django.http import HttpResponse
from rest_framework import serializers
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny

from aurora.core.models import Validator

from .base import SmartViewSet


class ValidatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Validator
        exclude = ()


class ValidatorViewSet(SmartViewSet):
    queryset = Validator.objects.all()
    serializer_class = ValidatorSerializer
    lookup_field = "name"
    WRAPPER = """
;function {name}(value){{
    return eval('{code}');
}};
"""

    @action(detail=True, permission_classes=[AllowAny], authentication_classes=[SessionAuthentication])
    def validator(self, request, name):
        obj = self.get_object()
        return HttpResponse(
            self.WRAPPER.format(name=obj.name, code=obj.code.replace("\n", "").replace("\r", "")),
            content_type="application/javascript",
        )

    @action(detail=True, permission_classes=[AllowAny], authentication_classes=[SessionAuthentication])
    def script(self, request, name):
        obj = self.get_object()
        return HttpResponse(
            obj.code,
            content_type="application/javascript",
        )
