from django.http import HttpResponse
from rest_framework import serializers
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from smart_register.core.models import Validator

from .base import SmartViewSet


class ValidatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Validator
        exclude = ()


class ValidatorViewSet(SmartViewSet):
    queryset = Validator.objects.all()
    serializer_class = ValidatorSerializer
    WRAPPER = """
;function {function_name}(value){{
    return eval('{code}');
}};
"""

    @action(detail=True, permission_classes=[AllowAny], authentication_classes=[SessionAuthentication])
    def script(self, request, pk):
        obj = self.get_object()
        return HttpResponse(
            self.WRAPPER.format(function_name=obj.function_name, code=obj.code.replace("\n", "").replace("\r", "")),
            content_type="application/javascript",
        )
