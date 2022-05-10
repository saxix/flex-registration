from rest_framework import serializers
from strategy_field.utils import fqn

from smart_register.core.models import FlexFormField

from .base import SmartViewSet


class FlexFormFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlexFormField
        exclude = ()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["field_type"] = fqn(instance.field_type)
        return data


class FlexFormFieldViewSet(SmartViewSet):
    """
    This viewset automatically provides `list` and `retrieve` actions.
    """

    queryset = FlexFormField.objects.all()
    serializer_class = FlexFormFieldSerializer
