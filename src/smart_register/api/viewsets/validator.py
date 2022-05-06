from rest_framework import serializers

from smart_register.core.models import Validator

from .base import SmartViewSet


class ValidatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Validator
        exclude = ()


class ValidatorViewSet(SmartViewSet):
    """
    This viewset automatically provides `list` and `retrieve` actions.
    """

    queryset = Validator.objects.all()
    serializer_class = ValidatorSerializer
